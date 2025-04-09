#!/usr/bin/env python3
"""
Setup script for PyWallet - Bitcoin Wallet Management Tool.

This setup script handles package configuration, dependencies,
and installation settings for both the main wallet tool and
the brute force component.
"""

import os
import re
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

# Ensure Python 3.9 or higher is being used
if sys.version_info < (3, 9):
    sys.exit('Python 3.9 or higher is required')

def get_version():
    """Extract version from __init__.py"""
    init_path = os.path.join('pywallet_refactored', '__init__.py')
    if not os.path.exists(init_path):
        return '0.1.0'  # Default version if file not found
    
    with open(init_path, 'r', encoding='utf-8') as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
        return '0.1.0'  # Default version if no match

def get_long_description():
    """Get long description from README files"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            main_desc = f.read()
        with open('README_wallet_brute_force.md', 'r', encoding='utf-8') as f:
            brute_force_desc = f.read()
        return f"{main_desc}\n\n## Brute Force Tool\n\n{brute_force_desc}"
    except FileNotFoundError:
        return "Bitcoin Wallet Management Tool"

# Core dependencies
CORE_REQUIREMENTS = [
    'bsddb3>=6.2.9',
    'ecdsa>=0.18.0',
    'pycryptodome>=3.15.0',
]

# Brute force tool dependencies
BRUTE_FORCE_REQUIREMENTS = [
    'pycryptodome>=3.19.0',
    'tqdm>=4.66.1',
    'colorama>=0.4.6',
    'psutil>=5.9.7',
    'numpy>=1.24.0',
]

# Platform-specific dependencies
APPLE_SILICON_REQUIREMENTS = [
    'tensorflow-macos>=2.15.0; platform_system == "Darwin" and platform_machine == "arm64"',
    'tensorflow-metal>=1.1.0; platform_system == "Darwin" and platform_machine == "arm64"',
    'metal-python>=1.0.0; platform_system == "Darwin" and platform_machine == "arm64"',
]

INTEL_REQUIREMENTS = [
    'intel-openmp>=2024.0.0; platform_machine == "x86_64"',
    'mkl>=2024.0.0; platform_machine == "x86_64"',
    'numba>=0.58.1; platform_machine == "x86_64"',
]

GPU_REQUIREMENTS = [
    'pyopencl>=2023.1.4; platform_system != "Darwin" or platform_machine != "arm64"',
]

# Development dependencies
DEV_REQUIREMENTS = [
    'pytest>=7.0.0',
    'pytest-cov>=3.0.0',
    'black>=22.3.0',
    'isort>=5.10.1',
    'flake8>=4.0.1',
    'mypy>=1.0.0',
    'pylint>=2.17.0',
]

# Documentation dependencies
DOCS_REQUIREMENTS = [
    'sphinx>=4.0.0',
    'sphinx-rtd-theme>=1.0.0',
    'sphinx-autodoc-typehints>=1.12.0',
]

class VerifyVersionCommand(install):
    """Custom command to verify Python version before installation."""
    def run(self):
        if sys.version_info < (3, 9):
            sys.exit('Python 3.9 or higher is required')
        install.run(self)

setup(
    name='pywallet',
    version=get_version(),
    description='Bitcoin Wallet Management and Recovery Tool',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='BoomerZ Team',
    author_email='info@boomerz.money',
    maintainer='BoomerZ Team',
    maintainer_email='support@boomerz.money',
    url='https://github.com/BoomerZ-money/pywallet3',
    project_urls={
        'Documentation': 'https://pywallet.readthedocs.io/',
        'Source': 'https://github.com/BoomerZ-money/pywallet3',
        'Tracker': 'https://github.com/BoomerZ-money/pywallet3/issues',
        'Original Project': 'https://github.com/jackjack-jj/pywallet',
    },
    packages=find_packages(exclude=['tests*', 'docs*']),
    entry_points={
        'console_scripts': [
            'pywallet=pywallet_refactored.__main__:main',
            'wallet-brute-force=pywallet_refactored.brute_force.__main__:main',
        ],
    },
    install_requires=CORE_REQUIREMENTS,
    extras_require={
        'brute_force': BRUTE_FORCE_REQUIREMENTS,
        'apple_silicon': APPLE_SILICON_REQUIREMENTS,
        'intel': INTEL_REQUIREMENTS,
        'gpu': GPU_REQUIREMENTS,
        'dev': DEV_REQUIREMENTS,
        'docs': DOCS_REQUIREMENTS,
        'all': (
            BRUTE_FORCE_REQUIREMENTS +
            APPLE_SILICON_REQUIREMENTS +
            INTEL_REQUIREMENTS +
            GPU_REQUIREMENTS +
            DEV_REQUIREMENTS +
            DOCS_REQUIREMENTS
        ),
    },
    python_requires='>=3.9',
    cmdclass={
        'install': VerifyVersionCommand,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Recovery Tools',
    ],
    keywords='bitcoin,wallet,cryptocurrency,recovery,brute-force,security',
    license='MIT',
    platforms=['any'],
    include_package_data=True,
    zip_safe=False,
)
