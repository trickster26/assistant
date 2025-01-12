from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class MessageStats:
    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    average_response_time: float = 0.0
    last_message_time: datetime = None
    
class ConversationStats:
    def __init__(self):
        self.start_time = datetime.now()
        self.message_stats = MessageStats()
        self.response_times: List[float] = []
        self.topics: Dict[str, int] = {}  # Track conversation topics
        
    def update_message_stats(self, role: str, response_time: float = None):
        self.message_stats.total_messages += 1
        self.message_stats.last_message_time = datetime.now()
        
        if role == "user":
            self.message_stats.user_messages += 1
        elif role == "assistant":
            self.message_stats.assistant_messages += 1
            if response_time:
                self.response_times.append(response_time)
                self.message_stats.average_response_time = sum(self.response_times) / len(self.response_times)
    
    def get_conversation_duration(self) -> float:
        """Get conversation duration in minutes"""
        return (datetime.now() - self.start_time).total_seconds() / 60 