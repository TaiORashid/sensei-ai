import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# API KEY CONFIGURATION
# ============================================
# Set your Google API key in the .env file:
# GOOGLE_API_KEY=your_api_key_here
# ============================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. Please set it in the .env file:\n"
        "GOOGLE_API_KEY=your_api_key_here"
    )

# Model configuration
MODEL_NAME = "gemini-2.5-flash"

# Document processing settings
CHUNK_SIZE = 2000
OVERLAP_SIZE = 200
MAX_PAGES_PER_REQUEST = 50
