# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import pymongo # Import pymongo for index model

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db = Database()

async def connect_to_mongo():
    """Connects to the MongoDB database and creates indexes."""
    print("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URI)
    db.db = db.client[settings.DB_NAME]
    try:
        # The ismaster command is cheap and does not require auth.
        await db.client.admin.command('ismaster')
        print("Successfully connected to MongoDB.")

        # Create unique index for user emails
        users_collection = db.db.users
        await users_collection.create_index(
            [("email", pymongo.ASCENDING)],
            unique=True,
            name="unique_email_idx"
        )
        print("Ensured unique email index exists for users collection.")

        # PRODUCTION IMPROVEMENT: Add indexes for the tasks collection for performance.
        tasks_collection = db.db.tasks
        await tasks_collection.create_index(
            [("user_id", pymongo.ASCENDING), ("task_date", pymongo.DESCENDING)],
            name="user_id_task_date_idx"
        )
        print("Ensured user_id and task_date index exists for tasks collection.")

    except Exception as e:
        print(f"Could not connect to MongoDB or create indexes: {e}")
        raise

async def close_mongo_connection():
    """Closes the MongoDB connection."""
    print("Closing MongoDB connection...")
    db.client.close()
    print("MongoDB connection closed.")

def get_database() -> AsyncIOMotorDatabase:
    """Returns the database instance."""
    return db.db