"""Repository management endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..models.repository import RepositoryConfig, Repository
from ..services.git_service import GitService
from ..services.auth_service import AuthService
from ..utils.validators import validate_repository_url, validate_branch_name

router = APIRouter(prefix="/repositories", tags=["repositories"])

# In-memory storage (should use Dify persistent storage in production)
repositories: Dict[str, RepositoryConfig] = {}


class CreateRepositoryRequest(BaseModel):
    name: str
    url: str
    branch: str = "main"
    auth_type: str = "none"
    credentials: Optional[Dict[str, Any]] = None
    auto_sync: bool = False
    sync_interval: int = 60
    workspace_id: str


class UpdateRepositoryRequest(BaseModel):
    name: Optional[str] = None
    branch: Optional[str] = None
    auto_sync: Optional[bool] = None
    sync_interval: Optional[int] = None
    credentials: Optional[Dict[str, Any]] = None


@router.post("", response_model=Dict[str, Any])
async def create_repository(request: CreateRepositoryRequest):
    """Connect a new Git repository"""
    # Validate URL
    if not validate_repository_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid repository URL")
    
    # Validate branch name
    if not validate_branch_name(request.branch):
        raise HTTPException(status_code=400, detail="Invalid branch name")
    
    # Generate repository ID
    import uuid
    repo_id = str(uuid.uuid4())
    
    # Encrypt credentials if provided
    auth_service = AuthService()
    encrypted_credentials = None
    if request.credentials:
        encrypted_credentials = auth_service.encrypt_credentials(request.credentials)
    
    # Create repository config
    config = RepositoryConfig(
        id=repo_id,
        name=request.name,
        url=request.url,
        branch=request.branch,
        auth_type=request.auth_type,
        credentials={"encrypted": encrypted_credentials} if encrypted_credentials else None,
        auto_sync=request.auto_sync,
        sync_interval=request.sync_interval,
        workspace_id=request.workspace_id
    )
    
    # Clone repository
    git_service = GitService()
    try:
        auth_handler = AuthService() if request.auth_type != "none" else None
        repo = git_service.clone_repository(config, auth_handler)
        config.local_path = str(git_service.temp_dir / config.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone repository: {str(e)}")
    
    # Store repository
    repositories[repo_id] = config
    
    return {
        "success": True,
        "repository": config.dict(),
        "message": "Repository connected successfully"
    }


@router.get("", response_model=List[Dict[str, Any]])
async def list_repositories(workspace_id: Optional[str] = None):
    """List connected repositories"""
    repo_list = list(repositories.values())
    
    if workspace_id:
        repo_list = [r for r in repo_list if r.workspace_id == workspace_id]
    
    return [repo.dict() for repo in repo_list]


@router.get("/{repository_id}", response_model=Dict[str, Any])
async def get_repository(repository_id: str):
    """Get repository details"""
    if repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    config = repositories[repository_id]
    git_service = GitService()
    
    try:
        repo = git_service.get_repo(config)
        status = git_service.get_repository_status(repo)
        
        repository = Repository(
            config=config,
            current_branch=status.get("branch"),
            has_changes=status.get("is_dirty", False),
            status="connected"
        )
        
        return repository.dict()
    except Exception as e:
        repository = Repository(
            config=config,
            status="error",
            error_message=str(e)
        )
        return repository.dict()


@router.get("/{repository_id}/status", response_model=Dict[str, Any])
async def get_repository_status(repository_id: str):
    """Get repository status"""
    if repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    config = repositories[repository_id]
    git_service = GitService()
    
    try:
        repo = git_service.get_repo(config)
        status = git_service.get_repository_status(repo)
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.put("/{repository_id}", response_model=Dict[str, Any])
async def update_repository(repository_id: str, request: UpdateRepositoryRequest):
    """Update repository configuration"""
    if repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    config = repositories[repository_id]
    
    # Update fields
    if request.name is not None:
        config.name = request.name
    if request.branch is not None:
        if not validate_branch_name(request.branch):
            raise HTTPException(status_code=400, detail="Invalid branch name")
        config.branch = request.branch
    if request.auto_sync is not None:
        config.auto_sync = request.auto_sync
    if request.sync_interval is not None:
        config.sync_interval = request.sync_interval
    if request.credentials is not None:
        auth_service = AuthService()
        encrypted_credentials = auth_service.encrypt_credentials(request.credentials)
        config.credentials = {"encrypted": encrypted_credentials}
    
    from datetime import datetime
    config.updated_at = datetime.utcnow()
    
    return {
        "success": True,
        "repository": config.dict(),
        "message": "Repository updated successfully"
    }


@router.delete("/{repository_id}", response_model=Dict[str, Any])
async def delete_repository(repository_id: str):
    """Disconnect repository"""
    if repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    del repositories[repository_id]
    
    return {
        "success": True,
        "message": "Repository disconnected successfully"
    }


