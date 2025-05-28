"""
Settings Manager for TaskHero AI.

Handles application settings, user preferences, and persistent configuration.
This extracts settings functionality from the monolithic app.py.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core import BaseManager


class SettingsManager(BaseManager):
    """Manager for application settings and user preferences."""

    def __init__(self, settings_file: str = ".taskhero_setup.json"):
        """
        Initialize the settings manager.

        Args:
            settings_file: Path to the settings file
        """
        super().__init__("SettingsManager", settings_file)
        self.settings_file = Path(settings_file)
        self.settings: Dict[str, Any] = {}

    def _perform_initialization(self) -> None:
        """Initialize the settings manager."""
        self.load_settings()
        self.update_status("settings_loaded", True)
        self.update_status("settings_file", str(self.settings_file))

    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from the settings file and merge with defaults.

        Returns:
            Dict containing the loaded settings merged with defaults
        """
        try:
            # Start with default settings
            self.settings = self.get_default_settings()

            if self.settings_file.exists():
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    existing_settings = json.load(f)

                # Merge existing settings with defaults (existing settings take precedence)
                self.settings = self._merge_settings(self.settings, existing_settings)
                self.logger.info(f"Settings loaded from {self.settings_file} and merged with defaults")
            else:
                self.logger.info("Using default settings (no existing settings file)")

            return self.settings
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self.settings = self.get_default_settings()
            return self.settings

    def save_settings(self, settings: Optional[Dict[str, Any]] = None) -> None:
        """Save current settings to the settings file, preserving setup-specific settings."""
        try:
            # Use provided settings or current settings
            settings_to_save = settings if settings is not None else self.settings.copy()

            # Setup-specific keys that should be preserved from the original file
            setup_specific_keys = {
                'codebase_path', 'task_storage_path', 'repository_type',
                'setup_completed', 'next_task_number'
            }

            # If the file exists, load it and preserve setup-specific settings
            if self.settings_file.exists():
                try:
                    with open(self.settings_file, "r", encoding="utf-8") as f:
                        existing_settings = json.load(f)

                    # Preserve setup-specific settings from the existing file
                    for key in setup_specific_keys:
                        if key in existing_settings:
                            settings_to_save[key] = existing_settings[key]
                            self.logger.debug(f"Preserved setup-specific setting: {key}")

                except Exception as e:
                    self.logger.warning(f"Could not read existing settings for preservation: {e}")

            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings_to_save, f, indent=2, ensure_ascii=False)

            # Update internal settings if external settings were provided
            if settings is not None:
                self.settings = settings

            self.logger.info(f"Settings saved to {self.settings_file} (setup-specific settings preserved)")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")

    def get_settings(self) -> Dict[str, Any]:
        """Get all current settings."""
        return self.settings.copy()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key (supports dot notation like 'ui.theme')
            default: Default value if key not found

        Returns:
            The setting value or default
        """
        keys = key.split('.')
        value = self.settings

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set_setting(self, key: str, value: Any, save: bool = True) -> None:
        """
        Set a setting value.

        Args:
            key: Setting key (supports dot notation)
            value: Value to set
            save: Whether to immediately save to file
        """
        keys = key.split('.')
        current = self.settings

        # Navigate to the correct nested dict
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the value
        current[keys[-1]] = value

        if save:
            self.save_settings()

        self.logger.debug(f"Setting '{key}' set to '{value}'")

    def get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings."""
        return {
            "last_directory": "",
            "recent_projects": [],
            "ui": {
                "enable_markdown_rendering": True,
                "show_thinking_blocks": False,
                "enable_streaming_mode": False,
                "theme": "default",
                "terminal_width": 80
            },
            "ai": {
                "default_provider": "anthropic",
                "max_chat_history": 50,
                "auto_save_chats": True
            },
            "project_management": {
                "auto_priority": True,
                "kanban_enabled": True,
                "default_project_template": "basic"
            },
            "indexing": {
                "auto_index": True,
                "index_timeout": 300,
                "batch_size": 10
            },
            "git": {
                "auto_check_enabled": True,
                "last_check_timestamp": None,
                "notifications_enabled": True,
                "repository_url": "https://github.com/Interstellar-code/taskheroai",
                "current_version": "1.0.0",
                "last_update_timestamp": None,
                "update_history": []
            }
        }

    def get_last_directory(self) -> str:
        """Get the last indexed directory."""
        return self.get_setting("last_directory", "")

    def set_last_directory(self, directory: str) -> None:
        """Set the last indexed directory."""
        self.set_setting("last_directory", directory)
        self.add_to_recent_projects(directory)

    def get_recent_projects(self) -> List[Dict[str, str]]:
        """Get list of recent projects."""
        return self.get_setting("recent_projects", [])

    def add_to_recent_projects(self, directory: str, max_recent: int = 10) -> None:
        """
        Add a directory to recent projects.

        Args:
            directory: Directory path to add
            max_recent: Maximum number of recent projects to keep
        """
        if not directory or not Path(directory).exists():
            return

        recent_projects = self.get_recent_projects()

        # Create project entry
        project_entry = {
            "path": directory,
            "name": Path(directory).name,
            "last_accessed": self._get_current_timestamp()
        }

        # Remove if already exists
        recent_projects = [p for p in recent_projects if p.get("path") != directory]

        # Add to front
        recent_projects.insert(0, project_entry)

        # Limit size
        recent_projects = recent_projects[:max_recent]

        self.set_setting("recent_projects", recent_projects)

    def remove_from_recent_projects(self, directory: str) -> None:
        """Remove a directory from recent projects."""
        recent_projects = self.get_recent_projects()
        recent_projects = [p for p in recent_projects if p.get("path") != directory]
        self.set_setting("recent_projects", recent_projects)

    def clear_recent_projects(self) -> None:
        """Clear all recent projects."""
        self.set_setting("recent_projects", [])

    def get_ui_setting(self, key: str, default: Any = None) -> Any:
        """Get a UI-specific setting."""
        return self.get_setting(f"ui.{key}", default)

    def set_ui_setting(self, key: str, value: Any) -> None:
        """Set a UI-specific setting."""
        self.set_setting(f"ui.{key}", value)

    def toggle_ui_setting(self, key: str) -> bool:
        """
        Toggle a boolean UI setting.

        Args:
            key: Setting key

        Returns:
            New value after toggle
        """
        current = self.get_ui_setting(key, False)
        new_value = not current
        self.set_ui_setting(key, new_value)
        return new_value

    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _merge_settings(self, defaults: Dict[str, Any], existing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge existing settings with defaults.

        Args:
            defaults: Default settings structure
            existing: Existing settings from file

        Returns:
            Merged settings with existing values taking precedence
        """
        merged = defaults.copy()

        # Setup-specific keys that should be preserved from existing settings
        setup_specific_keys = {
            'codebase_path', 'task_storage_path', 'repository_type',
            'setup_completed', 'next_task_number'
        }

        for key, value in existing.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                merged[key] = self._merge_settings(merged[key], value)
            else:
                # Use existing value (takes precedence over default)
                merged[key] = value

        # Special handling for last_directory: use codebase_path if last_directory is empty
        if 'codebase_path' in existing and existing['codebase_path']:
            if not merged.get('last_directory'):
                merged['last_directory'] = existing['codebase_path']
                self.logger.debug(f"Set last_directory from codebase_path: {existing['codebase_path']}")

        return merged

    def export_settings(self, file_path: str) -> bool:
        """
        Export settings to a file.

        Args:
            file_path: Path to export file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Settings exported to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            return False

    def import_settings(self, file_path: str) -> bool:
        """
        Import settings from a file.

        Args:
            file_path: Path to import file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                imported_settings = json.load(f)

            # Merge with current settings
            self.settings.update(imported_settings)
            self.save_settings()

            self.logger.info(f"Settings imported from {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            return False

    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self.settings = self.get_default_settings()
        self.save_settings()
        self.logger.info("Settings reset to defaults")

    def _perform_reset(self) -> None:
        """Reset the settings manager."""
        self.reset_to_defaults()