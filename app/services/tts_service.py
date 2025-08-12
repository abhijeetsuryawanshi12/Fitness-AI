from elevenlabs.client import ElevenLabs
from app.config import settings

# Ensure the API key is available
if not settings.ELEVEN_LABS_API_KEY:
    # This check is mainly for development; the config already warns.
    raise ValueError("ELEVEN_LABS_API_KEY environment variable not set.")

elevenlabs_client = ElevenLabs(api_key=settings.ELEVEN_LABS_API_KEY)

async def text_to_speech_bytes(text: str) -> bytes:
    """
    Generates audio from text using ElevenLabs and returns it as bytes.
    """
    try:
        # Generate audio stream from the API
        audio_stream = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # A common, clear voice (e.g., "George")
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128" # A standard, browser-compatible format
        )
        
        # The stream is an iterator of chunks. We collect them into a single bytes object.
        audio_bytes = b"".join([chunk for chunk in audio_stream])
        
        return audio_bytes
            
    except Exception as e:
        print(f"Error generating audio bytes from ElevenLabs: {e}")
        # Re-raise the exception to be caught by the API endpoint
        raise e