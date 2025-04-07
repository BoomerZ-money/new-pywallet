"""
Utility functions for PyWallet
"""

import os
import platform
import binascii
import hashlib
import collections

# Constants
ko = 1e3
kio = 1024
Mo = 1e6
Mio = 1024 ** 2
Go = 1e9
Gio = 1024 ** 3
To = 1e12
Tio = 1024 ** 4

KeyInfo = collections.namedtuple('KeyInfo', 'secret private_key public_key uncompressed_public_key addr wif compressed')

def plural(a):
    """Return 's' if a >= 2, otherwise return empty string"""
    if a >= 2:
        return 's'
    return ''

def systype():
    """Return the system type: 'Mac', 'Win', or 'Linux'"""
    if platform.system() == "Darwin":
        return 'Mac'
    elif platform.system() == "Windows":
        return 'Win'
    return 'Linux'

def determine_db_dir():
    """Determine the default database directory based on the operating system"""
    from pywallet.config import wallet_dir
    
    if not wallet_dir:
        if platform.system() == "Darwin":
            return os.path.expanduser("~/Library/Application Support/Bitcoin/")
        elif platform.system() == "Windows":
            return os.path.join(os.environ['APPDATA'], "Bitcoin")
        return os.path.expanduser("~/.bitcoin")
    else:
        return wallet_dir

def determine_db_name():
    """Determine the default database name"""
    from pywallet.config import wallet_name
    
    if not wallet_name:
        return "wallet.dat"
    else:
        return wallet_name

def md5_2(string):
    """Return the MD5 hash of a string"""
    return hashlib.md5(string.encode('utf-8')).hexdigest()

def readpartfile(fd, offset, length):
    """Read a part of a file, making sure to read in 512-byte blocks for Windows compatibility"""
    rest = offset % 512
    new_offset = offset - rest
    big_length = 512 * (int((length + rest - 1) // 512) + 1)
    os.lseek(fd, new_offset, os.SEEK_SET)
    d = os.read(fd, big_length)
    return d[rest:rest + length]

def multiextract(s, ll):
    """Extract multiple parts from a string based on a list of lengths"""
    r = []
    cursor = 0
    for length in ll:
        r.append(s[cursor:cursor + length])
        cursor += length
    if s[cursor:] != b'':
        r.append(s[cursor:])
    return r
