"""
Blockchain interaction module for PyWallet.

This module provides functions for interacting with the Bitcoin blockchain,
including fetching balance information and transaction history.
"""

import json
import time
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional, Union, Tuple

from pywallet_refactored.logger import logger
from pywallet_refactored.config import config

class BlockchainError(Exception):
    """Exception raised for blockchain interaction errors."""
    pass

class BlockchainAPI:
    """Base class for blockchain API providers."""
    
    def __init__(self):
        """Initialize blockchain API."""
        self.rate_limit_delay = 1.0  # seconds between requests
        self._last_request_time = 0
    
    def _rate_limit(self):
        """Apply rate limiting to API requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self._last_request_time = time.time()
    
    def _make_request(self, url: str) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            url: URL to request
            
        Returns:
            JSON response as dictionary
            
        Raises:
            BlockchainError: If the request fails
        """
        self._rate_limit()
        
        try:
            with urllib.request.urlopen(url) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise BlockchainError(f"HTTP error: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            raise BlockchainError(f"URL error: {e.reason}")
        except json.JSONDecodeError:
            raise BlockchainError("Invalid JSON response")
        except Exception as e:
            raise BlockchainError(f"Request failed: {e}")
    
    def get_balance(self, address: str) -> int:
        """
        Get balance for an address in satoshis.
        
        Args:
            address: Bitcoin address
            
        Returns:
            Balance in satoshis
            
        Raises:
            BlockchainError: If the balance cannot be fetched
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement get_balance")
    
    def get_transactions(self, address: str) -> List[Dict[str, Any]]:
        """
        Get transaction history for an address.
        
        Args:
            address: Bitcoin address
            
        Returns:
            List of transactions
            
        Raises:
            BlockchainError: If the transactions cannot be fetched
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement get_transactions")

class BlockchainInfoAPI(BlockchainAPI):
    """Blockchain.info API provider."""
    
    def __init__(self):
        """Initialize blockchain.info API."""
        super().__init__()
        self.base_url = "https://blockchain.info"
        self.rate_limit_delay = 2.0  # blockchain.info has stricter rate limits
    
    def get_balance(self, address: str) -> int:
        """
        Get balance for an address in satoshis from blockchain.info.
        
        Args:
            address: Bitcoin address
            
        Returns:
            Balance in satoshis
            
        Raises:
            BlockchainError: If the balance cannot be fetched
        """
        url = f"{self.base_url}/balance?active={address}&format=json"
        
        try:
            response = self._make_request(url)
            if address in response:
                return response[address]['final_balance']
            else:
                raise BlockchainError(f"Address {address} not found in response")
        except Exception as e:
            raise BlockchainError(f"Failed to get balance for {address}: {e}")
    
    def get_transactions(self, address: str) -> List[Dict[str, Any]]:
        """
        Get transaction history for an address from blockchain.info.
        
        Args:
            address: Bitcoin address
            
        Returns:
            List of transactions
            
        Raises:
            BlockchainError: If the transactions cannot be fetched
        """
        url = f"{self.base_url}/rawaddr/{address}"
        
        try:
            response = self._make_request(url)
            if 'txs' in response:
                return response['txs']
            else:
                raise BlockchainError(f"No transactions found for {address}")
        except Exception as e:
            raise BlockchainError(f"Failed to get transactions for {address}: {e}")

class BlockcypherAPI(BlockchainAPI):
    """Blockcypher API provider."""
    
    def __init__(self):
        """Initialize blockcypher API."""
        super().__init__()
        self.base_url = "https://api.blockcypher.com/v1/btc/main"
        self.rate_limit_delay = 1.0
    
    def get_balance(self, address: str) -> int:
        """
        Get balance for an address in satoshis from blockcypher.
        
        Args:
            address: Bitcoin address
            
        Returns:
            Balance in satoshis
            
        Raises:
            BlockchainError: If the balance cannot be fetched
        """
        url = f"{self.base_url}/addrs/{address}/balance"
        
        try:
            response = self._make_request(url)
            if 'final_balance' in response:
                return response['final_balance']
            else:
                raise BlockchainError(f"Balance not found in response for {address}")
        except Exception as e:
            raise BlockchainError(f"Failed to get balance for {address}: {e}")
    
    def get_transactions(self, address: str) -> List[Dict[str, Any]]:
        """
        Get transaction history for an address from blockcypher.
        
        Args:
            address: Bitcoin address
            
        Returns:
            List of transactions
            
        Raises:
            BlockchainError: If the transactions cannot be fetched
        """
        url = f"{self.base_url}/addrs/{address}/full"
        
        try:
            response = self._make_request(url)
            if 'txs' in response:
                return response['txs']
            else:
                raise BlockchainError(f"No transactions found for {address}")
        except Exception as e:
            raise BlockchainError(f"Failed to get transactions for {address}: {e}")

def get_api_provider() -> BlockchainAPI:
    """
    Get the configured blockchain API provider.
    
    Returns:
        BlockchainAPI instance
    """
    provider = config.get('blockchain_provider', 'blockchain.info')
    
    if provider == 'blockchain.info':
        return BlockchainInfoAPI()
    elif provider == 'blockcypher':
        return BlockcypherAPI()
    else:
        logger.warning(f"Unknown blockchain provider: {provider}, using blockchain.info")
        return BlockchainInfoAPI()

def get_balance(address: str) -> Tuple[int, str]:
    """
    Get balance for an address in satoshis and formatted BTC.
    
    Args:
        address: Bitcoin address
        
    Returns:
        Tuple of (balance_satoshis, balance_btc)
        
    Raises:
        BlockchainError: If the balance cannot be fetched
    """
    api = get_api_provider()
    
    try:
        balance_satoshis = api.get_balance(address)
        balance_btc = format_btc(balance_satoshis)
        return balance_satoshis, balance_btc
    except Exception as e:
        raise BlockchainError(f"Failed to get balance: {e}")

def get_transactions(address: str) -> List[Dict[str, Any]]:
    """
    Get transaction history for an address.
    
    Args:
        address: Bitcoin address
        
    Returns:
        List of transactions
        
    Raises:
        BlockchainError: If the transactions cannot be fetched
    """
    api = get_api_provider()
    
    try:
        return api.get_transactions(address)
    except Exception as e:
        raise BlockchainError(f"Failed to get transactions: {e}")

def format_btc(satoshis: int) -> str:
    """
    Format satoshis as BTC string.
    
    Args:
        satoshis: Amount in satoshis
        
    Returns:
        Formatted BTC string
    """
    btc = satoshis / 100000000.0
    return f"{btc:.8f} BTC"
