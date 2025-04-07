#!/usr/bin/env python3
"""
Setup script for PyWallet.
"""

from setuptools import setup, find_packages
import os
import re

# Get version from __init__.py
with open(os.path.join('pywallet_refactored', '__init__.py'), 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        version = '0.0.0'

# Get long description from README.md
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='pywallet',
    version=version,
    description='Bitcoin Wallet Tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='PyWallet Team',
    author_email='info@example.com',
    url='https://github.com/example/pywallet',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pywallet=pywallet_refactored.__main__:main',
        ],
    },
    install_requires=[
        'bsddb3>=6.2.9',
        'ecdsa>=0.18.0',
        'pycryptodome>=3.15.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.3.0',
            'isort>=5.10.1',
            'flake8>=4.0.1',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Security :: Cryptography',
    ],
    python_requires='>=3.9',
)
