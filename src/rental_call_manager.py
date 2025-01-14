from assistant.twilio_handler import TwilioHandler
from assistant.assistant_handler import AssistantHandler
from assistant.customer_db import CustomerDB
from assistant.config.rental_config import RENTAL_SCRIPT
from assistant.utils.logger import setup_logger
import asyncio
import json

logger = setup_logger(__name__)

class RentalCallManager:
    def __init__(self):
        self.twilio_handler = TwilioHandler()
        self.assistant_handler = AssistantHandler()
        self.customer_db = CustomerDB()
        logger.info("RentalCallManager initialized")
        
    async def initiate_rental_calls(self, customers):
        """Initiate calls to customers"""
        for customer in customers:
            try:
                # Format initial greeting
                greeting = RENTAL_SCRIPT['greeting'].format(
                    customer_name=customer['name']
                )
                
                # Store or update customer data
                self.customer_db.update_customer(
                    customer['phone'],
                    {
                        'name': customer['name'],
                        'last_contact': None,
                        'rental_status': 'pending'
                    }
                )
                
                # Start call
                call_sid = self.twilio_handler.make_call(customer['phone'])
                logger.info(f"Initiated call to {customer['name']}: {call_sid}")
                
                # Update customer with call info
                self.customer_db.update_customer(
                    customer['phone'],
                    {
                        'current_call_sid': call_sid,
                        'last_contact': 'outbound_call'
                    }
                )
                
                # Wait briefly between calls
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error calling {customer['name']}: {e}")

def main():
    # Sample customer list - you can modify this or load from a file
    customers = [
        {
            "name": "John Smith",
            "phone": "+917009614671"
        },
        {
            "name": "Sarah Johnson",
            "phone": "+9174885 41302"
        }
    ]
    
    try:
        # Initialize manager
        call_manager = RentalCallManager()
        
        # Run the calls
        asyncio.run(call_manager.initiate_rental_calls(customers))
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        
if __name__ == "__main__":
    main() 