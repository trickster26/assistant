from openai import OpenAI
from .config.settings import OPENAI_API_KEY
import time
from typing import Optional

class ThreadManager:
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.threads = {}
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _retry_operation(self, operation, *args, **kwargs):
        """Generic retry mechanism for API operations"""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_error = e
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        raise last_error

    def get_or_create_thread(self, client_id):
        """Get existing thread or create new one for client"""
        if client_id not in self.threads:
            thread = self.client.beta.threads.create()
            self.threads[client_id] = thread.id
        return self.threads[client_id]

    def create_thread(self):
        """Create a new thread"""
        thread = self.client.beta.threads.create()
        return thread

    def add_message(self, thread_id, content, role="user"):
        """Add a message to the thread"""
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )

    def run_assistant(self, thread_id: str, assistant_id: str) -> Optional[str]:
        """Run the assistant on the thread with retry logic"""
        try:
            run = self._retry_operation(
                self.client.beta.threads.runs.create,
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            return self._wait_for_completion(thread_id, run.id)
        except Exception as e:
            print(f"Error running assistant: {str(e)}")
            return None

    def _wait_for_completion(self, thread_id: str, run_id: str, timeout: int = 30) -> Optional[str]:
        """Wait for the assistant's response with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                run = self._retry_operation(
                    self.client.beta.threads.runs.retrieve,
                    thread_id=thread_id,
                    run_id=run_id
                )
                
                if run.status == "completed":
                    messages = self._retry_operation(
                        self.client.beta.threads.messages.list,
                        thread_id=thread_id
                    )
                    return messages.data[0].content[0].text.value
                elif run.status == "failed":
                    print(f"Run failed with status: {run.status}")
                    return None
                elif run.status == "expired":
                    print("Run expired")
                    return None
                    
                time.sleep(1)
            except Exception as e:
                print(f"Error checking run status: {str(e)}")
                time.sleep(1)
                
        print("Timeout waiting for assistant response")
        return None

    def get_messages(self, thread_id):
        """Get all messages in a thread"""
        return self.client.beta.threads.messages.list(thread_id=thread_id) 