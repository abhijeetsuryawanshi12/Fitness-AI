# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import pymongo  # Import pymongo for index model
import asyncio
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    _connection_retries: int = 0
    _max_retries: int = 5
    _is_connected: bool = False


db = Database()


async def connect_to_mongo():
    """
    Connects to the MongoDB database with retry logic and exponential backoff.
    Creates necessary indexes after successful connection.
    """
    retries = 0
    max_retries = db._max_retries
    base_delay = 2  # seconds
    max_delay = 60  # seconds

    while retries < max_retries:
        try:
            logger.info(f"Attempting to connect to MongoDB (Attempt {retries + 1}/{max_retries})...")

            # Create MongoDB client with connection settings
            db.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,  # 10 second connection timeout
                socketTimeoutMS=10000,  # 10 second socket timeout
                retryWrites=True,
                retryReads=True,
                maxPoolSize=50,
                minPoolSize=10,
            )

            db.db = db.client[settings.DB_NAME]

            # Verify connection with a ping
            await db.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB!")

            db._is_connected = True
            db._connection_retries = 0

            # Create indexes after successful connection
            await create_indexes()

            return  # Success - exit function

        except pymongo.errors.ServerSelectionTimeoutError as e:
            retries += 1
            db._connection_retries = retries

            if retries >= max_retries:
                logger.error(f"❌ Failed to connect to MongoDB after {max_retries} attempts")
                logger.error(f"Error: {e}")
                logger.error("Please check:")
                logger.error("  1. MongoDB Atlas cluster is running")
                logger.error("  2. Network/firewall allows connections")
                logger.error("  3. MongoDB URI is correct")
                logger.error("  4. IP whitelist includes your IP")
                raise ConnectionError(
                    f"Could not connect to MongoDB after {max_retries} attempts. "
                    f"Please check your connection settings and try again."
                )

            # Calculate exponential backoff delay
            delay = min(base_delay * (2 ** (retries - 1)), max_delay)
            logger.warning(f"⚠️ Connection failed. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

        except pymongo.errors.ConfigurationError as e:
            logger.error(f"❌ MongoDB configuration error: {e}")
            logger.error("Check your MONGODB_URI in .env file")
            raise

        except pymongo.errors.OperationFailure as e:
            logger.error(f"❌ MongoDB authentication failed: {e}")
            logger.error("Check your MongoDB credentials")
            raise

        except Exception as e:
            retries += 1
            db._connection_retries = retries

            if retries >= max_retries:
                logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
                raise

            delay = min(base_delay * (2 ** (retries - 1)), max_delay)
            logger.warning(f"⚠️ Unexpected error: {e}. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)


async def create_indexes():
    """
    Creates necessary indexes for collections.
    Separated from connection logic for better error handling.
    """
    try:
        logger.info("Creating database indexes...")

        # Create unique index for user emails
        users_collection = db.db.users
        await users_collection.create_index(
            [("email", pymongo.ASCENDING)],
            unique=True,
            name="unique_email_idx"
        )
        logger.info("✅ Ensured unique email index exists for users collection")

        # Index for tasks collection (for performance)
        tasks_collection = db.db.tasks
        await tasks_collection.create_index(
            [("user_id", pymongo.ASCENDING), ("task_date", pymongo.DESCENDING)],
            name="user_id_task_date_idx"
        )
        logger.info("✅ Ensured user_id and task_date index exists for tasks collection")

        # Additional useful indexes
        await tasks_collection.create_index(
            [("user_id", pymongo.ASCENDING), ("completed", pymongo.ASCENDING)],
            name="user_id_completed_idx"
        )
        logger.info("✅ Ensured user_id and completed index exists for tasks collection")

        # Index for plans
        plans_collection = db.db.plans
        await plans_collection.create_index(
            [("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)],
            name="user_id_created_at_idx"
        )
        logger.info("✅ Ensured user_id and created_at index exists for plans collection")

        logger.info("🎉 All indexes created successfully!")

    except Exception as e:
        logger.error(f"⚠️ Error creating indexes: {e}")
        logger.warning("Application will continue but performance may be affected")
        # Don't raise - indexes are not critical for app to start

async def close_mongo_connection():
    """Closes the MongoDB connection gracefully."""
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()
        db._is_connected = False
        logger.info("✅ MongoDB connection closed")


async def check_connection() -> bool:
    """
    Checks if MongoDB connection is alive.
    Returns True if connected, False otherwise.
    """
    if not db.client or not db._is_connected:
        return False

    try:
        # Ping database to check connection
        await db.client.admin.command('ping')
        return True
    except Exception as e:
        logger.warning(f"⚠️ MongoDB connection check failed: {e}")
        db._is_connected = False
        return False


async def ensure_connection():
    """
    Ensures MongoDB connection is active.
    Reconnects if connection was lost.
    """
    if await check_connection():
        return  # Already connected

    logger.warning("⚠️ MongoDB connection lost. Attempting to reconnect...")

    try:
        await connect_to_mongo()
    except Exception as e:
        logger.error(f"❌ Failed to reconnect to MongoDB: {e}")
        raise


def get_database() -> AsyncIOMotorDatabase:
    """
    Returns the database instance.

    Note: This is a synchronous function that returns the database object.
    Use with dependency injection in FastAPI routes.
    For runtime connection checks, use ensure_connection() in your routes.
    """
    if not db.db:
        raise RuntimeError(
            "Database not initialized. Call connect_to_mongo() first."
        )
    return db.db


async def get_database_with_retry() -> AsyncIOMotorDatabase:
    """
    Returns the database instance with automatic reconnection.
    Use this in routes that need guaranteed connection.

    Example:
        @router.get("/")
        async def my_route(db: AsyncIOMotorDatabase = Depends(get_database_with_retry)):
            # Your code here
    """
    await ensure_connection()
    return db.db