from assistant.conversation_manager import ConversationManager
import asyncio
from utils.logger import setup_logger

logger = setup_logger("main")

async def main():
    # Initialize conversation manager
    conv_manager = ConversationManager()
    
    try:
        # Create a new conversation
        conversation = conv_manager.create_conversation(
            instructions="You are a helpful assistant that provides clear and concise responses."
        )
        
        # Send a message and get response
        response = await conv_manager.send_message(
            conversation.thread_id,
            "Hello! Can you help me with a Python question?"
        )
        logger.info(f"Assistant's response: {response}")

        # Add some metadata
        conv_manager.add_metadata(
            conversation.thread_id,
            "topic",
            "Python programming"
        )

        # Get conversation history
        history = conv_manager.get_conversation_history(conversation.thread_id)
        logger.info("Conversation history:")
        for msg in history:
            logger.info(f"{msg['role']}: {msg['content'][:50]}...")

        # Close the conversation
        conv_manager.close_conversation(conversation.thread_id)

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 