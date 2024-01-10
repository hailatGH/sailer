import os
import subprocess
AGE_DIR = "/app/age/"

def generate_age_keys():
    try:
        os.makedirs(AGE_DIR, exist_ok=True)
        result = subprocess.run(
            ["age-keygen", "-o", f"{AGE_DIR}/key.txt"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        for line in result.stderr.splitlines():
            if line.startswith("Public key:"):
                public_key = line.split("Public key: ")[1].strip()
                print(f"Public key: {public_key}")
                return public_key

        raise RuntimeError("Failed to extract the public key from the output.")

    except FileNotFoundError:
        raise FileNotFoundError("The `age-keygen` command is not installed. Please install the 'age' tool.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running age-keygen: {e.stderr.strip()}")
