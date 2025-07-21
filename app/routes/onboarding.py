from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import User
from app.db import get_database

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

USER_COLLECTION = "users"

@router.post(
    "/user", 
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user with detailed profile"
)
async def create_user(
    user: User, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new user profile with their fitness details.
    """
    # Pydantic now ensures `goal_deadline` is a datetime object.
    # We can dump the model directly to a dict.
    print("Hello")
    user_dict = user.model_dump(by_alias=True, exclude=["id"])
    
    result = await db[USER_COLLECTION].insert_one(user_dict)
    
    created_user = await db[USER_COLLECTION].find_one({"_id": result.inserted_id})
    
    if created_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the user."
        )

    return created_user