# UI Setup Guide: Connecting Dify Applications to GitHub

This guide explains how to set up a connection between a Dify application and a GitHub repository through the Dify UI.

## Overview

The Git Integration plugin provides a configuration form in Dify's UI that allows you to:
1. Configure GitHub repository connection settings
2. Link Dify applications to GitHub repositories
3. Automatically sync workflows and applications with Git

## Step 1: Configure Plugin Settings

When you install the plugin, Dify will show a configuration form with the following fields:

### Required Settings

- **Repository URL** (Required)
  - Enter your GitHub repository URL
  - Example: `https://github.com/username/repository.git`
  - This can be a public or private repository

### Optional Settings

- **Default Branch**
  - Default: `main`
  - The branch name to use for operations

- **Authentication Type**
  - Options: `No Authentication`, `Personal Access Token`, `SSH Key`
  - Default: `No Authentication`
  - For private repositories, select `Personal Access Token`

- **GitHub Token** (Required if using token authentication)
  - Your GitHub Personal Access Token
  - Create one at: https://github.com/settings/tokens
  - Required scopes: `repo` (for private repos) or `public_repo` (for public repos)

- **Enable Auto-Sync**
  - Default: `false`
  - Automatically sync changes between Dify and Git

- **Sync Interval (minutes)**
  - Default: `60`
  - How often to check for changes (only if auto-sync is enabled)

## Step 2: Create Repository Connection

After configuring the plugin settings, you can create a repository connection in two ways:

### Option A: Using Plugin Settings (Automatic)

When you configure the plugin settings in Dify UI and save them, the plugin will automatically:
1. Use the settings to create a repository connection
2. Clone the repository locally
3. Set up authentication if provided

### Option B: Using API Endpoint (Manual)

You can also create a connection programmatically:

```bash
POST /repositories
{
  "name": "My Workflows Repository",
  "url": "https://github.com/username/repo.git",
  "branch": "main",
  "auth_type": "token",
  "credentials": {
    "token": "your-github-token"
  },
  "workspace_id": "your-workspace-id",
  "auto_sync": false
}
```

The plugin will merge the API request with the UI settings (API values take precedence).

## Step 3: Link Application to Repository

Once you have a repository connection, link a Dify application to it:

```bash
POST /repositories/link-application
{
  "application_id": "your-application-id",
  "repository_id": "repository-id-from-step-2",
  "workspace_id": "your-workspace-id"
}
```

### Finding Your Application ID

1. Go to your Dify application
2. Check the URL or application settings
3. The application ID is typically a UUID

### Finding Your Repository ID

After creating a repository connection, you'll receive a response with the `repository.id` field. You can also list all repositories:

```bash
GET /repositories?workspace_id=your-workspace-id
```

## Step 4: Verify Connection

Check that your application is linked to the repository:

```bash
GET /repositories/application/{application_id}
```

This will return the repository details linked to your application.

## Step 5: Export/Import Workflows

Once linked, you can:

### Export a Workflow to Git

```bash
POST /sync/export/workflow
{
  "repository_id": "repository-id",
  "workflow_id": "workflow-id",
  "file_naming": "id-name"
}
```

### Import a Workflow from Git

```bash
POST /sync/import/workflow
{
  "repository_id": "repository-id",
  "file_path": "workflows/workflow-123.json",
  "auto_merge": true
}
```

## Complete Example Workflow

1. **Install Plugin** in Dify
2. **Configure Settings** in Dify UI:
   - Repository URL: `https://github.com/myuser/myworkflows.git`
   - Auth Type: `Personal Access Token`
   - GitHub Token: `ghp_xxxxxxxxxxxx`
   - Auto-Sync: `false`
3. **Create Repository Connection** (automatic from settings or via API)
4. **Link Application**:
   ```bash
   POST /repositories/link-application
   {
     "application_id": "app-123",
     "repository_id": "repo-456",
     "workspace_id": "workspace-789"
   }
   ```
5. **Export Workflow**:
   ```bash
   POST /sync/export/workflow
   {
     "repository_id": "repo-456",
     "workflow_id": "workflow-abc",
     "file_naming": "id-name"
   }
   ```
6. **Commit and Push**:
   ```bash
   POST /git/commit
   {
     "repository_id": "repo-456",
     "message": "Add workflow export",
     "author": {
       "name": "Your Name",
       "email": "your@email.com"
     }
   }
   
   POST /git/push
   {
     "repository_id": "repo-456",
     "branch": "main"
   }
   ```

## Troubleshooting

### "Repository URL is required" Error

- Make sure you've configured the Repository URL in plugin settings
- Or provide it in the API request body

### Authentication Failures

- Verify your GitHub token has the correct scopes
- For private repos, ensure token has `repo` scope
- Check that the token hasn't expired

### Application Not Found

- Verify the application ID is correct
- Ensure the application exists in the same workspace

### Repository Not Found

- Check that the repository connection was created successfully
- Verify the repository ID is correct
- List repositories to see available connections

## Next Steps

- Set up **Auto-Sync** to automatically keep Dify and Git in sync
- Use **Branch Management** to work with feature branches
- Create **Pull Requests** for code reviews
- Export **All Workflows** at once for backup

For more details, see the [README.md](README.md) and [TESTING.md](TESTING.md) files.

