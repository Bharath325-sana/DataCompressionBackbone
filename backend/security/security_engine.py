import os
import hashlib
from cryptography.fernet import Fernet


# --------------------------------------------------
# ENCRYPTION KEY
# --------------------------------------------------

KEY_FILE = "security.key"


def get_encryption_key():
    """
    Creates an encryption key the first time the
    application runs and reuses it afterwards.
    """

    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as file:
            return file.read()

    key = Fernet.generate_key()

    with open(KEY_FILE, "wb") as file:
        file.write(key)

    return key


# --------------------------------------------------
# ENCRYPT DATA
# --------------------------------------------------

def encrypt_data(data):
    key = get_encryption_key()

    cipher = Fernet(key)

    encrypted_data = cipher.encrypt(data)

    return encrypted_data


# --------------------------------------------------
# DECRYPT DATA
# --------------------------------------------------

def decrypt_data(encrypted_data):
    key = get_encryption_key()

    cipher = Fernet(key)

    decrypted_data = cipher.decrypt(encrypted_data)

    return decrypted_data


# --------------------------------------------------
# SHA-256 HASH
# --------------------------------------------------

def calculate_sha256(data):
    return hashlib.sha256(data).hexdigest()