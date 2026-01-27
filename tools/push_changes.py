"""Push Changes to Remote Git Tool"""

from typing import Any

from dify_plugin import Tool

from models.repository import RepositoryConfig
from services.auth_service import AuthService
from services.git_service import GitService


class PushChangesTool(Tool):
    """Tool for pushing changes to remote Git repository"""

    def _invoke(self, tool_parameters: dict[str, Any]):
        """
        Invoke the push changes tool.

        Args:
            tool_parameters: Tool parameters including branch

        Yields:
            ToolInvokeMessage with the result
        """
        branch = tool_parameters.get("branch")

        # Get credentials from runtime
        credentials = self.runtime.credentials

        # Create repository config
        config = RepositoryConfig(
            id="tool-runtime",
            name="Git Integration",
            url=credentials.get("repository_url"),
            branch=branch or credentials.get("branch", "main"),
            auth_type=credentials.get("auth_type", "none"),
            credentials={"token": credentials.get("github_token")} if credentials.get("github_token") else None,
            workspace_id="default",
        )

        # Initialize services
        git_service = GitService()
        auth_service = AuthService()

        try:
            # Get repository
            repo = git_service.clone_repository(config, None)
            config.local_path = str(git_service.temp_dir / config.id)

            # Push changes
            auth_handler = auth_service if config.auth_type != "none" else None
            result = git_service.push(repo, config.branch, config.auth_type, auth_handler)

            if result.get("success"):
                yield self.create_text_message(
                    f"✅ Changes pushed successfully!\n"
                    f"Branch: {config.branch}\n"
                    f"Remote: {result.get('remote', 'origin')}"
                )
            else:
                yield self.create_text_message(f"❌ Push failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            yield self.create_text_message(f"❌ Error: {str(e)}")
