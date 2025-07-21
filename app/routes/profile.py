from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import User, UserUpdate
from app.db import get_database
from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/profile", tags=["Profile"])

USER_COLLECTION = "users"

@router.get(
    "/{user_id}",
    response_model=User,
    summary="Get user profile details"
)
async def get_user_profile(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieve the full profile for a given user.
    """
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {user_id}"
        )
    
    user = await db[USER_COLLECTION].find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return user

@router.put(
    "/{user_id}",
    response_model=User,
    summary="Update user profile details"
)
async def update_user_profile(
    user_id: str,
    user_update: UserUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update a user's profile information. Only the provided fields will be updated.
    """
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {user_id}"
        )
        
    if not await db[USER_COLLECTION].find_one({"_id": user_obj_id}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Create a dictionary of fields to update, excluding any that are None
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided."
        )

    await db[USER_COLLECTION].update_one(
        {"_id": user_obj_id},
        {"$set": update_data}
    )

    # Fetch and return the updated user document
    updated_user = await db[USER_COLLECTION].find_one({"_id": user_obj_id})
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated user profile."
        )
        
    return updated_user