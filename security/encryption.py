import os
from cryptography.fernet import Fernet
from core.paths import project_root

DATA_DIR = os.path.join(project_root(), "data")
KEY_FILE = os.path.join(DATA_DIR, "secret.key")

def generate_key():
    """Generate a secret key for encryption and save it to a file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    """Load the secret key from the file. Generate if missing."""
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt_data(data: str) -> bytes:
    """Encrypt the given data using the secret key."""
    key = load_key()
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypt the given data using the secret key."""
    key = load_key()
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()
