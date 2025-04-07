"""
Batch operations for PyWallet.

This module provides functions for batch operations on Bitcoin keys.
"""

import os
import csv
import json
from typing import List, Dict, Any, Optional, Union, Tuple

from pywallet_refactored.logger import logger
from pywallet_refactored.db.wallet import WalletDB, WalletDBError
from pywallet_refactored.crypto.keys import (
    generate_key_pair, is_valid_wif, is_valid_address,
    wif_to_private_key, private_key_to_public_key, public_key_to_address
)

class BatchError(Exception):
    """Exception raised for batch operation errors."""
    pass

def import_keys_from_file(wallet_path: str, input_file: str, label_prefix: str = "") -> List[str]:
    """
    Import private keys from a file into a wallet.
    
    The file can be in CSV, JSON, or plain text format.
    
    Args:
        wallet_path: Path to the wallet file
        input_file: Path to the input file containing keys
        label_prefix: Prefix for key labels
        
    Returns:
        List of imported addresses
        
    Raises:
        BatchError: If the keys cannot be imported
    """
    try:
        # Read keys from file
        keys = read_keys_from_file(input_file)
        
        if not keys:
            raise BatchError(f"No valid keys found in {input_file}")
        
        # Open wallet
        wallet = WalletDB(wallet_path)
        
        # Import keys
        imported_addresses = []
        
        for i, key_data in enumerate(keys):
            try:
                # Get key and label
                if isinstance(key_data, dict):
                    wif = key_data.get('wif') or key_data.get('private_key')
                    label = key_data.get('label') or f"{label_prefix}{i+1}"
                else:
                    wif = key_data
                    label = f"{label_prefix}{i+1}"
                
                # Validate key
                if not is_valid_wif(wif):
                    logger.warning(f"Invalid key: {wif}")
                    continue
                
                # Import key
                address = wallet.import_key(wif, label)
                imported_addresses.append(address)
                
                logger.info(f"Imported key {i+1}/{len(keys)}: {address}")
            except Exception as e:
                logger.error(f"Failed to import key {i+1}/{len(keys)}: {e}")
        
        return imported_addresses
    except Exception as e:
        raise BatchError(f"Failed to import keys: {e}")

def export_keys_to_file(wallet_path: str, output_file: str, include_private: bool = True, passphrase: str = "") -> int:
    """
    Export keys from a wallet to a file.
    
    Args:
        wallet_path: Path to the wallet file
        output_file: Path to the output file
        include_private: Whether to include private keys
        passphrase: Wallet passphrase for encrypted wallets
        
    Returns:
        Number of exported keys
        
    Raises:
        BatchError: If the keys cannot be exported
    """
    try:
        # Open wallet
        wallet = WalletDB(wallet_path)
        
        # Read wallet
        wallet_data = wallet.read_wallet(passphrase)
        
        # Get keys
        keys = wallet_data.get('keys', [])
        
        if not keys:
            logger.warning(f"No keys found in {wallet_path}")
            return 0
        
        # Determine file format from extension
        _, ext = os.path.splitext(output_file)
        ext = ext.lower()
        
        # Export keys
        if ext == '.json':
            export_keys_to_json(keys, output_file, include_private)
        elif ext == '.csv':
            export_keys_to_csv(keys, output_file, include_private)
        else:
            export_keys_to_text(keys, output_file, include_private)
        
        logger.info(f"Exported {len(keys)} keys to {output_file}")
        return len(keys)
    except Exception as e:
        raise BatchError(f"Failed to export keys: {e}")

def read_keys_from_file(input_file: str) -> List[Union[str, Dict[str, str]]]:
    """
    Read keys from a file.
    
    The file can be in CSV, JSON, or plain text format.
    
    Args:
        input_file: Path to the input file
        
    Returns:
        List of keys (strings or dictionaries)
        
    Raises:
        BatchError: If the keys cannot be read
    """
    try:
        # Determine file format from extension
        _, ext = os.path.splitext(input_file)
        ext = ext.lower()
        
        # Read keys
        if ext == '.json':
            return read_keys_from_json(input_file)
        elif ext == '.csv':
            return read_keys_from_csv(input_file)
        else:
            return read_keys_from_text(input_file)
    except Exception as e:
        raise BatchError(f"Failed to read keys from {input_file}: {e}")

def read_keys_from_json(input_file: str) -> List[Dict[str, str]]:
    """
    Read keys from a JSON file.
    
    Args:
        input_file: Path to the JSON file
        
    Returns:
        List of key dictionaries
        
    Raises:
        BatchError: If the keys cannot be read
    """
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON formats
        if isinstance(data, list):
            # List of keys
            return data
        elif isinstance(data, dict):
            # Dictionary with keys
            if 'keys' in data:
                return data['keys']
            else:
                # Try to convert to list
                return [data]
        else:
            raise BatchError(f"Invalid JSON format in {input_file}")
    except json.JSONDecodeError:
        raise BatchError(f"Invalid JSON in {input_file}")
    except Exception as e:
        raise BatchError(f"Failed to read JSON from {input_file}: {e}")

def read_keys_from_csv(input_file: str) -> List[Dict[str, str]]:
    """
    Read keys from a CSV file.
    
    Args:
        input_file: Path to the CSV file
        
    Returns:
        List of key dictionaries
        
    Raises:
        BatchError: If the keys cannot be read
    """
    try:
        keys = []
        
        with open(input_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Check for required fields
                if 'wif' in row or 'private_key' in row:
                    keys.append(row)
                else:
                    logger.warning(f"Skipping row without private key: {row}")
        
        return keys
    except Exception as e:
        raise BatchError(f"Failed to read CSV from {input_file}: {e}")

def read_keys_from_text(input_file: str) -> List[str]:
    """
    Read keys from a text file.
    
    Args:
        input_file: Path to the text file
        
    Returns:
        List of key strings
        
    Raises:
        BatchError: If the keys cannot be read
    """
    try:
        keys = []
        
        with open(input_file, 'r') as f:
            for line in f:
                # Strip whitespace and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Extract key (first word in line)
                key = line.split()[0]
                
                # Validate key
                if is_valid_wif(key):
                    keys.append(key)
                else:
                    logger.warning(f"Invalid key: {key}")
        
        return keys
    except Exception as e:
        raise BatchError(f"Failed to read text from {input_file}: {e}")

def export_keys_to_json(keys: List[Dict[str, Any]], output_file: str, include_private: bool = True) -> None:
    """
    Export keys to a JSON file.
    
    Args:
        keys: List of key dictionaries
        output_file: Path to the output file
        include_private: Whether to include private keys
        
    Raises:
        BatchError: If the keys cannot be exported
    """
    try:
        # Filter keys
        filtered_keys = []
        
        for key in keys:
            key_data = {
                'address': key['address'],
                'compressed': key['compressed']
            }
            
            if include_private:
                key_data['wif'] = key['wif']
                key_data['private_key'] = key['private_key']
            
            filtered_keys.append(key_data)
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump({'keys': filtered_keys}, f, indent=4)
    except Exception as e:
        raise BatchError(f"Failed to export keys to JSON: {e}")

def export_keys_to_csv(keys: List[Dict[str, Any]], output_file: str, include_private: bool = True) -> None:
    """
    Export keys to a CSV file.
    
    Args:
        keys: List of key dictionaries
        output_file: Path to the output file
        include_private: Whether to include private keys
        
    Raises:
        BatchError: If the keys cannot be exported
    """
    try:
        # Determine fields
        fields = ['address', 'compressed']
        
        if include_private:
            fields.extend(['wif', 'private_key'])
        
        # Write to file
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            
            for key in keys:
                # Filter fields
                row = {field: key.get(field, '') for field in fields}
                writer.writerow(row)
    except Exception as e:
        raise BatchError(f"Failed to export keys to CSV: {e}")

def export_keys_to_text(keys: List[Dict[str, Any]], output_file: str, include_private: bool = True) -> None:
    """
    Export keys to a text file.
    
    Args:
        keys: List of key dictionaries
        output_file: Path to the output file
        include_private: Whether to include private keys
        
    Raises:
        BatchError: If the keys cannot be exported
    """
    try:
        with open(output_file, 'w') as f:
            f.write("# PyWallet exported keys\n")
            f.write("# Format: [WIF] [Address] [Compressed]\n\n")
            
            for key in keys:
                if include_private:
                    f.write(f"{key['wif']} {key['address']} {key['compressed']}\n")
                else:
                    f.write(f"{key['address']} {key['compressed']}\n")
    except Exception as e:
        raise BatchError(f"Failed to export keys to text: {e}")

def generate_key_batch(count: int, compressed: bool = True) -> List[Dict[str, Any]]:
    """
    Generate a batch of key pairs.
    
    Args:
        count: Number of key pairs to generate
        compressed: Whether to use compressed format
        
    Returns:
        List of key pair dictionaries
        
    Raises:
        BatchError: If the keys cannot be generated
    """
    try:
        keys = []
        
        for i in range(count):
            try:
                key_pair = generate_key_pair(compressed)
                keys.append(key_pair)
                
                logger.debug(f"Generated key {i+1}/{count}: {key_pair['address']}")
            except Exception as e:
                logger.error(f"Failed to generate key {i+1}/{count}: {e}")
        
        return keys
    except Exception as e:
        raise BatchError(f"Failed to generate keys: {e}")

def save_key_batch(keys: List[Dict[str, Any]], output_file: str) -> None:
    """
    Save a batch of key pairs to a file.
    
    Args:
        keys: List of key pair dictionaries
        output_file: Path to the output file
        
    Raises:
        BatchError: If the keys cannot be saved
    """
    try:
        # Determine file format from extension
        _, ext = os.path.splitext(output_file)
        ext = ext.lower()
        
        # Save keys
        if ext == '.json':
            export_keys_to_json(keys, output_file)
        elif ext == '.csv':
            export_keys_to_csv(keys, output_file)
        else:
            export_keys_to_text(keys, output_file)
        
        logger.info(f"Saved {len(keys)} keys to {output_file}")
    except Exception as e:
        raise BatchError(f"Failed to save keys: {e}")

def import_addresses_from_file(wallet_path: str, input_file: str, label_prefix: str = "") -> List[str]:
    """
    Import addresses from a file into a wallet as watch-only addresses.
    
    The file can be in CSV, JSON, or plain text format.
    
    Args:
        wallet_path: Path to the wallet file
        input_file: Path to the input file containing addresses
        label_prefix: Prefix for address labels
        
    Returns:
        List of imported addresses
        
    Raises:
        BatchError: If the addresses cannot be imported
    """
    try:
        # Read addresses from file
        addresses = read_addresses_from_file(input_file)
        
        if not addresses:
            raise BatchError(f"No valid addresses found in {input_file}")
        
        # Open wallet
        wallet = WalletDB(wallet_path)
        
        # Import addresses
        imported_addresses = []
        
        for i, addr_data in enumerate(addresses):
            try:
                # Get address and label
                if isinstance(addr_data, dict):
                    address = addr_data.get('address')
                    label = addr_data.get('label') or f"{label_prefix}{i+1}"
                else:
                    address = addr_data
                    label = f"{label_prefix}{i+1}"
                
                # Validate address
                if not is_valid_address(address):
                    logger.warning(f"Invalid address: {address}")
                    continue
                
                # Import address
                # TODO: Implement watch-only address import in WalletDB
                # For now, just add to list
                imported_addresses.append(address)
                
                logger.info(f"Imported address {i+1}/{len(addresses)}: {address}")
            except Exception as e:
                logger.error(f"Failed to import address {i+1}/{len(addresses)}: {e}")
        
        return imported_addresses
    except Exception as e:
        raise BatchError(f"Failed to import addresses: {e}")

def read_addresses_from_file(input_file: str) -> List[Union[str, Dict[str, str]]]:
    """
    Read addresses from a file.
    
    The file can be in CSV, JSON, or plain text format.
    
    Args:
        input_file: Path to the input file
        
    Returns:
        List of addresses (strings or dictionaries)
        
    Raises:
        BatchError: If the addresses cannot be read
    """
    try:
        # Determine file format from extension
        _, ext = os.path.splitext(input_file)
        ext = ext.lower()
        
        # Read addresses
        if ext == '.json':
            return read_addresses_from_json(input_file)
        elif ext == '.csv':
            return read_addresses_from_csv(input_file)
        else:
            return read_addresses_from_text(input_file)
    except Exception as e:
        raise BatchError(f"Failed to read addresses from {input_file}: {e}")

def read_addresses_from_json(input_file: str) -> List[Dict[str, str]]:
    """
    Read addresses from a JSON file.
    
    Args:
        input_file: Path to the JSON file
        
    Returns:
        List of address dictionaries
        
    Raises:
        BatchError: If the addresses cannot be read
    """
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON formats
        if isinstance(data, list):
            # List of addresses
            return data
        elif isinstance(data, dict):
            # Dictionary with addresses
            if 'addresses' in data:
                return data['addresses']
            else:
                # Try to convert to list
                return [data]
        else:
            raise BatchError(f"Invalid JSON format in {input_file}")
    except json.JSONDecodeError:
        raise BatchError(f"Invalid JSON in {input_file}")
    except Exception as e:
        raise BatchError(f"Failed to read JSON from {input_file}: {e}")

def read_addresses_from_csv(input_file: str) -> List[Dict[str, str]]:
    """
    Read addresses from a CSV file.
    
    Args:
        input_file: Path to the CSV file
        
    Returns:
        List of address dictionaries
        
    Raises:
        BatchError: If the addresses cannot be read
    """
    try:
        addresses = []
        
        with open(input_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Check for required fields
                if 'address' in row:
                    addresses.append(row)
                else:
                    logger.warning(f"Skipping row without address: {row}")
        
        return addresses
    except Exception as e:
        raise BatchError(f"Failed to read CSV from {input_file}: {e}")

def read_addresses_from_text(input_file: str) -> List[str]:
    """
    Read addresses from a text file.
    
    Args:
        input_file: Path to the text file
        
    Returns:
        List of address strings
        
    Raises:
        BatchError: If the addresses cannot be read
    """
    try:
        addresses = []
        
        with open(input_file, 'r') as f:
            for line in f:
                # Strip whitespace and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Extract address (first word in line)
                address = line.split()[0]
                
                # Validate address
                if is_valid_address(address):
                    addresses.append(address)
                else:
                    logger.warning(f"Invalid address: {address}")
        
        return addresses
    except Exception as e:
        raise BatchError(f"Failed to read text from {input_file}: {e}")
