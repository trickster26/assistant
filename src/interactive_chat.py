import asyncio
from assistant.conversation_manager import ConversationManager
from assistant.utils.logger import setup_logger
from assistant.config.settings import OPENAI_API_KEY
import sys

logger = setup_logger("interactive_chat")

async def start_interactive_chat():
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found. Please check your .env file.")
        sys.exit(1)
        
    conversation_manager = ConversationManager()
    
    # Create a new conversation thread
    thread_id = conversation_manager.thread_mgr.create_thread().id
    
    # Create an assistant for this conversation
    assistant = conversation_manager.assistant_mgr.create_assistant(
        name="Interactive_Assistant",
        instructions="""You are a helpful assistant. Be concise but friendly in your responses.
        Try to provide specific, actionable information when possible."""
    )
    
    conversation_manager.conversations[thread_id] = assistant.id
    
    print("\nWelcome to the Interactive Chat!")
    print("Type 'exit' to end the conversation")
    print("Type 'clear' to start a new conversation thread")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                print("\nEnding conversation. Goodbye!")
                break
                
            if user_input.lower() == 'clear':
                thread_id = conversation_manager.thread_mgr.create_thread().id
                print("\nStarted new conversation thread!")
                continue
                
            if not user_input:
                continue
            
            # Add user message to thread
            conversation_manager.thread_mgr.add_message(
                thread_id=thread_id,
                content=user_input
            )
            
            # Get assistant's response
            response = conversation_manager.thread_mgr.run_assistant(
                thread_id=thread_id,
                assistant_id=assistant.id
            )
            
            if response:
                print(f"\nAssistant: {response}")
            else:
                print("\nAssistant: I apologize, but I couldn't generate a response. Please try again.")
                
        except KeyboardInterrupt:
            print("\nEnding conversation. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print("\nAn error occurred. Please try again.")

if __name__ == "__main__":
    asyncio.run(start_interactive_chat()) 