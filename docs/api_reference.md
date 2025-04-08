# PyWallet API Reference

This document provides detailed information about the PyWallet API.

## Table of Contents

- [Configuration](#configuration)
- [Wallet Database](#wallet-database)
- [Cryptography](#cryptography)
  - [Keys](#keys)
  - [AES Encryption](#aes-encryption)
  - [Base58 Encoding](#base58-encoding)
- [Blockchain](#blockchain)
- [Batch Operations](#batch-operations)
- [Recovery](#recovery)
- [Utilities](#utilities)
- [Testing](#testing)
  - [Basic Tests](#basic-tests)
  - [Integration Tests](#integration-tests)

## Configuration

### `pywallet_refactored.config.Config`

The `Config` class manages configuration settings for PyWallet.

#### Methods

##### `__init__()`

Initialize with default configuration.

##### `load_from_file(config_file: str) -> bool`

Load configuration from a JSON file.

- **Parameters**:
  - `config_file`: Path to the configuration file
- **Returns**: `True` if configuration was loaded successfully, `False` otherwise

##### `save_to_file(config_file: Optional[str] = None) -> bool`

Save current configuration to a JSON file.

- **Parameters**:
  - `config_file`: Path to save the configuration file (defaults to previously loaded file)
- **Returns**: `True` if configuration was saved successfully, `False` otherwise

##### `get(key: str, default: Any = None) -> Any`

Get a configuration value.

- **Parameters**:
  - `key`: Configuration key
  - `default`: Default value if key is not found
- **Returns**: The configuration value or default

##### `set(key: str, value: Any) -> None`

Set a configuration value.

- **Parameters**:
  - `key`: Configuration key
  - `value`: Configuration value

##### `update(config_dict: Dict[str, Any]) -> None`

Update multiple configuration values.

- **Parameters**:
  - `config_dict`: Dictionary of configuration values

##### `get_network(network_name: Optional[str] = None) -> Dict[str, Any]`

Get network parameters.

- **Parameters**:
  - `network_name`: Network name (defaults to configured network)
- **Returns**: Network parameters dictionary

##### `determine_wallet_dir() -> str`

Determine the wallet directory based on configuration or system defaults.

- **Returns**: Wallet directory path

##### `determine_wallet_path() -> str`

Determine the full wallet path.

- **Returns**: Full path to the wallet file

##### `as_dict() -> Dict[str, Any]`

Get the configuration as a dictionary.

- **Returns**: Configuration dictionary

### Global Instance

A global `config` instance is available:

```python
from pywallet_refactored.config import config

# Get a configuration value
wallet_path = config.determine_wallet_path()

# Set a configuration value
config.set('network', 'testnet')
```

## Wallet Database

### `pywallet_refactored.db.wallet.WalletDB`

The `WalletDB` class handles Bitcoin wallet database operations.

#### Methods

##### `__init__(wallet_path: Optional[str] = None)`

Initialize wallet database handler.

- **Parameters**:
  - `wallet_path`: Path to wallet.dat file (defaults to configured path)

##### `open(read_only: bool = True) -> None`

Open the wallet database.

- **Parameters**:
  - `read_only`: Whether to open in read-only mode
- **Raises**: `WalletDBError` if the wallet cannot be opened

##### `close() -> None`

Close the wallet database.

##### `read_wallet(passphrase: str = "") -> Dict[str, Any]`

Read wallet data.

- **Parameters**:
  - `passphrase`: Wallet passphrase for decrypting encrypted keys
- **Returns**: Dictionary with wallet data
- **Raises**: `WalletDBError` if the wallet cannot be read

##### `dump_wallet(output_file: str, include_private: bool = True) -> None`

Dump wallet data to a JSON file.

- **Parameters**:
  - `output_file`: Path to output file
  - `include_private`: Whether to include private keys
- **Raises**: `WalletDBError` if the wallet cannot be dumped

##### `import_key(wif: str, label: str = "") -> str`

Import a private key into the wallet.

- **Parameters**:
  - `wif`: WIF encoded private key
  - `label`: Label for the key
- **Returns**: Bitcoin address for the imported key
- **Raises**: `WalletDBError` if the key cannot be imported

##### `create_new_wallet(wallet_path: Optional[str] = None) -> None`

Create a new empty wallet.

- **Parameters**:
  - `wallet_path`: Path to new wallet file (defaults to configured path)
- **Raises**: `WalletDBError` if the wallet cannot be created

##### `create_backup(backup_path: str) -> None`

Create a backup of the wallet.

- **Parameters**:
  - `backup_path`: Path to backup file
- **Raises**: `WalletDBError` if the backup cannot be created

##### `create_watch_only(output_path: str) -> None`

Create a watch-only wallet from this wallet.

A watch-only wallet contains public keys but no private keys, allowing monitoring of addresses without the ability to spend.

- **Parameters**:
  - `output_path`: Path to the watch-only wallet file
- **Raises**: `WalletDBError` if the watch-only wallet cannot be created

#### Usage Example

```python
from pywallet_refactored.db.wallet import WalletDB

# Open a wallet
with WalletDB('/path/to/wallet.dat') as wallet:
    # Read wallet data
    wallet_data = wallet.read_wallet(passphrase='your_passphrase')

    # Import a key
    wallet.import_key('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8', label='My Key')

    # Dump wallet
    wallet.dump_wallet('keys.json')
```

## Cryptography

### Keys

#### `pywallet_refactored.crypto.keys`

This module provides functions for handling Bitcoin keys.

##### `hash160(data: bytes) -> bytes`

Perform RIPEMD-160(SHA-256(data)).

- **Parameters**:
  - `data`: Data to hash
- **Returns**: RIPEMD-160 of SHA-256 hash

##### `public_key_to_address(public_key: bytes, network: Optional[Dict[str, Any]] = None) -> str`

Convert a public key to a Bitcoin address.

- **Parameters**:
  - `public_key`: Public key bytes
  - `network`: Network parameters (defaults to Bitcoin mainnet)
- **Returns**: Bitcoin address

##### `private_key_to_wif(private_key: bytes, compressed: bool = True, network: Optional[Dict[str, Any]] = None) -> str`

Convert a private key to WIF format.

- **Parameters**:
  - `private_key`: Private key bytes
  - `compressed`: Whether to use compressed format
  - `network`: Network parameters (defaults to Bitcoin mainnet)
- **Returns**: WIF encoded private key

##### `wif_to_private_key(wif: str, network: Optional[Dict[str, Any]] = None) -> Tuple[bytes, bool]`

Convert a WIF private key to raw bytes.

- **Parameters**:
  - `wif`: WIF encoded private key
  - `network`: Network parameters (defaults to Bitcoin mainnet)
- **Returns**: Tuple of (private_key, compressed)
- **Raises**: `KeyError` if the WIF key is invalid

##### `private_key_to_public_key(private_key: bytes, compressed: bool = True) -> bytes`

Convert a private key to a public key.

- **Parameters**:
  - `private_key`: Private key bytes
  - `compressed`: Whether to use compressed format
- **Returns**: Public key bytes
- **Raises**: `ImportError` if ecdsa module is not available

##### `generate_key_pair(compressed: bool = True, network: Optional[Dict[str, Any]] = None) -> Dict[str, str]`

Generate a new Bitcoin key pair.

- **Parameters**:
  - `compressed`: Whether to use compressed format
  - `network`: Network parameters (defaults to Bitcoin mainnet)
- **Returns**: Dictionary with private_key, wif, public_key, and address
- **Raises**: `ImportError` if ecdsa module is not available

##### `is_valid_address(address: str, network: Optional[Dict[str, Any]] = None) -> bool`

Check if a Bitcoin address is valid.

- **Parameters**:
  - `address`: Bitcoin address to check
  - `network`: Network parameters (defaults to Bitcoin mainnet)
- **Returns**: True if address is valid, False otherwise

##### `is_valid_wif(wif: str, network: Optional[Dict[str, Any]] = None) -> bool`

Check if a WIF private key is valid.

- **Parameters**:
  - `wif`: WIF encoded private key to check
  - `network`: Network parameters (defaults to Bitcoin mainnet)
- **Returns**: True if WIF is valid, False otherwise

#### Usage Example

```python
from pywallet_refactored.crypto.keys import generate_key_pair, is_valid_address

# Generate a new key pair
key_pair = generate_key_pair()
print(f"Address: {key_pair['address']}")
print(f"Private key: {key_pair['wif']}")

# Check if an address is valid
valid = is_valid_address('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
print(f"Address is valid: {valid}")
```

### AES Encryption

#### `pywallet_refactored.crypto.aes`

This module provides functions for AES encryption and decryption.

##### `derive_key(password: bytes, salt: bytes, iterations: int, key_length: int) -> bytes`

Derive a key from a password using PBKDF2-HMAC-SHA512.

- **Parameters**:
  - `password`: Password bytes
  - `salt`: Salt bytes
  - `iterations`: Number of iterations
  - `key_length`: Length of the derived key in bytes
- **Returns**: Derived key

##### `encrypt_aes(data: bytes, key: bytes, iv: Optional[bytes] = None) -> bytes`

Encrypt data using AES-256-CBC.

- **Parameters**:
  - `data`: Data to encrypt
  - `key`: Encryption key (32 bytes for AES-256)
  - `iv`: Initialization vector (16 bytes, random if not provided)
- **Returns**: Encrypted data with IV prepended
- **Raises**:
  - `ImportError`: If neither PyCryptodome nor cryptography is available
  - `ValueError`: If key length is invalid

##### `decrypt_aes(encrypted_data: bytes, key: bytes) -> bytes`

Decrypt data using AES-256-CBC.

- **Parameters**:
  - `encrypted_data`: Encrypted data with IV prepended
  - `key`: Decryption key (32 bytes for AES-256)
- **Returns**: Decrypted data
- **Raises**:
  - `ImportError`: If neither PyCryptodome nor cryptography is available
  - `ValueError`: If key length or encrypted data is invalid

##### `decrypt_wallet_key(encrypted_key: bytes, derived_key: bytes) -> bytes`

Decrypt a Bitcoin wallet key.

- **Parameters**:
  - `encrypted_key`: Encrypted key from wallet
  - `derived_key`: Key derived from passphrase
- **Returns**: Decrypted key

#### Usage Example

```python
from pywallet_refactored.crypto.aes import derive_key, encrypt_aes, decrypt_aes

# Derive a key from a password
password = b'my_secure_password'
salt = os.urandom(8)
iterations = 2048
key_length = 32  # AES-256
key = derive_key(password, salt, iterations, key_length)

# Encrypt data
data = b'secret data'
encrypted_data = encrypt_aes(data, key)

# Decrypt data
decrypted_data = decrypt_aes(encrypted_data, key)
print(decrypted_data)  # b'secret data'
```

### Base58 Encoding

#### `pywallet_refactored.crypto.base58`

This module provides functions for Base58 encoding and decoding.

##### `b58encode(data: bytes) -> str`

Encode bytes using Base58.

- **Parameters**:
  - `data`: Bytes to encode
- **Returns**: Base58 encoded string

##### `b58decode(encoded: str) -> bytes`

Decode a Base58 encoded string to bytes.

- **Parameters**:
  - `encoded`: Base58 encoded string
- **Returns**: Decoded bytes

##### `b58encode_check(data: bytes) -> str`

Encode bytes using Base58 with a 4-byte checksum.

- **Parameters**:
  - `data`: Bytes to encode
- **Returns**: Base58Check encoded string

##### `b58decode_check(encoded: str) -> Optional[bytes]`

Decode a Base58Check encoded string to bytes.

- **Parameters**:
  - `encoded`: Base58Check encoded string
- **Returns**: Decoded bytes without checksum, or None if checksum is invalid

#### Usage Example

```python
from pywallet_refactored.crypto.base58 import b58encode_check, b58decode_check

# Encode data with checksum
data = b'\x00' + bytes.fromhex('0123456789abcdef')
encoded = b58encode_check(data)
print(encoded)

# Decode data with checksum verification
decoded = b58decode_check(encoded)
print(decoded.hex())
```

## Blockchain

### `pywallet_refactored.blockchain`

This module provides functions for interacting with the Bitcoin blockchain, including fetching balance information and transaction history.

#### Classes

##### `BlockchainAPI`

Base class for blockchain API providers.

###### Methods

- `__init__()`: Initialize blockchain API.
- `_rate_limit()`: Apply rate limiting to API requests.
- `_make_request(url: str) -> Dict[str, Any]`: Make an HTTP request to the API.
- `get_balance(address: str) -> int`: Get balance for an address in satoshis.
- `get_transactions(address: str) -> List[Dict[str, Any]]`: Get transaction history for an address.

##### `BlockchainInfoAPI`

Blockchain.info API provider.

###### Methods

- `__init__()`: Initialize blockchain.info API.
- `get_balance(address: str) -> int`: Get balance for an address in satoshis from blockchain.info.
- `get_transactions(address: str) -> List[Dict[str, Any]]`: Get transaction history for an address from blockchain.info.

##### `BlockcypherAPI`

Blockcypher API provider.

###### Methods

- `__init__()`: Initialize blockcypher API.
- `get_balance(address: str) -> int`: Get balance for an address in satoshis from blockcypher.
- `get_transactions(address: str) -> List[Dict[str, Any]]`: Get transaction history for an address from blockcypher.

#### Functions

##### `get_api_provider() -> BlockchainAPI`

Get the configured blockchain API provider.

- **Returns**: BlockchainAPI instance

##### `get_balance(address: str) -> Tuple[int, str]`

Get balance for an address in satoshis and formatted BTC.

- **Parameters**:
  - `address`: Bitcoin address
- **Returns**: Tuple of (balance_satoshis, balance_btc)
- **Raises**: `BlockchainError` if the balance cannot be fetched

##### `get_transactions(address: str) -> List[Dict[str, Any]]`

Get transaction history for an address.

- **Parameters**:
  - `address`: Bitcoin address
- **Returns**: List of transactions
- **Raises**: `BlockchainError` if the transactions cannot be fetched

##### `format_btc(satoshis: int) -> str`

Format satoshis as BTC string.

- **Parameters**:
  - `satoshis`: Amount in satoshis
- **Returns**: Formatted BTC string

#### Usage Example

```python
from pywallet_refactored.blockchain import get_balance, get_transactions

# Get balance for an address
balance_satoshis, balance_btc = get_balance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
print(f"Balance: {balance_btc} ({balance_satoshis} satoshis)")

# Get transaction history for an address
transactions = get_transactions('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
print(f"Found {len(transactions)} transactions")

# Print transaction details
for tx in transactions[:5]:  # Show first 5 transactions
    print(f"Transaction: {tx['hash']}")
    print(f"Time: {tx.get('time', 'Unknown')}")
```

## Batch Operations

### `pywallet_refactored.batch`

This module provides functions for batch operations on Bitcoin keys.

#### Classes

##### `BatchError`

Exception raised for batch operation errors.

#### Functions

##### `import_keys_from_file(wallet_path: str, input_file: str, label_prefix: str = "") -> List[str]`

Import private keys from a file into a wallet.

- **Parameters**:
  - `wallet_path`: Path to the wallet file
  - `input_file`: Path to the input file containing keys
  - `label_prefix`: Prefix for key labels
- **Returns**: List of imported addresses
- **Raises**: `BatchError` if the keys cannot be imported

##### `export_keys_to_file(wallet_path: str, output_file: str, include_private: bool = True, passphrase: str = "") -> int`

Export keys from a wallet to a file.

- **Parameters**:
  - `wallet_path`: Path to the wallet file
  - `output_file`: Path to the output file
  - `include_private`: Whether to include private keys
  - `passphrase`: Wallet passphrase for encrypted wallets
- **Returns**: Number of exported keys
- **Raises**: `BatchError` if the keys cannot be exported

##### `read_keys_from_file(input_file: str) -> List[Union[str, Dict[str, str]]]`

Read keys from a file.

- **Parameters**:
  - `input_file`: Path to the input file
- **Returns**: List of keys (strings or dictionaries)
- **Raises**: `BatchError` if the keys cannot be read

##### `read_keys_from_json(input_file: str) -> List[Dict[str, str]]`

Read keys from a JSON file.

- **Parameters**:
  - `input_file`: Path to the JSON file
- **Returns**: List of key dictionaries
- **Raises**: `BatchError` if the keys cannot be read

##### `read_keys_from_csv(input_file: str) -> List[Dict[str, str]]`

Read keys from a CSV file.

- **Parameters**:
  - `input_file`: Path to the CSV file
- **Returns**: List of key dictionaries
- **Raises**: `BatchError` if the keys cannot be read

##### `read_keys_from_text(input_file: str) -> List[str]`

Read keys from a text file.

- **Parameters**:
  - `input_file`: Path to the text file
- **Returns**: List of key strings
- **Raises**: `BatchError` if the keys cannot be read

##### `export_keys_to_json(keys: List[Dict[str, Any]], output_file: str, include_private: bool = True) -> None`

Export keys to a JSON file.

- **Parameters**:
  - `keys`: List of key dictionaries
  - `output_file`: Path to the output file
  - `include_private`: Whether to include private keys
- **Raises**: `BatchError` if the keys cannot be exported

##### `export_keys_to_csv(keys: List[Dict[str, Any]], output_file: str, include_private: bool = True) -> None`

Export keys to a CSV file.

- **Parameters**:
  - `keys`: List of key dictionaries
  - `output_file`: Path to the output file
  - `include_private`: Whether to include private keys
- **Raises**: `BatchError` if the keys cannot be exported

##### `export_keys_to_text(keys: List[Dict[str, Any]], output_file: str, include_private: bool = True) -> None`

Export keys to a text file.

- **Parameters**:
  - `keys`: List of key dictionaries
  - `output_file`: Path to the output file
  - `include_private`: Whether to include private keys
- **Raises**: `BatchError` if the keys cannot be exported

##### `generate_key_batch(count: int, compressed: bool = True) -> List[Dict[str, Any]]`

Generate a batch of key pairs.

- **Parameters**:
  - `count`: Number of key pairs to generate
  - `compressed`: Whether to use compressed format
- **Returns**: List of key pair dictionaries
- **Raises**: `BatchError` if the keys cannot be generated

##### `save_key_batch(keys: List[Dict[str, Any]], output_file: str) -> None`

Save a batch of key pairs to a file.

- **Parameters**:
  - `keys`: List of key pair dictionaries
  - `output_file`: Path to the output file
- **Raises**: `BatchError` if the keys cannot be saved

#### Usage Example

```python
from pywallet_refactored.batch import import_keys_from_file, export_keys_to_file, generate_key_batch, save_key_batch

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

## Recovery

### `pywallet_refactored.recovery`

This module provides functions for recovering Bitcoin wallet keys.

#### Classes

##### `RecoveredKey`

Class for recovered keys.

###### Methods

- `__init__(private_key: bytes, public_key: bytes, compressed: bool = False)`: Initialize a recovered key.
- `address() -> str`: Get the Bitcoin address for this key.
- `wif() -> str`: Get the WIF encoded private key.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary.

##### `RecoveredEncryptedKey`

Class for recovered encrypted keys.

###### Methods

- `__init__(encrypted_private_key: bytes, public_key: bytes, compressed: bool = False)`: Initialize a recovered encrypted key.
- `address() -> str`: Get the Bitcoin address for this key.
- `decrypt(master_key: bytes) -> RecoveredKey`: Decrypt the private key using the master key.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary.

##### `RecoveredMasterKey`

Class for recovered master keys.

###### Methods

- `__init__(encrypted_key: bytes, salt: bytes, iterations: int, method: int)`: Initialize a recovered master key.
- `decrypt(passphrase: str) -> bytes`: Decrypt the master key using the passphrase.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary.

#### Functions

##### `scan_file(file_path: str, start_offset: int = 0, max_size: Optional[int] = None) -> Dict[str, List[Any]]`

Scan a file for Bitcoin keys.

- **Parameters**:
  - `file_path`: Path to file to scan
  - `start_offset`: Offset to start scanning from
  - `max_size`: Maximum number of bytes to scan
- **Returns**: Dictionary with recovered keys
- **Raises**: `RecoveryError` if the file cannot be scanned

##### `scan_device(device_path: str, start_offset: int = 0, max_size: Optional[int] = None) -> Dict[str, List[Any]]`

Scan a device for Bitcoin keys.

- **Parameters**:
  - `device_path`: Path to device to scan
  - `start_offset`: Offset to start scanning from
  - `max_size`: Maximum number of bytes to scan
- **Returns**: Dictionary with recovered keys
- **Raises**: `RecoveryError` if the device cannot be scanned

##### `recover_keys_from_passphrase(encrypted_keys: List[RecoveredEncryptedKey], master_key: RecoveredMasterKey, passphrase: str) -> List[RecoveredKey]`

Recover keys from encrypted keys using a passphrase.

- **Parameters**:
  - `encrypted_keys`: List of encrypted keys
  - `master_key`: Master key
  - `passphrase`: Wallet passphrase
- **Returns**: List of recovered keys
- **Raises**: `RecoveryError` if the keys cannot be recovered

##### `dump_keys_to_file(keys: List[RecoveredKey], output_file: str) -> None`

Dump recovered keys to a file.

- **Parameters**:
  - `keys`: List of recovered keys
  - `output_file`: Path to output file
- **Raises**: `RecoveryError` if the keys cannot be dumped

##### `dump_encrypted_keys_to_file(encrypted_keys: List[RecoveredEncryptedKey], master_key: RecoveredMasterKey, output_file: str) -> None`

Dump encrypted keys to a file.

- **Parameters**:
  - `encrypted_keys`: List of encrypted keys
  - `master_key`: Master key
  - `output_file`: Path to output file
- **Raises**: `RecoveryError` if the encrypted keys cannot be dumped

#### Usage Example

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
```

## Utilities

### `pywallet_refactored.utils.common`

This module provides common utility functions.

#### Functions

##### `plural(count: int) -> str`

Return 's' if count is not 1, otherwise return empty string.

- **Parameters**:
  - `count`: The count to check
- **Returns**: 's' if count is not 1, otherwise ''

##### `systype() -> str`

Return the system type: 'Mac', 'Win', or 'Linux'.

- **Returns**: System type string

##### `md5_hash(data: Union[str, bytes]) -> str`

Calculate MD5 hash of data.

- **Parameters**:
  - `data`: Data to hash (string or bytes)
- **Returns**: MD5 hash as hexadecimal string

##### `sha256_hash(data: Union[str, bytes]) -> str`

Calculate SHA256 hash of data.

- **Parameters**:
  - `data`: Data to hash (string or bytes)
- **Returns**: SHA256 hash as hexadecimal string

##### `str_to_bytes(text: Any) -> bytes`

Convert string to bytes.

- **Parameters**:
  - `text`: Text to convert
- **Returns**: Bytes representation

##### `bytes_to_str(data: bytes) -> str`

Convert bytes to string.

- **Parameters**:
  - `data`: Bytes to convert
- **Returns**: String representation

##### `hex_to_bytes(hex_string: str) -> bytes`

Convert hexadecimal string to bytes.

- **Parameters**:
  - `hex_string`: Hexadecimal string
- **Returns**: Bytes representation

##### `bytes_to_hex(data: bytes) -> str`

Convert bytes to hexadecimal string.

- **Parameters**:
  - `data`: Bytes to convert
- **Returns**: Hexadecimal string

##### `read_part_file(fd: int, offset: int, length: int) -> bytes`

Read a part of a file, making sure to read in 512-byte blocks for Windows compatibility.

- **Parameters**:
  - `fd`: File descriptor
  - `offset`: Offset to start reading from
  - `length`: Number of bytes to read
- **Returns**: Bytes read from file

##### `multi_extract(data: bytes, lengths: List[int]) -> List[bytes]`

Extract multiple parts from bytes based on a list of lengths.

- **Parameters**:
  - `data`: Bytes to extract from
  - `lengths`: List of lengths to extract
- **Returns**: List of extracted parts

#### Usage Example

```python
from pywallet_refactored.utils.common import bytes_to_hex, hex_to_bytes, sha256_hash

# Convert bytes to hex
data = b'hello world'
hex_data = bytes_to_hex(data)
print(hex_data)  # '68656c6c6f20776f726c64'

# Convert hex to bytes
bytes_data = hex_to_bytes(hex_data)
print(bytes_data)  # b'hello world'

# Calculate SHA256 hash
hash_value = sha256_hash(data)
```

## Testing

PyWallet includes a comprehensive test suite to ensure the reliability and correctness of its functionality.

### Basic Tests

#### `pywallet_refactored.tests.test_basic`

Basic tests for core functionality and utility functions.

##### Test Cases

- `TestBasicFunctions`: Tests for basic utility functions
  - `test_is_valid_address`: Tests address validation
  - `test_is_valid_wif`: Tests WIF key validation
  - `test_generate_key_pair`: Tests key pair generation

#### Example

```python
import unittest
from pywallet_refactored.tests.test_basic import TestBasicFunctions

# Run all tests in TestBasicFunctions
suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicFunctions)
unittest.TextTestRunner().run(suite)
```

### Integration Tests

#### `tests.test_pywallet_refactored`

Integration tests for command-line interface and end-to-end functionality.

##### Test Cases

- `TestPyWalletRefactored`: Tests for the main command-line interface
  - `test_dump_wallet`: Tests wallet dumping functionality
  - `test_balance_check`: Tests balance checking functionality
  - `test_transaction_history`: Tests transaction history functionality
  - `test_watch_only_wallet`: Tests watch-only wallet creation
  - `test_batch_operations`: Tests batch operations for keys
  - `test_output_parameter`: Tests the --output parameter for commands

#### Example

```python
import unittest
from tests.test_pywallet_refactored import TestPyWalletRefactored

# Run all tests in TestPyWalletRefactored
suite = unittest.TestLoader().loadTestsFromTestCase(TestPyWalletRefactored)
unittest.TextTestRunner().run(suite)
```

For more detailed information about testing, see the [Testing Guide](testing.md).
