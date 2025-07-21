from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.db import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict
from datetime import datetime, timedelta, timezone
from app.agents.progress_agent import analyze_diet_progress
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
    Calculates and returns the user's nutritional progress for a specified period.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
    
    user_object_id = ObjectId(user_id)
    now = datetime.now(timezone.utc)
    
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
    descriptions = [task['description'] for task in tasks_list]

    # --- AI Analysis for Summary ---
    try:
        analysis_str = await analyze_diet_progress(descriptions)
        summary = json.loads(analysis_str).get("summary", {})
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI summary response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during AI analysis: {e}")

    # --- Chart Data Calculation ---
    # Aggregate tasks by day to prepare for analysis
    tasks_by_day: Dict[str, List[str]] = {}
    for task in tasks_list:
        day_str = task['task_date'].strftime('%Y-%m-%d')
        if day_str not in tasks_by_day:
            tasks_by_day[day_str] = []
        tasks_by_day[day_str].append(task['description'])

    # Analyze each day's worth of tasks to get daily calorie totals
    calories_by_day = {}
    for day_str, descs in tasks_by_day.items():
        try:
            day_analysis_str = await analyze_diet_progress(descs)
            calories = json.loads(day_analysis_str).get("summary", {}).get("total_calories", 0)
            calories_by_day[day_str] = calories
        except (json.JSONDecodeError, KeyError):
            calories_by_day[day_str] = 0 # Default to 0 if analysis for a day fails

    # Format for chart
    chart_data = [{"time_label": day, "calories": cals} for day, cals in sorted(calories_by_day.items())]

    return {
        "summary": summary,
        "chart_data": chart_data
    }