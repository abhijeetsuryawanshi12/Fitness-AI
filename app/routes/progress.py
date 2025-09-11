# app/routes/progress.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.db import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import User
from app.security import get_current_user
from typing import Dict, List
from datetime import datetime, timedelta, timezone
from app.services.dashboard_services import (fetch_tasks_today, fetch_tasks_week, fetch_tasks_month, fetch_calories_burned)
from app.services.progress_services import fetch_total_workouts, hours_trained

router = APIRouter(
    prefix="/progress",
    tags=["Progress Tracking"]
)

@router.get("/me")
async def get_my_progress(
    period: str = Query("daily", enum=["daily", "weekly", "monthly"], description="The time period for the progress report."),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Calculates and returns the authenticated user's nutritional progress for a specified period
    by using efficient MongoDB aggregation pipelines.
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

    # --- Match stage for all pipelines ---
    match_stage = {
        "$match": {
            "user_id": user_id_str,
            "type": "diet",
            "completed": True,
            "task_date": {"$gte": start_date}
        }
    }

    # --- Aggregation Pipeline for Overall Summary ---
    summary_pipeline = [
        match_stage,
        {
            "$group": {
                "_id": None,
                "total_calories": {"$sum": "$details.nutrition_facts.calories"},
                "total_protein_g": {"$sum": "$details.nutrition_facts.protein"},
                "total_carbs_g": {"$sum": "$details.nutrition_facts.carbs"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_calories": {"$ifNull": ["$total_calories", 0]},
                "total_protein_g": {"$ifNull": ["$total_protein_g", 0]},
                "total_carbs_g": {"$ifNull": ["$total_carbs_g", 0]}
            }
        }
    ]

    # --- Aggregation Pipeline for Chart Data ---
    chart_pipeline = [
        match_stage,
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$task_date", "timezone": "UTC"}},
                "calories": {"$sum": "$details.nutrition_facts.calories"}
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "time_label": "$_id",
                "calories": {"$ifNull": ["$calories", 0]}
            }
        }
    ]

    # --- Execute Pipelines ---
    summary_result = await db.tasks.aggregate(summary_pipeline).to_list(length=1)
    chart_data_result = await db.tasks.aggregate(chart_pipeline).to_list(length=None)

    # --- Format Results ---
    if not summary_result:
        total_summary = {"total_calories": 0, "total_protein_g": 0, "total_carbs_g": 0}
    else:
        total_summary = summary_result[0]
        # Round the values for a cleaner response
        total_summary["total_calories"] = round(total_summary["total_calories"])
        total_summary["total_protein_g"] = round(total_summary["total_protein_g"])
        total_summary["total_carbs_g"] = round(total_summary["total_carbs_g"])

    return {
        "summary": total_summary,
        "chart_data": chart_data_result,
        "tasks_completion_percent": tasks_percent,
        "calories_burned": calories_burnt,
        "total_workouts": total_workouts,
        "total_hours_trained": total_hours
    }

