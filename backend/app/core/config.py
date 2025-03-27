import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
USER_DAILY_LIMIT = int(os.getenv("USER_DAILY_LIMIT", 3))