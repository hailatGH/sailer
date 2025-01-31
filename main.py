import argparse
import logging
from pgsailer import start_scheduled_backup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description="Entrypoint script for managing sailer.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("pgsailer", help="Start the pgsailer service")
    
    args = parser.parse_args()
    if args.command == "pgsailer":
        logging.info("Starting pgsailer service.")
        start_scheduled_backup()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()