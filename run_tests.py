#!/usr/bin/env python3
"""
Test runner for PyWallet.

This script runs all tests for the PyWallet refactored version.
"""

import unittest
import sys
import os

def run_tests():
    """Run all tests."""
    # Add the current directory to the path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('pywallet_refactored/tests', pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
