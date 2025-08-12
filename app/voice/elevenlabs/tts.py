from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv
from elevenlabs import play

# Load environment variables from .env file
load_dotenv()

elevenlabs_api_key = os.environ.get("ELEVEN_LABS_API_KEY")
if not elevenlabs_api_key:
    raise ValueError("ELEVEN_LABS_API_KEY environment variable not set.")

elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

async def text_to_speech_bytes(text: str) -> bytes:
    """
    Generates audio from text and returns it as bytes.
    This is suitable for a web server that needs to send audio to a client.
    """
    try:
        print("🔊 Generating audio bytes...")

        # Generate audio stream from the API
        audio_stream = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # George voice
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"  # A common, browser-compatible format
        )
        
        # The stream is an iterator of chunks. We collect all chunks into a single bytes object.
        audio_bytes = b"".join([chunk for chunk in audio_stream])

        play(audio_bytes)
        
        print("✅ Audio bytes generated successfully.")
        return audio_bytes
            
    except Exception as e:
        print(f"❌ Error generating audio bytes: {e}")
        # Re-raise or handle the exception to be caught by the API endpoint
        raise e

# Note to developer: The original `generate_audio` function which used `elevenlabs.play()` was
# replaced because it is for local script execution and plays audio on the server.
# For a web application, we must send the audio data back to the browser to be played.