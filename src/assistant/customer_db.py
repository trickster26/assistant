import json
import os
from datetime import datetime
from .utils.logger import setup_logger

logger = setup_logger(__name__)

class CustomerDB:
    def __init__(self, db_file="customer_data.json"):
        self.db_file = db_file
        self.load_db()
        
    def load_db(self):
        """Load customer database from file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    self.db = json.load(f)
            else:
                self.db = {}
                self.save_db()  # Create initial file
            logger.info(f"Loaded customer database with {len(self.db)} records")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            self.db = {}
            
    def save_db(self):
        """Save customer database to file"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.db, f, indent=2)
            logger.info("Database saved successfully")
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            
    def get_customer(self, phone_number):
        """Get customer data by phone number"""
        return self.db.get(phone_number, {})
        
    def update_customer(self, phone_number, data):
        """Update customer data"""
        if phone_number not in self.db:
            self.db[phone_number] = {}
        self.db[phone_number].update(data)
        self.save_db()
        logger.info(f"Updated customer data for {phone_number}")
        
    def store_conversation(self, phone_number, thread_id, conversation_data):
        """Store conversation data for a customer"""
        try:
            if phone_number not in self.db:
                self.db[phone_number] = {}
                
            if 'conversations' not in self.db[phone_number]:
                self.db[phone_number]['conversations'] = []
                
            conversation = {
                'thread_id': thread_id,
                'timestamp': datetime.now().isoformat(),
                'data': conversation_data
            }
            
            self.db[phone_number]['conversations'].append(conversation)
            self.save_db()
            logger.info(f"Stored conversation for {phone_number}")
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
        
    def get_last_conversation(self, phone_number):
        """Get customer's last conversation"""
        customer = self.get_customer(phone_number)
        conversations = customer.get('conversations', [])
        return conversations[-1] if conversations else None