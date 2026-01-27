"""List Git Branches Tool"""

from typing import Any

from dify_plugin import Tool

from models.repository import RepositoryConfig
from services.git_service import GitService


class ListBranchesTool(Tool):
    """Tool for listing Git branches"""

    def _invoke(self, tool_parameters: dict[str, Any]):
        """
        Invoke the list branches tool.

        Args:
            tool_parameters: Tool parameters (none required)

        Yields:
            ToolInvokeMessage with the result
        """
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

        # Initialize service
        git_service = GitService()

        try:
            # Get repository
            repo = git_service.clone_repository(config, None)
            config.local_path = str(git_service.temp_dir / config.id)

            # List branches
            branches = git_service.get_branches(repo)

            if branches:
                branch_list = "\n".join([f"{'* ' if b.get('is_current') else '  '}{b.get('name')}" for b in branches])
                yield self.create_text_message(f"📋 Available branches:\n\n{branch_list}")
            else:
                yield self.create_text_message("No branches found")

        except Exception as e:
            yield self.create_text_message(f"❌ Error: {str(e)}")
