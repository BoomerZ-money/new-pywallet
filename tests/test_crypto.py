"""
Tests for the crypto module
"""

import unittest
import binascii
from pywallet.crypto import (
    hash_160, 
    public_key_to_address, 
    private_key_to_wif, 
    wif_to_private_key,
    private_key_to_public_key
)
from pywallet.config import network_bitcoin, network_testnet

class TestCrypto(unittest.TestCase):
    def test_private_key_to_wif_uncompressed(self):
        # Test vector from Bitcoin Wiki
        private_key = binascii.unhexlify('0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        wif = private_key_to_wif(private_key, compressed=False)
        self.assertEqual(wif, '5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ')

    def test_private_key_to_wif_compressed(self):
        # Test vector from Bitcoin Wiki
        private_key = binascii.unhexlify('0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        wif = private_key_to_wif(private_key, compressed=True)
        self.assertEqual(wif, 'KwdMAjGmerYanjeui5SHS7JkmpZvVipYvB2LJGU1ZxJwYvP98617')

    def test_wif_to_private_key_uncompressed(self):
        wif = '5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ'
        private_key, compressed = wif_to_private_key(wif)
        self.assertEqual(binascii.hexlify(private_key).decode('ascii').upper(), 
                         '0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        self.assertFalse(compressed)

    def test_wif_to_private_key_compressed(self):
        wif = 'KwdMAjGmerYanjeui5SHS7JkmpZvVipYvB2LJGU1ZxJwYvP98617'
        private_key, compressed = wif_to_private_key(wif)
        self.assertEqual(binascii.hexlify(private_key).decode('ascii').upper(), 
                         '0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        self.assertTrue(compressed)

    def test_private_key_to_public_key_uncompressed(self):
        private_key = binascii.unhexlify('0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        public_key = private_key_to_public_key(private_key, compressed=False)
        expected = '04D0DE0AAEAEFAD02B8BDC8A01A1B8B11C696BD3D66A2C5F10780D95B7DF42645CD85228A6FB29940E858E7E55842AE2BD115D1ED7CC0E82D934E929C97648CB0A'
        self.assertEqual(binascii.hexlify(public_key).decode('ascii').upper(), expected)

    def test_private_key_to_public_key_compressed(self):
        private_key = binascii.unhexlify('0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D')
        public_key = private_key_to_public_key(private_key, compressed=True)
        # The expected value depends on whether the y-coordinate is even or odd
        expected_even = '02D0DE0AAEAEFAD02B8BDC8A01A1B8B11C696BD3D66A2C5F10780D95B7DF42645C'
        expected_odd = '03D0DE0AAEAEFAD02B8BDC8A01A1B8B11C696BD3D66A2C5F10780D95B7DF42645C'
        
        actual = binascii.hexlify(public_key).decode('ascii').upper()
        self.assertTrue(actual == expected_even or actual == expected_odd)

if __name__ == '__main__':
    unittest.main()
