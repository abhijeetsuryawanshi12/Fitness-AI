from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import Document
from app.vector_store import process_and_store_document
from typing import List
from bson import ObjectId
import os
import shutil
import tempfile

router = APIRouter(prefix="/documents", tags=["Documents"])

DOCUMENT_COLLECTION = "documents"

@router.post(
    "/upload",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process a document"
)
async def upload_document(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Uploads a PDF document, extracts its text, stores the text in MongoDB,
    and stores its embeddings in ChromaDB for RAG.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format.")
        
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is supported.")

    # Create a temporary file to store the upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    document_id = None
    try:
        # 1. First, create the document record in MongoDB to get an ID
        doc_mongo = Document(
            user_id=user_id,
            filename=file.filename,
            content="" # Will be updated after processing
        )
        doc_data = doc_mongo.model_dump(by_alias=True, exclude=["id"])
            
        result = await db[DOCUMENT_COLLECTION].insert_one(doc_data)
        document_id = result.inserted_id

        # 2. Process the document and store in vector store
        full_text = process_and_store_document(
            file_path=tmp_path,
            user_id=user_id,
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
    "/user/{user_id}",
    response_model=List[Document],
    summary="List all documents for a user"
)
async def list_user_documents(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieves a list of all documents uploaded by a specific user.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format.")
    
    cursor = db[DOCUMENT_COLLECTION].find({"user_id": user_id}).sort("created_at", -1)
    documents = await cursor.to_list(length=None)
    return documents