"""Input validation utilities"""

import re
from pathlib import Path
from urllib.parse import urlparse


def validate_repository_url(url: str) -> bool:
    """Validate Git repository URL"""
    if not url:
        return False

    # Check for common Git URL patterns
    patterns = [
        r"^https?://.+",  # HTTP/HTTPS
        r"^git@.+:.+",  # SSH
        r"^git://.+",  # Git protocol
        r"^file://.+",  # Local file
    ]

    for pattern in patterns:
        if re.match(pattern, url):
            return True

    return False


def validate_branch_name(branch: str) -> bool:
    """Validate Git branch name"""
    if not branch:
        return False

    # Git branch naming rules
    # Cannot contain: spaces, ~, ^, :, ?, *, [, \, @, {, }
    invalid_chars = r"[ ~^:?*\[\\@{]"
    if re.search(invalid_chars, branch):
        return False

    # Cannot start with . or end with .lock
    if branch.startswith(".") or branch.endswith(".lock"):
        return False

    # Cannot be a single dot or double dots
    if branch in [".", ".."]:
        return False

    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "_", filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]

    return sanitized


def validate_file_path(file_path: str, base_dir: Path) -> bool:
    """Validate file path to prevent directory traversal"""
    try:
        full_path = (base_dir / file_path).resolve()
        base_resolved = base_dir.resolve()

        # Check if resolved path is within base directory
        return str(full_path).startswith(str(base_resolved))
    except Exception:
        return False
