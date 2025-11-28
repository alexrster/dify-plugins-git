"""Dify API client service"""

import os
from typing import Any, Dict, List, Optional

import httpx


class DifyAPIClient:
    """Client for interacting with Dify API"""

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url or os.getenv("DIFY_API_URL", "http://localhost:5001")
        self.api_key = api_key or os.getenv("DIFY_API_KEY", "")
        self.base_url = f"{self.api_url}/api/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Dify API"""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def list_workflows(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """List workflows"""
        return await self._request("GET", "/workflows", params={"page": page, "limit": limit})

    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow details"""
        return await self._request("GET", f"/workflows/{workflow_id}")

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow"""
        return await self._request("POST", "/workflows", json=workflow_data)

    async def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workflow"""
        return await self._request("PUT", f"/workflows/{workflow_id}", json=workflow_data)

    async def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete a workflow"""
        return await self._request("DELETE", f"/workflows/{workflow_id}")

    async def list_applications(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """List applications"""
        return await self._request("GET", "/apps", params={"page": page, "limit": limit})

    async def get_application(self, app_id: str) -> Dict[str, Any]:
        """Get application details"""
        return await self._request("GET", f"/apps/{app_id}")

    async def create_application(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new application"""
        return await self._request("POST", "/apps", json=app_data)

    async def update_application(self, app_id: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing application"""
        return await self._request("PUT", f"/apps/{app_id}", json=app_data)

    async def delete_application(self, app_id: str) -> Dict[str, Any]:
        """Delete an application"""
        return await self._request("DELETE", f"/apps/{app_id}")

    async def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows (paginated)"""
        all_workflows = []
        page = 1
        limit = 50

        while True:
            result = await self.list_workflows(page=page, limit=limit)
            workflows = result.get("data", [])
            all_workflows.extend(workflows)

            if len(workflows) < limit:
                break
            page += 1

        return all_workflows

    async def get_all_applications(self) -> List[Dict[str, Any]]:
        """Get all applications (paginated)"""
        all_apps = []
        page = 1
        limit = 50

        while True:
            result = await self.list_applications(page=page, limit=limit)
            apps = result.get("data", [])
            all_apps.extend(apps)

            if len(apps) < limit:
                break
            page += 1

        return all_apps
