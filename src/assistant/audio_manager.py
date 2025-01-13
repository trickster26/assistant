import wave
import pyaudio
from typing import Generator
import numpy as np
from openai import OpenAI
import tempfile
import os

class AudioManager:
    def __init__(self):
        self.client = OpenAI()
        self.chunk = 1024
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.rate = 16000
        self.p = pyaudio.PyAudio()
        
    def text_to_speech(self, text: str) -> str:
        """Convert text to speech and save as temporary file"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            response.stream_to_file(temp_file.name)
            return temp_file.name
            
        except Exception as e:
            raise Exception(f"Text-to-speech conversion failed: {str(e)}")
            
    def speech_to_text(self, audio_file: str) -> str:
        """Convert speech to text"""
        try:
            with open(audio_file, "rb") as file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file
                )
            return transcript.text
            
        except Exception as e:
            raise Exception(f"Speech-to-text conversion failed: {str(e)}")
            
    def cleanup_audio_file(self, file_path: str):
        """Remove temporary audio file"""
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up audio file: {str(e)}") 