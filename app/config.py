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

    # --- NEW: Keys for Voice Services ---
    ASSEMBLYAI_API_KEY: str = os.getenv("ASSEMBLYAI_API_KEY")
    ELEVEN_LABS_API_KEY: str = os.getenv("ELEVEN_LABS_API_KEY")

    # ChromaDB settings for persisting vector store on disk
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "chroma_db_store")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "fitness_documents")

    # JWT settings
    # To generate a secret key, you can run this in a Python shell:
    # >>> import secrets; secrets.token_hex(32)
    SECRET_KEY: str = os.getenv("SECRET_KEY") # No default value for production safety
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # Load VAPID keys from environment variables (recommended)
    VAPID_PUBLIC_KEY: str = os.environ.get("VAPID_PUBLIC_KEY")
    VAPID_PRIVATE_KEY: str = os.environ.get("VAPID_PRIVATE_KEY")
    VAPID_EMAIL: str = os.environ.get("VAPID_EMAIL")

    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable not set in .env file")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set in .env file")
    # PRODUCTION SAFETY: Ensure a real secret key is set and not the default
    if not SECRET_KEY or SECRET_KEY == "a_very_secret_key_that_should_be_in_env_file":
        raise ValueError("FATAL: SECRET_KEY environment variable not set or is set to the default. Please generate a secure key.")

    # --- NEW: Validation for Voice Service Keys ---
    # We print a warning so the app can start, but voice features will fail.
    if not ASSEMBLYAI_API_KEY:
        print("Warning: ASSEMBLYAI_API_KEY is not set. Voice input will not work.")
    if not ELEVEN_LABS_API_KEY:
        print("Warning: ELEVEN_LABS_API_KEY is not set. Voice output will not work.")

settings = Settings()