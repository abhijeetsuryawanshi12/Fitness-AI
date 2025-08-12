import io
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub is not installed. Audio conversion will be skipped. `pip install pydub`")


def ensure_mp3_bytes(input_bytes: bytes) -> bytes:
    """
    Converts audio bytes to MP3 format if not already MP3.
    This standardizes audio before sending to STT services.
    """
    if not PYDUB_AVAILABLE:
        return input_bytes # Skip conversion if pydub is missing

    try:
        # pydub can often auto-detect the format from the buffer
        audio = AudioSegment.from_file(io.BytesIO(input_bytes))
        
        out_buf = io.BytesIO()
        audio.export(out_buf, format="mp3", bitrate="128k")
        return out_buf.getvalue()
    except Exception as e:
        print(f"Could not convert audio to MP3: {e}. Returning original bytes.")
        # If conversion fails, return the original bytes as a fallback.
        # AssemblyAI supports various formats, so it might still work.
        return input_bytes