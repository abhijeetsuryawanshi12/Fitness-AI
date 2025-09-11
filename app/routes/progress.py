from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from app.db import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import User, WeightLog, WeightLogCreate
from app.security import get_current_user
from typing import Dict, List, Any
from datetime import datetime, timedelta, timezone, time
from app.services.dashboard_services import (fetch_tasks_today, fetch_tasks_week, fetch_tasks_month, fetch_calories_burned)
from app.services.progress_services import fetch_total_workouts, hours_trained

router = APIRouter(
    prefix="/progress",
    tags=["Progress Tracking"]
)

WEIGHT_LOGS_COLLECTION = "weight_logs"
USER_COLLECTION = "users"

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
    
    # --- Define time range based on the period ---
    if period == "daily":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tasks_percent = fetch_tasks_today()
        calories_burnt = fetch_calories_burned("daily")
        total_workouts = fetch_total_workouts(start_date)
        total_hours = hours_trained(start_date)
    elif period == "weekly":
        start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        tasks_percent = fetch_tasks_week()
        calories_burnt = fetch_calories_burned("weekly")
        total_workouts = fetch_total_workouts(start_date)
        total_hours = hours_trained(start_date)
    else: # monthly
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        tasks_percent = fetch_tasks_month()
        calories_burnt = fetch_calories_burned("monthly")
        total_workouts = fetch_total_workouts(start_date)
        total_hours = hours_trained(start_date)

    # --- Match stage for diet aggregation ---
    match_stage = {
        "$match": {
            "user_id": user_id_str,
            "type": "diet",
            "completed": True,
            "task_date": {"$gte": start_date}
        }
    }

    # --- Aggregation Pipeline for Nutritional Summary ---
    summary_pipeline = [
        match_stage,
        {"$group": {"_id": None, "total_calories": {"$sum": "$details.nutrition_facts.calories"}, "total_protein_g": {"$sum": "$details.nutrition_facts.protein"}, "total_carbs_g": {"$sum": "$details.nutrition_facts.carbs"}}},
        {"$project": {"_id": 0, "total_calories": {"$ifNull": ["$total_calories", 0]}, "total_protein_g": {"$ifNull": ["$total_protein_g", 0]}, "total_carbs_g": {"$ifNull": ["$total_carbs_g", 0]}}}
    ]

    # --- Aggregation Pipeline for Calorie Chart Data ---
    chart_pipeline = [
        match_stage,
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$task_date", "timezone": "UTC"}}, "calories": {"$sum": "$details.nutrition_facts.calories"}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "time_label": "$_id", "calories": {"$ifNull": ["$calories", 0]}}}
    ]

    # --- Fetch Weight Progress Data ---
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

    # --- Execute Pipelines ---
    summary_result = await db.tasks.aggregate(summary_pipeline).to_list(length=1)
    chart_data_result = await db.tasks.aggregate(chart_pipeline).to_list(length=None)

    # --- Format Results ---
    total_summary = summary_result[0] if summary_result else {"total_calories": 0, "total_protein_g": 0, "total_carbs_g": 0}

    return {
        "summary": {
            "total_calories": round(total_summary["total_calories"]),
            "total_protein_g": round(total_summary["total_protein_g"]),
            "total_carbs_g": round(total_summary["total_carbs_g"])
        },
        "chart_data": chart_data_result,
        "tasks_completion_percent": tasks_percent,
        "calories_burned": calories_burnt,
        "total_workouts": total_workouts,
        "total_hours_trained": total_hours,
        "body_metrics": {
            "current_weight": current_user.weight,
            "weight_change": weight_change,
            "weight_history": weight_history_formatted,
        }
    }
