# CI/CD Setup Summary

This document describes the GitHub Actions CI/CD workflows and development tools that have been set up for the Dify Git Integration Plugin.

## 🚀 Workflows Created

### 1. **CI Workflow** (`.github/workflows/ci.yml`)
Main continuous integration workflow that runs on every push and PR.

**Features:**
- ✅ Multi-platform testing (Ubuntu, macOS, Windows)
- ✅ Multi-version Python testing (3.12, 3.13)
- ✅ Code linting (flake8, black, isort, pylint)
- ✅ Security scanning (bandit, safety)
- ✅ Plugin packaging
- ✅ Markdown linting
- ✅ Code coverage reporting

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

### 2. **Release Workflow** (`.github/workflows/release.yml`)
Automated release process when tags are pushed.

**Features:**
- ✅ Automatic version extraction from tags
- ✅ Manifest version update
- ✅ Plugin packaging (.difypkg format)
- ✅ GitHub release creation
- ✅ Changelog generation
- ✅ Artifact upload

**Usage:**
```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0

# Or trigger manually via GitHub UI
```

### 3. **CodeQL Analysis** (`.github/workflows/codeql.yml`)
Automated security vulnerability scanning.

**Features:**
- ✅ Python code analysis
- ✅ Security vulnerability detection
- ✅ Weekly scheduled scans
- ✅ PR and push triggers

### 4. **Nightly Tests** (`.github/workflows/nightly.yml`)
Comprehensive daily testing.

**Features:**
- ✅ Full test suite execution
- ✅ All linters
- ✅ Security scans
- ✅ Coverage reports
- ✅ Runs daily at 2 AM UTC

### 5. **Documentation Checks** (`.github/workflows/docs.yml`)
Validates markdown documentation.

**Features:**
- ✅ Link checking
- ✅ Markdown linting
- ✅ Runs on markdown file changes

## 📋 Additional Files

### Development Dependencies
- **`requirements-dev.txt`**: Development dependencies (testing, linting, security tools)

### Configuration Files
- **`.flake8`**: Flake8 linting configuration
- **`pyproject.toml`**: Unified configuration for black, isort, pylint, mypy, pytest, coverage
- **`pytest.ini`**: Pytest configuration (already existed, kept)

### GitHub Templates
- **`.github/PULL_REQUEST_TEMPLATE.md`**: PR template with checklist
- **`.github/ISSUE_TEMPLATE/bug_report.md`**: Bug report template
- **`.github/ISSUE_TEMPLATE/feature_request.md`**: Feature request template
- **`.github/dependabot.yml`**: Automated dependency updates

### Development Tools
- **`Makefile`**: Convenient commands for local development
  - `make install-dev` - Install dev dependencies
  - `make test` - Run tests
  - `make lint` - Run linters
  - `make format` - Format code
  - `make security` - Run security checks
  - `make ci` - Run all CI checks
  - `make build` - Build plugin package

### Documentation
- **`CONTRIBUTING.md`**: Contribution guidelines
- **`.github/workflows/README.md`**: Workflow documentation

## 🛠️ Local Development

### Quick Start

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Run all CI checks locally
make ci
```

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make install` | Install production dependencies |
| `make install-dev` | Install development dependencies |
| `make test` | Run tests with coverage |
| `make lint` | Run all linters |
| `make format` | Format code (black, isort) |
| `make security` | Run security checks |
| `make clean` | Clean build artifacts |
| `make build` | Build plugin package |
| `make ci` | Run all CI checks |
| `make pre-commit` | Run pre-commit checks |

## 🔒 Security Features

1. **Bandit**: Scans for common security issues in Python code
2. **Safety**: Checks dependencies for known vulnerabilities
3. **CodeQL**: Advanced security analysis by GitHub
4. **Dependabot**: Automated dependency updates with security patches

## 📊 Coverage & Quality

- **Code Coverage**: Tracked via pytest-cov and Codecov
- **Code Quality**: Multiple linters ensure consistent code style
- **Type Checking**: mypy for type safety (optional)
- **Documentation**: Markdown linting and link checking

## 🚦 Workflow Status

Add these badges to your README.md:

```markdown
![CI](https://github.com/YOUR_USERNAME/dify-plugins-git/workflows/CI/badge.svg)
![Release](https://github.com/YOUR_USERNAME/dify-plugins-git/workflows/Release/badge.svg)
![CodeQL](https://github.com/YOUR_USERNAME/dify-plugins-git/workflows/CodeQL%20Analysis/badge.svg)
![Nightly](https://github.com/YOUR_USERNAME/dify-plugins-git/workflows/Nightly%20Tests/badge.svg)
```

## 📝 Next Steps

1. **Enable workflows**: Push to GitHub to activate workflows
2. **Configure Codecov** (optional): Add `CODECOV_TOKEN` secret for coverage reports
3. **Set up branch protection**: Protect `main` branch to require CI checks
4. **Review Dependabot**: Dependabot will automatically create PRs for dependency updates

## 🔧 Customization

### Adjust Python Versions
Edit `.github/workflows/ci.yml`:
```yaml
python-version: ['3.12', '3.13']  # Modify as needed
```

### Adjust Linting Rules
Edit `.flake8` or `pyproject.toml` for specific linting configurations.

### Add More Tests
Add test files to `tests/` directory. They'll be automatically discovered by pytest.

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)

## ✅ Checklist

- [x] CI workflow with testing
- [x] Release workflow
- [x] Security scanning (CodeQL, Bandit, Safety)
- [x] Code quality checks (linting, formatting)
- [x] Documentation validation
- [x] Development dependencies
- [x] Makefile for local development
- [x] PR and issue templates
- [x] Dependabot configuration
- [x] Contributing guidelines

---

**All CI/CD workflows are ready to use!** 🎉


