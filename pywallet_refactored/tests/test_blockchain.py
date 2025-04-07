"""
Tests for the blockchain module.
"""

import unittest
import json
from unittest.mock import patch, MagicMock

from pywallet_refactored.blockchain import (
    BlockchainAPI, BlockchainInfoAPI, BlockcypherAPI,
    get_api_provider, get_balance, get_transactions, format_btc,
    BlockchainError
)

class TestBlockchainAPI(unittest.TestCase):
    """Tests for the base BlockchainAPI class."""
    
    def test_rate_limit(self):
        """Test rate limiting."""
        api = BlockchainAPI()
        
        # Set last request time to now
        api._last_request_time = 0
        
        # Call rate limit
        with patch('time.time', side_effect=[1.0, 1.5]):
            with patch('time.sleep') as mock_sleep:
                api._rate_limit()
                mock_sleep.assert_called_once()
                self.assertAlmostEqual(mock_sleep.call_args[0][0], api.rate_limit_delay - 0.5, places=1)
        
        # Call rate limit again with enough time passed
        with patch('time.time', side_effect=[api.rate_limit_delay + 1.0, api.rate_limit_delay + 1.5]):
            with patch('time.sleep') as mock_sleep:
                api._rate_limit()
                mock_sleep.assert_not_called()
    
    def test_make_request(self):
        """Test making HTTP requests."""
        api = BlockchainAPI()
        
        # Mock rate limit
        api._rate_limit = MagicMock()
        
        # Mock urlopen
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'test': 'data'}).encode('utf-8')
        
        with patch('urllib.request.urlopen', return_value=mock_response) as mock_urlopen:
            result = api._make_request('https://example.com/api')
            
            api._rate_limit.assert_called_once()
            mock_urlopen.assert_called_once_with('https://example.com/api')
            self.assertEqual(result, {'test': 'data'})
    
    def test_get_balance_not_implemented(self):
        """Test get_balance raises NotImplementedError."""
        api = BlockchainAPI()
        
        with self.assertRaises(NotImplementedError):
            api.get_balance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
    
    def test_get_transactions_not_implemented(self):
        """Test get_transactions raises NotImplementedError."""
        api = BlockchainAPI()
        
        with self.assertRaises(NotImplementedError):
            api.get_transactions('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')

class TestBlockchainInfoAPI(unittest.TestCase):
    """Tests for the BlockchainInfoAPI class."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = BlockchainInfoAPI()
        self.api._make_request = MagicMock()
    
    def test_get_balance(self):
        """Test getting balance from blockchain.info."""
        # Mock response
        self.api._make_request.return_value = {
            '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa': {
                'final_balance': 12345678
            }
        }
        
        # Test get_balance
        balance = self.api.get_balance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        
        self.api._make_request.assert_called_once_with(
            'https://blockchain.info/balance?active=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa&format=json'
        )
        self.assertEqual(balance, 12345678)
    
    def test_get_balance_error(self):
        """Test error handling when getting balance."""
        # Mock response with missing address
        self.api._make_request.return_value = {}
        
        # Test get_balance
        with self.assertRaises(BlockchainError):
            self.api.get_balance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
    
    def test_get_transactions(self):
        """Test getting transactions from blockchain.info."""
        # Mock response
        self.api._make_request.return_value = {
            'txs': [
                {'hash': 'tx1', 'time': 1234567890},
                {'hash': 'tx2', 'time': 1234567891}
            ]
        }
        
        # Test get_transactions
        transactions = self.api.get_transactions('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        
        self.api._make_request.assert_called_once_with(
            'https://blockchain.info/rawaddr/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
        )
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]['hash'], 'tx1')
        self.assertEqual(transactions[1]['hash'], 'tx2')
    
    def test_get_transactions_error(self):
        """Test error handling when getting transactions."""
        # Mock response with missing txs
        self.api._make_request.return_value = {}
        
        # Test get_transactions
        with self.assertRaises(BlockchainError):
            self.api.get_transactions('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')

class TestBlockcypherAPI(unittest.TestCase):
    """Tests for the BlockcypherAPI class."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = BlockcypherAPI()
        self.api._make_request = MagicMock()
    
    def test_get_balance(self):
        """Test getting balance from blockcypher."""
        # Mock response
        self.api._make_request.return_value = {
            'final_balance': 12345678
        }
        
        # Test get_balance
        balance = self.api.get_balance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        
        self.api._make_request.assert_called_once_with(
            'https://api.blockcypher.com/v1/btc/main/addrs/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa/balance'
        )
        self.assertEqual(balance, 12345678)
    
    def test_get_balance_error(self):
        """Test error handling when getting balance."""
        # Mock response with missing final_balance
        self.api._make_request.return_value = {}
        
        # Test get_balance
        with self.assertRaises(BlockchainError):
            self.api.get_balance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
    
    def test_get_transactions(self):
        """Test getting transactions from blockcypher."""
        # Mock response
        self.api._make_request.return_value = {
            'txs': [
                {'hash': 'tx1', 'time': 1234567890},
                {'hash': 'tx2', 'time': 1234567891}
            ]
        }
        
        # Test get_transactions
        transactions = self.api.get_transactions('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        
        self.api._make_request.assert_called_once_with(
            'https://api.blockcypher.com/v1/btc/main/addrs/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa/full'
        )
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]['hash'], 'tx1')
        self.assertEqual(transactions[1]['hash'], 'tx2')
    
    def test_get_transactions_error(self):
        """Test error handling when getting transactions."""
        # Mock response with missing txs
        self.api._make_request.return_value = {}
        
        # Test get_transactions
        with self.assertRaises(BlockchainError):
            self.api.get_transactions('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')

class TestBlockchainUtils(unittest.TestCase):
    """Tests for blockchain utility functions."""
    
    @patch('pywallet_refactored.blockchain.config')
    def test_get_api_provider(self, mock_config):
        """Test getting API provider."""
        # Test blockchain.info provider
        mock_config.get.return_value = 'blockchain.info'
        provider = get_api_provider()
        self.assertIsInstance(provider, BlockchainInfoAPI)
        
        # Test blockcypher provider
        mock_config.get.return_value = 'blockcypher'
        provider = get_api_provider()
        self.assertIsInstance(provider, BlockcypherAPI)
        
        # Test unknown provider
        mock_config.get.return_value = 'unknown'
        provider = get_api_provider()
        self.assertIsInstance(provider, BlockchainInfoAPI)  # Default to blockchain.info
    
    @patch('pywallet_refactored.blockchain.get_api_provider')
    def test_get_balance(self, mock_get_provider):
        """Test get_balance function."""
        # Mock API provider
        mock_api = MagicMock()
        mock_api.get_balance.return_value = 12345678
        mock_get_provider.return_value = mock_api
        
        # Test get_balance
        balance_satoshis, balance_btc = get_balance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        
        mock_get_provider.assert_called_once()
        mock_api.get_balance.assert_called_once_with('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(balance_satoshis, 12345678)
        self.assertEqual(balance_btc, '0.12345678 BTC')
    
    @patch('pywallet_refactored.blockchain.get_api_provider')
    def test_get_transactions(self, mock_get_provider):
        """Test get_transactions function."""
        # Mock API provider
        mock_api = MagicMock()
        mock_api.get_transactions.return_value = [
            {'hash': 'tx1', 'time': 1234567890},
            {'hash': 'tx2', 'time': 1234567891}
        ]
        mock_get_provider.return_value = mock_api
        
        # Test get_transactions
        transactions = get_transactions('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        
        mock_get_provider.assert_called_once()
        mock_api.get_transactions.assert_called_once_with('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]['hash'], 'tx1')
        self.assertEqual(transactions[1]['hash'], 'tx2')
    
    def test_format_btc(self):
        """Test BTC formatting."""
        self.assertEqual(format_btc(0), '0.00000000 BTC')
        self.assertEqual(format_btc(1), '0.00000001 BTC')
        self.assertEqual(format_btc(100000000), '1.00000000 BTC')
        self.assertEqual(format_btc(123456789), '1.23456789 BTC')
        self.assertEqual(format_btc(12345678900), '123.45678900 BTC')

if __name__ == '__main__':
    unittest.main()
