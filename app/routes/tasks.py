# app/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import Task, User
from app.security import get_current_user
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, time, timezone

router = APIRouter(prefix="/tasks", tags=["Tasks"])

TASK_COLLECTION = "tasks"

@router.get(
    "/today",
    response_model=List[Task],
    summary="Get tasks for the current user for today"
)
async def get_my_tasks_for_today(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieves all workout and diet tasks for the authenticated user for the current calendar day (UTC).
    """
    user_id_str = str(current_user.id)

    # Define the start and end of the current day in UTC
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.utc)

    cursor = db[TASK_COLLECTION].find({
        "user_id": user_id_str,
        "task_date": {
            "$gte": start_of_day,
            "$lte": end_of_day
        }
    }).sort("created_at", 1) # Sort by creation time
    
    tasks = await cursor.to_list(length=None)
    return tasks

@router.put(
    "/{task_id}/toggle_completion",
    response_model=Task,
    summary="Mark a task as complete or incomplete"
)
async def toggle_task_completion(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Toggles the 'completed' status of a specific task.
    Ensures the task belongs to the authenticated user.
    """
    try:
        task_obj_id = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task ID format: {task_id}"
        )

    task = await db[TASK_COLLECTION].find_one({"_id": task_obj_id})
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    # --- Authorization Check ---
    if task.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task."
        )

    # Toggle the completion status
    new_status = not task.get("completed", False)
    
    updated_task = await db[TASK_COLLECTION].find_one_and_update(
        {"_id": task_obj_id},
        {"$set": {"completed": new_status}},
        return_document=True
    )

    return updated_task