from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Start, Stream
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
        """Initiate a call to the specified number"""
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=f"{SERVER_URL}/incoming-call",
                record=True,
                timeout=600,  # 10 min timeout
                status_callback=f"{SERVER_URL}/call-status",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST'
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
        response.say("Hello! I'm your AI assistant. How can I help you today?", voice='alice')
        
        # Start the stream
        connect = Connect()
        stream = Stream(name='audio_stream', url=f"{SERVER_URL}/media-stream")
        stream.parameter(name='track', value='both_tracks')
        connect.stream(stream)
        response.append(connect)
        
        # Add a gather to keep the call alive and capture DTMF
        response.gather(
            input='speech dtmf',
            action=f"{SERVER_URL}/gather",
            method='POST',
            timeout=3600,
            speechTimeout='auto'
        )
        
        return str(response)
        
    def send_message_to_call(self, call_sid, message):
        """Send a message to an active call"""
        try:
            logger.info(f"Sending message to call {call_sid}: {message}")
            
            # Create TwiML response
            response = VoiceResponse()
            response.say(message, voice='alice')
            
            # Add gather after message to keep listening
            response.gather(
                input='speech dtmf',
                action=f"{SERVER_URL}/gather",
                method='POST',
                timeout=3600,
                speechTimeout='auto'
            )
            
            # Convert TwiML to string
            twiml_str = str(response)
            logger.info(f"Generated TwiML: {twiml_str}")
            
            # Update the call
            call = self.client.calls(call_sid).fetch()
            if call.status in ['in-progress', 'ringing']:
                self.client.calls(call_sid).update(twiml=twiml_str)
                logger.info(f"Successfully updated call {call_sid}")
            else:
                logger.warning(f"Call {call_sid} is not active (status: {call.status})")
                
        except Exception as e:
            logger.error(f"Error sending message to call: {str(e)}", exc_info=True)
            raise
            
    def keep_call_alive(self, call_sid):
        """Send empty TwiML to keep the call active"""
        try:
            response = VoiceResponse()
            response.gather(
                input='speech dtmf',
                action=f"{SERVER_URL}/gather",
                method='POST',
                timeout=600,
                speechTimeout='auto'
            )
            return str(response)
        except Exception as e:
            logger.error(f"Error keeping call alive: {e}")
            return None 