# Quick Start Guide

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your Dify API credentials
```

3. **Run the plugin:**
```bash
python main.py
```

## Basic Usage

### 1. Connect a Repository

```bash
curl -X POST http://localhost:8000/repositories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Workflows Repo",
    "url": "https://github.com/username/repo.git",
    "branch": "main",
    "auth_type": "token",
    "credentials": {
      "token": "your-github-token"
    },
    "workspace_id": "your-workspace-id",
    "auto_sync": false
  }'
```

### 2. Export a Workflow

```bash
curl -X POST http://localhost:8000/sync/export/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": "repo-uuid",
    "workflow_id": "workflow-id",
    "file_naming": "id-name"
  }'
```

### 3. Commit and Push

```bash
# Commit changes
curl -X POST http://localhost:8000/git/commit \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": "repo-uuid",
    "message": "Add new workflow"
  }'

# Push to remote
curl -X POST http://localhost:8000/git/push \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": "repo-uuid",
    "branch": "main"
  }'
```

### 4. Import from Git

```bash
curl -X POST http://localhost:8000/sync/import/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": "repo-uuid",
    "file_path": "workflows/workflow-123-my-workflow.json",
    "auto_merge": true
  }'
```

### 5. Create a Branch

```bash
curl -X POST http://localhost:8000/git/branches \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": "repo-uuid",
    "branch_name": "feature/new-workflow",
    "from_branch": "main"
  }'
```

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Development

### Project Structure
- `endpoints/` - HTTP API endpoints
- `services/` - Business logic
- `models/` - Data models
- `utils/` - Utility functions
- `tests/` - Test suite

### Adding New Features

1. Add service methods in `services/`
2. Create endpoints in `endpoints/`
3. Update models if needed in `models/`
4. Add tests in `tests/`

## Troubleshooting

### Repository Connection Issues
- Verify Git URL is correct
- Check authentication credentials
- Ensure Git is installed on the system

### Export/Import Errors
- Verify Dify API credentials in `.env`
- Check workflow/application IDs exist
- Review file paths in repository

### Git Operations Fail
- Check repository status: `GET /repositories/{id}/status`
- Verify branch names are valid
- Ensure you have push permissions

## Next Steps

1. Review the [README.md](README.md) for detailed documentation
2. Check [PLAN.md](PLAN.md) for architecture details
3. See [IMPLEMENTATION.md](IMPLEMENTATION.md) for implementation status


