from assemblyai import settings
from app.db import get_database
from app.vector_store import query_vector_store
from app.agents.plan_agent import generate_full_plan
from app.agents.tasks_agent import generate_one_day_plan
from bson import ObjectId
from datetime import datetime, time, timezone
from typing import List
from app.db import get_database
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings as st2

# --- Database & RAG Tools ---

db: AsyncIOMotorDatabase = Depends(get_database)
TASKS_COLLECTION = "tasks"

async def get_user_data_tool(user_id: str) -> dict:
    """Fetches the user's profile and their tasks for today from MongoDB."""
    db = get_database()
    
    # Fetch user profile
    user_profile = await db.users.find_one({"_id": ObjectId(user_id)})
    if user_profile:
        # Convert ObjectId to string for JSON serialization
        user_profile['_id'] = str(user_profile['_id'])

    # Fetch today's tasks
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.utc)
    tasks_cursor = db.tasks.find({
        "user_id": user_id,
        "task_date": {"$gte": start_of_day, "$lte": end_of_day}
    })
    todays_tasks = await tasks_cursor.to_list(length=None)
    for task in todays_tasks:
        task['_id'] = str(task['_id']) # Sanitize ObjectId
        plan_id = task.get('plan_id')
        request_type = task.get('type')

    return {"user_profile": user_profile, "plan_id": plan_id, "request_type": request_type, "todays_tasks": todays_tasks}

async def rag_search_tool(user_id: str, query: str) -> str:
    """Performs a RAG search on the user's documents and returns formatted context."""
    retrieved_docs = await query_vector_store(user_id, query)
    if not retrieved_docs:
        return "No relevant information was found in your documents."
    
    context_strings = []
    for doc in retrieved_docs:
        context_strings.append(f"From document '{doc['filename']}':\n---\n{doc['content']}\n---")
        
    return "\n\n".join(context_strings)

# --- Plan Adaptation Tool ---

async def regenerate_plan_tool(user_profile: dict, plan_id: str, request_type: str, todays_tasks: List[dict], suggestion: str) -> dict:
    """
    Calls the existing plan generation agent to create a new plan.
    'suggestion' is a hint from the coach agent (e.g., 'make it lighter').
    """
    # The `generate_full_plan` function needs a specific input format.
    # We can potentially add the 'suggestion' to the user's primary goal to influence the LLM.

    if suggestion == "tired":
        # Update plan for the same day
        await db[TASKS_COLLECTION].delete_many({"_id": {"$in": [task["_id"] for task in todays_tasks]}})

        modified_user_profile = user_profile.copy()
        # modified_user_profile["primary_goal"] = f"{user_profile['primary_goal']} ({suggestion})"
        client = AsyncIOMotorClient(st2.MONGODB_URI)
        db = client[st2.DB_NAME]

        print(f"Regenerating plan with suggestion: {suggestion}")
        new_plan_content = await generate_one_day_plan(modified_user_profile,plan_id, request_type, db, suggestion)
    
    # Here, we would also need the logic to save the new plan and create tasks,
    # similar to the /plan/generate endpoint. For now, we return the content.
    return new_plan_content