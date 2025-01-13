from assistant.twilio_handler import TwilioHandler
import time
from assistant.utils.logger import setup_logger

logger = setup_logger(__name__)

def monitor_calls():
    twilio = TwilioHandler()
    
    try:
        while True:
            # Get recent calls
            calls = twilio.client.calls.list(limit=20)
            
            print("\nRecent Calls:")
            print("-" * 50)
            for call in calls:
                print(f"SID: {call.sid}")
                print(f"To: {call.to}")
                print(f"From: {call.from_}")
                print(f"Status: {call.status}")
                print(f"Duration: {call.duration}s")
                print("-" * 50)
                
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\nMonitoring ended by user")

if __name__ == "__main__":
    monitor_calls() 