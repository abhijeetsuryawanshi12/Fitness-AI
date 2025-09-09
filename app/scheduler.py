# app/scheduler.py
import json
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pywebpush import webpush, WebPushException
from bson import ObjectId

from app.db import get_database
from app.config import settings

# Initialize the scheduler
scheduler = AsyncIOScheduler(timezone="UTC")

async def check_for_due_tasks():
    """
    This function runs periodically, checks for due tasks, and sends notifications.
    """
    db = get_database()
    print(f"[{datetime.now(timezone.utc)}] Running scheduled check for due tasks...")

    # Query for tasks that are due in the next 5 minutes and haven't been notified yet
    # This gives a buffer in case the scheduler is slightly delayed.
    now = datetime.now(timezone.utc)
    in_5_minutes = now + timedelta(minutes=5)

    # Find tasks that are due between now and the next 5 minutes and are not completed
    due_tasks_cursor = db.tasks.find({
        "task_date": {"$gte": now, "$lt": in_5_minutes},
        "notified": False,
        "completed": False,
    })

    async for task in due_tasks_cursor:
        print(f"  -> Found due task: '{task['name']}' for user {task['user_id']}")
        
        try:
            user_id_obj = ObjectId(task['user_id'])
        except Exception:
            print(f"     - Invalid user_id format: {task['user_id']}. Skipping.")
            continue
            
        user = await db.users.find_one({"_id": user_id_obj})
        
        if user and user.get("push_subscriptions"):
            payload = {
                "title": "Task Reminder!",
                "body": f"It's time for your task: {task['name']}"
            }
            
            # Send notification to all devices/subscriptions for this user
            subscriptions_to_keep = []
            for sub in user["push_subscriptions"]:
                try:
                    webpush(
                        subscription_info=sub,
                        data=json.dumps(payload),
                        vapid_private_key=settings.VAPID_PRIVATE_KEY,
                        vapid_claims={"sub": f"mailto:{settings.VAPID_EMAIL}"}
                    )
                    print(f"     - Notification sent to endpoint: {sub.get('endpoint', 'N/A')[:30]}...")
                    subscriptions_to_keep.append(sub)
                except WebPushException as ex:
                    print(f"     - Error sending notification: {ex}")
                    # If subscription is expired (410 Gone), don't add it back
                    if ex.response and ex.response.status_code == 410:
                        print(f"     - Subscription expired. Removing for user {user['_id']}.")
                    else:
                        subscriptions_to_keep.append(sub) # Keep if another error occurred

            # Update user's subscriptions if any were removed
            if len(subscriptions_to_keep) < len(user["push_subscriptions"]):
                 await db.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"push_subscriptions": subscriptions_to_keep}}
                )

            # Mark the task as notified to prevent sending it again
            await db.tasks.update_one(
                {"_id": task["_id"]},
                {"$set": {"notified": True}}
            )
        else:
            print(f"  -> User {task['user_id']} has no subscriptions. Marking as notified.")
            # Mark as notified anyway to prevent re-checking for a user with no subscriptions
            await db.tasks.update_one(
                {"_id": task["_id"]},
                {"$set": {"notified": True}}
            )

def start_scheduler():
    """Starts the task scheduler."""
    # Schedule the job to run every minute
    scheduler.add_job(check_for_due_tasks, 'interval', minutes=1, id="due_task_checker")
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started. Will check for tasks every minute.")

def stop_scheduler():
    """Stops the task scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped.")