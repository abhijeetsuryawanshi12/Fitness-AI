# app/agents/tools.py
from app.db import get_database
from app.vector_store import query_vector_store
from app.agents.tasks_agent import generate_one_day_plan
from bson import ObjectId
from datetime import datetime, time, timezone, date
from typing import List, Dict, Any

def _sanitize_for_json(data: Any) -> Any:
    """
    Recursively traverses a data structure and converts non-JSON-serializable
    types (like datetime, date, and ObjectId) to strings.
    """
    if isinstance(data, dict):
        return {key: _sanitize_for_json(value) for key, value in data.items()}
    if isinstance(data, list):
        return [_sanitize_for_json(item) for item in data]
    if isinstance(data, (datetime, date)):
        return data.isoformat()
    if isinstance(data, ObjectId):
        return str(data)
    return data


async def get_user_context_tool(user_id: str) -> Dict[str, Any]:
    """Fetches the user's profile, latest plan, and today's tasks from MongoDB."""
    db = get_database()  # Relies on global db instance from db.py

    # Fetch user profile
    user_profile = await db.users.find_one({"_id": ObjectId(user_id)})

    # Fetch the most recent plan
    latest_plan = await db.plans.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )

    # Fetch today's tasks
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.utc)
    tasks_cursor = db.tasks.find({
        "user_id": user_id,
        "task_date": {"$gte": start_of_day, "$lte": end_of_day}
    })
    todays_tasks = await tasks_cursor.to_list(length=None)

    # Sanitize all fetched data before returning to ensure it's JSON-serializable
    return {
        "user_profile": _sanitize_for_json(user_profile) or {},
        "plan": _sanitize_for_json(latest_plan) or {},
        "tasks": _sanitize_for_json(todays_tasks)
    }


async def rag_search_tool(user_id: str, query: str) -> str:
    """Performs a RAG search on the user's documents and returns formatted context."""
    retrieved_docs = await query_vector_store(user_id, query)
    if not retrieved_docs:
        return "No relevant information was found in your documents."
    
    context_strings = []
    for doc in retrieved_docs:
        context_strings.append(f"From document '{doc['filename']}':\n---\n{doc['content']}\n---")
        
    return "\n\n".join(context_strings)


async def regenerate_todays_plan_tool(user_profile: dict, plan: dict, todays_tasks: List[dict], suggestion: str) -> Dict[str, Any]:
    """
    Deletes today's tasks and calls the plan generation agent to create a new,
    adapted one-day plan based on a suggestion (e.g., 'tired', 'lighter workout').
    Returns the newly generated plan content and tasks.
    """
    db = get_database()
    
    # Add defensive checks for missing data in the state
    if not user_profile or '_id' not in user_profile:
        return {"error": "User profile is missing or invalid in the current state."}
    if not plan or '_id' not in plan:
        return {"error": "Active plan is missing or invalid in the current state."}

    plan_id = plan.get("_id")
    user_id_str = user_profile.get("_id")
    request_type = plan.get("type", "workout and diet")  # Default if not found

    # 1. Delete today's existing tasks if any
    if todays_tasks:
        task_ids_to_delete = [ObjectId(task["_id"]) for task in todays_tasks]
        if task_ids_to_delete:
            await db.tasks.delete_many({"_id": {"$in": task_ids_to_delete}})
            print(f"Deleted {len(task_ids_to_delete)} old tasks for today.")

    # 2. Generate a new one-day plan and associated tasks
    print(f"Regenerating today's plan with suggestion: {suggestion}")
    try:
        # **FIXED**: Removed the unnecessary database refetch.
        # We directly use the sanitized 'user_profile' from the agent's state.
        # It contains all the necessary data as simple types.
        new_plan_content = await generate_one_day_plan(
            user=user_profile, # Use the sanitized dictionary directly
            plan_id=plan_id,
            request_type=request_type,
            db=db,
            suggestion=suggestion
        )

        # 3. Fetch the newly created tasks to return to the agent state
        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, time.max, tzinfo=timezone.utc)
        new_tasks_cursor = db.tasks.find({
            "user_id": user_id_str,
            "plan_id": plan_id,
            "task_date": {"$gte": start_of_day, "$lte": end_of_day}
        })
        newly_created_tasks = await new_tasks_cursor.to_list(length=None)
        
        return {
            "new_plan_content": _sanitize_for_json(new_plan_content),
            "new_tasks": _sanitize_for_json(newly_created_tasks)
        }
    except Exception as e:
        # Add more detailed error logging
        import traceback
        traceback.print_exc()
        print(f"Error during plan regeneration: {e}")
        return {"error": f"Failed to regenerate plan: {e}"}