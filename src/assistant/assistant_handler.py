from openai import OpenAI
from .config.settings import OPENAI_API_KEY
from .config.rental_config import RENTAL_ASSISTANT_INSTRUCTIONS, RENTAL_SCRIPT
from .customer_db import CustomerDB
import asyncio
import json

logger = setup_logger(__name__)

class AssistantHandler:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.assistant = None
        self.threads = {}
        self.customer_db = CustomerDB()
        
    def create_assistant(self):
        """Create or get the rental assistant"""
        if not self.assistant:
            self.assistant = self.client.beta.assistants.create(
                name="Bike Rental Assistant",
                instructions=RENTAL_ASSISTANT_INSTRUCTIONS,
                model="gpt-4-turbo-preview"
            )
        return self.assistant
        
    def get_or_create_thread(self, phone_number):
        """Get existing thread or create new one for the customer"""
        if phone_number not in self.threads:
            # Check if customer has previous thread
            last_conv = self.customer_db.get_last_conversation(phone_number)
            if last_conv:
                self.threads[phone_number] = last_conv['thread_id']
            else:
                thread = self.client.beta.threads.create()
                self.threads[phone_number] = thread.id
                
        return self.threads[phone_number]
        
    async def process_rental_conversation(self, phone_number, customer_name, message):
        """Process rental conversation"""
        try:
            thread_id = self.get_or_create_thread(phone_number)
            
            # Add context if it's a returning customer
            last_conv = self.customer_db.get_last_conversation(phone_number)
            if last_conv:
                context = f"Previous rental details: {json.dumps(last_conv['data'])}"
                self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="system",
                    content=context
                )
            
            # Add the current message
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            
            # Run the assistant
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
                    messages = self.client.beta.threads.messages.list(
                        thread_id=thread_id
                    )
                    response = messages.data[0].content[0].text.value
                    
                    # Store conversation data
                    conversation_data = {
                        'customer_name': customer_name,
                        'message': message,
                        'response': response
                    }
                    self.customer_db.store_conversation(phone_number, thread_id, conversation_data)
                    
                    return response
                elif run_status.status == 'failed':
                    raise Exception("Assistant run failed")
                    
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error processing rental conversation: {e}")
            return "I apologize, but I'm having trouble processing your request. Could you please try again?"