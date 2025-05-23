"""
Task Manager Module - Enhanced Core Implementation

Handles comprehensive task management functionality with full CRUD operations,
status workflow management, and AI integration preparation.
Provides functionality for managing tasks across different states: backlog, todo, inprogress, devdone, testing, done.
"""

import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import re

logger = logging.getLogger("TaskHeroAI.ProjectManagement.TaskManager")


class TaskStatus(Enum):
    """Enum for valid task statuses with workflow transitions."""
    BACKLOG = "backlog"
    TODO = "todo"
    INPROGRESS = "inprogress"
    DEVDONE = "devdone"
    TESTING = "testing"
    DONE = "done"
    ARCHIVE = "archive"

    @classmethod
    def get_valid_transitions(cls, current_status: 'TaskStatus') -> List['TaskStatus']:
        """Get valid status transitions from current status."""
        transitions = {
            cls.BACKLOG: [cls.TODO, cls.ARCHIVE],
            cls.TODO: [cls.INPROGRESS, cls.BACKLOG, cls.ARCHIVE],
            cls.INPROGRESS: [cls.DEVDONE, cls.TODO, cls.ARCHIVE],
            cls.DEVDONE: [cls.TESTING, cls.INPROGRESS, cls.ARCHIVE],
            cls.TESTING: [cls.DONE, cls.DEVDONE, cls.ARCHIVE],
            cls.DONE: [cls.ARCHIVE],
            cls.ARCHIVE: [cls.BACKLOG, cls.TODO]  # Can be reactivated
        }
        return transitions.get(current_status, [])

    @classmethod
    def from_string(cls, status_str: str) -> 'TaskStatus':
        """Create TaskStatus from string, case-insensitive."""
        status_str = status_str.lower().strip()
        for status in cls:
            if status.value == status_str:
                return status
        raise ValueError(f"Invalid status: {status_str}")


class TaskPriority(Enum):
    """Enum for task priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_string(cls, priority_str: str) -> 'TaskPriority':
        """Create TaskPriority from string, case-insensitive."""
        priority_str = priority_str.lower().strip()
        for priority in cls:
            if priority.value == priority_str:
                return priority
        return cls.MEDIUM  # Default to medium if invalid


@dataclass
class TaskMetadata:
    """Enhanced task metadata with comprehensive fields."""
    task_id: str
    title: str
    status: TaskStatus
    priority: TaskPriority
    created_date: str
    due_date: Optional[str] = None
    assigned_to: str = "Developer"
    task_type: str = "Development"
    sequence: Optional[int] = None
    tags: List[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    completion_percentage: int = 0
    dependencies: Optional[str] = None
    effort_estimate: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.tags is None:
            self.tags = []
        if not self.created_date:
            self.created_date = datetime.now().strftime("%Y-%m-%d")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskMetadata':
        """Create TaskMetadata from dictionary with robust field mapping."""
        # Create a normalized data dictionary
        normalized_data = {}
        
        # Handle different field name variations
        field_mappings = {
            'task_id': ['task_id', 'id'],
            'title': ['title', 'name'],
            'status': ['status'],
            'priority': ['priority'],
            'created_date': ['created_date', 'created'],
            'due_date': ['due_date', 'due'],
            'assigned_to': ['assigned_to', 'assignee', 'assigned'],
            'task_type': ['task_type', 'type'],
            'sequence': ['sequence'],
            'tags': ['tags'],
            'estimated_hours': ['estimated_hours'],
            'actual_hours': ['actual_hours'],
            'completion_percentage': ['completion_percentage'],
            'dependencies': ['dependencies'],
            'effort_estimate': ['effort_estimate']
        }
        
        # Map fields from data to normalized names
        for target_field, source_fields in field_mappings.items():
            for source_field in source_fields:
                if source_field in data and data[source_field]:
                    normalized_data[target_field] = data[source_field]
                    break
        
        # Set required defaults
        if 'task_id' not in normalized_data:
            normalized_data['task_id'] = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        if 'title' not in normalized_data:
            normalized_data['title'] = "Untitled Task"
        if 'created_date' not in normalized_data:
            normalized_data['created_date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Convert enum fields with error handling
        if 'status' in normalized_data:
            try:
                # Handle various status formats and invalid values
                status_str = str(normalized_data['status']).lower().strip()
                # Clean up common status variations
                status_mappings = {
                    'todo': 'todo',
                    'to do': 'todo',
                    'pending': 'todo',
                    'inprogress': 'inprogress',
                    'in progress': 'inprogress',
                    'in-progress': 'inprogress',
                    'development': 'inprogress',
                    'devdone': 'devdone',
                    'dev done': 'devdone',
                    'dev-done': 'devdone',
                    'testing': 'testing',
                    'test': 'testing',
                    'done': 'done',
                    'complete': 'done',
                    'completed': 'done',
                    'finished': 'done',
                    'backlog': 'backlog',
                    'archive': 'archive'
                }
                
                # Try direct mapping first
                if status_str in status_mappings:
                    normalized_data['status'] = TaskStatus.from_string(status_mappings[status_str])
                else:
                    # If not found, try to extract a valid status from the string
                    for key, value in status_mappings.items():
                        if key in status_str:
                            normalized_data['status'] = TaskStatus.from_string(value)
                            break
                    else:
                        # Default to TODO if no valid status found
                        normalized_data['status'] = TaskStatus.TODO
            except ValueError:
                normalized_data['status'] = TaskStatus.TODO
        else:
            normalized_data['status'] = TaskStatus.TODO
        
        if 'priority' in normalized_data:
            try:
                normalized_data['priority'] = TaskPriority.from_string(str(normalized_data['priority']))
            except ValueError:
                normalized_data['priority'] = TaskPriority.MEDIUM
        else:
            normalized_data['priority'] = TaskPriority.MEDIUM
        
        # Handle tags as list
        if 'tags' in normalized_data:
            if isinstance(normalized_data['tags'], str):
                # Split by comma, semicolon, or space
                tags_str = normalized_data['tags']
                tags = []
                for delimiter in [',', ';', ' ']:
                    if delimiter in tags_str:
                        tags = [tag.strip() for tag in tags_str.split(delimiter) if tag.strip()]
                        break
                else:
                    # Single tag
                    tags = [tags_str.strip()] if tags_str.strip() else []
                normalized_data['tags'] = tags
            elif not isinstance(normalized_data['tags'], list):
                normalized_data['tags'] = []
        else:
            normalized_data['tags'] = []
        
        # Handle numeric fields
        for field in ['estimated_hours', 'actual_hours', 'completion_percentage', 'sequence']:
            if field in normalized_data:
                try:
                    if field == 'completion_percentage':
                        normalized_data[field] = int(float(normalized_data[field]))
                    elif field == 'sequence':
                        normalized_data[field] = int(normalized_data[field])
                    else:
                        normalized_data[field] = float(normalized_data[field])
                except (ValueError, TypeError):
                    if field == 'completion_percentage':
                        normalized_data[field] = 0
                    else:
                        normalized_data[field] = None
        
        # Create the TaskMetadata object with only the fields it expects
        valid_fields = {
            'task_id', 'title', 'status', 'priority', 'created_date', 
            'due_date', 'assigned_to', 'task_type', 'sequence', 'tags',
            'estimated_hours', 'actual_hours', 'completion_percentage',
            'dependencies', 'effort_estimate'
        }
        
        final_data = {k: v for k, v in normalized_data.items() if k in valid_fields and v is not None}
        
        return cls(**final_data)


class Task:
    """Enhanced Task class with comprehensive functionality."""
    
    def __init__(self, metadata: TaskMetadata, content: str = "", file_path: Optional[str] = None):
        """Initialize Task.
        
        Args:
            metadata: Task metadata
            content: Task content (markdown body)
            file_path: Path to the task file
        """
        self.metadata = metadata
        self.content = content
        self.file_path = file_path
        self._original_status = metadata.status  # Track for validation
        
    @property
    def title(self) -> str:
        return self.metadata.title
    
    @property
    def status(self) -> TaskStatus:
        return self.metadata.status
    
    @property
    def priority(self) -> TaskPriority:
        return self.metadata.priority
    
    @property
    def task_id(self) -> str:
        return self.metadata.task_id
    
    @property
    def due_date(self) -> Optional[str]:
        return self.metadata.due_date
    
    @property
    def created_date(self) -> str:
        return self.metadata.created_date
    
    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """Check if task can transition to new status."""
        valid_transitions = TaskStatus.get_valid_transitions(self.status)
        return new_status in valid_transitions
    
    def update_status(self, new_status: TaskStatus, validate: bool = True) -> bool:
        """Update task status with optional validation.
        
        Args:
            new_status: New status to set
            validate: Whether to validate the transition
            
        Returns:
            True if successful, False if invalid transition
        """
        if validate and not self.can_transition_to(new_status):
            logger.warning(f"Invalid status transition from {self.status.value} to {new_status.value}")
            return False
        
        self.metadata.status = new_status
        return True
    
    def to_markdown(self) -> str:
        """Convert task to markdown format."""
        # Generate metadata section
        metadata_lines = [
            f"# Task: {self.metadata.task_id} - {self.metadata.title}",
            "",
            "## Metadata",
            f"- **Created:** {self.metadata.created_date}",
        ]
        
        if self.metadata.due_date:
            metadata_lines.append(f"- **Due:** {self.metadata.due_date}")
        
        metadata_lines.extend([
            f"- **Priority:** {self.metadata.priority.value.title()}",
            f"- **Status:** {self.metadata.status.value.title()}",
            f"- **Assigned to:** {self.metadata.assigned_to}",
            f"- **Task Type:** {self.metadata.task_type}",
        ])
        
        if self.metadata.sequence:
            metadata_lines.append(f"- **Sequence:** {self.metadata.sequence}")
        
        if self.metadata.tags:
            tags_str = ", ".join(self.metadata.tags)
            metadata_lines.append(f"- **Tags:** {tags_str}")
        
        if self.metadata.dependencies:
            metadata_lines.append(f"- **Dependencies:** {self.metadata.dependencies}")
        
        if self.metadata.effort_estimate:
            metadata_lines.append(f"- **Effort Estimate:** {self.metadata.effort_estimate}")
        
        metadata_lines.extend([
            "",
            "## Overview",
            self.content if self.content else "[Task content will be generated here]",
            "",
        ])
        
        # Add time tracking section
        if self.metadata.estimated_hours or self.metadata.actual_hours:
            metadata_lines.extend([
                "## Time Tracking",
                f"- **Estimated hours:** {self.metadata.estimated_hours or 'TBD'}",
                f"- **Actual hours:** {self.metadata.actual_hours or 'TBD'}",
                "",
            ])
        
        return "\n".join(metadata_lines)
    
    @classmethod
    def from_markdown(cls, content: str, file_path: Optional[str] = None) -> 'Task':
        """Create Task from markdown content with robust parsing.
        
        Args:
            content: Markdown content
            file_path: Path to the source file
            
        Returns:
            Task object
        """
        lines = content.split('\n')
        metadata_dict = {}
        task_content = ""
        
        # Parse title from various formats
        title_line = lines[0] if lines else ''
        if title_line.startswith('# Task: '):
            task_info = title_line[8:].strip()  # Remove "# Task: "
            if ' - ' in task_info:
                task_id, title = task_info.split(' - ', 1)
                metadata_dict['task_id'] = task_id.strip()
                metadata_dict['title'] = title.strip()
            else:
                metadata_dict['task_id'] = task_info
                metadata_dict['title'] = task_info
        elif title_line.startswith('# '):
            # Simple markdown title
            title = title_line[2:].strip()
            metadata_dict['title'] = title
            # Try to extract task ID from title
            task_id_match = re.search(r'(TASK-\d+)', title)
            if task_id_match:
                metadata_dict['task_id'] = task_id_match.group(1)
        
        # Parse metadata section
        in_metadata = False
        content_start_idx = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            if line_stripped == "## Metadata":
                in_metadata = True
                continue
            elif in_metadata and line.startswith('## '):
                in_metadata = False
                content_start_idx = i
                break
            elif in_metadata and line_stripped.startswith('- **'):
                # Parse metadata line like "- **Status:** Todo" or "- **Created:** 2025-01-27"
                if ':**' in line:
                    key_part = line.split(':**')[0].replace('- **', '').strip()
                    value_part = line.split(':**')[1].strip()
                    
                    # Normalize key names
                    key = key_part.lower().replace(' ', '_')
                    
                    # Handle common key variations
                    key_mappings = {
                        'status': 'status',
                        'priority': 'priority',
                        'created': 'created_date',
                        'created_date': 'created_date',
                        'due': 'due_date',
                        'due_date': 'due_date',
                        'assigned_to': 'assigned_to',
                        'assignee': 'assigned_to',
                        'assigned': 'assigned_to',
                        'task_type': 'task_type',
                        'type': 'task_type',
                        'sequence': 'sequence',
                        'tags': 'tags',
                        'estimated_hours': 'estimated_hours',
                        'actual_hours': 'actual_hours',
                        'dependencies': 'dependencies',
                        'effort_estimate': 'effort_estimate'
                    }
                    
                    mapped_key = key_mappings.get(key, key)
                    metadata_dict[mapped_key] = value_part
        
        # Extract content (everything after metadata)
        if content_start_idx > 0:
            content_lines = lines[content_start_idx:]
            # Skip empty lines at the beginning
            while content_lines and not content_lines[0].strip():
                content_lines.pop(0)
            task_content = '\n'.join(content_lines).strip()
        else:
            # If no metadata section found, use everything after title as content
            if len(lines) > 1:
                task_content = '\n'.join(lines[1:]).strip()
        
        # Create metadata object with robust error handling
        try:
            metadata = TaskMetadata.from_dict(metadata_dict)
        except Exception as e:
            logger.warning(f"Error parsing task metadata from {file_path}: {e}")
            # Create minimal metadata with defaults
            metadata = TaskMetadata(
                task_id=metadata_dict.get('task_id', f"TASK-{uuid.uuid4().hex[:8].upper()}"),
                title=metadata_dict.get('title', 'Untitled Task'),
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                created_date=datetime.now().strftime("%Y-%m-%d")
            )
        
        return cls(metadata, task_content, file_path)


class TaskManager:
    """Enhanced TaskManager with comprehensive CRUD operations and workflow management."""
    
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
        for status in TaskStatus:
            dir_path = self.planning_dir / status.value
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _get_task_file_path(self, task_id: str, status: TaskStatus, title: str = "") -> Path:
        """Get the file path for a task."""
        # Create filename from task_id and title if available
        if title:
            # Sanitize title for filename
            sanitized_title = re.sub(r'[^\w\s-]', '', title.lower())
            sanitized_title = re.sub(r'[-\s]+', '-', sanitized_title).strip('-')
            # Limit length to keep filename reasonable
            if len(sanitized_title) > 40:
                sanitized_title = sanitized_title[:40].rstrip('-')
            filename = f"{task_id.lower()}-{sanitized_title}.md"
        else:
            filename = f"{task_id.lower()}.md"
        return self.planning_dir / status.value / filename
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        # Get existing task IDs to determine next sequence number
        all_tasks = self.get_all_tasks()
        max_sequence = 0
        
        for status_tasks in all_tasks.values():
            for task in status_tasks:
                # Extract sequence number from task ID (e.g., TASK-001 -> 1)
                match = re.search(r'TASK-(\d+)', task.task_id)
                if match:
                    sequence = int(match.group(1))
                    max_sequence = max(max_sequence, sequence)
        
        # Generate next task ID
        next_sequence = max_sequence + 1
        return f"TASK-{next_sequence:03d}"
    
    # CREATE Operations
    def create_task(self, title: str, content: str = "", priority: TaskPriority = TaskPriority.MEDIUM,
                   status: TaskStatus = TaskStatus.TODO, **kwargs) -> Optional[Task]:
        """Create a new task.
        
        Args:
            title: Task title
            content: Task content
            priority: Task priority
            status: Initial task status
            **kwargs: Additional metadata fields
            
        Returns:
            Created Task object or None if failed
        """
        try:
            # Generate task ID
            task_id = kwargs.get('task_id', self._generate_task_id())
            
            # Create metadata
            metadata = TaskMetadata(
                task_id=task_id,
                title=title,
                status=status,
                priority=priority,
                created_date=datetime.now().strftime("%Y-%m-%d"),
                **kwargs
            )
            
            # Create task object
            task = Task(metadata, content)
            
            # Save to file
            if self.save_task(task):
                logger.info(f"Created new task: {task_id} - {title}")
                return task
            else:
                logger.error(f"Failed to save new task: {task_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def create_task_from_template(self, title: str, template_name: str = "task-template.md", 
                                 **kwargs) -> Optional[Task]:
        """Create a new task from a template.
        
        Args:
            title: Task title
            template_name: Name of the template file to use
            **kwargs: Additional metadata fields
            
        Returns:
            Created Task object or None if failed
        """
        try:
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                logger.error(f"Template not found: {template_path}")
                return None
            
            # Read template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Generate task ID
            task_id = kwargs.get('task_id', self._generate_task_id())
            
            # Replace placeholders in template
            replacements = {
                '[TASK_ID]': task_id,
                'TASK-ID': task_id,
                '[TASK_TITLE]': title,
                'TASK-TITLE': title,
                '[CREATED_DATE]': datetime.now().strftime("%Y-%m-%d"),
                'PRIORITY': kwargs.get('priority', 'Medium'),
                'DUE-DATE': kwargs.get('due_date', ''),
                'STATUS': kwargs.get('status', 'Todo'),
                'ASSIGNEE': kwargs.get('assigned_to', 'Developer'),
                'TASK-TYPE': kwargs.get('task_type', 'Development'),
                'SEQUENCE': str(kwargs.get('sequence', '')),
                'TAGS': kwargs.get('tags', ''),
                'DEPENDENCIES': kwargs.get('dependencies', ''),
                'EFFORT-ESTIMATE': kwargs.get('effort_estimate', 'TBD'),
                '[DEPENDENCIES]': kwargs.get('dependencies', ''),
                '[EFFORT_ESTIMATE]': kwargs.get('effort_estimate', 'TBD'),
            }
            
            task_content = template_content
            for placeholder, value in replacements.items():
                task_content = task_content.replace(placeholder, str(value))
            
            # Create task from processed template
            task = Task.from_markdown(task_content)
            
            # Override task metadata with passed parameters to ensure consistency
            task.metadata.task_id = task_id
            task.metadata.title = title
            if 'priority' in kwargs:
                try:
                    task.metadata.priority = TaskPriority.from_string(kwargs['priority'])
                except ValueError:
                    pass  # Keep existing priority
            if 'due_date' in kwargs and kwargs['due_date']:
                task.metadata.due_date = kwargs['due_date']
            
            # Save to file with title in filename
            file_path = self._get_task_file_path(task_id, task.status, title)
            task.file_path = str(file_path)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write markdown content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(task.to_markdown())
            
            logger.info(f"Created task from template: {task_id} - {title}")
            return task
                
        except Exception as e:
            logger.error(f"Error creating task from template: {e}")
            return None
    
    # READ Operations
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID.
        
        Args:
            task_id: Task ID to search for
            
        Returns:
            Task object or None if not found
        """
        all_tasks = self.get_all_tasks()
        for status_tasks in all_tasks.values():
            for task in status_tasks:
                if task.task_id == task_id:
                    return task
        return None
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with the specified status.
        
        Args:
            status: Task status
            
        Returns:
            List of Task objects
        """
        status_dir = self.planning_dir / status.value
        if not status_dir.exists():
            return []
        
        tasks = []
        for file_path in status_dir.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                task = Task.from_markdown(content, str(file_path))
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error parsing task file {file_path}: {e}")
                continue
        
        return tasks
    
    def get_all_tasks(self) -> Dict[str, List[Task]]:
        """Get all tasks organized by status.
        
        Returns:
            Dictionary with status as key and list of tasks as value
        """
        all_tasks = {}
        
        for status in TaskStatus:
            all_tasks[status.value] = self.get_tasks_by_status(status)
        
        return all_tasks
    
    # UPDATE Operations
    def save_task(self, task: Task) -> bool:
        """Save a task to file.
        
        Args:
            task: Task to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_task_file_path(task.task_id, task.status, task.title)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write markdown content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(task.to_markdown())
            
            # Update task's file path
            task.file_path = str(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving task {task.task_id}: {e}")
            return False
    
    def update_task(self, task: Task) -> bool:
        """Update an existing task.
        
        Args:
            task: Task with updated information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # If status changed, we might need to move the file
            old_file_path = Path(task.file_path) if task.file_path else None
            new_file_path = self._get_task_file_path(task.task_id, task.status, task.title)
            
            # Save to new location
            if self.save_task(task):
                # Remove old file if location changed
                if old_file_path and old_file_path != new_file_path and old_file_path.exists():
                    old_file_path.unlink()
                
                logger.info(f"Updated task: {task.task_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error updating task {task.task_id}: {e}")
            return False
    
    def move_task_status(self, task_id: str, new_status: TaskStatus, validate: bool = True) -> bool:
        """Move a task to a new status.
        
        Args:
            task_id: Task ID to move
            new_status: New status
            validate: Whether to validate the transition
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the task
            task = self.get_task_by_id(task_id)
            if not task:
                logger.error(f"Task not found: {task_id}")
                return False
            
            old_status = task.status
            
            # Check if transition is valid
            if validate and not task.can_transition_to(new_status):
                logger.error(f"Invalid status transition for {task_id}: {old_status.value} -> {new_status.value}")
                return False
            
            # Remove old file if it exists
            old_file_path = Path(task.file_path) if task.file_path else None
            if old_file_path and old_file_path.exists():
                old_file_path.unlink()
            
            # Update status
            task.update_status(new_status, validate=False)  # Already validated above
            
            # Save to new location
            if self.save_task(task):
                logger.info(f"Moved task {task_id} from {old_status.value} to {new_status.value}")
                return True
            else:
                # Revert status change if save failed
                task.update_status(old_status, validate=False)
                logger.error(f"Failed to save task {task_id} after status change")
                return False
                
        except Exception as e:
            logger.error(f"Error moving task {task_id}: {e}")
            return False
    
    # DELETE Operations
    def delete_task(self, task_id: str) -> bool:
        """Delete a task.
        
        Args:
            task_id: Task ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            task = self.get_task_by_id(task_id)
            if not task:
                logger.error(f"Task not found: {task_id}")
                return False
            
            if task.file_path and Path(task.file_path).exists():
                Path(task.file_path).unlink()
                logger.info(f"Deleted task: {task_id}")
                return True
            else:
                logger.error(f"Task file not found: {task.file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False
    
    # UTILITY Operations
    def get_task_summary(self) -> Dict[str, int]:
        """Get a summary of task counts by status.
        
        Returns:
            Dictionary with status as key and count as value
        """
        summary = {}
        
        for status in TaskStatus:
            tasks = self.get_tasks_by_status(status)
            summary[status.value] = len(tasks)
        
        return summary
    
    def search_tasks(self, query: str, search_content: bool = True) -> List[Task]:
        """Search for tasks containing the query string.
        
        Args:
            query: Search query
            search_content: Whether to search in task content
            
        Returns:
            List of matching Task objects
        """
        all_tasks = self.get_all_tasks()
        matching_tasks = []
        
        query_lower = query.lower()
        
        for status, tasks in all_tasks.items():
            for task in tasks:
                # Search in title, task ID, and tags
                if (query_lower in task.title.lower() or 
                    query_lower in task.task_id.lower() or
                    any(query_lower in tag.lower() for tag in task.metadata.tags)):
                    matching_tasks.append(task)
                    continue
                
                # Search in content if requested
                if search_content and query_lower in task.content.lower():
                    matching_tasks.append(task)
                    continue
        
        return matching_tasks
    
    def get_valid_transitions(self, task_id: str) -> List[TaskStatus]:
        """Get valid status transitions for a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            List of valid status transitions
        """
        task = self.get_task_by_id(task_id)
        if task:
            return TaskStatus.get_valid_transitions(task.status)
        return []
    
    def validate_task_data(self, task_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate task data structure.
        
        Args:
            task_data: Task data dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['task_id', 'title']
        for field in required_fields:
            if field not in task_data or not task_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate status
        if 'status' in task_data:
            try:
                TaskStatus.from_string(task_data['status'])
            except ValueError:
                errors.append(f"Invalid status: {task_data['status']}")
        
        # Validate priority
        if 'priority' in task_data:
            try:
                TaskPriority.from_string(task_data['priority'])
            except ValueError:
                errors.append(f"Invalid priority: {task_data['priority']}")
        
        # Validate dates
        date_fields = ['created_date', 'due_date']
        for field in date_fields:
            if field in task_data and task_data[field]:
                try:
                    datetime.strptime(task_data[field], "%Y-%m-%d")
                except ValueError:
                    errors.append(f"Invalid date format for {field}: {task_data[field]} (expected YYYY-MM-DD)")
        
        return len(errors) == 0, errors


# Legacy compatibility wrapper for existing Task class usage
# ... existing code ... 