"""Import Workflow from Git Tool"""

from typing import Any

from dify_plugin import Tool

from models.repository import RepositoryConfig
from services.dify_api import DifyAPIClient
from services.git_service import GitService
from services.sync_service import SyncService


class ImportWorkflowTool(Tool):
    """Tool for importing Dify workflows from Git"""

    def _invoke(self, tool_parameters: dict[str, Any]):
        """
        Invoke the import workflow tool.

        Args:
            tool_parameters: Tool parameters including file_path and auto_merge

        Yields:
            ToolInvokeMessage with the result
        """
        file_path = tool_parameters.get("file_path")
        auto_merge = tool_parameters.get("auto_merge", True)

        # Get credentials from runtime
        credentials = self.runtime.credentials

        # Create repository config
        config = RepositoryConfig(
            id="tool-runtime",
            name="Git Integration",
            url=credentials.get("repository_url"),
            branch=credentials.get("branch", "main"),
            auth_type=credentials.get("auth_type", "none"),
            credentials={"token": credentials.get("github_token")} if credentials.get("github_token") else None,
            workspace_id="default",
        )

        # Initialize services
        git_service = GitService()
        dify_client = DifyAPIClient()
        sync_service = SyncService(git_service, dify_client)

        try:
            # Clone/get repository
            repo = git_service.clone_repository(config, None)
            config.local_path = str(git_service.temp_dir / config.id)

            # Pull latest changes
            git_service.pull(repo, config.branch)

            # Import workflow
            result = sync_service.import_workflow_sync(config, file_path, auto_merge)

            if result.get("success"):
                yield self.create_text_message(
                    f"✅ Workflow imported successfully!\n"
                    f"Workflow ID: {result.get('workflow_id', 'N/A')}\n"
                    f"Name: {result.get('workflow_name', 'N/A')}"
                )
            else:
                yield self.create_text_message(f"❌ Import failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            yield self.create_text_message(f"❌ Error: {str(e)}")
