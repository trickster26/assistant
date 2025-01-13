from datetime import datetime, timedelta
from typing import List, Dict

# Sample client data with various scenarios
TEST_CLIENTS = [
    {
        "id": "client1",
        "name": "John Smith",
        "phone": "+1234567890",
        "email": "john.smith@email.com",
        "last_contact": (datetime.now() - timedelta(days=30)).isoformat(),
        "notes": ["Interested in premium package", "Prefers morning calls"],
        "preferred_time": "09:00-12:00",
        "timezone": "America/New_York"
    },
    {
        "id": "client2",
        "name": "Sarah Johnson",
        "phone": "+1987654321",
        "email": "sarah.j@email.com",
        "last_contact": (datetime.now() - timedelta(days=15)).isoformat(),
        "notes": ["Currently using basic plan", "Looking to upgrade"],
        "preferred_time": "14:00-17:00",
        "timezone": "America/Chicago"
    },
    {
        "id": "client3",
        "name": "Michael Chen",
        "phone": "+1122334455",
        "email": "m.chen@email.com",
        "last_contact": None,  # New client
        "notes": ["New lead", "Requested information about services"],
        "preferred_time": "11:00-15:00",
        "timezone": "America/Los_Angeles"
    }
]

# Sample conversation history
SAMPLE_CONVERSATIONS = {
    "client1": [
        {
            "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
            "summary": "Discussed premium package features",
            "key_points": ["Interested in pricing", "Asked about implementation timeline"],
            "follow_up_needed": True
        }
    ],
    "client2": [
        {
            "timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
            "summary": "Reviewed current plan usage",
            "key_points": ["Experiencing growth", "Need more capacity"],
            "follow_up_needed": True
        }
    ]
}

def get_test_clients() -> List[Dict]:
    """Return test client data"""
    return TEST_CLIENTS

def get_client_conversation_history(client_id: str) -> List[Dict]:
    """Return conversation history for a specific client"""
    return SAMPLE_CONVERSATIONS.get(client_id, []) 