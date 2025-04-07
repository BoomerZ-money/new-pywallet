"""
Common utility functions for PyWallet.
"""

import os
import sys
import platform
import hashlib
import binascii
from typing import List, Union, Any, Optional

def plural(count: int) -> str:
    """
    Return 's' if count is not 1, otherwise return empty string.
    
    Args:
        count: The count to check
        
    Returns:
        's' if count is not 1, otherwise ''
    """
    return '' if count == 1 else 's'

def systype() -> str:
    """
    Return the system type: 'Mac', 'Win', or 'Linux'.
    
    Returns:
        System type string
    """
    if platform.system() == "Darwin":
        return 'Mac'
    elif platform.system() == "Windows":
        return 'Win'
    return 'Linux'

def md5_hash(data: Union[str, bytes]) -> str:
    """
    Calculate MD5 hash of data.
    
    Args:
        data: Data to hash (string or bytes)
        
    Returns:
        MD5 hash as hexadecimal string
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.md5(data).hexdigest()

def sha256_hash(data: Union[str, bytes]) -> str:
    """
    Calculate SHA256 hash of data.
    
    Args:
        data: Data to hash (string or bytes)
        
    Returns:
        SHA256 hash as hexadecimal string
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def str_to_bytes(text: Any) -> bytes:
    """
    Convert string to bytes.
    
    Args:
        text: Text to convert
        
    Returns:
        Bytes representation
    """
    if isinstance(text, bytes):
        return text
    if isinstance(text, str):
        return text.encode('utf-8')
    return str(text).encode('utf-8')

def bytes_to_str(data: bytes) -> str:
    """
    Convert bytes to string.
    
    Args:
        data: Bytes to convert
        
    Returns:
        String representation
    """
    if isinstance(data, str):
        return data
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('latin1')

def hex_to_bytes(hex_string: str) -> bytes:
    """
    Convert hexadecimal string to bytes.
    
    Args:
        hex_string: Hexadecimal string
        
    Returns:
        Bytes representation
    """
    return binascii.unhexlify(hex_string)

def bytes_to_hex(data: bytes) -> str:
    """
    Convert bytes to hexadecimal string.
    
    Args:
        data: Bytes to convert
        
    Returns:
        Hexadecimal string
    """
    return binascii.hexlify(data).decode('ascii')

def read_part_file(fd: int, offset: int, length: int) -> bytes:
    """
    Read a part of a file, making sure to read in 512-byte blocks for Windows compatibility.
    
    Args:
        fd: File descriptor
        offset: Offset to start reading from
        length: Number of bytes to read
        
    Returns:
        Bytes read from file
    """
    rest = offset % 512
    new_offset = offset - rest
    big_length = 512 * (int((length + rest - 1) // 512) + 1)
    os.lseek(fd, new_offset, os.SEEK_SET)
    d = os.read(fd, big_length)
    return d[rest:rest + length]

def multi_extract(data: bytes, lengths: List[int]) -> List[bytes]:
    """
    Extract multiple parts from bytes based on a list of lengths.
    
    Args:
        data: Bytes to extract from
        lengths: List of lengths to extract
        
    Returns:
        List of extracted parts
    """
    result = []
    cursor = 0
    for length in lengths:
        result.append(data[cursor:cursor + length])
        cursor += length
    if cursor < len(data):
        result.append(data[cursor:])
    return result
