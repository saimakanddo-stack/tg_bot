import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Configuration variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
JSON_URL = os.getenv("JSON_URL")
BLOG_URL = os.getenv("BLOG_URL")

# Validation
if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN not found in environment or .env file.")
if not JSON_URL:
    raise ValueError("Error: JSON_URL not found in environment or .env file.")
if not BLOG_URL:
    raise ValueError("Error: BLOG_URL not found in environment or .env file.")
