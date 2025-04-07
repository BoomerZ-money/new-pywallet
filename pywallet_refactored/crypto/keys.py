"""
Bitcoin key handling functions.

This module provides functions for handling Bitcoin keys, including
private keys, public keys, and addresses.
"""

import hashlib
import binascii
from typing import Tuple, Dict, Any, Optional, Union

try:
    import ecdsa
except ImportError:
    ecdsa = None

from pywallet_refactored.crypto.base58 import b58encode, b58decode, b58encode_check, b58decode_check
from pywallet_refactored.utils.common import bytes_to_hex, hex_to_bytes
from pywallet_refactored.config import config

class KeyError(Exception):
    """Exception raised for key-related errors."""
    pass

def hash160(data: bytes) -> bytes:
    """
    Perform RIPEMD-160(SHA-256(data)).
    
    Args:
        data: Data to hash
        
    Returns:
        RIPEMD-160 of SHA-256 hash
    """
    sha256_hash = hashlib.sha256(data).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    return ripemd160.digest()

def public_key_to_address(public_key: bytes, network: Optional[Dict[str, Any]] = None) -> str:
    """
    Convert a public key to a Bitcoin address.
    
    Args:
        public_key: Public key bytes
        network: Network parameters (defaults to Bitcoin mainnet)
        
    Returns:
        Bitcoin address
    """
    if network is None:
        network = config.get_network()
    
    # Hash the public key
    h160 = hash160(public_key)
    
    # Add version byte
    vh160 = bytes([network['pubKeyHash']]) + h160
    
    # Add checksum
    checksum = hashlib.sha256(hashlib.sha256(vh160).digest()).digest()[:4]
    
    # Encode with Base58
    return b58encode(vh160 + checksum)

def private_key_to_wif(private_key: bytes, compressed: bool = True, network: Optional[Dict[str, Any]] = None) -> str:
    """
    Convert a private key to WIF format.
    
    Args:
        private_key: Private key bytes
        compressed: Whether to use compressed format
        network: Network parameters (defaults to Bitcoin mainnet)
        
    Returns:
        WIF encoded private key
    """
    if network is None:
        network = config.get_network()
    
    # Add network byte
    extended_key = bytes([network['wif']]) + private_key
    
    # Add compression flag if needed
    if compressed:
        extended_key += b'\x01'
    
    # Encode with Base58Check
    return b58encode_check(extended_key)

def wif_to_private_key(wif: str, network: Optional[Dict[str, Any]] = None) -> Tuple[bytes, bool]:
    """
    Convert a WIF private key to raw bytes.
    
    Args:
        wif: WIF encoded private key
        network: Network parameters (defaults to Bitcoin mainnet)
        
    Returns:
        Tuple of (private_key, compressed)
    """
    if network is None:
        network = config.get_network()
    
    # Decode WIF
    decoded = b58decode_check(wif)
    if decoded is None:
        raise KeyError("Invalid WIF key (checksum mismatch)")
    
    # Check network byte
    if decoded[0] != network['wif']:
        raise KeyError(f"WIF key is for a different network (expected {network['wif']}, got {decoded[0]})")
    
    # Check if compressed
    if len(decoded) == 34:  # 1 byte version + 32 bytes key + 1 byte compression flag
        return decoded[1:-1], True
    elif len(decoded) == 33:  # 1 byte version + 32 bytes key
        return decoded[1:], False
    else:
        raise KeyError(f"Invalid WIF key length: {len(decoded)}")

def private_key_to_public_key(private_key: bytes, compressed: bool = True) -> bytes:
    """
    Convert a private key to a public key.
    
    Args:
        private_key: Private key bytes
        compressed: Whether to use compressed format
        
    Returns:
        Public key bytes
    """
    if ecdsa is None:
        raise ImportError("ecdsa module is required for key operations")
    
    # SECP256k1 is the Bitcoin elliptic curve
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    
    if compressed:
        # Compressed public key format
        if vk.pubkey.point.y() & 1:  # Odd y
            return b'\x03' + vk.pubkey.point.x().to_bytes(32, byteorder='big')
        else:  # Even y
            return b'\x02' + vk.pubkey.point.x().to_bytes(32, byteorder='big')
    else:
        # Uncompressed public key format
        return b'\x04' + vk.pubkey.point.x().to_bytes(32, byteorder='big') + vk.pubkey.point.y().to_bytes(32, byteorder='big')

def generate_key_pair(compressed: bool = True, network: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Generate a new Bitcoin key pair.
    
    Args:
        compressed: Whether to use compressed format
        network: Network parameters (defaults to Bitcoin mainnet)
        
    Returns:
        Dictionary with private_key, wif, public_key, and address
    """
    if ecdsa is None:
        raise ImportError("ecdsa module is required for key operations")
    
    if network is None:
        network = config.get_network()
    
    # Generate private key
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    private_key = sk.to_string()
    
    # Generate public key
    public_key = private_key_to_public_key(private_key, compressed)
    
    # Generate address
    address = public_key_to_address(public_key, network)
    
    # Generate WIF
    wif = private_key_to_wif(private_key, compressed, network)
    
    return {
        'private_key': bytes_to_hex(private_key),
        'wif': wif,
        'public_key': bytes_to_hex(public_key),
        'address': address,
        'compressed': compressed
    }

def is_valid_address(address: str, network: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if a Bitcoin address is valid.
    
    Args:
        address: Bitcoin address to check
        network: Network parameters (defaults to Bitcoin mainnet)
        
    Returns:
        True if address is valid, False otherwise
    """
    if network is None:
        network = config.get_network()
    
    try:
        # Decode the address
        decoded = b58decode_check(address)
        if decoded is None:
            return False
        
        # Check version byte
        return decoded[0] == network['pubKeyHash'] or decoded[0] == network['scriptHash']
    except Exception:
        return False

def is_valid_wif(wif: str, network: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if a WIF private key is valid.
    
    Args:
        wif: WIF encoded private key to check
        network: Network parameters (defaults to Bitcoin mainnet)
        
    Returns:
        True if WIF is valid, False otherwise
    """
    try:
        wif_to_private_key(wif, network)
        return True
    except Exception:
        return False
