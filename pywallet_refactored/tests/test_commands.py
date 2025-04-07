"""
Tests for the CLI commands.
"""

import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

from pywallet_refactored.cli.commands import (
    dump_wallet, import_key, create_wallet, backup_wallet,
    generate_key, check_address, check_key, recover_keys,
    check_balance, get_tx_history, create_watch_only_wallet
)
from pywallet_refactored.db.wallet import WalletDBError

class TestCommands(unittest.TestCase):
    """Tests for CLI commands."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.wallet_path = os.path.join(self.temp_dir, 'test_wallet.dat')
        self.output_path = os.path.join(self.temp_dir, 'output.json')
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    @patch('pywallet_refactored.cli.commands.WalletDB')
    @patch('pywallet_refactored.cli.commands.config')
    def test_dump_wallet(self, mock_config, mock_wallet_db):
        """Test dump_wallet command."""
        # Mock config
        mock_config.determine_wallet_path.return_value = self.wallet_path
        
        # Mock WalletDB
        mock_wallet_instance = MagicMock()
        mock_wallet_db.return_value = mock_wallet_instance
        
        # Test with explicit wallet path
        args = {
            'wallet': self.wallet_path,
            'dumpwallet': self.output_path,
            'no_private': False,
            'passphrase': 'test'
        }
        
        result = dump_wallet(args)
        
        mock_wallet_db.assert_called_once_with(self.wallet_path)
        mock_wallet_instance.read_wallet.assert_called_once_with('test')
        mock_wallet_instance.dump_wallet.assert_called_once_with(self.output_path, include_private=True)
        self.assertEqual(result, 0)
        
        # Test with default wallet path
        mock_wallet_db.reset_mock()
        mock_wallet_instance.reset_mock()
        
        args = {
            'wallet': None,
            'dumpwallet': True,  # Flag without value
            'no_private': True
        }
        
        result = dump_wallet(args)
        
        mock_config.determine_wallet_path.assert_called_once()
        mock_wallet_db.assert_called_once_with(self.wallet_path)
        mock_wallet_instance.dump_wallet.assert_called_once_with(
            os.path.splitext(self.wallet_path)[0] + '.json', include_private=False
        )
        self.assertEqual(result, 0)
        
        # Test error handling
        mock_wallet_instance.read_wallet.side_effect = WalletDBError("Test error")
        
        result = dump_wallet(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.WalletDB')
    @patch('pywallet_refactored.cli.commands.config')
    @patch('pywallet_refactored.cli.commands.is_valid_wif')
    def test_import_key(self, mock_is_valid_wif, mock_config, mock_wallet_db):
        """Test import_key command."""
        # Mock config
        mock_config.determine_wallet_path.return_value = self.wallet_path
        
        # Mock WalletDB
        mock_wallet_instance = MagicMock()
        mock_wallet_instance.import_key.return_value = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
        mock_wallet_db.return_value = mock_wallet_instance
        
        # Mock is_valid_wif
        mock_is_valid_wif.return_value = True
        
        # Test with explicit wallet path
        args = {
            'wallet': self.wallet_path,
            'importprivkey': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8',
            'label': 'Test Key'
        }
        
        result = import_key(args)
        
        mock_is_valid_wif.assert_called_once_with('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8')
        mock_wallet_db.assert_called_once_with(self.wallet_path)
        mock_wallet_instance.import_key.assert_called_once_with(
            '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8', 'Test Key'
        )
        self.assertEqual(result, 0)
        
        # Test with invalid key
        mock_is_valid_wif.return_value = False
        
        result = import_key(args)
        
        self.assertEqual(result, 1)
        
        # Test error handling
        mock_is_valid_wif.return_value = True
        mock_wallet_instance.import_key.side_effect = WalletDBError("Test error")
        
        result = import_key(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.WalletDB')
    @patch('pywallet_refactored.cli.commands.generate_key_pair')
    def test_create_wallet(self, mock_generate_key, mock_wallet_db):
        """Test create_wallet command."""
        # Mock WalletDB
        mock_wallet_instance = MagicMock()
        mock_wallet_db.return_value = mock_wallet_instance
        
        # Mock generate_key_pair
        mock_generate_key.return_value = {
            'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'wif': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8'
        }
        
        # Test with explicit output path
        args = {
            'createwallet': self.wallet_path,
            'force': False,
            'generate_key': True,
            'save_key': True
        }
        
        result = create_wallet(args)
        
        mock_wallet_db.assert_called_once_with(self.wallet_path)
        mock_wallet_instance.create_new_wallet.assert_called_once()
        mock_generate_key.assert_called_once()
        mock_wallet_instance.import_key.assert_called_once_with(
            '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8', 'Initial key'
        )
        self.assertEqual(result, 0)
        
        # Test with existing wallet and force=True
        mock_wallet_db.reset_mock()
        mock_wallet_instance.reset_mock()
        
        with patch('os.path.exists', return_value=True):
            with patch('os.rename') as mock_rename:
                args = {
                    'createwallet': self.wallet_path,
                    'force': True,
                    'generate_key': False
                }
                
                result = create_wallet(args)
                
                mock_rename.assert_called_once()
                mock_wallet_db.assert_called_once_with(self.wallet_path)
                mock_wallet_instance.create_new_wallet.assert_called_once()
                mock_wallet_instance.import_key.assert_not_called()
                self.assertEqual(result, 0)
        
        # Test with existing wallet and force=False
        with patch('os.path.exists', return_value=True):
            args = {
                'createwallet': self.wallet_path,
                'force': False
            }
            
            result = create_wallet(args)
            
            self.assertEqual(result, 1)
        
        # Test error handling
        mock_wallet_instance.create_new_wallet.side_effect = WalletDBError("Test error")
        
        with patch('os.path.exists', return_value=False):
            result = create_wallet(args)
            
            self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.WalletDB')
    @patch('pywallet_refactored.cli.commands.config')
    def test_backup_wallet(self, mock_config, mock_wallet_db):
        """Test backup_wallet command."""
        # Mock config
        mock_config.determine_wallet_path.return_value = self.wallet_path
        
        # Mock WalletDB
        mock_wallet_instance = MagicMock()
        mock_wallet_db.return_value = mock_wallet_instance
        
        # Test with explicit paths
        args = {
            'wallet': self.wallet_path,
            'backupwallet': self.output_path
        }
        
        result = backup_wallet(args)
        
        mock_wallet_db.assert_called_once_with(self.wallet_path)
        mock_wallet_instance.create_backup.assert_called_once_with(self.output_path)
        self.assertEqual(result, 0)
        
        # Test with default backup path
        mock_wallet_db.reset_mock()
        mock_wallet_instance.reset_mock()
        
        with patch('time.time', return_value=1234567890):
            args = {
                'wallet': self.wallet_path,
                'backupwallet': True  # Flag without value
            }
            
            result = backup_wallet(args)
            
            mock_wallet_instance.create_backup.assert_called_once_with(self.wallet_path + '.bak.1234567890')
            self.assertEqual(result, 0)
        
        # Test error handling
        mock_wallet_instance.create_backup.side_effect = WalletDBError("Test error")
        
        result = backup_wallet(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.WalletDB')
    @patch('pywallet_refactored.cli.commands.config')
    def test_create_watch_only_wallet(self, mock_config, mock_wallet_db):
        """Test create_watch_only_wallet command."""
        # Mock config
        mock_config.determine_wallet_path.return_value = self.wallet_path
        
        # Mock WalletDB
        mock_wallet_instance = MagicMock()
        mock_wallet_db.return_value = mock_wallet_instance
        
        # Test with explicit paths
        args = {
            'wallet': self.wallet_path,
            'output': self.output_path
        }
        
        result = create_watch_only_wallet(args)
        
        mock_wallet_db.assert_called_once_with(self.wallet_path)
        mock_wallet_instance.create_watch_only.assert_called_once_with(self.output_path)
        self.assertEqual(result, 0)
        
        # Test without output path
        args = {
            'wallet': self.wallet_path,
            'output': None
        }
        
        result = create_watch_only_wallet(args)
        
        self.assertEqual(result, 1)
        
        # Test error handling
        mock_wallet_instance.create_watch_only.side_effect = WalletDBError("Test error")
        
        args = {
            'wallet': self.wallet_path,
            'output': self.output_path
        }
        
        result = create_watch_only_wallet(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.generate_key_pair')
    def test_generate_key(self, mock_generate_key):
        """Test generate_key command."""
        # Mock generate_key_pair
        mock_generate_key.return_value = {
            'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'wif': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8',
            'private_key': '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
            'public_key': '0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',
            'compressed': True
        }
        
        # Test with default options
        args = {
            'uncompressed': False,
            'save_key': False
        }
        
        with patch('builtins.print') as mock_print:
            result = generate_key(args)
            
            mock_generate_key.assert_called_once_with(True)
            self.assertEqual(mock_print.call_count, 5)  # 5 print statements
            self.assertEqual(result, 0)
        
        # Test with uncompressed=True
        mock_generate_key.reset_mock()
        
        args = {
            'uncompressed': True,
            'save_key': False
        }
        
        with patch('builtins.print'):
            result = generate_key(args)
            
            mock_generate_key.assert_called_once_with(False)
            self.assertEqual(result, 0)
        
        # Test with save_key=True
        mock_generate_key.reset_mock()
        
        args = {
            'uncompressed': False,
            'save_key': True
        }
        
        with patch('builtins.print'):
            with patch('builtins.open', create=True) as mock_open:
                with patch('json.dump') as mock_json_dump:
                    result = generate_key(args)
                    
                    mock_generate_key.assert_called_once_with(True)
                    mock_open.assert_called_once()
                    mock_json_dump.assert_called_once()
                    self.assertEqual(result, 0)
        
        # Test error handling
        mock_generate_key.side_effect = Exception("Test error")
        
        result = generate_key(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.is_valid_address')
    def test_check_address(self, mock_is_valid):
        """Test check_address command."""
        # Test with valid address
        mock_is_valid.return_value = True
        
        args = {
            'checkaddress': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
        }
        
        with patch('builtins.print') as mock_print:
            result = check_address(args)
            
            mock_is_valid.assert_called_once_with('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
            mock_print.assert_called_once_with('Address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa is valid')
            self.assertEqual(result, 0)
        
        # Test with invalid address
        mock_is_valid.return_value = False
        
        with patch('builtins.print') as mock_print:
            result = check_address(args)
            
            mock_print.assert_called_once_with('Address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa is NOT valid')
            self.assertEqual(result, 1)
        
        # Test error handling
        mock_is_valid.side_effect = Exception("Test error")
        
        result = check_address(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.is_valid_wif')
    @patch('pywallet_refactored.cli.commands.wif_to_private_key')
    @patch('pywallet_refactored.cli.commands.private_key_to_public_key')
    @patch('pywallet_refactored.cli.commands.public_key_to_address')
    def test_check_key(self, mock_to_address, mock_to_public, mock_wif_to_private, mock_is_valid):
        """Test check_key command."""
        # Test with valid key
        mock_is_valid.return_value = True
        mock_wif_to_private.return_value = (b'private_key', True)
        mock_to_public.return_value = b'public_key'
        mock_to_address.return_value = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
        
        args = {
            'checkkey': '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8'
        }
        
        with patch('builtins.print') as mock_print:
            result = check_key(args)
            
            mock_is_valid.assert_called_once_with('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8')
            mock_wif_to_private.assert_called_once_with('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8')
            mock_to_public.assert_called_once_with(b'private_key', True)
            mock_to_address.assert_called_once_with(b'public_key')
            self.assertEqual(mock_print.call_count, 3)  # 3 print statements
            self.assertEqual(result, 0)
        
        # Test with invalid key
        mock_is_valid.return_value = False
        
        with patch('builtins.print') as mock_print:
            result = check_key(args)
            
            mock_print.assert_called_once_with('Private key is NOT valid')
            self.assertEqual(result, 1)
        
        # Test error handling
        mock_is_valid.side_effect = Exception("Test error")
        
        result = check_key(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.config')
    @patch('pywallet_refactored.cli.commands.get_balance')
    @patch('pywallet_refactored.cli.commands.is_valid_address')
    def test_check_balance(self, mock_is_valid, mock_get_balance, mock_config):
        """Test check_balance command."""
        # Test with valid address
        mock_is_valid.return_value = True
        mock_get_balance.return_value = (12345678, '0.12345678 BTC')
        
        args = {
            'addresses': ['1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'],
            'provider': 'blockchain.info'
        }
        
        with patch('builtins.print') as mock_print:
            result = check_balance(args)
            
            mock_config.set.assert_called_once_with('blockchain_provider', 'blockchain.info')
            mock_is_valid.assert_called_once_with('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
            mock_get_balance.assert_called_once_with('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
            self.assertEqual(mock_print.call_count, 3)  # 3 print statements
            self.assertEqual(result, 0)
        
        # Test with invalid address
        mock_is_valid.return_value = False
        
        result = check_balance(args)
        
        self.assertEqual(result, 0)  # Still returns 0 but logs an error
        
        # Test with multiple addresses
        mock_is_valid.return_value = True
        
        args = {
            'addresses': ['1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'],
            'provider': None
        }
        
        with patch('builtins.print'):
            result = check_balance(args)
            
            self.assertEqual(mock_is_valid.call_count, 3)  # Called for both addresses
            self.assertEqual(mock_get_balance.call_count, 2)  # Called for both addresses
            self.assertEqual(result, 0)
        
        # Test error handling
        mock_get_balance.side_effect = Exception("Test error")
        
        result = check_balance(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.config')
    @patch('pywallet_refactored.cli.commands.get_transactions')
    @patch('pywallet_refactored.cli.commands.is_valid_address')
    def test_get_tx_history(self, mock_is_valid, mock_get_transactions, mock_config):
        """Test get_tx_history command."""
        # Test with valid address
        mock_is_valid.return_value = True
        mock_get_transactions.return_value = [
            {
                'hash': 'tx1',
                'time': 1234567890,
                'inputs': [{'prev_out': {'addr': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'value': 1000000}}],
                'out': [{'addr': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2', 'value': 900000}]
            }
        ]
        
        args = {
            'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'provider': 'blockchain.info',
            'output': None
        }
        
        with patch('builtins.print') as mock_print:
            with patch('time.strftime', return_value='2009-02-13 23:31:30'):
                result = get_tx_history(args)
                
                mock_config.set.assert_called_once_with('blockchain_provider', 'blockchain.info')
                mock_is_valid.assert_called_once_with('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
                mock_get_transactions.assert_called_once_with('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
                self.assertEqual(mock_print.call_count, 8)  # 8 print statements
                self.assertEqual(result, 0)
        
        # Test with invalid address
        mock_is_valid.return_value = False
        
        result = get_tx_history(args)
        
        self.assertEqual(result, 1)
        
        # Test with output file
        mock_is_valid.return_value = True
        
        args = {
            'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'provider': None,
            'output': self.output_path
        }
        
        with patch('builtins.print'):
            with patch('builtins.open', create=True) as mock_open:
                with patch('json.dump') as mock_json_dump:
                    result = get_tx_history(args)
                    
                    mock_open.assert_called_once_with(self.output_path, 'w')
                    mock_json_dump.assert_called_once()
                    self.assertEqual(result, 0)
        
        # Test error handling
        mock_get_transactions.side_effect = Exception("Test error")
        
        result = get_tx_history(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.commands.scan_file')
    @patch('pywallet_refactored.cli.commands.scan_device')
    @patch('pywallet_refactored.cli.commands.recover_keys_from_passphrase')
    @patch('pywallet_refactored.cli.commands.dump_keys_to_file')
    @patch('pywallet_refactored.cli.commands.dump_encrypted_keys_to_file')
    def test_recover_keys(self, mock_dump_encrypted, mock_dump_keys, mock_recover, mock_scan_device, mock_scan_file):
        """Test recover_keys command."""
        # Mock scan results
        scan_results = {
            'keys': [{'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'}],
            'encrypted_keys': [{'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'}],
            'master_keys': [{'iterations': 2048}]
        }
        
        # Test with file
        mock_scan_file.return_value = scan_results
        
        args = {
            'file': self.wallet_path,
            'device': None,
            'start': 0,
            'size': None,
            'output': self.output_path,
            'passphrase': None
        }
        
        result = recover_keys(args)
        
        mock_scan_file.assert_called_once_with(self.wallet_path, 0, None)
        mock_dump_keys.assert_called_once_with([{'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'}], self.output_path)
        self.assertEqual(result, 0)
        
        # Test with device
        mock_scan_file.reset_mock()
        mock_dump_keys.reset_mock()
        mock_scan_device.return_value = scan_results
        
        args = {
            'file': None,
            'device': '/dev/sda',
            'start': 1024,
            'size': 1048576,
            'output': self.output_path,
            'passphrase': None
        }
        
        result = recover_keys(args)
        
        mock_scan_device.assert_called_once_with('/dev/sda', 1024, 1048576)
        mock_dump_keys.assert_called_once_with([{'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'}], self.output_path)
        self.assertEqual(result, 0)
        
        # Test with passphrase
        mock_scan_device.reset_mock()
        mock_dump_keys.reset_mock()
        mock_recover.return_value = [{'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'}]
        
        args = {
            'file': self.wallet_path,
            'device': None,
            'start': 0,
            'size': None,
            'output': self.output_path,
            'passphrase': 'test'
        }
        
        result = recover_keys(args)
        
        mock_scan_file.assert_called_with(self.wallet_path, 0, None)
        mock_recover.assert_called_once_with(
            [{'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'}],
            {'iterations': 2048},
            'test'
        )
        mock_dump_keys.assert_called_once_with(
            [{'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'}, {'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'}],
            self.output_path
        )
        self.assertEqual(result, 0)
        
        # Test with no keys found but encrypted keys
        mock_scan_file.return_value = {
            'keys': [],
            'encrypted_keys': [{'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'}],
            'master_keys': [{'iterations': 2048}]
        }
        mock_recover.return_value = []
        
        result = recover_keys(args)
        
        mock_dump_encrypted.assert_called_once_with(
            [{'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'}],
            {'iterations': 2048},
            self.output_path
        )
        self.assertEqual(result, 0)
        
        # Test with no source
        args = {
            'file': None,
            'device': None,
            'output': self.output_path
        }
        
        result = recover_keys(args)
        
        self.assertEqual(result, 1)
        
        # Test error handling
        mock_scan_file.side_effect = Exception("Test error")
        
        args = {
            'file': self.wallet_path,
            'device': None,
            'output': self.output_path
        }
        
        result = recover_keys(args)
        
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()
