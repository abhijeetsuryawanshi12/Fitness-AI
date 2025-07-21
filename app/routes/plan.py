from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Literal
from pydantic import BaseModel, Field
from app.db import get_database
from app.models import Plan, User, Task
from app.agents.plan_agent import generate_plan_with_agent
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/plan", tags=["Plan Generation"])

class GeneratePlanRequest(BaseModel):
    user_id: str = Field(..., example="60d5f3f7e6c4b4a3e8e1f4b1")
    type: Literal["workout", "diet"]

@router.post("/generate", response_model=Plan, status_code=status.HTTP_201_CREATED)
async def generate_plan_endpoint(
    request: GeneratePlanRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generates a new workout or diet plan for a user and creates all associated tasks.
    """
    # Validate user ID format
    if not ObjectId.is_valid(request.user_id):
        raise HTTPException(status_code=400, detail=f"Invalid user_id format: {request.user_id}")
    
    user_obj_id = ObjectId(request.user_id)

    # 1. Fetch user from the database
    user_doc = await db.users.find_one({"_id": user_obj_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail=f"User with id {request.user_id} not found")
    
    # Convert MongoDB doc to a dictionary that the agent can use
    user_details = User(**user_doc).model_dump()

    # 2. Call the AI agent to generate the plan content
    try:
        print(f"Calling AI agent for user {request.user_id}...")
        plan_content = await generate_plan_with_agent(user_details, request.type)
        print("AI agent returned successfully.")
    except Exception as e:
        print(f"Error calling AI agent: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"The AI agent failed to generate a valid plan. Please try again. Error: {e}"
        )

    # 3. Create a new Plan object
    new_plan = Plan(
        user_id=request.user_id,
        type=request.type,
        content=plan_content
    )
    
    plan_data_to_insert = new_plan.model_dump(exclude_none=True, by_alias=True)
    if 'id' in plan_data_to_insert:
        del plan_data_to_insert['id']
    
    # 4. Insert plan into database and get its new ID
    result = await db.plans.insert_one(plan_data_to_insert)
    new_plan_id = str(result.inserted_id)

    # 5. --- NEW LOGIC: Create Task documents from the plan content ---
    tasks_to_create = []
    today = datetime.now(timezone.utc).date()
    daily_schedule = plan_content.get("daily_tasks", [])

    if not daily_schedule:
        print(f"Warning: Plan generated for user {request.user_id} has no daily_tasks.")

    for day_plan in daily_schedule:
        day_number = day_plan.get("day", 1)
        # Calculate the date for the task, starting from today (day 1 = today)
        task_datetime = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc) + timedelta(days=day_number - 1)

        for task_desc in day_plan.get("tasks", []):
            # Use the Pydantic model for validation before creating the dict
            task_model = Task(
                user_id=request.user_id,
                plan_id=new_plan_id,
                task_date=task_datetime,
                description=task_desc,
                type=request.type,
                completed=False
            )
            # Dump the model to a dictionary for insertion
            tasks_to_create.append(task_model.model_dump(by_alias=True, exclude=["id"]))
            
    # Bulk insert all tasks for efficiency
    if tasks_to_create:
        try:
            await db.tasks.insert_many(tasks_to_create)
            print(f"Successfully created {len(tasks_to_create)} tasks for plan {new_plan_id}.")
        except Exception as e:
            # If task creation fails, we should ideally roll back the plan creation.
            # For simplicity, we just log the error.
            print(f"Error bulk inserting tasks for plan {new_plan_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Plan was generated, but failed to create associated tasks."
            )

    # 6. Fetch the newly created plan to return it in the response
    created_plan_doc = await db.plans.find_one({"_id": result.inserted_id})

    if not created_plan_doc:
        raise HTTPException(status_code=500, detail="Failed to create and retrieve the plan from the database.")
    
    return created_plan_doc