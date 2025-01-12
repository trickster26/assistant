from openai import OpenAI
from .config.settings import OPENAI_API_KEY
import time

class ThreadManager:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.thread = None

    def create_thread(self):
        """Create a new thread"""
        self.thread = self.client.beta.threads.create()
        return self.thread

    def add_message(self, thread_id, content, role="user"):
        """Add a message to the thread"""
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )

    def run_assistant(self, thread_id, assistant_id):
        """Run the assistant on the thread"""
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        return self._wait_for_completion(thread_id, run.id)

    def _wait_for_completion(self, thread_id, run_id):
        """Wait for the assistant's response"""
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(thread_id=thread_id)
                return messages.data[0].content[0].text.value
            elif run.status == "failed":
                raise Exception("Assistant run failed")
            time.sleep(1)

    def get_messages(self, thread_id):
        """Get all messages in a thread"""
        return self.client.beta.threads.messages.list(thread_id=thread_id) 