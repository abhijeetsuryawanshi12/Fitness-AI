from celery import Celery
from app.config import settings
import asyncio
from app.graphs.coach_agent import run_proactive_adaptation_check

# Initialize Celery
celery_app = Celery(
    "worker",
    broker=settings.REDIS_URI,
    backend=settings.REDIS_URI
)

celery_app.conf.update(
    task_track_started=True,
    # This tells celery to find tasks in any file named tasks.py in our app
    imports=('app.tasks',)
)


# We will define tasks in a separate file to keep things organized.
# For example, create a new file app/tasks.py for celery tasks.