import os
import time
import boto3
import logging
import subprocess
from croniter import croniter
from datetime import datetime

from sailer import env

def pg_backup():
    base = datetime.now()
    logging.info(f"Base time: {base}")

    cron = croniter(env.backup_cron_schedule, base)
    next_time = cron.get_next(datetime)
    logging.info(f"Next backup time: {next_time}")

    while True:
        logging.info("Backup started")
        
        backup_env = os.environ.copy()
        backup_env["PGPASSWORD"] = env.postgres_password
        backup_file = datetime.now().strftime("%Y_%m_%d_%H_%M_%S.sql")
        subprocess.run(
            [
            "pg_dumpall",
            "-U", env.postgres_user,
            "-h", env.postgres_host,
            "-p", str(env.postgres_port),
            "-f", backup_file
            ],
            env=backup_env
        )

        # Upload to s3 using boto3
        logging.info("Uploading to s3")
        s3_client = boto3.client(
            "s3",
            endpoint_url=env.aws_endpoint_url,
            aws_access_key_id=env.aws_access_key_id,
            aws_secret_access_key=env.aws_secret_access_key
        )
        s3_client.upload_file(backup_file, env.aws_bucket_name, backup_file)

        # Remove the backup file
        logging.info("Removing backup file")
        os.remove(backup_file)

        logging.info("Backup finished")

        next_time = cron.get_next(datetime)
        logging.info(f"Next backup time: {next_time}")
        
        seconds = (next_time - datetime.now()).total_seconds()
        logging.info(f"Sleeping for {seconds} seconds")
        time.sleep(seconds)