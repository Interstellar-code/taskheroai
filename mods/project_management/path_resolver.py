#!/usr/bin/env python3
"""
Centralized Path Resolution Utility for TaskHero AI

This module provides intelligent path resolution for all project components,
ensuring that embeddings, task storage, and other project directories are
found correctly regardless of how the project_root is configured.

TASK-045: Fix systemic path resolution issues across all components
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger("TaskHeroAI.ProjectManagement.PathResolver")


@dataclass
class ProjectPaths:
    """Container for all resolved project paths."""
    project_root: Path
    embeddings_dir: Path
    task_storage_dir: Path
    index_dir: Path
    metadata_dir: Path
    binary_dir: Path
    templates_dir: Path
    setup_file: Path
    
    def __post_init__(self):
        """Ensure all paths are Path objects."""
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, str):
                setattr(self, field_name, Path(field_value))


class PathResolver:
    """Intelligent path resolver for TaskHero AI project components."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the path resolver.
        
        Args:
            project_root: Initial project root directory. If None, uses current working directory.
        """
        self.initial_project_root = Path(project_root) if project_root else Path.cwd()
        self._resolved_paths: Optional[ProjectPaths] = None
        self._setup_settings: Optional[Dict[str, Any]] = None
        
    def resolve_paths(self) -> ProjectPaths:
        """Resolve all project paths intelligently.
        
        Returns:
            ProjectPaths object with all resolved paths
        """
        if self._resolved_paths is not None:
            return self._resolved_paths
            
        logger.info(f"Resolving paths from initial project root: {self.initial_project_root}")
        
        # Step 1: Find the actual project root (directory containing .taskhero_setup.json or .index)
        actual_project_root = self._find_actual_project_root()
        
        # Step 2: Load setup settings if available
        self._load_setup_settings(actual_project_root)
        
        # Step 3: Resolve all specific paths
        embeddings_dir = self._resolve_embeddings_directory(actual_project_root)
        task_storage_dir = self._resolve_task_storage_directory(actual_project_root)
        index_dir = self._resolve_index_directory(actual_project_root)
        
        # Step 4: Derive other paths
        metadata_dir = index_dir / "metadata"
        binary_dir = index_dir / "binary"
        templates_dir = actual_project_root / "mods" / "project_management" / "templates"
        setup_file = actual_project_root / ".taskhero_setup.json"
        
        self._resolved_paths = ProjectPaths(
            project_root=actual_project_root,
            embeddings_dir=embeddings_dir,
            task_storage_dir=task_storage_dir,
            index_dir=index_dir,
            metadata_dir=metadata_dir,
            binary_dir=binary_dir,
            templates_dir=templates_dir,
            setup_file=setup_file
        )
        
        logger.info(f"Resolved project paths:")
        logger.info(f"  Project root: {self._resolved_paths.project_root}")
        logger.info(f"  Embeddings: {self._resolved_paths.embeddings_dir}")
        logger.info(f"  Task storage: {self._resolved_paths.task_storage_dir}")
        logger.info(f"  Index directory: {self._resolved_paths.index_dir}")
        
        return self._resolved_paths
    
    def _find_actual_project_root(self) -> Path:
        """Find the actual project root by searching for key indicators.
        
        Returns:
            Path to the actual project root directory
        """
        search_paths = [
            self.initial_project_root,
            self.initial_project_root.parent,
            self.initial_project_root.parent.parent,
        ]
        
        # Look for .taskhero_setup.json first (most reliable indicator)
        for path in search_paths:
            setup_file = path / ".taskhero_setup.json"
            if setup_file.exists():
                logger.info(f"Found .taskhero_setup.json at: {path}")
                return path
        
        # Look for .index directory
        for path in search_paths:
            index_dir = path / ".index"
            if index_dir.exists() and index_dir.is_dir():
                # Verify it contains expected subdirectories
                if any((index_dir / subdir).exists() for subdir in ["embeddings", "metadata", "binary"]):
                    logger.info(f"Found .index directory at: {path}")
                    return path
        
        # Look for mods directory (indicates this is the TaskHero AI project root)
        for path in search_paths:
            mods_dir = path / "mods"
            if mods_dir.exists() and mods_dir.is_dir():
                # Check if it contains expected modules
                expected_modules = ["project_management", "code", "settings"]
                if all((mods_dir / module).exists() for module in expected_modules):
                    logger.info(f"Found TaskHero AI mods directory at: {path}")
                    return path
        
        # Special handling for 'taskheroai' subdirectory
        if 'taskheroai' in str(self.initial_project_root).lower():
            parent_path = self.initial_project_root.parent
            logger.info(f"Detected 'taskheroai' in path, checking parent: {parent_path}")
            return parent_path
        
        # Fallback to initial project root
        logger.warning(f"Could not find clear project root indicators. Using: {self.initial_project_root}")
        return self.initial_project_root
    
    def _load_setup_settings(self, project_root: Path) -> None:
        """Load settings from .taskhero_setup.json if available.
        
        Args:
            project_root: The resolved project root directory
        """
        setup_file = project_root / ".taskhero_setup.json"
        if setup_file.exists():
            try:
                with open(setup_file, 'r', encoding='utf-8') as f:
                    self._setup_settings = json.load(f)
                logger.info(f"Loaded setup settings from: {setup_file}")
            except Exception as e:
                logger.warning(f"Could not load setup settings from {setup_file}: {e}")
                self._setup_settings = {}
        else:
            self._setup_settings = {}
    
    def _resolve_embeddings_directory(self, project_root: Path) -> Path:
        """Resolve the embeddings directory path.
        
        Args:
            project_root: The resolved project root directory
            
        Returns:
            Path to the embeddings directory
        """
        # Search for existing embeddings directory
        search_paths = [
            project_root / ".index" / "embeddings",
            self.initial_project_root / ".index" / "embeddings",
        ]
        
        for embeddings_path in search_paths:
            if embeddings_path.exists() and embeddings_path.is_dir():
                # Verify it contains embedding files
                if any(embeddings_path.glob("*.json")):
                    logger.info(f"Found embeddings directory with content at: {embeddings_path}")
                    return embeddings_path
                else:
                    logger.debug(f"Found empty embeddings directory at: {embeddings_path}")
        
        # Default to project root .index/embeddings
        default_path = project_root / ".index" / "embeddings"
        logger.info(f"Using default embeddings directory: {default_path}")
        return default_path
    
    def _resolve_task_storage_directory(self, project_root: Path) -> Path:
        """Resolve the task storage directory path.
        
        Args:
            project_root: The resolved project root directory
            
        Returns:
            Path to the task storage directory
        """
        if self._setup_settings:
            # Get paths from settings
            indexed_directory = self._setup_settings.get('codebase_path') or self._setup_settings.get('last_directory')
            task_storage_path = self._setup_settings.get('task_storage_path')
            
            if indexed_directory and task_storage_path:
                indexed_path = Path(indexed_directory)
                
                # Extract just the folder name if it's an absolute path
                if os.path.isabs(task_storage_path) or (':\\' in task_storage_path) or (':/' in task_storage_path):
                    if '\\' in task_storage_path:
                        task_folder_name = task_storage_path.split('\\')[-1]
                    else:
                        task_folder_name = os.path.basename(task_storage_path)
                else:
                    task_folder_name = task_storage_path
                
                resolved_path = indexed_path / task_folder_name
                logger.info(f"Resolved task storage from settings: {resolved_path}")
                return resolved_path
            
            elif task_storage_path:
                # Extract folder name and use with project root
                if os.path.isabs(task_storage_path) or (':\\' in task_storage_path) or (':/' in task_storage_path):
                    if '\\' in task_storage_path:
                        task_folder_name = task_storage_path.split('\\')[-1]
                    else:
                        task_folder_name = os.path.basename(task_storage_path)
                else:
                    task_folder_name = task_storage_path
                
                resolved_path = project_root / task_folder_name
                logger.info(f"Resolved task storage from settings (relative): {resolved_path}")
                return resolved_path
        
        # Default to theherotasks in project root
        default_path = project_root / "theherotasks"
        logger.info(f"Using default task storage directory: {default_path}")
        return default_path
    
    def _resolve_index_directory(self, project_root: Path) -> Path:
        """Resolve the index directory path.
        
        Args:
            project_root: The resolved project root directory
            
        Returns:
            Path to the index directory
        """
        # The index directory should be in the project root
        index_path = project_root / ".index"
        logger.info(f"Using index directory: {index_path}")
        return index_path
    
    def get_paths(self) -> ProjectPaths:
        """Get resolved project paths (convenience method).
        
        Returns:
            ProjectPaths object with all resolved paths
        """
        return self.resolve_paths()
    
    def refresh_paths(self) -> ProjectPaths:
        """Refresh and re-resolve all paths.
        
        Returns:
            ProjectPaths object with newly resolved paths
        """
        self._resolved_paths = None
        self._setup_settings = None
        return self.resolve_paths()


# Global path resolver instance for shared use
_global_path_resolver: Optional[PathResolver] = None


def get_global_path_resolver(project_root: Optional[str] = None) -> PathResolver:
    """Get or create the global path resolver instance.
    
    Args:
        project_root: Project root directory (only used for first initialization)
        
    Returns:
        Global PathResolver instance
    """
    global _global_path_resolver
    if _global_path_resolver is None:
        _global_path_resolver = PathResolver(project_root)
    return _global_path_resolver


def get_project_paths(project_root: Optional[str] = None) -> ProjectPaths:
    """Get resolved project paths using the global resolver.
    
    Args:
        project_root: Project root directory (only used for first initialization)
        
    Returns:
        ProjectPaths object with all resolved paths
    """
    resolver = get_global_path_resolver(project_root)
    return resolver.get_paths()


def refresh_global_paths() -> ProjectPaths:
    """Refresh the global path resolver and get new paths.
    
    Returns:
        ProjectPaths object with newly resolved paths
    """
    global _global_path_resolver
    if _global_path_resolver is not None:
        return _global_path_resolver.refresh_paths()
    else:
        return get_project_paths()
