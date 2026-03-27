from cryptography.fernet import Fernet
import base64
import hashlib
import os

class CryptoManager:
    def __init__(self, key=None):
        if key is None:
            self.key = Fernet.generate_key()
        elif isinstance(key, str):
            # Derive a 32-byte key from the string using SHA256
            hash_obj = hashlib.sha256(key.encode())
            self.key = base64.urlsafe_b64encode(hash_obj.digest())
        else:
            self.key = key
        self.cipher = Fernet(self.key)

    def get_key(self):
        return self.key.decode()

    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)

    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data)

    def decrypt_str(self, encrypted_data):
        return self.decrypt(encrypted_data).decode()
