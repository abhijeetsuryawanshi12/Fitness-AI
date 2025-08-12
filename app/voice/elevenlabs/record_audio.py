# streamlit_assemblyai_agent_tts.py
import streamlit as st
import requests
import time
import tempfile
import os
import io
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# load env
load_dotenv()

# --- YOUR EXISTING IMPORTS (unchanged) ---
# these must exist and be the functions you provided
from agent import generate_response
from tts import text_to_speech_bytes

# --- Configuration ---
ASSEMBLYAI_API_KEY = os.environ.get("ASSEMBLYAI_API_KEY", "")
if not ASSEMBLYAI_API_KEY:
    st.error("Please set ASSEMBLYAI_API_KEY in environment or .env file.")
BASE_URL = "https://api.assemblyai.com"
HEADERS_AAI = {"authorization": ASSEMBLYAI_API_KEY}

st.set_page_config(page_title="Record → AssemblyAI → Agent → TTS", layout="centered")
st.title("Record → AssemblyAI → Agent → TTS")

st.markdown(
    """
Record audio in the browser, convert/save to MP3, upload to AssemblyAI, transcribe,
use your `agent.generate_response` and `tts.text_to_speech_bytes`, then play the TTS in the browser.
"""
)

# Try to import pydub for format conversion
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except Exception:
    PYDUB_AVAILABLE = False

# UI
col1, col2 = st.columns([3,1])
with col1:
    st.header("Record / Upload")
    st.write("Use the browser recorder or upload an audio file (wav/ogg/mp3).")
    audio_input = st.audio_input("Record a voice message")  # Streamlit >=1.27
    uploaded_file = st.file_uploader("Or upload audio file", type=["wav","mp3","ogg","m4a"])

with col2:
    st.header("Options")
    speech_model = st.selectbox("AssemblyAI speech model", options=["slam-1", "large-v2"], index=0)
    run_button = st.button("Process & Reply")

# Helper: write bytes to temp mp3 file (with optional conversion using pydub)
def ensure_mp3_bytes(input_bytes: bytes, input_format_hint: str = None) -> bytes:
    """
    Return MP3 bytes for the provided audio bytes.
    If already MP3 (by header) returns as-is. Otherwise convert using pydub if available.
    """
    # Quick MP3 detection
    if input_bytes[:3] == b"ID3" or input_bytes[:2] == b"\xff\xfb":  # ID3 tag or MP3 frame
        return input_bytes

    if not PYDUB_AVAILABLE:
        # If no pydub and input is not mp3, try to return as-is (AssemblyAI supports wav/ogg too)
        return input_bytes

    # pydub conversion: format hint if available (e.g., "wav", "ogg")
    buf = io.BytesIO(input_bytes)
    fmt = input_format_hint or None
    # If format not guessed, let pydub detect
    audio = AudioSegment.from_file(buf, format=fmt)
    out_buf = io.BytesIO()
    audio.export(out_buf, format="mp3", bitrate="128k")
    return out_buf.getvalue()

def upload_bytes_to_assemblyai(file_bytes: bytes) -> str:
    """
    Uploads raw bytes to AssemblyAI /v2/upload and returns the upload_url.
    """
    upload_url = None
    upload_endpoint = f"{BASE_URL}/v2/upload"
    # streaming upload
    with requests.post(upload_endpoint, headers=HEADERS_AAI, data=file_bytes) as resp:
        resp.raise_for_status()
        upload_url = resp.json().get("upload_url")
    return upload_url

def request_transcription(upload_url: str, speech_model: str = "slam-1") -> str:
    """
    Kicks off transcription and returns transcript_id.
    """
    transcript_endpoint = f"{BASE_URL}/v2/transcript"
    payload = {"audio_url": upload_url, "speech_model": speech_model}
    r = requests.post(transcript_endpoint, json=payload, headers=HEADERS_AAI)
    r.raise_for_status()
    return r.json()["id"]

def poll_transcription(transcript_id: str, poll_interval: float = 2.0, timeout: int = 120) -> dict:
    """
    Poll the /v2/transcript endpoint until 'completed' or 'error'.
    Returns the final JSON response.
    """
    polling_endpoint = f"{BASE_URL}/v2/transcript/{transcript_id}"
    start = time.time()
    while True:
        r = requests.get(polling_endpoint, headers=HEADERS_AAI)
        r.raise_for_status()
        j = r.json()
        status = j.get("status")
        if status == "completed":
            return j
        if status == "error":
            raise RuntimeError("Transcription error: " + str(j.get("error")))
        if time.time() - start > timeout:
            raise TimeoutError("Transcription polling timed out.")
        time.sleep(poll_interval)

# Main flow
if run_button:
    # obtain bytes from recorder or uploader
    if audio_input is None and uploaded_file is None:
        st.error("Record or upload audio first.")
        st.stop()

    # prefer recorded audio (browser)
    if audio_input is not None:
        # audio_input is a BytesIO-like object
        audio_bytes = audio_input.getvalue()
        # try to guess format; streamlit recorder usually gives WAV bytes
        format_hint = None
    else:
        audio_bytes = uploaded_file.read()
        # guess from filename
        format_hint = uploaded_file.type.split("/")[-1] if uploaded_file.type else None

    st.info("Converting to MP3 (if needed)...")
    try:
        mp3_bytes = ensure_mp3_bytes(audio_bytes, input_format_hint=format_hint)
    except Exception as e:
        st.exception(e)
        st.stop()

    # Optional: save mp3 for debugging
    tmp_mp3_path = Path(tempfile.gettempdir()) / f"input_{int(time.time())}.mp3"
    tmp_mp3_path.write_bytes(mp3_bytes)
    st.audio(str(tmp_mp3_path))

    try:
        st.info("Uploading to AssemblyAI...")
        upload_url = upload_bytes_to_assemblyai(mp3_bytes)
        st.success("Uploaded to AssemblyAI.")
    except Exception as e:
        st.exception(e)
        st.stop()

    try:
        st.info("Requesting transcription...")
        transcript_id = request_transcription(upload_url, speech_model=speech_model)
    except Exception as e:
        st.exception(e)
        st.stop()

    # Poll for transcription
    with st.spinner("Transcribing (AssemblyAI)..."):
        try:
            transcript_result = poll_transcription(transcript_id, poll_interval=2.0, timeout=180)
            transcript_text = transcript_result.get("text", "")
            st.success("Transcription complete.")
            st.write("**You said:**", transcript_text)
        except Exception as e:
            st.exception(e)
            st.stop()

    # -------------- Use your agent to generate a response --------------
    st.info("Generating response from agent...")
    try:
        # your generate_response is async in your original code; call with asyncio.run
        ai_response = asyncio.run(generate_response(transcript_text))
    except Exception as e:
        # If generate_response is sync fallback
        try:
            ai_response = generate_response(transcript_text)
        except Exception as e2:
            st.exception(e2)
            st.stop()

    st.write("**AI Response:**", ai_response)

    # -------------- Convert AI response to speech using your tts --------------
    st.info("Calling your text_to_speech_bytes (ElevenLabs) ...")
    try:
        tts_bytes = asyncio.run(text_to_speech_bytes(ai_response))
    except Exception as e:
        # fallback if tts is sync
        try:
            tts_bytes = text_to_speech_bytes(ai_response)
        except Exception as e2:
            st.exception(e2)
            st.stop()

    # tts_bytes should be bytes (your tts uses mp3_44100_128), so attempt to detect
    if not isinstance(tts_bytes, (bytes, bytearray)):
        st.error("tts.text_to_speech_bytes did not return bytes.")
        st.stop()

    # save and play
    out_path = Path(tempfile.gettempdir()) / f"ai_reply_{int(time.time())}.mp3"
    out_path.write_bytes(tts_bytes)
    st.success("Generated TTS saved.")
    st.audio(str(out_path))

    st.balloons()
