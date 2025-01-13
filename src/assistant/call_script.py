from typing import List, Dict, Optional

class CallScript:
    def __init__(self):
        self.questions: List[Dict] = [
            {
                "id": "greeting",
                "text": "Hello {client_name}, this is AI assistant calling from {company_name}. How are you today?",
                "type": "open"
            },
            {
                "id": "availability",
                "text": "I'm calling to {purpose}. Do you have a few minutes to talk?",
                "type": "yes_no"
            },
            {
                "id": "follow_up",
                "text": "Last time we spoke about {previous_topic}. Have you had a chance to consider that?",
                "type": "yes_no"
            }
        ]
        
    def generate_script(self, last_conversation: Optional[Dict] = None) -> List[str]:
        """Generate conversation script based on history"""
        script = []
        
        # Default company info - in production, this would come from config
        company_info = {
            "name": "ACME Corp",
            "purpose": "discuss our latest services"
        }
        
        # Basic greeting
        greeting = self.questions[0]["text"].format(
            client_name="{client_name}",
            company_name=company_info["name"]
        )
        script.append(greeting)
        
        # If there's previous conversation history, add follow-up
        if last_conversation and last_conversation.get("key_points"):
            follow_up = self.questions[2]["text"].format(
                previous_topic=last_conversation["key_points"][0]
            )
            script.append(follow_up)
        else:
            # If no history, use availability question
            availability = self.questions[1]["text"].format(
                purpose=company_info["purpose"]
            )
            script.append(availability)
            
        return script

    def get_next_question(self, current_id: str, previous_response: str) -> Dict:
        """Get next question based on previous response"""
        # Find current question index
        current_index = next(
            (i for i, q in enumerate(self.questions) if q["id"] == current_id),
            -1
        )
        
        if current_index < len(self.questions) - 1:
            return self.questions[current_index + 1]
        return None 