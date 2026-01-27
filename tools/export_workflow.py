"""Export Workflow to Git Tool"""

import json
from typing import Any

from dify_plugin import Tool

from models.repository import RepositoryConfig
from models.workflow import WorkflowExport
from services.auth_service import AuthService
from services.git_service import GitService


class ExportWorkflowTool(Tool):
    """Tool for exporting Dify workflows to Git"""

    def _invoke(self, tool_parameters: dict[str, Any]):
        """
        Invoke the export workflow tool.
        
        Args:
            tool_parameters: Tool parameters including workflow_id, file_naming, and commit_message
            
        Yields:
            ToolInvokeMessage with the result
        """
        # Get app/workflow ID - ALWAYS use session app_id (current workflow context)
        # The workflow_id parameter is ignored because we're already in a workflow context
        app_id = self.session.app_id
        file_naming = tool_parameters.get("file_naming", "id-name")
        commit_message = tool_parameters.get("commit_message", "Export workflow")
        
        if not app_id:
            yield self.create_text_message(
                "❌ No app/workflow ID available from session context. "
                "This tool must be used within a workflow/app context."
            )
            return
        
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
        auth_service = AuthService()
        
        # Create auth handler if credentials are provided
        auth_handler = None
        if config.auth_type != "none" and config.credentials:
            # Decrypt credentials if needed and set up auth handler
            if isinstance(config.credentials, dict) and "encrypted" in config.credentials:
                try:
                    decrypted_creds = auth_service.decrypt_credentials(config.credentials["encrypted"])
                    # Store decrypted credentials in auth_service for use
                    auth_service._decrypted_credentials = decrypted_creds
                except Exception as e:
                    yield self.create_text_message(
                        f"❌ Failed to decrypt credentials: {str(e)}"
                    )
                    return
            elif isinstance(config.credentials, dict) and "token" in config.credentials:
                # Store token directly
                auth_service._decrypted_credentials = config.credentials
            auth_handler = auth_service
        
        try:
            # Get workflow/app data from session using app_id
            try:
                workflow_data = self.session.app.fetch_app(app_id)
                
                # Handle case where fetch_app returns None or empty
                if workflow_data is None:
                    yield self.create_text_message(
                        f"❌ Workflow data is None. The app/workflow may not exist or may not be accessible.\\n"
                        f"App ID: {app_id}\\n"
                        f"Note: Make sure you're using this tool within a valid workflow/app context."
                    )
                    return
                
                # Handle case where fetch_app returns a string (JSON) instead of dict
                if isinstance(workflow_data, str):
                    if not workflow_data.strip():
                        yield self.create_text_message(
                            f"❌ Empty workflow data returned.\\n"
                            f"App ID: {app_id}"
                        )
                        return
                    try:
                        workflow_data = json.loads(workflow_data)
                    except json.JSONDecodeError:
                        yield self.create_text_message(
                            f"❌ Invalid workflow data format returned from API.\\n"
                            f"Expected JSON dict, got: {type(workflow_data).__name__}\\n"
                            f"Data: {workflow_data[:200]}..."
                        )
                        return
                
                # Ensure workflow_data is a dict-like object
                if not isinstance(workflow_data, dict):
                    yield self.create_text_message(
                        f"❌ Unexpected workflow data type: {type(workflow_data).__name__}\\n"
                        f"Expected dict, got: {workflow_data}"
                    )
                    return
                    
            except Exception as e:
                error_msg = str(e)
                # Provide more helpful error messages
                if "data is nil" in error_msg or "nil" in error_msg.lower():
                    yield self.create_text_message(
                        f"❌ Cannot access workflow data: The app/workflow was not found or is not accessible.\\n"
                        f"App ID: {app_id}\\n"
                        f"Error: {error_msg}\\n"
                        f"\\n"
                        f"Note: This tool automatically uses the current workflow/app context. "
                        f"If you're seeing this error, the workflow may not be properly initialized."
                    )
                else:
                    yield self.create_text_message(
                        f"❌ Cannot access workflow data: {error_msg}\\n"
                        f"App ID: {app_id}\\n"
                        f"Note: This tool requires access to Dify's internal app API."
                    )
                return
            
            # Extract workflow information from the data
            # The workflow_data might be nested or have different structure
            workflow_id = workflow_data.get("id") or workflow_data.get("app_id") or app_id
            workflow_name = workflow_data.get("name") or workflow_data.get("app_name") or "Unnamed Workflow"
            
            # Ensure workflow_id and workflow_name are strings
            workflow_id = str(workflow_id) if workflow_id else str(app_id)
            workflow_name = str(workflow_name) if workflow_name else "Unnamed Workflow"
            
            # Create export model
            try:
                workflow_export = WorkflowExport(
                    id=workflow_id,
                    name=workflow_name,
                    data=workflow_data,
                    metadata={"exported_by": "dify-git-plugin", "workspace_id": "default"},
                )
            except Exception as e:
                yield self.create_text_message(
                    f"❌ Failed to create workflow export model: {str(e)}\\n"
                    f"Workflow ID: {workflow_id}\\n"
                    f"Workflow Name: {workflow_name}\\n"
                    f"Name type: {type(workflow_name).__name__}"
                )
                return
            
            # Clone/get repository with auth handler
            repo = git_service.clone_repository(config, auth_handler)
            config.local_path = str(git_service.temp_dir / config.id)
            
            # Export workflow to file
            file_path = git_service.export_workflow(repo, workflow_export, file_naming)
            
            # Commit changes
            author = {
                "name": self.runtime.user_id or "Dify User",
                "email": f"{self.runtime.user_id or 'user'}@dify.local"
            }
            commit_result = git_service.commit(repo, commit_message, author)
            
            # Check if commit was successful
            if not commit_result.get("success"):
                error_msg = commit_result.get("error", "Unknown error")
                yield self.create_text_message(
                    f"⚠️ Workflow exported to file but commit failed:\\n"
                    f"File: {file_path}\\n"
                    f"Error: {error_msg}\\n"
                    f"\\n"
                    f"Note: The file was created locally but not committed to Git."
                )
                return
            
            commit_hash = commit_result.get("commit_hash", "N/A")
            
            # Push changes to remote
            push_result = git_service.push(repo, config.branch, config.auth_type, auth_handler)
            
            if push_result.get("success"):
                yield self.create_text_message(
                    f"✅ Workflow exported and pushed successfully!\\n"
                    f"File: {file_path}\\n"
                    f"Commit: {commit_hash[:7] if commit_hash != 'N/A' else 'N/A'}\\n"
                    f"Branch: {push_result.get('branch', config.branch)}\\n"
                    f"\\n"
                    f"The workflow has been committed and pushed to the remote repository."
                )
            else:
                push_error = push_result.get("error", "Unknown error")
                yield self.create_text_message(
                    f"⚠️ Workflow exported and committed but push failed:\\n"
                    f"File: {file_path}\\n"
                    f"Commit: {commit_hash[:7] if commit_hash != 'N/A' else 'N/A'}\\n"
                    f"Push Error: {push_error}\\n"
                    f"\\n"
                    f"Note: The workflow was committed locally but could not be pushed to the remote. "
                    f"You may need to check your authentication settings."
                )
                
        except Exception as e:
            yield self.create_text_message(f"❌ Error: {str(e)}")
