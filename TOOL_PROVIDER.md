# Git Integration - Tool Provider Implementation

## Overview

The Git Integration plugin has been enhanced with a **Tool Provider** interface, making Git operations available as tools within Dify workflows. This allows users to add Git operations directly into their workflow nodes, similar to how MCP and other tools work in Dify.

## What Changed

### New Structure

```
dify-plugins-git/
├── provider.yaml                 # Tool provider manifest
├── provider/
│   ├── __init__.py
│   └── git_provider.py          # Tool provider implementation
└── tools/
    ├── __init__.py
    ├── export_workflow.yaml     # Tool: Export workflow to Git
    ├── export_workflow.py
    ├── import_workflow.yaml     # Tool: Import workflow from Git
    ├── import_workflow.py
    ├── commit_changes.yaml      # Tool: Commit changes
    ├── commit_changes.py
    ├── push_changes.yaml        # Tool: Push to remote
    ├── push_changes.py
    ├── create_branch.yaml       # Tool: Create Git branch
    ├── create_branch.py
    ├── list_branches.yaml       # Tool: List branches
    └── list_branches.py
```

### Available Tools

1. **Export Workflow to Git**
   - Exports a Dify workflow to the Git repository
   - Parameters: workflow_id, file_naming, commit_message
   - Automatically commits the changes

2. **Import Workflow from Git**
   - Imports a workflow from the Git repository
   - Parameters: file_path, auto_merge
   - Creates or updates workflows in Dify

3. **Commit Changes to Git**
   - Commits pending changes to the repository
   - Parameters: message, author_name, author_email

4. **Push Changes to Remote**
   - Pushes committed changes to the remote repository
   - Parameters: branch (optional)

5. **Create Git Branch**
   - Creates a new branch in the repository
   - Parameters: branch_name, from_branch (optional)

6. **List Git Branches**
   - Lists all available branches
   - No parameters required

## How It Appears in Dify UI

Once installed, the Git Integration will appear in:

1. **Workflow Editor** → **Add Tool** → **Git Integration**
2. **Application Settings** → **Tools** → **Git Integration**

Users can:
- Configure the repository URL, branch, and authentication in the tool settings
- Add Git tools as nodes in their workflows
- Chain Git operations (e.g., Export → Commit → Push)

## Configuration

When adding the Git Integration tool to a workflow, users configure:

- **Repository URL**: GitHub repository URL (e.g., `https://github.com/user/repo.git`)
- **Default Branch**: Branch name (default: `main`)
- **Authentication Type**: `No Authentication`, `Personal Access Token`, or `SSH Key`
- **GitHub Token**: Personal Access Token (if using token authentication)

## Example Workflow

A typical workflow might look like:

```
[Trigger] → [Export Workflow] → [Commit Changes] → [Push Changes] → [Notification]
```

This would automatically export a workflow to Git, commit it, and push to the remote repository whenever triggered.

## Dual Interface

The plugin now supports **two interfaces**:

1. **Tool Provider** (NEW)
   - Available in workflow editor
   - User-friendly for visual workflow building
   - Integrated into Dify UI

2. **HTTP Endpoints** (Existing)
   - Available via REST API
   - For programmatic access
   - Advanced operations

Both interfaces share the same underlying services and functionality.

## Next Steps

1. **Package the plugin**: Run `make build` to create the `.difypkg` file
2. **Sign the plugin**: Run `make sign` to sign it
3. **Install in Dify**: Upload the signed `.difypkg` file
4. **Configure**: Add Git Integration tool to your workflows
5. **Use**: Start using Git operations in your workflows!

## Migration Note

Existing API endpoint functionality remains unchanged. The tool provider is an **addition**, not a replacement. You can use both interfaces simultaneously.
