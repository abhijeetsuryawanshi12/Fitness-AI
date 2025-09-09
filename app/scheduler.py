from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from app.config import settings

# Configure the job store to use MongoDB, allowing persistence across restarts
jobstores = {
    'default': MongoDBJobStore(
        database=settings.DB_NAME,
        collection="apscheduler_jobs",
        host=settings.MONGODB_URI
    )
}

# Initialize the scheduler
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="UTC")
