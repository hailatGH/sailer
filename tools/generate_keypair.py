import os
import subprocess

AGE_DIR = "/app/age/"
KEY_PATH = os.path.join(AGE_DIR, "key.txt")

def generate_age_keys():
    try:
        os.makedirs(AGE_DIR, exist_ok=True)

        if os.path.exists(KEY_PATH):
            print("✅ Key already exists. Reading from file...")

            with open(KEY_PATH, "r") as f:
                private_key = f.read().strip()

            public_key = None
            for line in private_key.splitlines():
                if line.startswith("# public key:"):
                    public_key = line.split("# public key: ")[1].strip()
                    break

            if not public_key:
                raise RuntimeError("Failed to extract the public key from existing key file.")

            print("\n🔑 **Existing Keys:**")
            print(f"📜 **Private Key (Saved at {KEY_PATH}):**\n{private_key}\n")
            print(f"🔓 **Public Key:** {public_key}")
            return public_key, private_key

        print("🔄 No key found. Generating a new one...")

        result = subprocess.run(
            ["age-keygen", "-o", KEY_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        public_key = None
        for line in result.stderr.splitlines():
            if line.startswith("Public key:"):
                public_key = line.split("Public key: ")[1].strip()
                break
            
        with open(KEY_PATH, "r") as f:
            private_key = f.read().strip()

        if not public_key:
            raise RuntimeError("Failed to extract the public key from age-keygen output.")

        print("\n🔑 **Generated New Keys:**")
        print(f"📜 **Private Key (Saved at {KEY_PATH}):**\n{private_key}\n")
        print(f"🔓 **Public Key:** {public_key}")

        return public_key, private_key

    except FileNotFoundError:
        raise FileNotFoundError("The `age-keygen` command is not installed. Please install 'age'.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running age-keygen: {e.stderr.strip()}")