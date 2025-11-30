# Testing Plugin Endpoints

This guide explains how to test if your Dify plugin endpoints are up and running.

## 1. Check Plugin Status

### Via Dify UI
1. Go to **Plugins** section in Dify
2. Find your plugin (`git-integration`)
3. Check if it shows as **Running** (green status)
4. Verify that endpoints are listed (even if it shows "0 sets of endpoints enabled", the endpoints may still work)

### Via Logs
Check the plugin daemon logs:
```bash
docker logs plugin_daemon-1 | grep "git-integration"
```

You should see:
```
[INFO]plugin alexrster/git-integration:X.X.X started
[INFO]plugin alexrster/git-integration:X.X.X: Installed endpoint: ['/repositories', ...]
```

## 2. Get Plugin Information

### Get Plugin ID
You need the plugin ID to construct endpoint URLs. Get it via Dify API:

```bash
# Get your Dify API key from Settings > API Keys
export DIFY_API_KEY="your-api-key"
export DIFY_API_URL="http://localhost:5001"  # or your Dify URL

# List all plugins
curl -X GET "${DIFY_API_URL}/api/v1/plugins" \
  -H "Authorization: Bearer ${DIFY_API_KEY}" \
  -H "Content-Type: application/json"
```

Look for your plugin in the response and note the `id` field.

### Get Plugin Endpoint URL
Dify plugin endpoints are typically accessible via:
```
${DIFY_API_URL}/console/api/plugins/${PLUGIN_ID}/endpoints${ENDPOINT_PATH}
```

Or through Dify's endpoint proxy (check Dify documentation for the exact format).

## 3. Test Endpoints

### Basic Health Check
Test if the endpoint handler is responding:

```bash
# Replace PLUGIN_ID with your actual plugin ID
export PLUGIN_ID="your-plugin-id"

# Test GET /repositories (should return empty list initially)
curl -X GET "${DIFY_API_URL}/console/api/plugins/${PLUGIN_ID}/endpoints/repositories" \
  -H "Authorization: Bearer ${DIFY_API_KEY}" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "message": "Endpoint handler active",
  "path": "/repositories",
  "method": "GET",
  "values": {}
}
```

### Test Repository Creation
```bash
curl -X POST "${DIFY_API_URL}/console/api/plugins/${PLUGIN_ID}/endpoints/repositories" \
  -H "Authorization: Bearer ${DIFY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Repository",
    "url": "https://github.com/user/repo.git",
    "branch": "main",
    "auth_type": "none",
    "workspace_id": "your-workspace-id",
    "auto_sync": false
  }'
```

### Test List Repositories
```bash
curl -X GET "${DIFY_API_URL}/console/api/plugins/${PLUGIN_ID}/endpoints/repositories?workspace_id=your-workspace-id" \
  -H "Authorization: Bearer ${DIFY_API_KEY}" \
  -H "Content-Type: application/json"
```

## 4. Alternative: Direct Plugin Endpoint Access

If the above URL format doesn't work, Dify might expose endpoints differently. Check:

1. **Dify Plugin Documentation** for the correct endpoint URL format
2. **Plugin Daemon Configuration** - endpoints might be accessible via plugin daemon directly
3. **Dify Console Network Tab** - inspect network requests when using the plugin in UI

## 5. Test via Python Script

Create a test script:

```python
import requests
import os

DIFY_API_URL = os.getenv("DIFY_API_URL", "http://localhost:5001")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
PLUGIN_ID = "your-plugin-id"  # Get this from Dify API

headers = {
    "Authorization": f"Bearer {DIFY_API_KEY}",
    "Content-Type": "application/json"
}

# Test GET /repositories
response = requests.get(
    f"{DIFY_API_URL}/console/api/plugins/{PLUGIN_ID}/endpoints/repositories",
    headers=headers
)
print(f"GET /repositories: {response.status_code}")
print(response.json())

# Test POST /repositories
response = requests.post(
    f"{DIFY_API_URL}/console/api/plugins/{PLUGIN_ID}/endpoints/repositories",
    headers=headers,
    json={
        "name": "Test Repo",
        "url": "https://github.com/user/repo.git",
        "branch": "main",
        "auth_type": "none",
        "workspace_id": "workspace-id",
        "auto_sync": False
    }
)
print(f"POST /repositories: {response.status_code}")
print(response.json())
```

## 6. Debugging

### Check Plugin Logs
```bash
# View real-time logs
docker logs -f plugin_daemon-1 | grep "git-integration"

# Check for errors
docker logs plugin_daemon-1 | grep -i error
```

### Verify Endpoint Handler
The endpoint handler returns a placeholder response. If you see:
```json
{
  "message": "Endpoint handler active",
  "path": "/repositories",
  "method": "GET"
}
```

This confirms:
- ✅ Plugin is running
- ✅ Endpoints are registered
- ✅ Endpoint handler is being called
- ⚠️ FastAPI routing needs proper ASGI conversion (currently returns placeholder)

### Next Steps
Once you confirm endpoints are being called, you'll need to:
1. Implement proper Werkzeug → ASGI conversion in `endpoint_handlers/handler.py`
2. Route requests to the correct FastAPI endpoint handlers
3. Convert ASGI responses back to Werkzeug Response format

## 7. Common Issues

### "0 sets of endpoints enabled"
- Endpoints are still functional even if UI shows this
- Check logs to confirm endpoints are installed
- Test endpoints directly via API

### "404 Not Found"
- Verify plugin ID is correct
- Check endpoint URL format matches Dify's expected pattern
- Ensure plugin is running (check logs)

### "500 Internal Server Error"
- Check plugin logs for detailed error messages
- Verify endpoint handler is properly implemented
- Check if FastAPI app is correctly initialized

## 8. Endpoint List

Available endpoints to test:

- `GET /repositories` - List repositories
- `POST /repositories` - Create repository
- `GET /repositories/{id}` - Get repository
- `PUT /repositories/{id}` - Update repository
- `DELETE /repositories/{id}` - Delete repository
- `GET /repositories/{id}/status` - Get repository status
- `POST /git/commit` - Commit changes
- `POST /git/push` - Push to remote
- `POST /git/pull` - Pull from remote
- `GET /git/{repository_id}/branches` - List branches
- `POST /git/branches` - Create branch
- `POST /git/checkout` - Checkout branch
- `GET /git/{repository_id}/history` - Get commit history
- `POST /git/diff` - Get diff
- `POST /git/pr` - Create pull request
- `POST /sync/export/workflow` - Export workflow
- `POST /sync/export/application` - Export application
- `POST /sync/export/all` - Export all
- `POST /sync/import/workflow` - Import workflow
- `POST /sync/import/application` - Import application
- `POST /sync/import/all` - Import all
- `POST /sync` - Manual sync
- `GET /sync/{repository_id}/status` - Get sync status

