"""
Tests for the utils module
"""

import unittest
import os
import tempfile
from pywallet.utils import plural, systype, md5_2, multiextract

class TestUtils(unittest.TestCase):
    def test_plural(self):
        self.assertEqual(plural(0), '')
        self.assertEqual(plural(1), '')
        self.assertEqual(plural(2), 's')
        self.assertEqual(plural(10), 's')

    def test_systype(self):
        # This test will depend on the system it's running on
        # Just make sure it returns one of the expected values
        system_type = systype()
        self.assertIn(system_type, ['Mac', 'Win', 'Linux'])

    def test_md5_2(self):
        self.assertEqual(md5_2('test'), '098f6bcd4621d373cade4e832627b4f6')
        self.assertEqual(md5_2(''), 'd41d8cd98f00b204e9800998ecf8427e')

    def test_multiextract(self):
        data = b'abcdefghijklmnopqrstuvwxyz'
        lengths = [3, 5, 7]
        result = multiextract(data, lengths)
        self.assertEqual(result, [b'abc', b'defgh', b'ijklmno', b'pqrstuvwxyz'])

    def test_multiextract_exact_length(self):
        data = b'abcdefghijklmn'
        lengths = [3, 5, 6]
        result = multiextract(data, lengths)
        self.assertEqual(result, [b'abc', b'defgh', b'ijklmn'])

if __name__ == '__main__':
    unittest.main()
