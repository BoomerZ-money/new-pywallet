"""
Base58 encoding and decoding functions.

This module provides functions for Base58 encoding and decoding,
which is commonly used in Bitcoin for encoding addresses and private keys.
"""

import hashlib
from typing import Union, Optional

# Base58 alphabet
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def b58encode(data: bytes) -> str:
    """
    Encode bytes using Base58.
    
    Args:
        data: Bytes to encode
        
    Returns:
        Base58 encoded string
    """
    # Convert bytes to integer
    n = int.from_bytes(data, byteorder='big')
    
    # Convert to base58 string
    result = ''
    while n > 0:
        n, remainder = divmod(n, 58)
        result = BASE58_ALPHABET[remainder] + result
    
    # Add '1' characters for leading zero bytes
    for byte in data:
        if byte != 0:
            break
        result = '1' + result
    
    return result

def b58decode(encoded: str) -> bytes:
    """
    Decode a Base58 encoded string to bytes.
    
    Args:
        encoded: Base58 encoded string
        
    Returns:
        Decoded bytes
    """
    # Convert base58 string to integer
    n = 0
    for char in encoded:
        n = n * 58 + BASE58_ALPHABET.index(char)
    
    # Convert to bytes
    result = n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')
    
    # Add leading zero bytes
    pad_count = 0
    for char in encoded:
        if char != '1':
            break
        pad_count += 1
    
    return b'\x00' * pad_count + result

def b58encode_check(data: bytes) -> str:
    """
    Encode bytes using Base58 with a 4-byte checksum.
    
    Args:
        data: Bytes to encode
        
    Returns:
        Base58Check encoded string
    """
    # Add 4-byte hash check to the end
    checksum = hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]
    return b58encode(data + checksum)

def b58decode_check(encoded: str) -> Optional[bytes]:
    """
    Decode a Base58Check encoded string to bytes.
    
    Args:
        encoded: Base58Check encoded string
        
    Returns:
        Decoded bytes without checksum, or None if checksum is invalid
    """
    decoded = b58decode(encoded)
    
    # Verify the checksum
    if len(decoded) < 4:
        return None
    
    data, checksum = decoded[:-4], decoded[-4:]
    calculated_checksum = hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]
    
    if checksum != calculated_checksum:
        return None
    
    return data
