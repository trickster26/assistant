from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

class ConversationHistory:
    def __init__(self, storage_dir: str = "conversation_history"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
    def save_conversation(self, client_id: str, thread_id: str, conversation: Dict) -> None:
        """Save conversation history to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{client_id}_{thread_id}_{timestamp}.json"
        
        conversation_data = {
            "client_id": client_id,
            "thread_id": thread_id,
            "timestamp": timestamp,
            "conversation": conversation
        }
        
        with open(self.storage_dir / filename, 'w') as f:
            json.dump(conversation_data, f, indent=2)
            
    def get_client_history(self, client_id: str) -> List[Dict]:
        """Get all conversation history for a client"""
        conversations = []
        for file in self.storage_dir.glob(f"{client_id}_*.json"):
            with open(file, 'r') as f:
                conversations.append(json.load(f))
        return sorted(conversations, key=lambda x: x['timestamp'], reverse=True)
        
    def get_last_conversation(self, client_id: str) -> Optional[Dict]:
        """Get the most recent conversation for a client"""
        history = self.get_client_history(client_id)
        return history[0] if history else None
        
    def get_client_conversation_history(self, client_id: str) -> List[Dict]:
        """Get conversation history for a specific client"""
        from test_data.clients import get_client_conversation_history
        # For testing, we'll use the sample data
        return get_client_conversation_history(client_id) 