import os
import logging
import subprocess


class AgeKeyGenerator:
    def __init__(self, age_dir="/app/age/", key_path="/app/age/key.txt"):
        self.age_dir = age_dir
        self.key_path = key_path
        self.public_key = None
        self.private_key = None
        self._load_or_generate_keys()

    def _run_command(self, command):
        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {e}")
            return False

    def _load_or_generate_keys(self):
        os.makedirs(self.age_dir, exist_ok=True)

        if os.path.exists(self.key_path):
            logging.info("Using existing age keys.")
            with open(self.key_path, "r") as f:
                lines = f.read().strip().splitlines()

            self.public_key = next(
                (
                    line.split(": ")[1].strip()
                    for line in lines
                    if line.startswith("# public key:")
                ),
                None,
            )
            self.private_key = next(
                (line.strip() for line in lines if line.startswith("AGE-SECRET-KEY-")),
                None,
            )

            if not self.public_key or not self.private_key:
                raise RuntimeError("Failed to extract the keys correctly.")
        else:
            if self._run_command(["age-keygen", "-o", self.key_path]):
                logging.info("Generated new age keys.")
                with open(self.key_path, "r") as f:
                    lines = f.read().strip().splitlines()

                self.public_key = next(
                    (
                        line.split(": ")[1].strip()
                        for line in lines
                        if line.startswith("# public key:")
                    ),
                    None,
                )
                self.private_key = next(
                    (
                        line.strip()
                        for line in lines
                        if line.startswith("AGE-SECRET-KEY-")
                    ),
                    None,
                )

                if not self.public_key or not self.private_key:
                    raise RuntimeError("Failed to generate keys correctly.")
