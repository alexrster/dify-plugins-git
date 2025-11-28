"""Authentication service for Git credentials"""
import os
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64


class AuthService:
    """Service for handling Git authentication and credential encryption"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        # Generate or use provided encryption key
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            # Use environment variable or generate from workspace ID
            key_env = os.getenv("PLUGIN_ENCRYPTION_KEY")
            if key_env:
                self.key = key_env.encode()
            else:
                # Generate a key from a default (should be set in production)
                self.key = self._generate_key("default-workspace-key")
        
        self.cipher = Fernet(self._derive_key(self.key))
    
    def _generate_key(self, password: str) -> bytes:
        """Generate encryption key from password"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'dify_git_plugin_salt',
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _derive_key(self, key: bytes) -> bytes:
        """Derive Fernet key from input key"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'dify_git_plugin_salt',
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(key))
    
    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """Encrypt credentials dictionary"""
        import json
        credentials_json = json.dumps(credentials)
        encrypted = self.cipher.encrypt(credentials_json.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_credentials(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt credentials"""
        import json
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return json.loads(decrypted.decode())
    
    def add_token_to_url(self, url: str) -> str:
        """Add authentication token to Git URL"""
        # This would be called with decrypted credentials
        # For now, return URL as-is (should be implemented with actual token)
        return url
    
    def get_ssh_environment(self):
        """Get SSH environment context manager"""
        # This would set up SSH key environment
        # For now, return a no-op context manager
        from contextlib import contextmanager
        
        @contextmanager
        def ssh_env():
            # Set SSH environment variables if needed
            yield
        
        return ssh_env()
    
    def validate_ssh_key(self, key_path: str, passphrase: Optional[str] = None) -> bool:
        """Validate SSH key"""
        try:
            if not os.path.exists(key_path):
                return False
            
            # Check if key is readable
            with open(key_path, 'r') as f:
                key_content = f.read()
            
            # Basic validation (check for SSH key markers)
            if "BEGIN" in key_content and "PRIVATE KEY" in key_content:
                return True
            
            return False
        except Exception:
            return False
    
    def validate_token(self, token: str) -> bool:
        """Validate Git token format"""
        # Basic validation - tokens are usually alphanumeric strings
        if not token or len(token) < 10:
            return False
        return True


