from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5050"))

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables") 