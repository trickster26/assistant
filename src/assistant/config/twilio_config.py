from dotenv import load_dotenv
import os

load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Server configuration
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5050")
WEBHOOK_PATH = "/incoming-call"
WEBHOOK_URL = f"{SERVER_URL}{WEBHOOK_PATH}"

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    raise ValueError("Missing required Twilio environment variables") 