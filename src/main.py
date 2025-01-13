from assistant.utils.audio_config import configure_audio
from assistant.client_manager import ClientManager
from assistant.conversation_manager import ConversationManager
from assistant.call_script import CallScript
from assistant.conversation_history import ConversationHistory
from test_data.clients import get_test_clients
from assistant.utils.logger import setup_logger
import asyncio

# Configure audio settings
configure_audio()
logger = setup_logger("test_client_calls")

async def simulate_client_interaction():
    # Initialize managers
    client_manager = ClientManager()
    conversation_manager = ConversationManager()
    call_script = CallScript()
    history_manager = ConversationHistory()
    
    # Load test clients
    test_clients = get_test_clients()
    
    # Process each client
    for client_data in test_clients:
        try:
            logger.info(f"\nProcessing client: {client_data['name']}")
            
            # Get client's last conversation
            last_conversation = history_manager.get_client_conversation_history(client_data["id"])
            
            # Generate script based on history
            script = call_script.generate_script(last_conversation[0] if last_conversation else None)
            
            # Format script with client's name
            formatted_script = [
                line.format(client_name=client_data["name"]) 
                for line in script
            ]
            
            logger.info(f"Using script: {formatted_script}")
            
            # Handle conversation
            success = await conversation_manager.handle_conversation(
                client_id=client_data["id"],
                script=formatted_script
            )
            
            if success:
                logger.info(f"Successfully completed conversation with {client_data['name']}")
            else:
                logger.warning(f"Conversation with {client_data['name']} completed with warnings")
            
        except Exception as e:
            logger.error(f"Error processing client {client_data['id']}: {str(e)}")
            continue

if __name__ == "__main__":
    asyncio.run(simulate_client_interaction()) 