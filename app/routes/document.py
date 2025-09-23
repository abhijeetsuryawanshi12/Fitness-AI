from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import Document, User
from app.vector_store import process_and_store_document, delete_document_from_vector_store
from app.security import get_current_user
from typing import List
import os
import shutil
import tempfile
from bson import ObjectId

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
    summary="Delete a document and its embeddings"
)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Deletes a specific document from MongoDB and its associated vector embeddings
    from the vector store.
    """
    try:
        doc_obj_id = ObjectId(document_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID format.")

    # 1. Find the document to ensure it exists and belongs to the current user
    document_to_delete = await db[DOCUMENT_COLLECTION].find_one(
        {"_id": doc_obj_id, "user_id": str(current_user.id)}
    )

    if not document_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or you do not have permission to delete it."
        )

    # 2. Delete the document from MongoDB
    delete_result = await db[DOCUMENT_COLLECTION].delete_one({"_id": doc_obj_id})

    if delete_result.deleted_count == 0:
        # This is an edge case, but good to handle
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document from the database."
        )

    # 3. Delete the embeddings from the vector store
    try:
        delete_document_from_vector_store(document_id=document_id)
    except Exception as e:
        # If this fails, the document is deleted from Mongo but not Chroma.
        # This is a state inconsistency. We should log this as a critical error.
        print(f"CRITICAL: Document {document_id} deleted from Mongo but failed to delete from vector store: {e}")
        # We don't raise an HTTPException because the primary resource (Mongo doc) is gone.
        # The user sees success, but we need to monitor these logs.

    # A 204 response does not return a body.
    return
