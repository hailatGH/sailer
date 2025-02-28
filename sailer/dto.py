from dataclasses import dataclass

@dataclass
class ENV:
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_bucket_name: str
    aws_endpoint_url: str
    backup_cron_schedule: str
    backup_retention_days: int