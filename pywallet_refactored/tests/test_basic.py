#!/usr/bin/env python3
"""
Basic tests for pywallet_refactored
"""

import unittest
import os
import sys

# Add parent directory to path to import pywallet_refactored
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pywallet_refactored.crypto.keys import (
    private_key_to_wif,
    private_key_to_public_key,
    public_key_to_address
)


class TestBasic(unittest.TestCase):
    """Basic tests for pywallet_refactored"""

    def test_key_conversion(self):
        """Test key conversion functions"""
        # Test private key to WIF conversion
        private_key = bytes.fromhex('0c28fca386c7a227600b2fe50b7cae11ec86d3bf1fbe471be89827e19d72aa1d')
        expected_wif = '5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ'
        
        wif = private_key_to_wif(private_key, compressed=False)
        self.assertEqual(wif, expected_wif)
        
        # Test private key to public key conversion
        public_key = private_key_to_public_key(private_key, compressed=False)
        self.assertTrue(len(public_key) > 0)
        
        # Test public key to address conversion
        address = public_key_to_address(public_key)
        self.assertTrue(address.startswith('1'))


if __name__ == '__main__':
    unittest.main()
