#!/usr/bin/env python3
"""
PyWallet - Bitcoin Wallet Tool (Python 3.9+ Version)

A tool for managing Bitcoin wallets, including dumping, importing, and recovering keys.
"""

import sys
import os

# Check Python version
if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 9):
    print("Error: This script requires Python 3.9 or higher")
    print("Your Python version: {}.{}.{}".format(
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro
    ))
    sys.exit(1)

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the package
try:
    from pywallet_refactored.__main__ import main
except ImportError:
    print("Error: Could not import pywallet_refactored package")
    print("Make sure the package is installed or in the same directory as this script")
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
