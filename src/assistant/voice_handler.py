from openai import OpenAI
import tempfile
import os
from .utils.logger import setup_logger

logger = setup_logger(__name__)

class VoiceHandler:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        
    def speech_to_text(self, audio_data):
        """Convert speech to text using Whisper API"""
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_data)
                audio_path = temp_file.name
            
            # Transcribe audio
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Clean up temp file
            os.unlink(audio_path)
            
            return transcript.text
            
        except Exception as e:
            logger.error(f"Error in speech to text: {e}")
            raise
            
    def text_to_speech(self, text):
        """Convert text to speech using OpenAI TTS"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="nova",  # Options: alloy, echo, fable, onyx, nova, shimmer
                input=text
            )
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                response.stream_to_file(temp_file.name)
                return temp_file.name
                
        except Exception as e:
            logger.error(f"Error in text to speech: {e}")
            raise 