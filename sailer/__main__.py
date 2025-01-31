import logging
import argparse

from pgsailer.backup import BackupScheduler


def main():
    parser = argparse.ArgumentParser(
        description="Entrypoint script for managing sailer."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("pgsailer", help="Start the pgsailer service")

    args = parser.parse_args()
    if args.command == "pgsailer":
        logging.info("Starting pgsailer service.")
        logging.info("Starting scheduled backup...")
        scheduler = BackupScheduler()
        scheduler.start()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
