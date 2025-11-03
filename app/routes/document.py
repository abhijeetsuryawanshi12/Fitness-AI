from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import Document, User
from app.vector_store import (
    process_and_store_document,
    delete_document_from_vector_store,
    get_document_chunks_from_vector_store,
    restore_document_to_vector_store
)
from app.security import get_current_user
from typing import List
import os
import shutil
import tempfile
import asyncio
import logging
from bson import ObjectId

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

DOCUMENT_COLLECTION = "documents"

@router.post(
    "/upload",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process a document for the current user"
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Uploads a PDF document for the authenticated user, extracts its text, 
    stores it in MongoDB, and its embeddings in ChromaDB for RAG.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is supported.")

    user_id_str = str(current_user.id)

    # Create a temporary file to store the upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    document_id = None
    try:
        # 1. First, create the document record in MongoDB to get an ID
        doc_mongo = Document(
            user_id=user_id_str,
            filename=file.filename,
            content="" # Will be updated after processing
        )
        doc_data = doc_mongo.model_dump(by_alias=True, exclude=["id"])
            
        result = await db[DOCUMENT_COLLECTION].insert_one(doc_data)
        document_id = result.inserted_id

        # 2. Process the document and store in vector store
        full_text = process_and_store_document(
            file_path=tmp_path,
            user_id=user_id_str,
            document_id=str(document_id),
            filename=file.filename
        )

        # 3. Update the MongoDB record with the full text
        await db[DOCUMENT_COLLECTION].update_one(
            {"_id": document_id},
            {"$set": {"content": full_text}}
        )

        # 4. Fetch the final document to return
        created_document = await db[DOCUMENT_COLLECTION].find_one({"_id": document_id})
        return created_document

    except Exception as e:
        # Clean up failed Mongo entry if processing fails
        if document_id:
            await db[DOCUMENT_COLLECTION].delete_one({"_id": document_id})
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get(
    "/",
    response_model=List[Document],
    summary="List all documents for the current user"
)
async def list_my_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieves a list of all documents uploaded by the currently authenticated user.
    """
    user_id_str = str(current_user.id)
    cursor = db[DOCUMENT_COLLECTION].find({"user_id": user_id_str}).sort("created_at", -1)
    documents = await cursor.to_list(length=None)
    return documents


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document and its embeddings with state consistency"
)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Deletes a specific document from MongoDB and its associated vector embeddings
    from the vector store with state consistency guarantees.

    This implementation ensures that either both MongoDB and ChromaDB deletions succeed,
    or neither does (with rollback). This prevents orphaned data.

    Strategy:
    1. Validate document exists and belongs to user
    2. Backup ChromaDB chunks (for potential rollback)
    3. Delete from ChromaDB first (with retries)
    4. Delete from MongoDB
    5. If MongoDB deletion fails, restore to ChromaDB (rollback)
    """
    try:
        doc_obj_id = ObjectId(document_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID format.")

    # Step 1: Verify document exists and belongs to current user
    document_to_delete = await db[DOCUMENT_COLLECTION].find_one(
        {"_id": doc_obj_id, "user_id": str(current_user.id)}
    )

    if not document_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or you do not have permission to delete it."
        )

    # Step 2: Backup ChromaDB chunks for potential rollback
    chromadb_backup = None
    try:
        logger.info(f"Backing up ChromaDB chunks for document {document_id}")
        chromadb_backup = get_document_chunks_from_vector_store(document_id)
    except Exception as e:
        logger.warning(f"Could not backup ChromaDB chunks for document {document_id}: {e}")
        # Continue anyway - if there are no chunks, deletion will be simpler

    # Step 3: Delete from ChromaDB FIRST (with retry logic)
    max_retries = 3
    chromadb_deleted = False
    last_chromadb_error = None

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting ChromaDB deletion for document {document_id} (attempt {attempt + 1}/{max_retries})")
            delete_document_from_vector_store(document_id=document_id)
            chromadb_deleted = True
            logger.info(f"Successfully deleted document {document_id} from ChromaDB")
            break
        except Exception as e:
            last_chromadb_error = e
            logger.warning(f"ChromaDB deletion attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                # Wait before retry with exponential backoff
                wait_time = 1 * (2 ** attempt)  # 1s, 2s, 4s
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)

    # If ChromaDB deletion failed after all retries, abort the entire operation
    if not chromadb_deleted:
        logger.error(f"Failed to delete document {document_id} from ChromaDB after {max_retries} attempts")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document from vector store after {max_retries} attempts. Please try again later."
        )

    # Step 4: Delete from MongoDB
    try:
        logger.info(f"Deleting document {document_id} from MongoDB")
        delete_result = await db[DOCUMENT_COLLECTION].delete_one({"_id": doc_obj_id})

        if delete_result.deleted_count == 0:
            raise Exception("Document not found in MongoDB (possibly already deleted)")

        logger.info(f"Successfully deleted document {document_id} from MongoDB")

    except Exception as mongo_error:
        # ROLLBACK: MongoDB deletion failed, restore to ChromaDB
        logger.error(f"MongoDB deletion failed for document {document_id}: {mongo_error}")
        logger.warning(f"Attempting to rollback - restoring document {document_id} to ChromaDB")

        if chromadb_backup and chromadb_backup.get('ids'):
            try:
                restore_document_to_vector_store(document_id, chromadb_backup)
                logger.info(f"Successfully rolled back document {document_id} to ChromaDB")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete document from database. No changes were made."
                )
            except Exception as rollback_error:
                # Critical: Rollback failed - data is now inconsistent
                logger.critical(
                    f"CRITICAL: Rollback failed for document {document_id}. "
                    f"Document deleted from ChromaDB but not from MongoDB. "
                    f"Rollback error: {rollback_error}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Critical error during deletion. Please contact support with document ID."
                )
        else:
            # No backup available, can't rollback
            logger.critical(
                f"CRITICAL: No backup available to rollback document {document_id}. "
                f"Document deleted from ChromaDB but not from MongoDB."
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document from database. Partial deletion occurred."
            )

    # Success: Both deletions completed
    logger.info(f"Document {document_id} successfully deleted from both MongoDB and ChromaDB")
    return
