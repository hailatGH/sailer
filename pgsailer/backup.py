import os
import time
import logging
import datetime
import psycopg2
import subprocess
from croniter import croniter
from datetime import datetime
from tools import generate_age_keys

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
CRON_EXP = os.getenv("BACKUP_SCHEDULE", "0 0 * * *")

def get_formatted_datetime():
    now = datetime.now()
    year = now.year
    month = now.strftime('%b')
    day = now.day
    hour = now.hour
    minute = now.minute

    formatted_output = f"{year}/{month}/{day}/{hour:02}/{minute:02}"
    return formatted_output


def get_all_databases():
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


def backup_database(db_name):
    now = get_formatted_datetime()
    BACKUP_DIR = f"/app/backups/{now}"
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    backup_file = os.path.join(BACKUP_DIR, f"{db_name}_backup.sql")

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

    subprocess.run(pg_dump_cmd, env=env, check=True)
    print(f"Backup successful for database {db_name}: {backup_file}")
    
    return backup_file


def encrypt_backup(backup_file, public_key):
    encrypted_backup_file = f"{backup_file}.age"
    subprocess.run(
        [
            "age",
            "--recipient",
            public_key,
            "--output",
            encrypted_backup_file,
            backup_file,
        ],
        check=True,
    )
    logging.info(f"Backup file encrypted and saved at: {encrypted_backup_file}")
    os.remove(backup_file)


def backup_all_databases(public_key):
    databases = get_all_databases()
    if not databases:
        print("No databases found to back up.")
        return

    for db in databases:
        print(f"Backing up database: {db}")
        backup_file = backup_database(db)
        encrypt_backup(backup_file, public_key)


def start_schedueled_backup():
    public_key, _ = generate_age_keys()
    iter = croniter(CRON_EXP, datetime.now())

    while True:
        if croniter.match(CRON_EXP, datetime.now()):
            backup_all_databases(public_key)
        sleep_duration = (iter.get_next(datetime) - datetime.now()).total_seconds()
        print(f"sleeping for {sleep_duration}")
        time.sleep(sleep_duration)
