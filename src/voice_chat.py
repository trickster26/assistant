import asyncio
import pyaudio
import wave
import threading
import queue
import numpy as np
from openai import OpenAI
from assistant.utils.logger import setup_logger
from assistant.config.settings import OPENAI_API_KEY
import tempfile
import os
import sounddevice as sd
import soundfile as sf
from datetime import datetime

logger = setup_logger("voice_chat")

class VoiceChat:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.sample_rate = 44100
        self.channels = 1
        self.chunk = 1024
        
    def start_recording(self):
        """Start recording audio from microphone"""
        self.is_recording = True
        self.audio_data = []
        
        def callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            self.audio_queue.put(indata.copy())
            
        try:
            with sd.InputStream(callback=callback,
                              channels=self.channels,
                              samplerate=self.sample_rate):
                print("\nRecording... Press Enter to stop.")
                input()
                
        except Exception as e:
            logger.error(f"Error recording: {e}")
            
        self.is_recording = False
        
    def save_audio(self, filename):
        """Save recorded audio to file"""
        data = []
        while not self.audio_queue.empty():
            data.append(self.audio_queue.get())
            
        if data:
            audio_data = np.concatenate(data)
            sf.write(filename, audio_data, self.sample_rate)
            return True
        return False
        
    def text_to_speech(self, text):
        """Convert text to speech using OpenAI API"""
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
            logger.error(f"Text-to-speech error: {e}")
            return None
            
    def play_audio(self, filename):
        """Play audio file"""
        try:
            data, samplerate = sf.read(filename)
            sd.play(data, samplerate)
            sd.wait()
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            
    def transcribe_audio(self, audio_file):
        """Transcribe audio file to text"""
        try:
            with open(audio_file, "rb") as file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file
                )
            return transcript.text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

async def start_voice_chat():
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found. Please check your .env file.")
        return
        
    voice_chat = VoiceChat()
    
    print("\nWelcome to Voice Chat!")
    print("Press Enter to start/stop recording")
    print("Type 'exit' to end the conversation")
    print("-" * 50)
    
    while True:
        try:
            # Record audio
            print("\nPress Enter to start speaking...")
            input()
            
            # Create temporary file for recording
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            
            # Start recording
            voice_chat.start_recording()
            
            # Save recorded audio
            if voice_chat.save_audio(temp_audio.name):
                # Transcribe audio to text
                user_text = voice_chat.transcribe_audio(temp_audio.name)
                
                if user_text:
                    print(f"\nYou said: {user_text}")
                    
                    if user_text.lower().strip() == "exit":
                        print("\nEnding conversation. Goodbye!")
                        break
                    
                    # Get assistant's response
                    response = voice_chat.client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[{"role": "user", "content": user_text}]
                    )
                    
                    assistant_response = response.choices[0].message.content
                    print(f"\nAssistant: {assistant_response}")
                    
                    # Convert response to speech
                    audio_file = voice_chat.text_to_speech(assistant_response)
                    if audio_file:
                        # Play the response
                        voice_chat.play_audio(audio_file)
                        os.unlink(audio_file)
                
                # Cleanup temporary file
                os.unlink(temp_audio.name)
                
        except KeyboardInterrupt:
            print("\nEnding conversation. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print("\nAn error occurred. Please try again.")

if __name__ == "__main__":
    asyncio.run(start_voice_chat()) 