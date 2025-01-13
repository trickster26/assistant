from dataclasses import dataclass
from typing import Dict, List, Optional
from .thread_manager import ThreadManager

@dataclass
class Client:
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    last_contact: Optional[str] = None
    notes: List[str] = None
    
class ClientManager:
    def __init__(self):
        self.clients: Dict[str, Client] = {}
        self.thread_manager = ThreadManager()  # Initialize ThreadManager
        
    def add_client(self, client: Client):
        self.clients[client.id] = client
        
    def get_client_thread(self, client_id: str) -> Optional[str]:
        """Get the conversation thread ID for a client"""
        return self.thread_manager.get_or_create_thread(client_id)
        
    async def make_call(self, client_id: str, script: str):
        """Initiate a call to a client"""
        client = self.clients.get(client_id)
        if not client:
            raise ValueError(f"No client found with ID: {client_id}")
            
        # Initialize call with OpenAI's speech API
        response = await self.thread_manager.start_audio_call(
            client_id=client_id,
            phone_number=client.phone
        ) 