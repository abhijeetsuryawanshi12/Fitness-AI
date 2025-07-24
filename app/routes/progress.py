from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.db import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict
from datetime import datetime, timedelta, timezone
import json

router = APIRouter(
    prefix="/progress",
    tags=["Progress Tracking"]
)

@router.get("/user/{user_id}")
async def get_user_progress(
    user_id: str = Path(..., description="The unique ID of the user"),
    period: str = Query("daily", enum=["daily", "weekly", "monthly"], description="The time period for the progress report."),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Calculates and returns the user's nutritional progress for a specified period
    by directly aggregating data from completed tasks. This method is fast, accurate,
    and does not require AI agent calls.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
    
    now = datetime.now(timezone.utc)
    print(f"Fetching progress for user {user_id} for period: {period} at {now.isoformat()}")
    
    # --- Define time range based on the period ---
    if period == "daily":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "weekly":
        start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    else: # monthly
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # --- Fetch completed diet tasks for the period ---
    tasks_cursor = db.tasks.find({
        "user_id": user_id,
        "type": "diet",
        "completed": True,
        "task_date": {"$gte": start_date}
    })
    
    tasks_list = await tasks_cursor.to_list(length=None)
    if not tasks_list:
        return {
            "summary": {"total_calories": 0, "total_protein_g": 0, "total_carbs_g": 0},
            "chart_data": []
        }

    # --- Directly aggregate nutritional data from tasks ---
    total_summary = {"total_calories": 0, "total_protein_g": 0, "total_carbs_g": 0}
    daily_totals: Dict[str, Dict[str, float]] = {}

    for task in tasks_list:
        day_str = task['task_date'].strftime('%Y-%m-%d')
        if day_str not in daily_totals:
            daily_totals[day_str] = {"calories": 0, "protein": 0, "carbs": 0}

        # Access the detailed nutritional facts stored within the task
        nutrition_facts = task.get("details", {}).get("nutrition_facts", {})
        
        calories = nutrition_facts.get("calories", 0)
        protein = nutrition_facts.get("protein", 0)
        carbs = nutrition_facts.get("carbs", 0)

        # Aggregate for the overall summary
        total_summary["total_calories"] += calories
        total_summary["total_protein_g"] += protein
        total_summary["total_carbs_g"] += carbs
        
        # Aggregate for the daily chart data
        daily_totals[day_str]["calories"] += calories
    
    # --- Prepare chart data ---
    chart_data = [
        {"time_label": day, "calories": totals["calories"]}
        for day, totals in daily_totals.items()
    ]
    
    # Sort chart data by date
    chart_data.sort(key=lambda x: x["time_label"])

    # Round the summary values for a cleaner response
    total_summary["total_calories"] = round(total_summary["total_calories"])
    total_summary["total_protein_g"] = round(total_summary["total_protein_g"])
    total_summary["total_carbs_g"] = round(total_summary["total_carbs_g"])

    return {
        "summary": total_summary,
        "chart_data": chart_data
    }