import os
import sys
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger("kpop_reporter")


logger = setup_logging()

# Environment settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
REDDIT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
