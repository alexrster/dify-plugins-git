"""
Dify Git Integration Plugin
Main entry point for the plugin
"""

import os
from typing import Any, Dict

from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.plugin import Plugin
from dotenv import load_dotenv
from fastapi import FastAPI

from endpoints.git_operations import router as git_router
from endpoints.repositories import router as repositories_router
from endpoints.sync import router as sync_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Dify Git Integration Plugin")

# Register routers
app.include_router(repositories_router)
app.include_router(git_router)
app.include_router(sync_router)

# Initialize plugin configuration
config = DifyPluginEnv()

# Initialize plugin
plugin = Plugin(config)


if __name__ == "__main__":
    # Plugin will run automatically
    pass
