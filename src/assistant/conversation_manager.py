from datetime import datetime
from typing import List, Dict, Optional
from ..utils.logger import setup_logger
from .thread_manager import ThreadManager
from .assistant_manager import AssistantManager

logger = setup_logger(__name__)

class Conversation:
    def __init__(self, thread_id: str, assistant_id: str):
        self.thread_id = thread_id
        self.assistant_id = assistant_id
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.message_count = 0
        self.metadata: Dict = {}

class ConversationManager:
    def __init__(self):
        self.assistant_mgr = AssistantManager()
        self.thread_mgr = ThreadManager()
        self.conversations: Dict[str, Conversation] = {}
        self.logger = logger

    def create_conversation(self, instructions: str = None) -> Conversation:
        """Create a new conversation with a dedicated assistant and thread"""
        try:
            # Create assistant with specific instructions if provided
            assistant = self.assistant_mgr.create_assistant(
                name=f"Assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                instructions=instructions or "You are a helpful assistant."
            )
            
            # Create thread
            thread = self.thread_mgr.create_thread()
            
            # Create and store conversation
            conversation = Conversation(thread.id, assistant.id)
            self.conversations[thread.id] = conversation
            
            self.logger.info(f"Created new conversation with thread ID: {thread.id}")
            return conversation
            
        except Exception as e:
            self.logger.error(f"Error creating conversation: {str(e)}")
            raise

    async def send_message(self, thread_id: str, message: str) -> str:
        """Send a message in a conversation and get the response"""
        try:
            conversation = self.conversations.get(thread_id)
            if not conversation:
                raise ValueError(f"No conversation found with thread ID: {thread_id}")

            # Update conversation stats
            conversation.last_active = datetime.now()
            conversation.message_count += 1

            # Log the incoming message
            self.logger.debug(f"Sending message in thread {thread_id}: {message[:50]}...")

            # Add message to thread
            self.thread_mgr.add_message(thread_id, message)

            # Get assistant's response
            response = self.thread_mgr.run_assistant(
                thread_id=thread_id,
                assistant_id=conversation.assistant_id
            )

            self.logger.debug(f"Received response in thread {thread_id}: {response[:50]}...")
            return response

        except Exception as e:
            self.logger.error(f"Error in conversation {thread_id}: {str(e)}")
            raise

    def get_conversation_history(self, thread_id: str) -> List[Dict]:
        """Get the full conversation history"""
        try:
            messages = self.thread_mgr.get_messages(thread_id)
            return [
                {
                    'role': msg.role,
                    'content': msg.content[0].text.value,
                    'created_at': msg.created_at
                }
                for msg in messages.data
            ]
        except Exception as e:
            self.logger.error(f"Error fetching conversation history: {str(e)}")
            raise

    def add_metadata(self, thread_id: str, key: str, value: any):
        """Add metadata to a conversation"""
        if thread_id in self.conversations:
            self.conversations[thread_id].metadata[key] = value
            self.logger.debug(f"Added metadata {key}={value} to conversation {thread_id}")

    def get_active_conversations(self) -> List[Conversation]:
        """Get all active conversations"""
        return list(self.conversations.values())

    def close_conversation(self, thread_id: str):
        """Close and cleanup a conversation"""
        try:
            if thread_id in self.conversations:
                conversation = self.conversations[thread_id]
                # Clean up assistant
                self.assistant_mgr.delete_assistant(conversation.assistant_id)
                # Remove from active conversations
                del self.conversations[thread_id]
                self.logger.info(f"Closed conversation {thread_id}")
        except Exception as e:
            self.logger.error(f"Error closing conversation {thread_id}: {str(e)}")
            raise 