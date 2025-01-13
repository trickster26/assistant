from flask import Flask, request, Response
from assistant.twilio_handler import TwilioHandler
from assistant.assistant_handler import AssistantHandler
from assistant.customer_db import CustomerDB
from assistant.utils.logger import setup_logger
import asyncio
import threading
import queue
import tempfile
import os
import time

app = Flask(__name__)
logger = setup_logger(__name__)

# Shared resources
twilio_handler = TwilioHandler()
assistant_handler = AssistantHandler()
customer_db = CustomerDB()
media_queues = {}  # Store media queues by call SID
active_calls = {}  # Store call state

# Initialize the assistant
with app.app_context():
    assistant_handler.create_assistant()

@app.route('/incoming-call', methods=['POST'])
def handle_incoming_call():
    """Handle incoming Twilio calls"""
    try:
        call_sid = request.values.get('CallSid')
        phone_number = request.values.get('From')
        logger.info(f"Incoming call from {phone_number}: {call_sid}")
        
        # Initialize call state
        active_calls[call_sid] = {
            'phone_number': phone_number,
            'last_transcript': None,
            'processing': False,
            'start_time': time.time()
        }
        
        # Get customer data
        customer = customer_db.get_customer(phone_number)
        if customer:
            logger.info(f"Returning customer: {customer.get('name', 'Unknown')}")
        
        # Generate TwiML response
        response = twilio_handler.generate_twiml_for_stream()
        return Response(response, mimetype='text/xml')
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        return str(e), 500

@app.route('/gather', methods=['POST'])
def handle_gather():
    """Handle gathered speech input"""
    try:
        call_sid = request.values.get('CallSid')
        phone_number = request.values.get('From')
        speech_result = request.values.get('SpeechResult')
        
        logger.info(f"Received speech from {phone_number}: {speech_result}")
        
        if speech_result:
            # Get customer data
            customer = customer_db.get_customer(phone_number)
            customer_name = customer.get('name', 'Customer')
            
            # Create an event loop for async processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Process with assistant
                response = loop.run_until_complete(
                    assistant_handler.process_rental_conversation(
                        phone_number, 
                        customer_name, 
                        speech_result
                    )
                )
                logger.info(f"Assistant response: {response}")
                
                # Send response back to call
                twilio_handler.send_message_to_call(call_sid, response)
                
            finally:
                loop.close()
        
        # Return TwiML to continue gathering
        response = twilio_handler.generate_twiml_for_stream()
        return Response(response, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"Error in gather: {e}")
        error_response = twilio_handler.generate_error_response()
        return Response(error_response, mimetype='text/xml')

@app.route('/call-status', methods=['POST'])
def handle_call_status():
    """Handle call status callbacks"""
    try:
        call_sid = request.values.get('CallSid')
        call_status = request.values.get('CallStatus')
        logger.info(f"Call {call_sid} status: {call_status}")
        
        if call_status in ['completed', 'failed']:
            # Cleanup call resources
            if call_sid in active_calls:
                del active_calls[call_sid]
            if call_sid in media_queues:
                del media_queues[call_sid]
                
    except Exception as e:
        logger.error(f"Error in call status: {e}")
        
    return '', 200

@app.route('/fallback', methods=['POST'])
def handle_fallback():
    """Handle fallback for failed requests"""
    try:
        call_sid = request.values.get('CallSid')
        logger.warning(f"Fallback triggered for call {call_sid}")
        
        response = twilio_handler.generate_error_response(
            "I apologize, but I'm having trouble. Let me restart our conversation."
        )
        return Response(response, mimetype='text/xml')
    except Exception as e:
        logger.error(f"Error in fallback: {e}")
        return '', 500

def start_server():
    """Start the Flask server"""
    app.run(host='0.0.0.0', port=5050, threaded=True)

if __name__ == '__main__':
    start_server() 