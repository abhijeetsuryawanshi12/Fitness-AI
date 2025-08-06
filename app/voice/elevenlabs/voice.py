import assemblyai as aai
from elevenlabs import play, voices, stream
from elevenlabs.client import ElevenLabs
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv  

load_dotenv()


class AI_Assistant:
    def __init__(self):
        """
        Initialize the AI Assistant with ElevenLabs API key.
        """
        # --- ERROR FIX: Correctly initialize the AssemblyAI Client ---
        assemblyai_api_key = os.environ.get("ASSEMBLYAI_API_KEY")
        if not assemblyai_api_key:
            raise ValueError("ASSEMBLYAI_API_KEY environment variable not set.")
        
        # 1. Create a Settings object with your API key
        settings = aai.Settings(api_key=assemblyai_api_key)
        
        # 2. Pass the settings object to the Client constructor
        self.assemblyai_client = aai.Client(settings=settings)
        # --- END FIX ---

        # self.assemblyai_client = aai.Client(assemblyai_api_key)
        self.elevenlabs_client = ElevenLabs(api_key=os.environ.get("ELEVEN_LABS_API_KEY"))
        self.llm = init_chat_model("gemini-2.0-flash",
                                   model_provider="google_genai",
                                   api_key=os.environ.get("GEMINI_API_KEY"),
                                   temperature=0.7)
        self.transcriber = None
        self.full_transcript = [
            {"role": "system", "content": "You are a helpful Fitness Coach, your job is to help users with their fitness goals."},
        ]
        self.output_parser = StrOutputParser()

    def start_transcription(self):
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate=16000,
            on_data=self.on_data,
            on_error=self.on_error,
            on_open=self.on_open,
            on_close=self.on_close,
            end_utterance_silence_threshold=1000
        )
        
        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(
            sample_rate=16000,
            chunk_size=1024,
            device_index=None
        )
        self.transcriber.stream(microphone_stream)
        
    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None
    
    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        # print("Session ID:", session_opened.session_id)
        return

    def on_data(self, transcript: aai.RealtimeTranscript):
        """
        Handle incoming transcription data.
        """
        if not transcript.text:
            return
        
        if isinstance(transcript, aai.RealtimeTranscript):
            #Generate AI response
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")

    def on_error(self, error: aai.RealtimeError):
        """
        Handle transcription errors.
        """        
        print(f"Transcription error: {error}")

    def on_close(self):
        """
        Handle transcription connection close.
        """
        print("Transcription connection closed.")
        
    
    def generate_ai_response(self, transcript):
        self.stop_transcription()
        self.full_transcript.append(
            {"role": "user", "content": transcript.text}
        )
        print(f"User: {transcript.text}", end="\r\n")
        
        response = self.llm.invoke(
            self.full_transcript,
            config={"session_id": "fitness_assistant_session"}
        )

        ai_response = response.choices[0].message.content

        self.generate_audio(ai_response)

        self.start_transcription()
        print(f"AI: {ai_response}", end="\r\n")

    def generate_audio(self, text):
        """
        Generate audio from text using ElevenLabs API.
        """

        self.full_transcript.append(
            {"role": "assistant", "content": text}
        
        )
        print(f"Generating audio for: {text}")

        

        audio_stream = self.elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128", 
        )

        play(audio_stream)


greeting = "Thank you for calling the AI Fitness Assistant. How can I assist you today?"

ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()