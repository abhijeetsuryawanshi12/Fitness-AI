from elevenlabs import play
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

elevenlabs_api_key = os.environ.get("ELEVEN_LABS_API_KEY")
if not elevenlabs_api_key:
    raise ValueError("ELEVEN_LABS_API_KEY environment variable not set.")

elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

async def generate_audio(text):
    """Generate and play audio from text using ElevenLabs"""
    try:
        print("🔊 Generating audio...")

    # Generate audio stream
        audio_stream = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # George voice
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Play the audio
        play(audio_stream)
        print("✅ Audio playback completed")
            
    except Exception as e:
        print(f"❌ Error generating audio: {e}")