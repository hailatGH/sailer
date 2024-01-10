import argparse
from pgsailer import start_schedueled_backup


def start_pgsailer():
    print("Starting pgsailer...")
    start_schedueled_backup()


def main():
    parser = argparse.ArgumentParser(
        description="Entrypoint script for managing sailer."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("pgsailer", help="Start the pgsailer service")

    args = parser.parse_args()

    if args.command == "pgsailer":
        return start_pgsailer()

    return parser.print_help()


if __name__ == "__main__":
    main()
