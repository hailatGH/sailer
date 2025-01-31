import logging
import logging.config
import os
import yaml
from pathlib import Path


def setup_logging(
    config_path: str = None,
    default_level: int = logging.INFO,
    env_key: str = "SAILER_LOG_CFG",
):
    """Setup logging configuration"""
    path = config_path or os.path.join(Path(__file__).parent.parent, "logging.yaml")
    value = os.getenv(env_key, None)
    if value:
        path = value

    if os.path.exists(path):
        with open(path, "rt") as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(f"Error loading logging config: {e}. Using default config")
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        print(f"Warning: logging config file not found at {path}. Using default config")
