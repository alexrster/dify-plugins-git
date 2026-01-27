"""Create Git Branch Tool"""

from typing import Any

from dify_plugin import Tool

from models.repository import RepositoryConfig
from services.git_service import GitService


class CreateBranchTool(Tool):
    """Tool for creating Git branches"""

    def _invoke(self, tool_parameters: dict[str, Any]):
        """
        Invoke the create branch tool.
        
        Args:
            tool_parameters: Tool parameters including branch_name and from_branch
            
        Yields:
            ToolInvokeMessage with the result
        """
        branch_name = tool_parameters.get("branch_name")
        from_branch = tool_parameters.get("from_branch")
        
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
            
            # Create branch
            result = git_service.create_branch(repo, branch_name, from_branch)
            
            if result.get("success"):
                yield self.create_text_message(
                    f"✅ Branch created successfully!\n"
                    f"Branch: {branch_name}\n"
                    f"From: {from_branch or 'current branch'}"
                )
            else:
                yield self.create_text_message(
                    f"❌ Branch creation failed: {result.get('error', 'Unknown error')}"
                )
                
        except Exception as e:
            yield self.create_text_message(f"❌ Error: {str(e)}")
