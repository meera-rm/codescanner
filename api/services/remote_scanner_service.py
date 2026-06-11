import os
from typing import Dict, Optional, Any
from api.services.scanner_service import ScannerService
from api.utils.remote_handler import (
    download_github_repo,
    extract_zip_file,
    get_github_info,
    cleanup_temp_directory,
    GitHubError,
    ZipError
)


class RemoteScannerService:
    """Service for scanning GitHub repos and ZIP files."""

    def __init__(self):
        self.scanner_service = ScannerService()
        self.github_size_limit_mb = int(os.getenv("GITHUB_SIZE_LIMIT_MB", "500"))
        self.zip_size_limit_mb = int(os.getenv("ZIP_SIZE_LIMIT_MB", "500"))
        self.download_timeout_seconds = int(os.getenv("GITHUB_TIMEOUT_SECONDS", "60"))

    def scan_github_repo(
        self,
        github_url: str,
        branch: str = "main",
        language: str = "python",
        options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Download and scan a GitHub repository.

        Args:
            github_url: GitHub URL (https://github.com/owner/repo)
            branch: Branch to scan
            language: Programming language (auto-detect if not specified)
            options: Scan options

        Returns:
            Scan result with job_id and status
        """
        extracted_path = None

        try:
            # Parse GitHub URL
            owner, repo = self._parse_github_url(github_url)

            # Download and extract
            extracted_path, metadata = download_github_repo(
                owner=owner,
                repo=repo,
                branch=branch,
                size_limit_mb=self.github_size_limit_mb,
                timeout_seconds=self.download_timeout_seconds
            )

            # Scan the extracted directory
            result = self.scanner_service.scan(
                directory_path=extracted_path,
                language=language,
                options=options
            )

            # Add metadata
            result["source"] = "github"
            result["github_url"] = github_url
            result["branch"] = branch
            result["temp_path"] = extracted_path

            return result

        except (GitHubError, ValueError) as e:
            return {
                "status": "error",
                "error": str(e),
                "findings": [],
                "metrics": {}
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "findings": [],
                "metrics": {}
            }
        finally:
            # Note: Don't cleanup immediately - keep for 1 hour for report export
            # Cleanup will be handled by background task or explicit request
            pass

    def scan_zip_file(
        self,
        zip_file_path: str,
        language: str = "python",
        options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Extract and scan a ZIP file.

        Args:
            zip_file_path: Path to ZIP file
            language: Programming language (auto-detect if not specified)
            options: Scan options

        Returns:
            Scan result with job_id and status
        """
        extracted_path = None

        try:
            # Extract ZIP
            extracted_path, metadata = extract_zip_file(
                zip_file_path=zip_file_path,
                size_limit_mb=self.zip_size_limit_mb
            )

            # Scan the extracted directory
            result = self.scanner_service.scan(
                directory_path=extracted_path,
                language=language,
                options=options
            )

            # Add metadata
            result["source"] = "zip"
            result["filename"] = os.path.basename(zip_file_path)
            result["temp_path"] = extracted_path

            return result

        except ZipError as e:
            return {
                "status": "error",
                "error": str(e),
                "findings": [],
                "metrics": {}
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "findings": [],
                "metrics": {}
            }
        finally:
            # Note: Don't cleanup immediately - keep for 1 hour for report export
            pass

    def get_github_repo_info(
        self,
        github_url: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Get GitHub repository info without downloading.

        Args:
            github_url: GitHub URL
            branch: Branch to check

        Returns:
            Repository metadata
        """
        try:
            owner, repo = self._parse_github_url(github_url)
            info = get_github_info(owner, repo, branch)
            info["github_url"] = github_url
            return info
        except GitHubError as e:
            return {
                "error": str(e),
                "scannable": False
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "scannable": False
            }

    def cleanup_scan_temp_files(self, temp_path: str) -> bool:
        """
        Manually cleanup temporary files from a scan.

        Args:
            temp_path: Path to cleanup

        Returns:
            True if successful
        """
        return cleanup_temp_directory(temp_path)

    @staticmethod
    def _parse_github_url(url: str) -> tuple:
        """
        Parse GitHub URL to extract owner and repo.

        Args:
            url: GitHub URL (supports multiple formats)

        Returns:
            Tuple of (owner, repo)

        Raises:
            ValueError: If URL format is invalid
        """
        # Remove protocol
        url = url.replace("https://", "").replace("http://", "").replace("git@github.com:", "")
        # Remove .git suffix
        url = url.rstrip("/").replace(".git", "")
        # Remove trailing path (branch, tree, etc.)
        url = url.split("/tree/")[0].split("/blob/")[0]

        parts = url.split("/")
        if len(parts) < 3:  # At minimum: github.com/owner/repo
            raise ValueError(f"Invalid GitHub URL format: {url}")

        # Extract owner and repo
        if parts[0] == "github.com":
            owner, repo = parts[1], parts[2]
        else:
            owner, repo = parts[0], parts[1]

        if not owner or not repo:
            raise ValueError("Could not parse owner and repo from URL")

        return owner, repo
