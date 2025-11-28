"""Logging configuration"""

import logging
import os
from typing import Optional


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration"""
    log_level = level or os.getenv("PLUGIN_LOG_LEVEL", "INFO")

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger("dify_git_plugin")
    return logger
