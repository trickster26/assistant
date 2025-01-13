from assistant.twilio_handler import TwilioHandler
from assistant.assistant_handler import AssistantHandler
from assistant.customer_db import CustomerDB
from assistant.config.rental_config import RENTAL_SCRIPT
import asyncio
import logging

logger = logging.getLogger(__name__)

class RentalCallManager:
    def __init__(self):
        self.twilio_handler = TwilioHandler()
        self.assistant_handler = AssistantHandler()
        self.customer_db = CustomerDB()
        
    async def initiate_rental_calls(self, customers):
        """Initiate calls to customers"""
        for customer in customers:
            try:
                # Format initial greeting
                greeting = RENTAL_SCRIPT['greeting'].format(
                    customer_name=customer['name']
                )
                
                # Start call
                call_sid = self.twilio_handler.make_call(customer['phone'])
                logger.info(f"Initiated call to {customer['name']}: {call_sid}")
                
                # Store initial customer data
                self.customer_db.update_customer(
                    customer['phone'],
                    {
                        'name': customer['name'],
                        'current_call_sid': call_sid
                    }
                )
                
            except Exception as e:
                logger.error(f"Error calling {customer['name']}: {e}")

# Usage example:
if __name__ == "__main__":
    # Sample customer list
    customers = [
        {"name": "John Smith", "phone": "+1234567890"},
        {"name": "Sarah Johnson", "phone": "+1987654321"}
    ]
    
    # Initialize and run
    call_manager = RentalCallManager()
    asyncio.run(call_manager.initiate_rental_calls(customers)) 