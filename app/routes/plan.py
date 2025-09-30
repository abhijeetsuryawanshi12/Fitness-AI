from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field
from app.db import get_database
from app.models import Plan, User, Task, PyObjectId
from app.agents.plan_agent import generate_full_plan
from app.security import get_current_user
from datetime import datetime, timedelta, timezone, time

router = APIRouter(prefix="/plan", tags=["Plan Generation"])

class GeneratePlanRequest(BaseModel):
    type: Literal["workout", "diet", "workout and diet"]

# --- NEW: A more flexible response model for backward compatibility ---
# This model allows start_date and end_date to be optional, so old plans
# in the database without these fields do not cause a validation error.
class PlanResponse(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    user_id: str
    type: Literal["workout", "diet", "workout and diet"]
    content: Dict
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

@router.get("/latest", response_model=PlanResponse, summary="Get the user's most recent plan")
async def get_latest_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieves the most recently created plan for the authenticated user.
    This endpoint is backward-compatible with older plan documents that
    may not have start_date and end_date.
    """
    user_id_str = str(current_user.id)
    
    # Find the latest plan by sorting by created_at in descending order
    latest_plan_doc = await db.plans.find_one(
        {"user_id": user_id_str},
        sort=[("created_at", -1)]
    )

    if not latest_plan_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plan found for the current user."
        )
    
    return latest_plan_doc


@router.post("/generate", response_model=Plan, status_code=status.HTTP_201_CREATED)
async def generate_plan_endpoint(
    request: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generates a new workout, diet, or combined plan for the authenticated user
    and creates all associated detailed tasks. All new plans will have a start_date and end_date.
    """
    user_id_str = str(current_user.id)
    user_details = current_user.model_dump()

    # 1. Call the AI agent to generate the plan content
    try:
        print(f"Calling AI agent for user {user_id_str}...")
        plan_content = await generate_full_plan(user_details, request.type)
        print("AI agent returned successfully.")
    except Exception as e:
        print(f"Error calling AI agent: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"The AI agent failed to generate a valid plan. Please try again. Error: {e}"
        )

    # 2. Create a new Plan object with start and end dates
    today_date = datetime.now(timezone.utc).date()
    start_date = datetime.combine(today_date, time.min, tzinfo=timezone.utc)
    end_date = datetime.combine(today_date + timedelta(days=6), time.max, tzinfo=timezone.utc)

    new_plan = Plan(
        user_id=user_id_str,
        type=request.type,
        content=plan_content,
        start_date=start_date,
        end_date=end_date
    )
    
    plan_data_to_insert = new_plan.model_dump(exclude_none=True, by_alias=True)
    if 'id' in plan_data_to_insert:
        del plan_data_to_insert['id']
    
    # 3. Insert plan into database and get its new ID
    result = await db.plans.insert_one(plan_data_to_insert)
    new_plan_id = str(result.inserted_id)

    # 4. Create structured Task documents from the plan content
    tasks_to_create = []
    daily_schedule = plan_content.get("daily_plan", [])

    if not daily_schedule:
        print(f"Warning: Plan generated for user {user_id_str} has no daily_plan.")

    for day_plan in daily_schedule:
        day_number = day_plan.get("day", 1)
        task_date_part = today_date + timedelta(days=day_number - 1)

        # Create tasks for exercises if the plan type includes "workout"
        if request.type in ["workout", "workout and diet"] and "exercises" in day_plan:
            for exercise in day_plan.get("exercises", []):
                task_time_data = exercise.get("task_time", {})
                hour, minute = 0, 0
                
                if isinstance(task_time_data, str):
                    try:
                        parts = task_time_data.split(':')
                        hour = int(parts[0])
                        minute = int(parts[1])
                    except (ValueError, IndexError):
                        print(f"Warning: Could not parse time string '{task_time_data}'. Defaulting to 00:00.")
                        hour, minute = 0, 0
                elif isinstance(task_time_data, dict):
                    hour = task_time_data.get("hour", 0)
                    minute = task_time_data.get("minute", 0)
                
                task_datetime = datetime.combine(
                    task_date_part,
                    time(hour=hour, minute=minute),
                    tzinfo=timezone.utc
                )

                task_model = Task(
                    user_id=user_id_str,
                    plan_id=new_plan_id,
                    task_date=task_datetime,
                    name=exercise.get("name", "Unnamed Exercise"),
                    details=exercise,
                    type="workout",
                    completed=False
                )
                tasks_to_create.append(task_model.model_dump(by_alias=True, exclude=["id"]))

        # Create tasks for meals if the plan type includes "diet"
        if request.type in ["diet", "workout and diet"] and "meals" in day_plan:
            for meal in day_plan.get("meals", []):
                task_time_data = meal.get("task_time", {})
                hour, minute = 0, 0
                
                if isinstance(task_time_data, str):
                    try:
                        parts = task_time_data.split(':')
                        hour = int(parts[0])
                        minute = int(parts[1])
                    except (ValueError, IndexError):
                        print(f"Warning: Could not parse time string '{task_time_data}'. Defaulting to 00:00.")
                        hour, minute = 0, 0
                elif isinstance(task_time_data, dict):
                    hour = task_time_data.get("hour", 0)
                    minute = task_time_data.get("minute", 0)

                task_datetime = datetime.combine(
                    task_date_part,
                    time(hour=hour, minute=minute),
                    tzinfo=timezone.utc
                )
                
                task_model = Task(
                    user_id=user_id_str,
                    plan_id=new_plan_id,
                    task_date=task_datetime,
                    name=meal.get("meal_name", "Unnamed Meal"),
                    details=meal,
                    type="diet",
                    completed=False
                )
                tasks_to_create.append(task_model.model_dump(by_alias=True, exclude=["id"]))
            
    # Bulk insert all tasks for efficiency
    if tasks_to_create:
        try:
            await db.tasks.insert_many(tasks_to_create)
            print(f"Successfully created {len(tasks_to_create)} tasks for plan {new_plan_id}.")
        except Exception as e:
            print(f"Error bulk inserting tasks for plan {new_plan_id}: {e}")
    
    # 5. Fetch the newly created plan to return it in the response
    created_plan_doc = await db.plans.find_one({"_id": result.inserted_id})

    if not created_plan_doc:
        raise HTTPException(status_code=500, detail="Failed to create and retrieve the plan from the database.")
    
    return created_plan_doc


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a plan and its tasks")
async def delete_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Deletes a specific plan and all of its associated tasks.
    This action is irreversible.
    """
    try:
        plan_obj_id = ObjectId(plan_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid plan ID format.")

    plan_to_delete = await db.plans.find_one(
        {"_id": plan_obj_id, "user_id": str(current_user.id)}
    )
    if not plan_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or you do not have permission to delete it."
        )

    delete_tasks_result = await db.tasks.delete_many(
        {"plan_id": plan_id, "user_id": str(current_user.id)}
    )
    print(f"Deleted {delete_tasks_result.deleted_count} tasks for plan {plan_id}.")

    await db.plans.delete_one({"_id": plan_obj_id})

    return
