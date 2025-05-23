"""
Task Manager Module

Handles task management functionality originally from TaskHeroMD PowerShell scripts.
Provides functionality for managing tasks across different states: todo, inprogress, done, etc.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("TaskHeroAI.ProjectManagement.TaskManager")


class Task:
    """Represents a single task."""
    
    def __init__(self, task_data: Dict[str, Any], file_path: str):
        self.file_path = file_path
        self.data = task_data
        
    @property
    def title(self) -> str:
        return self.data.get('title', 'Untitled Task')
    
    @property
    def status(self) -> str:
        return self.data.get('status', 'todo')
    
    @property
    def priority(self) -> str:
        return self.data.get('priority', 'medium')
    
    @property
    def due_date(self) -> Optional[str]:
        return self.data.get('due_date')
    
    @property
    def created_date(self) -> Optional[str]:
        return self.data.get('created_date')


class TaskManager:
    """Manages tasks across different states and provides task operations."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize TaskManager.
        
        Args:
            project_root: Root directory for project management. Defaults to current working directory.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.planning_dir = self.project_root / "mods" / "project_management" / "planning"
        self.templates_dir = self.project_root / "mods" / "project_management" / "templates"
        
        # Ensure planning directories exist
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            "todo", "inprogress", "testing", "devdone", "done", "backlog", "archive"
        ]
        
        for dir_name in directories:
            dir_path = self.planning_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _parse_task_file(self, file_path: Path) -> Optional[Task]:
        """Parse a task markdown file and extract metadata.
        
        Args:
            file_path: Path to the task file
            
        Returns:
            Task object or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from markdown
            metadata = {}
            lines = content.split('\n')
            
            # Look for metadata section
            in_metadata = False
            for line in lines:
                if line.strip() == "## Metadata":
                    in_metadata = True
                    continue
                elif in_metadata and line.startswith('## '):
                    break
                elif in_metadata and line.strip().startswith('- **'):
                    # Parse metadata line like "- **Status:** Todo"
                    if ':' in line:
                        key_part = line.split(':**')[0].replace('- **', '').strip()
                        value_part = line.split(':**')[1].strip() if ':**' in line else ''
                        
                        key = key_part.lower().replace(' ', '_')
                        metadata[key] = value_part
            
            # Extract title from first line
            title_line = lines[0] if lines else ''
            if title_line.startswith('# '):
                metadata['title'] = title_line[2:].strip()
            
            return Task(metadata, str(file_path))
            
        except Exception as e:
            logger.error(f"Error parsing task file {file_path}: {e}")
            return None
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get all tasks with the specified status.
        
        Args:
            status: Task status (todo, inprogress, done, etc.)
            
        Returns:
            List of Task objects
        """
        status_dir = self.planning_dir / status
        if not status_dir.exists():
            return []
        
        tasks = []
        for file_path in status_dir.glob("*.md"):
            task = self._parse_task_file(file_path)
            if task:
                tasks.append(task)
        
        return tasks
    
    def get_all_tasks(self) -> Dict[str, List[Task]]:
        """Get all tasks organized by status.
        
        Returns:
            Dictionary with status as key and list of tasks as value
        """
        statuses = ["todo", "inprogress", "testing", "devdone", "done", "backlog"]
        all_tasks = {}
        
        for status in statuses:
            all_tasks[status] = self.get_tasks_by_status(status)
        
        return all_tasks
    
    def move_task(self, task_file: str, from_status: str, to_status: str) -> bool:
        """Move a task from one status to another.
        
        Args:
            task_file: Name of the task file (without path)
            from_status: Current status directory
            to_status: Target status directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = self.planning_dir / from_status / task_file
            target_path = self.planning_dir / to_status / task_file
            
            if not source_path.exists():
                logger.error(f"Task file not found: {source_path}")
                return False
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(str(source_path), str(target_path))
            
            # Update the status in the file content
            self._update_task_status(target_path, to_status)
            
            logger.info(f"Moved task {task_file} from {from_status} to {to_status}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving task {task_file}: {e}")
            return False
    
    def _update_task_status(self, file_path: Path, new_status: str):
        """Update the status field in a task file.
        
        Args:
            file_path: Path to the task file
            new_status: New status to set
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('- **Status:**'):
                    lines[i] = f"- **Status:** {new_status.title()}"
                    break
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
                
        except Exception as e:
            logger.error(f"Error updating task status in {file_path}: {e}")
    
    def create_task_from_template(self, task_id: str, title: str, template_name: str = "task-template.md") -> bool:
        """Create a new task from a template.
        
        Args:
            task_id: Unique task identifier (e.g., TASK-001)
            title: Task title
            template_name: Name of the template file to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                logger.error(f"Template not found: {template_path}")
                return False
            
            # Read template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace placeholders
            current_date = datetime.now().strftime("%Y-%m-%d")
            task_content = template_content.replace("[TASK_ID]", task_id)
            task_content = task_content.replace("[TASK_TITLE]", title)
            task_content = task_content.replace("[CREATED_DATE]", current_date)
            
            # Create task file in todo directory
            task_filename = f"{task_id.lower()}-{title.lower().replace(' ', '-')}.md"
            task_path = self.planning_dir / "todo" / task_filename
            
            with open(task_path, 'w', encoding='utf-8') as f:
                f.write(task_content)
            
            logger.info(f"Created new task: {task_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating task from template: {e}")
            return False
    
    def get_task_summary(self) -> Dict[str, int]:
        """Get a summary of task counts by status.
        
        Returns:
            Dictionary with status as key and count as value
        """
        summary = {}
        statuses = ["todo", "inprogress", "testing", "devdone", "done", "backlog"]
        
        for status in statuses:
            tasks = self.get_tasks_by_status(status)
            summary[status] = len(tasks)
        
        return summary
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search for tasks containing the query string.
        
        Args:
            query: Search query
            
        Returns:
            List of matching Task objects
        """
        all_tasks = self.get_all_tasks()
        matching_tasks = []
        
        query_lower = query.lower()
        
        for status, tasks in all_tasks.items():
            for task in tasks:
                # Search in title and file content
                if query_lower in task.title.lower():
                    matching_tasks.append(task)
                    continue
                
                # Search in file content
                try:
                    with open(task.file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if query_lower in content:
                            matching_tasks.append(task)
                except Exception:
                    continue
        
        return matching_tasks 