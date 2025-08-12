import asyncio
import base64
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, time, timezone

from app.db import get_database
from app.models import User, VoiceChatResponse
from app.security import get_current_user
from app.services.audio_service import ensure_mp3_bytes
from app.services.stt_service import transcribe_audio_bytes
from app.services.tts_service import text_to_speech_bytes
from app.agents.chat_agent import get_chat_response
from app.vector_store import query_vector_store

# Import context formatters and constants from the text chat route
from app.routes.chat import (
    format_plan_context,
    format_tasks_context,
    format_document_context,
    PLAN_COLLECTION,
    TASK_COLLECTION,
)

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

@router.post(
    "/chat",
    response_model=VoiceChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Handle a full voice chat interaction"
)
async def voice_chat(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Receives an audio file, transcribes it, gets a contextual response from the
    chat agent, converts the response to speech, and returns the transcription,
    agent response text, and TTS audio.
    """
    user_id_str = str(current_user.id)
    
    # 1. Read, Convert, and Transcribe Audio
    try:
        audio_bytes = await file.read()
        mp3_bytes = ensure_mp3_bytes(audio_bytes)
        
        # Run the synchronous transcription function in a thread to avoid blocking the event loop
        user_text = await asyncio.to_thread(transcribe_audio_bytes, mp3_bytes)
        
        if not user_text:
            raise HTTPException(status_code=400, detail="Could not understand audio or audio was empty.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed during speech-to-text processing: {e}")

    # 2. Gather Context (RAG - same logic as text chat for consistency)
    latest_plan = await db[PLAN_COLLECTION].find_one({"user_id": user_id_str}, sort=[("created_at", -1)])
    plan_context = format_plan_context(latest_plan)
    
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(today, time.max, tzinfo=timezone.utc)
    tasks_cursor = db[TASK_COLLECTION].find({"user_id": user_id_str, "task_date": {"$gte": start_of_day, "$lte": end_of_day}})
    todays_tasks = await tasks_cursor.to_list(length=None)
    tasks_context = format_tasks_context(todays_tasks)
    
    retrieved_docs = await query_vector_store(user_id_str, user_text)
    document_context = format_document_context(retrieved_docs)

    # 3. Get AI Chat Response
    try:
        ai_text = await get_chat_response(
            user_input=user_text,
            session_id=user_id_str,
            plan_context=plan_context,
            tasks_context=tasks_context,
            document_context=document_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI agent failed to generate a response: {e}")

    # 4. Convert AI Response to Speech (TTS)
    try:
        tts_audio_bytes = await text_to_speech_bytes(ai_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed during text-to-speech conversion: {e}")

    # 5. Encode audio to base64 and return the complete response object
    audio_b64 = base64.b64encode(tts_audio_bytes).decode('utf-8')
    
    return VoiceChatResponse(
        user_text=user_text,
        ai_text=ai_text,
        audio_b64=audio_b64
    )