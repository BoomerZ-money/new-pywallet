# PyWallet Testing Guide

This document provides detailed information about the PyWallet test suite, how to run tests, and how to write new tests.

## Table of Contents

- [Overview](#overview)
- [Running Tests](#running-tests)
  - [Running All Tests](#running-all-tests)
  - [Running Specific Tests](#running-specific-tests)
  - [Test Coverage](#test-coverage)
- [Test Structure](#test-structure)
  - [Basic Tests](#basic-tests)
  - [Integration Tests](#integration-tests)
- [Writing New Tests](#writing-new-tests)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests-1)
  - [Test Fixtures](#test-fixtures)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Overview

PyWallet includes a comprehensive test suite to ensure the reliability and correctness of its functionality. The tests are organized into two main categories:

1. **Basic Tests**: Unit tests for core functionality and utility functions
2. **Integration Tests**: End-to-end tests for command-line interface and complete workflows

## Running Tests

### Running All Tests

To run the complete test suite:

```bash
python -m unittest discover -s tests
```

This command will discover and run all tests in the `tests` directory and its subdirectories.

### Running Specific Tests

To run specific test modules:

```bash
# Run integration tests
python -m unittest tests.test_pywallet_refactored

# Run basic unit tests
python -m unittest pywallet_refactored.tests.test_basic
```

To run a specific test case or test method:

```bash
# Run a specific test case
python -m unittest tests.test_pywallet_refactored.TestPyWalletRefactored

# Run a specific test method
python -m unittest tests.test_pywallet_refactored.TestPyWalletRefactored.test_dump_wallet
```

### Test Coverage

To run tests with coverage reporting (requires pytest and pytest-cov):

```bash
python -m pytest --cov=pywallet_refactored tests/
```

This will generate a coverage report showing which parts of the code are covered by tests and which are not.

## Test Structure

### Basic Tests

Basic tests are located in the `pywallet_refactored/tests/` directory. These tests focus on individual components and functions of the PyWallet codebase.

Key test files include:

- `test_basic.py`: Tests for core functionality and utility functions
- `test_crypto.py`: Tests for cryptographic functions
- `test_wallet.py`: Tests for wallet database operations

### Integration Tests

Integration tests are located in the `tests/` directory. These tests focus on end-to-end functionality and command-line interface.

Key test files include:

- `test_pywallet_refactored.py`: Tests for the main command-line interface and complete workflows

## Writing New Tests

### Unit Tests

When writing unit tests for PyWallet, follow these guidelines:

1. Create a new test file in the `pywallet_refactored/tests/` directory if testing a specific module
2. Use the `unittest` framework
3. Create a test class that inherits from `unittest.TestCase`
4. Write test methods that start with `test_`
5. Use assertions to verify expected behavior
6. Use mocks to isolate the code being tested

Example:

```python
import unittest
from unittest.mock import patch
from pywallet_refactored.crypto import keys

class TestKeys(unittest.TestCase):
    def test_generate_key_pair(self):
        # Test that a key pair is generated correctly
        key_pair = keys.generate_key_pair()
        self.assertIn('address', key_pair)
        self.assertIn('wif', key_pair)
        self.assertIn('public_key', key_pair)
        self.assertIn('private_key', key_pair)
```

### Integration Tests

When writing integration tests for PyWallet, follow these guidelines:

1. Create a new test file in the `tests/` directory
2. Use the `unittest` framework
3. Create a test class that inherits from `unittest.TestCase`
4. Write test methods that start with `test_`
5. Use `setUp` and `tearDown` methods to set up and clean up test fixtures
6. Use `patch` to mock external dependencies like API calls
7. Test complete workflows from command-line to output

Example:

```python
import unittest
import os
import tempfile
from unittest.mock import patch
from pywallet_refactored.__main__ import main

class TestCommandLine(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_wallet_path = os.path.join(self.test_dir, "test_wallet.dat")
        self.test_output_json = os.path.join(self.test_dir, "output.json")
        
    def tearDown(self):
        # Clean up test files
        for file in [self.test_wallet_path, self.test_output_json]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.test_dir)
        
    def test_dump_wallet(self):
        # Mock sys.argv to simulate command line arguments
        with patch('sys.argv', ['pywallet_refactored.py', 'dump',
                               f'--wallet={self.test_wallet_path}',
                               f'--output={self.test_output_json}']):
            try:
                main()
                # If we get here without exceptions, the test passes
            except SystemExit as e:
                # Some commands exit with sys.exit(), which is expected
                self.assertEqual(e.code, 0)
```

### Test Fixtures

Test fixtures are resources needed for tests, such as sample wallet files, key files, or mock data. Store test fixtures in the `tests/fixtures/` directory.

When using test fixtures:

1. Load fixtures in the `setUp` method
2. Clean up fixtures in the `tearDown` method
3. Use relative paths to ensure tests work in any environment

## Continuous Integration

PyWallet uses continuous integration to automatically run tests on every commit and pull request. This ensures that changes don't break existing functionality.

The CI pipeline runs:

1. Linting checks (flake8)
2. Unit tests
3. Integration tests
4. Coverage reporting

## Troubleshooting

### Common Test Issues

#### Tests Failing Due to Missing Dependencies

If tests are failing due to missing dependencies, ensure all development dependencies are installed:

```bash
pip install -r requirements-dev.txt
```

#### Tests Failing Due to File Permissions

If tests are failing due to file permission issues, ensure the test user has write access to the test directory.

#### Tests Hanging or Taking Too Long

If tests are hanging or taking too long, it may be due to:

1. Network requests not being properly mocked
2. Infinite loops in the code
3. Resource leaks (e.g., files not being closed)

Use the `-v` flag to get more verbose output:

```bash
python -m unittest discover -s tests -v
```

#### Tests Failing Intermittently

If tests are failing intermittently, it may be due to:

1. Race conditions
2. Dependency on external services
3. Time-dependent code

Try to make tests more deterministic by:

1. Mocking external dependencies
2. Using fixed timestamps
3. Adding appropriate delays or synchronization
