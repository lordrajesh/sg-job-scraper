import os
from dotenv import load_dotenv

load_dotenv()

# Global settings from .env
MIN_DELAY = int(os.getenv("MIN_DELAY", 2))
MAX_DELAY = int(os.getenv("MAX_DELAY", 5))
MAX_PAGES = int(os.getenv("MAX_PAGES", 5))
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "csv")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
