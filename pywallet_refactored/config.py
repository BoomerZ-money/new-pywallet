"""
Configuration management for PyWallet.

This module handles loading and managing configuration settings for PyWallet.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration values
DEFAULT_CONFIG = {
    "wallet_dir": "",
    "wallet_name": "wallet.dat",
    "network": "bitcoin",
    "debug": False,
    "log_level": "INFO",
    "log_file": "",
}

# Bitcoin network parameters
NETWORK_BITCOIN = {
    'name': 'Bitcoin',
    'messagePrefix': b'\x18Bitcoin Signed Message:\n',
    'bip32': {
        'public': 0x0488b21e,
        'private': 0x0488ade4,
    },
    'pubKeyHash': 0x00,
    'scriptHash': 0x05,
    'wif': 0x80,
    'bech32': 'bc',
}

# Testnet network parameters
NETWORK_TESTNET = {
    'name': 'Testnet',
    'messagePrefix': b'\x18Bitcoin Signed Message:\n',
    'bip32': {
        'public': 0x043587cf,
        'private': 0x04358394,
    },
    'pubKeyHash': 0x6f,
    'scriptHash': 0xc4,
    'wif': 0xef,
    'bech32': 'tb',
}

# Available networks
NETWORKS = {
    "bitcoin": NETWORK_BITCOIN,
    "testnet": NETWORK_TESTNET,
}

class Config:
    """Configuration manager for PyWallet."""
    
    def __init__(self):
        """Initialize with default configuration."""
        self._config = DEFAULT_CONFIG.copy()
        self._config_file = None
        
    def load_from_file(self, config_file: str) -> bool:
        """
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to the configuration file
            
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self._config.update(file_config)
                self._config_file = config_file
                return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load configuration from {config_file}: {e}")
            return False
    
    def save_to_file(self, config_file: Optional[str] = None) -> bool:
        """
        Save current configuration to a JSON file.
        
        Args:
            config_file: Path to save the configuration file (defaults to previously loaded file)
            
        Returns:
            bool: True if configuration was saved successfully, False otherwise
        """
        if config_file is None:
            if self._config_file is None:
                logging.error("No configuration file specified")
                return False
            config_file = self._config_file
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
                return True
        except Exception as e:
            logging.error(f"Failed to save configuration to {config_file}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            The configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.
        
        Args:
            config_dict: Dictionary of configuration values
        """
        self._config.update(config_dict)
    
    def get_network(self, network_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get network parameters.
        
        Args:
            network_name: Network name (defaults to configured network)
            
        Returns:
            Network parameters dictionary
        """
        if network_name is None:
            network_name = self.get('network', 'bitcoin')
            
        return NETWORKS.get(network_name, NETWORK_BITCOIN)
    
    def determine_wallet_dir(self) -> str:
        """
        Determine the wallet directory based on configuration or system defaults.
        
        Returns:
            Wallet directory path
        """
        wallet_dir = self.get('wallet_dir')
        if wallet_dir:
            return wallet_dir
            
        if os.name == 'posix':
            if os.uname().sysname == 'Darwin':  # macOS
                return os.path.expanduser("~/Library/Application Support/Bitcoin/")
            else:  # Linux/Unix
                return os.path.expanduser("~/.bitcoin")
        elif os.name == 'nt':  # Windows
            return os.path.join(os.environ.get('APPDATA', ''), "Bitcoin")
        
        # Fallback
        return os.path.expanduser("~/.bitcoin")
    
    def determine_wallet_path(self) -> str:
        """
        Determine the full wallet path.
        
        Returns:
            Full path to the wallet file
        """
        wallet_dir = self.determine_wallet_dir()
        wallet_name = self.get('wallet_name', 'wallet.dat')
        return os.path.join(wallet_dir, wallet_name)
    
    @property
    def as_dict(self) -> Dict[str, Any]:
        """
        Get the configuration as a dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()


# Global configuration instance
config = Config()
