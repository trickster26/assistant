from flask import Flask, request, Response
from assistant.assistant_handler import AssistantHandler
from assistant.twilio_handler import TwilioHandler
import asyncio
import os

app = Flask(__name__)
assistant_handler = AssistantHandler()
twilio_handler = TwilioHandler()

# Initialize the assistant
with app.app_context():
    assistant_handler.create_assistant()

@app.route('/incoming-call', methods=['POST'])
def handle_incoming_call():
    """Handle incoming calls"""
    try:
        response = twilio_handler.generate_response_twiml(
            gather=True
        )
        return Response(response, mimetype='text/xml')
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        return str(e), 500

@app.route('/handle-input', methods=['POST'])
async def handle_input():
    """Handle voice input"""
    try:
        # Get audio data from request
        audio_data = request.files['recording'].read() if 'recording' in request.files else None
        thread_id = request.values.get('thread_id')
        
        if audio_data:
            # Process conversation
            result = await assistant_handler.process_audio_conversation(
                audio_data,
                thread_id
            )
            
            # Generate response with audio
            response = twilio_handler.generate_response_twiml(
                audio_file=result['audio_file'],
                gather=True
            )
            
            return Response(response, mimetype='text/xml')
            
    except Exception as e:
        logger.error(f"Error handling input: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 