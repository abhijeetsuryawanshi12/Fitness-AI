from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db = Database()

async def connect_to_mongo():
    """Connects to the MongoDB database."""
    print("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URI)
    db.db = db.client[settings.DB_NAME]
    try:
        # The ismaster command is cheap and does not require auth.
        await db.client.admin.command('ismaster')
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Closes the MongoDB connection."""
    print("Closing MongoDB connection...")
    db.client.close()
    print("MongoDB connection closed.")

def get_database() -> AsyncIOMotorDatabase:
    """Returns the database instance."""
    return db.db