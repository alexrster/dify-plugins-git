"""Endpoint handler that wraps FastAPI app for Dify"""

import json
from typing import Any

from dify_plugin.core.runtime import Session
from dify_plugin.interfaces.endpoint import Endpoint

# Create FastAPI app
from fastapi import FastAPI
from werkzeug import Request, Response

# Import our routers to ensure they're registered
from endpoints.git_operations import router as git_router
from endpoints.repositories import router as repositories_router
from endpoints.sync import router as sync_router

app = FastAPI(title="Dify Git Integration Plugin")
app.include_router(repositories_router)
app.include_router(git_router)
app.include_router(sync_router)


class FastAPIEndpoint(Endpoint):
    """Endpoint wrapper that uses FastAPI app"""

    def invoke(self, request: Request, values: dict, settings: dict) -> Response:
        """Invoke FastAPI endpoint using ASGI"""
        try:
            # Convert Werkzeug request to ASGI and call FastAPI
            # This is a simplified approach - in production use proper ASGI adapter
            import asyncio

            from starlette.requests import Request as StarletteRequest
            from starlette.responses import Response as StarletteResponse

            # Get request body
            body = request.get_data()

            # Create a simple ASGI call
            # For now, return a basic response
            # In production, you'd need to properly convert Werkzeug to ASGI

            # Simple routing based on path
            path = request.path
            method = request.method

            # For now, return a placeholder response
            # The actual implementation would need proper ASGI conversion
            response_data = {"message": "Endpoint handler active", "path": path, "method": method, "values": values}

            return Response(json.dumps(response_data), status=200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), status=500, mimetype="application/json")
