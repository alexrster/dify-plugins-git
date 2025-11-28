"""Sync state models"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SyncStatus(str, Enum):
    """Sync status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class SyncState(BaseModel):
    """Sync state model"""
    repository_id: str
    status: SyncStatus = SyncStatus.PENDING
    last_sync: Optional[datetime] = None
    last_success: Optional[datetime] = None
    pending_changes: List[str] = Field(default_factory=list)
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    error_message: Optional[str] = None
    sync_direction: Literal["export", "import", "bidirectional"] = "bidirectional"


