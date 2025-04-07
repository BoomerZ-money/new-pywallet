"""
Main entry point for PyWallet.

This module provides the main entry point for PyWallet.
"""

import sys
import os
from typing import List, Optional

from pywallet_refactored.logger import logger, setup_logging
from pywallet_refactored.config import config
from pywallet_refactored.cli.parser import parse_args
from pywallet_refactored.cli.commands import (
    dump_wallet, import_key, create_wallet, backup_wallet,
    generate_key, check_address, check_key, recover_keys
)

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for PyWallet.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Check Python version
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 9):
        print("Error: This script requires Python 3.9 or higher")
        print("Your Python version: {}.{}.{}".format(
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro
        ))
        return 1

    # Parse arguments
    args_dict = parse_args(args)

    # Set up logging
    if args_dict.get('debug'):
        setup_logging('DEBUG')

    # Set up configuration
    if args_dict.get('wallet'):
        config.set('wallet_dir', os.path.dirname(args_dict['wallet']))
        config.set('wallet_name', os.path.basename(args_dict['wallet']))

    # Execute command
    command = args_dict.get('command')

    if command == 'dump' or args_dict.get('dumpwallet'):
        return dump_wallet(args_dict)
    elif command == 'import' or args_dict.get('importprivkey'):
        return import_key(args_dict)
    elif command == 'create' or args_dict.get('createwallet'):
        return create_wallet(args_dict)
    elif command == 'backup' or args_dict.get('backupwallet'):
        return backup_wallet(args_dict)
    elif command == 'genkey':
        return generate_key(args_dict)
    elif command == 'checkaddr':
        return check_address(args_dict)
    elif command == 'checkkey':
        return check_key(args_dict)
    elif command == 'recover':
        return recover_keys(args_dict)
    else:
        logger.error("No command specified")
        return 1

if __name__ == "__main__":
    sys.exit(main())
