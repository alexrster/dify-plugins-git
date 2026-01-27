"""Commit Changes to Git Tool"""

from typing import Any

from dify_plugin import Tool

from models.repository import RepositoryConfig
from services.git_service import GitService


class CommitChangesTool(Tool):
    """Tool for committing changes to Git"""

    def _invoke(self, tool_parameters: dict[str, Any]):
        """
        Invoke the commit changes tool.

        Args:
            tool_parameters: Tool parameters including message, author_name, and author_email

        Yields:
            ToolInvokeMessage with the result
        """
        message = tool_parameters.get("message")
        if not message:
            yield self.create_text_message("❌ Commit message is required")
            return

        # Get author info with proper defaults
        user_id = getattr(self.runtime, "user_id", None) or "Dify User"
        author_name = tool_parameters.get("author_name") or str(user_id)
        author_email = tool_parameters.get("author_email") or f"{user_id}@dify.local"

        # Ensure author_name and author_email are strings
        author_name = str(author_name) if author_name else "Dify User"
        author_email = str(author_email) if author_email else "dify@example.com"

        # Get credentials from runtime
        credentials = self.runtime.credentials or {}

        # Validate required credentials
        if not credentials.get("repository_url"):
            yield self.create_text_message(
                "❌ Repository URL is required. Please configure it in the Git Integration tool settings."
            )
            return

        # Create repository config
        try:
            config = RepositoryConfig(
                id="tool-runtime",
                name="Git Integration",
                url=str(credentials.get("repository_url", "")),
                branch=str(credentials.get("branch", "main")),
                auth_type=credentials.get("auth_type", "none") or "none",
                credentials={"token": credentials.get("github_token")} if credentials.get("github_token") else None,
                workspace_id="default",
            )
        except Exception as e:
            yield self.create_text_message(f"❌ Failed to create repository config: {str(e)}")
            return

        # Initialize service
        git_service = GitService()

        try:
            # Get repository
            repo = git_service.clone_repository(config, None)
            config.local_path = str(git_service.temp_dir / config.id)

            # Commit changes - ensure author is a dict with string values
            author = {"name": str(author_name), "email": str(author_email)}

            # Validate author dict
            if (
                not isinstance(author, dict)
                or not isinstance(author.get("name"), str)
                or not isinstance(author.get("email"), str)
            ):
                yield self.create_text_message(f"❌ Invalid author information: {author}")
                return

            result = git_service.commit(repo, str(message), author)

            if result.get("success"):
                yield self.create_text_message(
                    f"✅ Changes committed successfully!\\n"
                    f"Commit: {result.get('commit_hash', 'N/A')}\\n"
                    f"Message: {message}"
                )
            else:
                error_msg = result.get("error", "Unknown error")
                yield self.create_text_message(f"❌ Commit failed: {error_msg}")

        except Exception as e:
            import traceback

            error_details = f"{str(e)}"
            # Add more context if it's an attribute error
            if "'str' object has no attribute" in str(e):
                error_details += f"\\n\\nDebug info:\\n"
                error_details += f"- message type: {type(message).__name__}\\n"
                error_details += f"- author type: {type(author).__name__}\\n"
                error_details += f"- author value: {author}\\n"
                error_details += f"- config type: {type(config).__name__}\\n"
            yield self.create_text_message(f"❌ Error: {error_details}")
