from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from .config.twilio_config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    SERVER_URL
)
from .utils.logger import setup_logger

logger = setup_logger(__name__)

class TwilioHandler:
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.phone_number = TWILIO_PHONE_NUMBER
        
    def make_call(self, to_number):
        """Initiate a call"""
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=f"{SERVER_URL}/incoming-call",
                record=True
            )
            return call.sid
        except Exception as e:
            logger.error(f"Error making call: {e}")
            raise
            
    def generate_response_twiml(self, audio_file=None, gather=True):
        """Generate TwiML response"""
        try:
            response = VoiceResponse()
            
            if audio_file:
                response.play(audio_file)
            
            if gather:
                gather = Gather(
                    input='speech',
                    action=f"{SERVER_URL}/handle-input",
                    method='POST',
                    timeout=3,
                    speechTimeout='auto'
                )
                response.append(gather)
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error generating TwiML: {e}")
            raise