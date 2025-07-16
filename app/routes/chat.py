# app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import ChatRequest, ChatResponse
from app.agents.chat_agent import get_chat_response
from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/chat", tags=["Chat"])

USER_COLLECTION = "users"

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
    Handles a user's message, gets a response from the chat agent,
    and relies on the agent to manage chat history using the user_id as the session_id.
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
        
    # 2. Get a response from the chat agent.
    # We pass the user_id as the session_id. The agent now handles fetching
    # the correct history and saving the new user message and its response.
    agent_response_content = await get_chat_response(
        user_input=user_message_content,
        session_id=user_id_str
    )

    # 3. Return the agent's response
    return ChatResponse(response=agent_response_content)