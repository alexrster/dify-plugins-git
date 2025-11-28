"""Tests for validators"""

import pytest

from utils.validators import sanitize_filename, validate_branch_name, validate_repository_url


def test_validate_repository_url():
    """Test repository URL validation"""
    # Valid URLs
    assert validate_repository_url("https://github.com/user/repo.git")
    assert validate_repository_url("http://github.com/user/repo.git")
    assert validate_repository_url("git@github.com:user/repo.git")
    assert validate_repository_url("git://github.com/user/repo.git")

    # Invalid URLs
    assert not validate_repository_url("")
    assert not validate_repository_url("not-a-url")
    assert not validate_repository_url("ftp://example.com/repo.git")


def test_validate_branch_name():
    """Test branch name validation"""
    # Valid branch names
    assert validate_branch_name("main")
    assert validate_branch_name("feature/new-feature")
    assert validate_branch_name("bugfix-123")
    assert validate_branch_name("release/v1.0.0")

    # Invalid branch names
    assert not validate_branch_name("")
    assert not validate_branch_name("branch with spaces")
    assert not validate_branch_name("branch~name")
    assert not validate_branch_name(".hidden")
    assert not validate_branch_name("branch.lock")


def test_sanitize_filename():
    """Test filename sanitization"""
    assert sanitize_filename("workflow-123") == "workflow-123"
    assert sanitize_filename("workflow:123") == "workflow_123"
    assert sanitize_filename("workflow/123") == "workflow_123"
    assert sanitize_filename("  workflow  ") == "workflow"
    assert sanitize_filename(".workflow") == "workflow"
