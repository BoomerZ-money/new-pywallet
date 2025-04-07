"""
Tests for the AES encryption module.
"""

import unittest
import os
from pywallet_refactored.crypto.aes import (
    derive_key, encrypt_aes, decrypt_aes, decrypt_wallet_key
)

class TestAES(unittest.TestCase):
    """Tests for AES encryption and decryption."""
    
    def test_derive_key(self):
        """Test key derivation from password."""
        password = b'test_password'
        salt = b'salt1234'
        iterations = 2048
        key_length = 32
        
        key = derive_key(password, salt, iterations, key_length)
        
        # Check key properties
        self.assertEqual(len(key), key_length)
        self.assertIsInstance(key, bytes)
        
        # Check deterministic output
        key2 = derive_key(password, salt, iterations, key_length)
        self.assertEqual(key, key2)
        
        # Check different password produces different key
        key3 = derive_key(b'different_password', salt, iterations, key_length)
        self.assertNotEqual(key, key3)
        
        # Check different salt produces different key
        key4 = derive_key(password, b'diff_salt', iterations, key_length)
        self.assertNotEqual(key, key4)
        
        # Check different iterations produces different key
        key5 = derive_key(password, salt, iterations + 1, key_length)
        self.assertNotEqual(key, key5)
    
    def test_encrypt_decrypt_aes(self):
        """Test AES encryption and decryption."""
        key = os.urandom(32)  # 256-bit key
        data = b'This is a test message for encryption'
        
        # Encrypt data
        encrypted = encrypt_aes(data, key)
        
        # Check encrypted data properties
        self.assertNotEqual(encrypted, data)
        self.assertTrue(len(encrypted) > len(data))
        
        # Decrypt data
        decrypted = decrypt_aes(encrypted, key)
        
        # Check decryption result
        self.assertEqual(decrypted, data)
        
        # Check wrong key fails
        wrong_key = os.urandom(32)
        with self.assertRaises(Exception):
            decrypt_aes(encrypted, wrong_key)
    
    def test_encrypt_decrypt_with_iv(self):
        """Test AES encryption and decryption with explicit IV."""
        key = os.urandom(32)  # 256-bit key
        iv = os.urandom(16)   # 128-bit IV
        data = b'This is a test message with explicit IV'
        
        # Encrypt data with explicit IV
        encrypted = encrypt_aes(data, key, iv)
        
        # Check encrypted data properties
        self.assertNotEqual(encrypted, data)
        self.assertTrue(len(encrypted) > len(data))
        
        # Decrypt data
        decrypted = decrypt_aes(encrypted, key)
        
        # Check decryption result
        self.assertEqual(decrypted, data)
    
    def test_decrypt_wallet_key(self):
        """Test wallet key decryption."""
        # This is a simplified test since we don't have real wallet keys
        derived_key = os.urandom(32)
        wallet_key = os.urandom(32)
        
        # Encrypt wallet key
        encrypted_key = encrypt_aes(wallet_key, derived_key)
        
        # Decrypt wallet key
        decrypted_key = decrypt_wallet_key(encrypted_key, derived_key)
        
        # Check decryption result
        self.assertEqual(decrypted_key, wallet_key)
    
    def test_padding(self):
        """Test padding handling in AES encryption."""
        key = os.urandom(32)
        
        # Test different data lengths to ensure padding works correctly
        for length in range(1, 33):  # Test lengths 1-32 bytes
            data = os.urandom(length)
            encrypted = encrypt_aes(data, key)
            decrypted = decrypt_aes(encrypted, key)
            self.assertEqual(decrypted, data)

if __name__ == '__main__':
    unittest.main()
