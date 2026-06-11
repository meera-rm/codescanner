import os
import tempfile
import zipfile
import shutil
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple


class RemoteHandlerError(Exception):
    """Base exception for remote file handling."""
    pass


class GitHubError(RemoteHandlerError):
    """GitHub-related errors."""
    pass


class ZipError(RemoteHandlerError):
    """ZIP file handling errors."""
    pass


def download_github_repo(
    owner: str,
    repo: str,
    branch: str = "main",
    size_limit_mb: int = 500,
    timeout_seconds: int = 60
) -> Tuple[str, Dict[str, any]]:
    """
    Download GitHub repo as ZIP and extract to temp directory.

    Args:
        owner: GitHub username
        repo: Repository name
        branch: Branch to download (default: main)
        size_limit_mb: Maximum download size in MB
        timeout_seconds: Download timeout

    Returns:
        Tuple of (extracted_path, metadata)

    Raises:
        GitHubError: If download or extraction fails
    """
    try:
        # Validate inputs
        if not owner or not repo:
            raise GitHubError("Owner and repo name required")

        # GitHub API endpoint for repo zipball
        url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

        # Pre-flight check: get repo info
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            info_response = requests.head(api_url, timeout=10)
            if info_response.status_code == 404:
                raise GitHubError(f"Repository not found: {owner}/{repo}")
        except requests.RequestException as e:
            raise GitHubError(f"Failed to verify repository: {str(e)}")

        # Create temp directory for this job
        job_temp_dir = tempfile.mkdtemp(prefix="codescanner_github_")

        try:
            # Download ZIP
            print(f"[GitHub] Downloading {owner}/{repo} ({branch})...")
            response = requests.get(url, timeout=timeout_seconds, stream=True)

            if response.status_code == 404:
                raise GitHubError(f"Branch '{branch}' not found in {owner}/{repo}")

            if response.status_code != 200:
                raise GitHubError(f"Download failed: HTTP {response.status_code}")

            # Check size limit
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > size_limit_mb:
                    raise GitHubError(f"Repository too large ({size_mb:.1f}MB > {size_limit_mb}MB limit)")

            # Save ZIP file
            zip_path = os.path.join(job_temp_dir, "repo.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"[GitHub] Downloaded to {zip_path}")

            # Extract ZIP
            extracted_dir = os.path.join(job_temp_dir, "extracted")
            os.makedirs(extracted_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extracted_dir)

            # GitHub creates a directory like "repo-branch/" inside the ZIP
            # Find and move contents up one level
            extracted_contents = os.listdir(extracted_dir)
            if len(extracted_contents) == 1:
                inner_dir = os.path.join(extracted_dir, extracted_contents[0])
                if os.path.isdir(inner_dir):
                    # Move contents up
                    for item in os.listdir(inner_dir):
                        src = os.path.join(inner_dir, item)
                        dst = os.path.join(extracted_dir, item)
                        shutil.move(src, dst)
                    os.rmdir(inner_dir)

            print(f"[GitHub] Extracted to {extracted_dir}")

            return extracted_dir, {
                "source": "github",
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "size_mb": size_mb if content_length else 0
            }

        except Exception as e:
            # Cleanup on error
            shutil.rmtree(job_temp_dir, ignore_errors=True)
            raise

    except GitHubError:
        raise
    except Exception as e:
        raise GitHubError(f"Unexpected error: {str(e)}")


def extract_zip_file(
    zip_file_path: str,
    size_limit_mb: int = 500
) -> Tuple[str, Dict[str, any]]:
    """
    Extract ZIP file to temp directory.

    Args:
        zip_file_path: Path to ZIP file
        size_limit_mb: Maximum extracted size in MB

    Returns:
        Tuple of (extracted_path, metadata)

    Raises:
        ZipError: If extraction fails
    """
    try:
        # Validate file
        if not os.path.exists(zip_file_path):
            raise ZipError(f"File not found: {zip_file_path}")

        if not zipfile.is_zipfile(zip_file_path):
            raise ZipError("File is not a valid ZIP archive")

        # Check size
        file_size_mb = os.path.getsize(zip_file_path) / (1024 * 1024)
        if file_size_mb > size_limit_mb:
            raise ZipError(f"File too large ({file_size_mb:.1f}MB > {size_limit_mb}MB limit)")

        # Create temp directory
        job_temp_dir = tempfile.mkdtemp(prefix="codescanner_zip_")

        try:
            # Extract ZIP
            print(f"[ZIP] Extracting {os.path.basename(zip_file_path)}...")
            extracted_dir = os.path.join(job_temp_dir, "extracted")
            os.makedirs(extracted_dir, exist_ok=True)

            with zipfile.ZipFile(zip_file_path, 'r') as zf:
                zf.extractall(extracted_dir)

            # If single top-level directory, move contents up
            extracted_contents = os.listdir(extracted_dir)
            if len(extracted_contents) == 1:
                inner_dir = os.path.join(extracted_dir, extracted_contents[0])
                if os.path.isdir(inner_dir):
                    for item in os.listdir(inner_dir):
                        src = os.path.join(inner_dir, item)
                        dst = os.path.join(extracted_dir, item)
                        shutil.move(src, dst)
                    os.rmdir(inner_dir)

            print(f"[ZIP] Extracted to {extracted_dir}")

            return extracted_dir, {
                "source": "zip",
                "filename": os.path.basename(zip_file_path),
                "size_mb": file_size_mb
            }

        except Exception as e:
            # Cleanup on error
            shutil.rmtree(job_temp_dir, ignore_errors=True)
            raise

    except ZipError:
        raise
    except Exception as e:
        raise ZipError(f"Failed to extract ZIP: {str(e)}")


def get_github_info(owner: str, repo: str, branch: str = "main") -> Dict[str, any]:
    """
    Get GitHub repository metadata without downloading.

    Args:
        owner: GitHub username
        repo: Repository name
        branch: Branch to check

    Returns:
        Dictionary with repo info

    Raises:
        GitHubError: If API call fails
    """
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 404:
            raise GitHubError(f"Repository not found: {owner}/{repo}")

        if response.status_code != 200:
            raise GitHubError(f"API request failed: HTTP {response.status_code}")

        data = response.json()

        return {
            "repo": data.get("name"),
            "description": data.get("description"),
            "size_mb": data.get("size", 0) / 1024,  # GitHub returns size in KB
            "language": data.get("language"),
            "stars": data.get("stargazers_count", 0),
            "branch": branch,
            "scannable": True
        }

    except GitHubError:
        raise
    except Exception as e:
        raise GitHubError(f"Failed to get repo info: {str(e)}")


def cleanup_temp_directory(temp_path: str) -> bool:
    """
    Safely remove temporary directory.

    Args:
        temp_path: Path to remove

    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(temp_path) and os.path.isdir(temp_path):
            shutil.rmtree(temp_path, ignore_errors=True)
            print(f"[Cleanup] Removed {temp_path}")
            return True
        return False
    except Exception as e:
        print(f"[Cleanup] Error removing {temp_path}: {str(e)}")
        return False
