from app.worker import celery_app
from app.graphs.coach_agent import run_proactive_adaptation_check
import asyncio

@celery_app.task(name="notifications.send_push")
def send_push_notification(user_id: str, message: str):
    """
    Sends a push notification to a user.
    For a web app, this could trigger a Web Push notification or an in-app alert.
    """
    print(f"--- SENDING NOTIFICATION ---")
    print(f"To: User {user_id}")
    print(f"Message: {message}")
    print(f"--------------------------")
    # Actual push notification logic (e.g., using a service like OneSignal) goes here.
    return {"status": "success", "user_id": user_id}

@celery_app.task(name="adaptation.check_user_progress")
def check_user_progress(user_id: str):
    """
    A scheduled task that proactively checks a user's progress and triggers
    the coach agent to see if an adaptation is needed.
    """
    print(f"Running proactive adaptation check for user: {user_id}")
    
    # Since our agent is async, we need to run it in an event loop.
    result = asyncio.run(run_proactive_adaptation_check(user_id))
    
    # If the check resulted in a notification, send it.
    if result and result.get('notifications_to_send'):
        for notification in result['notifications_to_send']:
            send_push_notification.delay(
                user_id=user_id,
                message=notification['message']
            )
            
    return result