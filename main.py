import argparse
from pgsailer import start_schedueled_backup
from tools import generate_age_keys

def start_pgsailer():
    print("Starting pgsailer...")
    start_schedueled_backup()

def generate_keys():
    print("Generating age keys...")
    generate_age_keys()

def main():
    parser = argparse.ArgumentParser(
        description="Entrypoint script for managing sailer."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("pgsailer", help="Start the pgsailer service")
    subparsers.add_parser("generate_keys", help="Generates the keys")

    args = parser.parse_args()

    if args.command == "pgsailer":
        return start_pgsailer()
    
    if args.command == "generate_keys":
        return generate_keys()

    return parser.print_help()


if __name__ == "__main__":
    main()
