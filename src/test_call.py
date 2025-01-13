from assistant.twilio_handler import TwilioHandler
import time
from assistant.utils.logger import setup_logger
from datetime import datetime

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
        start_time = datetime.now()
        
        # Monitor call duration
        while True:
            time.sleep(1)
            duration = datetime.now() - start_time
            logger.info(f"Call duration: {duration}")
            
            # Get call status
            call = twilio.client.calls(call_sid).fetch()
            logger.info(f"Call status: {call.status}")
            
            if call.status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
                logger.info(f"Call ended with status: {call.status}")
                break
            
    except KeyboardInterrupt:
        logger.info("Test ended by user")
    except Exception as e:
        logger.error(f"Error during test: {e}")

if __name__ == "__main__":
    test_outbound_call() 