import requests
import time
from app.config import settings

BASE_URL = "https://api.assemblyai.com"
HEADERS_AAI = {"authorization": settings.ASSEMBLYAI_API_KEY}

def _upload_bytes_to_assemblyai(file_bytes: bytes) -> str:
    upload_endpoint = f"{BASE_URL}/v2/upload"
    try:
        response = requests.post(upload_endpoint, headers=HEADERS_AAI, data=file_bytes)
        response.raise_for_status()
        return response.json().get("upload_url")
    except requests.exceptions.RequestException as e:
        print(f"Error uploading to AssemblyAI: {e}")
        raise

def _request_transcription(upload_url: str) -> str:
    transcript_endpoint = f"{BASE_URL}/v2/transcript"
    payload = {"audio_url": upload_url, "speech_model": "slam-1"}
    try:
        response = requests.post(transcript_endpoint, json=payload, headers=HEADERS_AAI)
        response.raise_for_status()
        return response.json()["id"]
    except requests.exceptions.RequestException as e:
        print(f"Error requesting transcription from AssemblyAI: {e}")
        raise

def _poll_transcription(transcript_id: str) -> dict:
    polling_endpoint = f"{BASE_URL}/v2/transcript/{transcript_id}"
    start_time = time.time()
    while True:
        if time.time() - start_time > 180: # 3 minute timeout
            raise TimeoutError("AssemblyAI transcription polling timed out.")
        
        try:
            response = requests.get(polling_endpoint, headers=HEADERS_AAI)
            response.raise_for_status()
            result = response.json()
            status = result.get("status")

            if status == "completed":
                return result
            if status == "error":
                raise RuntimeError(f"AssemblyAI transcription failed: {result.get('error')}")
            
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"Error polling AssemblyAI transcription: {e}")
            raise

def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """
    Transcribes audio bytes using the full AssemblyAI upload/poll process.
    This is a synchronous, blocking function.
    """
    if not settings.ASSEMBLYAI_API_KEY:
        raise ValueError("ASSEMBLYAI_API_KEY is not set.")
    
    upload_url = _upload_bytes_to_assemblyai(audio_bytes)
    if not upload_url:
        raise Exception("Failed to upload audio to AssemblyAI.")
    
    transcript_id = _request_transcription(upload_url)
    if not transcript_id:
        raise Exception("Failed to request transcription from AssemblyAI.")
        
    result = _poll_transcription(transcript_id)
    return result.get("text", "")