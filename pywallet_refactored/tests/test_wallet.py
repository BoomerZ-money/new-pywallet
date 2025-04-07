"""
Tests for the wallet database module.
"""

import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

from pywallet_refactored.db.wallet import WalletDB, WalletDBError

class TestWalletDB(unittest.TestCase):
    """Tests for wallet database operations."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.wallet_path = os.path.join(self.temp_dir, 'test_wallet.dat')
        
        # Mock the DB and DBEnv classes
        self.db_patcher = patch('pywallet_refactored.db.wallet.DB')
        self.dbenv_patcher = patch('pywallet_refactored.db.wallet.DBEnv')
        self.mock_db = self.db_patcher.start()
        self.mock_dbenv = self.dbenv_patcher.start()
        
        # Set up mock DB instance
        self.mock_db_instance = MagicMock()
        self.mock_db.return_value = self.mock_db_instance
        
        # Set up mock DBEnv instance
        self.mock_dbenv_instance = MagicMock()
        self.mock_dbenv.return_value = self.mock_dbenv_instance
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop patchers
        self.db_patcher.stop()
        self.dbenv_patcher.stop()
        
        # Remove temporary directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_init(self):
        """Test WalletDB initialization."""
        wallet = WalletDB(self.wallet_path)
        
        self.assertEqual(wallet.wallet_path, self.wallet_path)
        self.assertIsNone(wallet.db_env)
        self.assertIsNone(wallet.db)
        self.assertIn('keys', wallet.json_db)
        self.assertIn('pool', wallet.json_db)
        self.assertIn('tx', wallet.json_db)
        self.assertIn('names', wallet.json_db)
        self.assertIn('ckey', wallet.json_db)
        self.assertIn('mkey', wallet.json_db)
    
    def test_open_close(self):
        """Test opening and closing wallet database."""
        wallet = WalletDB(self.wallet_path)
        
        # Test open
        wallet.open()
        
        self.mock_dbenv.assert_called_once()
        self.mock_dbenv_instance.open.assert_called_once()
        self.mock_db.assert_called_once()
        self.mock_db_instance.open.assert_called_once()
        
        # Test close
        wallet.close()
        
        self.mock_db_instance.close.assert_called_once()
        self.mock_dbenv_instance.close.assert_called_once()
    
    def test_context_manager(self):
        """Test using WalletDB as a context manager."""
        with WalletDB(self.wallet_path) as wallet:
            self.mock_dbenv.assert_called_once()
            self.mock_dbenv_instance.open.assert_called_once()
            self.mock_db.assert_called_once()
            self.mock_db_instance.open.assert_called_once()
        
        self.mock_db_instance.close.assert_called_once()
        self.mock_dbenv_instance.close.assert_called_once()
    
    @patch('pywallet_refactored.db.wallet.WalletDB._read_records')
    def test_read_wallet(self, mock_read_records):
        """Test reading wallet data."""
        wallet = WalletDB(self.wallet_path)
        
        # Mock open method
        wallet.open = MagicMock()
        
        # Test read_wallet
        result = wallet.read_wallet()
        
        wallet.open.assert_called_once()
        mock_read_records.assert_called_once()
        self.assertEqual(result, wallet.json_db)
    
    @patch('pywallet_refactored.db.wallet.WalletDB.read_wallet')
    def test_dump_wallet(self, mock_read_wallet):
        """Test dumping wallet data to a file."""
        wallet = WalletDB(self.wallet_path)
        
        # Mock read_wallet to return test data
        mock_read_wallet.return_value = {
            'keys': [
                {
                    'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                    'wif': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8',
                    'private_key': '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                    'public_key': '0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',
                    'compressed': True
                }
            ],
            'tx': ['tx1', 'tx2'],
            'names': [{'name': 'test', 'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'}],
            'ckey': [],
            'mkey': []
        }
        
        # Test dump_wallet
        output_file = os.path.join(self.temp_dir, 'wallet_dump.json')
        wallet.dump_wallet(output_file)
        
        # Check output file
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r') as f:
            dump_data = json.load(f)
        
        self.assertIn('keys', dump_data)
        self.assertEqual(len(dump_data['keys']), 1)
        self.assertEqual(dump_data['keys'][0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(dump_data['keys'][0]['wif'], '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8')
        
        # Test without private keys
        output_file_no_private = os.path.join(self.temp_dir, 'wallet_dump_no_private.json')
        wallet.dump_wallet(output_file_no_private, include_private=False)
        
        with open(output_file_no_private, 'r') as f:
            dump_data_no_private = json.load(f)
        
        self.assertIn('keys', dump_data_no_private)
        self.assertEqual(len(dump_data_no_private['keys']), 1)
        self.assertEqual(dump_data_no_private['keys'][0]['address'], '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertNotIn('wif', dump_data_no_private['keys'][0])
    
    @patch('pywallet_refactored.crypto.keys.wif_to_private_key')
    @patch('pywallet_refactored.crypto.keys.private_key_to_public_key')
    @patch('pywallet_refactored.crypto.keys.public_key_to_address')
    def test_import_key(self, mock_to_address, mock_to_public, mock_wif_to_private):
        """Test importing a private key."""
        wallet = WalletDB(self.wallet_path)
        
        # Mock methods
        wallet.open = MagicMock()
        wallet.close = MagicMock()
        
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.next.side_effect = Exception("No more records")
        self.mock_db_instance.cursor.return_value = mock_cursor
        
        # Mock key conversion
        mock_wif_to_private.return_value = (b'private_key', True)
        mock_to_public.return_value = b'public_key'
        mock_to_address.return_value = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
        
        # Test import_key
        wif = '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8'
        address = wallet.import_key(wif, 'Test Key')
        
        wallet.open.assert_called_once()
        mock_wif_to_private.assert_called_once_with(wif)
        mock_to_public.assert_called_once_with(b'private_key', True)
        mock_to_address.assert_called_once_with(b'public_key')
        self.mock_db_instance.put.assert_called()
        self.assertEqual(address, '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
    
    def test_create_new_wallet(self):
        """Test creating a new wallet."""
        wallet = WalletDB(self.wallet_path)
        
        # Test create_new_wallet
        wallet.create_new_wallet()
        
        self.mock_dbenv.assert_called_once()
        self.mock_dbenv_instance.open.assert_called_once()
        self.mock_db.assert_called_once()
        self.mock_db_instance.open.assert_called_once()
        self.mock_db_instance.put.assert_called_once()
    
    def test_create_backup(self):
        """Test creating a wallet backup."""
        wallet = WalletDB(self.wallet_path)
        
        # Mock open method
        wallet.open = MagicMock()
        
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.next.side_effect = [('key1', 'value1'), ('key2', 'value2'), Exception("No more records")]
        self.mock_db_instance.cursor.return_value = mock_cursor
        
        # Test create_backup
        backup_path = os.path.join(self.temp_dir, 'backup.dat')
        wallet.create_backup(backup_path)
        
        wallet.open.assert_called_once()
        self.mock_dbenv.assert_called_once()
        self.mock_db.assert_called_once()
        self.assertEqual(self.mock_db_instance.put.call_count, 2)  # Two records
    
    def test_create_watch_only(self):
        """Test creating a watch-only wallet."""
        wallet = WalletDB(self.wallet_path)
        
        # Mock open method
        wallet.open = MagicMock()
        
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.next.side_effect = [
            (b'\x04key\x01\x02\x03', b'\x01\x02\x03\x04'),  # Private key record
            (b'\x04ckey\x05\x06\x07', b'\x05\x06\x07\x08'),  # Encrypted key record
            (b'\x04mkey\x09\x0A\x0B', b'\x09\x0A\x0B\x0C'),  # Master key record
            (b'\x04name\x0D\x0E\x0F', b'\x0D\x0E\x0F\x10'),  # Name record
            Exception("No more records")
        ]
        self.mock_db_instance.cursor.return_value = mock_cursor
        
        # Test create_watch_only
        watch_only_path = os.path.join(self.temp_dir, 'watch_only.dat')
        wallet.create_watch_only(watch_only_path)
        
        wallet.open.assert_called_once()
        self.mock_dbenv.assert_called_once()
        self.mock_db.assert_called_once()
        self.assertEqual(self.mock_db_instance.put.call_count, 2)  # Private key with dummy value and name record

if __name__ == '__main__':
    unittest.main()
