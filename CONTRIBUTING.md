# Contributing to PyVenice

First off, thank you for considering contributing to PyVenice! It's people like you that make PyVenice such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct: be respectful, inclusive, and considerate of others.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed and explain why it's a problem**
* **Explain which behavior you expected to see instead**
* **Include your Python version and PyVenice version**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Provide specific examples to demonstrate the enhancement**
* **Describe the current behavior and explain why it's insufficient**
* **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code follows the style guidelines.
6. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/PyVenice.git
cd PyVenice

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
black .
ruff check .
```

## Style Guidelines

### Python Style

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use [Black](https://github.com/psf/black) for code formatting
* Use [Ruff](https://github.com/astral-sh/ruff) for linting
* Write docstrings for all public functions, classes, and modules
* Use type hints for all function parameters and return values

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Testing

* Write tests for all new functionality
* Maintain or improve code coverage (currently at 82%)
* Use pytest for all tests
* Mock external API calls - don't make real requests in unit tests
* Use the `@pytest.mark.integration` decorator for tests that require API keys

## Project Structure

```
pyvenice/
├── pyvenice/          # Main package
│   ├── client.py      # Base HTTP client
│   ├── chat.py        # Chat completions endpoint
│   ├── models.py      # Models endpoint
│   └── ...            # Other endpoint modules
├── tests/             # Test suite
│   ├── conftest.py    # Pytest configuration
│   └── test_*.py      # Test modules
├── docs/              # Documentation
└── examples/          # Usage examples
```

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a pull request with these changes
4. After merging, create a GitHub release
5. The package will be automatically published to PyPI

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing! 🎉