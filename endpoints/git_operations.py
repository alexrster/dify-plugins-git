"""Git operations endpoints"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .repositories import repositories
from models.repository import RepositoryConfig
from services.auth_service import AuthService
from services.git_service import GitService

router = APIRouter(prefix="/git", tags=["git"])


class CommitRequest(BaseModel):
    repository_id: str
    message: str
    author: Optional[Dict[str, str]] = None


class PushRequest(BaseModel):
    repository_id: str
    branch: Optional[str] = None


class PullRequest(BaseModel):
    repository_id: str
    branch: Optional[str] = None


class CreateBranchRequest(BaseModel):
    repository_id: str
    branch_name: str
    from_branch: Optional[str] = None


class CheckoutRequest(BaseModel):
    repository_id: str
    branch_name: str


class DiffRequest(BaseModel):
    repository_id: str
    commit1: Optional[str] = None
    commit2: Optional[str] = None


@router.post("/commit", response_model=Dict[str, Any])
async def commit_changes(request: CommitRequest):
    """Commit changes to Git repository"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()
    auth_service = AuthService()

    try:
        repo = git_service.get_repo(config)
        result = git_service.commit(repo, request.message, request.author)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Commit failed"))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push", response_model=Dict[str, Any])
async def push_changes(request: PushRequest):
    """Push changes to remote repository"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()
    auth_service = AuthService()

    try:
        repo = git_service.get_repo(config)

        # Decrypt credentials if needed
        auth_handler = None
        if config.auth_type != "none" and config.credentials:
            auth_handler = auth_service

        result = git_service.push(repo, request.branch, config.auth_type, auth_handler)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Push failed"))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pull", response_model=Dict[str, Any])
async def pull_changes(request: PullRequest):
    """Pull latest changes from remote repository"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()

    try:
        repo = git_service.get_repo(config)
        result = git_service.pull(repo, request.branch or config.branch)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Pull failed"))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/branches", response_model=List[Dict[str, Any]])
async def list_branches(repository_id: str):
    """List all branches"""
    if repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[repository_id]
    git_service = GitService()

    try:
        repo = git_service.get_repo(config)
        branches = git_service.get_branches(repo)
        return branches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/branches", response_model=Dict[str, Any])
async def create_branch(request: CreateBranchRequest):
    """Create a new branch"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()

    try:
        repo = git_service.get_repo(config)
        result = git_service.create_branch(repo, request.branch_name, request.from_branch)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create branch"))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout", response_model=Dict[str, Any])
async def checkout_branch(request: CheckoutRequest):
    """Checkout a branch"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()

    try:
        repo = git_service.get_repo(config)
        result = git_service.checkout_branch(repo, request.branch_name)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to checkout branch"))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repository_id}/history", response_model=List[Dict[str, Any]])
async def get_commit_history(repository_id: str, limit: int = 20):
    """Get commit history"""
    if repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[repository_id]
    git_service = GitService()

    try:
        repo = git_service.get_repo(config)
        history = git_service.get_commit_history(repo, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diff", response_model=Dict[str, Any])
async def get_diff(request: DiffRequest):
    """Get diff between commits or working directory"""
    if request.repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[request.repository_id]
    git_service = GitService()

    try:
        repo = git_service.get_repo(config)
        diff = git_service.get_diff(repo, request.commit1, request.commit2)
        return {"success": True, "diff": diff}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pr", response_model=Dict[str, Any])
async def create_pull_request(repository_id: str, title: str, description: str, base_branch: str, head_branch: str):
    """
    Create a pull request (merge request)
    Note: This is a placeholder for PR functionality.
    Actual PR creation depends on Git provider API (GitHub, GitLab, etc.)
    For generic Git, this would create a merge commit or prepare for manual PR.
    """
    if repository_id not in repositories:
        raise HTTPException(status_code=404, detail="Repository not found")

    config = repositories[repository_id]
    git_service = GitService()

    try:
        repo = git_service.get_repo(config)

        # For generic Git, we'll create a merge commit
        # In a full implementation, this would call provider-specific APIs
        repo.git.checkout(base_branch)
        repo.git.merge(head_branch, no_ff=True, m=f"{title}\n\n{description}")

        return {
            "success": True,
            "message": "Merge created successfully",
            "note": "For GitHub/GitLab, use provider-specific API for PR creation",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
