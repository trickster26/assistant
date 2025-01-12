from assistant.conversation_manager import ConversationManager
import asyncio
from utils.logger import setup_logger

logger = setup_logger("main")

async def dynamic_conversation():
    conv_manager = ConversationManager()
    
    try:
        # Create a new conversation
        conversation = conv_manager.create_conversation(
            instructions="You are a helpful assistant that provides clear and concise responses."
        )
        
        print("Start chatting with the assistant! Type 'exit' to end the conversation.")
        
        while True:
            # Get user input
            user_input = input("You: ")
            
            if user_input.lower() == 'exit':
                print("Ending conversation...")
                break
            
            # Send message and get response
            response = await conv_manager.send_message(
                conversation.thread_id,
                user_input
            )
            
            print(f"Assistant: {response}")

        # Optionally, print conversation stats
        history = conv_manager.get_conversation_history(conversation.thread_id)
        stats = history['stats']
        print("\nConversation Stats:")
        print(f"Total Messages: {stats['total_messages']}")
        print(f"User Messages: {stats['user_messages']}")
        print(f"Assistant Messages: {stats['assistant_messages']}")
        print(f"Average Response Time: {stats['average_response_time']:.2f} seconds")
        print(f"Conversation Duration: {stats['conversation_duration']:.2f} minutes")

    except Exception as e:
        logger.error(f"Error in dynamic conversation: {str(e)}")

if __name__ == "__main__":
    asyncio.run(dynamic_conversation()) 