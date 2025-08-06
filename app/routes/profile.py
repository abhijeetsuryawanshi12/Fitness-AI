# app/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import User, UserUpdate
from app.db import get_database
from app.security import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])

USER_COLLECTION = "users"

@router.get(
    "/me",
    response_model=User,
    summary="Get current user's profile"
)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the full profile for the currently authenticated user.
    """
    # The user object is already retrieved from the token by the dependency.
    return current_user

@router.put(
    "/me",
    response_model=User,
    summary="Update current user's profile"
)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update the current user's profile information. 
    Only the provided fields will be updated. This is used for both
    regular edits and the initial detailed onboarding form.
    """
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided."
        )

    await db[USER_COLLECTION].update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )

    # Fetch and return the updated user document
    updated_user = await db[USER_COLLECTION].find_one({"_id": current_user.id})
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated user profile."
        )
        
    return updated_user