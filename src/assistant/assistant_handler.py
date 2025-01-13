from openai import OpenAI
from .config.settings import OPENAI_API_KEY
from .utils.logger import setup_logger
import asyncio

logger = setup_logger(__name__)

class AssistantHandler:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.assistant = None
        self.threads = {}  # Store threads by call_sid
        logger.info("AssistantHandler initialized")
        
    def create_assistant(self):
        """Create or get the assistant"""
        try:
            if not self.assistant:
                logger.info("Creating new assistant...")
                self.assistant = self.client.beta.assistants.create(
                    name="Phone Assistant",
                    instructions="""You are a helpful phone assistant. Keep responses clear and concise. 
                    Be friendly but professional. If you don't understand something, ask for clarification.""",
                    model="gpt-4-turbo-preview"
                )
                logger.info(f"Assistant created with ID: {self.assistant.id}")
            return self.assistant
        except Exception as e:
            logger.error(f"Error creating assistant: {e}")
            raise
        
    def get_or_create_thread(self, call_sid):
        """Get existing thread or create new one for the call"""
        try:
            if call_sid not in self.threads:
                logger.info(f"Creating new thread for call {call_sid}")
                thread = self.client.beta.threads.create()
                self.threads[call_sid] = thread.id
                logger.info(f"Created thread {thread.id} for call {call_sid}")
            return self.threads[call_sid]
        except Exception as e:
            logger.error(f"Error in get_or_create_thread: {e}")
            raise
        
    async def process_message(self, call_sid, message):
        """Process a message in the conversation thread"""
        logger.info(f"Processing message for call {call_sid}: {message}")
        
        try:
            # Ensure we have an assistant
            if not self.assistant:
                logger.info("No assistant found, creating one...")
                self.create_assistant()
            
            # Get or create thread
            thread_id = self.get_or_create_thread(call_sid)
            logger.info(f"Using thread {thread_id}")
            
            # Add the message to the thread
            logger.info("Adding message to thread...")
            message_obj = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            logger.info(f"Message added with ID: {message_obj.id}")
            
            # Run the assistant
            logger.info("Starting assistant run...")
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant.id
            )
            logger.info(f"Run created with ID: {run.id}")
            
            # Wait for completion
            while True:
                logger.info(f"Checking run status for {run.id}...")
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                logger.info(f"Run status: {run_status.status}")
                
                if run_status.status == 'completed':
                    # Get the latest message
                    logger.info("Run completed, fetching response...")
                    messages = self.client.beta.threads.messages.list(
                        thread_id=thread_id
                    )
                    response = messages.data[0].content[0].text.value
                    logger.info(f"Got response: {response}")
                    return response
                    
                elif run_status.status == 'failed':
                    logger.error("Assistant run failed")
                    raise Exception("Assistant run failed")
                    
                logger.info("Waiting for completion...")
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I apologize, but I'm having trouble processing your request. Could you please try again?" 