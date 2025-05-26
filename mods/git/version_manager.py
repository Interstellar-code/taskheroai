"""
Version Manager for TaskHero AI Git Integration.

Handles version checking, comparison, and update detection.
"""

import json
import logging
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import requests
from packaging import version


class VersionManager:
    """Manages version checking and comparison for Git updates."""

    def __init__(self, repository_url: str = "https://github.com/Interstellar-code/taskheroai"):
        """
        Initialize the version manager.
        
        Args:
            repository_url: GitHub repository URL
        """
        self.repository_url = repository_url
        self.logger = logging.getLogger("VersionManager")
        self.cache_duration = timedelta(hours=1)  # Cache version checks for 1 hour
        
        # Extract owner and repo from URL
        self.owner, self.repo = self._parse_github_url(repository_url)
        
    def _parse_github_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repository name."""
        # Handle both https://github.com/owner/repo and git@github.com:owner/repo.git formats
        if "github.com/" in url:
            parts = url.split("github.com/")[-1].split("/")
            owner = parts[0]
            repo = parts[1].replace(".git", "")
            return owner, repo
        else:
            raise ValueError(f"Invalid GitHub URL format: {url}")
    
    def get_current_version(self) -> Dict[str, Any]:
        """
        Get current local version information.
        
        Returns:
            Dictionary containing version info
        """
        try:
            # Try to get version from Git
            git_info = self._get_git_info()
            
            # Try to get version from package info or version file
            version_info = self._get_version_from_files()
            
            return {
                "version": version_info.get("version", "unknown"),
                "commit_hash": git_info.get("commit_hash", "unknown"),
                "branch": git_info.get("branch", "unknown"),
                "last_commit_date": git_info.get("last_commit_date", "unknown"),
                "is_git_repo": git_info.get("is_git_repo", False),
                "has_uncommitted_changes": git_info.get("has_uncommitted_changes", False)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting current version: {e}")
            return {
                "version": "unknown",
                "commit_hash": "unknown",
                "branch": "unknown",
                "last_commit_date": "unknown",
                "is_git_repo": False,
                "has_uncommitted_changes": False,
                "error": str(e)
            }
    
    def _get_git_info(self) -> Dict[str, Any]:
        """Get Git repository information."""
        try:
            # Check if we're in a Git repository
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            if result.returncode != 0:
                return {"is_git_repo": False}
            
            # Get current commit hash
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            commit_hash = commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Get last commit date
            date_result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            last_commit_date = date_result.stdout.strip() if date_result.returncode == 0 else "unknown"
            
            # Check for uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            has_uncommitted_changes = bool(status_result.stdout.strip()) if status_result.returncode == 0 else False
            
            return {
                "is_git_repo": True,
                "commit_hash": commit_hash,
                "branch": branch,
                "last_commit_date": last_commit_date,
                "has_uncommitted_changes": has_uncommitted_changes
            }
            
        except Exception as e:
            self.logger.error(f"Error getting Git info: {e}")
            return {"is_git_repo": False, "error": str(e)}
    
    def _get_version_from_files(self) -> Dict[str, Any]:
        """Try to get version from various files."""
        version_info = {"version": "1.0.0"}  # Default version
        
        # Try to get version from setup.py, pyproject.toml, or version.txt
        version_files = [
            ("setup.py", self._parse_setup_py),
            ("pyproject.toml", self._parse_pyproject_toml),
            ("version.txt", self._parse_version_txt),
            ("__version__.py", self._parse_version_py)
        ]
        
        for filename, parser in version_files:
            file_path = Path(filename)
            if file_path.exists():
                try:
                    parsed_version = parser(file_path)
                    if parsed_version:
                        version_info["version"] = parsed_version
                        break
                except Exception as e:
                    self.logger.debug(f"Error parsing {filename}: {e}")
                    continue
        
        return version_info
    
    def _parse_setup_py(self, file_path: Path) -> Optional[str]:
        """Parse version from setup.py."""
        content = file_path.read_text(encoding='utf-8')
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        return match.group(1) if match else None
    
    def _parse_pyproject_toml(self, file_path: Path) -> Optional[str]:
        """Parse version from pyproject.toml."""
        try:
            import tomli
            content = file_path.read_text(encoding='utf-8')
            data = tomli.loads(content)
            return data.get("project", {}).get("version") or data.get("tool", {}).get("poetry", {}).get("version")
        except ImportError:
            # Fallback to regex if tomli not available
            content = file_path.read_text(encoding='utf-8')
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            return match.group(1) if match else None
    
    def _parse_version_txt(self, file_path: Path) -> Optional[str]:
        """Parse version from version.txt."""
        return file_path.read_text(encoding='utf-8').strip()
    
    def _parse_version_py(self, file_path: Path) -> Optional[str]:
        """Parse version from __version__.py."""
        content = file_path.read_text(encoding='utf-8')
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        return match.group(1) if match else None
    
    def get_remote_version(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get remote version information from GitHub.
        
        Args:
            use_cache: Whether to use cached results if available
            
        Returns:
            Dictionary containing remote version info
        """
        try:
            # Check cache first
            if use_cache:
                cached_result = self._get_cached_remote_version()
                if cached_result:
                    return cached_result
            
            # Get latest commit from master branch
            api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/master"
            
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            commit_data = response.json()
            
            # Get latest release if available
            release_info = self._get_latest_release()
            
            result = {
                "commit_hash": commit_data["sha"],
                "commit_date": commit_data["commit"]["committer"]["date"],
                "commit_message": commit_data["commit"]["message"],
                "author": commit_data["commit"]["author"]["name"],
                "version": release_info.get("version", "unknown"),
                "release_date": release_info.get("date", "unknown"),
                "release_notes": release_info.get("notes", ""),
                "check_timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            # Cache the result
            self._cache_remote_version(result)
            
            return result
            
        except requests.RequestException as e:
            self.logger.error(f"Network error checking remote version: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "check_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting remote version: {e}")
            return {
                "success": False,
                "error": str(e),
                "check_timestamp": datetime.now().isoformat()
            }
    
    def _get_latest_release(self) -> Dict[str, Any]:
        """Get latest release information from GitHub."""
        try:
            api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 404:
                # No releases found
                return {}
            
            response.raise_for_status()
            release_data = response.json()
            
            return {
                "version": release_data["tag_name"],
                "date": release_data["published_at"],
                "notes": release_data["body"],
                "url": release_data["html_url"]
            }
            
        except Exception as e:
            self.logger.debug(f"Error getting latest release: {e}")
            return {}
    
    def _get_cached_remote_version(self) -> Optional[Dict[str, Any]]:
        """Get cached remote version if still valid."""
        try:
            cache_file = Path(".git_version_cache.json")
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check if cache is still valid
            check_time = datetime.fromisoformat(cached_data["check_timestamp"])
            if datetime.now() - check_time < self.cache_duration:
                self.logger.debug("Using cached remote version")
                return cached_data
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error reading version cache: {e}")
            return None
    
    def _cache_remote_version(self, version_data: Dict[str, Any]) -> None:
        """Cache remote version data."""
        try:
            cache_file = Path(".git_version_cache.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2)
            self.logger.debug("Cached remote version data")
        except Exception as e:
            self.logger.debug(f"Error caching version data: {e}")
    
    def compare_versions(self, current: Dict[str, Any], remote: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare current and remote versions.
        
        Args:
            current: Current version info
            remote: Remote version info
            
        Returns:
            Comparison result
        """
        try:
            if not remote.get("success", False):
                return {
                    "update_available": False,
                    "comparison": "error",
                    "error": remote.get("error", "Unknown error"),
                    "can_update": False
                }
            
            # Compare commit hashes first
            current_hash = current.get("commit_hash", "")
            remote_hash = remote.get("commit_hash", "")
            
            if current_hash == remote_hash:
                return {
                    "update_available": False,
                    "comparison": "up_to_date",
                    "message": "You are running the latest version",
                    "can_update": False
                }
            
            # If we have version numbers, compare them
            current_version = current.get("version", "unknown")
            remote_version = remote.get("version", "unknown")
            
            version_comparison = "unknown"
            if current_version != "unknown" and remote_version != "unknown":
                try:
                    if version.parse(remote_version) > version.parse(current_version):
                        version_comparison = "newer_available"
                    elif version.parse(remote_version) < version.parse(current_version):
                        version_comparison = "ahead"
                    else:
                        version_comparison = "same_version"
                except Exception:
                    version_comparison = "unknown"
            
            # Check if we can update (no uncommitted changes)
            can_update = not current.get("has_uncommitted_changes", False) and current.get("is_git_repo", False)
            
            # Determine if update is available
            update_available = current_hash != remote_hash and can_update
            
            return {
                "update_available": update_available,
                "comparison": "newer_available" if update_available else "different",
                "version_comparison": version_comparison,
                "current_version": current_version,
                "remote_version": remote_version,
                "current_hash": current_hash[:8] if current_hash else "unknown",
                "remote_hash": remote_hash[:8] if remote_hash else "unknown",
                "can_update": can_update,
                "uncommitted_changes": current.get("has_uncommitted_changes", False),
                "is_git_repo": current.get("is_git_repo", False),
                "message": self._get_comparison_message(update_available, can_update, current, remote)
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing versions: {e}")
            return {
                "update_available": False,
                "comparison": "error",
                "error": str(e),
                "can_update": False
            }
    
    def _get_comparison_message(self, update_available: bool, can_update: bool, 
                              current: Dict[str, Any], remote: Dict[str, Any]) -> str:
        """Generate a human-readable comparison message."""
        if not current.get("is_git_repo", False):
            return "Not a Git repository - updates not available"
        
        if current.get("has_uncommitted_changes", False):
            return "Uncommitted changes detected - please commit or stash changes before updating"
        
        if update_available:
            return "New version available - ready to update"
        
        if current.get("commit_hash") == remote.get("commit_hash"):
            return "You are running the latest version"
        
        return "Version status unclear - manual check recommended"
    
    def clear_cache(self) -> None:
        """Clear the version cache."""
        try:
            cache_file = Path(".git_version_cache.json")
            if cache_file.exists():
                cache_file.unlink()
                self.logger.info("Version cache cleared")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
