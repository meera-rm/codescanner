"""GitHub integration service for OAuth and webhook handling."""
import os
import json
import hmac
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import requests
from cryptography.fernet import Fernet


class GitHubService:
    """Handles GitHub OAuth, API calls, and token management."""

    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID", "123456")
        self.private_key = os.getenv("GITHUB_PRIVATE_KEY", "").replace("\\n", "\n")
        self.client_id = os.getenv("GITHUB_CLIENT_ID", "")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET", "")
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
        self.encryption_key = os.getenv("GITHUB_TOKEN_KEY", "").encode()

        if self.encryption_key:
            self.cipher = Fernet(self.encryption_key)
        else:
            self.cipher = None

    def get_app_installation_url(self) -> str:
        """Get URL for user to install GitHub App."""
        return f"https://github.com/apps/{os.getenv('GITHUB_APP_NAME', 'codepulse-ai')}/installations/new"

    def get_oauth_url(self, redirect_uri: str) -> str:
        """Get OAuth authorization URL."""
        return (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={self.client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=user:email,repo,workflow&"
            f"state=randomstate"
        )

    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange OAuth code for access token."""
        try:
            response = requests.post(
                "https://github.com/login/oauth/access_token",
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            data = response.json()

            if "access_token" in data:
                return {
                    "access_token": data["access_token"],
                    "scope": data.get("scope", ""),
                    "token_type": data.get("token_type", "bearer"),
                }
            return None
        except Exception as e:
            print(f"Error exchanging code: {e}")
            return None

    def get_installation_access_token(self, installation_id: int) -> Optional[str]:
        """Get temporary access token for GitHub App installation."""
        try:
            if not self.private_key:
                return None

            # Create JWT
            payload = {
                "iat": int(datetime.utcnow().timestamp()),
                "exp": int((datetime.utcnow() + timedelta(minutes=10)).timestamp()),
                "iss": int(self.app_id),
            }
            token = jwt.encode(payload, self.private_key, algorithm="RS256")

            # Get installation access token
            response = requests.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            if response.status_code == 201:
                data = response.json()
                return data.get("token")
            return None
        except Exception as e:
            print(f"Error getting installation token: {e}")
            return None

    def encrypt_token(self, token: str) -> str:
        """Encrypt token for storage."""
        if not self.cipher:
            return token
        return self.cipher.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt token from storage."""
        if not self.cipher:
            return encrypted_token
        return self.cipher.decrypt(encrypted_token.encode()).decode()

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        if not self.webhook_secret:
            return False

        expected_signature = "sha256=" + hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def get_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get authenticated user info."""
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def get_user_repos(self, access_token: str) -> Optional[list]:
        """Get user's repositories."""
        try:
            response = requests.get(
                "https://api.github.com/user/repos",
                params={"sort": "updated", "per_page": 100},
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting repos: {e}")
            return None

    def post_pr_comment(
        self, token: str, repo: str, pr_number: int, comment: str
    ) -> bool:
        """Post comment on PR."""
        try:
            response = requests.post(
                f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
                json={"body": comment},
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Error posting comment: {e}")
            return False

    def set_pr_status(
        self,
        token: str,
        repo: str,
        commit_sha: str,
        state: str,  # pending, success, failure
        context: str = "codepulse/scan",
        description: str = "",
        target_url: str = "",
    ) -> bool:
        """Set status check on PR commit."""
        try:
            response = requests.post(
                f"https://api.github.com/repos/{repo}/statuses/{commit_sha}",
                json={
                    "state": state,
                    "context": context,
                    "description": description,
                    "target_url": target_url,
                },
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Error setting status: {e}")
            return False

    def get_pr_files(self, token: str, repo: str, pr_number: int) -> Optional[list]:
        """Get list of files changed in PR."""
        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files",
                params={"per_page": 100},
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting PR files: {e}")
            return None
