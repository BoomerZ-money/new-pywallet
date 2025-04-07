"""
Cryptographic functions for PyWallet
"""

import hashlib
import binascii
import ecdsa
from pywallet.config import network_bitcoin, network_testnet

def hash_160(public_key):
    """Perform RIPEMD-160(SHA-256(public_key))"""
    md = hashlib.new('ripemd160')
    md.update(hashlib.sha256(public_key).digest())
    return md.digest()

def public_key_to_address(public_key, network=network_bitcoin):
    """Convert a public key to a Bitcoin address"""
    h160 = hash_160(public_key)
    return hash_160_to_address(h160, network['pubKeyHash'])

def hash_160_to_address(h160, addrtype):
    """Convert a RIPEMD-160 hash to a Bitcoin address"""
    vh160 = bytes([addrtype]) + h160
    h = hashlib.sha256(hashlib.sha256(vh160).digest()).digest()
    addr = vh160 + h[0:4]
    return b58encode(addr)

def b58encode(v):
    """Base58 encode a string"""
    b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    long_value = int.from_bytes(v, byteorder='big')
    
    result = ''
    while long_value >= 58:
        div, mod = divmod(long_value, 58)
        result = b58_digits[mod] + result
        long_value = div
    result = b58_digits[long_value] + result
    
    # Bitcoin does a little leading-zero dance
    nPad = 0
    for c in v:
        if c == 0:
            nPad += 1
        else:
            break
    
    return b58_digits[0] * nPad + result

def b58decode(v):
    """Base58 decode a string"""
    b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    long_value = 0
    for c in v:
        long_value = long_value * 58 + b58_digits.find(c)
    
    result = long_value.to_bytes((long_value.bit_length() + 7) // 8, byteorder='big')
    
    # Bitcoin does a little leading-zero dance
    nPad = 0
    for c in v:
        if c == b58_digits[0]:
            nPad += 1
        else:
            break
    
    result = b'\x00' * nPad + result
    
    return result

def private_key_to_wif(private_key, compressed=True, network=network_bitcoin):
    """Convert a private key to WIF format"""
    # Add network byte and compression flag
    if compressed:
        extended_key = bytes([network['wif']]) + private_key + b'\x01'
    else:
        extended_key = bytes([network['wif']]) + private_key
    
    # Double SHA-256 checksum
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    
    # Encode with Base58
    return b58encode(extended_key + checksum)

def wif_to_private_key(wif, network=network_bitcoin):
    """Convert a WIF private key to raw bytes"""
    decoded = b58decode(wif)
    
    # Check network byte
    if decoded[0] != network['wif']:
        raise ValueError("WIF key is not for the correct network")
    
    # Check checksum
    checksum = hashlib.sha256(hashlib.sha256(decoded[:-4]).digest()).digest()[:4]
    if checksum != decoded[-4:]:
        raise ValueError("WIF checksum is invalid")
    
    # Check if compressed
    if len(decoded) == 38:  # Compressed key
        return decoded[1:-5], True
    else:  # Uncompressed key
        return decoded[1:-4], False

def private_key_to_public_key(private_key, compressed=True):
    """Convert a private key to a public key"""
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
