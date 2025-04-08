# PyWallet User Guide

This guide provides detailed instructions for using PyWallet to manage Bitcoin wallets.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Working with Wallets](#working-with-wallets)
  - [Dumping Wallet Data](#dumping-wallet-data)
  - [Importing Private Keys](#importing-private-keys)
  - [Creating New Wallets](#creating-new-wallets)
  - [Backing Up Wallets](#backing-up-wallets)
  - [Creating Watch-Only Wallets](#creating-watch-only-wallets)
- [Key Management](#key-management)
  - [Generating Key Pairs](#generating-key-pairs)
  - [Checking Addresses](#checking-addresses)
  - [Checking Private Keys](#checking-private-keys)
- [Blockchain Operations](#blockchain-operations)
  - [Checking Address Balances](#checking-address-balances)
  - [Viewing Transaction History](#viewing-transaction-history)
- [Batch Operations](#batch-operations)
  - [Importing Multiple Keys](#importing-multiple-keys)
  - [Exporting Multiple Keys](#exporting-multiple-keys)
  - [Generating Multiple Keys](#generating-multiple-keys)
- [Recovery](#recovery)
  - [Recovering Keys from Wallet Files](#recovering-keys-from-wallet-files)
  - [Recovering Keys from Devices](#recovering-keys-from-devices)
  - [Decrypting Encrypted Keys](#decrypting-encrypted-keys)
- [Using Docker](#using-docker)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

Before installing PyWallet, ensure you have the following prerequisites:

- Python 3.9 or higher
- Berkeley DB 4.x
- Build tools (for compiling bsddb3)

### Installation Steps

#### Using pip

The easiest way to install PyWallet is using pip:

```bash
pip install pywallet
```

#### From Source

To install from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pywallet.git
   cd pywallet
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

### Platform-Specific Instructions

#### Debian/Ubuntu Linux

```bash
# Install system dependencies
apt install build-essential python3-dev libdb-dev

# Install PyWallet
pip install pywallet
```

#### macOS

```bash
# Install Berkeley DB using Homebrew
brew install berkeley-db@4

# Install PyWallet
pip install pywallet
```

#### Windows

1. Download and install Berkeley DB from [Oracle's website](https://www.oracle.com/database/technologies/related/berkeleydb-downloads.html)
2. Install PyWallet:
   ```bash
   pip install pywallet
   ```

## Basic Usage

PyWallet can be used as a command-line tool with various subcommands:

```bash
# Show help
python -m pywallet_refactored --help
```

This will display the available commands and options.

## Working with Wallets

### Dumping Wallet Data

To dump the contents of a wallet to a JSON file:

```bash
# Using the modern subcommand syntax
python -m pywallet_refactored dump --wallet=/path/to/wallet.dat --output=keys.json

# Using the legacy flag syntax
python -m pywallet_refactored --dumpwallet --wallet=/path/to/wallet.dat --output=keys.json
```

Options:
- `--wallet`: Path to the wallet.dat file
- `--output`: Path to the output JSON file
- `--no-private`: Do not include private keys in the dump

If the wallet is encrypted, you can provide the passphrase:

```bash
python -m pywallet_refactored dump --wallet=/path/to/wallet.dat --output=keys.json --passphrase="your passphrase"
```

### Importing Private Keys

To import a private key into a wallet:

```bash
python -m pywallet_refactored import 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8 --wallet=/path/to/wallet.dat
```

Options:
- `--wallet`: Path to the wallet.dat file
- `--label`: Label for the imported key

### Creating New Wallets

To create a new wallet:

```bash
python -m pywallet_refactored create --output=/path/to/new_wallet.dat
```

Options:
- `--output`: Path to the new wallet.dat file
- `--force`: Overwrite existing wallet
- `--generate-key`: Generate an initial key
- `--save-key`: Save generated key to a file

### Backing Up Wallets

To create a backup of a wallet:

```bash
python -m pywallet_refactored backup --wallet=/path/to/wallet.dat --output=/path/to/backup.dat
```

Options:
- `--wallet`: Path to the wallet.dat file
- `--output`: Path to the backup file

### Creating Watch-Only Wallets

A watch-only wallet contains public keys but no private keys, allowing you to monitor addresses without the ability to spend funds. This is useful for tracking balances without exposing private keys.

To create a watch-only wallet from an existing wallet:

```bash
python -m pywallet_refactored watchonly --wallet=/path/to/wallet.dat --output=/path/to/watchonly.dat
```

Options:
- `--wallet`: Path to the source wallet.dat file
- `--output`: Path to the watch-only wallet file (required)

## Key Management

### Generating Key Pairs

To generate a new Bitcoin key pair:

```bash
python -m pywallet_refactored genkey
```

Options:
- `--uncompressed`: Generate uncompressed key
- `--save`: Save key to a file

Example output:
```
Address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
Private key (WIF): 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8
Private key (hex): 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
Public key (hex): 0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
Compressed: True
```

### Checking Addresses

To check if a Bitcoin address is valid:

```bash
python -m pywallet_refactored checkaddr 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

### Checking Private Keys

To check if a private key is valid and get its corresponding address:

```bash
python -m pywallet_refactored checkkey 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8
```

Example output:
```
Private key is valid
Address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
Compressed: True
```

## Blockchain Operations

### Checking Address Balances

To check the balance of one or more Bitcoin addresses:

```bash
python -m pywallet_refactored balance 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2
```

Options:
- `--provider`, `-p`: Blockchain API provider to use (choices: 'blockchain.info', 'blockcypher')

Example output:
```
Address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
Balance: 0.12345678 BTC (12345678 satoshis)

Address: 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2
Balance: 0.00000000 BTC (0 satoshis)
```

### Viewing Transaction History

To view the transaction history for a Bitcoin address:

```bash
python -m pywallet_refactored txhistory 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

Options:
- `--output`, `-o`: Output file for transaction history
- `--provider`, `-p`: Blockchain API provider to use (choices: 'blockchain.info', 'blockcypher')

Example output:
```
Transaction history for 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa:
Found 10 transactions

Transaction 1:
  Hash: 6f7cf9580f1c2dfb3c4d5d043cdbb128c640e3f20161245aa7372e9666168516
  Time: 2021-01-01 12:00:00
  Effect: +100000 satoshis (received)

Transaction 2:
  Hash: 7f8cf9580f1c2dfb3c4d5d043cdbb128c640e3f20161245aa7372e9666168517
  Time: 2021-01-02 13:00:00
  Effect: -50000 satoshis (sent)
```

## Batch Operations

### Importing Multiple Keys

To import multiple private keys from a file into a wallet:

```bash
python -m pywallet_refactored batch import --wallet=/path/to/wallet.dat --input=/path/to/keys.txt --label="Imported"
```

Options:
- `--wallet`, `-w`: Path to the wallet file
- `--input`, `-i`: Input file with keys (required)
- `--label`, `-l`: Label prefix for imported keys

Supported input file formats:
- JSON: `.json` extension
- CSV: `.csv` extension
- Text: Any other extension (one key per line)

### Exporting Multiple Keys

To export keys from a wallet to a file:

```bash
python -m pywallet_refactored batch export --wallet=/path/to/wallet.dat --output=/path/to/exported_keys.json
```

Options:
- `--wallet`, `-w`: Path to the wallet file
- `--output`, `-o`: Output file for keys (required)
- `--no-private`: Do not include private keys in export
- `--passphrase`, `-p`: Wallet passphrase for encrypted wallets

Supported output file formats (determined by extension):
- JSON: `.json` extension
- CSV: `.csv` extension
- Text: Any other extension

### Generating Multiple Keys

To generate multiple key pairs:

```bash
python -m pywallet_refactored batch generate 10 --output=/path/to/generated_keys.json
```

Options:
- `count`: Number of key pairs to generate (required)
- `--output`, `-o`: Output file for generated keys (required)
- `--uncompressed`, `-u`: Generate uncompressed keys

## Recovery

### Recovering Keys from Wallet Files

To recover keys from a wallet file:

```bash
python -m pywallet_refactored recover --file=/path/to/wallet.dat --output=recovered_keys.json
```

Options:
- `--file`: Path to the wallet.dat file
- `--output`: Path to the output JSON file
- `--start`: Start offset for scanning
- `--size`: Maximum size to scan
- `--passphrase`: Passphrase for encrypted keys

### Recovering Keys from Devices

To recover keys from a device (e.g., a disk):

```bash
python -m pywallet_refactored recover --device=/dev/sda --output=recovered_keys.json
```

Options:
- `--device`: Path to the device
- `--output`: Path to the output JSON file
- `--start`: Start offset for scanning
- `--size`: Maximum size to scan
- `--passphrase`: Passphrase for encrypted keys

### Decrypting Encrypted Keys

If you have recovered encrypted keys but didn't provide a passphrase during recovery, you can decrypt them later:

```bash
python -m pywallet_refactored recover --file=encrypted_keys.json --passphrase="your passphrase" --output=decrypted_keys.json
```

## Using Docker

PyWallet can be run using Docker, which handles all dependencies automatically:

```bash
# Build the Docker image
docker build -t pywallet .

# Run PyWallet with Docker (example: show help)
docker run pywallet

# Run with specific options (example: dump wallet)
docker run -v $(pwd):/wallet pywallet dump --wallet=/wallet/wallet.dat --output=/wallet/keys.json
```

When using Docker, you need to mount your wallet directory as a volume to make it accessible to the container.

## Troubleshooting

### Common Issues

#### Berkeley DB Errors

If you encounter errors related to Berkeley DB, ensure you have the correct version installed (4.x) and that the development headers are available.

#### Encrypted Wallet Issues

If you're having trouble with an encrypted wallet:
- Double-check your passphrase
- Ensure you're using the correct wallet file
- Check if the wallet is actually encrypted

#### Import Errors

If you encounter import errors when running PyWallet:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check your Python version (3.9+ required)
- If using from source, ensure you're in the correct directory

### Getting Help

If you encounter issues not covered in this guide:
1. Check the [GitHub issues](https://github.com/yourusername/pywallet/issues) for similar problems
2. Create a new issue with detailed information about your problem
3. Include error messages, your environment details, and steps to reproduce the issue
