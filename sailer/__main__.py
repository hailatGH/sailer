import sys
import argparse

from sailer.pg_sailer import pg_backup

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pg_backup", help="Execute postgres backup process")
    args = parser.parse_args()
    
    if args.pg_backup:
        print("Executing postgres backup process")
        pg_backup()
        sys.exit(0)
    else:
        print("No arguments passed")
        sys.exit(1)

if __name__ == "__main__":
    main()