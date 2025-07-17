from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import ChatRequest, ChatResponse, Task
from app.agents.chat_agent import get_chat_response
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, time, timezone
import json

router = APIRouter(prefix="/chat", tags=["Chat"])

USER_COLLECTION = "users"
PLAN_COLLECTION = "plans"
TASK_COLLECTION = "tasks"


def format_plan_context(plan: dict) -> str:
    """Formats the plan dictionary into a readable string for the AI."""
    if not plan or "content" not in plan:
        return "The user does not have a plan generated yet."
    
    content = plan.get("content", {})
    title = content.get('title', 'N/A')
    
    # Create a brief summary instead of dumping the whole JSON.
    plan_summary = f"Plan Title: {title}\nPlan Type: {plan.get('type', 'N/A')}"
    return plan_summary


def format_tasks_context(tasks: list) -> str:
    """Formats the list of task objects into a readable string for the AI."""
    if not tasks:
        return "The user has no tasks scheduled for today."
    
    task_strings = []
    for task in tasks:
        status = "Completed" if task.get("completed") else "Pending"
        task_strings.append(f"- {task['description']} (Status: {status})")
        
    return "Today's Tasks:\n" + "\n".join(task_strings)


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the chatbot"
)
async def chat_with_agent(
    chat_request: ChatRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Handles a user's message, retrieves their latest plan and today's tasks (RAG),
    gets a response from the chat agent, and relies on the agent to manage chat history.
    """
    user_id_str = chat_request.user_id
    user_message_content = chat_request.message

    # 1. Validate the User ID format and existence
    try:
        user_obj_id = ObjectId(user_id_str)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {user_id_str}"
        )

    user = await db[USER_COLLECTION].find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id_str} not found"
        )
        
    # 2. --- RAG: Retrieve Context ---
    # 2a. Fetch the user's most recent plan
    latest_plan = await db[PLAN_COLLECTION].find_one(
        {"user_id": user_id_str},
        sort=[("created_at", -1)]
    )
    plan_context = format_plan_context(latest_plan)

    # 2b. Fetch the user's tasks for the current day
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.utc)

    tasks_cursor = db[TASK_COLLECTION].find({
        "user_id": user_id_str,
        "task_date": {
            "$gte": start_of_day,
            "$lte": end_of_day
        }
    })
    todays_tasks = await tasks_cursor.to_list(length=None)
    tasks_context = format_tasks_context(todays_tasks)
    print(f"Plan Context: {plan_context}")
    print(f"Tasks Context: {tasks_context}")

    # 3. Get a response from the chat agent, now with context.
    # We pass the user_id as the session_id for history management.
    agent_response_content = await get_chat_response(
        user_input=user_message_content,
        session_id=user_id_str,
        plan_context=plan_context,
        tasks_context=tasks_context
    )

    # 4. Return the agent's response
    return ChatResponse(response=agent_response_content)