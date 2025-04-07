"""
AES encryption and decryption functions.

This module provides functions for AES encryption and decryption,
which is used in Bitcoin wallet encryption.
"""

import hashlib
import os
from typing import Optional

# Try to import PyCryptodome (preferred) or PyCrypto
try:
    from Crypto.Cipher import AES
    CRYPTO_AVAILABLE = True
    USING_CRYPTOGRAPHY = False
except ImportError:
    try:
        # Fallback to cryptography library
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        CRYPTO_AVAILABLE = True
        USING_CRYPTOGRAPHY = True
    except ImportError:
        CRYPTO_AVAILABLE = False
        USING_CRYPTOGRAPHY = False
        # Define AES for type checking
        class AES:
            MODE_CBC = 2
            @staticmethod
            def new(key, mode, iv):
                raise ImportError("No crypto library available")

def derive_key(password: bytes, salt: bytes, iterations: int, key_length: int) -> bytes:
    """
    Derive a key from a password using PBKDF2-HMAC-SHA512.

    Args:
        password: Password bytes
        salt: Salt bytes
        iterations: Number of iterations
        key_length: Length of the derived key in bytes

    Returns:
        Derived key
    """
    return hashlib.pbkdf2_hmac('sha512', password, salt, iterations, key_length)

def encrypt_aes(data: bytes, key: bytes, iv: Optional[bytes] = None) -> bytes:
    """
    Encrypt data using AES-256-CBC.

    Args:
        data: Data to encrypt
        key: Encryption key (32 bytes for AES-256)
        iv: Initialization vector (16 bytes, random if not provided)

    Returns:
        Encrypted data with IV prepended

    Raises:
        ImportError: If neither PyCryptodome nor cryptography is available
        ValueError: If key length is invalid
    """
    if not CRYPTO_AVAILABLE:
        raise ImportError("Either PyCryptodome or cryptography is required for AES encryption")

    if len(key) != 32:
        raise ValueError("AES-256 requires a 32-byte key")

    # Generate random IV if not provided
    if iv is None:
        try:
            from Crypto.Random import get_random_bytes
            iv = get_random_bytes(16)
        except ImportError:
            # Fallback to os.urandom
            iv = os.urandom(16)
    elif len(iv) != 16:
        raise ValueError("AES-CBC requires a 16-byte IV")

    # Pad data to 16-byte blocks (PKCS#7)
    pad_length = 16 - (len(data) % 16)
    padded_data = data + bytes([pad_length]) * pad_length

    # Encrypt data
    try:
        # Try using PyCryptodome/PyCrypto
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(padded_data)
    except NameError:
        # Fallback to cryptography
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Return IV + encrypted data
    return iv + encrypted_data

def decrypt_aes(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Decrypt data using AES-256-CBC.

    Args:
        encrypted_data: Encrypted data with IV prepended
        key: Decryption key (32 bytes for AES-256)

    Returns:
        Decrypted data

    Raises:
        ImportError: If neither PyCryptodome nor cryptography is available
        ValueError: If key length or encrypted data is invalid
    """
    if not CRYPTO_AVAILABLE:
        raise ImportError("Either PyCryptodome or cryptography is required for AES decryption")

    if len(key) != 32:
        raise ValueError("AES-256 requires a 32-byte key")

    if len(encrypted_data) < 16:
        raise ValueError("Encrypted data is too short")

    # Extract IV and encrypted data
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]

    # Decrypt data
    try:
        # Try using PyCryptodome/PyCrypto
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data)
    except NameError:
        # Fallback to cryptography
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove padding (PKCS#7)
    pad_length = decrypted_data[-1]
    if pad_length > 16:
        raise ValueError("Invalid padding")

    return decrypted_data[:-pad_length]


def decrypt_wallet_key(encrypted_key: bytes, derived_key: bytes) -> bytes:
    """
    Decrypt a Bitcoin wallet key.

    Args:
        encrypted_key: Encrypted key from wallet
        derived_key: Key derived from passphrase

    Returns:
        Decrypted key
    """
    # Bitcoin wallet uses AES-256-CBC
    return decrypt_aes(encrypted_key, derived_key)
