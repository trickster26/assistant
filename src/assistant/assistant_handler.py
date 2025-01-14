from openai import OpenAI
from .config.settings import OPENAI_API_KEY
from .config.rental_config import RENTAL_ASSISTANT_INSTRUCTIONS
from .voice_handler import VoiceHandler
from datetime import datetime
import json
import asyncio

logger = setup_logger(__name__)

class AssistantHandler:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.voice_handler = VoiceHandler(OPENAI_API_KEY)
        self.assistant = None
        self.threads = {}
        
    def create_assistant(self):
        """Create or get the rental assistant"""
        try:
            if not self.assistant:
                self.assistant = self.client.beta.assistants.create(
                    name="Bike Rental Assistant",
                    instructions=RENTAL_ASSISTANT_INSTRUCTIONS,
                    model="gpt-4-turbo-preview"
                )
            return self.assistant
        except Exception as e:
            logger.error(f"Error creating assistant: {e}")
            raise
            
    async def process_audio_conversation(self, audio_data, thread_id=None):
        """Process audio conversation"""
        try:
            # Convert speech to text
            text = self.voice_handler.speech_to_text(audio_data)
            logger.info(f"Transcribed text: {text}")
            
            # Create or get thread
            if not thread_id:
                thread = self.client.beta.threads.create()
                thread_id = thread.id
            
            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=text
            )
            
            # Run assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant.id
            )
            
            # Wait for completion
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                
                if run_status.status == 'completed':
                    # Get assistant's response
                    messages = self.client.beta.threads.messages.list(
                        thread_id=thread_id
                    )
                    response_text = messages.data[0].content[0].text.value
                    
                    # Convert response to speech
                    audio_file = self.voice_handler.text_to_speech(response_text)
                    
                    return {
                        'thread_id': thread_id,
                        'text': response_text,
                        'audio_file': audio_file
                    }
                    
                elif run_status.status == 'failed':
                    raise Exception("Assistant run failed")
                    
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error processing audio conversation: {e}")
            raise