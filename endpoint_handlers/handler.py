"""Endpoint handler that wraps FastAPI app for Dify"""

import asyncio
import json
import re
from typing import Any, Dict, Optional, Tuple

from dify_plugin.core.runtime import Session
from dify_plugin.interfaces.endpoint import Endpoint
from werkzeug import Request, Response

from endpoint_handlers.git_operations import (
    CheckoutRequest,
    CommitRequest,
    CreateBranchRequest,
    DiffRequest,
    PullRequest,
    PushRequest,
    checkout_branch,
    commit_changes,
    create_branch,
    create_pull_request,
    get_commit_history,
    get_diff,
    list_branches,
    pull_changes,
    push_changes,
)

# Import handler functions and models
from endpoint_handlers.repositories import (
    CreateRepositoryRequest,
    LinkApplicationRequest,
    UpdateRepositoryRequest,
    create_repository,
    delete_repository,
    get_application_repository,
    get_repository,
    get_repository_status,
    link_application_to_repository,
    list_repositories,
    unlink_application,
    update_repository,
)
from endpoint_handlers.sync import (
    ExportAllRequest,
    ExportApplicationRequest,
    ExportWorkflowRequest,
    ImportAllRequest,
    ImportApplicationRequest,
    ImportWorkflowRequest,
    SyncRequest,
    export_all,
    export_application,
    export_workflow,
    get_sync_status,
    import_all,
    import_application,
    import_workflow,
    sync_repository,
)


class FastAPIEndpoint(Endpoint):
    """Endpoint wrapper that uses FastAPI app"""

    def _match_path(self, pattern: str, path: str) -> Optional[Dict[str, str]]:
        """
        Match a path against a pattern with parameters (e.g. /users/{id})
        Returns a dictionary of parameters if matched, None otherwise.
        """
        # Convert {param} to (?P<param>[^/]+)
        regex_pattern = re.sub(r"{([^}]+)}", r"(?P<\1>[^/]+)", pattern)
        regex_pattern = f"^{regex_pattern}$"

        match = re.match(regex_pattern, path)
        if match:
            return match.groupdict()
        return None

    def _invoke(self, request: Request, values: dict, settings: dict) -> Response:
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

            # --- Repositories Endpoints ---

            # POST /repositories
            if method == "POST" and path == "/repositories":
                import uuid

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

                create_req = CreateRepositoryRequest(
                    name=repo_name,
                    url=repo_url,
                    branch=branch,
                    auth_type=auth_type,
                    credentials=credentials,
                    auto_sync=auto_sync,
                    sync_interval=sync_interval,
                    workspace_id=workspace_id,
                )
                result = asyncio.run(create_repository(create_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # GET /repositories
            if method == "GET" and path == "/repositories":
                workspace_id = request.args.get("workspace_id") if hasattr(request, "args") else None
                result = asyncio.run(list_repositories(workspace_id))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /repositories/link-application
            if method == "POST" and path == "/repositories/link-application":
                link_req = LinkApplicationRequest(**request_data)
                result = asyncio.run(link_application_to_repository(link_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # GET /repositories/application/{application_id}
            params = self._match_path("/repositories/application/{application_id}", path)
            if method == "GET" and params:
                result = asyncio.run(get_application_repository(params["application_id"]))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # DELETE /repositories/application/{application_id}/unlink
            params = self._match_path("/repositories/application/{application_id}/unlink", path)
            if method == "DELETE" and params:
                result = asyncio.run(unlink_application(params["application_id"]))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # GET /repositories/{id}/status
            params = self._match_path("/repositories/{id}/status", path)
            if method == "GET" and params:
                result = asyncio.run(get_repository_status(params["id"]))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # GET /repositories/{id}
            params = self._match_path("/repositories/{id}", path)
            if method == "GET" and params:
                result = asyncio.run(get_repository(params["id"]))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # PUT /repositories/{id}
            params = self._match_path("/repositories/{id}", path)
            if method == "PUT" and params:
                update_req = UpdateRepositoryRequest(**request_data)
                result = asyncio.run(update_repository(params["id"], update_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # DELETE /repositories/{id}
            params = self._match_path("/repositories/{id}", path)
            if method == "DELETE" and params:
                result = asyncio.run(delete_repository(params["id"]))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # --- Git Operations Endpoints ---

            # POST /git/commit
            if method == "POST" and path == "/git/commit":
                commit_req = CommitRequest(**request_data)
                result = asyncio.run(commit_changes(commit_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /git/push
            if method == "POST" and path == "/git/push":
                push_req = PushRequest(**request_data)
                result = asyncio.run(push_changes(push_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /git/pull
            if method == "POST" and path == "/git/pull":
                pull_req = PullRequest(**request_data)
                result = asyncio.run(pull_changes(pull_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # GET /git/{repository_id}/branches
            params = self._match_path("/git/{repository_id}/branches", path)
            if method == "GET" and params:
                result = asyncio.run(list_branches(params["repository_id"]))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /git/branches
            if method == "POST" and path == "/git/branches":
                branch_req = CreateBranchRequest(**request_data)
                result = asyncio.run(create_branch(branch_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /git/checkout
            if method == "POST" and path == "/git/checkout":
                checkout_req = CheckoutRequest(**request_data)
                result = asyncio.run(checkout_branch(checkout_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # GET /git/{repository_id}/history
            params = self._match_path("/git/{repository_id}/history", path)
            if method == "GET" and params:
                limit = int(request.args.get("limit", 20)) if hasattr(request, "args") else 20
                result = asyncio.run(get_commit_history(params["repository_id"], limit))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /git/diff
            if method == "POST" and path == "/git/diff":
                diff_req = DiffRequest(**request_data)
                result = asyncio.run(get_diff(diff_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /git/pr
            if method == "POST" and path == "/git/pr":
                repository_id = request_data.get("repository_id")
                title = request_data.get("title")
                description = request_data.get("description")
                base_branch = request_data.get("base_branch")
                head_branch = request_data.get("head_branch")
                result = asyncio.run(create_pull_request(repository_id, title, description, base_branch, head_branch))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # --- Sync Endpoints ---

            # POST /sync/export/workflow
            if method == "POST" and path == "/sync/export/workflow":
                export_wf_req = ExportWorkflowRequest(**request_data)
                result = asyncio.run(export_workflow(export_wf_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /sync/export/application
            if method == "POST" and path == "/sync/export/application":
                export_app_req = ExportApplicationRequest(**request_data)
                result = asyncio.run(export_application(export_app_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /sync/export/all
            if method == "POST" and path == "/sync/export/all":
                export_all_req = ExportAllRequest(**request_data)
                result = asyncio.run(export_all(export_all_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /sync/import/workflow
            if method == "POST" and path == "/sync/import/workflow":
                import_wf_req = ImportWorkflowRequest(**request_data)
                result = asyncio.run(import_workflow(import_wf_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /sync/import/application
            if method == "POST" and path == "/sync/import/application":
                import_app_req = ImportApplicationRequest(**request_data)
                result = asyncio.run(import_application(import_app_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /sync/import/all
            if method == "POST" and path == "/sync/import/all":
                import_all_req = ImportAllRequest(**request_data)
                result = asyncio.run(import_all(import_all_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # POST /sync
            if method == "POST" and path == "/sync":
                sync_req = SyncRequest(**request_data)
                result = asyncio.run(sync_repository(sync_req))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # GET /sync/{repository_id}/status
            params = self._match_path("/sync/{repository_id}/status", path)
            if method == "GET" and params:
                result = asyncio.run(get_sync_status(params["repository_id"]))
                return Response(json.dumps(result), status=200, mimetype="application/json")

            # 404 Not Found
            return Response(
                json.dumps({"error": f"Endpoint not found: {method} {path}"}), status=404, mimetype="application/json"
            )

        except Exception as e:
            import traceback

            error_details = {"error": str(e), "traceback": traceback.format_exc()}
            return Response(json.dumps(error_details), status=500, mimetype="application/json")
