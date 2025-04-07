"""
Wallet database handling.

This module provides functions for reading and writing Bitcoin wallet.dat files.
"""

import os
import struct
import hashlib
import binascii
import json
from typing import Dict, List, Any, Optional, Tuple, Callable, Union, BinaryIO

try:
    from bsddb3.db import *
except ImportError:
    try:
        from bsddb.db import *
    except ImportError:
        # Define constants for compatibility
        DB_CREATE = 1
        DB_INIT_LOCK = 2
        DB_INIT_LOG = 4
        DB_INIT_MPOOL = 8
        DB_INIT_TXN = 16
        DB_THREAD = 32
        DB_RECOVER = 64
        DB_RDONLY = 128
        DB_BTREE = 256
        
        class DBError(Exception):
            """Berkeley DB error."""
            pass
        
        class DB:
            """Dummy DB class."""
            def __init__(self, *args):
                pass
            
            def open(self, *args, **kwargs):
                raise DBError("bsddb module not available")
        
        class DBEnv:
            """Dummy DBEnv class."""
            def __init__(self, *args):
                pass
            
            def open(self, *args, **kwargs):
                raise DBError("bsddb module not available")

from pywallet_refactored.logger import logger
from pywallet_refactored.config import config
from pywallet_refactored.utils.common import bytes_to_hex, hex_to_bytes

class WalletDBError(Exception):
    """Exception raised for wallet database errors."""
    pass

class WalletDB:
    """Bitcoin wallet database handler."""
    
    def __init__(self, wallet_path: Optional[str] = None):
        """
        Initialize wallet database handler.
        
        Args:
            wallet_path: Path to wallet.dat file (defaults to configured path)
        """
        self.wallet_path = wallet_path or config.determine_wallet_path()
        self.db_env = None
        self.db = None
        self.json_db = {
            'keys': [],
            'pool': [],
            'tx': [],
            'names': [],
            'ckey': [],
            'mkey': []
        }
    
    def open(self, read_only: bool = True) -> None:
        """
        Open the wallet database.
        
        Args:
            read_only: Whether to open in read-only mode
            
        Raises:
            WalletDBError: If the wallet cannot be opened
        """
        try:
            # Get wallet directory and filename
            wallet_dir = os.path.dirname(self.wallet_path)
            wallet_file = os.path.basename(self.wallet_path)
            
            # Create DB environment
            self.db_env = DBEnv(0)
            flags = (DB_CREATE | DB_INIT_LOCK | DB_INIT_LOG | DB_INIT_MPOOL | 
                     DB_INIT_TXN | DB_THREAD | DB_RECOVER)
            self.db_env.open(wallet_dir, flags)
            
            # Open wallet
            self.db = DB(self.db_env)
            flags = DB_THREAD | (DB_RDONLY if read_only else DB_CREATE)
            self.db.open(wallet_file, "main", DB_BTREE, flags)
            
            logger.info(f"Opened wallet database: {self.wallet_path}")
        except DBError as e:
            raise WalletDBError(f"Failed to open wallet database: {e}")
    
    def close(self) -> None:
        """Close the wallet database."""
        if self.db:
            self.db.close()
            self.db = None
        
        if self.db_env:
            self.db_env.close()
            self.db_env = None
        
        logger.info("Closed wallet database")
    
    def read_wallet(self, passphrase: str = "") -> Dict[str, Any]:
        """
        Read wallet data.
        
        Args:
            passphrase: Wallet passphrase for decrypting encrypted keys
            
        Returns:
            Dictionary with wallet data
            
        Raises:
            WalletDBError: If the wallet cannot be read
        """
        if not self.db:
            self.open()
        
        try:
            # Reset JSON DB
            self.json_db = {
                'keys': [],
                'pool': [],
                'tx': [],
                'names': [],
                'ckey': [],
                'mkey': []
            }
            
            # Read wallet records
            self._read_records(passphrase)
            
            # Process encrypted keys if passphrase is provided
            if passphrase and self.json_db['mkey']:
                self._decrypt_keys(passphrase)
            
            return self.json_db
        except Exception as e:
            raise WalletDBError(f"Failed to read wallet: {e}")
    
    def _read_records(self, passphrase: str) -> None:
        """
        Read records from the wallet database.
        
        Args:
            passphrase: Wallet passphrase
        """
        cursor = self.db.cursor()
        while True:
            try:
                record = cursor.next()
            except DBNotFoundError:
                break
            
            if not record:
                continue
            
            key, value = record
            
            # Parse record based on type
            if key[0:4] == b"\x04mkey":
                self._parse_master_key(key, value)
            elif key[0:4] == b"\x04ckey":
                self._parse_crypto_key(key, value)
            elif key[0:4] == b"\x04key":
                self._parse_key(key, value)
            elif key[0:4] == b"\x04pool":
                self._parse_pool(key, value)
            elif key[0:4] == b"\x04name":
                self._parse_name(key, value)
            elif key[0:4] == b"\x04tx":
                self._parse_transaction(key, value)
    
    def _parse_master_key(self, key: bytes, value: bytes) -> None:
        """
        Parse a master key record.
        
        Args:
            key: Record key
            value: Record value
        """
        # Extract master key data
        # Format: [encrypted_key][salt][iterations][method][id]
        encrypted_key = value[8:72]
        salt = value[72:80]
        iterations = struct.unpack("<I", value[80:84])[0]
        method = struct.unpack("<I", value[84:88])[0]
        
        self.json_db['mkey'].append({
            'encrypted_key': bytes_to_hex(encrypted_key),
            'salt': bytes_to_hex(salt),
            'iterations': iterations,
            'method': method
        })
        
        logger.debug(f"Found master key: iterations={iterations}, method={method}")
    
    def _parse_crypto_key(self, key: bytes, value: bytes) -> None:
        """
        Parse an encrypted key record.
        
        Args:
            key: Record key
            value: Record value
        """
        # Extract public key and encrypted private key
        public_key = value[5:74]
        encrypted_private_key = value[74:]
        
        # Determine if key is compressed
        compressed = public_key[0] != 4
        
        self.json_db['ckey'].append({
            'public_key': bytes_to_hex(public_key),
            'encrypted_private_key': bytes_to_hex(encrypted_private_key),
            'compressed': compressed
        })
        
        logger.debug(f"Found encrypted key: compressed={compressed}")
    
    def _parse_key(self, key: bytes, value: bytes) -> None:
        """
        Parse a key record.
        
        Args:
            key: Record key
            value: Record value
        """
        # Extract public key and private key
        public_key = key[4:]
        private_key = value[8:72]
        
        # Determine if key is compressed
        compressed = public_key[0] != 4
        
        from pywallet_refactored.crypto.keys import public_key_to_address, private_key_to_wif
        
        # Get address and WIF
        address = public_key_to_address(public_key)
        wif = private_key_to_wif(private_key, compressed)
        
        self.json_db['keys'].append({
            'public_key': bytes_to_hex(public_key),
            'private_key': bytes_to_hex(private_key),
            'address': address,
            'wif': wif,
            'compressed': compressed
        })
        
        logger.debug(f"Found key: address={address}, compressed={compressed}")
    
    def _parse_pool(self, key: bytes, value: bytes) -> None:
        """
        Parse a pool record.
        
        Args:
            key: Record key
            value: Record value
        """
        # Extract pool data
        pool_index = struct.unpack("<I", key[4:8])[0]
        pool_version = struct.unpack("<I", value[0:4])[0]
        pool_time = struct.unpack("<I", value[4:8])[0]
        public_key = value[8:8+65]
        
        self.json_db['pool'].append({
            'index': pool_index,
            'version': pool_version,
            'time': pool_time,
            'public_key': bytes_to_hex(public_key)
        })
        
        logger.debug(f"Found pool entry: index={pool_index}, time={pool_time}")
    
    def _parse_name(self, key: bytes, value: bytes) -> None:
        """
        Parse a name record.
        
        Args:
            key: Record key
            value: Record value
        """
        # Extract name data
        name = key[4:]
        address = value
        
        try:
            name_str = name.decode('utf-8')
            address_str = address.decode('utf-8')
            
            self.json_db['names'].append({
                'name': name_str,
                'address': address_str
            })
            
            logger.debug(f"Found name: {name_str} -> {address_str}")
        except UnicodeDecodeError:
            logger.warning(f"Could not decode name record: {bytes_to_hex(name)} -> {bytes_to_hex(address)}")
    
    def _parse_transaction(self, key: bytes, value: bytes) -> None:
        """
        Parse a transaction record.
        
        Args:
            key: Record key
            value: Record value
        """
        # Extract transaction hash
        tx_hash = bytes_to_hex(key[4:])
        
        # Add to transactions list
        self.json_db['tx'].append({
            'hash': tx_hash,
            'data': bytes_to_hex(value)
        })
        
        logger.debug(f"Found transaction: {tx_hash}")
    
    def _decrypt_keys(self, passphrase: str) -> None:
        """
        Decrypt encrypted keys using the provided passphrase.
        
        Args:
            passphrase: Wallet passphrase
        """
        if not self.json_db['mkey']:
            logger.warning("No master key found, cannot decrypt keys")
            return
        
        # Get master key
        mkey = self.json_db['mkey'][0]
        
        # Derive key from passphrase
        from pywallet_refactored.crypto.aes import derive_key, decrypt_aes
        
        derived_key = derive_key(
            passphrase.encode('utf-8'),
            hex_to_bytes(mkey['salt']),
            mkey['iterations'],
            32  # AES-256 key size
        )
        
        # Try to decrypt master key
        try:
            decrypted_master_key = decrypt_aes(
                hex_to_bytes(mkey['encrypted_key']),
                derived_key
            )
            
            logger.info("Successfully decrypted master key")
        except Exception as e:
            logger.error(f"Failed to decrypt master key: {e}")
            return
        
        # Decrypt each encrypted key
        for ckey in self.json_db['ckey']:
            try:
                # Decrypt private key
                encrypted_private_key = hex_to_bytes(ckey['encrypted_private_key'])
                private_key = decrypt_aes(encrypted_private_key, decrypted_master_key)
                
                # Get public key
                public_key = hex_to_bytes(ckey['public_key'])
                
                from pywallet_refactored.crypto.keys import public_key_to_address, private_key_to_wif
                
                # Get address and WIF
                address = public_key_to_address(public_key)
                wif = private_key_to_wif(private_key, ckey['compressed'])
                
                # Add to keys list
                self.json_db['keys'].append({
                    'public_key': ckey['public_key'],
                    'private_key': bytes_to_hex(private_key),
                    'address': address,
                    'wif': wif,
                    'compressed': ckey['compressed']
                })
                
                logger.debug(f"Decrypted key: address={address}")
            except Exception as e:
                logger.error(f"Failed to decrypt key: {e}")
    
    def dump_wallet(self, output_file: str, include_private: bool = True) -> None:
        """
        Dump wallet data to a JSON file.
        
        Args:
            output_file: Path to output file
            include_private: Whether to include private keys
            
        Raises:
            WalletDBError: If the wallet cannot be dumped
        """
        try:
            # Read wallet if not already read
            if not self.json_db['keys'] and not self.json_db['ckey']:
                self.read_wallet()
            
            # Create a copy of the wallet data
            wallet_data = {
                'keys': [],
                'transactions': len(self.json_db['tx']),
                'names': self.json_db['names'],
                'encrypted': bool(self.json_db['ckey'])
            }
            
            # Add keys
            for key in self.json_db['keys']:
                key_data = {
                    'address': key['address'],
                    'compressed': key['compressed']
                }
                
                if include_private:
                    key_data['wif'] = key['wif']
                
                wallet_data['keys'].append(key_data)
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(wallet_data, f, indent=4)
            
            logger.info(f"Dumped wallet to {output_file}")
        except Exception as e:
            raise WalletDBError(f"Failed to dump wallet: {e}")
    
    def import_key(self, wif: str, label: str = "") -> str:
        """
        Import a private key into the wallet.
        
        Args:
            wif: WIF encoded private key
            label: Label for the key
            
        Returns:
            Bitcoin address for the imported key
            
        Raises:
            WalletDBError: If the key cannot be imported
        """
        try:
            from pywallet_refactored.crypto.keys import wif_to_private_key, private_key_to_public_key, public_key_to_address
            
            # Decode WIF
            private_key, compressed = wif_to_private_key(wif)
            
            # Generate public key
            public_key = private_key_to_public_key(private_key, compressed)
            
            # Generate address
            address = public_key_to_address(public_key)
            
            # Open wallet in write mode
            if not self.db or self.db.get_open_flags() & DB_RDONLY:
                self.close()
                self.open(read_only=False)
            
            # Check if key already exists
            cursor = self.db.cursor()
            while True:
                try:
                    record = cursor.next()
                except DBNotFoundError:
                    break
                
                if not record:
                    continue
                
                key, value = record
                
                if key[0:4] == b"\x04key" and key[4:] == public_key:
                    logger.warning(f"Key already exists in wallet: {address}")
                    return address
            
            # Add key to wallet
            key_record = b"\x04key" + public_key
            value_record = struct.pack("<I", 1) + struct.pack("<I", 1) + private_key
            
            self.db.put(key_record, value_record)
            
            # Add name record if label is provided
            if label:
                name_record = b"\x04name" + label.encode('utf-8')
                self.db.put(name_record, address.encode('utf-8'))
            
            logger.info(f"Imported key: {address}")
            return address
        except Exception as e:
            raise WalletDBError(f"Failed to import key: {e}")
    
    def create_new_wallet(self, wallet_path: Optional[str] = None) -> None:
        """
        Create a new empty wallet.
        
        Args:
            wallet_path: Path to new wallet file (defaults to configured path)
            
        Raises:
            WalletDBError: If the wallet cannot be created
        """
        try:
            # Set wallet path
            if wallet_path:
                self.wallet_path = wallet_path
            
            # Get wallet directory and filename
            wallet_dir = os.path.dirname(self.wallet_path)
            wallet_file = os.path.basename(self.wallet_path)
            
            # Create directory if it doesn't exist
            os.makedirs(wallet_dir, exist_ok=True)
            
            # Create DB environment
            self.db_env = DBEnv(0)
            flags = (DB_CREATE | DB_INIT_LOCK | DB_INIT_LOG | DB_INIT_MPOOL | 
                     DB_INIT_TXN | DB_THREAD | DB_RECOVER)
            self.db_env.open(wallet_dir, flags)
            
            # Create wallet
            self.db = DB(self.db_env)
            self.db.open(wallet_file, "main", DB_BTREE, DB_CREATE)
            
            # Add version record
            self.db.put(b"\x04version", struct.pack("<I", 1))
            
            logger.info(f"Created new wallet: {self.wallet_path}")
        except Exception as e:
            raise WalletDBError(f"Failed to create wallet: {e}")
    
    def create_backup(self, backup_path: str) -> None:
        """
        Create a backup of the wallet.
        
        Args:
            backup_path: Path to backup file
            
        Raises:
            WalletDBError: If the backup cannot be created
        """
        try:
            # Open wallet if not already open
            if not self.db:
                self.open()
            
            # Create backup directory if it doesn't exist
            backup_dir = os.path.dirname(backup_path)
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create new DB
            backup_env = DBEnv(0)
            flags = (DB_CREATE | DB_INIT_LOCK | DB_INIT_LOG | DB_INIT_MPOOL | 
                     DB_INIT_TXN | DB_THREAD | DB_RECOVER)
            backup_env.open(backup_dir, flags)
            
            backup_db = DB(backup_env)
            backup_db.open(os.path.basename(backup_path), "main", DB_BTREE, DB_CREATE)
            
            # Copy records
            cursor = self.db.cursor()
            while True:
                try:
                    record = cursor.next()
                except DBNotFoundError:
                    break
                
                if not record:
                    continue
                
                key, value = record
                backup_db.put(key, value)
            
            # Close backup
            backup_db.close()
            backup_env.close()
            
            logger.info(f"Created wallet backup: {backup_path}")
        except Exception as e:
            raise WalletDBError(f"Failed to create backup: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
