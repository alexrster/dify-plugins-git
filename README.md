# Dify Git Integration Plugin

A Dify plugin that enables Git-based version control for managing workflows and applications.

## Testing

See [TESTING.md](TESTING.md) for detailed instructions on how to test if endpoints are up and running.

## UI Setup

See [UI_SETUP_GUIDE.md](UI_SETUP_GUIDE.md) for step-by-step instructions on setting up connections between Dify applications and GitHub repositories through the Dify UI.

## Features

- 🔗 **Repository Management**: Connect and manage Git repositories
- 📤 **Export**: Export workflows and applications to Git
- 📥 **Import**: Import workflows and applications from Git
- 🔄 **Synchronization**: Sync changes between Dify and Git
- 🌿 **Branch Management**: Create, switch, and manage branches
- 📝 **Commit & Push**: Commit changes and push to remote repositories
- 🔀 **Auto-merge**: Automatic conflict resolution (configurable)
- 🔐 **Security**: Encrypted credential storage

## Installation

### Prerequisites

- Python 3.12 or higher
- Dify instance with plugin support
- Git installed on the system

### Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd dify-plugins-git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Dify API URL and key
```

4. Package the plugin:
```bash
make build
# or
dify plugin package . -o dist/git-integration-plugin.difypkg
```

5. **Sign the plugin** (required if Dify has signature verification enabled):
```bash
# Generate keys first (one-time setup)
make generate-keys

# Build and sign the plugin
make sign
```

6. Install in Dify:
   - Upload the **signed** `.difypkg` file (`dist/git-integration-plugin.signed.difypkg`) through Dify's plugin management interface
   - **Note:** If you get a signature verification error, see [README_SIGNING.md](README_SIGNING.md) for solutions

## Configuration

### Environment Variables

- `DIFY_API_URL`: Dify API URL (default: http://localhost:5001)
- `DIFY_API_KEY`: Dify API key
- `PLUGIN_DEBUG`: Enable debug mode (default: false)
- `PLUGIN_LOG_LEVEL`: Logging level (default: INFO)
- `STORAGE_PATH`: Path for plugin storage (default: ./storage)
- `GIT_TEMP_DIR`: Temporary directory for Git repositories (default: ./temp/git)

### Plugin Configuration

Configure the plugin through Dify's plugin settings UI:

- **Repository URL** (Required): GitHub repository URL (e.g., `https://github.com/user/repo.git`)
- **Default Branch**: Default branch name (default: `main`)
- **Authentication Type**: Choose `none`, `token`, or `ssh` (default: `none`)
- **GitHub Token**: Personal Access Token (required if using token authentication)
- **Enable Auto-Sync**: Automatically sync changes (default: `false`, opt-in)
- **Sync Interval**: Auto-sync interval in minutes (default: `60`)

When you configure these settings in Dify's UI, the plugin will automatically use them when creating repository connections. See [UI_SETUP_GUIDE.md](UI_SETUP_GUIDE.md) for detailed instructions.

## Usage

### Connect a Repository

```bash
POST /repositories
{
  "name": "My Workflows",
  "url": "https://github.com/user/repo.git",
  "branch": "main",
  "auth_type": "token",
  "credentials": {
    "token": "your-git-token"
  },
  "workspace_id": "workspace-id",
  "auto_sync": false
}
```

### Export Workflow

```bash
POST /sync/export/workflow
{
  "repository_id": "repo-id",
  "workflow_id": "workflow-id",
  "file_naming": "id-name"
}
```

### Import Workflow

```bash
POST /sync/import/workflow
{
  "repository_id": "repo-id",
  "file_path": "workflows/workflow-123.json",
  "auto_merge": true
}
```

### Commit Changes

```bash
POST /git/commit
{
  "repository_id": "repo-id",
  "message": "Update workflows",
  "author": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### Push to Remote

```bash
POST /git/push
{
  "repository_id": "repo-id",
  "branch": "main"
}
```

### Create Branch

```bash
POST /git/branches
{
  "repository_id": "repo-id",
  "branch_name": "feature/new-workflow",
  "from_branch": "main"
}
```

### Sync Repository

```bash
POST /sync
{
  "repository_id": "repo-id",
  "direction": "bidirectional"
}
```

## API Endpoints

### Repository Management

- `POST /repositories` - Connect a new repository (uses UI settings if configured)
- `GET /repositories` - List connected repositories
- `GET /repositories/{id}` - Get repository details
- `PUT /repositories/{id}` - Update repository configuration
- `DELETE /repositories/{id}` - Disconnect repository
- `GET /repositories/{id}/status` - Get repository status
- `POST /repositories/link-application` - Link a Dify application to a repository
- `GET /repositories/application/{application_id}` - Get repository linked to an application
- `DELETE /repositories/application/{application_id}/unlink` - Unlink application from repository

### Export Operations

- `POST /sync/export/workflow` - Export single workflow
- `POST /sync/export/application` - Export single application
- `POST /sync/export/all` - Export all workflows/applications

### Import Operations

- `POST /sync/import/workflow` - Import workflow from Git
- `POST /sync/import/application` - Import application from Git
- `POST /sync/import/all` - Import all from Git

### Git Operations

- `POST /git/commit` - Commit changes
- `POST /git/push` - Push to remote
- `POST /git/pull` - Pull from remote
- `GET /git/{repository_id}/branches` - List branches
- `POST /git/branches` - Create branch
- `POST /git/checkout` - Switch branch
- `GET /git/{repository_id}/history` - View commit history
- `POST /git/diff` - View diff
- `POST /git/pr` - Create pull request (merge)

### Synchronization

- `POST /sync` - Manual sync trigger
- `GET /sync/{repository_id}/status` - Get sync status

## Repository Structure

The plugin organizes exported files in the Git repository as follows:

```
repository/
├── workflows/
│   ├── workflow-{id}-{name}.json
│   └── ...
├── applications/
│   ├── app-{id}-{name}.json
│   └── ...
├── .dify/
│   ├── config.json
│   └── sync-state.json
└── README.md
```

## Security

- Credentials are encrypted using AES-256 encryption
- SSH keys are validated before use
- Repository URLs are validated
- File paths are sanitized to prevent directory traversal attacks

## Development

### Project Structure

```
dify-plugins-git/
├── manifest.yaml          # Plugin manifest
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── endpoint_handlers/    # HTTP endpoint handlers
│   ├── repositories.py
│   ├── git_operations.py
│   └── sync.py
├── services/             # Business logic
│   ├── git_service.py
│   ├── dify_api.py
│   ├── sync_service.py
│   └── auth_service.py
├── models/               # Data models
│   ├── repository.py
│   ├── workflow.py
│   └── sync.py
└── utils/                # Utilities
    ├── validators.py
    └── encryption.py
```

### Running Tests

```bash
pytest tests/
```

### Debugging

Enable debug mode in `.env`:
```
PLUGIN_DEBUG=true
PLUGIN_LOG_LEVEL=DEBUG
```

## Limitations

- Pull requests require provider-specific APIs (GitHub, GitLab) for full functionality
- Generic Git implementation uses merge commits for PR simulation
- Auto-sync is opt-in and requires manual configuration

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

## License

[Specify your license here]

## Support

For issues and questions, please open an issue on GitHub.


