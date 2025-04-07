"""
Batch command handlers for PyWallet.

This module provides command handlers for batch operations.
"""

from typing import Dict, Any

from pywallet_refactored.logger import logger
from pywallet_refactored.config import config
from pywallet_refactored.batch import (
    import_keys_from_file, export_keys_to_file, generate_key_batch, save_key_batch,
    BatchError
)

def batch_import_keys(args: Dict[str, Any]) -> int:
    """
    Import keys from a file.
    
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
        
        # Get input file
        input_file = args.get('input')
        if not input_file:
            logger.error("Input file is required")
            return 1
        
        # Get label prefix
        label_prefix = args.get('label', 'Imported')
        
        # Import keys
        imported_addresses = import_keys_from_file(wallet_path, input_file, label_prefix)
        
        if not imported_addresses:
            logger.warning("No keys were imported")
            return 1
        
        logger.info(f"Successfully imported {len(imported_addresses)} keys")
        return 0
    except BatchError as e:
        logger.error(f"Failed to import keys: {e}")
        return 1
    except Exception as e:
        logger.error(f"Failed to import keys: {e}")
        return 1

def batch_export_keys(args: Dict[str, Any]) -> int:
    """
    Export keys to a file.
    
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
        output_file = args.get('output')
        if not output_file:
            logger.error("Output file is required")
            return 1
        
        # Get options
        include_private = not args.get('no_private', False)
        passphrase = args.get('passphrase', '')
        
        # Export keys
        num_keys = export_keys_to_file(wallet_path, output_file, include_private, passphrase)
        
        if num_keys == 0:
            logger.warning("No keys were exported")
            return 1
        
        logger.info(f"Successfully exported {num_keys} keys to {output_file}")
        return 0
    except BatchError as e:
        logger.error(f"Failed to export keys: {e}")
        return 1
    except Exception as e:
        logger.error(f"Failed to export keys: {e}")
        return 1

def batch_generate_keys(args: Dict[str, Any]) -> int:
    """
    Generate multiple key pairs.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Get count
        count = args.get('count')
        if not count or count <= 0:
            logger.error("Count must be a positive integer")
            return 1
        
        # Get output file
        output_file = args.get('output')
        if not output_file:
            logger.error("Output file is required")
            return 1
        
        # Get options
        compressed = not args.get('uncompressed', False)
        
        # Generate keys
        logger.info(f"Generating {count} key pairs...")
        keys = generate_key_batch(count, compressed)
        
        if not keys:
            logger.warning("No keys were generated")
            return 1
        
        # Save keys
        save_key_batch(keys, output_file)
        
        logger.info(f"Successfully generated and saved {len(keys)} keys to {output_file}")
        return 0
    except BatchError as e:
        logger.error(f"Failed to generate keys: {e}")
        return 1
    except Exception as e:
        logger.error(f"Failed to generate keys: {e}")
        return 1

def handle_batch_command(args: Dict[str, Any]) -> int:
    """
    Handle batch commands.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    batch_command = args.get('batch_command')
    
    if batch_command == 'import':
        return batch_import_keys(args)
    elif batch_command == 'export':
        return batch_export_keys(args)
    elif batch_command == 'generate':
        return batch_generate_keys(args)
    else:
        logger.error(f"Unknown batch command: {batch_command}")
        return 1
