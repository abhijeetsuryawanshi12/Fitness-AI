from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

# --- Connection Details ---
MONGODB_URI: str = os.getenv("MONGODB_URI")
DB_NAME: str = os.getenv("DB_NAME", "user_fitness")

try:
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    tasks_collection = db.tasks
    print("✅ Successfully connected to MongoDB.")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")
    exit()

def fetch_total_workouts(start_date: datetime) -> int:
    """
    Fetches the total number of workout tasks completed since start_date.
    """
    try:
        count = tasks_collection.count_documents({
            "type": "workout",
            "completed": True,
            "task_date": {"$gte": start_date}
        })
        return count
    except Exception as e:
        print(f"❌ Error while fetching total workouts: {e}")
        return 0

from datetime import datetime

def hours_trained(start_date: datetime) -> float:
    """
    Calculates total hours trained since start_date.
    Uses consecutive differences between task_date timestamps.
    """
    try:
        # 1. Fetch all workout tasks after start_date
        task_dates = list(tasks_collection.find(
            {
                "type": "workout",
                "completed": True,
                "task_date": {"$gte": start_date}
            },
            {"task_date": 1, "_id": 0}
        ).sort("task_date", 1))  # sort ascending

        # 2. Extract datetime list
        dates = [t["task_date"] for t in task_dates]

        # 3. Calculate total duration in seconds
        total_seconds = 0
        for i in range(1, len(dates)):
            diff = (dates[i] - dates[i-1]).total_seconds()
            total_seconds += diff

        # 4. Convert to hours
        total_hours = round(total_seconds / 3600, 2)
        print(f"Total hours trained: {total_hours}")
        return total_hours

    except Exception as e:
        print(f"❌ Error while calculating hours trained: {e}")
        return 0.0

def streak_count(last_completed_date: datetime) -> int:
    """
    Calculate the current streak based on the last completed task date.
    A streak is defined as consecutive days with at least one completed task.
    """

    