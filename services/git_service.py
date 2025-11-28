"""Git operations service"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from git import GitCommandError, InvalidGitRepositoryError, Repo
from git.exc import GitError

from models.repository import RepositoryConfig
from models.workflow import ApplicationExport, WorkflowExport


class GitService:
    """Service for Git operations"""

    def __init__(self, temp_dir: str = "./temp/git"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def clone_repository(self, config: RepositoryConfig, auth_handler=None) -> Repo:
        """Clone a Git repository"""
        repo_path = self.temp_dir / config.id

        if repo_path.exists():
            # Repository already exists, try to open it
            try:
                return Repo(repo_path)
            except InvalidGitRepositoryError:
                # Remove invalid repository
                import shutil

                shutil.rmtree(repo_path)

        # Clone repository
        try:
            if config.auth_type == "ssh" and auth_handler:
                with auth_handler.get_ssh_environment():
                    repo = Repo.clone_from(config.url, repo_path)
            elif config.auth_type == "token" and auth_handler:
                # Use token in URL
                url_with_token = auth_handler.add_token_to_url(config.url)
                repo = Repo.clone_from(url_with_token, repo_path)
            else:
                repo = Repo.clone_from(config.url, repo_path)

            # Checkout default branch
            if config.branch:
                repo.git.checkout(config.branch)

            return repo
        except GitCommandError as e:
            raise Exception(f"Failed to clone repository: {str(e)}")

    def get_repo(self, config: RepositoryConfig) -> Repo:
        """Get existing repository instance"""
        repo_path = self.temp_dir / config.id
        if not repo_path.exists():
            raise Exception(f"Repository not found at {repo_path}")

        try:
            return Repo(repo_path)
        except InvalidGitRepositoryError:
            raise Exception(f"Invalid Git repository at {repo_path}")

    def pull(self, repo: Repo, branch: Optional[str] = None) -> Dict[str, Any]:
        """Pull latest changes from remote"""
        try:
            if branch:
                repo.git.checkout(branch)

            # Fetch and pull
            repo.remotes.origin.fetch()
            before_commit = repo.head.commit.hexsha
            repo.remotes.origin.pull()
            after_commit = repo.head.commit.hexsha

            return {
                "success": True,
                "updated": before_commit != after_commit,
                "before_commit": before_commit,
                "after_commit": after_commit,
            }
        except GitCommandError as e:
            return {"success": False, "error": str(e)}

    def commit(self, repo: Repo, message: str, author: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Commit changes to repository"""
        try:
            # Check if there are changes
            if repo.is_dirty() or repo.untracked_files:
                # Add all changes
                repo.git.add(A=True)

                # Commit
                if author:
                    repo.index.commit(
                        message, author=f"{author.get('name', 'Dify')} <{author.get('email', 'dify@example.com')}>"
                    )
                else:
                    repo.index.commit(message)

                return {"success": True, "commit_hash": repo.head.commit.hexsha, "message": message}
            else:
                return {"success": False, "error": "No changes to commit"}
        except GitCommandError as e:
            return {"success": False, "error": str(e)}

    def push(self, repo: Repo, branch: Optional[str] = None, auth_type: str = "none", auth_handler=None) -> Dict[str, Any]:
        """Push changes to remote"""
        try:
            branch = branch or repo.active_branch.name

            if auth_type == "ssh" and auth_handler:
                with auth_handler.get_ssh_environment():
                    repo.remotes.origin.push(branch)
            else:
                repo.remotes.origin.push(branch)

            return {"success": True, "branch": branch}
        except GitCommandError as e:
            return {"success": False, "error": str(e)}

    def get_branches(self, repo: Repo) -> List[Dict[str, Any]]:
        """Get list of branches"""
        try:
            branches = []
            for branch in repo.branches:
                branches.append(
                    {
                        "name": branch.name,
                        "is_current": branch == repo.active_branch,
                        "commit": branch.commit.hexsha[:7],
                        "message": branch.commit.message.split("\n")[0],
                    }
                )

            # Add remote branches
            for remote in repo.remotes:
                for branch in remote.refs:
                    if branch.name not in [b["name"] for b in branches]:
                        branches.append(
                            {
                                "name": branch.name.replace(f"{remote.name}/", ""),
                                "is_current": False,
                                "is_remote": True,
                                "commit": branch.commit.hexsha[:7],
                                "message": branch.commit.message.split("\n")[0],
                            }
                        )

            return branches
        except Exception as e:
            raise Exception(f"Failed to get branches: {str(e)}")

    def create_branch(self, repo: Repo, branch_name: str, from_branch: Optional[str] = None) -> Dict[str, Any]:
        """Create a new branch"""
        try:
            if from_branch:
                repo.git.checkout(from_branch)

            new_branch = repo.create_head(branch_name)
            new_branch.checkout()

            return {"success": True, "branch": branch_name}
        except GitCommandError as e:
            return {"success": False, "error": str(e)}

    def checkout_branch(self, repo: Repo, branch_name: str) -> Dict[str, Any]:
        """Checkout a branch"""
        try:
            repo.git.checkout(branch_name)
            return {"success": True, "branch": branch_name}
        except GitCommandError as e:
            return {"success": False, "error": str(e)}

    def get_commit_history(self, repo: Repo, limit: int = 20) -> List[Dict[str, Any]]:
        """Get commit history"""
        try:
            commits = []
            for commit in repo.iter_commits(max_count=limit):
                commits.append(
                    {
                        "hash": commit.hexsha,
                        "short_hash": commit.hexsha[:7],
                        "message": commit.message.split("\n")[0],
                        "author": f"{commit.author.name} <{commit.author.email}>",
                        "date": datetime.fromtimestamp(commit.committed_date).isoformat(),
                    }
                )
            return commits
        except Exception as e:
            raise Exception(f"Failed to get commit history: {str(e)}")

    def get_diff(self, repo: Repo, commit1: Optional[str] = None, commit2: Optional[str] = None) -> str:
        """Get diff between commits or working directory"""
        try:
            if commit1 and commit2:
                return repo.git.diff(commit1, commit2)
            elif commit1:
                return repo.git.diff(commit1)
            else:
                return repo.git.diff()
        except GitCommandError as e:
            raise Exception(f"Failed to get diff: {str(e)}")

    def export_workflow(self, repo: Repo, workflow: WorkflowExport, file_naming: str = "id-name") -> str:
        """Export workflow to Git repository"""
        workflows_dir = Path(repo.working_dir) / "workflows"
        workflows_dir.mkdir(exist_ok=True)

        # Determine filename
        if file_naming == "id":
            filename = f"workflow-{workflow.id}.json"
        elif file_naming == "name":
            # Sanitize name for filename
            safe_name = "".join(c for c in workflow.name if c.isalnum() or c in (" ", "-", "_")).strip()
            filename = f"workflow-{safe_name}.json"
        else:  # id-name
            safe_name = "".join(c for c in workflow.name if c.isalnum() or c in (" ", "-", "_")).strip()
            filename = f"workflow-{workflow.id}-{safe_name}.json"

        file_path = workflows_dir / filename

        # Write workflow data
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(workflow.dict(), f, indent=2, default=str)

        return str(file_path.relative_to(repo.working_dir))

    def export_application(self, repo: Repo, application: ApplicationExport, file_naming: str = "id-name") -> str:
        """Export application to Git repository"""
        applications_dir = Path(repo.working_dir) / "applications"
        applications_dir.mkdir(exist_ok=True)

        # Determine filename
        if file_naming == "id":
            filename = f"app-{application.id}.json"
        elif file_naming == "name":
            safe_name = "".join(c for c in application.name if c.isalnum() or c in (" ", "-", "_")).strip()
            filename = f"app-{safe_name}.json"
        else:  # id-name
            safe_name = "".join(c for c in application.name if c.isalnum() or c in (" ", "-", "_")).strip()
            filename = f"app-{application.id}-{safe_name}.json"

        file_path = applications_dir / filename

        # Write application data
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(application.dict(), f, indent=2, default=str)

        return str(file_path.relative_to(repo.working_dir))

    def import_workflow(self, repo: Repo, file_path: str) -> Dict[str, Any]:
        """Import workflow from Git repository"""
        full_path = Path(repo.working_dir) / file_path
        if not full_path.exists():
            raise Exception(f"Workflow file not found: {file_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    def import_application(self, repo: Repo, file_path: str) -> Dict[str, Any]:
        """Import application from Git repository"""
        full_path = Path(repo.working_dir) / file_path
        if not full_path.exists():
            raise Exception(f"Application file not found: {file_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    def list_exported_files(self, repo: Repo) -> Dict[str, List[str]]:
        """List all exported workflows and applications"""
        workflows_dir = Path(repo.working_dir) / "workflows"
        applications_dir = Path(repo.working_dir) / "applications"

        workflows = []
        applications = []

        if workflows_dir.exists():
            workflows = [str(f.relative_to(repo.working_dir)) for f in workflows_dir.glob("*.json")]

        if applications_dir.exists():
            applications = [str(f.relative_to(repo.working_dir)) for f in applications_dir.glob("*.json")]

        return {"workflows": workflows, "applications": applications}

    def get_repository_status(self, repo: Repo) -> Dict[str, Any]:
        """Get repository status"""
        try:
            return {
                "branch": repo.active_branch.name,
                "is_dirty": repo.is_dirty(),
                "untracked_files": repo.untracked_files,
                "modified_files": [item.a_path for item in repo.index.diff(None)],
                "staged_files": [item.a_path for item in repo.index.diff("HEAD")],
                "last_commit": {
                    "hash": repo.head.commit.hexsha,
                    "message": repo.head.commit.message.split("\n")[0],
                    "date": datetime.fromtimestamp(repo.head.commit.committed_date).isoformat(),
                },
            }
        except Exception as e:
            raise Exception(f"Failed to get repository status: {str(e)}")
