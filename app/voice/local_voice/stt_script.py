#!/usr/bin/env python3
"""
Local Speech-to-Text using faster-whisper
Supports both real-time audio capture and file transcription
"""

import os
import sys
import argparse
import threading
import queue
import time
from pathlib import Path
import wave
import tempfile
# CORRECTION: Added uuid and atexit imports to the top for clarity and good practice.
import uuid
import atexit

try:
    import pyaudio
    import numpy as np
    from faster_whisper import WhisperModel
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install faster-whisper pyaudio numpy")
    sys.exit(1)

class LocalSTT:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        Initialize the STT engine
        
        Args:
            model_size: Model size (tiny, base, small, medium, large-v2, large-v3)
            device: Device to run on ("cpu", "cuda", "auto")
            compute_type: Computation type ("int8", "int16", "float16", "float32")
        """
        print(f"Loading Whisper model: {model_size}")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Model loaded successfully!")
        
        # Audio settings
        self.chunk_size = 1024
        self.sample_rate = 16000
        self.channels = 1
        self.audio_format = pyaudio.paInt16
        
        # Real-time processing
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.pyaudio_instance = None
        self.stream = None
    
    def transcribe_file(self, audio_file_path, language=None):
        """
        Transcribe an audio file
        
        Args:
            audio_file_path: Path to audio file
            language: Language code (e.g., 'en', 'es') or None for auto-detection
        
        Returns:
            Transcription text
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        print(f"Transcribing file: {audio_file_path}")
        
        segments, info = self.model.transcribe(
            audio_file_path, 
            language=language,
            beam_size=5,
            best_of=5,
            temperature=0
        )
        
        print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
        
        transcription = ""
        for segment in segments:
            print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
            transcription += segment.text + " "
        
        return transcription.strip()
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if status:
            print(f"Audio callback status: {status}")
        
        self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
    
    def start_recording(self):
        """Start real-time audio recording"""
        if self.is_recording:
            print("Already recording!")
            return
        
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            
            self.stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self.stream.start_stream()
            print("Started recording... Press Ctrl+C to stop")
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.stop_recording()
    
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
        
        print("Recording stopped")
    
    # CORRECTION: The entire 'transcribe_audio_data' method has been fixed.
    # The misplaced code block was removed and turned into its own proper method `_save_audio_to_wav`.
    # The call to `atexit` now correctly references a newly defined `_safe_remove` method.
    def transcribe_audio_data(self, audio_data, language=None):
        """
        Transcribe raw audio data directly by saving to a temporary file.
        
        Args:
            audio_data: Raw audio bytes
            language: Language code or None for auto-detection
        
        Returns:
            Transcription text
        """
        temp_dir = tempfile.gettempdir()
        temp_filename = None
        
        try:
            # Create temporary file with unique name
            temp_filename = os.path.join(temp_dir, f"whisper_temp_{uuid.uuid4().hex}.wav")
            
            # Save audio data using the helper method
            self._save_audio_to_wav(audio_data, temp_filename)
            
            # Transcribe
            segments, info = self.model.transcribe(
                temp_filename,
                language=language,
                beam_size=5,
                best_of=5,
                temperature=0
            )
            
            transcription = "".join(segment.text + " " for segment in segments)
            return transcription.strip()
            
        finally:
            # Ensure cleanup happens
            if temp_filename:
                self._safe_remove(temp_filename)

    # CORRECTION 1: This new method properly encapsulates the logic to save a WAV file.
    # It was created from the misplaced code block in the original script.
    # CORRECTION 2: It no longer depends on `self.pyaudio_instance`, removing a potential crash.
    # `pyaudio.paInt16` is known to be 2 bytes, so we can hardcode it for robustness.
    def _save_audio_to_wav(self, audio_data, filename):
        """Save a chunk of audio data to a WAV file."""
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                # Use hardcoded sample width for paInt16 (2 bytes)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)
        except Exception as e:
            print(f"Error saving audio chunk to {filename}: {e}")
            raise
    
    # CORRECTION: Added the missing _safe_remove method, which was referenced but not defined.
    # This method is used as a fallback to clean up temp files.
    def _safe_remove(self, filepath):
        """Safely remove a file, handling potential errors like file locks."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except (PermissionError, FileNotFoundError) as e:
            print(f"Could not remove temp file {filepath} immediately: {e}. Scheduling for exit.")
            atexit.register(os.remove, filepath)
        except Exception as e:
            print(f"Unhandled error removing temp file {filepath}: {e}")

    def real_time_transcription(self, chunk_duration=5, language=None):
        """
        Perform real-time transcription
        
        Args:
            chunk_duration: Duration in seconds for each transcription chunk
            language: Language code or None for auto-detection
        """
        self.start_recording()
        
        try:
            frames_per_chunk = int(self.sample_rate * chunk_duration)
            audio_buffer = []
            
            while self.is_recording:
                try:
                    # Collect audio data
                    data = self.audio_queue.get(timeout=0.1)
                    audio_buffer.append(data)
                    
                    # Check if we have enough data for transcription
                    # 2 bytes per frame (int16)
                    total_frames = sum(len(chunk) for chunk in audio_buffer) // 2
                    
                    if total_frames >= frames_per_chunk:
                        # Combine audio chunks
                        audio_data = b''.join(audio_buffer)
                        audio_buffer = []
                        
                        # Transcribe directly from audio data in a non-blocking way
                        # (This could be improved with a thread pool for heavy loads)
                        try:
                            transcription = self.transcribe_audio_data(audio_data, language)
                            if transcription.strip():
                                print(f"\n🎤 Transcription: {transcription}\n", end="", flush=True)
                        except Exception as e:
                            print(f"Transcription error: {e}")
                
                except queue.Empty:
                    continue
        
        except KeyboardInterrupt:
            print("\nStopping real-time transcription...")
        finally:
            self.stop_recording()
    
    def list_audio_devices(self):
        """List available audio input devices"""
        p = pyaudio.PyAudio()
        print("\nAvailable audio input devices:")
        print("-" * 50)
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"Device {i}: {info['name']}")
                print(f"  Channels: {info['maxInputChannels']}")
                print(f"  Sample Rate: {info['defaultSampleRate']}")
                print()
        
        p.terminate()


def main():
    parser = argparse.ArgumentParser(description="Local Speech-to-Text using faster-whisper")
    parser.add_argument("--model", default="base", 
                       choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
                       help="Whisper model size")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda", "auto"],
                       help="Device to run inference on")
    parser.add_argument("--compute-type", default="int8", 
                       choices=["int8", "int16", "float16", "float32"],
                       help="Compute type for inference")
    parser.add_argument("--file", type=str, help="Audio file to transcribe")
    parser.add_argument("--real-time", action="store_true", help="Real-time transcription")
    parser.add_argument("--chunk-duration", type=int, default=5, 
                       help="Duration in seconds for real-time chunks")
    parser.add_argument("--language", type=str, help="Language code (e.g., 'en', 'es')")
    parser.add_argument("--list-devices", action="store_true", help="List audio input devices")
    
    args = parser.parse_args()
    
    # Initialize STT
    stt = LocalSTT(
        model_size=args.model,
        device=args.device,
        compute_type=args.compute_type
    )
    
    # List audio devices
    if args.list_devices:
        stt.list_audio_devices()
        return
    
    # File transcription
    if args.file:
        try:
            transcription = stt.transcribe_file(args.file, args.language)
            print(f"\n📝 Final Transcription:\n{transcription}")
        except Exception as e:
            print(f"Error: {e}")
            return
    
    # Real-time transcription
    elif args.real_time:
        print("Starting real-time transcription...")
        print("Speak into your microphone. Press Ctrl+C to stop.")
        stt.real_time_transcription(args.chunk_duration, args.language)
    
    else:
        print("Please specify either --file or --real-time option")
        parser.print_help()


if __name__ == "__main__":
    main()