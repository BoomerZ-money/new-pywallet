"""
Tests for the batch operations module.
"""

import unittest
import os
import tempfile
import json
import csv
from unittest.mock import patch, MagicMock

from pywallet_refactored.batch import (
    import_keys_from_file, export_keys_to_file, read_keys_from_file,
    read_keys_from_json, read_keys_from_csv, read_keys_from_text,
    export_keys_to_json, export_keys_to_csv, export_keys_to_text,
    generate_key_batch, save_key_batch, BatchError
)

class TestBatchOperations(unittest.TestCase):
    """Tests for batch operations."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample keys for testing
        self.sample_keys = [
            {
                'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                'wif': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8',
                'private_key': '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                'public_key': '0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',
                'compressed': True
            },
            {
                'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
                'wif': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9',
                'private_key': '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                'public_key': '0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',
                'compressed': True
            }
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_read_keys_from_json(self):
        """Test reading keys from a JSON file."""
        # Create a JSON file with keys
        json_file = os.path.join(self.temp_dir, 'keys.json')
        with open(json_file, 'w') as f:
            json.dump({'keys': self.sample_keys}, f)
        
        # Test reading keys
        keys = read_keys_from_json(json_file)
        
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(keys[1]['address'], '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2')
        
        # Test reading keys from a list
        json_file_list = os.path.join(self.temp_dir, 'keys_list.json')
        with open(json_file_list, 'w') as f:
            json.dump(self.sample_keys, f)
        
        keys = read_keys_from_json(json_file_list)
        
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(keys[1]['address'], '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2')
        
        # Test reading keys from a single object
        json_file_single = os.path.join(self.temp_dir, 'key_single.json')
        with open(json_file_single, 'w') as f:
            json.dump(self.sample_keys[0], f)
        
        keys = read_keys_from_json(json_file_single)
        
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        
        # Test invalid JSON
        json_file_invalid = os.path.join(self.temp_dir, 'invalid.json')
        with open(json_file_invalid, 'w') as f:
            f.write('invalid json')
        
        with self.assertRaises(BatchError):
            read_keys_from_json(json_file_invalid)
    
    def test_read_keys_from_csv(self):
        """Test reading keys from a CSV file."""
        # Create a CSV file with keys
        csv_file = os.path.join(self.temp_dir, 'keys.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['address', 'wif', 'private_key', 'compressed'])
            writer.writeheader()
            for key in self.sample_keys:
                writer.writerow({
                    'address': key['address'],
                    'wif': key['wif'],
                    'private_key': key['private_key'],
                    'compressed': key['compressed']
                })
        
        # Test reading keys
        keys = read_keys_from_csv(csv_file)
        
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(keys[1]['address'], '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2')
        
        # Test CSV without private key
        csv_file_no_private = os.path.join(self.temp_dir, 'keys_no_private.csv')
        with open(csv_file_no_private, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['address', 'compressed'])
            writer.writeheader()
            for key in self.sample_keys:
                writer.writerow({
                    'address': key['address'],
                    'compressed': key['compressed']
                })
        
        keys = read_keys_from_csv(csv_file_no_private)
        
        self.assertEqual(len(keys), 0)  # No keys with private key
    
    @patch('pywallet_refactored.batch.is_valid_wif')
    def test_read_keys_from_text(self, mock_is_valid_wif):
        """Test reading keys from a text file."""
        # Mock is_valid_wif to return True
        mock_is_valid_wif.return_value = True
        
        # Create a text file with keys
        text_file = os.path.join(self.temp_dir, 'keys.txt')
        with open(text_file, 'w') as f:
            f.write('# Private keys\n')
            f.write('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8 # First key\n')
            f.write('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9 # Second key\n')
            f.write('# End of file\n')
        
        # Test reading keys
        keys = read_keys_from_text(text_file)
        
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0], '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8')
        self.assertEqual(keys[1], '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9')
        
        # Test with invalid keys
        mock_is_valid_wif.side_effect = lambda x: x == '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8'
        
        keys = read_keys_from_text(text_file)
        
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0], '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8')
    
    def test_read_keys_from_file(self):
        """Test reading keys from different file types."""
        # Create files
        json_file = os.path.join(self.temp_dir, 'keys.json')
        with open(json_file, 'w') as f:
            json.dump({'keys': self.sample_keys}, f)
        
        csv_file = os.path.join(self.temp_dir, 'keys.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['address', 'wif', 'private_key', 'compressed'])
            writer.writeheader()
            for key in self.sample_keys:
                writer.writerow({
                    'address': key['address'],
                    'wif': key['wif'],
                    'private_key': key['private_key'],
                    'compressed': key['compressed']
                })
        
        # Mock functions
        with patch('pywallet_refactored.batch.read_keys_from_json') as mock_json:
            with patch('pywallet_refactored.batch.read_keys_from_csv') as mock_csv:
                with patch('pywallet_refactored.batch.read_keys_from_text') as mock_text:
                    # Test JSON
                    read_keys_from_file(json_file)
                    mock_json.assert_called_once_with(json_file)
                    
                    # Test CSV
                    read_keys_from_file(csv_file)
                    mock_csv.assert_called_once_with(csv_file)
                    
                    # Test text
                    read_keys_from_file('keys.txt')
                    mock_text.assert_called_once_with('keys.txt')
    
    def test_export_keys_to_json(self):
        """Test exporting keys to a JSON file."""
        # Test with private keys
        json_file = os.path.join(self.temp_dir, 'export.json')
        export_keys_to_json(self.sample_keys, json_file)
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('keys', data)
        self.assertEqual(len(data['keys']), 2)
        self.assertEqual(data['keys'][0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(data['keys'][0]['wif'], '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8')
        
        # Test without private keys
        json_file_no_private = os.path.join(self.temp_dir, 'export_no_private.json')
        export_keys_to_json(self.sample_keys, json_file_no_private, include_private=False)
        
        with open(json_file_no_private, 'r') as f:
            data = json.load(f)
        
        self.assertIn('keys', data)
        self.assertEqual(len(data['keys']), 2)
        self.assertEqual(data['keys'][0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertNotIn('wif', data['keys'][0])
        self.assertNotIn('private_key', data['keys'][0])
    
    def test_export_keys_to_csv(self):
        """Test exporting keys to a CSV file."""
        # Test with private keys
        csv_file = os.path.join(self.temp_dir, 'export.csv')
        export_keys_to_csv(self.sample_keys, csv_file)
        
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(rows[0]['wif'], '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8')
        
        # Test without private keys
        csv_file_no_private = os.path.join(self.temp_dir, 'export_no_private.csv')
        export_keys_to_csv(self.sample_keys, csv_file_no_private, include_private=False)
        
        with open(csv_file_no_private, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertNotIn('wif', rows[0])
        self.assertNotIn('private_key', rows[0])
    
    def test_export_keys_to_text(self):
        """Test exporting keys to a text file."""
        # Test with private keys
        text_file = os.path.join(self.temp_dir, 'export.txt')
        export_keys_to_text(self.sample_keys, text_file)
        
        with open(text_file, 'r') as f:
            lines = f.readlines()
        
        self.assertTrue(any(line.startswith('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8') for line in lines))
        self.assertTrue(any(line.startswith('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9') for line in lines))
        
        # Test without private keys
        text_file_no_private = os.path.join(self.temp_dir, 'export_no_private.txt')
        export_keys_to_text(self.sample_keys, text_file_no_private, include_private=False)
        
        with open(text_file_no_private, 'r') as f:
            lines = f.readlines()
        
        self.assertTrue(any(line.startswith('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa') for line in lines))
        self.assertTrue(any(line.startswith('1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2') for line in lines))
        self.assertFalse(any(line.startswith('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8') for line in lines))
    
    @patch('pywallet_refactored.batch.WalletDB')
    @patch('pywallet_refactored.batch.read_keys_from_file')
    @patch('pywallet_refactored.batch.is_valid_wif')
    def test_import_keys_from_file(self, mock_is_valid_wif, mock_read_keys, mock_wallet_db):
        """Test importing keys from a file."""
        # Mock is_valid_wif to return True
        mock_is_valid_wif.return_value = True
        
        # Mock read_keys_from_file
        mock_read_keys.return_value = [
            '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8',
            '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9'
        ]
        
        # Mock WalletDB
        mock_wallet_instance = MagicMock()
        mock_wallet_instance.import_key.side_effect = ['1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2']
        mock_wallet_db.return_value = mock_wallet_instance
        
        # Test import_keys_from_file
        wallet_path = os.path.join(self.temp_dir, 'wallet.dat')
        input_file = os.path.join(self.temp_dir, 'keys.txt')
        
        addresses = import_keys_from_file(wallet_path, input_file, 'Test')
        
        mock_read_keys.assert_called_once_with(input_file)
        mock_wallet_db.assert_called_once_with(wallet_path)
        self.assertEqual(mock_wallet_instance.import_key.call_count, 2)
        self.assertEqual(len(addresses), 2)
        self.assertEqual(addresses[0], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(addresses[1], '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2')
        
        # Test with dictionary keys
        mock_read_keys.return_value = [
            {'wif': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8', 'label': 'Key 1'},
            {'wif': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9', 'label': 'Key 2'}
        ]
        
        addresses = import_keys_from_file(wallet_path, input_file, 'Test')
        
        self.assertEqual(mock_wallet_instance.import_key.call_count, 4)
        self.assertEqual(len(addresses), 2)
    
    @patch('pywallet_refactored.batch.WalletDB')
    def test_export_keys_to_file(self, mock_wallet_db):
        """Test exporting keys to a file."""
        # Mock WalletDB
        mock_wallet_instance = MagicMock()
        mock_wallet_instance.read_wallet.return_value = {
            'keys': self.sample_keys
        }
        mock_wallet_db.return_value = mock_wallet_instance
        
        # Test export_keys_to_file
        wallet_path = os.path.join(self.temp_dir, 'wallet.dat')
        
        # Test JSON export
        json_file = os.path.join(self.temp_dir, 'export.json')
        
        with patch('pywallet_refactored.batch.export_keys_to_json') as mock_export_json:
            export_keys_to_file(wallet_path, json_file)
            
            mock_wallet_db.assert_called_once_with(wallet_path)
            mock_wallet_instance.read_wallet.assert_called_once_with('')
            mock_export_json.assert_called_once_with(self.sample_keys, json_file, True)
        
        # Test CSV export
        csv_file = os.path.join(self.temp_dir, 'export.csv')
        
        with patch('pywallet_refactored.batch.export_keys_to_csv') as mock_export_csv:
            export_keys_to_file(wallet_path, csv_file, include_private=False, passphrase='test')
            
            mock_wallet_instance.read_wallet.assert_called_with('test')
            mock_export_csv.assert_called_once_with(self.sample_keys, csv_file, False)
    
    @patch('pywallet_refactored.batch.generate_key_pair')
    def test_generate_key_batch(self, mock_generate_key):
        """Test generating a batch of keys."""
        # Mock generate_key_pair
        mock_generate_key.side_effect = [
            {'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'wif': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8'},
            {'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2', 'wif': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9'}
        ]
        
        # Test generate_key_batch
        keys = generate_key_batch(2)
        
        self.assertEqual(mock_generate_key.call_count, 2)
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(keys[1]['address'], '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2')
        
        # Test with compressed=False
        generate_key_batch(1, compressed=False)
        
        mock_generate_key.assert_called_with(False)
    
    def test_save_key_batch(self):
        """Test saving a batch of keys."""
        # Test JSON
        json_file = os.path.join(self.temp_dir, 'batch.json')
        
        with patch('pywallet_refactored.batch.export_keys_to_json') as mock_export_json:
            save_key_batch(self.sample_keys, json_file)
            mock_export_json.assert_called_once_with(self.sample_keys, json_file)
        
        # Test CSV
        csv_file = os.path.join(self.temp_dir, 'batch.csv')
        
        with patch('pywallet_refactored.batch.export_keys_to_csv') as mock_export_csv:
            save_key_batch(self.sample_keys, csv_file)
            mock_export_csv.assert_called_once_with(self.sample_keys, csv_file)
        
        # Test text
        text_file = os.path.join(self.temp_dir, 'batch.txt')
        
        with patch('pywallet_refactored.batch.export_keys_to_text') as mock_export_text:
            save_key_batch(self.sample_keys, text_file)
            mock_export_text.assert_called_once_with(self.sample_keys, text_file)

if __name__ == '__main__':
    unittest.main()
