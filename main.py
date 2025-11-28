"""
Dify Git Integration Plugin
Main entry point for the plugin
"""

import os
import sys
from typing import Any, Dict

from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.plugin import Plugin
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize plugin configuration
config = DifyPluginEnv()

# Initialize plugin
plugin = Plugin(config)

# Start the plugin - this will start all threads and keep running
# This is a blocking call that keeps the plugin alive
plugin.run()
