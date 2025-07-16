from fastapi import APIRouter, HTTPException, Depends, status, Body
from app.models import Plan
from app.db import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Literal, List
from app.agents.plan_agent import generate_plan_with_agent
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

router = APIRouter(prefix="/plan", tags=["Plan Generation"])

USER_COLLECTION = "users"
PLAN_COLLECTION = "plans"

@router.post(
    "/generate", 
    response_model=Plan,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new workout or diet plan"
)
async def generate_plan(
    db: AsyncIOMotorDatabase = Depends(get_database),
    user_id: str = Body(..., description="The ID of the user for whom to generate the plan."),
    plan_type: Literal["workout", "diet"] = Body(..., alias="type", description="The type of plan to generate.")
):
    """
    Generates a personalized workout or diet plan for a given user.
    Requires `user_id` and `type` in the request body.
    """
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid user ID format: {user_id}")

    user_data = await db[USER_COLLECTION].find_one({"_id": user_obj_id})
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")

    # The agent call is now async and non-blocking
    plan_content = await generate_plan_with_agent(user_data, plan_type)
    
    now = datetime.utcnow()
    
    # The Pydantic model `Plan` and custom type `PyObjectId` handle the
    # conversion of the user_id string into a proper ObjectId.
    new_plan = Plan(
        user_id=user_id,
        type=plan_type,
        content=plan_content,
        created_at=now,
        updated_at=now
    )
    
    plan_dict = new_plan.model_dump(by_alias=True, exclude=["id"])
    
    result = await db[PLAN_COLLECTION].insert_one(plan_dict)

    created_plan = await db[PLAN_COLLECTION].find_one({"_id": result.inserted_id})

    if created_plan is None:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the plan."
        )

    return created_plan

@router.get(
    "/user/{user_id}",
    response_model=List[Plan],
    status_code=status.HTTP_200_OK,
    summary="Get all plans for a specific user"
)
async def get_plans_for_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieves all workout and diet plans that have been generated for a user,
    ordered by creation date.
    """
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid user ID format: {user_id}")

    # Find all plans for the given user_id and sort them from newest to oldest
    cursor = db[PLAN_COLLECTION].find({"user_id": user_obj_id}).sort("created_at", -1)
    
    # The response_model `List[Plan]` will automatically handle serialization
    plans = await cursor.to_list(length=None)
    
    return plans