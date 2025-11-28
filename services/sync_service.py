"""Synchronization service"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from models.repository import RepositoryConfig
from models.sync import SyncState, SyncStatus
from models.workflow import ApplicationExport, WorkflowExport
from services.dify_api import DifyAPIClient
from services.git_service import GitService


class SyncService:
    """Service for synchronizing Dify workflows/applications with Git"""

    def __init__(self, git_service: GitService, dify_client: DifyAPIClient):
        self.git_service = git_service
        self.dify_client = dify_client
        self.sync_states: Dict[str, SyncState] = {}

    async def export_workflow(
        self, config: RepositoryConfig, workflow_id: str, file_naming: str = "id-name"
    ) -> Dict[str, Any]:
        """Export a workflow to Git"""
        try:
            # Get workflow from Dify
            workflow_data = await self.dify_client.get_workflow(workflow_id)

            # Create export model
            workflow_export = WorkflowExport(
                id=workflow_data.get("id", workflow_id),
                name=workflow_data.get("name", "Unnamed Workflow"),
                data=workflow_data,
                metadata={"exported_by": "dify-git-plugin", "workspace_id": config.workspace_id},
            )

            # Get repository
            repo = self.git_service.get_repo(config)

            # Export to Git
            file_path = self.git_service.export_workflow(repo, workflow_export, file_naming)

            return {
                "success": True,
                "workflow_id": workflow_id,
                "file_path": file_path,
                "message": f"Workflow exported to {file_path}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def export_application(self, config: RepositoryConfig, app_id: str, file_naming: str = "id-name") -> Dict[str, Any]:
        """Export an application to Git"""
        try:
            # Get application from Dify
            app_data = await self.dify_client.get_application(app_id)

            # Create export model
            app_export = ApplicationExport(
                id=app_data.get("id", app_id),
                name=app_data.get("name", "Unnamed Application"),
                data=app_data,
                metadata={"exported_by": "dify-git-plugin", "workspace_id": config.workspace_id},
            )

            # Get repository
            repo = self.git_service.get_repo(config)

            # Export to Git
            file_path = self.git_service.export_application(repo, app_export, file_naming)

            return {
                "success": True,
                "app_id": app_id,
                "file_path": file_path,
                "message": f"Application exported to {file_path}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def export_all(self, config: RepositoryConfig, file_naming: str = "id-name") -> Dict[str, Any]:
        """Export all workflows and applications"""
        results = {"workflows": [], "applications": [], "errors": []}

        try:
            # Export all workflows
            workflows = await self.dify_client.get_all_workflows()
            for workflow in workflows:
                workflow_id = workflow.get("id")
                if workflow_id:
                    result = await self.export_workflow(config, workflow_id, file_naming)
                    results["workflows"].append(result)
                    if not result.get("success"):
                        results["errors"].append(f"Workflow {workflow_id}: {result.get('error')}")

            # Export all applications
            applications = await self.dify_client.get_all_applications()
            for app in applications:
                app_id = app.get("id")
                if app_id:
                    result = await self.export_application(config, app_id, file_naming)
                    results["applications"].append(result)
                    if not result.get("success"):
                        results["errors"].append(f"Application {app_id}: {result.get('error')}")

            results["success"] = len(results["errors"]) == 0
            return results
        except Exception as e:
            return {"success": False, "error": str(e), "results": results}

    async def import_workflow(self, config: RepositoryConfig, file_path: str, auto_merge: bool = True) -> Dict[str, Any]:
        """Import a workflow from Git"""
        try:
            # Get repository
            repo = self.git_service.get_repo(config)

            # Import from Git
            workflow_data = self.git_service.import_workflow(repo, file_path)

            # Check if workflow exists in Dify
            workflow_id = workflow_data.get("id")
            existing_workflow = None

            if workflow_id:
                try:
                    existing_workflow = await self.dify_client.get_workflow(workflow_id)
                except Exception:
                    # Workflow doesn't exist, will create new
                    pass

            # Prepare workflow data for Dify API
            workflow_payload = workflow_data.get("data", {})

            if existing_workflow and auto_merge:
                # Auto-merge: update existing workflow
                result = await self.dify_client.update_workflow(workflow_id, workflow_payload)
                action = "updated"
            elif existing_workflow:
                # Manual merge required
                return {
                    "success": False,
                    "conflict": True,
                    "workflow_id": workflow_id,
                    "message": "Workflow exists, manual merge required",
                }
            else:
                # Create new workflow
                result = await self.dify_client.create_workflow(workflow_payload)
                action = "created"

            return {"success": True, "action": action, "workflow_id": result.get("id", workflow_id), "file_path": file_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def import_application(self, config: RepositoryConfig, file_path: str, auto_merge: bool = True) -> Dict[str, Any]:
        """Import an application from Git"""
        try:
            # Get repository
            repo = self.git_service.get_repo(config)

            # Import from Git
            app_data = self.git_service.import_application(repo, file_path)

            # Check if application exists in Dify
            app_id = app_data.get("id")
            existing_app = None

            if app_id:
                try:
                    existing_app = await self.dify_client.get_application(app_id)
                except Exception:
                    # Application doesn't exist, will create new
                    pass

            # Prepare application data for Dify API
            app_payload = app_data.get("data", {})

            if existing_app and auto_merge:
                # Auto-merge: update existing application
                result = await self.dify_client.update_application(app_id, app_payload)
                action = "updated"
            elif existing_app:
                # Manual merge required
                return {
                    "success": False,
                    "conflict": True,
                    "app_id": app_id,
                    "message": "Application exists, manual merge required",
                }
            else:
                # Create new application
                result = await self.dify_client.create_application(app_payload)
                action = "created"

            return {"success": True, "action": action, "app_id": result.get("id", app_id), "file_path": file_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def import_all(self, config: RepositoryConfig, auto_merge: bool = True) -> Dict[str, Any]:
        """Import all workflows and applications from Git"""
        results = {"workflows": [], "applications": [], "errors": []}

        try:
            # Get repository
            repo = self.git_service.get_repo(config)

            # List all exported files
            files = self.git_service.list_exported_files(repo)

            # Import workflows
            for file_path in files.get("workflows", []):
                result = await self.import_workflow(config, file_path, auto_merge)
                results["workflows"].append(result)
                if not result.get("success"):
                    results["errors"].append(f"Workflow {file_path}: {result.get('error', 'Unknown error')}")

            # Import applications
            for file_path in files.get("applications", []):
                result = await self.import_application(config, file_path, auto_merge)
                results["applications"].append(result)
                if not result.get("success"):
                    results["errors"].append(f"Application {file_path}: {result.get('error', 'Unknown error')}")

            results["success"] = len(results["errors"]) == 0
            return results
        except Exception as e:
            return {"success": False, "error": str(e), "results": results}

    def get_sync_state(self, repository_id: str) -> Optional[SyncState]:
        """Get sync state for repository"""
        return self.sync_states.get(repository_id)

    def update_sync_state(self, repository_id: str, state: SyncState) -> None:
        """Update sync state"""
        self.sync_states[repository_id] = state
