# GitHub Actions Workflows

This directory contains CI/CD workflows for the Dify Git Integration Plugin.

## Workflows

### `ci.yml` - Continuous Integration
Runs on every push and pull request to main/develop branches.

**Jobs:**
- **test**: Runs tests on multiple OS (Ubuntu, macOS, Windows) and Python versions (3.12, 3.13)
- **lint**: Runs code quality checks (flake8, black, isort, pylint)
- **security**: Runs security scans (bandit, safety)
- **build**: Validates manifest and builds plugin package

### `release.yml` - Release Workflow
Runs when a tag is pushed (v*) or manually triggered.

**Features:**
- Updates manifest version
- Packages the plugin
- Creates GitHub release with artifacts
- Generates changelog

**Usage:**
```bash
# Automatic (on tag push)
git tag v1.0.0
git push origin v1.0.0

# Manual (via GitHub UI)
# Go to Actions > Release > Run workflow
```

### `codeql.yml` - CodeQL Security Analysis
Runs automated security analysis using GitHub's CodeQL.

- Runs on push/PR to main/develop
- Weekly scheduled scan
- Analyzes Python code for security vulnerabilities

### `nightly.yml` - Nightly Tests
Runs comprehensive tests daily at 2 AM UTC.

- Full test suite with coverage
- All linters
- Security scans
- Uploads coverage reports


## Workflow Status Badges

Add these badges to your README.md:

```markdown
![CI](https://github.com/YOUR_USERNAME/dify-plugins-git/workflows/CI/badge.svg)
![Release](https://github.com/YOUR_USERNAME/dify-plugins-git/workflows/Release/badge.svg)
![CodeQL](https://github.com/YOUR_USERNAME/dify-plugins-git/workflows/CodeQL%20Analysis/badge.svg)
```

## Local Development

Run CI checks locally using the Makefile:

```bash
make ci          # Run all CI checks
make lint        # Run linters
make test        # Run tests
make security    # Run security checks
make format      # Format code
```

## Secrets and Variables

No secrets required for basic workflows. For advanced features:

- `CODECOV_TOKEN`: (Optional) For code coverage reporting
- `GITHUB_TOKEN`: (Auto-provided) For releases and PR comments

## Dependencies

Workflows use:
- Python 3.12, 3.13
- Ubuntu, macOS, Windows runners
- Standard GitHub Actions marketplace actions

## Troubleshooting

### Tests failing
- Check Python version compatibility
- Verify all dependencies are in `requirements.txt` and `requirements-dev.txt`

### Build failing
- Ensure `manifest.yaml` is valid YAML
- Check that all required files are present

### Release failing
- Verify tag format: `v*` (e.g., `v1.0.0`)
- Check GitHub token permissions


