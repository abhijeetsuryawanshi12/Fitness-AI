from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from app.db import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import User, WeightLog, WeightLogCreate
from app.security import get_current_user
from typing import Dict, List, Any
from app.services.progress_services import fetch_total_workouts, hours_trained, streak_count
from datetime import datetime, timedelta, timezone, time

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
                "date": start_of_day  # Store at the beginning of the day for consistency
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

    # --- Task Completion (Consistency) ---
    total_tasks_cursor = db[TASK_COLLECTION].find({"user_id": user_id_str, "task_date": {"$gte": start_date}})
    completed_tasks_cursor = db[TASK_COLLECTION].find({"user_id": user_id_str, "task_date": {"$gte": start_date}, "completed": True})
    
    total_tasks_count = await db[TASK_COLLECTION].count_documents({"user_id": user_id_str, "task_date": {"$gte": start_date}})
    completed_tasks_count = await db[TASK_COLLECTION].count_documents({"user_id": user_id_str, "task_date": {"$gte": start_date}, "completed": True})
    
    tasks_completion_percent = (completed_tasks_count / total_tasks_count * 100) if total_tasks_count > 0 else 0

    # --- Nutritional Summary (Macro Breakdown) ---
    match_stage = {
        "$match": {
            "user_id": user_id_str,
            "type": "diet",
            "completed": True,
            "task_date": {"$gte": start_date}
        }
    }
    summary_pipeline = [
        match_stage,
        {"$group": {"_id": None, "total_calories": {"$sum": "$details.nutrition_facts.calories"}, "total_protein_g": {"$sum": "$details.nutrition_facts.protein"}, "total_carbs_g": {"$sum": "$details.nutrition_facts.carbs"}, "total_fats_g": {"$sum": "$details.nutrition_facts.total_fat"}}},
        {"$project": {"_id": 0, "total_calories": {"$ifNull": ["$total_calories", 0]}, "total_protein_g": {"$ifNull": ["$total_protein_g", 0]}, "total_carbs_g": {"$ifNull": ["$total_carbs_g", 0]}, "total_fats_g": {"$ifNull": ["$total_fats_g", 0]}}}
    ]

    # --- Weight History ---
    weight_logs_cursor = db[WEIGHT_LOGS_COLLECTION].find(
        {"user_id": user_id_str, "date": {"$gte": start_date}}
    ).sort("date", 1)
    weight_logs = await weight_logs_cursor.to_list(length=None)

    weight_history_formatted = [
        {"date": log['date'].strftime("%Y-%m-%d"), "weight": log['weight']} for log in weight_logs
    ]
    
    weight_change = 0
    if len(weight_logs) > 1:
        weight_change = round(weight_logs[-1]['weight'] - weight_logs[0]['weight'], 2)

    # --- Execute Aggregations ---
    summary_result = await db.tasks.aggregate(summary_pipeline).to_list(length=1)
    total_summary = summary_result[0] if summary_result else {"total_calories": 0, "total_protein_g": 0, "total_carbs_g": 0, "total_fats_g": 0}

    return {
        "summary": {
            "total_calories": round(total_summary["total_calories"]),
            "total_protein_g": round(total_summary["total_protein_g"]),
            "total_carbs_g": round(total_summary["total_carbs_g"]),
            "total_fats_g": round(total_summary["total_fats_g"])
        },
        "tasks_completion_percent": round(tasks_completion_percent),
        "total_workouts": fetch_total_workouts(start_date),
        "total_hours_trained": round(hours_trained(start_date), 2),
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
    Retrieves all completed workout tasks for a specific exercise to track strength
    progress over time.
    """
    user_id_str = str(current_user.id)
    
    pipeline = [
        {"$match": {
            "user_id": user_id_str,
            "name": {"$regex": f"^{exercise_name}$", "$options": "i"}, # Case-insensitive match
            "type": "workout",
            "completed": True,
            "performance": {"$exists": True, "$ne": None}
        }},
        {"$sort": {"task_date": 1}},
        {"$project": {
            "_id": 0,
            "date": "$task_date",
            "performance": "$performance"
        }}
    ]
    
    history = await db.tasks.aggregate(pipeline).to_list(length=None)
    
    if not history:
        raise HTTPException(status_code=404, detail="No performance history found for this exercise.")
        
    return history
