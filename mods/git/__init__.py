"""
Git Integration Module for TaskHero AI.

Provides Git integration and auto-update functionality.
"""

from .git_manager import GitManager
from .version_manager import VersionManager

__all__ = ['GitManager', 'VersionManager']
