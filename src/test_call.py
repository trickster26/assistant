from assistant.twilio_handler import TwilioHandler
import time
from assistant.utils.logger import setup_logger

logger = setup_logger(__name__)

def test_outbound_call():
    try:
        # Initialize Twilio handler
        twilio = TwilioHandler()
        
        # Replace with the phone number you want to call
        to_number = "+1234567890"  # Your test phone number
        
        # Make the call
        logger.info(f"Initiating call to {to_number}")
        call_sid = twilio.make_call(to_number)
        
        logger.info(f"Call initiated with SID: {call_sid}")
        
        # Wait for a while to keep the script running
        logger.info("Call in progress. Press Ctrl+C to end...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Test ended by user")
    except Exception as e:
        logger.error(f"Error during test: {e}")

if __name__ == "__main__":
    test_outbound_call() 