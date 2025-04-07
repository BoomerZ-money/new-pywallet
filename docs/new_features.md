# New Features in PyWallet Refactored

This document provides detailed information about the new features added to the refactored PyWallet.

## Table of Contents

- [Balance Checking](#balance-checking)
- [Transaction History](#transaction-history)
- [Watch-Only Wallet Creation](#watch-only-wallet-creation)
- [Batch Operations](#batch-operations)

## Balance Checking

The balance checking feature allows you to check the balance of Bitcoin addresses using various blockchain API providers.

### Command-Line Usage

```bash
python -m pywallet_refactored balance <address1> [<address2> ...]
```

Options:
- `--provider`, `-p`: Blockchain API provider to use (choices: 'blockchain.info', 'blockcypher')

Example:
```bash
python -m pywallet_refactored balance 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2 --provider=blockcypher
```

### API Usage

```python
from pywallet_refactored.blockchain import get_balance
from pywallet_refactored.config import config

# Set blockchain provider (optional)
config.set('blockchain_provider', 'blockchain.info')

# Get balance for an address
balance_satoshis, balance_btc = get_balance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
print(f"Balance: {balance_btc} ({balance_satoshis} satoshis)")
```

### Implementation Details

The balance checking feature is implemented in the `pywallet_refactored.blockchain` module. It provides:

1. A base `BlockchainAPI` class that defines the interface for blockchain API providers
2. Concrete implementations for different providers:
   - `BlockchainInfoAPI` for blockchain.info
   - `BlockcypherAPI` for blockcypher.com
3. Helper functions for getting balances and formatting BTC amounts

The implementation includes rate limiting to avoid API throttling and proper error handling for network issues.

## Transaction History

The transaction history feature allows you to view the transaction history for Bitcoin addresses.

### Command-Line Usage

```bash
python -m pywallet_refactored txhistory <address>
```

Options:
- `--output`, `-o`: Output file for transaction history
- `--provider`, `-p`: Blockchain API provider to use (choices: 'blockchain.info', 'blockcypher')

Example:
```bash
python -m pywallet_refactored txhistory 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa --output=transactions.json
```

### API Usage

```python
from pywallet_refactored.blockchain import get_transactions
from pywallet_refactored.config import config
import json

# Set blockchain provider (optional)
config.set('blockchain_provider', 'blockchain.info')

# Get transaction history for an address
transactions = get_transactions('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')

# Print transaction summary
print(f"Found {len(transactions)} transactions")

# Process transactions
for tx in transactions[:5]:  # Show first 5 transactions
    print(f"Transaction: {tx['hash']}")
    print(f"Time: {tx.get('time', 'Unknown')}")
    
    # Save to file
    with open('transactions.json', 'w') as f:
        json.dump(transactions, f, indent=4)
```

### Implementation Details

The transaction history feature uses the same blockchain API infrastructure as the balance checking feature. It:

1. Fetches raw transaction data from the selected blockchain API
2. Parses the transaction data to extract relevant information
3. Calculates the net effect of each transaction on the address (received, sent, or no change)
4. Formats the transaction data for display or saves it to a file

The implementation handles different transaction formats from different API providers and provides a consistent interface.

## Watch-Only Wallet Creation

The watch-only wallet feature allows you to create a wallet that contains public keys but no private keys, enabling you to monitor addresses without the ability to spend funds.

### Command-Line Usage

```bash
python -m pywallet_refactored watchonly --wallet=/path/to/wallet.dat --output=/path/to/watchonly.dat
```

Options:
- `--wallet`, `-w`: Path to the source wallet.dat file
- `--output`, `-o`: Path to the watch-only wallet file (required)

### API Usage

```python
from pywallet_refactored.db.wallet import WalletDB

# Open source wallet
wallet = WalletDB('/path/to/wallet.dat')

# Create watch-only wallet
wallet.create_watch_only('/path/to/watchonly.dat')
```

### Implementation Details

The watch-only wallet feature is implemented in the `WalletDB` class. It:

1. Opens the source wallet
2. Creates a new wallet database at the specified output path
3. Copies all non-private records from the source wallet
4. For private key records, creates dummy records with zeroed private keys
5. Skips encrypted private keys and master keys
6. Preserves address records and other metadata

The resulting watch-only wallet can be used with the balance checking and transaction history features to monitor addresses without exposing private keys.

## Batch Operations

The batch operations feature allows you to perform operations on multiple keys at once.

### Command-Line Usage

#### Importing Multiple Keys

```bash
python -m pywallet_refactored batch import --wallet=/path/to/wallet.dat --input=/path/to/keys.txt --label="Imported"
```

Options:
- `--wallet`, `-w`: Path to the wallet file
- `--input`, `-i`: Input file with keys (required)
- `--label`, `-l`: Label prefix for imported keys

#### Exporting Multiple Keys

```bash
python -m pywallet_refactored batch export --wallet=/path/to/wallet.dat --output=/path/to/exported_keys.json
```

Options:
- `--wallet`, `-w`: Path to the wallet file
- `--output`, `-o`: Output file for keys (required)
- `--no-private`: Do not include private keys in export
- `--passphrase`, `-p`: Wallet passphrase for encrypted wallets

#### Generating Multiple Keys

```bash
python -m pywallet_refactored batch generate 10 --output=/path/to/generated_keys.json
```

Options:
- `count`: Number of key pairs to generate (required)
- `--output`, `-o`: Output file for generated keys (required)
- `--uncompressed`, `-u`: Generate uncompressed keys

### API Usage

```python
from pywallet_refactored.batch import (
    import_keys_from_file, export_keys_to_file,
    generate_key_batch, save_key_batch
)

# Import keys from a file
imported_addresses = import_keys_from_file('/path/to/wallet.dat', 'keys.txt', 'Imported')
print(f"Imported {len(imported_addresses)} keys")

# Export keys to a file
num_keys = export_keys_to_file('/path/to/wallet.dat', 'exported_keys.json')
print(f"Exported {num_keys} keys")

# Generate a batch of keys
keys = generate_key_batch(10)  # Generate 10 key pairs
print(f"Generated {len(keys)} key pairs")

# Save keys to a file
save_key_batch(keys, 'generated_keys.json')
print(f"Saved keys to generated_keys.json")
```

### Implementation Details

The batch operations feature is implemented in the `pywallet_refactored.batch` module. It provides:

1. Functions for importing keys from various file formats (JSON, CSV, text)
2. Functions for exporting keys to various file formats
3. Functions for generating multiple key pairs
4. Helper functions for reading and writing key data

The implementation supports different file formats and provides proper error handling and logging.

### Supported File Formats

#### JSON Format

```json
{
  "keys": [
    {
      "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
      "wif": "5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8",
      "private_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
      "compressed": true
    },
    {
      "address": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
      "wif": "5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9",
      "private_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
      "compressed": true
    }
  ]
}
```

#### CSV Format

```csv
address,wif,private_key,compressed
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa,5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8,0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef,true
1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2,5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9,0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef,true
```

#### Text Format

```
# Private keys
5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8 # First key
5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz9 # Second key
```
