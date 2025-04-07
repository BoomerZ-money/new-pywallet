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
```bash
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
# Modern Version (Python 3.9+)
python3 pywallet3.py --dumpwallet --dumpwithbalance --wallet=./wallet.dat
```
```bash
# Legacy Version (Python 2.x)
python pywallet.py --dumpwallet --dumpwithbalance --wallet=./wallet.dat
```

2. **Import a private key:**
```bash
# Modern Version (Python 3.9+)
python3 pywallet3.py --importprivkey=5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8
```
```bash
# Legacy Version (Python 2.x)
python pywallet.py --importprivkey=5KQNQrchXvxdR5WNi5Y1BqQyfeHGLEyqKHDB3XyCQYJjPo5rtz8
```

3. **Check balance of specific address:**
```bash
# Modern Version (Python 3.9+)
python3 pywallet3.py --balance=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```
```bash
# Legacy Version (Python 2.x)
python pywallet.py --balance=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

4. **Create watch-only wallet:**
```bash
# Modern Version (Python 3.9+)
python3 pywallet3.py --clone_watchonly_from=./wallet.dat --clone_watchonly_to=./watch_only.dat
```
```bash
# Legacy Version (Python 2.x)
python pywallet.py --clone_watchonly_from=./wallet.dat --clone_watchonly_to=./watch_only.dat
```

5. **Extract Bitcoin whitepaper:**
```bash
# Modern Version (Python 3.9+)
python3 pywallet3.py --whitepaper
```
```bash
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
