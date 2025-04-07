"""
Configuration variables for PyWallet
"""

import binascii

# Global configuration variables
wallet_dir = ""
wallet_name = ""
passphrase = ""
json_db = {}
addrtype = 0
kdbx = {}
aversions = {}
private_keys = []
private_hex_keys = []
addr_to_keys = {}

# Bitcoin network parameters
network_bitcoin = {
    'name': 'Bitcoin',
    'messagePrefix': b'\x18Bitcoin Signed Message:\n',
    'bip32': {
        'public': 0x0488b21e,
        'private': 0x0488ade4,
    },
    'pubKeyHash': 0x00,
    'scriptHash': 0x05,
    'wif': 0x80,
    'bech32': 'bc',
}

# Testnet network parameters
network_testnet = {
    'name': 'Testnet',
    'messagePrefix': b'\x18Bitcoin Signed Message:\n',
    'bip32': {
        'public': 0x043587cf,
        'private': 0x04358394,
    },
    'pubKeyHash': 0x6f,
    'scriptHash': 0xc4,
    'wif': 0xef,
    'bech32': 'tb',
}

# Prekeys and postkeys for key extraction
prekeys = [binascii.unhexlify("308201130201010420"), binascii.unhexlify("308201120201010420")]
postkeys = [binascii.unhexlify("a081a530"), binascii.unhexlify("81a530")]
