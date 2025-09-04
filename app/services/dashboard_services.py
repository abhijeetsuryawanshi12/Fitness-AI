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


# --- Generic Function ---
def fetch_task_percent(start_date: datetime, end_date: datetime) -> int:
    """
    Generic function to calculate % of completed tasks between start_date and end_date.
    """
    try:
        query_range = {"$gte": start_date, "$lt": end_date}

        count = tasks_collection.count_documents({
            "completed": True,
            "task_date": query_range
        })

        total_count = tasks_collection.count_documents({
            "task_date": query_range
        })

        return round(count / total_count * 100) if total_count > 0 else 0

    except Exception as e:
        print(f"❌ Error while fetching tasks: {e}")
        return 0


# --- Specialized Functions ---
def fetch_tasks_today():
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    return fetch_task_percent(today, tomorrow)


def fetch_tasks_week():
    now = datetime.now(timezone.utc)
    start_of_week = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)
    return fetch_task_percent(start_of_week, end_of_week)


def fetch_tasks_month():
    now = datetime.now(timezone.utc)
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        next_month = first_day.replace(year=now.year + 1, month=1)
    else:
        next_month = first_day.replace(month=now.month + 1)
    return fetch_task_percent(first_day, next_month)


def fetch_calories_burned(period):
    now = datetime.now(timezone.utc)

    if period == "daily":
        match_stage = {
            "completed": True,
            "type": "diet",
            "task_date": {
                "$gte": now.replace(hour=0, minute=0, second=0, microsecond=0),
                "$lt": now.replace(hour=23, minute=59, second=59, microsecond=999999)
            }
        }
    elif period == "weekly":
        start_of_week = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        match_stage = {
            "completed": True,
            "type": "diet",
            "task_date": {
                "$gte": start_of_week,
                "$lt": now.replace(hour=23, minute=59, second=59, microsecond=999999)
            }
        }
    elif period == "monthly":
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (start_of_month + timedelta(days=31)).replace(day=1)
        match_stage = {
            "completed": True,
            "type": "diet",
            "task_date": {
                "$gte": start_of_month,
                "$lt": next_month
            }
        }
    else:
        return []

    pipeline = [
        {"$match": match_stage},
        {"$group": {"_id": None, "total_calories": {"$sum": "$details.nutrition_facts.calories"}}}
    ]

    result = list(tasks_collection.aggregate(pipeline))
    return result[0]["total_calories"] if result else 0


calories_burnt = fetch_calories_burned("weekly")
print(calories_burnt)