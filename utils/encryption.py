"""Encryption utilities"""
from cryptography.fernet import Fernet
import base64


def encrypt_data(data: bytes, key: bytes) -> str:
    """Encrypt data using Fernet"""
    cipher = Fernet(key)
    encrypted = cipher.encrypt(data)
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str, key: bytes) -> bytes:
    """Decrypt data using Fernet"""
    cipher = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
    return cipher.decrypt(encrypted_bytes)


