import logging
import dataconf
from dotenv import load_dotenv

from sailer.dto import ENV

# Load environment variables
load_dotenv()
env = dataconf.env("SAILER_", ENV)

# Configure logging at the top of the file.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info("Starting sailer")