# PyWallet

![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive Bitcoin wallet management tool for dumping, importing, and recovering keys from wallet.dat files.

## Features

- 🔑 Dump wallet keys and addresses
- 🔒 Import private keys into wallets
- 🔍 Recover keys from corrupted wallets
- 🔄 Create watch-only wallets
- 🛡️ Support for encrypted wallets
- 🐳 Docker support for easy deployment
- 💰 Check balance of Bitcoin addresses
- 📜 View transaction history for addresses
- 📦 Batch operations for multiple keys

## Installation

### Using Docker (Recommended)

The easiest way to use PyWallet is with Docker, which handles all dependencies automatically:

```bash
# Build the Docker image
docker build -t pywallet .

# Run PyWallet with Docker (example: show help)
docker run pywallet

# Run with specific options (example: dump wallet)
docker run -v /path/to/your/wallet:/wallet pywallet dump --wallet=/wallet/wallet.dat
```

### Manual Installation

#### Prerequisites

- Python 3.9 or higher
- Berkeley DB 4.x
- Build tools (for compiling bsddb3)

#### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BoomerZ-money/pywallet.git
   cd pywallet
   ```

2. **Install dependencies**:

   **Debian/Ubuntu Linux**:
   ```bash
   apt install build-essential python3-dev libdb-dev
   pip install -r requirements.txt
   ```

   **macOS**:
   ```bash
   brew install berkeley-db@4
   pip install -r requirements.txt
   ```

   **Windows**:
   ```bash
   # Install Berkeley DB from https://www.oracle.com/database/technologies/related/berkeleydb-downloads.html
   pip install -r requirements.txt
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

## Usage

PyWallet can be used as a command-line tool with various subcommands:

```bash
# Show help
python -m pywallet_refactored --help

# Dump wallet (modern syntax)
python -m pywallet_refactored dump --wallet=/path/to/wallet.dat --output=keys.json

# Dump wallet (legacy syntax)
python -m pywallet_refactored --dumpwallet --wallet=/path/to/wallet.dat --output=keys.json

# Import a private key
python -m pywallet_refactored import 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8 --wallet=/path/to/wallet.dat

# Create a new wallet
python -m pywallet_refactored create --output=/path/to/new_wallet.dat --generate-key

# Backup a wallet
python -m pywallet_refactored backup --wallet=/path/to/wallet.dat --output=/path/to/backup.dat

# Generate a new key pair
python -m pywallet_refactored genkey --save

# Check if an address is valid
python -m pywallet_refactored checkaddr 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# Check if a private key is valid
python -m pywallet_refactored checkkey 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8

# Check balance of addresses
python -m pywallet_refactored balance 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2

# View transaction history
python -m pywallet_refactored txhistory 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa --output=transactions.json

# Create a watch-only wallet
python -m pywallet_refactored watchonly --wallet=/path/to/wallet.dat --output=/path/to/watchonly.dat

# Batch operations
python -m pywallet_refactored batch import --wallet=/path/to/wallet.dat --input=keys.txt
python -m pywallet_refactored batch export --wallet=/path/to/wallet.dat --output=exported_keys.json
python -m pywallet_refactored batch generate 10 --output=generated_keys.json

# Recover keys from a wallet
python -m pywallet_refactored recover --file=/path/to/wallet.dat --output=recovered_keys.json
```

### Docker Examples

```bash
# Dump wallet (modern syntax)
docker run -v $(pwd):/wallet pywallet dump --wallet=/wallet/wallet.dat --output=/wallet/keys.json

# Dump wallet (legacy syntax)
docker run -v $(pwd):/wallet pywallet --dumpwallet --wallet=/wallet/wallet.dat --output=/wallet/keys.json

# Import a private key
docker run -v $(pwd):/wallet pywallet import 5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8 --wallet=/wallet/wallet.dat

# Check balance of addresses
docker run -v $(pwd):/wallet pywallet balance 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# View transaction history
docker run -v $(pwd):/wallet pywallet txhistory 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa --output=/wallet/transactions.json

# Create a watch-only wallet
docker run -v $(pwd):/wallet pywallet watchonly --wallet=/wallet/wallet.dat --output=/wallet/watchonly.dat

# Batch operations
docker run -v $(pwd):/wallet pywallet batch import --wallet=/wallet/wallet.dat --input=/wallet/keys.txt
docker run -v $(pwd):/wallet pywallet batch export --wallet=/wallet/wallet.dat --output=/wallet/exported_keys.json
docker run -v $(pwd):/wallet pywallet batch generate 10 --output=/wallet/generated_keys.json

# Recover keys from a wallet
docker run -v $(pwd):/wallet pywallet recover --file=/wallet/wallet.dat --output=/wallet/recovered_keys.json
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [API Reference](docs/api_reference.md) - Detailed API documentation
- [User Guide](docs/user_guide.md) - Step-by-step guide for using PyWallet
- [Examples](docs/examples.md) - Practical examples of using PyWallet

## API Usage

PyWallet can also be used as a Python library:

```python
from pywallet_refactored.db.wallet import WalletDB
from pywallet_refactored.crypto.keys import generate_key_pair

# Open a wallet
with WalletDB('/path/to/wallet.dat') as wallet:
    # Read wallet data
    wallet_data = wallet.read_wallet(passphrase='your_passphrase')

    # Import a key
    wallet.import_key('5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8', label='My Key')

    # Dump wallet
    wallet.dump_wallet('keys.json')

# Generate a new key pair
key_pair = generate_key_pair()
print(f"Address: {key_pair['address']}")
print(f"Private key: {key_pair['wif']}")
```

For more detailed API documentation, see the [API Reference](docs/api_reference.md).

## Project Structure

```
.
├── pywallet_refactored/       # Main module directory
│   ├── __init__.py            # Package initialization
│   ├── __main__.py            # Entry point
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging configuration
│   ├── recovery.py            # Recovery functions
│   ├── cli/                   # Command-line interface
│   │   ├── __init__.py
│   │   ├── commands.py        # Command implementations
│   │   └── parser.py          # Argument parsing
│   ├── crypto/                # Cryptographic functions
│   │   ├── __init__.py
│   │   ├── aes.py             # AES encryption/decryption
│   │   ├── base58.py          # Base58 encoding/decoding
│   │   └── keys.py            # Key handling
│   ├── db/                    # Database handling
│   │   ├── __init__.py
│   │   └── wallet.py          # Wallet database
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   └── common.py          # Common utilities
│   └── tests/                 # Test directory
│       ├── __init__.py
│       ├── test_crypto.py     # Tests for crypto module
│       └── test_utils.py      # Tests for utils module
├── docs/                      # Documentation
│   ├── api_reference.md       # API reference
│   ├── user_guide.md          # User guide
│   └── examples.md            # Examples
├── Dockerfile                 # Docker configuration
├── README.md                  # This file
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # License file
├── pywallet_refactored.py     # Wrapper script
├── setup.py                   # Package setup
└── requirements.txt           # Python dependencies
```

## Development

### Running Tests

To run the test suite:

```bash
# Run all tests
python run_tests.py

# Run specific test modules
python -m unittest pywallet_refactored.tests.test_crypto
python -m unittest pywallet_refactored.tests.test_wallet

# Run with unittest discover
python -m unittest discover -s pywallet_refactored/tests

# Run with pytest
pytest pywallet_refactored/tests
```

### Test Coverage

The test suite includes comprehensive tests for:

- Cryptographic functions (keys, AES encryption)
- Wallet database operations
- Blockchain API interactions
- Batch operations for keys
- Command-line interface commands

To run tests with coverage reporting:

```bash
python -m pytest --cov=pywallet_refactored pywallet_refactored/tests/
```

### Code Style

This project follows PEP 8 style guidelines. You can check your code with:

```bash
flake8 pywallet_refactored
```

And format it with:

```bash
black pywallet_refactored
isort pywallet_refactored
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- The original pywallet project
- Bitcoin Core developers
- All contributors to this project
