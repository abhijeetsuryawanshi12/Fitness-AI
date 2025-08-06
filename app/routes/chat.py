# app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import ChatRequest, ChatResponse, User
from app.agents.chat_agent import get_chat_response
from app.vector_store import query_vector_store
from app.security import get_current_user
from datetime import datetime, time, timezone
import json

router = APIRouter(prefix="/chat", tags=["Chat"])

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
        task_strings.append(f"- {task['name']} (Status: {status})")
        
    return "Today's Tasks:\n" + "\n".join(task_strings)


def format_document_context(docs: list) -> str:
    """Formats the retrieved document chunks into a readable string for the AI."""
    if not docs:
        return "No relevant information found in the user's documents for this query."
    
    context_strings = []
    for doc in docs:
        context_strings.append(f"From document '{doc['filename']}':\n---\n{doc['content']}\n---")
        
    return "\n\n".join(context_strings)


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the chatbot"
)
async def chat_with_agent(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Handles a user's message, retrieves context from their plan, tasks, and uploaded documents (RAG),
    gets a response from the chat agent, and relies on the agent to manage chat history.
    """
    user_id_str = str(current_user.id)
    user_message_content = chat_request.message
        
    # --- RAG: Retrieve Context ---
    # Fetch the user's most recent plan
    latest_plan = await db[PLAN_COLLECTION].find_one(
        {"user_id": user_id_str},
        sort=[("created_at", -1)]
    )
    plan_context = format_plan_context(latest_plan)

    # Fetch the user's tasks for the current day
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

    # Fetch relevant document chunks from the vector store
    retrieved_docs = await query_vector_store(user_id_str, user_message_content)
    document_context = format_document_context(retrieved_docs)
    
    print(f"Plan Context: {plan_context}")
    print(f"Tasks Context: {tasks_context}")
    print(f"Document Context: {document_context}")

    # Get a response from the chat agent, now with all context.
    # Use the user's ID from the token as the session_id for chat history
    agent_response_content = await get_chat_response(
        user_input=user_message_content,
        session_id=user_id_str,
        plan_context=plan_context,
        tasks_context=tasks_context,
        document_context=document_context
    )

    # Return the agent's response
    return ChatResponse(response=agent_response_content)