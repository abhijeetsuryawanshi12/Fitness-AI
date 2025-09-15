from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from app.db import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import User, WeightLog, WeightLogCreate
from app.security import get_current_user
from typing import Dict, List, Any
from datetime import datetime, timedelta, timezone, time

# --- NEW HELPER FUNCTIONS to calculate progress ---

async def fetch_total_workouts(db: AsyncIOMotorDatabase, user_id: str, start_date: datetime) -> int:
    """Calculates the total number of completed workout tasks for a user since a start date."""
    count = await db.tasks.count_documents({
        "user_id": user_id,
        "type": "workout",
        "completed": True,
        "task_date": {"$gte": start_date}
    })
    return count

async def hours_trained(db: AsyncIOMotorDatabase, user: User, start_date: datetime) -> float:
    """
    Calculates the total hours trained based on completed workout tasks.
    Uses the user's preferred workout duration as an estimate for each session.
    """
    num_workouts = await fetch_total_workouts(db, str(user.id), start_date)
    # If user has not set their preferred workout time, default to 60 minutes.
    minutes_per_workout = user.workout_time_minutes if user.workout_time_minutes else 60
    total_minutes = num_workouts * minutes_per_workout
    return total_minutes / 60.0

async def calculate_exercise_volume_history(db: AsyncIOMotorDatabase, user_id: str, exercise_name: str) -> List[Dict[str, Any]]:
    """
    Calculates the total volume (sets * reps * weight) for each completed workout session
    of a specific exercise.
    """
    pipeline = [
        {"$match": {
            "user_id": user_id,
            "name": {"$regex": f"^{exercise_name}$", "$options": "i"}, # Case-insensitive match
            "type": "workout",
            "completed": True,
            "performance": {"$ne": None} # Ensure performance data exists
        }},
        {"$sort": {"task_date": 1}},
        {"$project": {
            "_id": 0,
            "date": "$task_date",
            "performance": "$performance"
        }}
    ]
    
    cursor = db.tasks.aggregate(pipeline)
    tasks = await cursor.to_list(length=None)
    
    volume_history = []
    for task in tasks:
        performance = task.get("performance")
        if not performance or not isinstance(performance, dict):
            continue
            
        sets = performance.get("sets", 0)
        reps = performance.get("reps", [])
        weights = performance.get("weights", [])
        
        if not isinstance(reps, list) or not isinstance(weights, list):
            continue
            
        total_volume = 0
        num_sets_to_process = min(sets, len(reps), len(weights))

        for i in range(num_sets_to_process):
            try:
                rep_count = float(reps[i]) if reps[i] not in [None, ''] else 0
                weight_val = float(weights[i]) if weights[i] not in [None, ''] else 0
                total_volume += rep_count * weight_val
            except (ValueError, TypeError):
                continue
        
        if total_volume > 0:
            volume_history.append({
                "date": task["date"],
                "volume": round(total_volume, 2)
            })
            
    return volume_history

# --- ROUTER DEFINITION ---

router = APIRouter(
    prefix="/progress",
    tags=["Progress Tracking"]
)

WEIGHT_LOGS_COLLECTION = "weight_logs"
USER_COLLECTION = "users"
TASK_COLLECTION = "tasks"

@router.post(
    "/log/weight",
    response_model=WeightLog,
    status_code=status.HTTP_201_CREATED,
    summary="Log user's weight for a specific day"
)
async def log_weight(
    log_data: WeightLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Logs the user's weight for a given date. If a log for that day already exists,
    it will be updated (upsert). Also updates the user's current weight in their profile.
    """
    user_id_str = str(current_user.id)
    log_date = datetime.combine(log_data.date_today, time.min, tzinfo=timezone.utc)

    # Upsert logic: Update if exists for that day, otherwise insert.
    start_of_day = log_date
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

    weight_log_doc = await db[WEIGHT_LOGS_COLLECTION].find_one_and_update(
        {
            "user_id": user_id_str,
            "date": {"$gte": start_of_day, "$lte": end_of_day}
        },
        {
            "$set": {
                "user_id": user_id_str,
                "weight": log_data.weight,
                "date": start_of_day
            }
        },
        upsert=True,
        return_document=True
    )

    # Also update the primary weight on the user's profile
    await db[USER_COLLECTION].update_one(
        {"_id": current_user.id},
        {"$set": {"weight": log_data.weight}}
    )

    return weight_log_doc


@router.get("/me")
async def get_my_progress(
    period: str = Query("daily", enum=["daily", "weekly", "monthly"], description="The time period for the progress report."),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Calculates and returns the authenticated user's progress for a specified period,
    including nutritional summary and weight history.
    """
    user_id_str = str(current_user.id)
    now = datetime.now(timezone.utc)
    
    if period == "daily":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "weekly":
        start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    else: # monthly
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_tasks_count = await db[TASK_COLLECTION].count_documents({"user_id": user_id_str, "task_date": {"$gte": start_date}})
    completed_tasks_count = await db[TASK_COLLECTION].count_documents({"user_id": user_id_str, "task_date": {"$gte": start_date}, "completed": True})
    tasks_completion_percent = (completed_tasks_count / total_tasks_count * 100) if total_tasks_count > 0 else 0

    summary_pipeline = [
        {"$match": {"user_id": user_id_str, "type": "diet", "completed": True, "task_date": {"$gte": start_date}}},
        {"$group": {"_id": None, "total_calories": {"$sum": "$details.nutrition_facts.calories"}, "total_protein_g": {"$sum": "$details.nutrition_facts.protein"}, "total_carbs_g": {"$sum": "$details.nutrition_facts.carbs"}, "total_fats_g": {"$sum": "$details.nutrition_facts.total_fat"}}},
        {"$project": {"_id": 0, "total_calories": {"$ifNull": ["$total_calories", 0]}, "total_protein_g": {"$ifNull": ["$total_protein_g", 0]}, "total_carbs_g": {"$ifNull": ["$total_carbs_g", 0]}, "total_fats_g": {"$ifNull": ["$total_fats_g", 0]}}}
    ]

    weight_logs_cursor = db[WEIGHT_LOGS_COLLECTION].find({"user_id": user_id_str, "date": {"$gte": start_date}}).sort("date", 1)
    weight_logs = await weight_logs_cursor.to_list(length=None)
    weight_history_formatted = [{"date": log['date'].strftime("%Y-%m-%d"), "weight": log['weight']} for log in weight_logs]
    
    weight_change = 0
    if len(weight_logs) > 1:
        weight_change = round(weight_logs[-1]['weight'] - weight_logs[0]['weight'], 2)

    summary_result = await db.tasks.aggregate(summary_pipeline).to_list(length=1)
    total_summary = summary_result[0] if summary_result else {"total_calories": 0, "total_protein_g": 0, "total_carbs_g": 0, "total_fats_g": 0}
    
    # --- MODIFIED: Await the new async helper functions ---
    total_workouts = await fetch_total_workouts(db, user_id_str, start_date)
    total_hours = await hours_trained(db, current_user, start_date)

    return {
        "summary": {
            "total_calories": round(total_summary.get("total_calories", 0)),
            "total_protein_g": round(total_summary.get("total_protein_g", 0)),
            "total_carbs_g": round(total_summary.get("total_carbs_g", 0)),
            "total_fats_g": round(total_summary.get("total_fats_g", 0))
        },
        "tasks_completion_percent": round(tasks_completion_percent),
        "total_workouts": total_workouts,
        "total_hours_trained": round(total_hours, 2),
        "body_metrics": {
            "current_weight": current_user.weight,
            "weight_change": weight_change,
            "weight_history": weight_history_formatted,
        }
    }


@router.get(
    "/exercise/{exercise_name}",
    response_model=List[Dict[str, Any]],
    summary="Get performance history for a specific exercise"
)
async def get_exercise_history(
    exercise_name: str = Path(..., description="The name of the exercise to track."),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieves all completed workout tasks for a specific exercise and calculates
    the total volume for each session to track strength progress over time.
    """
    user_id_str = str(current_user.id)
    
    history = await calculate_exercise_volume_history(db, user_id_str, exercise_name)
    
    if not history:
        raise HTTPException(status_code=404, detail=f"No performance history found for this exercise: '{exercise_name}'.")
        
    return history
