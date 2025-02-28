import logging
import dataconf
from dotenv import load_dotenv

from sailer.dto import ENV

# Load environment variables
load_dotenv()
env = dataconf.env("SAILER_", ENV)

# Set up logging
logging.basicConfig(level=logging.INFO)
logging.info("Starting sailer")
logging.info(f"Environment: {env}")