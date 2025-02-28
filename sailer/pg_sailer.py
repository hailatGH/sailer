import os
import time
import logging
import subprocess
from datetime import datetime
from croniter import croniter
import boto3

from sailer import env

def get_next_backup_time(schedule: str, base_time: datetime) -> datetime:
    """
    Returns the next backup time based on the cron schedule.
    """
    cron = croniter(schedule, base_time)
    return cron.get_next(datetime)

def perform_backup() -> str:
    """
    Performs a PostgreSQL backup using pg_dumpall and returns the backup filename.
    """
    logging.info("Starting PostgreSQL backup")
    backup_env = os.environ.copy()
    backup_env["PGPASSWORD"] = env.postgres_password

    backup_filename = datetime.now().strftime("%Y_%m_%d_%H_%M_%S.sql")
    command = [
        "pg_dumpall",
        "-U", env.postgres_user,
        "-h", env.postgres_host,
        "-p", str(env.postgres_port),
        "-f", backup_filename
    ]

    subprocess.run(command, env=backup_env, check=True)
    logging.info(f"Backup successfully created: {backup_filename}")
    return backup_filename

def upload_backup_to_s3(backup_filename: str) -> None:
    """
    Upload the backup file to S3 using boto3.
    """
    logging.info("Uploading backup to S3")
    s3_client = boto3.client(
        "s3",
        endpoint_url=env.aws_endpoint_url,
        aws_access_key_id=env.aws_access_key_id,
        aws_secret_access_key=env.aws_secret_access_key
    )
    s3_client.upload_file(backup_filename, env.aws_bucket_name, backup_filename)
    logging.info("Backup successfully uploaded to S3")

def cleanup_backup_file(backup_filename: str) -> None:
    """
    Remove the backup file from local storage.
    """
    if os.path.exists(backup_filename):
        os.remove(backup_filename)
        logging.info(f"Removed backup file: {backup_filename}")
    else:
        logging.warning(f"Backup file {backup_filename} does not exist")

def run_backup_cycle():
    """
    Runs the backup cycle repeatedly at the scheduled times.
    """
    # Establish the first backup time.
    base_time = datetime.now()
    next_backup = get_next_backup_time(env.backup_cron_schedule, base_time)
    logging.info(f"Initial next backup time: {next_backup}")

    while True:
        current_time = datetime.now()
        if current_time < next_backup:
            sleep_duration = (next_backup - current_time).total_seconds()
            logging.info(f"Sleeping for {sleep_duration:.2f} seconds until next backup")
            time.sleep(sleep_duration)

        backup_filename = None
        try:
            backup_filename = perform_backup()
            upload_backup_to_s3(backup_filename)
        except subprocess.CalledProcessError as e:
            logging.error(f"Backup failed: {e}")
        except Exception as ex:
            logging.error(f"An error occurred: {ex}")
        finally:
            if backup_filename:
                cleanup_backup_file(backup_filename)

        # Calculate the next backup time based on the current time.
        next_backup = get_next_backup_time(env.backup_cron_schedule, datetime.now())
        logging.info(f"Next backup scheduled at: {next_backup}")