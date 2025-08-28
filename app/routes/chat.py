# app/routes/chat.py
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

# --- Import the LangGraph agent and its state definition ---
from app.graphs.coach_agent import coach_agent_graph, AgentState

router = APIRouter(prefix="/chat", tags=["Chat"])

CHAT_SESSIONS_COLLECTION = "chat_sessions"
CHAT_HISTORIES_COLLECTION = "chat_histories"

# --- NEW: Simple In-Memory Session State Cache ---
# This dictionary will store state between user messages for a given session.
# In a production environment with multiple server instances,
# this should be replaced with a persistent key-value store like Redis.
session_state_cache = {}


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

    # --- Session Management ---
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

    # --- LangGraph Agent Invocation with State Management ---
    
    # 1. Get chat history
    history = MongoDBChatMessageHistory(
        connection_string=settings.MONGODB_URI, session_id=session_id,
        database_name=settings.DB_NAME, collection_name=CHAT_HISTORIES_COLLECTION,
    )

    # 2. Prepare the initial state for the graph
    initial_state: AgentState = {
        "user_id": user_id_str,
        "input": chat_request.message,
        "chat_history": history.messages,
        "user_profile": {}, "plan": {}, "tasks": [], "rag_context": "", "response": "",
        "pending_suggestion": None,
    }

    # **MODIFIED**: Load persistent state from our cache for this session
    if session_id in session_state_cache:
        cached_state = session_state_cache.get(session_id, {})
        initial_state.update(cached_state)
        print(f"Loaded state from cache for session {session_id}: {cached_state}")

    # 3. Asynchronously invoke the graph
    config = {"recursion_limit": 50}
    final_state = await coach_agent_graph.ainvoke(initial_state, config=config)
    
    agent_response = final_state.get("response", "I'm sorry, I encountered an issue and can't respond right now.")

    # 4. Manually update history
    history.add_user_message(chat_request.message)
    history.add_ai_message(agent_response)

    # **MODIFIED**: Save or clear the relevant state back to the cache
    if final_state.get("pending_suggestion"):
        # If the graph ended with a pending suggestion, save it.
        session_state_cache[session_id] = {
            "pending_suggestion": final_state["pending_suggestion"]
        }
        print(f"Saved state to cache for session {session_id}: {session_state_cache[session_id]}")
    elif session_id in session_state_cache:
        # If the graph ended and there's NO pending suggestion, it means the
        # suggestion was either used or cancelled. Clean up the cache.
        del session_state_cache[session_id]
        print(f"Cleared cached state for session {session_id}")
        
    return ChatResponse(response=agent_response, session_id=session_id)