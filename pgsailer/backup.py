import os
import time
import logging
import datetime
import psycopg2
import subprocess
from croniter import croniter
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PostgresBackup:
    def __init__(self):
        self.db_user = os.getenv("POSTGRES_USER")
        self.db_password = os.getenv("POSTGRES_PASSWORD")
        self.db_host = os.getenv("POSTGRES_HOST")
        self.db_port = os.getenv("POSTGRES_PORT")
        self.backup_dir = "/app/backups/"
        self.age_dir = "/app/age/"
        self.key_path = os.path.join(self.age_dir, "key.txt")
        logging.info("PostgresBackup initialized.")
        
    def _get_formatted_datetime(self):
        now = datetime.now()
        return now.strftime("%Y/%b/%d/%H/%M")

    def get_all_databases(self):
        try:
            with psycopg2.connect(dbname="postgres", user=self.db_user, password=self.db_password, host=self.db_host, port=self.db_port) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                    databases = [row[0] for row in cursor.fetchall()]
                    logging.info(f"Found databases: {databases}")
                    return databases
        except Exception as e:
            logging.error(f"Error fetching databases: {e}")
            return []
    
    def backup_database(self, db_name):
        try:
            backup_path = os.path.join(self.backup_dir, self._get_formatted_datetime())
            os.makedirs(backup_path, exist_ok=True)
            backup_file = os.path.join(backup_path, f"{db_name}_backup.sql")
            
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_password
            
            subprocess.run([
                "pg_dump", "-h", self.db_host, "-p", self.db_port, "-U", self.db_user,
                "-d", db_name, "-f", backup_file
            ], env=env, check=True)
            
            logging.info(f"Backup successful for {db_name}: {backup_file}")
            return backup_file
        except subprocess.CalledProcessError as e:
            logging.error(f"Backup failed for {db_name}: {e}")
            return None
    
    def encrypt_backup(self, backup_file, public_key):
        try:
            encrypted_file = f"{backup_file}.age"
            subprocess.run(["age", "--recipient", public_key, "--output", encrypted_file, backup_file], check=True)
            logging.info(f"Encrypted backup saved at: {encrypted_file}")
            os.remove(backup_file)
        except subprocess.CalledProcessError as e:
            logging.error(f"Encryption failed for {backup_file}: {e}")
    
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

    def generate_age_keys(self):
        try:
            os.makedirs(self.age_dir, exist_ok=True)
            if os.path.exists(self.key_path):
                with open(self.key_path, "r") as f:
                    private_key = f.read().strip()
                for line in private_key.splitlines():
                    if line.startswith("# public key:"):
                        logging.info("Using existing age keys.")
                        return line.split("# public key: ")[1].strip(), private_key
                raise RuntimeError("Failed to extract public key.")
            
            subprocess.run(["age-keygen", "-o", self.key_path], check=True)
            with open(self.key_path, "r") as f:
                private_key = f.read().strip()
            for line in private_key.splitlines():
                if line.startswith("# public key:"):
                    logging.info("Generated new age keys.")
                    return line.split("# public key: ")[1].strip(), private_key
            
            raise RuntimeError("Failed to generate public key.")
        except Exception as e:
            logging.error(f"Error generating age keys: {e}")
            raise


class BackupScheduler:
    def __init__(self):
        self.cron_exp = os.getenv("BACKUP_SCHEDULE", "0 0 * * *")
        self.backup_manager = PostgresBackup()
        logging.info("BackupScheduler initialized.")

    def start(self):
        public_key, _ = self.backup_manager.generate_age_keys()
        iter = croniter(self.cron_exp, datetime.now())
        while True:
            if croniter.match(self.cron_exp, datetime.now()):
                self.backup_manager.backup_all(public_key)
            sleep_duration = (iter.get_next(datetime) - datetime.now()).total_seconds()
            logging.info(f"Sleeping for {sleep_duration} seconds")
            time.sleep(sleep_duration)