from openai import OpenAI
from ..config.settings import OPENAI_API_KEY, ASSISTANT_MODEL

class AssistantManager:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.assistant = None

    def create_assistant(self, name, instructions, tools=None):
        """Create a new assistant with specified parameters"""
        self.assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=ASSISTANT_MODEL,
            tools=tools or []
        )
        return self.assistant

    def get_assistant(self, assistant_id):
        """Retrieve an existing assistant"""
        return self.client.beta.assistants.retrieve(assistant_id)

    def update_assistant(self, assistant_id, **kwargs):
        """Update assistant properties"""
        return self.client.beta.assistants.update(assistant_id, **kwargs)

    def delete_assistant(self, assistant_id):
        """Delete an assistant"""
        return self.client.beta.assistants.delete(assistant_id) 