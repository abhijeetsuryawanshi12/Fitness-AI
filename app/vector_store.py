import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from app.config import settings
from typing import List
import chromadb

# Initialize the embedding model using a freely available model from Hugging Face.
# LangChain will handle downloading and caching the model automatically.
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'} # Explicitly use CPU, can be changed to 'cuda' if a GPU is available
)

# Initialize ChromaDB client
# This setup ensures that the data is persisted to disk
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)

vector_store = Chroma(
    client=chroma_client,
    collection_name=settings.CHROMA_COLLECTION_NAME,
    embedding_function=embedding_model,
)

def process_and_store_document(file_path: str, user_id: str, document_id: str, filename: str):
    """
    Loads a document, splits it into chunks, and stores it in ChromaDB.
    Args:
        file_path: The temporary path to the uploaded PDF file.
        user_id: The ID of the user uploading the document.
        document_id: The ID of the document record in MongoDB.
        filename: The original name of the file.
    """
    # 1. Load the document
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # 2. Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # 3. Add metadata to each chunk
    for split in splits:
        split.metadata = {
            "user_id": user_id,
            "document_id": document_id,
            "filename": filename
        }

    # 4. Add to ChromaDB vector store
    vector_store.add_documents(documents=splits)
    print(f"Successfully added {len(splits)} chunks to ChromaDB for document {filename}.")

    # 5. Return the full text content for storage in MongoDB
    full_text = " ".join([doc.page_content for doc in docs])
    return full_text


def get_retriever_for_user(user_id: str):
    """
    Creates a retriever that filters documents by user_id.
    """
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3, "filter": {"user_id": user_id}}
    )

async def query_vector_store(user_id: str, query: str) -> List[dict]:
    """
    Queries the vector store for relevant documents for a specific user.
    """
    if not user_id:
        return []
        
    print(f"Querying vector store for user '{user_id}' with query: '{query}'")
    retriever = get_retriever_for_user(user_id)
    
    # Use 'ainvoke' for async retrieval
    relevant_docs = await retriever.ainvoke(query)
    
    # Format the results
    return [
        {
            "content": doc.page_content,
            "filename": doc.metadata.get("filename", "N/A")
        }
        for doc in relevant_docs
    ]
