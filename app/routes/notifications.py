# app/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any

from app.db import get_database
from app.models import User
from app.security import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def save_subscription(
    subscription: PushSubscription,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Saves a push notification subscription for the current user.
    """
    sub_dict = subscription.model_dump()
    
    # Use $addToSet to add the subscription only if it doesn't already exist in the array.
    # This prevents duplicate subscriptions for the same device/browser.
    result = await db.users.update_one(
        {"_id": current_user.id},
        {"$addToSet": {"push_subscriptions": sub_dict}}
    )
    
    if result.modified_count > 0 or result.matched_count > 0:
        return {"message": "Subscription saved successfully"}
    
    # This case should ideally not happen if the user is authenticated
    raise HTTPException(status_code=404, detail="User not found")