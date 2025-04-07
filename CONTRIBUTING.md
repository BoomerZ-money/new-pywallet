# Contributing to PyWallet

Thank you for considering contributing to PyWallet! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Be patient and welcoming
- Be thoughtful
- Be collaborative
- When disagreeing, try to understand why

## How to Contribute

### Reporting Bugs

If you find a bug in the code, please create an issue on GitHub with the following information:

1. A clear, descriptive title
2. A detailed description of the issue
3. Steps to reproduce the bug
4. Expected behavior
5. Actual behavior
6. Screenshots (if applicable)
7. Environment information (OS, Python version, etc.)

### Suggesting Enhancements

If you have an idea for an enhancement, please create an issue on GitHub with the following information:

1. A clear, descriptive title
2. A detailed description of the enhancement
3. The motivation behind the enhancement
4. Any potential implementation details

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Add or update tests as necessary
5. Update documentation as necessary
6. Run the tests to ensure they pass
7. Submit a pull request

#### Pull Request Process

1. Ensure your code follows the style guidelines
2. Update the README.md or documentation with details of changes if applicable
3. The pull request will be merged once it has been reviewed and approved

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Berkeley DB 4.x
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pywallet.git
   cd pywallet
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Running Tests

Run the tests with:

```bash
python -m unittest discover -s pywallet_refactored/tests
```

Or with pytest:

```bash
pytest pywallet_refactored/tests
```

### Code Style

This project follows PEP 8 style guidelines. You can check your code with:

```bash
flake8 pywallet_refactored
```

And format it with:

```bash
black pywallet_refactored
isort pywallet_refactored
```

## Documentation

### Docstrings

All modules, classes, and functions should have docstrings following the Google style:

```python
def function_with_types_in_docstring(param1, param2):
    """Example function with types documented in the docstring.
    
    Args:
        param1: The first parameter.
        param2: The second parameter.
    
    Returns:
        The return value. True for success, False otherwise.
    
    Raises:
        ValueError: If param1 is None.
    """
    if param1 is None:
        raise ValueError("param1 cannot be None")
    return True
```

### Documentation Updates

When making changes, please update the documentation accordingly:

1. Update docstrings for any modified code
2. Update the README.md if necessary
3. Update the API documentation in the docs/ directory if necessary

## Versioning

We use [Semantic Versioning](https://semver.org/) for versioning. For the versions available, see the tags on this repository.

## License

By contributing to PyWallet, you agree that your contributions will be licensed under the project's MIT License.
