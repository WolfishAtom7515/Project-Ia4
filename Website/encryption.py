import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

# AES POWER <3
key = b'1234567890abcdef1234567890abcdef'  # 32-byte key

# Encrypt function (single argument)
def encrypt_message(message):
    # Generate a random IV
    iv = os.urandom(16)
    
    # Pad the message
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message.encode()) + padder.finalize()
    
    # Encrypt using AES
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
    
    # Combine IV and encrypted message, then encode as Base64
    return base64.b64encode(iv + encrypted_message).decode()

# Decrypt function (single argument)
def decrypt_message(encrypted_message):
    # Decode Base64 to get combined IV and encrypted bytes
    encrypted_bytes = base64.b64decode(encrypted_message)
    
    # Split the IV and encrypted message
    iv = encrypted_bytes[:16]
    encrypted_message = encrypted_bytes[16:]
    
    # Decrypt using AES
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
    
    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    original_message = unpadder.update(padded_message) + unpadder.finalize()
    
    return original_message.decode()

