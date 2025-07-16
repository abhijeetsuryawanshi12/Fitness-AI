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
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable not set in .env file")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set in .env file")

settings = Settings()