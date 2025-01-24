import os
import time
import datetime
import psycopg2
import subprocess
from croniter import croniter
from datetime import datetime

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
CRON_EXP = os.getenv("BACKUP_SCHEDULE", "0 0 * * *")

BACKUP_DIR = "/app/backups/"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

os.makedirs(BACKUP_DIR, exist_ok=True)


def get_all_databases():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        cursor = conn.cursor()

        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return databases
    except Exception as e:
        print(f"Error fetching database list: {e}")
        return []


def backup_database(db_name):
    backup_file = os.path.join(BACKUP_DIR, f"{db_name}_backup_{TIMESTAMP}.sql")

    pg_dump_cmd = [
        "pg_dump",
        "-h",
        DB_HOST,
        "-p",
        DB_PORT,
        "-U",
        DB_USER,
        "-d",
        db_name,
        "-f",
        backup_file,
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    try:
        subprocess.run(pg_dump_cmd, env=env, check=True)
        print(f"Backup successful for database {db_name}: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Backup failed for database {db_name}: {e}")


def backup_all_databases():
    databases = get_all_databases()
    if not databases:
        print("No databases found to back up.")
        return

    for db in databases:
        print(f"Backing up database: {db}")
        backup_database(db)


if __name__ == "__main__":
    iter = croniter(CRON_EXP, datetime.now())

    while True:
        if croniter.match(CRON_EXP, datetime.now()):
            backup_all_databases()
        sleep_duration = (iter.get_next(datetime) - datetime.now()).total_seconds()
        print(f"sleeping for {sleep_duration}")
        time.sleep(sleep_duration)
