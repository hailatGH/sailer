import logging
from pgsailer.backup import BackupScheduler

def start_scheduled_backup():
    logging.info("Starting scheduled backup...")
    scheduler = BackupScheduler()
    scheduler.start()