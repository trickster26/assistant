from flask import Flask, request, Response
from assistant.twilio_handler import TwilioHandler
from assistant.voice_chat import VoiceChat
from assistant.utils.logger import setup_logger
import asyncio
import threading
import queue

app = Flask(__name__)
logger = setup_logger(__name__)

# Shared resources
voice_chat = VoiceChat()
twilio_handler = TwilioHandler()
media_queues = {}  # Store media queues by call SID

@app.route('/incoming-call', methods=['POST'])
def handle_incoming_call():
    """Handle incoming Twilio calls"""
    try:
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
            
            # Process audio with OpenAI
            response = await voice_chat.process_audio_stream(audio_data)
            
            if response:
                # Convert response to speech and send back to call
                audio_response = voice_chat.text_to_speech(response)
                # TODO: Send audio back to Twilio stream
                
    except Exception as e:
        logger.error(f"Error processing media stream: {e}")
    finally:
        # Cleanup
        if call_sid in media_queues:
            del media_queues[call_sid]

def start_server():
    """Start the Flask server"""
    app.run(host='0.0.0.0', port=5050)

if __name__ == '__main__':
    start_server() 