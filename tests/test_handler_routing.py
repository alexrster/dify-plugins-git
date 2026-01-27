import json
import unittest
from unittest.mock import MagicMock, patch

from endpoint_handlers.handler import FastAPIEndpoint
from werkzeug import Request


class TestHandlerRouting(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.endpoint = FastAPIEndpoint(self.session)
        self.settings = {}

    def create_mock_request(self, method, path, data=None):
        req = MagicMock(spec=Request)
        req.method = method
        req.path = path
        req.get_data.return_value = json.dumps(data).encode("utf-8") if data else b""
        
        # Mock args for GET requests
        if method == "GET":
             # Simple mock for args
            class MockArgs:
                def get(self, key, default=None):
                    return default
            req.args = MockArgs()
            
        return req

    @patch("endpoint_handlers.handler.create_repository")
    def test_create_repository(self, mock_create):
        mock_create.return_value = {"success": True}
        
        data = {"name": "test", "url": "http://example.com"}
        req = self.create_mock_request("POST", "/repositories", data)
        
        resp = self.endpoint.invoke(req, {}, self.settings)
        
        self.assertEqual(resp.status_code, 200)
        mock_create.assert_called_once()

    @patch("endpoint_handlers.handler.list_repositories")
    def test_list_repositories(self, mock_list):
        mock_list.return_value = []
        
        req = self.create_mock_request("GET", "/repositories")
        
        resp = self.endpoint.invoke(req, {}, self.settings)
        
        self.assertEqual(resp.status_code, 200)
        mock_list.assert_called_once()

    @patch("endpoint_handlers.handler.get_repository")
    def test_get_repository(self, mock_get):
        mock_get.return_value = {"id": "123"}
        
        req = self.create_mock_request("GET", "/repositories/123")
        
        resp = self.endpoint.invoke(req, {}, self.settings)
        
        self.assertEqual(resp.status_code, 200)
        mock_get.assert_called_once_with("123")

    @patch("endpoint_handlers.handler.commit_changes")
    def test_commit_changes(self, mock_commit):
        mock_commit.return_value = {"success": True}
        
        data = {"repository_id": "123", "message": "test"}
        req = self.create_mock_request("POST", "/git/commit", data)
        
        resp = self.endpoint.invoke(req, {}, self.settings)
        
        self.assertEqual(resp.status_code, 200)
        mock_commit.assert_called_once()

    @patch("endpoint_handlers.handler.export_workflow")
    def test_export_workflow(self, mock_export):
        mock_export.return_value = {"success": True}
        
        data = {"repository_id": "123", "workflow_id": "wf-1"}
        req = self.create_mock_request("POST", "/sync/export/workflow", data)
        
        resp = self.endpoint.invoke(req, {}, self.settings)
        
        self.assertEqual(resp.status_code, 200)
        mock_export.assert_called_once()

if __name__ == "__main__":
    unittest.main()
