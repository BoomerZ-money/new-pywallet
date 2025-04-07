"""
Recovery functions for PyWallet.

This module provides functions for recovering Bitcoin wallet keys.
"""

import os
import re
import time
import struct
import hashlib
import binascii
from typing import Dict, List, Any, Optional, Tuple, BinaryIO

from pywallet_refactored.logger import logger
from pywallet_refactored.utils.common import bytes_to_hex, hex_to_bytes, read_part_file
from pywallet_refactored.crypto.keys import public_key_to_address, private_key_to_wif

class RecoveryError(Exception):
    """Exception raised for recovery errors."""
    pass

class RecoveredKey:
    """Class for recovered keys."""
    
    def __init__(self, private_key: bytes, public_key: bytes, compressed: bool = False):
        """
        Initialize a recovered key.
        
        Args:
            private_key: Private key bytes
            public_key: Public key bytes
            compressed: Whether the key is compressed
        """
        self.private_key = private_key
        self.public_key = public_key
        self.compressed = compressed
        self._address = None
        self._wif = None
    
    @property
    def address(self) -> str:
        """Get the Bitcoin address for this key."""
        if self._address is None:
            self._address = public_key_to_address(self.public_key)
        return self._address
    
    @property
    def wif(self) -> str:
        """Get the WIF encoded private key."""
        if self._wif is None:
            self._wif = private_key_to_wif(self.private_key, self.compressed)
        return self._wif
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'private_key': bytes_to_hex(self.private_key),
            'public_key': bytes_to_hex(self.public_key),
            'address': self.address,
            'wif': self.wif,
            'compressed': self.compressed
        }

class RecoveredEncryptedKey:
    """Class for recovered encrypted keys."""
    
    def __init__(self, encrypted_private_key: bytes, public_key: bytes, compressed: bool = False):
        """
        Initialize a recovered encrypted key.
        
        Args:
            encrypted_private_key: Encrypted private key bytes
            public_key: Public key bytes
            compressed: Whether the key is compressed
        """
        self.encrypted_private_key = encrypted_private_key
        self.public_key = public_key
        self.compressed = compressed
        self._address = None
    
    @property
    def address(self) -> str:
        """Get the Bitcoin address for this key."""
        if self._address is None:
            self._address = public_key_to_address(self.public_key)
        return self._address
    
    def decrypt(self, master_key: bytes) -> RecoveredKey:
        """
        Decrypt the private key using the master key.
        
        Args:
            master_key: Master key bytes
            
        Returns:
            RecoveredKey instance
        """
        from pywallet_refactored.crypto.aes import decrypt_aes
        
        # Decrypt private key
        private_key = decrypt_aes(self.encrypted_private_key, master_key)
        
        # Create recovered key
        return RecoveredKey(private_key, self.public_key, self.compressed)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'encrypted_private_key': bytes_to_hex(self.encrypted_private_key),
            'public_key': bytes_to_hex(self.public_key),
            'address': self.address,
            'compressed': self.compressed
        }

class RecoveredMasterKey:
    """Class for recovered master keys."""
    
    def __init__(self, encrypted_key: bytes, salt: bytes, iterations: int, method: int):
        """
        Initialize a recovered master key.
        
        Args:
            encrypted_key: Encrypted master key bytes
            salt: Salt bytes
            iterations: Number of iterations
            method: Encryption method
        """
        self.encrypted_key = encrypted_key
        self.salt = salt
        self.iterations = iterations
        self.method = method
    
    def decrypt(self, passphrase: str) -> bytes:
        """
        Decrypt the master key using the passphrase.
        
        Args:
            passphrase: Wallet passphrase
            
        Returns:
            Decrypted master key bytes
        """
        from pywallet_refactored.crypto.aes import derive_key, decrypt_aes
        
        # Derive key from passphrase
        derived_key = derive_key(
            passphrase.encode('utf-8'),
            self.salt,
            self.iterations,
            32  # AES-256 key size
        )
        
        # Decrypt master key
        return decrypt_aes(self.encrypted_key, derived_key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'encrypted_key': bytes_to_hex(self.encrypted_key),
            'salt': bytes_to_hex(self.salt),
            'iterations': self.iterations,
            'method': self.method
        }

def scan_file(file_path: str, start_offset: int = 0, max_size: Optional[int] = None) -> Dict[str, List[Any]]:
    """
    Scan a file for Bitcoin keys.
    
    Args:
        file_path: Path to file to scan
        start_offset: Offset to start scanning from
        max_size: Maximum number of bytes to scan
        
    Returns:
        Dictionary with recovered keys
    """
    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        
        if max_size is None:
            max_size = file_size - start_offset
        
        # Open file
        fd = os.open(file_path, os.O_RDONLY)
        
        # Patterns to search for
        patterns = [
            # Private key pattern (unencrypted)
            re.compile(b'\\x04\\x01\\x01\\x04[\\x00-\\xff]{72}', re.DOTALL),
            # Master key pattern
            re.compile(b'\\x04mkey[\\x00-\\xff]{84}', re.DOTALL),
            # Encrypted key pattern
            re.compile(b'\\x04ckey[\\x00-\\xff]{140}', re.DOTALL)
        ]
        
        # Results
        results = {
            'keys': [],
            'encrypted_keys': [],
            'master_keys': []
        }
        
        # Scan file
        offset = start_offset
        buffer_size = 1024 * 1024  # 1 MB
        
        while offset < start_offset + max_size:
            # Read buffer
            size = min(buffer_size, start_offset + max_size - offset)
            buffer = read_part_file(fd, offset, size)
            
            if not buffer:
                break
            
            # Search for patterns
            for pattern in patterns:
                for match in pattern.finditer(buffer):
                    data = match.group(0)
                    
                    if data.startswith(b'\\x04\\x01\\x01\\x04'):
                        # Private key
                        private_key = data[4:36]
                        public_key = data[36:101]
                        compressed = public_key[0] != 4
                        
                        key = RecoveredKey(private_key, public_key, compressed)
                        results['keys'].append(key)
                        
                        logger.debug(f"Found key at offset {offset + match.start()}: {key.address}")
                    
                    elif data.startswith(b'\\x04mkey'):
                        # Master key
                        encrypted_key = data[4:68]
                        salt = data[68:76]
                        iterations = struct.unpack("<I", data[76:80])[0]
                        method = struct.unpack("<I", data[80:84])[0]
                        
                        master_key = RecoveredMasterKey(encrypted_key, salt, iterations, method)
                        results['master_keys'].append(master_key)
                        
                        logger.debug(f"Found master key at offset {offset + match.start()}: iterations={iterations}, method={method}")
                    
                    elif data.startswith(b'\\x04ckey'):
                        # Encrypted key
                        public_key = data[5:70]
                        encrypted_private_key = data[70:]
                        compressed = public_key[0] != 4
                        
                        encrypted_key = RecoveredEncryptedKey(encrypted_private_key, public_key, compressed)
                        results['encrypted_keys'].append(encrypted_key)
                        
                        logger.debug(f"Found encrypted key at offset {offset + match.start()}: {encrypted_key.address}")
            
            # Move to next buffer
            offset += size
        
        # Close file
        os.close(fd)
        
        return results
    except Exception as e:
        raise RecoveryError(f"Failed to scan file: {e}")

def scan_device(device_path: str, start_offset: int = 0, max_size: Optional[int] = None) -> Dict[str, List[Any]]:
    """
    Scan a device for Bitcoin keys.
    
    Args:
        device_path: Path to device to scan
        start_offset: Offset to start scanning from
        max_size: Maximum number of bytes to scan
        
    Returns:
        Dictionary with recovered keys
    """
    try:
        # Open device
        fd = os.open(device_path, os.O_RDONLY)
        
        # Get device size
        try:
            import fcntl
            import array
            
            # BLKGETSIZE64 ioctl to get device size
            buf = array.array('L', [0])
            fcntl.ioctl(fd, 0x80081272, buf)  # BLKGETSIZE64
            device_size = buf[0]
        except (ImportError, IOError):
            # Fallback: try to read until EOF
            os.lseek(fd, 0, os.SEEK_END)
            device_size = os.lseek(fd, 0, os.SEEK_CUR)
        
        if max_size is None:
            max_size = device_size - start_offset
        
        # Close device
        os.close(fd)
        
        # Use scan_file function
        return scan_file(device_path, start_offset, max_size)
    except Exception as e:
        raise RecoveryError(f"Failed to scan device: {e}")

def recover_keys_from_passphrase(encrypted_keys: List[RecoveredEncryptedKey], 
                                master_key: RecoveredMasterKey, 
                                passphrase: str) -> List[RecoveredKey]:
    """
    Recover keys from encrypted keys using a passphrase.
    
    Args:
        encrypted_keys: List of encrypted keys
        master_key: Master key
        passphrase: Wallet passphrase
        
    Returns:
        List of recovered keys
    """
    try:
        # Decrypt master key
        decrypted_master_key = master_key.decrypt(passphrase)
        
        # Decrypt each encrypted key
        recovered_keys = []
        
        for encrypted_key in encrypted_keys:
            try:
                key = encrypted_key.decrypt(decrypted_master_key)
                recovered_keys.append(key)
                
                logger.debug(f"Recovered key: {key.address}")
            except Exception as e:
                logger.error(f"Failed to decrypt key {encrypted_key.address}: {e}")
        
        return recovered_keys
    except Exception as e:
        raise RecoveryError(f"Failed to recover keys: {e}")

def dump_keys_to_file(keys: List[RecoveredKey], output_file: str) -> None:
    """
    Dump recovered keys to a file.
    
    Args:
        keys: List of recovered keys
        output_file: Path to output file
    """
    try:
        # Convert keys to dictionaries
        key_dicts = [key.to_dict() for key in keys]
        
        # Write to file
        with open(output_file, 'w') as f:
            import json
            json.dump(key_dicts, f, indent=4)
        
        logger.info(f"Dumped {len(keys)} keys to {output_file}")
    except Exception as e:
        raise RecoveryError(f"Failed to dump keys: {e}")

def dump_encrypted_keys_to_file(encrypted_keys: List[RecoveredEncryptedKey], 
                               master_key: RecoveredMasterKey, 
                               output_file: str) -> None:
    """
    Dump encrypted keys to a file.
    
    Args:
        encrypted_keys: List of encrypted keys
        master_key: Master key
        output_file: Path to output file
    """
    try:
        # Convert keys to dictionaries
        key_dicts = [key.to_dict() for key in encrypted_keys]
        
        # Add master key
        data = {
            'master_key': master_key.to_dict(),
            'encrypted_keys': key_dicts
        }
        
        # Write to file
        with open(output_file, 'w') as f:
            import json
            json.dump(data, f, indent=4)
        
        logger.info(f"Dumped {len(encrypted_keys)} encrypted keys to {output_file}")
    except Exception as e:
        raise RecoveryError(f"Failed to dump encrypted keys: {e}")
