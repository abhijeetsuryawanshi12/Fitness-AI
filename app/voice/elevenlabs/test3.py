import pyaudio
import websockets
import json
import asyncio
import wave
from urllib.parse import urlencode
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Assume you have this file and function
from agent import generate_response 
from tts import text_to_speech_bytes

# --- Configuration ---
# It's better practice to load this from an environment variable or a config file

# AssemblyAI WebSocket Configuration
CONNECTION_PARAMS = {"sample_rate": 16000, "format_turns": True}
API_ENDPOINT_BASE_URL = "wss://streaming.assemblyai.com/v3/ws"
API_ENDPOINT = f"{API_ENDPOINT_BASE_URL}?{urlencode(CONNECTION_PARAMS)}"
HEADERS = {"Authorization": os.environ.get("ASSEMBLYAI_API_KEY")}

# Audio Configuration
FRAMES_PER_BUFFER = 800  # 50ms of audio (0.05s * 16000Hz)
SAMPLE_RATE = CONNECTION_PARAMS["sample_rate"]
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Global State (managed within async context) ---
recorded_frames = []


async def audio_sender(ws: websockets.WebSocketClientProtocol, stream: pyaudio.Stream, stop_event: asyncio.Event):
    """
    Reads audio from the microphone stream and sends it to the WebSocket server.
    This runs as a concurrent task.
    """
    logging.info("Audio sender task started.")
    try:
        while not stop_event.is_set():
            # Use asyncio.to_thread to run the blocking PyAudio call in a separate thread
            audio_data = await asyncio.to_thread(
                stream.read, FRAMES_PER_BUFFER, exception_on_overflow=False
            )
            
            # Append to our recording list
            recorded_frames.append(audio_data)
            
            # Send audio data over the WebSocket
            await ws.send(audio_data)
            
    except websockets.exceptions.ConnectionClosed as e:
        logging.warning(f"Connection closed by server in sender: {e.code} {e.reason}")
    except Exception as e:
        logging.error(f"Error in audio sender: {e}")
    finally:
        logging.info("Audio sender task finished.")


async def message_receiver(ws: websockets.WebSocketClientProtocol, stop_event: asyncio.Event):
    """

    Receives messages from the WebSocket server and processes them.
    This runs as a concurrent task.
    """
    logging.info("Message receiver task started.")
    try:
        async for message in ws:
            if stop_event.is_set():
                break
                
            data = json.loads(message)
            msg_type = data.get('type')

            if msg_type == "Begin":
                session_id = data.get('id')
                expires_at = data.get('expires_at')
                logging.info(f"Session began: ID={session_id}, ExpiresAt={datetime.fromtimestamp(expires_at)}")
                
            elif msg_type == "Turn":
                transcript = data.get('transcript', '')
                formatted = data.get('turn_is_formatted', False)

                if formatted:
                    # Clear the line and print the final transcript
                    print('\r' + ' ' * 80 + '\r', end='')
                    print(f"👤 User: {transcript}")
                    
                    # Call your agent asynchronously
                    print("🤖 AI is thinking...")
                    response = await generate_response(transcript)
                    print(f"🤖 AI: {response}")
                    await text_to_speech_bytes(response)
                else:
                    # Print partial transcript on the same line
                    print(f"\r💬 Partial: {transcript}", end='')
                    
            elif msg_type == "Termination":
                audio_duration = data.get('audio_duration_seconds', 0)
                session_duration = data.get('session_duration_seconds', 0)
                logging.info(f"Session Terminated: Audio Duration={audio_duration}s, Session Duration={session_duration}s")
                # Stop other tasks when server terminates session
                stop_event.set()
                
    except websockets.exceptions.ConnectionClosed as e:
        logging.warning(f"Connection closed by server in receiver: {e.code} {e.reason}")
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON message: {message}")
    except Exception as e:
        logging.error(f"Error in message receiver: {e}")
    finally:
        logging.info("Message receiver task finished.")
        # Ensure stop is signaled if receiver exits unexpectedly
        if not stop_event.is_set():
            stop_event.set()

def save_wav_file():
    """Saves the recorded audio frames to a WAV file."""
    if not recorded_frames:
        logging.warning("No audio data was recorded.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recorded_audio_{timestamp}.wav"

    try:
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(recorded_frames))
        
        duration = len(recorded_frames) * FRAMES_PER_BUFFER / SAMPLE_RATE
        logging.info(f"Audio saved to '{filename}' (Duration: {duration:.2f}s)")
    except Exception as e:
        logging.error(f"Error saving WAV file: {e}")


async def main():
    """Main asynchronous function to orchestrate the application."""
    audio = pyaudio.PyAudio()
    stream = None
    stop_event = asyncio.Event()

    try:
        # Open microphone stream
        stream = audio.open(
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
            channels=CHANNELS,
            format=FORMAT,
            rate=SAMPLE_RATE,
        )
        logging.info("Microphone stream opened successfully.")
        print("\nSpeak into your microphone. Press Ctrl+C to stop.")
        
        # Connect to WebSocket server
        async with websockets.connect(API_ENDPOINT, extra_headers=HEADERS) as ws:
            logging.info("WebSocket connection established.")

            # Create and run sender and receiver tasks concurrently
            sender_task = asyncio.create_task(audio_sender(ws, stream, stop_event))
            receiver_task = asyncio.create_task(message_receiver(ws, stop_event))

            # Wait for either task to complete or for the stop event to be set
            done, pending = await asyncio.wait(
                [sender_task, receiver_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # If any task finishes, it likely means the connection is closed or an error occurred.
            # We signal the other task to stop.
            for task in pending:
                task.cancel()

    except websockets.exceptions.InvalidURI:
        logging.error(f"Invalid WebSocket URI: {API_ENDPOINT}")
    except websockets.exceptions.InvalidHandshake as e:
        logging.error(f"WebSocket handshake failed: {e}. Check your API key and endpoint.")
    except KeyboardInterrupt:
        logging.info("\nCtrl+C received. Shutting down gracefully...")
    except Exception as e:
        logging.error(f"An unexpected error occurred in main: {e}")
    finally:
        # Graceful shutdown
        stop_event.set()
        
        # Close and terminate audio resources
        if stream:
            stream.stop_stream()
            stream.close()
            logging.info("Microphone stream closed.")
        if audio:
            audio.terminate()
            logging.info("PyAudio terminated.")
            
        # Save the recorded audio
        save_wav_file()
        logging.info("Application has shut down.")


if __name__ == "__main__":
    # Ensure you have a valid API key before running
    if "your_actual_api_key" in os.environ.get("ASSEMBLYAI_API_KEY") or not os.environ.get("ASSEMBLYAI_API_KEY"):
         print("ERROR: Please replace 'YOUR_API_KEY' with your actual AssemblyAI API key.")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            # This is to prevent asyncio's own KeyboardInterrupt message from showing
            pass