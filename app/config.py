import os
from dotenv import load_dotenv

# This will load the .env file from the root of your project (`FitnessAI/`)
# Make sure your .env file is located at `FitnessAI/.env`
load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables.
    """
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    DB_NAME: str = os.getenv("DB_NAME", "user_fitness")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    # ChromaDB settings for persisting vector store on disk
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "chroma_db_store")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "fitness_documents")

    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable not set in .env file")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set in .env file")

settings = Settings()