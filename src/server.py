from flask import Flask, request, Response
from assistant.twilio_handler import TwilioHandler
from assistant.assistant_handler import AssistantHandler
from assistant.voice_chat import VoiceChat
from assistant.utils.logger import setup_logger
import asyncio
import threading
import queue
import tempfile
import os

app = Flask(__name__)
logger = setup_logger(__name__)

# Shared resources
voice_chat = VoiceChat()
twilio_handler = TwilioHandler()
assistant_handler = AssistantHandler()
media_queues = {}  # Store media queues by call SID
active_calls = {}  # Store call state

@app.before_first_request
def setup_assistant():
    """Initialize the OpenAI assistant"""
    assistant_handler.create_assistant()

@app.route('/incoming-call', methods=['POST'])
def handle_incoming_call():
    """Handle incoming Twilio calls"""
    try:
        call_sid = request.values.get('CallSid')
        logger.info(f"Incoming call: {call_sid}")
        
        # Initialize call state
        active_calls[call_sid] = {
            'last_transcript': None,
            'processing': False
        }
        
        # Generate TwiML response with media stream
        response = twilio_handler.generate_twiml_for_stream()
        return Response(response, mimetype='text/xml')
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        return str(e), 500

@app.route('/media-stream', methods=['POST'])
def handle_media_stream():
    """Handle media stream from Twilio"""
    call_sid = request.values.get('CallSid')
    
    if call_sid not in media_queues:
        media_queues[call_sid] = queue.Queue()
        
        # Start processing thread for this call
        def process_audio():
            asyncio.run(process_media_stream(call_sid))
            
        threading.Thread(target=process_audio, daemon=True).start()
    
    # Add incoming audio to queue
    if 'media' in request.files:
        audio_data = request.files['media'].read()
        media_queues[call_sid].put(audio_data)
    
    return '', 200

async def process_media_stream(call_sid):
    """Process media stream for a call"""
    try:
        while True:
            # Get audio from queue
            audio_data = media_queues[call_sid].get()
            
            if active_calls[call_sid]['processing']:
                continue
                
            active_calls[call_sid]['processing'] = True
            
            try:
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                    temp_audio.write(audio_data)
                    temp_audio_path = temp_audio.name
                
                # Transcribe audio
                transcript = voice_chat.transcribe_audio(temp_audio_path)
                
                # Clean up temp file
                os.unlink(temp_audio_path)
                
                if transcript and transcript != active_calls[call_sid]['last_transcript']:
                    active_calls[call_sid]['last_transcript'] = transcript
                    logger.info(f"Transcribed: {transcript}")
                    
                    # Process with assistant
                    response = await assistant_handler.process_message(call_sid, transcript)
                    logger.info(f"Assistant response: {response}")
                    
                    # Convert to speech
                    speech_file = voice_chat.text_to_speech(response)
                    
                    if speech_file:
                        # TODO: Send audio back to Twilio stream
                        # For now, we'll use TwiML Say
                        twilio_handler.send_message_to_call(call_sid, response)
                        
                        # Clean up speech file
                        os.unlink(speech_file)
                        
            finally:
                active_calls[call_sid]['processing'] = False
                
    except Exception as e:
        logger.error(f"Error processing media stream: {e}")
    finally:
        # Cleanup
        if call_sid in media_queues:
            del media_queues[call_sid]
        if call_sid in active_calls:
            del active_calls[call_sid]

def start_server():
    """Start the Flask server"""
    app.run(host='0.0.0.0', port=5050)

if __name__ == '__main__':
    start_server() 