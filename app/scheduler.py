from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from app.config import settings
from app.db import get_database
from datetime import datetime, time, timedelta, timezone
from app.agents.plan_agent import generate_next_week_plan
from app.models import Plan, Task, User
import logging
from bson import ObjectId

# Configure the job store to use MongoDB, allowing persistence across restarts
jobstores = {
    'default': MongoDBJobStore(
        database=settings.DB_NAME,
        collection="apscheduler_jobs",
        host=settings.MONGODB_URI
    )
}

# Initialize the scheduler
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="UTC")

logger = logging.getLogger(__name__)


async def regenerate_expiring_plans():
    """
    Scheduled job to find plans ending today and generate the next week's plan.
    """
    logger.info("Scheduler: Running job to regenerate expiring plans.")
    db = get_database()
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.utc)

    expiring_plans_cursor = db.plans.find({
        "end_date": {"$gte": start_of_day, "$lte": end_of_day}
    })
    
    async for plan_doc in expiring_plans_cursor:
        try:
            user_id = plan_doc.get("user_id")
            logger.info(f"Found expiring plan for user_id: {user_id}")
            
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                logger.warning(f"User not found for user_id: {user_id}. Skipping plan regeneration.")
                continue

            # 1. Call agent to generate the new plan content
            new_plan_content = await generate_next_week_plan(user=user_doc, previous_plan=plan_doc)

            if not new_plan_content or not new_plan_content.get("daily_plan"):
                logger.error(f"AI agent failed to return valid content for user {user_id}.")
                continue
            
            # 2. Create and save the new Plan object
            new_start_date_obj = today + timedelta(days=1)
            new_start_date = datetime.combine(new_start_date_obj, time.min, tzinfo=timezone.utc)
            new_end_date = datetime.combine(new_start_date_obj + timedelta(days=6), time.max, tzinfo=timezone.utc)

            new_plan = Plan(
                user_id=str(user_id),
                type=plan_doc["type"],
                content=new_plan_content,
                start_date=new_start_date,
                end_date=new_end_date
            )
            
            plan_data_to_insert = new_plan.model_dump(by_alias=True, exclude=["id"])
            result = await db.plans.insert_one(plan_data_to_insert)
            new_plan_id = str(result.inserted_id)
            logger.info(f"Successfully created new plan {new_plan_id} for user {user_id}.")

            # 3. Create tasks for the new plan
            tasks_to_create = []
            daily_schedule = new_plan_content.get("daily_plan", [])
            for day_plan in daily_schedule:
                day_number = day_plan.get("day", 1)
                task_date_part = new_start_date_obj + timedelta(days=day_number - 1)

                if plan_doc["type"] in ["workout", "workout and diet"] and "exercises" in day_plan:
                    for exercise in day_plan.get("exercises", []):
                        task_time_data = exercise.get("task_time", {})
                        hour = task_time_data.get("hour", 0)
                        minute = task_time_data.get("minute", 0)
                        task_datetime = datetime.combine(task_date_part, time(hour=hour, minute=minute), tzinfo=timezone.utc)
                        tasks_to_create.append(Task(user_id=str(user_id), plan_id=new_plan_id, task_date=task_datetime, name=exercise.get("name"), details=exercise, type="workout").model_dump(by_alias=True, exclude=["id"]))

                if plan_doc["type"] in ["diet", "workout and diet"] and "meals" in day_plan:
                    for meal in day_plan.get("meals", []):
                        task_time_data = meal.get("task_time", {})
                        hour = task_time_data.get("hour", 0)
                        minute = task_time_data.get("minute", 0)
                        task_datetime = datetime.combine(task_date_part, time(hour=hour, minute=minute), tzinfo=timezone.utc)
                        tasks_to_create.append(Task(user_id=str(user_id), plan_id=new_plan_id, task_date=task_datetime, name=meal.get("meal_name"), details=meal, type="diet").model_dump(by_alias=True, exclude=["id"]))
            
            if tasks_to_create:
                await db.tasks.insert_many(tasks_to_create)
                logger.info(f"Successfully created {len(tasks_to_create)} tasks for new plan {new_plan_id}.")

        except Exception as e:
            logger.error(f"Error regenerating plan for user {plan_doc.get('user_id')}: {e}", exc_info=True)
            
    logger.info("Scheduler: Finished job to regenerate expiring plans.")
