"""Workflow and Application export models"""
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class WorkflowExport(BaseModel):
    """Workflow export model"""
    id: str
    name: str
    type: str = "workflow"
    data: Dict[str, Any] = Field(..., description="Workflow data from Dify API")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"


class ApplicationExport(BaseModel):
    """Application export model"""
    id: str
    name: str
    type: str = "application"
    data: Dict[str, Any] = Field(..., description="Application data from Dify API")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"


