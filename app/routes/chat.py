from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import ChatRequest, ChatResponse, User, ChatSession
from app.agents.chat_agent import get_chat_response
from app.vector_store import query_vector_store
from app.security import get_current_user
from datetime import datetime, time, timezone
from typing import List, Any
from bson import ObjectId
from app.config import settings
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory


router = APIRouter(prefix="/chat", tags=["Chat"])

PLAN_COLLECTION = "plans"
TASK_COLLECTION = "tasks"
CHAT_SESSIONS_COLLECTION = "chat_sessions"
CHAT_HISTORIES_COLLECTION = "chat_histories"


def format_plan_context(plan: dict) -> str:
    """Formats the plan dictionary into a readable string for the AI."""
    if not plan or "content" not in plan:
        return "The user does not have a plan generated yet."
    
    content = plan.get("content", {})
    title = content.get('title', 'N/A')
    
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


@router.get(
    "/sessions",
    response_model=List[ChatSession],
    summary="List all chat sessions for the current user"
)
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Retrieves a list of all chat sessions started by the user."""
    sessions_cursor = db[CHAT_SESSIONS_COLLECTION].find(
        {"user_id": str(current_user.id)}
    ).sort("created_at", -1)
    sessions = await sessions_cursor.to_list(length=None)
    return sessions


@router.get(
    "/sessions/{session_id}/history",
    response_model=List[Any],
    summary="Get chat history for a specific session"
)
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieves the full message history for a given session,
    ensuring the session belongs to the current user.
    """
    try:
        session_obj_id = ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session ID format.")

    # Security check: Verify the session belongs to the logged-in user.
    session_meta = await db[CHAT_SESSIONS_COLLECTION].find_one(
        {"_id": session_obj_id, "user_id": str(current_user.id)}
    )
    if not session_meta:
        raise HTTPException(status_code=404, detail="Chat session not found or permission denied.")

    # Fetch history using LangChain's helper
    history = MongoDBChatMessageHistory(
        connection_string=settings.MONGODB_URI,
        session_id=session_id,
        database_name=settings.DB_NAME,
        collection_name=CHAT_HISTORIES_COLLECTION,
    )
    # The `messages` property contains a list of BaseMessage objects.
    # FastAPI's Pydantic integration will serialize them to JSON.
    return history.messages


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
    Handles a user's message.
    - If `session_id` is provided, continues the conversation.
    - If `session_id` is null, creates a new chat session.
    - Retrieves RAG context and gets a response from the chat agent.
    - Returns the agent's response and the active `session_id`.
    """
    user_id_str = str(current_user.id)
    session_id = chat_request.session_id

    if not session_id:
        # Start a new session
        title = " ".join(chat_request.message.split()[:5])
        if not title: title = "New Chat"
        
        new_session_doc = {
            "user_id": user_id_str,
            "title": title,
            "created_at": datetime.now(timezone.utc)
        }
        result = await db[CHAT_SESSIONS_COLLECTION].insert_one(new_session_doc)
        session_id = str(result.inserted_id)
    else:
        # Validate existing session
        try:
            session_obj_id = ObjectId(session_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid session ID format.")
        
        session_meta = await db[CHAT_SESSIONS_COLLECTION].find_one(
            {"_id": session_obj_id, "user_id": user_id_str}
        )
        if not session_meta:
            raise HTTPException(status_code=403, detail="Access to this chat session is forbidden.")
        
    # --- RAG: Retrieve Context ---
    latest_plan = await db[PLAN_COLLECTION].find_one({"user_id": user_id_str}, sort=[("created_at", -1)])
    plan_context = format_plan_context(latest_plan)

    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.utc)
    tasks_cursor = db[TASK_COLLECTION].find({"user_id": user_id_str, "task_date": {"$gte": start_of_day, "$lte": end_of_day}})
    todays_tasks = await tasks_cursor.to_list(length=None)
    tasks_context = format_tasks_context(todays_tasks)

    retrieved_docs = await query_vector_store(user_id_str, chat_request.message)
    document_context = format_document_context(retrieved_docs)
    
    # --- Get Agent Response ---
    agent_response_content = await get_chat_response(
        user_input=chat_request.message,
        session_id=session_id,
        plan_context=plan_context,
        tasks_context=tasks_context,
        document_context=document_context
    )

    return ChatResponse(response=agent_response_content, session_id=session_id)