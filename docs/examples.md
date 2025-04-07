# PyWallet Examples

This document provides practical examples of using PyWallet for various tasks.

## Table of Contents

- [Command-Line Examples](#command-line-examples)
  - [Basic Wallet Operations](#basic-wallet-operations)
  - [Key Management](#key-management)
  - [Recovery Operations](#recovery-operations)
- [Python API Examples](#python-api-examples)
  - [Working with Wallets](#working-with-wallets)
  - [Key Generation and Validation](#key-generation-and-validation)
  - [Encryption and Decryption](#encryption-and-decryption)
  - [Recovery](#recovery)
- [Docker Examples](#docker-examples)

## Command-Line Examples

### Basic Wallet Operations

#### Dumping a Wallet

```bash
# Dump wallet to a JSON file
python -m pywallet_refactored dump --wallet=/path/to/wallet.dat --output=keys.json

# Dump wallet without private keys
python -m pywallet_refactored dump --wallet=/path/to/wallet.dat --output=public_keys.json --no-private

# Dump encrypted wallet with passphrase
python -m pywallet_refactored dump --wallet=/path/to/wallet.dat --output=keys.json --passphrase="your passphrase"
```

#### Importing Keys

```bash
# Import a private key
python -m pywallet_refactored import 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8 --wallet=/path/to/wallet.dat

# Import a private key with a label
python -m pywallet_refactored import 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8 --wallet=/path/to/wallet.dat --label="Donation Key"
```

#### Creating Wallets

```bash
# Create a new empty wallet
python -m pywallet_refactored create --output=/path/to/new_wallet.dat

# Create a new wallet with an initial key
python -m pywallet_refactored create --output=/path/to/new_wallet.dat --generate-key

# Create a new wallet with an initial key and save the key to a file
python -m pywallet_refactored create --output=/path/to/new_wallet.dat --generate-key --save-key
```

#### Backing Up Wallets

```bash
# Create a backup of a wallet
python -m pywallet_refactored backup --wallet=/path/to/wallet.dat --output=/path/to/backup.dat
```

### Key Management

#### Generating Keys

```bash
# Generate a new key pair
python -m pywallet_refactored genkey

# Generate an uncompressed key pair
python -m pywallet_refactored genkey --uncompressed

# Generate a key pair and save it to a file
python -m pywallet_refactored genkey --save
```

#### Checking Addresses and Keys

```bash
# Check if an address is valid
python -m pywallet_refactored checkaddr 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# Check if a private key is valid
python -m pywallet_refactored checkkey 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8
```

### Recovery Operations

#### Recovering from Wallet Files

```bash
# Scan a wallet file for keys
python -m pywallet_refactored recover --file=/path/to/wallet.dat --output=recovered_keys.json

# Scan a wallet file with a specific start offset
python -m pywallet_refactored recover --file=/path/to/wallet.dat --output=recovered_keys.json --start=1024

# Scan a wallet file with a specific size limit
python -m pywallet_refactored recover --file=/path/to/wallet.dat --output=recovered_keys.json --size=1048576

# Scan an encrypted wallet file with a passphrase
python -m pywallet_refactored recover --file=/path/to/wallet.dat --output=recovered_keys.json --passphrase="your passphrase"
```

#### Recovering from Devices

```bash
# Scan a device for keys
python -m pywallet_refactored recover --device=/dev/sda --output=recovered_keys.json

# Scan a specific partition
python -m pywallet_refactored recover --device=/dev/sda1 --output=recovered_keys.json

# Scan a device with a specific start offset and size
python -m pywallet_refactored recover --device=/dev/sda --output=recovered_keys.json --start=1048576 --size=104857600
```

## Python API Examples

### Working with Wallets

#### Opening and Reading a Wallet

```python
from pywallet_refactored.db.wallet import WalletDB

# Open a wallet
with WalletDB('/path/to/wallet.dat') as wallet:
    # Read wallet data
    wallet_data = wallet.read_wallet()
    
    # Print wallet information
    print(f"Found {len(wallet_data['keys'])} keys")
    for key in wallet_data['keys']:
        print(f"Address: {key['address']}")
```

#### Opening an Encrypted Wallet

```python
from pywallet_refactored.db.wallet import WalletDB

# Open an encrypted wallet
with WalletDB('/path/to/wallet.dat') as wallet:
    # Read wallet data with passphrase
    wallet_data = wallet.read_wallet(passphrase='your_passphrase')
    
    # Print wallet information
    print(f"Found {len(wallet_data['keys'])} keys")
    for key in wallet_data['keys']:
        print(f"Address: {key['address']}")
        print(f"Private key (WIF): {key['wif']}")
```

#### Importing a Key

```python
from pywallet_refactored.db.wallet import WalletDB

# Open a wallet
with WalletDB('/path/to/wallet.dat') as wallet:
    # Import a key
    address = wallet.import_key('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8', label='My Key')
    
    print(f"Imported key with address: {address}")
```

#### Creating a New Wallet

```python
from pywallet_refactored.db.wallet import WalletDB
from pywallet_refactored.crypto.keys import generate_key_pair

# Create a new wallet
wallet = WalletDB('/path/to/new_wallet.dat')
wallet.create_new_wallet()

# Generate and import a key
key_pair = generate_key_pair()
address = wallet.import_key(key_pair['wif'], label='Initial Key')

print(f"Created new wallet with address: {address}")
```

### Key Generation and Validation

#### Generating a Key Pair

```python
from pywallet_refactored.crypto.keys import generate_key_pair

# Generate a key pair
key_pair = generate_key_pair()

print(f"Address: {key_pair['address']}")
print(f"Private key (WIF): {key_pair['wif']}")
print(f"Private key (hex): {key_pair['private_key']}")
print(f"Public key (hex): {key_pair['public_key']}")
print(f"Compressed: {key_pair['compressed']}")
```

#### Converting Between Formats

```python
from pywallet_refactored.crypto.keys import wif_to_private_key, private_key_to_public_key, public_key_to_address
from pywallet_refactored.utils.common import bytes_to_hex

# Convert WIF to private key
wif = '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8'
private_key, compressed = wif_to_private_key(wif)

print(f"Private key (hex): {bytes_to_hex(private_key)}")
print(f"Compressed: {compressed}")

# Convert private key to public key
public_key = private_key_to_public_key(private_key, compressed)
print(f"Public key (hex): {bytes_to_hex(public_key)}")

# Convert public key to address
address = public_key_to_address(public_key)
print(f"Address: {address}")
```

#### Validating Addresses and Keys

```python
from pywallet_refactored.crypto.keys import is_valid_address, is_valid_wif

# Check if an address is valid
address = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
if is_valid_address(address):
    print(f"Address {address} is valid")
else:
    print(f"Address {address} is NOT valid")

# Check if a private key is valid
wif = '5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8'
if is_valid_wif(wif):
    print(f"Private key is valid")
else:
    print(f"Private key is NOT valid")
```

### Encryption and Decryption

#### Deriving a Key from a Passphrase

```python
import os
from pywallet_refactored.crypto.aes import derive_key

# Derive a key from a passphrase
passphrase = b'my_secure_passphrase'
salt = os.urandom(8)
iterations = 2048
key_length = 32  # AES-256

derived_key = derive_key(passphrase, salt, iterations, key_length)
print(f"Derived key: {derived_key.hex()}")
```

#### Encrypting and Decrypting Data

```python
import os
from pywallet_refactored.crypto.aes import derive_key, encrypt_aes, decrypt_aes

# Derive a key from a passphrase
passphrase = b'my_secure_passphrase'
salt = os.urandom(8)
iterations = 2048
key_length = 32  # AES-256

derived_key = derive_key(passphrase, salt, iterations, key_length)

# Encrypt data
data = b'secret data'
encrypted_data = encrypt_aes(data, derived_key)
print(f"Encrypted data: {encrypted_data.hex()}")

# Decrypt data
decrypted_data = decrypt_aes(encrypted_data, derived_key)
print(f"Decrypted data: {decrypted_data.decode()}")
```

### Recovery

#### Scanning a File for Keys

```python
from pywallet_refactored.recovery import scan_file, dump_keys_to_file

# Scan a wallet file for keys
results = scan_file('/path/to/wallet.dat')

# Process results
keys = results['keys']
encrypted_keys = results['encrypted_keys']
master_keys = results['master_keys']

print(f"Found {len(keys)} unencrypted keys")
print(f"Found {len(encrypted_keys)} encrypted keys")
print(f"Found {len(master_keys)} master keys")

# Dump keys to file
if keys:
    dump_keys_to_file(keys, 'recovered_keys.json')
    print(f"Dumped {len(keys)} keys to recovered_keys.json")
```

#### Recovering Encrypted Keys

```python
from pywallet_refactored.recovery import scan_file, recover_keys_from_passphrase, dump_keys_to_file

# Scan a wallet file for keys
results = scan_file('/path/to/wallet.dat')

# Process results
keys = results['keys']
encrypted_keys = results['encrypted_keys']
master_keys = results['master_keys']

print(f"Found {len(keys)} unencrypted keys")
print(f"Found {len(encrypted_keys)} encrypted keys")
print(f"Found {len(master_keys)} master keys")

# Try to decrypt encrypted keys if passphrase is provided
if encrypted_keys and master_keys:
    passphrase = 'your_passphrase'
    recovered_keys = recover_keys_from_passphrase(
        encrypted_keys, master_keys[0], passphrase
    )
    
    keys.extend(recovered_keys)
    
    print(f"Successfully decrypted {len(recovered_keys)} keys")

# Dump keys to file
if keys:
    dump_keys_to_file(keys, 'recovered_keys.json')
    print(f"Dumped {len(keys)} keys to recovered_keys.json")
```

## Docker Examples

### Basic Usage

```bash
# Build the Docker image
docker build -t pywallet .

# Show help
docker run pywallet
```

### Wallet Operations

```bash
# Dump wallet
docker run -v $(pwd):/wallet pywallet dump --wallet=/wallet/wallet.dat --output=/wallet/keys.json

# Import a private key
docker run -v $(pwd):/wallet pywallet import 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8 --wallet=/wallet/wallet.dat

# Create a new wallet
docker run -v $(pwd):/wallet pywallet create --output=/wallet/new_wallet.dat --generate-key

# Backup a wallet
docker run -v $(pwd):/wallet pywallet backup --wallet=/wallet/wallet.dat --output=/wallet/backup.dat
```

### Key Management

```bash
# Generate a new key pair
docker run pywallet genkey

# Check if an address is valid
docker run pywallet checkaddr 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# Check if a private key is valid
docker run pywallet checkkey 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8
```

### Recovery Operations

```bash
# Recover keys from a wallet file
docker run -v $(pwd):/wallet pywallet recover --file=/wallet/wallet.dat --output=/wallet/recovered_keys.json

# Recover keys from an encrypted wallet file
docker run -v $(pwd):/wallet pywallet recover --file=/wallet/wallet.dat --output=/wallet/recovered_keys.json --passphrase="your passphrase"
```
