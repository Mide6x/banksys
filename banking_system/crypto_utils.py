#ai generated, please confirm it's accurate
#ai generated, please confirm it's accurate
#ai generated, please confirm it's accurate

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import os

class CryptoManager:
    def __init__(self):
        self.symmetric_key = None
        self.private_key = None
        self.public_key = None
        
    def generate_symmetric_key(self):
        """Generate a new Fernet symmetric key"""
        self.symmetric_key = Fernet.generate_key()
        return self.symmetric_key
    
    def generate_asymmetric_keys(self):
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.private_key = private_key
        self.public_key = private_key.public_key()
        return self.private_key, self.public_key
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt data using symmetric encryption"""
        if not self.symmetric_key:
            self.generate_symmetric_key()
        f = Fernet(self.symmetric_key)
        return f.encrypt(data.encode())
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data using symmetric encryption"""
        if not self.symmetric_key:
            raise ValueError("No symmetric key available")
        f = Fernet(self.symmetric_key)
        return f.decrypt(encrypted_data).decode()
    
    def hash_password(self, password: str, salt: bytes = None) -> tuple:
        """Hash password using PBKDF2"""
        if not salt:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.b64encode(kdf.derive(password.encode()))
        return key, salt 