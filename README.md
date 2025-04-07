# PyWallet - Bitcoin Wallet Tool

## Description
A Python-based tool for managing Bitcoin wallets, available in two versions to support both legacy and modern systems.

## Version Information
This repository contains two versions of PyWallet:

1. `pywallet.py`  - Legacy Version (Python 2.x)
2. `pywallet3.py` - Modern Version (Python 3.9+)

## System Requirements

### Legacy Version (pywallet.py)
- Python 2.x
- bsddb library
- ecdsa library

### Modern Version (pywallet3.py)
- Python 3.9 or higher
- bsddb3 library
- ecdsa library
- Berkeley DB 4.x

## Installation Instructions

### Legacy Version (Python 2.x)

#### Debian/Ubuntu Linux:
```bash
aptitude install build-essential python-dev python-bsddb3
```

#### Mac OS X:
1. Install MacPorts from http://www.macports.org/
2. Run the following commands:
```bash
sudo port install python27 py27-pip py-bsddb python_select
sudo port select --set python python27
sudo easy_install ecdsa
```

#### Windows:
- Install Python 2.7 from python.org
- Install required packages using pip

### Modern Version (Python 3.9+)

#### Debian/Ubuntu Linux:
```bash
apt install build-essential python3-dev python3-bsddb3
```

#### Mac OS X:
1. Install Homebrew from https://brew.sh/
2. Run the following commands:
```bash
brew install python@3.9
brew install berkeley-db@4
pip3 install bsddb3 ecdsa
```

#### Windows:
1. Install Python 3.9 or higher from https://www.python.org/
2. Install required packages:
```bash
pip install bsddb3 ecdsa
```

## Usage Instructions

### Command Line Options
Both versions support the same command-line options:

#### Legacy Version:
```bash
python pywallet.py [options]
```

#### Modern Version:
```bash
python pywallet3.py [options]
```

### Available Options
```
  --version             show program's version number and exit
  -h, --help           show this help message and exit
  --dumpwallet         dump wallet in json format
  --importprivkey=KEY  import private key from vanitygen
  --importhex          KEY is in hexadecimal format
  --datadir=DATADIR    wallet directory (defaults to bitcoin default)
  --wallet=WALLETFILE  wallet filename (defaults to wallet.dat)
  --label=LABEL        label shown in the address book (defaults to '')
  --testnet            use testnet subdirectory and address type
  --namecoin           use namecoin address type
  --otherversion=OTHERVERSION
                       use other network address type, whose version is
                       OTHERVERSION
  --info               display pubkey, privkey (both depending on the
                       network) and hexkey
  --reserve            import as a reserve key, i.e. won't show in address book
  --balance=KEY_BALANCE
                       prints balance of KEY_BALANCE
  --web                run pywallet web interface
  --port=PORT          port of web interface (defaults to 8989)
```

### Common Examples

1. **Dump wallet with balance information:**
```bash
# Modern Version (Python 3.9+)
python3 pywallet3.py --dumpwallet --dumpwithbalance --wallet=./wallet.dat

# Legacy Version (Python 2.x)
python pywallet.py --dumpwallet --dumpwithbalance --wallet=./wallet.dat
```

2. **Import a private key:**
```bash
# Modern Version (Python 3.9+)
python3 pywallet3.py --importprivkey=5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8

# Legacy Version (Python 2.x)
python pywallet.py --importprivkey=5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8
```

3. **Check balance of specific address:**
```bash
# Modern Version (Python 3.9+)
python3 pywallet3.py --balance=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# Legacy Version (Python 2.x)
python pywallet.py --balance=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

4. **Create watch-only wallet:**
```bash
# Modern Version (Python 3.9+)
python3 pywallet3.py --clone_watchonly_from=./wallet.dat --clone_watchonly_to=./watch_only.dat

# Legacy Version (Python 2.x)
python pywallet.py --clone_watchonly_from=./wallet.dat --clone_watchonly_to=./watch_only.dat
```

5. **Extract Bitcoin whitepaper:**
```bash
# Modern Version (Python 3.9+)
python3 pywallet3.py --whitepaper

# Legacy Version (Python 2.x)
python pywallet.py --whitepaper
```

> **Note:** Replace file paths and addresses with your actual values. Always verify addresses and keys before using them.

## Important Notes

### Version Recommendation
The modern version (`pywallet3.py`) is recommended for most users as it includes:
- ✨ Improved security features
- 🔄 Better compatibility with current Bitcoin standards
- 🚀 Modern Python features and optimizations
- 🛠️ Active maintenance and updates

Only use the legacy version (`pywallet.py`) if you have specific requirements for Python 2.x compatibility.

### Security Notice
⚠️ Always ensure you:
- Keep secure backups of your wallet
- Use strong passwords
- Run this tool in a secure environment
- Verify the authenticity of the software

## Support and Contributing
For issues, questions, or contributions, please:
1. Check the existing issues on GitHub
2. Create a new issue if needed
3. Follow the contribution guidelines when submitting pull requests

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.