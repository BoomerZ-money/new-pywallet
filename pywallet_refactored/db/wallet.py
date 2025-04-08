"""
Wallet database handling.

This module provides functions for reading and writing Bitcoin wallet.dat files.
"""

import os
import struct
import hashlib
import binascii
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Callable, Union, BinaryIO

from pywallet_refactored.utils.datastream import BCDataStream
from pywallet_refactored.crypto.keys import (
    bytes_to_hex, private_key_to_wif, private_key_to_public_key,
    public_key_to_address, hash_160_to_address, hash160 as hash_160
)
from pywallet_refactored.logger import logger

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

        class DBNotFoundError(Exception):
            """Record not found error."""
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

def get_tmp_dir() -> str:
    """
    Get the path to the tmp directory for Berkeley DB temporary files.

    Returns:
        Path to the tmp directory
    """
    # Get the absolute path to the current file
    current_file = os.path.abspath(__file__)

    # Get the directory containing the current file (db directory)
    db_dir = os.path.dirname(current_file)

    # Get the parent directory (pywallet_refactored directory)
    pywallet_refactored_dir = os.path.dirname(db_dir)

    # Get the parent directory (project root directory)
    project_root = os.path.dirname(pywallet_refactored_dir)

    # Define the tmp directory path
    tmp_dir = os.path.join(project_root, 'tmp')

    # Create the directory if it doesn't exist
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        logger.debug(f"Using tmp directory: {tmp_dir}")
    except Exception as e:
        logger.error(f"Failed to create tmp directory {tmp_dir}: {e}")
        # Fallback to a temporary directory in the current directory
        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        logger.debug(f"Using fallback tmp directory: {tmp_dir}")

    return tmp_dir
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

        # Ensure tmp directory exists
        self.tmp_dir = get_tmp_dir()

    def open(self, read_only: bool = True) -> None:
        """
        Open the wallet database.

        Args:
            read_only: Whether to open in read-only mode

        Raises:
            WalletDBError: If the wallet cannot be opened
        """
        if self.db:
            return

        try:
            # Get wallet directory and filename
            wallet_dir = os.path.dirname(self.wallet_path)
            wallet_file = os.path.basename(self.wallet_path)

            # Check if wallet file exists
            if not os.path.exists(self.wallet_path):
                raise WalletDBError(f"Wallet file not found: {self.wallet_path}")

            # Get the wallet directory
            wallet_dir = os.path.dirname(self.wallet_path)
            if not wallet_dir:
                wallet_dir = '.'

            # Create DB environment in the wallet directory
            self.db_env = DBEnv(0)
            flags = (DB_CREATE | DB_INIT_LOCK | DB_INIT_LOG | DB_INIT_MPOOL |
                     DB_INIT_TXN | DB_THREAD | DB_RECOVER)

            # Use wallet directory for environment files
            logger.debug(f"Opening wallet using directory: {wallet_dir}")
            try:
                self.db_env.open(wallet_dir, flags)
            except DBError as e:
                logger.error(f"Failed to open DB environment: {e}")
                # Try creating the directory if it doesn't exist
                if not os.path.exists(wallet_dir):
                    os.makedirs(wallet_dir)
                    self.db_env.open(wallet_dir, flags)

            # Open wallet
            self.db = DB(self.db_env)
            flags = DB_THREAD | (DB_RDONLY if read_only else DB_CREATE)

            try:
                self.db.open(wallet_file, "main", DB_BTREE, flags)
                logger.info(f"Opened wallet database: {self.wallet_path}")
            except DBError as e:
                logger.error(f"Failed to open wallet: {e}")
                raise WalletDBError(f"Failed to open wallet database: {e}")

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
                'names': {},  # Use dictionary for names with address as key
                'ckey': [],
                'mkey': {},
                'version': 0,
                'defaultkey': '',
                'bestblock': '',
                'settings': {}
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
        start_time = time.time()
        # No timeout - read all records

        # Create data streams for parsing
        kds = BCDataStream()
        vds = BCDataStream()

        # Define helper functions for parsing transactions
        def parse_TxIn(vds):
            d = {}
            d['prevout_hash'] = binascii.hexlify(vds.read_bytes(32)).decode('utf-8')
            d['prevout_n'] = vds.read_uint32()
            d['scriptSig'] = binascii.hexlify(vds.read_bytes(vds.read_compact_size())).decode('utf-8')
            d['sequence'] = vds.read_uint32()
            return d

        def parse_TxOut(vds):
            d = {}
            d['value'] = vds.read_int64() / 1e8  # Convert satoshis to BTC
            d['scriptPubKey'] = binascii.hexlify(vds.read_bytes(vds.read_compact_size())).decode('utf-8')
            return d

        def parse_BlockLocator(vds):
            d = {'hashes': []}
            nHashes = vds.read_compact_size()
            for i in range(nHashes):
                d['hashes'].append(vds.read_bytes(32))
            return d

        # Get all items from the database
        cursor = self.db.cursor()
        record_count = 0
        key_count = 0
        tx_count = 0

        # First pass: read all records
        logger.info("Starting to read wallet records...")
        max_records = 10000  # Maximum number of records to read
        while True:
            try:
                record = cursor.next()
                record_count += 1
                if record_count % 100 == 0:
                    logger.info(f"Read {record_count} records so far...")

                # Check if we've reached the maximum number of records
                if record_count >= max_records:
                    logger.warning(f"Reached maximum number of records ({max_records}). Stopping record reading.")
                    break
            except DBNotFoundError:
                logger.info("Finished reading all records.")
                break

            if not record:
                continue

            key, value = record

            # Clear data streams
            kds.clear()
            vds.clear()

            # Write data to streams
            kds.write(key)
            vds.write(value)

            # Read type from key
            type_bytes = key[0:4]
            type_str = binascii.hexlify(type_bytes).decode('utf-8')
            logger.info(f"Record type: {type_str}, key length: {len(key)}, value length: {len(value)}")

            # Convert type bytes to string for easier comparison

            # Parse record based on type
            if type_str == "046d6b6579" or type_str.startswith("046d6b65"):  # "\x04mkey"
                # Master key
                nID = kds.read_bytes(4)[0]  # Read ID from key
                encrypted_key = vds.read_bytes(vds.read_compact_size())
                salt = vds.read_bytes(vds.read_compact_size())
                method = vds.read_uint32()
                iterations = vds.read_uint32()
                other_params = vds.read_bytes(vds.read_compact_size())

                self.json_db['mkey'] = {
                    'nID': nID,
                    'encrypted_key': binascii.hexlify(encrypted_key).decode('utf-8'),
                    'salt': binascii.hexlify(salt).decode('utf-8'),
                    'method': method,
                    'iterations': iterations,
                    'otherParams': binascii.hexlify(other_params).decode('utf-8') if other_params else ''
                }

                logger.debug(f"Found master key: iterations={iterations}, method={method}")

            elif type_str == "04636b6579" or type_str.startswith("04636b65"):  # "\x04ckey"
                # Encrypted key
                try:
                    # Skip the 'ckey' prefix in the key
                    kds.read_bytes(4)
                    # Read the public key from the key data
                    public_key = kds.read_bytes(kds.read_compact_size())
                    # Read the encrypted private key from the value
                    encrypted_private_key = vds.read_bytes(vds.read_compact_size())

                    # Determine if key is compressed
                    compressed = public_key[0] != 4

                    # Generate address from public key
                    address = public_key_to_address(binascii.hexlify(public_key))

                    self.json_db['ckey'].append({
                        'pubkey': binascii.hexlify(public_key).decode('utf-8'),
                        'encrypted_privkey': binascii.hexlify(encrypted_private_key).decode('utf-8'),
                        'compressed': compressed,
                        'addr': address,
                        'reserve': 1
                    })

                    key_count += 1
                    logger.debug(f"Found encrypted key: address={address}, compressed={compressed}")
                except Exception as e:
                    logger.warning(f"Failed to parse encrypted key: {e}")

            elif type_str == "046b6579" or type_str.startswith("046b65"):  # "\x04key"
                # Regular key
                public_key = kds.read_bytes(kds.read_compact_size())
                nVersion = vds.read_uint32()
                created_time = vds.read_uint32()
                private_key = vds.read_bytes(32)

                # Determine if key is compressed
                compressed = public_key[0] != 4

                # Generate address and WIF
                address = public_key_to_address(binascii.hexlify(public_key))
                wif = private_key_to_wif(private_key, compressed)

                self.json_db['keys'].append({
                    'pubkey': binascii.hexlify(public_key).decode('utf-8'),
                    'hexsec': binascii.hexlify(private_key).decode('utf-8'),
                    'sec': wif,
                    'created': created_time,
                    'compressed': compressed,
                    'addr': address,
                    'reserve': 0
                })

                key_count += 1
                logger.debug(f"Found key: address={address}, compressed={compressed}")

            elif type_str == "04706f6f6c" or type_str.startswith("04706f6f"):  # "\x04pool"
                # Key pool
                try:
                    n = kds.read_uint64()
                    nVersion = vds.read_uint32()
                    nTime = vds.read_uint32()

                    # Try to read the public key, but it might not be present in all pool entries
                    try:
                        public_key = vds.read_bytes(vds.read_compact_size())
                        public_key_hex = binascii.hexlify(public_key).decode('utf-8')
                    except Exception:
                        public_key_hex = ""

                    self.json_db['pool'].append({
                        'n': n,
                        'nVersion': nVersion,
                        'nTime': nTime,
                        'public_key': public_key_hex
                    })

                    logger.debug(f"Found pool key: n={n}, time={nTime}")
                except Exception as e:
                    logger.warning(f"Failed to parse pool entry: {e}")

            elif type_str == "046e616d65" or type_str.startswith("046e616d"):  # "\x04name"
                # Name record
                address_bytes = kds.read_bytes(kds.read_compact_size())
                name_bytes = vds.read_bytes(vds.read_compact_size())

                try:
                    address_str = public_key_to_address(binascii.hexlify(address_bytes))
                    name_str = name_bytes.decode('utf-8')

                    # Store as a dictionary with address as key
                    self.json_db['names'][address_str] = name_str

                    logger.debug(f"Found name: {name_str} -> {address_str}")
                except UnicodeDecodeError:
                    logger.warning(f"Could not decode name record: {binascii.hexlify(name_bytes)} -> {binascii.hexlify(address_bytes)}")

            elif type_str.startswith("0274"):  # Transaction
                try:
                    # Transaction
                    tx_hash = binascii.hexlify(key[4:]).decode('utf-8')

                    # For transactions, we'll just store the raw data for now
                    # This is a complex format that requires special handling
                    self.json_db['tx'].append({
                        'tx_id': tx_hash,
                        'txv': 1,  # Default version
                        'txk': 0,   # Default locktime
                        'txIn': [],
                        'txOut': []
                    })

                    tx_count += 1
                    logger.debug(f"Found transaction: hash={tx_hash}")
                except Exception as e:
                    logger.warning(f"Failed to parse transaction: {e}")

            elif type_str == "07766572" or type_str.startswith("0776657273"):  # "\x07version"
                # Wallet version
                version = vds.read_uint32()
                self.json_db['version'] = version
                logger.debug(f"Wallet version: {version}")

            elif type_str == "0a646566" or type_str.startswith("0a646566"):  # "\x0adefaultkey"
                # Default key
                key_data = vds.read_bytes(vds.read_compact_size())
                self.json_db['defaultkey'] = public_key_to_address(binascii.hexlify(key_data))
                logger.debug(f"Default key: {self.json_db['defaultkey']}")

            elif type_str == "09626573" or type_str.startswith("09626573"):  # "\x09bestblock"
                # Best block
                nVersion = vds.read_uint32()
                block_locator = parse_BlockLocator(vds)
                if 'hashes' in block_locator and len(block_locator['hashes']) > 0:
                    self.json_db['bestblock'] = binascii.hexlify(block_locator['hashes'][0][::-1]).decode('utf-8')  # Reverse for big-endian
                    logger.debug(f"Best block: {self.json_db['bestblock']}")

        logger.info(f"Read {record_count} wallet records ({key_count} keys, {tx_count} transactions) in {time.time() - start_time:.2f} seconds")

        # If we have crypto keys but no regular keys, the wallet is encrypted
        if self.json_db['ckey'] and not self.json_db['keys']:
            logger.info("Wallet is encrypted")

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

        # Generate address from public key
        from pywallet_refactored.crypto.keys import public_key_to_address
        address = public_key_to_address(bytes_to_hex(public_key))

        self.json_db['ckey'].append({
            'public_key': bytes_to_hex(public_key),
            'encrypted_private_key': bytes_to_hex(encrypted_private_key),
            'compressed': compressed,
            'address': address
        })

        logger.debug(f"Found encrypted key: address={address}, compressed={compressed}")

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

        # Add to transactions list - only store the hash for efficiency
        self.json_db['tx'].append({
            'hash': tx_hash
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

            # Use the tmp directory that was created in __init__
            tmp_dir = self.tmp_dir
            logger.debug(f"Creating new wallet using tmp directory: {tmp_dir}")

            # Create DB environment
            self.db_env = DBEnv(0)
            flags = (DB_CREATE | DB_INIT_LOCK | DB_INIT_LOG | DB_INIT_MPOOL |
                     DB_INIT_TXN | DB_THREAD | DB_RECOVER)
            self.db_env.open(tmp_dir, flags)

            # Create wallet
            self.db = DB(self.db_env)

            # Use the full path to the wallet file in the tmp directory
            try:
                self.db.open(wallet_file, "main", DB_BTREE, DB_CREATE)
            except DBError as e:
                # If opening with just the filename fails, try with the full path
                logger.debug(f"Failed to open wallet with filename only, trying with full path: {e}")
                self.db.open(self.wallet_path, "main", DB_BTREE, DB_CREATE)

            # Add version record
            self.db.put(b"\x04version", struct.pack("<I", 1))

            # Close the database to ensure all changes are written
            self.db.close()
            self.db_env.close()
            self.db = None
            self.db_env = None

            # Copy the wallet file from tmp directory to the specified location
            tmp_wallet_path = os.path.join(tmp_dir, wallet_file)
            if os.path.exists(tmp_wallet_path):
                try:
                    import shutil
                    shutil.copy2(tmp_wallet_path, self.wallet_path)
                    logger.debug(f"Copied wallet file from tmp directory to: {self.wallet_path}")
                except Exception as e:
                    logger.error(f"Failed to copy wallet file from tmp directory: {e}")

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

            # Use the tmp directory that was created in __init__
            tmp_dir = self.tmp_dir
            logger.debug(f"Creating backup using tmp directory: {tmp_dir}")

            # Create new DB
            backup_env = DBEnv(0)
            flags = (DB_CREATE | DB_INIT_LOCK | DB_INIT_LOG | DB_INIT_MPOOL |
                     DB_INIT_TXN | DB_THREAD | DB_RECOVER)
            backup_env.open(tmp_dir, flags)

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

    def create_watch_only(self, output_path: str) -> None:
        """
        Create a watch-only wallet from this wallet.

        A watch-only wallet contains public keys but no private keys,
        allowing monitoring of addresses without the ability to spend.

        Args:
            output_path: Path to the watch-only wallet file

        Raises:
            WalletDBError: If the watch-only wallet cannot be created
        """
        try:
            # Open wallet if not already open
            if not self.db:
                self.open()

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)

            # Use the tmp directory that was created in __init__
            tmp_dir = self.tmp_dir
            logger.debug(f"Creating watch-only wallet using tmp directory: {tmp_dir}")

            # Create new DB
            watch_env = DBEnv(0)
            flags = (DB_CREATE | DB_INIT_LOCK | DB_INIT_LOG | DB_INIT_MPOOL |
                     DB_INIT_TXN | DB_THREAD | DB_RECOVER)
            watch_env.open(tmp_dir, flags)

            watch_db = DB(watch_env)
            watch_db.open(os.path.basename(output_path), "main", DB_BTREE, DB_CREATE)

            # Copy non-private records
            cursor = self.db.cursor()
            while True:
                try:
                    record = cursor.next()
                except DBNotFoundError:
                    break

                if not record:
                    continue

                key, value = record

                # Skip private key records
                if key.startswith(b"\x04key"):
                    # Extract public key from private key record
                    public_key = key[4:]

                    # Create a dummy private key record with zeros
                    dummy_value = struct.pack("<I", 1) + struct.pack("<I", 1) + b"\x00" * 32

                    # Add public key record with dummy private key
                    watch_db.put(key, dummy_value)
                elif key.startswith(b"\x04ckey"):
                    # Skip encrypted private keys
                    continue
                elif key.startswith(b"\x04mkey"):
                    # Skip master keys
                    continue
                else:
                    # Copy all other records
                    watch_db.put(key, value)

            # Close watch-only wallet
            watch_db.close()
            watch_env.close()

            logger.info(f"Created watch-only wallet: {output_path}")
        except Exception as e:
            raise WalletDBError(f"Failed to create watch-only wallet: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
