# PyWallet API Reference

This document provides detailed information about the PyWallet API.

## Table of Contents

- [Configuration](#configuration)
- [Wallet Database](#wallet-database)
- [Cryptography](#cryptography)
  - [Keys](#keys)
  - [AES Encryption](#aes-encryption)
  - [Base58 Encoding](#base58-encoding)
- [Recovery](#recovery)
- [Utilities](#utilities)

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
print(hash_value)  # 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
```
