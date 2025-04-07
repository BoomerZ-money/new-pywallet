# PyWallet - Bitcoin Wallet Tool (Original Version)

## Description
A Python-based tool for managing Bitcoin wallets. PyWallet allows you to dump, import, and recover Bitcoin wallet keys, as well as perform various other wallet operations.

## Version Information
This README documents the original PyWallet implementation (pywallet.py and pywallet3.py). For the refactored version with improved architecture, see [README_refactored.md](README_refactored.md).

This repository contains PyWallet for Python 3.9+. The legacy Python 2.x version has been deprecated.

## System Requirements

- Python 3.9 or higher
- bsddb3 library
- ecdsa library
- Berkeley DB 4.x

## Installation Instructions

### Using Docker (Recommended)

The easiest way to use PyWallet is with Docker, which handles all dependencies automatically:

```bash
# Build the Docker image
docker build -t pywallet .

# Run PyWallet with Docker (example: show help)
docker run pywallet

# Run with specific options (example: dump wallet)
docker run -v /path/to/your/wallet:/wallet pywallet --dumpwallet --wallet=/wallet/wallet.dat
```

### Manual Installation

#### Debian/Ubuntu Linux:
```bash
apt install build-essential python3-dev python3-bsddb3
pip3 install -r requirements.txt
```

#### Mac OS X:
1. Install Homebrew from https://brew.sh/
2. Run the following commands:
```bash
brew install python@3.9
brew install berkeley-db@4
pip3 install -r requirements.txt
```

#### Windows:
1. Install Python 3.9 or higher from https://www.python.org/
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage Instructions

The original PyWallet (pywallet.py and pywallet3.py) can be used as a command-line tool with various options.

### Command Line Options

```bash
python pywallet3.py [options]
```

Or with Docker:

```bash
docker run pywallet [options]
```

### Available Options
```text
  --version                   show program's version number and exit
  -h, --help                  show this help message and exit
  --dump_bip32                dump the keys from a xpriv and a path
                              usage: --dump_bip32 xprv9s21ZrQH143K m/0H/1-2/2H/2-4
  --bip32_format              format of dumped bip32 keys
  --passphrase                passphrase for the encrypted wallet
  --find_address              find info about an address
  -d, --dumpwallet            dump wallet in json format
  --dumpformat                choose what to extract in a wallet dump (default: all)
  --dumpwithbalance           includes balance of each address in the json dump
                              (takes about 2 minutes per 100 addresses)
  --importprivkey=KEY         import private key from vanitygen
  --importhex                 DEPRECATED, useless
  --datadir=DATADIR           REMOVED OPTION: put full path in the --wallet option
  -w, --wallet                wallet filename (defaults to wallet.dat)
  --label=LABEL               label shown in the address book (defaults to '')
  --testnet                   use testnet subdirectory and address type
  --namecoin                  use namecoin address type
  --eth                       use ethereum address type
  --otherversion              use other network address type
                              either P2PKH prefix only (e.g. 111) or
                              full network info as 'name,p2pkh,p2sh,wif,segwithrp'
                              (e.g. btc,0,0,0x80,bc)
  --info                      display pubkey, privkey and hexkey
  --reserve                   import as a reserve key (won't show in address book)
  --multidelete               deletes data in your wallet according to file provided
  --balance                   prints balance of specified address
  --recover                   recover deleted keys (use with recov_size and recov_device)
  --recov_device              device to read (e.g. /dev/sda1 or E: or a file)
  --recov_size                number of bytes to read (e.g. 20Mo or 50Gio)
  --recov_outputdir           output directory for recovered wallet
  --clone_watchonly_from      path of the original wallet
  --clone_watchonly_to        path of the resulting watch-only wallet
  --dont_check_walletversion  don't check wallet version before running
                              (WARNING: may break your wallet)
  --random_key                print info of a randomly generated private key
  --whitepaper                write the Bitcoin whitepaper using bitcoin-cli
                              or blockchain.info
  --minimal_encrypted_copy    write a copy of an encrypted wallet with only an empty
                              address (safe to share when needing password help)
  --tests                     run tests
```

### Common Examples

1. **Dump wallet with balance information:**
```bash
python3 pywallet3.py --dumpwallet --dumpwithbalance --wallet=./wallet.dat
```
With Docker:
```bash
docker run -v $(pwd):/wallet pywallet --dumpwallet --dumpwithbalance --wallet=/wallet/wallet.dat
```

2. **Import a private key:**
```bash
python3 pywallet3.py --importprivkey=5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8
```

3. **Check balance of specific address:**
```bash
python3 pywallet3.py --balance=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

4. **Create watch-only wallet:**
```bash
python3 pywallet3.py --clone_watchonly_from=./wallet.dat --clone_watchonly_to=./watch_only.dat
```

5. **Extract Bitcoin whitepaper:**
```bash
python3 pywallet3.py --whitepaper
```

> **Note:** Replace file paths and addresses with your actual values. Always verify addresses and keys before using them.

## Important Notes

### Features
PyWallet includes:
- ✨ Secure wallet handling
- 🔄 Compatibility with Bitcoin standards
- 🚀 Modern Python features and optimizations
- 🛠️ Active maintenance and updates
- 🐳 Docker support for easy deployment

### Security Notice
⚠️ Always ensure you:
- Keep secure backups of your wallet
- Use strong passwords
- Run this tool in a secure environment
- Verify the authenticity of the software

## Development

### Running Tests

To run the test suite:

```bash
python pywallet3.py --tests
```

Or with Docker:

```bash
docker run pywallet --tests
```

### Project Structure

```
.
├── pywallet/           # Main module directory
│   ├── __init__.py     # Package initialization
│   ├── config.py       # Configuration variables
│   ├── crypto.py       # Cryptographic functions
│   ├── recovery.py     # Recovery functions
│   ├── utils.py        # Utility functions
│   └── wallet.py       # Wallet handling functions
├── tests/              # Test directory
│   ├── __init__.py     # Test package initialization
│   ├── test_crypto.py  # Tests for crypto module
│   └── test_utils.py   # Tests for utils module
├── Dockerfile          # Docker configuration
├── README.md           # This file
├── pywallet3.py        # Main script
└── requirements.txt    # Python dependencies
```

## Support and Contributing
For issues, questions, or contributions, please:
1. Check the existing issues on GitHub
2. Create a new issue if needed
3. Follow the contribution guidelines when submitting pull requests

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Refactored Version
A refactored version of PyWallet with improved architecture, better documentation, and more features is available. See [README_refactored.md](README_refactored.md) for details on the refactored version.
