"""Git Integration Tool Provider"""

from typing import Any

from dify_plugin import ToolProvider


class GitIntegrationProvider(ToolProvider):
    """Git Integration tool provider for managing workflows and applications with version control"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate the credentials for the Git integration provider.
        
        Args:
            credentials: Provider credentials containing repository_url, branch, auth_type, and github_token
            
        Raises:
            ValueError: If credentials are invalid
        """
        repository_url = credentials.get("repository_url")
        if not repository_url:
            raise ValueError("Repository URL is required")
        
        auth_type = credentials.get("auth_type", "none")
        if auth_type == "token":
            github_token = credentials.get("github_token")
            if not github_token:
                raise ValueError("GitHub token is required when using token authentication")
        
        # Validate repository URL format
        if not (repository_url.startswith("http://") or 
                repository_url.startswith("https://") or 
                repository_url.startswith("git@")):
            raise ValueError("Invalid repository URL format")
