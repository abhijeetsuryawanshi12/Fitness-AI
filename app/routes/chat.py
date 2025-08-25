from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import ChatRequest, ChatResponse, User, ChatSession
from app.security import get_current_user
from datetime import datetime, timezone
from typing import List, Any
from bson import ObjectId
from app.config import settings
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory

# --- NEW: Import the LangGraph agent ---
from app.graphs.coach_agent import coach_agent_graph

router = APIRouter(prefix="/chat", tags=["Chat"])

CHAT_SESSIONS_COLLECTION = "chat_sessions"
CHAT_HISTORIES_COLLECTION = "chat_histories"
USER_DATA_COLLECTION = "users"
PLANS_COLLECTION = "plans"
TASKS_COLLECTION = "tasks"

# (The utility functions for listing sessions and getting history remain the same)
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

    session_meta = await db[CHAT_SESSIONS_COLLECTION].find_one(
        {"_id": session_obj_id, "user_id": str(current_user.id)}
    )
    if not session_meta:
        raise HTTPException(status_code=404, detail="Chat session not found or permission denied.")

    history = MongoDBChatMessageHistory(
        connection_string=settings.MONGODB_URI,
        session_id=session_id,
        database_name=settings.DB_NAME,
        collection_name=CHAT_HISTORIES_COLLECTION,
    )
    return history.messages

# --- REFACTORED CHAT ENDPOINT ---
@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the AI Coach"
)
async def chat_with_agent(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Handles a user's message using the new LangGraph-based AI Coach agent.
    It manages session history and orchestrates complex, multi-step responses.
    """

    user_id_str = str(current_user.id)
    session_id = chat_request.session_id

    user_data = await db[USER_DATA_COLLECTION].find(
        {"user_id": str(current_user.id)}
    )

    plan = await db[PLANS_COLLECTION].find(
        {"user_id": str(current_user.id)}
    )

    tasks = await db[TASKS_COLLECTION].find(
        {"user_id": str(current_user.id)}
    )

    # --- Session Management (Unchanged) ---
    if not session_id:
        title = " ".join(chat_request.message.split()[:5]) or "New Chat"
        new_session_doc = {"user_id": user_id_str, "title": title, "created_at": datetime.now(timezone.utc)}
        result = await db[CHAT_SESSIONS_COLLECTION].insert_one(new_session_doc)
        session_id = str(result.inserted_id)
    else:
        try:
            session_obj_id = ObjectId(session_id)
            session_meta = await db[CHAT_SESSIONS_COLLECTION].find_one({"_id": session_obj_id, "user_id": user_id_str})
            if not session_meta:
                raise HTTPException(status_code=403, detail="Access to this chat session is forbidden.")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid session ID format.")

    # --- NEW: Invoke the LangGraph Agent ---
    
    # 1. Get chat history
    history = MongoDBChatMessageHistory(
        connection_string=settings.MONGODB_URI, session_id=session_id,
        database_name=settings.DB_NAME, collection_name=CHAT_HISTORIES_COLLECTION,
    )

    # 2. Prepare the initial state for the graph
    initial_state = {
        "user_id": user_id_str,
        "input": chat_request.message,
        "chat_history": history.messages,
        "user_data": user_data,
        "plan": plan,
        "tasks": tasks,
        "notifications_to_send": [], # Initialize as empty
        "rag_context": "" # Initialize as empty
    }
    
    # 3. Asynchronously invoke the graph
    config = {"configurable": {"session_id": session_id}} # This might be useful for LangServe later
    final_state = await coach_agent_graph.ainvoke(initial_state, config=config)
    
    agent_response = final_state.get("response", "I'm sorry, I encountered an issue and can't respond right now.")

    # 4. Manually update history (LangGraph doesn't auto-manage it like RunnableWithMessageHistory)
    history.add_user_message(chat_request.message)
    history.add_ai_message(agent_response)

    # 5. TODO: Trigger any notifications the agent decided to send
    if final_state.get('notifications_to_send'):
        # from app.tasks import send_push_notification
        # for notification in final_state['notifications_to_send']:
        #     send_push_notification.delay(user_id=user_id_str, message=notification['message'])
        pass
        
    return ChatResponse(response=agent_response, session_id=session_id)