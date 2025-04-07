"""
Command-line interface commands for PyWallet.

This module provides command-line interface commands for PyWallet.
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Callable, Union

from pywallet_refactored.logger import logger
from pywallet_refactored.config import config
from pywallet_refactored.db.wallet import WalletDB, WalletDBError
from pywallet_refactored.crypto.keys import generate_key_pair, is_valid_address, is_valid_wif

def dump_wallet(args: Dict[str, Any]) -> int:
    """
    Dump wallet data to a JSON file.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Get wallet path
        wallet_path = args.get('wallet')
        if not wallet_path:
            wallet_path = config.determine_wallet_path()

        # Get output file
        output_file = args.get('dumpwallet')
        if output_file is True:  # Flag provided without value
            output_file = os.path.splitext(wallet_path)[0] + '.json'

        # Get passphrase
        passphrase = args.get('passphrase', '')

        # Open wallet
        with WalletDB(wallet_path) as wallet:
            # Read wallet
            wallet.read_wallet(passphrase)

            # Dump wallet
            wallet.dump_wallet(output_file, include_private=not args.get('no_private', False))

        logger.info(f"Wallet dumped to {output_file}")
        return 0
    except WalletDBError as e:
        logger.error(f"Failed to dump wallet: {e}")
        return 1

def import_key(args: Dict[str, Any]) -> int:
    """
    Import a private key into the wallet.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Get wallet path
        wallet_path = args.get('wallet')
        if not wallet_path:
            wallet_path = config.determine_wallet_path()

        # Get private key
        private_key = args.get('importprivkey')
        if not private_key or not is_valid_wif(private_key):
            logger.error("Invalid private key")
            return 1

        # Get label
        label = args.get('label', '')

        # Open wallet
        with WalletDB(wallet_path) as wallet:
            # Import key
            address = wallet.import_key(private_key, label)

        logger.info(f"Imported key with address: {address}")
        return 0
    except WalletDBError as e:
        logger.error(f"Failed to import key: {e}")
        return 1

def create_wallet(args: Dict[str, Any]) -> int:
    """
    Create a new wallet.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Get wallet path
        wallet_path = args.get('createwallet')
        if wallet_path is True:  # Flag provided without value
            wallet_path = config.determine_wallet_path()

        # Check if wallet already exists
        if os.path.exists(wallet_path):
            if not args.get('force', False):
                logger.error(f"Wallet already exists: {wallet_path}")
                return 1

            # Backup existing wallet
            backup_path = wallet_path + '.bak.' + str(int(time.time()))
            os.rename(wallet_path, backup_path)
            logger.info(f"Existing wallet backed up to {backup_path}")

        # Create wallet
        wallet = WalletDB(wallet_path)
        wallet.create_new_wallet()

        # Generate initial key if requested
        if args.get('generate_key', False):
            key_pair = generate_key_pair()
            wallet.import_key(key_pair['wif'], 'Initial key')

            logger.info(f"Generated initial key with address: {key_pair['address']}")

            # Save key to file if requested
            if args.get('save_key', False):
                key_file = os.path.splitext(wallet_path)[0] + '.keys.json'
                with open(key_file, 'w') as f:
                    json.dump(key_pair, f, indent=4)

                logger.info(f"Saved key to {key_file}")

        logger.info(f"Created new wallet: {wallet_path}")
        return 0
    except WalletDBError as e:
        logger.error(f"Failed to create wallet: {e}")
        return 1

def backup_wallet(args: Dict[str, Any]) -> int:
    """
    Create a backup of the wallet.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Get wallet path
        wallet_path = args.get('wallet')
        if not wallet_path:
            wallet_path = config.determine_wallet_path()

        # Get backup path
        backup_path = args.get('backupwallet')
        if backup_path is True:  # Flag provided without value
            backup_path = wallet_path + '.bak.' + str(int(time.time()))

        # Create backup
        with WalletDB(wallet_path) as wallet:
            wallet.create_backup(backup_path)

        logger.info(f"Wallet backed up to {backup_path}")
        return 0
    except WalletDBError as e:
        logger.error(f"Failed to backup wallet: {e}")
        return 1

def generate_key(args: Dict[str, Any]) -> int:
    """
    Generate a new key pair.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Generate key
        compressed = not args.get('uncompressed', False)
        key_pair = generate_key_pair(compressed)

        # Print key information
        print(f"Address: {key_pair['address']}")
        print(f"Private key (WIF): {key_pair['wif']}")
        print(f"Private key (hex): {key_pair['private_key']}")
        print(f"Public key (hex): {key_pair['public_key']}")
        print(f"Compressed: {key_pair['compressed']}")

        # Save key to file if requested
        if args.get('save_key'):
            key_file = args.get('save_key')
            if key_file is True:  # Flag provided without value
                key_file = f"key_{key_pair['address']}.json"

            with open(key_file, 'w') as f:
                json.dump(key_pair, f, indent=4)

            logger.info(f"Saved key to {key_file}")

        return 0
    except Exception as e:
        logger.error(f"Failed to generate key: {e}")
        return 1

def check_address(args: Dict[str, Any]) -> int:
    """
    Check if an address is valid.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Get address
        address = args.get('checkaddress')

        # Check address
        valid = is_valid_address(address)

        if valid:
            print(f"Address {address} is valid")
        else:
            print(f"Address {address} is NOT valid")

        return 0 if valid else 1
    except Exception as e:
        logger.error(f"Failed to check address: {e}")
        return 1

def check_key(args: Dict[str, Any]) -> int:
    """
    Check if a private key is valid.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Get key
        key = args.get('checkkey')

        # Check key
        valid = is_valid_wif(key)

        if valid:
            print(f"Private key is valid")

            # Get address
            from pywallet_refactored.crypto.keys import wif_to_private_key, private_key_to_public_key, public_key_to_address

            private_key, compressed = wif_to_private_key(key)
            public_key = private_key_to_public_key(private_key, compressed)
            address = public_key_to_address(public_key)

            print(f"Address: {address}")
            print(f"Compressed: {compressed}")
        else:
            print(f"Private key is NOT valid")

        return 0 if valid else 1
    except Exception as e:
        logger.error(f"Failed to check key: {e}")
        return 1

def recover_keys(args: Dict[str, Any]) -> int:
    """
    Recover keys from a wallet or device.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        from pywallet_refactored.recovery import (
            scan_file, scan_device, recover_keys_from_passphrase,
            dump_keys_to_file, dump_encrypted_keys_to_file
        )

        # Get source
        file_path = args.get('file')
        device_path = args.get('device')

        if not file_path and not device_path:
            logger.error("Either --file or --device must be specified")
            return 1

        # Get scan parameters
        start_offset = args.get('start', 0)
        max_size = args.get('size')

        # Get output file
        output_file = args.get('output')
        if not output_file:
            if file_path:
                output_file = file_path + '.keys.json'
            else:
                output_file = 'recovered_keys.json'

        # Scan for keys
        if file_path:
            logger.info(f"Scanning file {file_path} from offset {start_offset}")
            results = scan_file(file_path, start_offset, max_size)
        else:
            logger.info(f"Scanning device {device_path} from offset {start_offset}")
            results = scan_device(device_path, start_offset, max_size)

        # Process results
        keys = results['keys']
        encrypted_keys = results['encrypted_keys']
        master_keys = results['master_keys']

        logger.info(f"Found {len(keys)} unencrypted keys")
        logger.info(f"Found {len(encrypted_keys)} encrypted keys")
        logger.info(f"Found {len(master_keys)} master keys")

        # Try to decrypt encrypted keys if passphrase is provided
        passphrase = args.get('passphrase')
        if passphrase and encrypted_keys and master_keys:
            logger.info(f"Attempting to decrypt {len(encrypted_keys)} keys with passphrase")

            recovered_keys = recover_keys_from_passphrase(
                encrypted_keys, master_keys[0], passphrase
            )

            keys.extend(recovered_keys)

            logger.info(f"Successfully decrypted {len(recovered_keys)} keys")

        # Dump keys to file
        if keys:
            dump_keys_to_file(keys, output_file)
        elif encrypted_keys and master_keys:
            # Dump encrypted keys if no keys were recovered
            dump_encrypted_keys_to_file(encrypted_keys, master_keys[0], output_file)
            logger.info(f"Dumped encrypted keys to {output_file}")
            logger.info(f"Use --passphrase to decrypt the keys")
        else:
            logger.warning(f"No keys found")

        return 0
    except Exception as e:
        logger.error(f"Failed to recover keys: {e}")
        return 1
