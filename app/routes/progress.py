from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.db import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict
from datetime import datetime, timedelta, timezone
from app.agents.progress_agent import analyze_diet_progress
import json
import asyncio


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
    This endpoint is now optimized to make fewer calls to the AI agent.
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

    # --- Group tasks by day for efficient analysis ---
    tasks_by_day: Dict[str, List[str]] = {}
    for task in tasks_list:
        day_str = task['task_date'].strftime('%Y-%m-%d')
        if day_str not in tasks_by_day:
            tasks_by_day[day_str] = []
        tasks_by_day[day_str].append(task['description'])

    # --- AI Analysis for each day in parallel ---
    # Create a list of analysis tasks to run concurrently
    analysis_tasks = [
        analyze_diet_progress(descriptions) for descriptions in tasks_by_day.values()
    ]
    
    try:
        # Run all daily analyses in parallel for speed
        daily_analysis_results = await asyncio.gather(*analysis_tasks)
    except Exception as e:
        # A failure in any of the parallel tasks will raise an exception here.
        raise HTTPException(status_code=500, detail=f"An error occurred during AI analysis: {e}")

    # --- Aggregate results and prepare response ---
    total_summary = {"total_calories": 0, "total_protein_g": 0, "total_carbs_g": 0}
    chart_data = []
    
    day_keys = list(tasks_by_day.keys())

    for i, analysis_str in enumerate(daily_analysis_results):
        day_str = day_keys[i]
        try:
            day_summary = json.loads(analysis_str).get("summary", {})
            
            # Aggregate totals for the overall summary
            total_summary["total_calories"] += day_summary.get("total_calories", 0)
            total_summary["total_protein_g"] += day_summary.get("total_protein_g", 0)
            total_summary["total_carbs_g"] += day_summary.get("total_carbs_g", 0)
            
            # Add data for the daily chart
            chart_data.append({
                "time_label": day_str,
                "calories": day_summary.get("total_calories", 0)
            })

        except (json.JSONDecodeError, KeyError) as e:
            # If a single day's analysis fails to parse, log it or handle it, 
            # but don't fail the whole request. Here we'll just skip it.
            print(f"Warning: Could not parse analysis for day {day_str}. Error: {e}")
            chart_data.append({"time_label": day_str, "calories": 0})
    
    # Sort chart data by date
    chart_data.sort(key=lambda x: x["time_label"])

    return {
        "summary": total_summary,
        "chart_data": chart_data
    }