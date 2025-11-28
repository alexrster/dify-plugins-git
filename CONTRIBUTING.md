# Contributing to Dify Git Integration Plugin

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dify-plugins-git.git
   cd dify-plugins-git
   ```

3. **Set up development environment:**
   ```bash
   make install-dev
   # or
   pip install -r requirements-dev.txt
   ```

4. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_validators.py -v
```

### Code Quality

Before committing, run:

```bash
# Format code
make format

# Run linters
make lint

# Run security checks
make security

# Run all CI checks
make ci
```

### Pre-commit Checks

```bash
make pre-commit
```

This runs formatting, linting, and tests.

## Code Style

- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for all public functions/classes
- Keep line length to 127 characters
- Use `black` for code formatting
- Use `isort` for import sorting

### Example

```python
from typing import Optional, Dict, Any

def example_function(param: str, optional: Optional[int] = None) -> Dict[str, Any]:
    """
    Example function with proper type hints and docstring.
    
    Args:
        param: Required parameter description
        optional: Optional parameter description
    
    Returns:
        Dictionary with results
    """
    return {"result": "example"}
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### Examples

```
feat: add support for GitLab repositories
fix: resolve authentication token expiration issue
docs: update installation instructions
test: add tests for branch management
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features or bug fixes
3. **Ensure all tests pass:**
   ```bash
   make test
   ```
4. **Run linting:**
   ```bash
   make lint
   ```
5. **Update CHANGELOG.md** (if applicable)
6. **Create pull request** with clear description

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts
- [ ] CI checks passing

## Testing Guidelines

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Test both success and error cases
- Mock external dependencies (Git, Dify API)

### Test Structure

```python
def test_feature_name():
    """Test description"""
    # Arrange
    # Act
    # Assert
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation if endpoints change
- Include examples in docstrings

## Issue Reporting

When reporting bugs or requesting features:

1. Check existing issues first
2. Use appropriate issue template
3. Provide clear description
4. Include steps to reproduce (for bugs)
5. Add relevant logs/error messages

## Code Review

- Be respectful and constructive
- Focus on code, not the person
- Explain reasoning for suggestions
- Respond to feedback promptly

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues/PRs

Thank you for contributing! 🎉


