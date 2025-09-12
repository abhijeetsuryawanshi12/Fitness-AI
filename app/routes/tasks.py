# app/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import Task, User, CreateTask, TaskPerformanceUpdate
from app.security import get_current_user
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, time, timezone, date, timedelta

router = APIRouter(prefix="/tasks", tags=["Tasks"])

TASK_COLLECTION = "tasks"
USER_COLLECTION = "users"

@router.post(
    "/",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
async def create_task(
    task_data: CreateTask, 
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Creates a new task for the authenticated user.
    """
    task_dict = task_data.model_dump()
    task_dict["user_id"] = str(current_user.id)
    task_dict["completed"] = False
    task_dict["created_at"] = datetime.now(timezone.utc)
    
    if isinstance(task_data.task_date, date):
        task_dict["task_date"] = datetime.combine(task_data.task_date, time.min, tzinfo=timezone.utc)

    result = await db[TASK_COLLECTION].insert_one(task_dict)
    created_task = await db[TASK_COLLECTION].find_one({"_id": result.inserted_id})
    
    return created_task


@router.get(
    "/week",
    response_model=List[Task],
    summary="Get tasks for a given week"
)
async def get_tasks_for_week(
    start_date: date, 
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieves all tasks for the authenticated user for a 7-day period starting from `start_date`.
    """
    user_id_str = str(current_user.id)
    
    start_of_week = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    end_of_week = start_of_week + timedelta(days=7) - timedelta(seconds=1)

    cursor = db[TASK_COLLECTION].find({
        "user_id": user_id_str,
        "task_date": {
            "$gte": start_of_week,
            "$lte": end_of_week
        }
    }).sort("task_date", 1)
    
    tasks = await cursor.to_list(length=None)
    return tasks

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
    Retrieves all tasks for the authenticated user for the current calendar day (UTC).
    """
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.utc)

    cursor = db[TASK_COLLECTION].find({
        "user_id": str(current_user.id),
        "task_date": {"$gte": start_of_day, "$lte": end_of_day}
    }).sort("task_date", 1)
    
    tasks = await cursor.to_list(length=None)
    return tasks


@router.put(
    "/{task_id}",
    response_model=Task,
    summary="Update an existing task"
)
async def update_task(
    task_id: str,
    task_updates: CreateTask, 
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Updates the details of a specific task.
    Ensures the task belongs to the authenticated user.
    """
    try:
        task_obj_id = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid task ID: {task_id}")

    task = await db[TASK_COLLECTION].find_one({"_id": task_obj_id})
    if not task or task.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=404, detail="Task not found or permission denied")

    update_data = task_updates.model_dump(exclude_unset=True)
    if 'task_date' in update_data and isinstance(task_updates.task_date, date):
        update_data["task_date"] = datetime.combine(task_updates.task_date, time.min, tzinfo=timezone.utc)

    updated_task = await db[TASK_COLLECTION].find_one_and_update(
        {"_id": task_obj_id},
        {"$set": update_data},
        return_document=True
    )
    return updated_task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Deletes a specific task.
    Ensures the task belongs to the authenticated user before deletion.
    """
    try:
        task_obj_id = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid task ID: {task_id}")

    task = await db[TASK_COLLECTION].find_one({"_id": task_obj_id})
    if not task or task.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=404, detail="Task not found or permission denied")

    await db[TASK_COLLECTION].delete_one({"_id": task_obj_id})
    return

@router.put(
    "/{task_id}/toggle_completion",
    response_model=Task,
    summary="Mark a task as complete or incomplete, with optional performance data"
)
async def toggle_task_completion(
    task_id: str,
    update_data: Optional[TaskPerformanceUpdate] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Toggles the 'completed' status of a task. For workout tasks, an optional
    'performance' payload can be sent to log the actual work done.
    """
    try:
        task_obj_id = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid task ID format: {task_id}")

    task = await db[TASK_COLLECTION].find_one({"_id": task_obj_id})
    if not task or task.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=404, detail="Task not found or permission denied")

    update_payload = {}
    
    # If performance data is provided, we are marking the task as COMPLETE
    if update_data and update_data.performance:
        if task.get("type") != "workout":
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Performance data can only be logged for workout tasks."
            )
        new_status = True
        update_payload['performance'] = update_data.performance
    else:
        # Standard toggle logic if no performance data is sent
        new_status = not task.get("completed", False)
        # If toggling OFF, clear any existing performance data
        if not new_status:
            update_payload['performance'] = None

    update_payload['completed'] = new_status
    
    # Streak logic only triggers when a task goes from incomplete to complete
    if new_status is True and not task.get("completed", False):
        today = datetime.now(timezone.utc).date()
        user_from_db = await db[USER_COLLECTION].find_one({"_id": current_user.id})
        last_completion_date = user_from_db.get("last_completed_task_date")
        if last_completion_date and isinstance(last_completion_date, datetime):
            last_completion_date = last_completion_date.date()

        if last_completion_date != today:
            yesterday = today - timedelta(days=1)
            new_streak = user_from_db.get("streak", 0) + 1 if last_completion_date == yesterday else 1
            await db[USER_COLLECTION].update_one(
                {"_id": current_user.id},
                {"$set": {
                    "streak": new_streak,
                    "last_completed_task_date": datetime.combine(today, time.min, tzinfo=timezone.utc)
                }}
            )

    updated_task = await db[TASK_COLLECTION].find_one_and_update(
        {"_id": task_obj_id},
        {"$set": update_payload},
        return_document=True
    )
    return updated_task
