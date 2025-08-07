import openwakeword
from openwakeword.model import Model
import faster_whisper
import webrtcvad
import pyaudio
import pyttsx3
import numpy as np
import wave
import os
import time
from typing import List
import asyncio

# Audio configuration
CHUNK = 1280  # Audio chunk size for wake word (matches openWakeWord requirements)
SAMPLE_RATE = 16000  # 16kHz for wake word and STT
VAD_MODE = 3  # Aggressive VAD mode
FRAME_DURATION = 30  # ms, for VAD
VAD_FRAMES = int((SAMPLE_RATE * FRAME_DURATION) / 1000)  # Samples per frame
WAKE_WORD = "hey_assistant"  # Wake word
WAKE_WORD_MODEL_PATH = "models/hey_assistant.tflite"  # Path to wake word model
VAD_SENSITIVITY = 0.6  # Sensitivity for wake word detection
WAKE_WORD_TIMEOUT = 5.0  # Seconds to wait for speech after wake word
OUTPUT_WAV = "temp_audio.wav"  # Temporary audio file

# Initialize components
vad = webrtcvad.Vad(VAD_MODE)
wake_word_model = Model(
    wakeword_models=[WAKE_WORD_MODEL_PATH],
    inference_framework="tflite",
    vad_threshold=VAD_SENSITIVITY
)
whisper_model = faster_whisper.WhisperModel("tiny.en", device="cpu", compute_type="int8")
tts_engine = pyttsx3.init()  # Placeholder for Orpheus TTS
tts_engine.setProperty('rate', 150)  # Speed of speech
tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=CHUNK
)

def save_audio(frames: List[bytes], filename: str):
    """Save audio frames to a WAV file."""
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def process_query(text: str) -> str:
    """Process the transcribed text and return a response."""
    # Placeholder: Echo the input. Replace with LLM integration (e.g., Llama, Grok).
    return f"You said: {text}"

def text_to_speech(text: str):
    """Convert text to speech using pyttsx3 (replace with Orpheus TTS)."""
    tts_engine.say(text)
    tts_engine.runAndWait()

async def main():
    print("Voice assistant started. Say 'Hey Assistant' to activate...")
    frames = []
    is_recording = False
    wake_word_detected = False
    last_wake_time = 0

    while True:
        # Read audio chunk
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

        # Wake word detection
        prediction = wake_word_model.predict(audio_chunk)
        wake_score = prediction.get(WAKE_WORD, 0.0)

        if wake_score > VAD_SENSITIVITY and not wake_word_detected:
            print("Wake word detected!")
            wake_word_detected = True
            is_recording = True
            frames = [data]
            last_wake_time = time.time()
            continue

        if wake_word_detected:
            # Check if still within timeout
            if time.time() - last_wake_time > WAKE_WORD_TIMEOUT:
                print("Timeout waiting for speech. Resetting...")
                wake_word_detected = False
                is_recording = False
                frames = []
                continue

            # VAD to detect speech
            is_speech = vad.is_speech(data, SAMPLE_RATE)
            if is_speech:
                frames.append(data)
            elif is_recording and len(frames) > 0:
                # Speech stopped, process audio
                print("Speech ended, processing...")
                is_recording = False
                wake_word_detected = False

                # Save audio to file
                save_audio(frames, OUTPUT_WAV)

                # Transcribe with faster-whisper
                segments, _ = whisper_model.transcribe(OUTPUT_WAV, language="en")
                transcribed_text = " ".join(segment.text for segment in segments).strip()
                print(f"Transcribed: {transcribed_text}")

                if transcribed_text:
                    # Process query and generate response
                    response = process_query(transcribed_text)
                    print(f"Response: {response}")

                    # Synthesize response (replace with Orpheus TTS)
                    text_to_speech(response)

                # Clean up
                frames = []
                if os.path.exists(OUTPUT_WAV):
                    os.remove(OUTPUT_WAV)

        await asyncio.sleep(0.01)  # Small sleep to prevent CPU overload

if __name__ == "__main__":
    try:
        if platform.system() == "Emscripten":
            asyncio.ensure_future(main())
        else:
            asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping voice assistant...")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()