from fastapi import APIRouter, Depends, HTTPException, status, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import User
from app.security import get_current_user
from app.config import settings
from pywebpush import webpush, WebPushException
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
import logging
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

VAPID_PRIVATE_KEY = settings.VAPID_PRIVATE_KEY
VAPID_PUBLIC_KEY = settings.VAPID_PUBLIC_KEY
VAPID_EMAIL = settings.VAPID_EMAIL

if not all([VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL]):
    logger.warning("VAPID keys not configured. Push notifications will be disabled.")

@router.get("/vapid_public_key", response_model=Dict[str, str])
def get_vapid_public_key():
    """Provides the VAPID public key to the frontend."""
    if not VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=503, detail="VAPID public key not configured on the server.")
    return {"public_key": VAPID_PUBLIC_KEY}

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_to_notifications(
    subscription: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Saves a user's push notification subscription to their profile.
    """
    user_id = current_user.id
    endpoint = subscription.get("endpoint")

    if not endpoint:
        raise HTTPException(status_code=400, detail="Subscription object must have an endpoint.")

    # Avoid duplicate subscriptions for the same endpoint
    await db.users.update_one(
        {"_id": user_id},
        {"$pull": {"push_subscriptions": {"endpoint": endpoint}}}
    )

    # Add the new subscription
    result = await db.users.update_one(
        {"_id": user_id},
        {"$push": {"push_subscriptions": subscription}}
    )

    if result.modified_count == 0:
        # It's possible the user was already there, so we check if it exists now
        user_doc = await db.users.find_one({"_id": user_id, "push_subscriptions.endpoint": endpoint})
        if not user_doc:
            raise HTTPException(status_code=500, detail="Failed to save push subscription.")

    return {"message": "Subscription saved successfully."}

def send_push_notification(subscription_info: Dict, title: str, body: str):
    """
    Sends a single push notification using pywebpush.
    """
    if not all([VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL]):
        logger.error("Cannot send push notification: VAPID keys are not configured.")
        return

    try:
        webpush(
            subscription_info=subscription_info,
            data=f'{{"title": "{title}", "body": "{body}"}}',
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{VAPID_EMAIL}"}
        )
        logger.info(f"Successfully sent notification to endpoint: {subscription_info.get('endpoint')}")
    except WebPushException as ex:
        logger.error(f"Failed to send notification to {subscription_info.get('endpoint')}: {ex}")
        # If subscription is expired (410) or gone (404), it should be removed from DB.
        if ex.response and ex.response.status_code in [404, 410]:
            logger.info(f"Subscription expired or invalid for endpoint: {subscription_info.get('endpoint')}. It should be removed.")
            # A robust implementation would remove the specific subscription here.

async def check_and_send_task_notifications():
    """
    Scheduled job function.
    - Finds tasks that are due soon.
    - Sends notifications to the respective users.
    - Marks tasks as notified to prevent re-sending.
    """
    db = get_database()
    now = datetime.now(timezone.utc)
    # Notify for tasks in the next 15 minutes that haven't been notified yet
    upcoming_window = now + timedelta(minutes=15)

    logger.info(f"Scheduler running at {now}: Checking for tasks between {now} and {upcoming_window}")

    tasks_cursor = db.tasks.find({
        "task_date": {"$gte": now, "$lt": upcoming_window},
        "completed": False,
        "notified": False
    })

    tasks_to_notify: List[Dict] = await tasks_cursor.to_list(length=None)
    
    if not tasks_to_notify:
        logger.info("No upcoming tasks to notify.")
        return

    for task in tasks_to_notify:
        user_id_str = task.get("user_id")
        try:
            user_obj_id = ObjectId(user_id_str)
        except Exception:
            logger.error(f"Invalid user_id format '{user_id_str}' for task {task['_id']}.")
            continue
            
        user = await db.users.find_one({"_id": user_obj_id})

        if user and user.get("push_subscriptions"):
            subscriptions = user["push_subscriptions"]
            logger.info(f"Found {len(subscriptions)} subscriptions for user {user_id_str} for task '{task['name']}'")
            for sub in subscriptions:
                send_push_notification(
                    subscription_info=sub,
                    title=f"Upcoming Task: {task['name']}",
                    body=f"Your '{task['name']}' task is scheduled for {task['task_date'].strftime('%H:%M')}."
                )
            
            # Mark the task as notified in the database
            await db.tasks.update_one(
                {"_id": task["_id"]},
                {"$set": {"notified": True}}
            )
            logger.info(f"Marked task {task['_id']} as notified.")
