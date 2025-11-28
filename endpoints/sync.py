"""Synchronization endpoints"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..endpoints.repositories import repositories
from ..models.repository import RepositoryConfig
from ..services.auth_service import AuthService
from ..services.dify_api import DifyAPIClient
from ..services.git_service import GitService
from ..services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


class ExportWorkflowRequest(BaseModel):
    repository_id: str
    workflow_id: str
    file_naming: Optional[str] = "id-name"


class ExportApplicationRequest(BaseModel):
    repository_id: str
    app_id: str
    file_naming: Optional[str] = "id-name"


class ExportAllRequest(BaseModel):
    repository_id: str
    file_naming: Optional[str] = "id-name"


class ImportWorkflowRequest(BaseModel):
    repository_id: str
    file_path: str
    auto_merge: bool = True


class ImportApplicationRequest(BaseModel):
    repository_id: str
    file_path: str
    auto_merge: bool = True


class ImportAllRequest(BaseModel):
    repository_id: str
    auto_merge: bool = True


class SyncRequest(BaseModel):
    repository_id: str
    direction: Optional[str] = "bidirectional"  # export, import, bidirectional


@router.post("/export/workflow", response_model=Dict[str, Any])
async def export_workflow(request: ExportWorkflowRequest):
    """Export a workflow to Git"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()
    dify_client = DifyAPIClient()
    sync_service = SyncService(git_service, dify_client)

    try:
        result = await sync_service.export_workflow(config, request.workflow_id, request.file_naming)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/application", response_model=Dict[str, Any])
async def export_application(request: ExportApplicationRequest):
    """Export an application to Git"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()
    dify_client = DifyAPIClient()
    sync_service = SyncService(git_service, dify_client)

    try:
        result = await sync_service.export_application(config, request.app_id, request.file_naming)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/all", response_model=Dict[str, Any])
async def export_all(request: ExportAllRequest):
    """Export all workflows and applications"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()
    dify_client = DifyAPIClient()
    sync_service = SyncService(git_service, dify_client)

    try:
        result = await sync_service.export_all(config, request.file_naming)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/workflow", response_model=Dict[str, Any])
async def import_workflow(request: ImportWorkflowRequest):
    """Import a workflow from Git"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()
    dify_client = DifyAPIClient()
    sync_service = SyncService(git_service, dify_client)

    try:
        result = await sync_service.import_workflow(config, request.file_path, request.auto_merge)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/application", response_model=Dict[str, Any])
async def import_application(request: ImportApplicationRequest):
    """Import an application from Git"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()
    dify_client = DifyAPIClient()
    sync_service = SyncService(git_service, dify_client)

    try:
        result = await sync_service.import_application(config, request.file_path, request.auto_merge)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/all", response_model=Dict[str, Any])
async def import_all(request: ImportAllRequest):
    """Import all workflows and applications from Git"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()
    dify_client = DifyAPIClient()
    sync_service = SyncService(git_service, dify_client)

    try:
        result = await sync_service.import_all(config, request.auto_merge)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=Dict[str, Any])
async def sync_repository(request: SyncRequest):
    """Manual sync trigger"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()
    dify_client = DifyAPIClient()
    sync_service = SyncService(git_service, dify_client)

    try:
        results = {}

        if request.direction in ["export", "bidirectional"]:
            # Pull latest from Git first
            repo = git_service.get_repo(config)
            git_service.pull(repo, config.branch)

            # Export all
            export_result = await sync_service.export_all(config)
            results["export"] = export_result

        if request.direction in ["import", "bidirectional"]:
            # Import all
            import_result = await sync_service.import_all(config, auto_merge=True)
            results["import"] = import_result

        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/status", response_model=Dict[str, Any])
async def get_sync_status(repository_id: str):
    """Get sync status"""
    if repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    git_service = GitService()
    sync_service = SyncService(git_service, DifyAPIClient())

    sync_state = sync_service.get_sync_state(repository_id)

    if sync_state:
        return sync_state.dict()
    else:
        return {"repository_id": repository_id, "status": "pending", "message": "No sync state available"}
