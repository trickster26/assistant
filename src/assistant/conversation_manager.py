from datetime import datetime
from typing import List, Dict, Optional
from .utils.logger import setup_logger
from .thread_manager import ThreadManager
from .assistant_manager import AssistantManager
from .conversation_stats import ConversationStats
import time

logger = setup_logger(__name__)

class ConversationManager:
    def __init__(self):
        self.assistant_mgr = AssistantManager()
        self.thread_mgr = ThreadManager()
        self.conversations = {}
        self.logger = logger
        self.conversation_stats = {}

    async def handle_conversation(self, client_id: str, script: List[str]):
        """Handle a conversation with a client"""
        try:
            # Create or get thread for this client
            thread_id = self.thread_mgr.get_or_create_thread(client_id)
            
            # Create assistant if needed
            if thread_id not in self.conversations:
                assistant = self.assistant_mgr.create_assistant(
                    name=f"Assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    instructions="You are a helpful assistant making calls to clients."
                )
                self.conversations[thread_id] = assistant.id
            
            # Process each script line
            for line in script:
                # Add message to thread
                self.thread_mgr.add_message(thread_id, line)
                
                # Get assistant's response
                response = self.thread_mgr.run_assistant(
                    thread_id=thread_id,
                    assistant_id=self.conversations[thread_id]
                )
                
                if response is None:
                    self.logger.warning(f"No response received for message: {line}")
                    continue
                
                # Log the interaction
                self.logger.info(f"Assistant: {line}")
                self.logger.info(f"Response: {response}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in conversation: {str(e)}")
            raise 