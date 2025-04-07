"""
Tests for the utils module.
"""

import unittest
import os
import tempfile
from pywallet_refactored.utils.common import (
    plural, systype, md5_hash, sha256_hash, str_to_bytes, bytes_to_str,
    hex_to_bytes, bytes_to_hex, multi_extract
)

class TestCommonUtils(unittest.TestCase):
    """Tests for common utility functions."""
    
    def test_plural(self):
        """Test plural function."""
        self.assertEqual(plural(0), 's')
        self.assertEqual(plural(1), '')
        self.assertEqual(plural(2), 's')
    
    def test_systype(self):
        """Test systype function."""
        system_type = systype()
        self.assertIn(system_type, ['Mac', 'Win', 'Linux'])
    
    def test_md5_hash(self):
        """Test MD5 hash function."""
        self.assertEqual(md5_hash('test'), '098f6bcd4621d373cade4e832627b4f6')
        self.assertEqual(md5_hash(b'test'), '098f6bcd4621d373cade4e832627b4f6')
        self.assertEqual(md5_hash(''), 'd41d8cd98f00b204e9800998ecf8427e')
    
    def test_sha256_hash(self):
        """Test SHA256 hash function."""
        self.assertEqual(sha256_hash('test'), '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08')
        self.assertEqual(sha256_hash(b'test'), '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08')
        self.assertEqual(sha256_hash(''), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
    
    def test_str_to_bytes(self):
        """Test string to bytes conversion."""
        self.assertEqual(str_to_bytes('test'), b'test')
        self.assertEqual(str_to_bytes(b'test'), b'test')
        self.assertEqual(str_to_bytes(123), b'123')
    
    def test_bytes_to_str(self):
        """Test bytes to string conversion."""
        self.assertEqual(bytes_to_str(b'test'), 'test')
        self.assertEqual(bytes_to_str('test'), 'test')
        self.assertEqual(bytes_to_str(b'\xff\xfe\xfd'), 'ÿþý')  # Latin-1 fallback
    
    def test_hex_to_bytes(self):
        """Test hex to bytes conversion."""
        self.assertEqual(hex_to_bytes('74657374'), b'test')
        self.assertEqual(hex_to_bytes('00010203'), b'\x00\x01\x02\x03')
    
    def test_bytes_to_hex(self):
        """Test bytes to hex conversion."""
        self.assertEqual(bytes_to_hex(b'test'), '74657374')
        self.assertEqual(bytes_to_hex(b'\x00\x01\x02\x03'), '00010203')
    
    def test_multi_extract(self):
        """Test multi_extract function."""
        data = b'abcdefghijklmnopqrstuvwxyz'
        lengths = [3, 5, 7]
        result = multi_extract(data, lengths)
        self.assertEqual(result, [b'abc', b'defgh', b'ijklmno', b'pqrstuvwxyz'])
        
        # Test exact length
        data = b'abcdefghijklmn'
        lengths = [3, 5, 6]
        result = multi_extract(data, lengths)
        self.assertEqual(result, [b'abc', b'defgh', b'ijklmn'])

if __name__ == '__main__':
    unittest.main()
