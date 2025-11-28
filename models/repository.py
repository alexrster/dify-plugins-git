"""Repository models"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


class RepositoryConfig(BaseModel):
    """Repository configuration"""
    id: str
    name: str
    url: str = Field(..., description="Git repository URL")
    branch: str = Field(default="main", description="Default branch")
    auth_type: Literal["ssh", "token", "none"] = Field(default="none")
    credentials: Optional[dict] = Field(default=None, description="Encrypted credentials")
    auto_sync: bool = Field(default=False, description="Enable auto-sync (opt-in)")
    sync_interval: int = Field(default=60, description="Sync interval in minutes")
    workspace_id: str
    local_path: Optional[str] = Field(default=None, description="Local repository path")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Repository(BaseModel):
    """Repository model with status"""
    config: RepositoryConfig
    current_branch: Optional[str] = None
    last_sync: Optional[datetime] = None
    has_changes: bool = False
    has_conflicts: bool = False
    status: Literal["connected", "disconnected", "error"] = "disconnected"
    error_message: Optional[str] = None


