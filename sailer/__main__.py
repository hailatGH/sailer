import sys
import logging
import argparse

from sailer.pg_sailer import run_backup_cycle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pg_backup", help="Execute postgres backup process")
    args = parser.parse_args()
    
    if args.pg_backup:
        logging.info("Executing postgres backup process")
        run_backup_cycle()
        sys.exit(0)
    else:
        logging.info("No arguments passed")
        sys.exit(1)

if __name__ == "__main__":
    main()