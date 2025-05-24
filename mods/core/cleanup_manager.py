"""
Project Cleanup Manager for TaskHero AI.

Provides comprehensive cleanup functionality for indexed projects,
including individual project cleanup, batch operations, and complete system reset.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core import BaseManager


class ProjectCleanupManager(BaseManager):
    """Manager for project cleanup and reset operations."""
    
    def __init__(self, settings_manager=None):
        """
        Initialize the Project Cleanup Manager.
        
        Args:
            settings_manager: Settings manager instance
        """
        super().__init__("ProjectCleanupManager")
        self.settings_manager = settings_manager
        
    def _perform_initialization(self) -> None:
        """Initialize the cleanup manager."""
        self.logger.info("Project Cleanup Manager initialized")
        self.update_status("cleanup_ready", True)
    
    def list_indexed_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects with index directories.
        
        Returns:
            List of dictionaries containing project information
        """
        projects = []
        
        # Get recent projects from settings
        if self.settings_manager:
            recent_projects = self.settings_manager.get_recent_projects()
            for project in recent_projects:
                project_path = project.get("path", "")
                if project_path and os.path.isdir(project_path):
                    index_dir = os.path.join(project_path, ".index")
                    if os.path.exists(index_dir):
                        # Count indexed files
                        file_count = self._count_indexed_files(index_dir)
                        projects.append({
                            "name": project.get("name", os.path.basename(project_path)),
                            "path": project_path,
                            "index_dir": index_dir,
                            "file_count": file_count,
                            "last_accessed": project.get("last_accessed", "Unknown")
                        })
        
        # Also check current project if different
        if self.settings_manager:
            current_project = self.settings_manager.get_last_directory()
            if current_project and os.path.isdir(current_project):
                index_dir = os.path.join(current_project, ".index")
                if os.path.exists(index_dir):
                    # Check if not already in list
                    if not any(p["path"] == current_project for p in projects):
                        file_count = self._count_indexed_files(index_dir)
                        projects.append({
                            "name": os.path.basename(current_project),
                            "path": current_project,
                            "index_dir": index_dir,
                            "file_count": file_count,
                            "last_accessed": "Current Project"
                        })
        
        return projects
    
    def _count_indexed_files(self, index_dir: str) -> int:
        """
        Count the number of indexed files in an index directory.
        
        Args:
            index_dir: Path to the index directory
            
        Returns:
            Number of indexed files
        """
        try:
            metadata_dir = os.path.join(index_dir, "metadata")
            if os.path.exists(metadata_dir):
                return len([f for f in os.listdir(metadata_dir) if f.endswith(".json")])
            return 0
        except Exception as e:
            self.logger.error(f"Error counting indexed files in {index_dir}: {e}")
            return 0
    
    def cleanup_project(self, project_path: str) -> Tuple[bool, str]:
        """
        Clean up a specific project's index data.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not os.path.isdir(project_path):
                return False, f"Project directory does not exist: {project_path}"
            
            index_dir = os.path.join(project_path, ".index")
            if not os.path.exists(index_dir):
                return False, f"No index directory found in project: {project_path}"
            
            # Remove the entire index directory
            self.logger.info(f"Removing index directory: {index_dir}")
            shutil.rmtree(index_dir)
            
            # Update settings to remove from recent projects
            if self.settings_manager:
                self.settings_manager.remove_from_recent_projects(project_path)
                
                # If this was the current project, clear it
                current_project = self.settings_manager.get_last_directory()
                if current_project == project_path:
                    self.settings_manager.set_last_directory("")
            
            return True, f"Successfully cleaned project: {os.path.basename(project_path)}"
            
        except PermissionError as e:
            return False, f"Permission denied: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error cleaning project {project_path}: {e}")
            return False, f"Error cleaning project: {str(e)}"
    
    def cleanup_multiple_projects(self, project_paths: List[str]) -> Dict[str, Tuple[bool, str]]:
        """
        Clean up multiple projects.
        
        Args:
            project_paths: List of project paths to clean
            
        Returns:
            Dictionary mapping project paths to (success, message) tuples
        """
        results = {}
        
        for project_path in project_paths:
            success, message = self.cleanup_project(project_path)
            results[project_path] = (success, message)
            
            # Log the result
            if success:
                self.logger.info(f"Successfully cleaned: {project_path}")
            else:
                self.logger.error(f"Failed to clean {project_path}: {message}")
        
        return results
    
    def reset_all_projects(self) -> Tuple[bool, str]:
        """
        Reset everything to clean state - removes all indices and clears settings.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            cleaned_count = 0
            failed_count = 0
            
            # Get all indexed projects
            projects = self.list_indexed_projects()
            
            # Clean each project
            for project in projects:
                success, _ = self.cleanup_project(project["path"])
                if success:
                    cleaned_count += 1
                else:
                    failed_count += 1
            
            # Clear all settings related to projects
            if self.settings_manager:
                self.settings_manager.set_last_directory("")
                self.settings_manager.clear_recent_projects()
                self.logger.info("Cleared project settings")
            
            if failed_count == 0:
                return True, f"Successfully reset all {cleaned_count} projects"
            else:
                return False, f"Reset {cleaned_count} projects, {failed_count} failed"
                
        except Exception as e:
            self.logger.error(f"Error during complete reset: {e}")
            return False, f"Error during reset: {str(e)}"
    
    def cleanup_logs_only(self) -> Tuple[bool, str]:
        """
        Clean up only log files.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            logs_dir = Path("logs")
            if logs_dir.exists():
                removed_count = 0
                for log_file in logs_dir.iterdir():
                    if log_file.is_file():
                        log_file.unlink()
                        removed_count += 1
                        
                self.logger.info(f"Removed {removed_count} log files")
                return True, f"Successfully removed {removed_count} log files"
            else:
                return True, "No logs directory found"
                
        except Exception as e:
            self.logger.error(f"Error cleaning logs: {e}")
            return False, f"Error cleaning logs: {str(e)}"
    
    def cleanup_settings_only(self) -> Tuple[bool, str]:
        """
        Reset only settings to defaults.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if self.settings_manager:
                self.settings_manager.reset_to_defaults()
                self.logger.info("Reset settings to defaults")
                return True, "Settings reset to defaults"
            else:
                return False, "Settings manager not available"
                
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
            return False, f"Error resetting settings: {str(e)}"
    
    def get_cleanup_preview(self, operation_type: str, target: str = None) -> Dict[str, Any]:
        """
        Get a preview of what will be cleaned without actually performing the operation.
        
        Args:
            operation_type: Type of cleanup ('project', 'multiple', 'reset_all', 'logs', 'settings')
            target: Target for operation (project path for 'project', list for 'multiple')
            
        Returns:
            Dictionary with preview information
        """
        preview = {
            "operation": operation_type,
            "items_to_clean": [],
            "estimated_size": 0,
            "warnings": []
        }
        
        try:
            if operation_type == "project" and target:
                if os.path.isdir(target):
                    index_dir = os.path.join(target, ".index")
                    if os.path.exists(index_dir):
                        size = self._get_directory_size(index_dir)
                        preview["items_to_clean"].append({
                            "type": "directory",
                            "path": index_dir,
                            "size": size
                        })
                        preview["estimated_size"] = size
                    else:
                        preview["warnings"].append(f"No index directory found: {index_dir}")
                else:
                    preview["warnings"].append(f"Project directory not found: {target}")
                    
            elif operation_type == "reset_all":
                projects = self.list_indexed_projects()
                total_size = 0
                for project in projects:
                    if os.path.exists(project["index_dir"]):
                        size = self._get_directory_size(project["index_dir"])
                        preview["items_to_clean"].append({
                            "type": "directory", 
                            "path": project["index_dir"],
                            "size": size
                        })
                        total_size += size
                preview["estimated_size"] = total_size
                
            elif operation_type == "logs":
                logs_dir = Path("logs")
                if logs_dir.exists():
                    total_size = 0
                    for log_file in logs_dir.iterdir():
                        if log_file.is_file():
                            size = log_file.stat().st_size
                            preview["items_to_clean"].append({
                                "type": "file",
                                "path": str(log_file),
                                "size": size
                            })
                            total_size += size
                    preview["estimated_size"] = total_size
                    
        except Exception as e:
            preview["warnings"].append(f"Error generating preview: {str(e)}")
            
        return preview
    
    def _get_directory_size(self, path: str) -> int:
        """
        Get the total size of a directory.
        
        Args:
            path: Directory path
            
        Returns:
            Size in bytes
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        continue
            return total_size
        except Exception:
            return 0
    
    def format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB" 