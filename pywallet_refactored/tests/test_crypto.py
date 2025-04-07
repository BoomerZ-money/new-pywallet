"""
Tests for the crypto module.
"""

import unittest
import binascii
from pywallet_refactored.crypto.base58 import b58encode, b58decode, b58encode_check, b58decode_check
from pywallet_refactored.crypto.keys import (
    hash160, public_key_to_address, private_key_to_wif, wif_to_private_key,
    private_key_to_public_key, is_valid_address, is_valid_wif
)

class TestBase58(unittest.TestCase):
    """Tests for Base58 encoding and decoding."""
    
    def test_b58encode(self):
        """Test Base58 encoding."""
        data = binascii.unhexlify('00010966776006953D5567439E5E39F86A0D273BEED61967F6')
        encoded = b58encode(data)
        self.assertEqual(encoded, '16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM')
    
    def test_b58decode(self):
        """Test Base58 decoding."""
        encoded = '16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM'
        data = b58decode(encoded)
        self.assertEqual(binascii.hexlify(data).decode('ascii').upper(), '00010966776006953D5567439E5E39F86A0D273BEED61967F6')
    
    def test_b58encode_check(self):
        """Test Base58Check encoding."""
        data = binascii.unhexlify('000000000000000000000000000000000000000000000000')
        encoded = b58encode_check(data)
        self.assertEqual(encoded, '1111111111111111111114oLvT2')
    
    def test_b58decode_check(self):
        """Test Base58Check decoding."""
        encoded = '1111111111111111111114oLvT2'
        data = b58decode_check(encoded)
        self.assertEqual(binascii.hexlify(data).decode('ascii').upper(), '000000000000000000000000000000000000000000000000')

class TestKeys(unittest.TestCase):
    """Tests for key handling functions."""
    
    def test_private_key_to_wif_uncompressed(self):
        """Test converting private key to WIF (uncompressed)."""
        private_key = binascii.unhexlify('0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        wif = private_key_to_wif(private_key, compressed=False)
        self.assertEqual(wif, '5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ')
    
    def test_private_key_to_wif_compressed(self):
        """Test converting private key to WIF (compressed)."""
        private_key = binascii.unhexlify('0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        wif = private_key_to_wif(private_key, compressed=True)
        self.assertEqual(wif, 'KwdMAjGmerYanjeui5SHS7JkmpZvVipYvB2LJGU1ZxJwYvP98617')
    
    def test_wif_to_private_key_uncompressed(self):
        """Test converting WIF to private key (uncompressed)."""
        wif = '5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ'
        private_key, compressed = wif_to_private_key(wif)
        self.assertEqual(binascii.hexlify(private_key).decode('ascii').upper(), '0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        self.assertFalse(compressed)
    
    def test_wif_to_private_key_compressed(self):
        """Test converting WIF to private key (compressed)."""
        wif = 'KwdMAjGmerYanjeui5SHS7JkmpZvVipYvB2LJGU1ZxJwYvP98617'
        private_key, compressed = wif_to_private_key(wif)
        self.assertEqual(binascii.hexlify(private_key).decode('ascii').upper(), '0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        self.assertTrue(compressed)
    
    def test_is_valid_wif(self):
        """Test WIF validation."""
        self.assertTrue(is_valid_wif('5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ'))
        self.assertTrue(is_valid_wif('KwdMAjGmerYanjeui5SHS7JkmpZvVipYvB2LJGU1ZxJwYvP98617'))
        self.assertFalse(is_valid_wif('5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyT'))  # Too short
        self.assertFalse(is_valid_wif('5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJJ'))  # Too long
        self.assertFalse(is_valid_wif('5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTI'))  # Invalid checksum
    
    def test_is_valid_address(self):
        """Test address validation."""
        self.assertTrue(is_valid_address('1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'))
        self.assertTrue(is_valid_address('3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy'))
        self.assertFalse(is_valid_address('1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN'))  # Too short
        self.assertFalse(is_valid_address('1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN22'))  # Too long
        self.assertFalse(is_valid_address('1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN1'))  # Invalid checksum

if __name__ == '__main__':
    unittest.main()
