"""
Command-line argument parser for PyWallet.

This module provides a command-line argument parser for PyWallet.
"""

import argparse
import sys
from typing import Dict, List, Any, Optional, Tuple

from pywallet_refactored import __version__

def create_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.

    Returns:
        ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="PyWallet - Bitcoin Wallet Tool",
        epilog="Use 'pywallet command --help' for more information on a command."
    )

    # Version
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'PyWallet {__version__}'
    )

    # Debug mode
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    # Wallet options
    wallet_group = parser.add_argument_group('Wallet options')
    wallet_group.add_argument(
        '--wallet', '-w',
        help='Path to wallet.dat file'
    )
    wallet_group.add_argument(
        '--passphrase', '-p',
        help='Wallet passphrase for encrypted wallets'
    )

    # Commands
    subparsers = parser.add_subparsers(
        title='Commands',
        dest='command',
        help='Command to execute'
    )

    # Dump wallet command
    dump_parser = subparsers.add_parser(
        'dump',
        help='Dump wallet data to a JSON file'
    )
    dump_parser.add_argument(
        '--output', '-o',
        help='Output file (defaults to wallet.json)'
    )
    dump_parser.add_argument(
        '--no-private',
        action='store_true',
        help='Do not include private keys in the dump'
    )

    # Import key command
    import_parser = subparsers.add_parser(
        'import',
        help='Import a private key into the wallet'
    )
    import_parser.add_argument(
        'key',
        help='WIF encoded private key'
    )
    import_parser.add_argument(
        '--label', '-l',
        help='Label for the key'
    )

    # Create wallet command
    create_parser = subparsers.add_parser(
        'create',
        help='Create a new wallet'
    )
    create_parser.add_argument(
        '--output', '-o',
        help='Output file (defaults to wallet.dat)'
    )
    create_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite existing wallet'
    )
    create_parser.add_argument(
        '--generate-key', '-g',
        action='store_true',
        help='Generate an initial key'
    )
    create_parser.add_argument(
        '--save-key', '-s',
        action='store_true',
        help='Save generated key to a file'
    )

    # Backup wallet command
    backup_parser = subparsers.add_parser(
        'backup',
        help='Create a backup of the wallet'
    )
    backup_parser.add_argument(
        '--output', '-o',
        help='Output file (defaults to wallet.dat.bak)'
    )

    # Watch-only wallet command
    watchonly_parser = subparsers.add_parser(
        'watchonly',
        help='Create a watch-only wallet from an existing wallet'
    )
    watchonly_parser.add_argument(
        '--wallet', '-w',
        help='Source wallet file'
    )
    watchonly_parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output file for watch-only wallet'
    )

    # Generate key command
    genkey_parser = subparsers.add_parser(
        'genkey',
        help='Generate a new key pair'
    )
    genkey_parser.add_argument(
        '--uncompressed', '-u',
        action='store_true',
        help='Generate uncompressed key'
    )
    genkey_parser.add_argument(
        '--save', '-s',
        action='store_true',
        help='Save key to a file'
    )

    # Check address command
    checkaddr_parser = subparsers.add_parser(
        'checkaddr',
        help='Check if an address is valid'
    )
    checkaddr_parser.add_argument(
        'address',
        help='Bitcoin address to check'
    )

    # Check key command
    checkkey_parser = subparsers.add_parser(
        'checkkey',
        help='Check if a private key is valid'
    )
    checkkey_parser.add_argument(
        'key',
        help='WIF encoded private key to check'
    )

    # Balance command
    balance_parser = subparsers.add_parser(
        'balance',
        help='Check balance of Bitcoin addresses'
    )
    balance_parser.add_argument(
        'addresses',
        nargs='+',
        help='Bitcoin addresses to check'
    )
    balance_parser.add_argument(
        '--provider', '-p',
        choices=['blockchain.info', 'blockcypher'],
        default='blockchain.info',
        help='Blockchain API provider to use'
    )

    # Transaction history command
    txhistory_parser = subparsers.add_parser(
        'txhistory',
        help='Get transaction history for Bitcoin addresses'
    )
    txhistory_parser.add_argument(
        'address',
        help='Bitcoin address to check'
    )
    txhistory_parser.add_argument(
        '--output', '-o',
        help='Output file for transaction history'
    )
    txhistory_parser.add_argument(
        '--provider', '-p',
        choices=['blockchain.info', 'blockcypher'],
        default='blockchain.info',
        help='Blockchain API provider to use'
    )

    # Batch operations commands
    batch_parser = subparsers.add_parser(
        'batch',
        help='Batch operations for keys and addresses'
    )
    batch_subparsers = batch_parser.add_subparsers(
        dest='batch_command',
        help='Batch command to execute'
    )

    # Batch import keys command
    batch_import_parser = batch_subparsers.add_parser(
        'import',
        help='Import keys from a file'
    )
    batch_import_parser.add_argument(
        '--wallet', '-w',
        help='Path to wallet file'
    )
    batch_import_parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input file with keys'
    )
    batch_import_parser.add_argument(
        '--label', '-l',
        default='Imported',
        help='Label prefix for imported keys'
    )

    # Batch export keys command
    batch_export_parser = batch_subparsers.add_parser(
        'export',
        help='Export keys to a file'
    )
    batch_export_parser.add_argument(
        '--wallet', '-w',
        help='Path to wallet file'
    )
    batch_export_parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output file for keys'
    )
    batch_export_parser.add_argument(
        '--no-private',
        action='store_true',
        help='Do not include private keys in export'
    )
    batch_export_parser.add_argument(
        '--passphrase', '-p',
        help='Wallet passphrase for encrypted wallets'
    )

    # Batch generate keys command
    batch_generate_parser = batch_subparsers.add_parser(
        'generate',
        help='Generate multiple key pairs'
    )
    batch_generate_parser.add_argument(
        'count',
        type=int,
        help='Number of key pairs to generate'
    )
    batch_generate_parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output file for generated keys'
    )
    batch_generate_parser.add_argument(
        '--uncompressed', '-u',
        action='store_true',
        help='Generate uncompressed keys'
    )

    # Recovery commands
    recovery_parser = subparsers.add_parser(
        'recover',
        help='Recover keys from a wallet or device'
    )
    recovery_parser.add_argument(
        '--file', '-f',
        help='File to scan for keys'
    )
    recovery_parser.add_argument(
        '--device', '-d',
        help='Device to scan for keys'
    )
    recovery_parser.add_argument(
        '--start', '-s',
        type=int,
        default=0,
        help='Start offset for scanning'
    )
    recovery_parser.add_argument(
        '--size', '-z',
        type=int,
        help='Maximum size to scan'
    )
    recovery_parser.add_argument(
        '--output', '-o',
        help='Output file for recovered keys'
    )
    recovery_parser.add_argument(
        '--passphrase', '-p',
        help='Passphrase for encrypted keys'
    )

    # Legacy options (for compatibility with old pywallet.py)
    legacy_group = parser.add_argument_group('Legacy options (deprecated)')
    legacy_group.add_argument(
        '--dumpwallet',
        nargs='?',
        const=True,
        help='Dump wallet data to a JSON file'
    )
    legacy_group.add_argument(
        '--importprivkey',
        help='Import a private key into the wallet'
    )
    legacy_group.add_argument(
        '--createwallet',
        nargs='?',
        const=True,
        help='Create a new wallet'
    )
    legacy_group.add_argument(
        '--backupwallet',
        nargs='?',
        const=True,
        help='Create a backup of the wallet'
    )
    legacy_group.add_argument(
        '--dumpwithbalance',
        action='store_true',
        help='Include balance information in wallet dump'
    )
    legacy_group.add_argument(
        '--label',
        help='Label for imported key'
    )

    return parser

def parse_args(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Dictionary of parsed arguments
    """
    parser = create_parser()

    if args is None:
        args = sys.argv[1:]

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Convert to dictionary
    args_dict = vars(parsed_args)

    # Handle legacy options
    if args_dict.get('dumpwallet'):
        args_dict['command'] = 'dump'
        args_dict['output'] = args_dict['dumpwallet'] if args_dict['dumpwallet'] is not True else None

    if args_dict.get('importprivkey'):
        args_dict['command'] = 'import'
        args_dict['key'] = args_dict['importprivkey']

    if args_dict.get('createwallet'):
        args_dict['command'] = 'create'
        args_dict['output'] = args_dict['createwallet'] if args_dict['createwallet'] is not True else None

    if args_dict.get('backupwallet'):
        args_dict['command'] = 'backup'
        args_dict['output'] = args_dict['backupwallet'] if args_dict['backupwallet'] is not True else None

    return args_dict
