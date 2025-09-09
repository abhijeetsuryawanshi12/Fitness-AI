# app/routes/plan.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Literal, Optional
from pydantic import BaseModel, Field
from app.db import get_database
from app.models import Plan, User, Task
from app.agents.plan_agent import generate_full_plan
from app.security import get_current_user
from datetime import datetime, timedelta, timezone, time

router = APIRouter(prefix="/plan", tags=["Plan Generation"])

class GeneratePlanRequest(BaseModel):
    type: Literal["workout", "diet", "workout and diet"]

# --- NEW ENDPOINT ADDED HERE ---
@router.get("/latest", response_model=Plan, summary="Get the user's most recent plan")
async def get_latest_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieves the most recently created plan for the authenticated user.
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
# --- END OF NEW ENDPOINT ---


@router.post("/generate", response_model=Plan, status_code=status.HTTP_201_CREATED)
async def generate_plan_endpoint(
    request: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generates a new workout, diet, or combined plan for the authenticated user
    and creates all associated detailed tasks.
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

    # 2. Create a new Plan object
    new_plan = Plan(
        user_id=user_id_str,
        type=request.type,
        content=plan_content
    )
    
    plan_data_to_insert = new_plan.model_dump(exclude_none=True, by_alias=True)
    if 'id' in plan_data_to_insert:
        del plan_data_to_insert['id']
    
    # 3. Insert plan into database and get its new ID
    result = await db.plans.insert_one(plan_data_to_insert)
    new_plan_id = str(result.inserted_id)

    # 4. Create structured Task documents from the plan content
    tasks_to_create = []
    today = datetime.now(timezone.utc).date()
    daily_schedule = plan_content.get("daily_plan", [])

    if not daily_schedule:
        print(f"Warning: Plan generated for user {user_id_str} has no daily_plan.")

    for day_plan in daily_schedule:
        day_number = day_plan.get("day", 1)
        # --- CORRECTED LOGIC: Get the base date for the task ---
        task_date_part = today + timedelta(days=day_number - 1)

        # Create tasks for exercises if the plan type includes "workout"
        if request.type in ["workout", "workout and diet"] and "exercises" in day_plan:
            for exercise in day_plan.get("exercises", []):
                # --- CORRECTED LOGIC: Extract time and create precise datetime ---
                task_time_data = exercise.get("task_time", {})
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
                    task_date=task_datetime, # Use the precise datetime
                    name=exercise.get("name", "Unnamed Exercise"),
                    details=exercise,
                    type="workout",
                    completed=False
                )
                tasks_to_create.append(task_model.model_dump(by_alias=True, exclude=["id"]))

        # Create tasks for meals if the plan type includes "diet"
        if request.type in ["diet", "workout and diet"] and "meals" in day_plan:
            for meal in day_plan.get("meals", []):
                # --- CORRECTED LOGIC: Extract time and create precise datetime ---
                task_time_data = meal.get("task_time", {})
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
                    task_date=task_datetime, # Use the precise datetime
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
            # This is not a critical failure, so we don't raise an HTTPException
            # The plan was still created. We can log this for monitoring.
    
    # 5. Fetch the newly created plan to return it in the response
    created_plan_doc = await db.plans.find_one({"_id": result.inserted_id})

    if not created_plan_doc:
        raise HTTPException(status_code=500, detail="Failed to create and retrieve the plan from the database.")
    
    return created_plan_doc
