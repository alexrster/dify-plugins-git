"""
Dify Git Integration Plugin
Main entry point for the plugin
"""

import os
from typing import Any, Dict

from dify_plugin_sdk import ExtensionPlugin, Plugin
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

# Initialize plugin
plugin = ExtensionPlugin(
    name="git-integration", version="0.1.0", description="Git integration for managing Dify workflows and applications"
)


@plugin.on_activate
async def on_activate(config: Dict[str, Any]) -> None:
    """Called when the plugin is activated"""
    print("Git Integration Plugin activated")
    # Initialize services if needed
    # Store configuration
    plugin.config = config


@plugin.on_deactivate
async def on_deactivate() -> None:
    """Called when the plugin is deactivated"""
    print("Git Integration Plugin deactivated")


# Register FastAPI app with plugin
plugin.register_app(app)


if __name__ == "__main__":
    plugin.run()
