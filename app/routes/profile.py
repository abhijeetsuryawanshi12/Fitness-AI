# app/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import User, UserUpdate
from app.db import get_database
from app.security import get_current_user
from datetime import datetime, date, timedelta, timezone

router = APIRouter(prefix="/profile", tags=["Profile"])

USER_COLLECTION = "users"

@router.get(
    "/me",
    response_model=User,
    summary="Get current user's profile"
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieve the full profile for the currently authenticated user.
    Also checks if the activity streak should be reset if a day has been missed.
    """
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    
    # Fetch fresh data from DB to ensure it's not stale from the token
    user_db_data = await db[USER_COLLECTION].find_one({"_id": current_user.id})
    
    if not user_db_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found."
        )

    last_completion_date = user_db_data.get("last_completed_task_date")
    
    if last_completion_date:
        # The date from DB is a datetime object, convert to date for comparison
        if isinstance(last_completion_date, datetime):
            last_completion_date = last_completion_date.date()
        
        # If the last completion was before yesterday, reset the streak.
        if last_completion_date < yesterday:
            if user_db_data.get("streak", 0) > 0:
                await db[USER_COLLECTION].update_one(
                    {"_id": current_user.id},
                    {"$set": {"streak": 0}}
                )
                print(f"User {current_user.id} streak reset due to inactivity.")
                # Refresh user data to return the reset streak
                user_db_data["streak"] = 0

    return User(**user_db_data)

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