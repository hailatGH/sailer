import time
from docpgsailer import logger

if __name__ == "__main__":
    while True:
        logger.debug(
            "This is a debug message."
        )  # Won't be logged because level is INFO
        logger.info("This is an info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        logger.critical("This is a critical message.")
        time.sleep(10)
