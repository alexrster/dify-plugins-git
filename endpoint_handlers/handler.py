"""Endpoint handler that wraps FastAPI app for Dify"""

import asyncio
import json
from typing import Any

from dify_plugin.core.runtime import Session
from dify_plugin.interfaces.endpoint import Endpoint

# Create FastAPI app
from fastapi import FastAPI
from werkzeug import Request, Response

# Import our routers to ensure they're registered
from endpoint_handlers.git_operations import router as git_router
from endpoint_handlers.repositories import router as repositories_router
from endpoint_handlers.sync import router as sync_router

app = FastAPI(title="Dify Git Integration Plugin")
app.include_router(repositories_router)
app.include_router(git_router)
app.include_router(sync_router)


class FastAPIEndpoint(Endpoint):
    """Endpoint wrapper that uses FastAPI app"""

    def invoke(self, request: Request, values: dict, settings: dict) -> Response:
        """Invoke FastAPI endpoint using ASGI"""
        try:
            # Get request body
            body = request.get_data()
            path = request.path
            method = request.method

            # Parse request body if available
            request_data = {}
            if body:
                try:
                    request_data = json.loads(body.decode("utf-8"))
                except:
                    pass

            # Handle POST /repositories - create repository connection
            if method == "POST" and path == "/repositories":
                import uuid

                from endpoint_handlers.repositories import CreateRepositoryRequest, create_repository

                # Merge settings from UI with request data (request data takes precedence)
                repo_name = request_data.get("name") or f"Repository-{uuid.uuid4().hex[:8]}"
                repo_url = request_data.get("url") or settings.get("repository_url", "")
                branch = request_data.get("branch") or settings.get("branch", "main")
                auth_type = request_data.get("auth_type") or settings.get("auth_type", "none")
                github_token = request_data.get("github_token") or settings.get("github_token")
                auto_sync = (
                    request_data.get("auto_sync", False)
                    if "auto_sync" in request_data
                    else (settings.get("auto_sync", False) if isinstance(settings.get("auto_sync"), bool) else False)
                )
                sync_interval = (
                    request_data.get("sync_interval", 60)
                    if "sync_interval" in request_data
                    else int(settings.get("sync_interval", 60)) if settings.get("sync_interval") else 60
                )

                # Get workspace_id from request or use default
                workspace_id = request_data.get("workspace_id", "default")

                # Prepare credentials
                credentials = None
                if auth_type == "token" and github_token:
                    credentials = {"token": github_token}
                elif request_data.get("credentials"):
                    credentials = request_data.get("credentials")

                # Validate URL is provided
                if not repo_url:
                    return Response(
                        json.dumps(
                            {
                                "error": "Repository URL is required. Please configure it in plugin settings or provide it in the request."
                            }
                        ),
                        status=400,
                        mimetype="application/json",
                    )

                # Create repository request
                create_request = CreateRepositoryRequest(
                    name=repo_name,
                    url=repo_url,
                    branch=branch,
                    auth_type=auth_type,
                    credentials=credentials,
                    auto_sync=auto_sync,
                    sync_interval=sync_interval,
                    workspace_id=workspace_id,
                )

                # Call the create_repository function
                result = asyncio.run(create_repository(create_request))

                return Response(json.dumps(result), status=200, mimetype="application/json")

            # Handle GET /repositories - list repositories
            elif method == "GET" and path == "/repositories":
                from endpoint_handlers.repositories import list_repositories

                workspace_id = request.args.get("workspace_id") if hasattr(request, "args") else None
                result = asyncio.run(list_repositories(workspace_id))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # For other endpoints, return placeholder for now
            response_data = {
                "message": "Endpoint handler active",
                "path": path,
                "method": method,
                "values": values,
                "settings_available": bool(settings),
                "note": "Full FastAPI routing will be implemented with proper ASGI conversion",
            }

            return Response(json.dumps(response_data), status=200, mimetype="application/json")
        except Exception as e:
            import traceback

            error_details = {"error": str(e), "traceback": traceback.format_exc()}
            return Response(json.dumps(error_details), status=500, mimetype="application/json")
