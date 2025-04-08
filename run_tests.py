#!/usr/bin/env python3
"""
Test runner for PyWallet.

This script runs all tests for the PyWallet refactored version.
"""

import unittest
import sys
import os
import argparse

def run_tests(verbose=True):
    """Run all tests."""
    # Add the current directory to the path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Discover and run tests
    test_loader = unittest.TestLoader()

    # Run the tests directly
    test_suite = unittest.TestSuite()

    # Add tests from pywallet_refactored/tests
    try:
        module_tests = test_loader.discover('pywallet_refactored/tests', pattern='test_*.py')
        test_suite.addTest(module_tests)
    except ImportError as e:
        print(f"Warning: Could not load tests from pywallet_refactored/tests: {e}")

    # Add tests from tests directory
    try:
        root_tests = test_loader.discover('tests', pattern='test_*.py')
        test_suite.addTest(root_tests)
    except ImportError as e:
        print(f"Warning: Could not load tests from tests: {e}")

    # Run tests with specified verbosity
    test_runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = test_runner.run(test_suite)

    return result.wasSuccessful()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run pywallet_refactored tests')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet output')
    args = parser.parse_args()

    verbose = not args.quiet if args.quiet else True
    success = run_tests(verbose=verbose)
    sys.exit(0 if success else 1)
