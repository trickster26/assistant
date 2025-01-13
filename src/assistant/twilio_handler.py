from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect
from .config.twilio_config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER
)
from .utils.logger import setup_logger

logger = setup_logger(__name__)

class TwilioHandler:
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.phone_number = TWILIO_PHONE_NUMBER
        
    def make_call(self, to_number):
        """Initiate a call to the specified number"""
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=f"{SERVER_URL}/incoming-call",
                record=True
            )
            logger.info(f"Initiated call: {call.sid}")
            return call.sid
        except Exception as e:
            logger.error(f"Error making call: {e}")
            raise
            
    def generate_twiml_for_stream(self):
        """Generate TwiML for media streams"""
        response = VoiceResponse()
        
        # Add initial greeting
        response.say("Hello! I'm your AI assistant. How can I help you today?")
        
        # Connect to media stream
        connect = Connect()
        connect.stream(url=f"{SERVER_URL}/media-stream")
        response.append(connect)
        
        return str(response) 

    def send_message_to_call(self, call_sid, message):
        """Send a message to an active call"""
        try:
            response = VoiceResponse()
            response.say(message)
            
            self.client.calls(call_sid).update(
                twiml=str(response)
            )
            logger.info(f"Sent message to call {call_sid}")
        except Exception as e:
            logger.error(f"Error sending message to call: {e}") 