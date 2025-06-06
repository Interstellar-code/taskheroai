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
import fnmatch
import glob

from ..core import BaseManager
from .version_manager import VersionManager
from ..code.directory import GitIgnorePattern


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

        # GitIgnore patterns for smart backup filtering
        self.gitignore_patterns = []
        self.gitignore_loaded = False

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

        # Essential files and directories to preserve during updates (regardless of .gitignore)
        self.essential_preserve_patterns = [
            "theherotasks/",
            ".env",
            ".taskhero_setup.json",
            # User-created files
            "user_*",
            "custom_*",
        ]

        # Additional files to preserve if not ignored by .gitignore
        self.conditional_preserve_patterns = [
            "logs/",
            "*.log",
            # Virtual environment (usually ignored, but preserve if tracked)
            "venv/",
            ".venv/",
            # IDE files (usually ignored, but preserve if tracked)
            ".vscode/",
            ".idea/",
            # OS files (usually ignored, but preserve if tracked)
            ".DS_Store",
            "Thumbs.db"
        ]

        # Patterns for user/config files that are expected to be modified
        self.user_file_patterns = [
            "theherotasks/",
            ".env",
            ".taskhero_setup.json",
            "taskhero_setup.json",  # Git sometimes shows without leading dot
            ".app_settings.json",
            "app_settings.json",    # Git sometimes shows without leading dot
            "logs/",
            "*.log",
            "user_*",
            "custom_*",
            "venv/",
            ".venv/",
            ".vscode/",
            ".idea/",
            ".DS_Store",
            "Thumbs.db",
            # Backup directories
            ".backup_*",
            # Cache files
            ".git_*_cache.json",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            # Temporary files
            "*.tmp",
            "*.temp",
            ".pytest_cache/",
            ".coverage"
        ]

    def _perform_initialization(self) -> None:
        """Initialize the Git manager."""
        try:
            # Get Git settings from app settings
            git_settings = self._get_git_settings()

            # Initialize version manager with settings manager for consolidated cache
            repository_url = git_settings.get("repository_url", self.default_settings["repository_url"])
            self.version_manager = VersionManager(repository_url, self.settings_manager)

            # Load .gitignore patterns for smart backup filtering
            self._load_gitignore_patterns()

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
                # Use set_setting to preserve setup-specific settings
                for key, value in self.default_settings.items():
                    self.settings_manager.set_setting(f"git.{key}", value, save=False)

                # Save once after setting all git settings
                self.settings_manager.save_settings()
                self.logger.info("Added Git settings to app settings")
        except Exception as e:
            self.logger.error(f"Error ensuring Git settings: {e}")

    def _load_gitignore_patterns(self) -> None:
        """Load and parse .gitignore patterns for smart backup filtering."""
        try:
            gitignore_path = Path(".gitignore")
            if not gitignore_path.exists():
                self.logger.info("No .gitignore file found - backup will use default patterns")
                self.gitignore_loaded = True
                return

            self.gitignore_patterns = []
            base_dir = str(Path.cwd())

            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    pattern_str = line.strip()
                    if not pattern_str or pattern_str.startswith("#"):
                        continue
                    try:
                        self.gitignore_patterns.append(
                            GitIgnorePattern(pattern_str, base_dir)
                        )
                    except Exception as e:
                        self.logger.warning(
                            f"Error compiling gitignore pattern '{pattern_str}' from "
                            f".gitignore:{line_num} - {e}"
                        )

            self.gitignore_loaded = True
            self.logger.info(f"Loaded {len(self.gitignore_patterns)} .gitignore patterns for smart backup")

        except Exception as e:
            self.logger.error(f"Error loading .gitignore patterns: {e}")
            self.gitignore_loaded = True  # Continue without gitignore filtering

    def _is_ignored_by_gitignore(self, file_path: str) -> bool:
        """
        Check if a file path is ignored by .gitignore patterns.

        Args:
            file_path: Path to check (relative or absolute)

        Returns:
            True if file should be ignored, False otherwise
        """
        if not self.gitignore_loaded or not self.gitignore_patterns:
            return False

        try:
            # Convert to absolute path for gitignore matching
            abs_path = str(Path(file_path).resolve())
            is_dir = Path(file_path).is_dir()

            # Check against all gitignore patterns
            ignored_status = False
            for pattern in self.gitignore_patterns:
                if pattern.matches(abs_path, is_dir):
                    ignored_status = not pattern.is_negation

            return ignored_status

        except Exception as e:
            self.logger.debug(f"Error checking gitignore for {file_path}: {e}")
            return False

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
            # Use set_setting to preserve setup-specific settings
            self.settings_manager.set_setting(f"git.{key}", value)
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
        """Get the last cached check result from consolidated settings."""
        try:
            if self.settings_manager:
                settings = self.settings_manager.get_settings()
                git_settings = settings.get("git", {})
                return git_settings.get("update_cache")
            else:
                # Fallback to old cache file if settings manager not available
                cache_file = Path(".git_update_cache.json")
                if cache_file.exists():
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception as e:
            self.logger.debug(f"Error reading update cache: {e}")
        return None

    def _cache_check_result(self, result: Dict[str, Any]) -> None:
        """Cache the check result in consolidated settings."""
        try:
            if self.settings_manager:
                # Use set_setting to preserve setup-specific settings
                self.settings_manager.set_setting("git.update_cache", result)
            else:
                # Fallback to old cache file if settings manager not available
                cache_file = Path(".git_update_cache.json")
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
        except Exception as e:
            self.logger.debug(f"Error caching update result: {e}")

    def perform_update(self, use_stash: bool = True) -> Dict[str, Any]:
        """
        Perform Git update using git stash for clean updates.

        Args:
            use_stash: Whether to use git stash (recommended: True)

        Returns:
            Update result
        """
        if use_stash:
            return self.perform_stash_update()
        else:
            return self.perform_legacy_update()

    def perform_stash_update(self) -> Dict[str, Any]:
        """
        Perform Git update using the new git stash strategy.

        This is the recommended update method that uses:
        1. git stash push (save uncommitted changes)
        2. git fetch && git pull (update from remote)
        3. git stash pop (restore uncommitted changes)

        Returns:
            Update result
        """
        try:
            self.logger.info("Starting Git stash-based update process...")

            # Pre-update checks (simplified for stash-based approach)
            pre_check = self._pre_update_checks_stash()
            if not pre_check["can_update"]:
                return {
                    "success": False,
                    "error": pre_check["error"],
                    "stage": "pre_check"
                }

            # Perform Git stash-based update
            git_result = self._perform_stash_update()
            if not git_result["success"]:
                return {
                    "success": False,
                    "error": f"Git stash update failed: {git_result['error']}",
                    "stage": "git_update",
                    "details": git_result
                }

            # Post-update tasks
            post_result = self._post_update_tasks(git_result)

            # Record update in history
            self._record_update_history(git_result)

            result = {
                "success": True,
                "message": "Git stash update completed successfully",
                "git_result": git_result,
                "post_result": post_result,
                "method": "git_stash",
                "update_timestamp": datetime.now().isoformat()
            }

            self.logger.info("Git stash update completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Error during stash update: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "unknown"
            }

    def perform_legacy_update(self, backup_user_files: bool = True) -> Dict[str, Any]:
        """
        Perform Git update using the legacy backup/restore strategy.

        This method is kept for compatibility but is not recommended.
        Use perform_stash_update() instead.

        Args:
            backup_user_files: Whether to backup user files before update

        Returns:
            Update result
        """
        try:
            self.logger.info("Starting legacy Git update process...")

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
                "message": "Legacy update completed successfully",
                "git_result": git_result,
                "post_result": post_result,
                "method": "legacy_backup",
                "backup_created": backup_info is not None,
                "update_timestamp": datetime.now().isoformat()
            }

            self.logger.info("Legacy Git update completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Error during legacy update: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "unknown"
            }

    def _categorize_uncommitted_files(self) -> Dict[str, List[str]]:
        """
        Categorize uncommitted files into user files and core files.

        Returns:
            Dictionary with 'user_files' and 'core_files' lists
        """
        try:
            # Get uncommitted files
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            if result.returncode != 0:
                return {"user_files": [], "core_files": []}

            uncommitted_files = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # Extract filename from git status output (skip status indicators)
                    filename = line[3:].strip()
                    uncommitted_files.append(filename)

            user_files = []
            core_files = []

            for file_path in uncommitted_files:
                is_user_file = False

                # Check against user file patterns
                for pattern in self.user_file_patterns:
                    if pattern.endswith("/"):
                        # Directory pattern
                        if file_path.startswith(pattern) or file_path.startswith(pattern.rstrip("/")):
                            is_user_file = True
                            break
                    elif "*" in pattern:
                        # Wildcard pattern
                        import fnmatch
                        if fnmatch.fnmatch(file_path, pattern):
                            is_user_file = True
                            break
                    else:
                        # Exact file pattern
                        if file_path == pattern or file_path.endswith("/" + pattern):
                            is_user_file = True
                            break

                if is_user_file:
                    user_files.append(file_path)
                else:
                    core_files.append(file_path)

            return {
                "user_files": user_files,
                "core_files": core_files
            }

        except Exception as e:
            self.logger.error(f"Error categorizing uncommitted files: {e}")
            return {"user_files": [], "core_files": []}

    def _pre_update_checks_stash(self) -> Dict[str, Any]:
        """Simplified pre-update checks for stash-based updates."""
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

            # Check for uncommitted changes (informational only)
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            has_changes = bool(status_result.stdout.strip())
            if has_changes:
                # Count changes for logging
                changes = status_result.stdout.strip().split('\n')
                self.logger.info(f"Found {len(changes)} uncommitted changes - will use git stash")

            return {
                "can_update": True,
                "has_uncommitted_changes": has_changes,
                "changes_count": len(status_result.stdout.strip().split('\n')) if has_changes else 0
            }

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

    def _pre_update_checks(self) -> Dict[str, Any]:
        """Legacy pre-update checks with smart uncommitted changes handling."""
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

            # Smart uncommitted changes check
            file_categories = self._categorize_uncommitted_files()
            core_files = file_categories.get("core_files", [])
            user_files = file_categories.get("user_files", [])

            if core_files:
                # Block update if core TaskHero files are modified
                core_files_str = ", ".join(core_files[:5])  # Show first 5 files
                if len(core_files) > 5:
                    core_files_str += f" (and {len(core_files) - 5} more)"

                return {
                    "can_update": False,
                    "error": f"Core TaskHero files have uncommitted changes: {core_files_str}. Please commit or stash these changes first."
                }

            if user_files:
                # Allow update but log user files that will be preserved
                user_files_str = ", ".join(user_files[:3])
                if len(user_files) > 3:
                    user_files_str += f" (and {len(user_files) - 3} more)"

                self.logger.info(f"User files detected and will be preserved: {user_files_str}")

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

            return {
                "can_update": True,
                "user_files_count": len(user_files),
                "core_files_count": len(core_files)
            }

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
        """Create gitignore-aware backup of user files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(f".backup_{timestamp}")
            backup_dir.mkdir(exist_ok=True)

            backed_up_files = []
            skipped_files = []
            essential_files = []

            # Process essential files first (always backup regardless of .gitignore)
            for pattern in self.essential_preserve_patterns:
                files_backed_up = self._backup_pattern(pattern, backup_dir, force_backup=True)
                backed_up_files.extend(files_backed_up)
                essential_files.extend(files_backed_up)

            # Process conditional files (only backup if not ignored by .gitignore)
            for pattern in self.conditional_preserve_patterns:
                files_backed_up, files_skipped = self._backup_pattern_conditional(pattern, backup_dir)
                backed_up_files.extend(files_backed_up)
                skipped_files.extend(files_skipped)

            # Log backup summary
            self.logger.info(f"Backup summary: {len(backed_up_files)} files backed up, {len(skipped_files)} files skipped (gitignore)")
            if essential_files:
                self.logger.info(f"Essential files backed up: {', '.join(essential_files[:5])}")
            if skipped_files:
                self.logger.info(f"Files skipped due to .gitignore: {', '.join(skipped_files[:5])}")

            return {
                "success": True,
                "backup_path": str(backup_dir),
                "backed_up_files": backed_up_files,
                "skipped_files": skipped_files,
                "essential_files": essential_files,
                "file_count": len(backed_up_files),
                "skipped_count": len(skipped_files)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _backup_pattern(self, pattern: str, backup_dir: Path, force_backup: bool = False) -> List[str]:
        """
        Backup files matching a pattern.

        Args:
            pattern: File pattern to match
            backup_dir: Backup directory
            force_backup: If True, backup regardless of .gitignore

        Returns:
            List of backed up file paths
        """
        backed_up_files = []

        try:
            # Handle directory patterns
            if pattern.endswith("/"):
                dir_path = Path(pattern.rstrip("/"))
                if dir_path.exists() and dir_path.is_dir():
                    if force_backup or not self._is_ignored_by_gitignore(str(dir_path)):
                        backup_path = backup_dir / dir_path
                        shutil.copytree(dir_path, backup_path)
                        backed_up_files.append(str(dir_path))
            else:
                # Handle file patterns
                if "*" in pattern:
                    for file_path in glob.glob(pattern):
                        if Path(file_path).exists():
                            if force_backup or not self._is_ignored_by_gitignore(file_path):
                                backup_path = backup_dir / file_path
                                backup_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(file_path, backup_path)
                                backed_up_files.append(file_path)
                else:
                    file_path = Path(pattern)
                    if file_path.exists():
                        if force_backup or not self._is_ignored_by_gitignore(str(file_path)):
                            backup_path = backup_dir / file_path
                            backup_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, backup_path)
                            backed_up_files.append(str(file_path))

        except Exception as e:
            self.logger.warning(f"Error backing up pattern '{pattern}': {e}")

        return backed_up_files

    def _backup_pattern_conditional(self, pattern: str, backup_dir: Path) -> Tuple[List[str], List[str]]:
        """
        Backup files matching a pattern only if not ignored by .gitignore.

        Args:
            pattern: File pattern to match
            backup_dir: Backup directory

        Returns:
            Tuple of (backed_up_files, skipped_files)
        """
        backed_up_files = []
        skipped_files = []

        try:
            # Handle directory patterns
            if pattern.endswith("/"):
                dir_path = Path(pattern.rstrip("/"))
                if dir_path.exists() and dir_path.is_dir():
                    if self._is_ignored_by_gitignore(str(dir_path)):
                        skipped_files.append(str(dir_path))
                    else:
                        backup_path = backup_dir / dir_path
                        shutil.copytree(dir_path, backup_path)
                        backed_up_files.append(str(dir_path))
            else:
                # Handle file patterns
                if "*" in pattern:
                    for file_path in glob.glob(pattern):
                        if Path(file_path).exists():
                            if self._is_ignored_by_gitignore(file_path):
                                skipped_files.append(file_path)
                            else:
                                backup_path = backup_dir / file_path
                                backup_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(file_path, backup_path)
                                backed_up_files.append(file_path)
                else:
                    file_path = Path(pattern)
                    if file_path.exists():
                        if self._is_ignored_by_gitignore(str(file_path)):
                            skipped_files.append(str(file_path))
                        else:
                            backup_path = backup_dir / file_path
                            backup_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, backup_path)
                            backed_up_files.append(str(file_path))

        except Exception as e:
            self.logger.warning(f"Error processing pattern '{pattern}': {e}")

        return backed_up_files, skipped_files

    def _perform_stash_update(self) -> Dict[str, Any]:
        """Perform Git update using stash, pull, and stash pop strategy."""
        stash_created = False
        stash_name = f"TaskHero-auto-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        try:
            self.logger.info("Starting git stash-based update...")

            # Check if there are any uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            has_changes = bool(status_result.stdout.strip())

            # Step 1: Stash changes if any exist
            if has_changes:
                self.logger.info(f"Stashing {len(status_result.stdout.strip().split())} uncommitted changes...")
                stash_result = subprocess.run(
                    ["git", "stash", "push", "-m", stash_name],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd()
                )

                if stash_result.returncode == 0:
                    stash_created = True
                    self.logger.info(f"✓ Successfully stashed changes as: {stash_name}")
                else:
                    return {
                        "success": False,
                        "error": f"Failed to stash changes: {stash_result.stderr}",
                        "stage": "stash"
                    }
            else:
                self.logger.info("No uncommitted changes to stash")

            # Step 2: Fetch latest changes
            self.logger.info("Fetching latest changes from remote...")
            fetch_result = subprocess.run(
                ["git", "fetch", "origin"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=60
            )

            if fetch_result.returncode != 0:
                if stash_created:
                    self._restore_stash_by_name(stash_name)
                return {
                    "success": False,
                    "error": f"Git fetch failed: {fetch_result.stderr}",
                    "stage": "fetch"
                }

            self.logger.info("✓ Successfully fetched changes")

            # Step 3: Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "master"
            self.logger.info(f"Current branch: {current_branch}")

            # Step 4: Pull changes
            self.logger.info(f"Pulling changes from origin/{current_branch}...")
            pull_result = subprocess.run(
                ["git", "pull", "origin", current_branch],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=60
            )

            if pull_result.returncode != 0:
                if stash_created:
                    self._restore_stash_by_name(stash_name)
                return {
                    "success": False,
                    "error": f"Git pull failed: {pull_result.stderr}",
                    "stage": "pull"
                }

            self.logger.info("✓ Successfully pulled changes")

            # Step 5: Restore stashed changes if any
            stash_conflicts = False
            if stash_created:
                self.logger.info("Restoring stashed changes...")
                pop_result = self._restore_stash_by_name(stash_name)
                if not pop_result["success"]:
                    if "conflict" in pop_result.get("error", "").lower():
                        stash_conflicts = True
                        self.logger.warning("Stash pop resulted in conflicts - manual resolution required")
                    else:
                        self.logger.warning(f"Failed to restore stash: {pop_result['error']}")
                else:
                    self.logger.info("✓ Successfully restored stashed changes")

            # Step 6: Get new commit info
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            new_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"

            result = {
                "success": True,
                "method": "git_stash",
                "branch": current_branch,
                "new_commit": new_commit,
                "stash_used": stash_created,
                "stash_name": stash_name if stash_created else None,
                "stash_restored": stash_created and not stash_conflicts,
                "has_conflicts": stash_conflicts,
                "fetch_output": fetch_result.stdout,
                "pull_output": pull_result.stdout
            }

            if stash_conflicts:
                result["warning"] = "Update completed but stash restoration had conflicts. Please resolve manually."
                result["manual_action_required"] = True

            self.logger.info("Git stash update completed successfully")
            return result

        except subprocess.TimeoutExpired:
            if stash_created:
                self._restore_stash_by_name(stash_name)
            return {
                "success": False,
                "error": "Git operation timed out",
                "stage": "timeout"
            }
        except Exception as e:
            if stash_created:
                self._restore_stash_by_name(stash_name)
            return {
                "success": False,
                "error": str(e),
                "stage": "exception"
            }

    def _perform_git_update(self) -> Dict[str, Any]:
        """Legacy Git update method with smart user file handling."""
        stash_created = False
        try:
            # Check if there are any uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            has_changes = bool(status_result.stdout.strip())

            # If there are changes, stash them temporarily
            if has_changes:
                stash_result = subprocess.run(
                    ["git", "stash", "push", "-m", "TaskHero auto-update stash"],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd()
                )

                if stash_result.returncode == 0:
                    stash_created = True
                    self.logger.info("Stashed uncommitted changes for update")
                else:
                    self.logger.warning(f"Failed to stash changes: {stash_result.stderr}")

            # Fetch latest changes
            fetch_result = subprocess.run(
                ["git", "fetch", "origin"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=60
            )

            if fetch_result.returncode != 0:
                # Restore stash if fetch failed
                if stash_created:
                    self._restore_stash()
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
                # Restore stash if pull failed
                if stash_created:
                    self._restore_stash()
                return {
                    "success": False,
                    "error": f"Git pull failed: {pull_result.stderr}"
                }

            # Restore stashed changes
            if stash_created:
                restore_result = self._restore_stash()
                if not restore_result:
                    self.logger.warning("Failed to restore stashed changes - they remain in stash")

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
                "pull_output": pull_result.stdout,
                "stash_used": stash_created,
                "stash_restored": stash_created
            }

        except subprocess.TimeoutExpired:
            # Restore stash if operation timed out
            if stash_created:
                self._restore_stash()
            return {
                "success": False,
                "error": "Git operation timed out"
            }
        except Exception as e:
            # Restore stash if operation failed
            if stash_created:
                self._restore_stash()
            return {
                "success": False,
                "error": str(e)
            }

    def _restore_stash_by_name(self, stash_name: str) -> Dict[str, Any]:
        """Restore a specific stash by name."""
        try:
            # Find the stash by name
            stash_list_result = subprocess.run(
                ["git", "stash", "list"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            if not stash_list_result.stdout.strip():
                return {
                    "success": True,
                    "message": "No stashes found"
                }

            # Find the stash index for our named stash
            stash_index = None
            for line in stash_list_result.stdout.strip().split('\n'):
                if stash_name in line:
                    # Extract stash index (e.g., "stash@{0}")
                    stash_index = line.split(':')[0]
                    break

            if not stash_index:
                return {
                    "success": False,
                    "error": f"Stash '{stash_name}' not found"
                }

            # Pop the specific stash
            stash_pop_result = subprocess.run(
                ["git", "stash", "pop", stash_index],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            if stash_pop_result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Successfully restored stash: {stash_name}",
                    "output": stash_pop_result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to restore stash: {stash_pop_result.stderr}",
                    "output": stash_pop_result.stdout
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error restoring stash: {str(e)}"
            }

    def _restore_stash(self) -> bool:
        """Restore the most recent stash (legacy method)."""
        try:
            # Check if there are any stashes
            stash_list_result = subprocess.run(
                ["git", "stash", "list"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            if not stash_list_result.stdout.strip():
                return True  # No stash to restore

            # Pop the most recent stash
            stash_pop_result = subprocess.run(
                ["git", "stash", "pop"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            if stash_pop_result.returncode == 0:
                self.logger.info("Successfully restored stashed changes")
                return True
            else:
                self.logger.error(f"Failed to restore stash: {stash_pop_result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error restoring stash: {e}")
            return False

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
