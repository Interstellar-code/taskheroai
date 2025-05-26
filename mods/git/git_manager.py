"""
Git Manager for TaskHero AI.

Handles Git operations, updates, and file preservation.
"""

import json
import logging
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from ..core import BaseManager
from .version_manager import VersionManager


class GitManager(BaseManager):
    """Manages Git operations and auto-updates for TaskHero AI."""

    def __init__(self, settings_manager=None):
        """
        Initialize the Git manager.
        
        Args:
            settings_manager: Settings manager instance
        """
        super().__init__("GitManager")
        self.settings_manager = settings_manager
        self.version_manager = None
        
        # Default settings
        self.default_settings = {
            "auto_check_enabled": True,
            "last_check_timestamp": None,
            "notifications_enabled": True,
            "repository_url": "https://github.com/Interstellar-code/taskheroai",
            "current_version": "1.0.0",
            "last_update_timestamp": None,
            "update_history": []
        }
        
        # Files and directories to preserve during updates
        self.preserve_patterns = [
            "theherotasks/",
            "app_settings.json",
            ".env",
            ".taskhero_setup.json",
            "logs/",
            "*.log",
            ".git_version_cache.json",
            # User-created files
            "user_*",
            "custom_*",
            # Virtual environment
            "venv/",
            ".venv/",
            # IDE files
            ".vscode/",
            ".idea/",
            # OS files
            ".DS_Store",
            "Thumbs.db"
        ]

    def _perform_initialization(self) -> None:
        """Initialize the Git manager."""
        try:
            # Get Git settings from app settings
            git_settings = self._get_git_settings()
            
            # Initialize version manager
            repository_url = git_settings.get("repository_url", self.default_settings["repository_url"])
            self.version_manager = VersionManager(repository_url)
            
            # Ensure Git settings exist in app settings
            self._ensure_git_settings()
            
            self.logger.info("Git Manager initialized")
            self.update_status("git_ready", True)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Git manager: {e}")
            self.update_status("git_error", str(e))

    def _get_git_settings(self) -> Dict[str, Any]:
        """Get Git settings from app settings."""
        if not self.settings_manager:
            return self.default_settings.copy()
        
        try:
            settings = self.settings_manager.get_settings()
            return settings.get("git", self.default_settings.copy())
        except Exception as e:
            self.logger.error(f"Error getting Git settings: {e}")
            return self.default_settings.copy()

    def _ensure_git_settings(self) -> None:
        """Ensure Git settings exist in app settings."""
        if not self.settings_manager:
            return
        
        try:
            settings = self.settings_manager.get_settings()
            if "git" not in settings:
                settings["git"] = self.default_settings.copy()
                self.settings_manager.save_settings(settings)
                self.logger.info("Added Git settings to app settings")
        except Exception as e:
            self.logger.error(f"Error ensuring Git settings: {e}")

    def update_git_setting(self, key: str, value: Any) -> bool:
        """
        Update a specific Git setting.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if successful, False otherwise
        """
        if not self.settings_manager:
            return False
        
        try:
            settings = self.settings_manager.get_settings()
            if "git" not in settings:
                settings["git"] = self.default_settings.copy()
            
            settings["git"][key] = value
            self.settings_manager.save_settings(settings)
            self.logger.info(f"Updated Git setting {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating Git setting {key}: {e}")
            return False

    def check_for_updates(self, force_check: bool = False) -> Dict[str, Any]:
        """
        Check for available updates.
        
        Args:
            force_check: Force check even if recently checked
            
        Returns:
            Update check result
        """
        try:
            if not self.version_manager:
                return {
                    "success": False,
                    "error": "Version manager not initialized",
                    "update_available": False
                }
            
            # Check if we should skip (unless forced)
            if not force_check and not self._should_check_for_updates():
                last_result = self._get_last_check_result()
                if last_result:
                    return last_result
            
            self.logger.info("Checking for updates...")
            
            # Get current and remote versions
            current_version = self.version_manager.get_current_version()
            remote_version = self.version_manager.get_remote_version(use_cache=not force_check)
            
            # Compare versions
            comparison = self.version_manager.compare_versions(current_version, remote_version)
            
            # Prepare result
            result = {
                "success": True,
                "check_timestamp": datetime.now().isoformat(),
                "current": current_version,
                "remote": remote_version,
                "comparison": comparison,
                "update_available": comparison.get("update_available", False),
                "can_update": comparison.get("can_update", False),
                "message": comparison.get("message", "")
            }
            
            # Update last check timestamp
            self.update_git_setting("last_check_timestamp", result["check_timestamp"])
            
            # Cache result
            self._cache_check_result(result)
            
            self.logger.info(f"Update check completed: {result['message']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return {
                "success": False,
                "error": str(e),
                "update_available": False,
                "check_timestamp": datetime.now().isoformat()
            }

    def _should_check_for_updates(self) -> bool:
        """Check if we should perform an update check."""
        git_settings = self._get_git_settings()
        
        if not git_settings.get("auto_check_enabled", True):
            return False
        
        last_check = git_settings.get("last_check_timestamp")
        if not last_check:
            return True
        
        try:
            last_check_time = datetime.fromisoformat(last_check)
            # Check at most once per hour
            return (datetime.now() - last_check_time).total_seconds() > 3600
        except Exception:
            return True

    def _get_last_check_result(self) -> Optional[Dict[str, Any]]:
        """Get the last cached check result."""
        try:
            cache_file = Path(".git_update_cache.json")
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.debug(f"Error reading update cache: {e}")
        return None

    def _cache_check_result(self, result: Dict[str, Any]) -> None:
        """Cache the check result."""
        try:
            cache_file = Path(".git_update_cache.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            self.logger.debug(f"Error caching update result: {e}")

    def perform_update(self, backup_user_files: bool = True) -> Dict[str, Any]:
        """
        Perform Git update while preserving user files.
        
        Args:
            backup_user_files: Whether to backup user files before update
            
        Returns:
            Update result
        """
        try:
            self.logger.info("Starting Git update process...")
            
            # Pre-update checks
            pre_check = self._pre_update_checks()
            if not pre_check["can_update"]:
                return {
                    "success": False,
                    "error": pre_check["error"],
                    "stage": "pre_check"
                }
            
            # Backup user files if requested
            backup_info = None
            if backup_user_files:
                backup_info = self._backup_user_files()
                if not backup_info["success"]:
                    return {
                        "success": False,
                        "error": f"Backup failed: {backup_info['error']}",
                        "stage": "backup"
                    }
            
            # Perform Git operations
            git_result = self._perform_git_update()
            if not git_result["success"]:
                # Restore backup if update failed
                if backup_info and backup_info["success"]:
                    self._restore_backup(backup_info["backup_path"])
                
                return {
                    "success": False,
                    "error": f"Git update failed: {git_result['error']}",
                    "stage": "git_update",
                    "backup_restored": backup_info is not None
                }
            
            # Post-update tasks
            post_result = self._post_update_tasks(git_result)
            
            # Clean up backup if successful
            if backup_info and backup_info["success"]:
                self._cleanup_backup(backup_info["backup_path"])
            
            # Record update in history
            self._record_update_history(git_result)
            
            result = {
                "success": True,
                "message": "Update completed successfully",
                "git_result": git_result,
                "post_result": post_result,
                "backup_created": backup_info is not None,
                "update_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("Git update completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during update: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "unknown"
            }

    def _pre_update_checks(self) -> Dict[str, Any]:
        """Perform pre-update checks."""
        try:
            # Check if Git is available
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    "can_update": False,
                    "error": "Git is not installed or not available in PATH"
                }
            
            # Check if we're in a Git repository
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            if result.returncode != 0:
                return {
                    "can_update": False,
                    "error": "Not in a Git repository"
                }
            
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            if result.stdout.strip():
                return {
                    "can_update": False,
                    "error": "Uncommitted changes detected. Please commit or stash changes first."
                }
            
            # Check network connectivity to remote
            result = subprocess.run(
                ["git", "ls-remote", "--heads", "origin"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=30
            )
            if result.returncode != 0:
                return {
                    "can_update": False,
                    "error": "Cannot connect to remote repository"
                }
            
            return {"can_update": True}
            
        except subprocess.TimeoutExpired:
            return {
                "can_update": False,
                "error": "Timeout connecting to remote repository"
            }
        except Exception as e:
            return {
                "can_update": False,
                "error": f"Pre-update check failed: {str(e)}"
            }

    def _backup_user_files(self) -> Dict[str, Any]:
        """Create backup of user files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(f".backup_{timestamp}")
            backup_dir.mkdir(exist_ok=True)
            
            backed_up_files = []
            
            for pattern in self.preserve_patterns:
                # Handle directory patterns
                if pattern.endswith("/"):
                    dir_path = Path(pattern.rstrip("/"))
                    if dir_path.exists() and dir_path.is_dir():
                        backup_path = backup_dir / dir_path
                        shutil.copytree(dir_path, backup_path)
                        backed_up_files.append(str(dir_path))
                else:
                    # Handle file patterns
                    if "*" in pattern:
                        import glob
                        for file_path in glob.glob(pattern):
                            if Path(file_path).exists():
                                backup_path = backup_dir / file_path
                                backup_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(file_path, backup_path)
                                backed_up_files.append(file_path)
                    else:
                        file_path = Path(pattern)
                        if file_path.exists():
                            backup_path = backup_dir / file_path
                            backup_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, backup_path)
                            backed_up_files.append(str(file_path))
            
            return {
                "success": True,
                "backup_path": str(backup_dir),
                "backed_up_files": backed_up_files,
                "file_count": len(backed_up_files)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _perform_git_update(self) -> Dict[str, Any]:
        """Perform the actual Git update."""
        try:
            # Fetch latest changes
            fetch_result = subprocess.run(
                ["git", "fetch", "origin"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=60
            )
            
            if fetch_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Git fetch failed: {fetch_result.stderr}"
                }
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "master"
            
            # Pull changes
            pull_result = subprocess.run(
                ["git", "pull", "origin", current_branch],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=60
            )
            
            if pull_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Git pull failed: {pull_result.stderr}"
                }
            
            # Get new commit info
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            new_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
            
            return {
                "success": True,
                "branch": current_branch,
                "new_commit": new_commit,
                "fetch_output": fetch_result.stdout,
                "pull_output": pull_result.stdout
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Git operation timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _restore_backup(self, backup_path: str) -> bool:
        """Restore files from backup."""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return False
            
            # Restore all backed up files
            for item in backup_dir.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(backup_dir)
                    target_path = Path(relative_path)
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_path)
            
            self.logger.info(f"Restored backup from {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {e}")
            return False

    def _cleanup_backup(self, backup_path: str) -> None:
        """Clean up backup directory."""
        try:
            backup_dir = Path(backup_path)
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
                self.logger.info(f"Cleaned up backup {backup_path}")
        except Exception as e:
            self.logger.error(f"Error cleaning up backup: {e}")

    def _post_update_tasks(self, git_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform post-update tasks."""
        try:
            tasks_completed = []
            
            # Update version info
            if self.version_manager:
                current_version = self.version_manager.get_current_version()
                self.update_git_setting("current_version", current_version.get("version", "unknown"))
                tasks_completed.append("Updated version info")
            
            # Update last update timestamp
            self.update_git_setting("last_update_timestamp", datetime.now().isoformat())
            tasks_completed.append("Updated timestamp")
            
            # Clear version cache to force fresh check
            if self.version_manager:
                self.version_manager.clear_cache()
                tasks_completed.append("Cleared version cache")
            
            return {
                "success": True,
                "tasks_completed": tasks_completed
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _record_update_history(self, git_result: Dict[str, Any]) -> None:
        """Record update in history."""
        try:
            git_settings = self._get_git_settings()
            history = git_settings.get("update_history", [])
            
            # Add new entry
            history.append({
                "timestamp": datetime.now().isoformat(),
                "commit": git_result.get("new_commit", "unknown"),
                "branch": git_result.get("branch", "unknown"),
                "success": git_result.get("success", False)
            })
            
            # Keep only last 10 entries
            if len(history) > 10:
                history = history[-10:]
            
            self.update_git_setting("update_history", history)
            
        except Exception as e:
            self.logger.error(f"Error recording update history: {e}")

    def get_update_status(self) -> Dict[str, Any]:
        """Get current update status and settings."""
        try:
            git_settings = self._get_git_settings()
            
            # Get last check result
            last_check = self._get_last_check_result()
            
            return {
                "settings": git_settings,
                "last_check": last_check,
                "version_manager_ready": self.version_manager is not None,
                "git_available": self._is_git_available(),
                "is_git_repo": self._is_git_repository()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting update status: {e}")
            return {
                "error": str(e),
                "settings": self.default_settings.copy()
            }

    def _is_git_available(self) -> bool:
        """Check if Git is available."""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def _is_git_repository(self) -> bool:
        """Check if current directory is a Git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            return result.returncode == 0
        except Exception:
            return False

    def _perform_reset(self) -> None:
        """Reset the Git manager."""
        self.version_manager = None
        self.logger.info("Git manager reset")
