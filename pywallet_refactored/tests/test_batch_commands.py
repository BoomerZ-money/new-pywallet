"""
Tests for the batch command handlers.
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock

from pywallet_refactored.cli.batch_commands import (
    batch_import_keys, batch_export_keys, batch_generate_keys,
    handle_batch_command
)
from pywallet_refactored.batch import BatchError

class TestBatchCommands(unittest.TestCase):
    """Tests for batch command handlers."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.wallet_path = os.path.join(self.temp_dir, 'test_wallet.dat')
        self.input_path = os.path.join(self.temp_dir, 'input.txt')
        self.output_path = os.path.join(self.temp_dir, 'output.json')
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    @patch('pywallet_refactored.cli.batch_commands.import_keys_from_file')
    @patch('pywallet_refactored.cli.batch_commands.config')
    def test_batch_import_keys(self, mock_config, mock_import_keys):
        """Test batch_import_keys command."""
        # Mock config
        mock_config.determine_wallet_path.return_value = self.wallet_path
        
        # Mock import_keys_from_file
        mock_import_keys.return_value = ['1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2']
        
        # Test with explicit wallet path
        args = {
            'wallet': self.wallet_path,
            'input': self.input_path,
            'label': 'Test'
        }
        
        result = batch_import_keys(args)
        
        mock_config.determine_wallet_path.assert_not_called()
        mock_import_keys.assert_called_once_with(self.wallet_path, self.input_path, 'Test')
        self.assertEqual(result, 0)
        
        # Test with default wallet path
        mock_config.reset_mock()
        mock_import_keys.reset_mock()
        
        args = {
            'wallet': None,
            'input': self.input_path,
            'label': 'Imported'
        }
        
        result = batch_import_keys(args)
        
        mock_config.determine_wallet_path.assert_called_once()
        mock_import_keys.assert_called_once_with(self.wallet_path, self.input_path, 'Imported')
        self.assertEqual(result, 0)
        
        # Test without input file
        args = {
            'wallet': self.wallet_path,
            'input': None
        }
        
        result = batch_import_keys(args)
        
        self.assertEqual(result, 1)
        
        # Test with no keys imported
        mock_import_keys.return_value = []
        
        args = {
            'wallet': self.wallet_path,
            'input': self.input_path
        }
        
        result = batch_import_keys(args)
        
        self.assertEqual(result, 1)
        
        # Test error handling
        mock_import_keys.side_effect = BatchError("Test error")
        
        result = batch_import_keys(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.batch_commands.export_keys_to_file')
    @patch('pywallet_refactored.cli.batch_commands.config')
    def test_batch_export_keys(self, mock_config, mock_export_keys):
        """Test batch_export_keys command."""
        # Mock config
        mock_config.determine_wallet_path.return_value = self.wallet_path
        
        # Mock export_keys_to_file
        mock_export_keys.return_value = 2
        
        # Test with explicit wallet path
        args = {
            'wallet': self.wallet_path,
            'output': self.output_path,
            'no_private': False,
            'passphrase': 'test'
        }
        
        result = batch_export_keys(args)
        
        mock_config.determine_wallet_path.assert_not_called()
        mock_export_keys.assert_called_once_with(self.wallet_path, self.output_path, True, 'test')
        self.assertEqual(result, 0)
        
        # Test with default wallet path
        mock_config.reset_mock()
        mock_export_keys.reset_mock()
        
        args = {
            'wallet': None,
            'output': self.output_path,
            'no_private': True,
            'passphrase': ''
        }
        
        result = batch_export_keys(args)
        
        mock_config.determine_wallet_path.assert_called_once()
        mock_export_keys.assert_called_once_with(self.wallet_path, self.output_path, False, '')
        self.assertEqual(result, 0)
        
        # Test without output file
        args = {
            'wallet': self.wallet_path,
            'output': None
        }
        
        result = batch_export_keys(args)
        
        self.assertEqual(result, 1)
        
        # Test with no keys exported
        mock_export_keys.return_value = 0
        
        args = {
            'wallet': self.wallet_path,
            'output': self.output_path
        }
        
        result = batch_export_keys(args)
        
        self.assertEqual(result, 1)
        
        # Test error handling
        mock_export_keys.side_effect = BatchError("Test error")
        
        result = batch_export_keys(args)
        
        self.assertEqual(result, 1)
    
    @patch('pywallet_refactored.cli.batch_commands.generate_key_batch')
    @patch('pywallet_refactored.cli.batch_commands.save_key_batch')
    def test_batch_generate_keys(self, mock_save_keys, mock_generate_keys):
        """Test batch_generate_keys command."""
        # Mock generate_key_batch
        mock_generate_keys.return_value = [
            {'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'},
            {'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'}
        ]
        
        # Test with valid arguments
        args = {
            'count': 2,
            'output': self.output_path,
            'uncompressed': False
        }
        
        result = batch_generate_keys(args)
        
        mock_generate_keys.assert_called_once_with(2, True)
        mock_save_keys.assert_called_once_with(
            [{'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'}, {'address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'}],
            self.output_path
        )
        self.assertEqual(result, 0)
        
        # Test with uncompressed=True
        mock_generate_keys.reset_mock()
        mock_save_keys.reset_mock()
        
        args = {
            'count': 2,
            'output': self.output_path,
            'uncompressed': True
        }
        
        result = batch_generate_keys(args)
        
        mock_generate_keys.assert_called_once_with(2, False)
        self.assertEqual(result, 0)
        
        # Test with invalid count
        args = {
            'count': 0,
            'output': self.output_path
        }
        
        result = batch_generate_keys(args)
        
        self.assertEqual(result, 1)
        
        # Test without output file
        args = {
            'count': 2,
            'output': None
        }
        
        result = batch_generate_keys(args)
        
        self.assertEqual(result, 1)
        
        # Test with no keys generated
        mock_generate_keys.return_value = []
        
        args = {
            'count': 2,
            'output': self.output_path
        }
        
        result = batch_generate_keys(args)
        
        self.assertEqual(result, 1)
        
        # Test error handling
        mock_generate_keys.side_effect = BatchError("Test error")
        
        result = batch_generate_keys(args)
        
        self.assertEqual(result, 1)
    
    def test_handle_batch_command(self):
        """Test handle_batch_command function."""
        # Test import command
        with patch('pywallet_refactored.cli.batch_commands.batch_import_keys', return_value=0) as mock_import:
            args = {'batch_command': 'import'}
            
            result = handle_batch_command(args)
            
            mock_import.assert_called_once_with(args)
            self.assertEqual(result, 0)
        
        # Test export command
        with patch('pywallet_refactored.cli.batch_commands.batch_export_keys', return_value=0) as mock_export:
            args = {'batch_command': 'export'}
            
            result = handle_batch_command(args)
            
            mock_export.assert_called_once_with(args)
            self.assertEqual(result, 0)
        
        # Test generate command
        with patch('pywallet_refactored.cli.batch_commands.batch_generate_keys', return_value=0) as mock_generate:
            args = {'batch_command': 'generate'}
            
            result = handle_batch_command(args)
            
            mock_generate.assert_called_once_with(args)
            self.assertEqual(result, 0)
        
        # Test unknown command
        args = {'batch_command': 'unknown'}
        
        result = handle_batch_command(args)
        
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()
