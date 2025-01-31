import os
import time
import logging
import psycopg2
import subprocess
from croniter import croniter
from datetime import datetime

from tools.age_key_generator import AgeKeyGenerator


class PostgresBackup:
    def __init__(self):
        self.db_config = {
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT"),
        }
        self.backup_dir = "/app/backups/"
        self.age_dir = "/app/age/"
        self.key_path = os.path.join(self.age_dir, "key.txt")
        logging.info("PostgresBackup initialized.")

    def _run_command(self, command, env=None):
        try:
            subprocess.run(command, env=env, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {e}")
            return None
        return True

    def _get_formatted_datetime(self):
        return datetime.now().strftime("%Y/%b/%d/%H/%M")

    def get_all_databases(self):
        try:
            with psycopg2.connect(dbname="postgres", **self.db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT datname FROM pg_database WHERE datistemplate = false;"
                    )
                    databases = [row[0] for row in cursor.fetchall()]
                    logging.info(f"Found databases: {databases}")
                    return databases
        except Exception as e:
            logging.error(f"Error fetching databases: {e}")
            return []

    def backup_database(self, db_name):
        backup_path = os.path.join(self.backup_dir, self._get_formatted_datetime())
        os.makedirs(backup_path, exist_ok=True)
        backup_file = os.path.join(backup_path, f"{db_name}_backup.sql")

        env = os.environ.copy()
        env["PGPASSWORD"] = self.db_config["password"]

        command = [
            "pg_dump",
            "-h",
            self.db_config["host"],
            "-p",
            self.db_config["port"],
            "-U",
            self.db_config["user"],
            "-d",
            db_name,
            "-f",
            backup_file,
        ]

        if self._run_command(command, env):
            logging.info(f"Backup successful for {db_name}: {backup_file}")
            return backup_file
        return None

    def encrypt_backup(self, backup_file, public_key):
        encrypted_file = f"{backup_file}.age"
        if self._run_command(
            ["age", "--recipient", public_key, "--output", encrypted_file, backup_file]
        ):
            logging.info(f"Encrypted backup saved at: {encrypted_file}")
            os.remove(backup_file)

    def backup_all(self, public_key):
        databases = self.get_all_databases()
        if not databases:
            logging.warning("No databases found to back up.")
            return

        for db in databases:
            logging.info(f"Backing up database: {db}")
            backup_file = self.backup_database(db)
            if backup_file:
                self.encrypt_backup(backup_file, public_key)


class BackupScheduler:
    def __init__(self):
        self.cron_exp = os.getenv("BACKUP_SCHEDULE", "0 0 * * *")
        self.age_key_generator = AgeKeyGenerator()
        self.backup_manager = PostgresBackup()
        logging.info("BackupScheduler initialized.")

    def start(self):
        public_key = self.age_key_generator.public_key
        cron_iter = croniter(self.cron_exp, datetime.now())

        while True:
            if croniter.match(self.cron_exp, datetime.now()):
                self.backup_manager.backup_all(public_key)

            sleep_duration = (
                cron_iter.get_next(datetime) - datetime.now()
            ).total_seconds()
            logging.info(f"Sleeping for {sleep_duration} seconds")
            time.sleep(sleep_duration)
