from openai import OpenAI
from .config.settings import OPENAI_API_KEY
from .utils.logger import setup_logger

logger = setup_logger(__name__)

class AssistantHandler:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.assistant = None
        self.threads = {}  # Store threads by call_sid
        
    def create_assistant(self):
        """Create or get the assistant"""
        if not self.assistant:
            self.assistant = self.client.beta.assistants.create(
                name="Phone Assistant",
                instructions="""You are a helpful phone assistant. Keep responses clear and concise. 
                Be friendly but professional. If you don't understand something, ask for clarification.""",
                model="gpt-4-turbo-preview"
            )
        return self.assistant
        
    def get_or_create_thread(self, call_sid):
        """Get existing thread or create new one for the call"""
        if call_sid not in self.threads:
            thread = self.client.beta.threads.create()
            self.threads[call_sid] = thread.id
        return self.threads[call_sid]
        
    async def process_message(self, call_sid, message):
        """Process a message in the conversation thread"""
        try:
            thread_id = self.get_or_create_thread(call_sid)
            
            # Add the message to the thread
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
                    # Get the latest message
                    messages = self.client.beta.threads.messages.list(
                        thread_id=thread_id
                    )
                    return messages.data[0].content[0].text.value
                elif run_status.status == 'failed':
                    raise Exception("Assistant run failed")
                    
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I apologize, but I'm having trouble processing your request. Could you please try again?" 