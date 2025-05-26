"""
Project Planner Module

Provides high-level project planning functionality, integrating task management
and template generation for comprehensive project coordination.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

from .task_manager import TaskManager
from .project_templates import ProjectTemplates

logger = logging.getLogger("TaskHeroAI.ProjectManagement.ProjectPlanner")


class ProjectPlanner:
    """High-level project planning and coordination."""

    def __init__(self, project_root: Optional[str] = None, task_manager: Optional[TaskManager] = None):
        """Initialize ProjectPlanner.

        Args:
            project_root: Root directory for project management. Defaults to current working directory.
            task_manager: Optional TaskManager instance. If None, creates a new one with configurable paths.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.task_manager = task_manager if task_manager else TaskManager(project_root)
        self.templates = ProjectTemplates(project_root)
        self.settings_path = self.project_root / "mods" / "project_management" / "settings.json"
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Load project management settings."""
        if not self.settings_path.exists():
            return self._create_default_settings()

        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return self._create_default_settings()

    def _create_default_settings(self) -> Dict[str, Any]:
        """Create default settings."""
        default_settings = {
            "project_name": "TaskHeroAI Project",
            "default_task_template": "task-template.md",
            "task_id_prefix": "TASK",
            "task_id_counter": 1,
            "statuses": {
                "todo": "To Do",
                "inprogress": "In Progress",
                "testing": "Testing",
                "devdone": "Development Done",
                "done": "Done",
                "backlog": "Backlog"
            },
            "priorities": ["low", "medium", "high", "critical"],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }

        try:
            # Ensure directory exists
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)

            # Save default settings
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving default settings: {e}")

        return default_settings

    def _save_settings(self):
        """Save current settings to file."""
        try:
            self.settings["modified"] = datetime.now().isoformat()
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def get_project_dashboard(self) -> Dict[str, Any]:
        """Get a comprehensive project dashboard view.

        Returns:
            Dictionary with project overview information
        """
        task_summary = self.task_manager.get_task_summary()
        all_tasks = self.task_manager.get_all_tasks()

        # Calculate progress
        total_tasks = sum(task_summary.values())
        completed_tasks = task_summary.get('done', 0)
        progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Get recent activity (tasks modified recently)
        recent_activity = []
        for status, tasks in all_tasks.items():
            for task in tasks:
                # You could add last modified tracking to tasks for more accurate recent activity
                recent_activity.append({
                    'task': task.title,
                    'status': status,
                    'file': Path(task.file_path).name
                })

        # Get upcoming deadlines (if due dates are set)
        upcoming_deadlines = []
        for status, tasks in all_tasks.items():
            if status == 'done':  # Skip completed tasks
                continue
            for task in tasks:
                if task.due_date:
                    upcoming_deadlines.append({
                        'task': task.title,
                        'due_date': task.due_date,
                        'status': status,
                        'priority': task.priority
                    })

        # Sort by due date
        upcoming_deadlines.sort(key=lambda x: x['due_date'])

        return {
            'project_name': self.settings.get('project_name', 'Unknown Project'),
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress_percentage': round(progress_percentage, 1),
            'task_summary': task_summary,
            'recent_activity': recent_activity[:10],  # Last 10 activities
            'upcoming_deadlines': upcoming_deadlines[:5],  # Next 5 deadlines
            'available_templates': self.templates.get_available_templates(),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def create_new_task(self, title: str,
                       priority: str = "medium",
                       due_date: Optional[str] = None,
                       template_name: Optional[str] = None,
                       assigned_to: str = "Developer",
                       task_type: str = "Development",
                       tags: str = "",
                       sequence: Optional[int] = None,
                       content: Optional[str] = None,
                       dependencies: Optional[str] = None,
                       effort_estimate: Optional[str] = None) -> Tuple[bool, str]:
        """Create a new task with auto-generated ID and enhanced metadata.

        Args:
            title: Task title
            priority: Task priority (low, medium, high, critical)
            due_date: Optional due date (YYYY-MM-DD format)
            template_name: Optional template to use (defaults to settings)
            assigned_to: Who the task is assigned to
            task_type: Type of task (Development, Test Case, etc.)
            tags: Comma-separated tags
            sequence: Optional sequence number
            content: Optional task content (overrides template content)
            dependencies: Optional comma-separated task dependencies
            effort_estimate: Optional effort estimate

        Returns:
            Tuple of (success, task_id or error_message)
        """
        # Generate task ID
        task_id = f"{self.settings['task_id_prefix']}-{self.settings['task_id_counter']:03d}"

        # Use sequence number if not provided
        if sequence is None:
            sequence = self.settings['task_id_counter']

        # Use default template if none specified
        if not template_name:
            template_name = self.settings.get('default_task_template', 'task-template.md')

        # Prepare additional keyword arguments
        kwargs = {
            'task_id': task_id,
            'priority': priority,
            'due_date': due_date,
            'assigned_to': assigned_to,
            'task_type': task_type,
            'tags': tags,
            'sequence': sequence
        }

        # Add optional fields if provided
        if dependencies:
            kwargs['dependencies'] = dependencies
        if effort_estimate:
            kwargs['effort_estimate'] = effort_estimate

        # Create task from template with enhanced metadata
        task = self.task_manager.create_task_from_template(
            title=title,
            template_name=template_name,
            **kwargs
        )

        if task and content:
            # If custom content is provided, update the task content
            try:
                task.content = content

                # Save the updated task with custom content
                file_path = Path(task.file_path)
                if file_path.exists():
                    # Read current template content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        current_content = f.read()

                    # Replace the overview section with custom content
                    if "## Overview" in current_content:
                        parts = current_content.split("## Overview")
                        if len(parts) > 1:
                            # Find the next section
                            next_section_pos = parts[1].find("\n## ")
                            if next_section_pos > 0:
                                # Replace overview content
                                updated_content = (
                                    parts[0] +
                                    "## Overview\n" +
                                    content + "\n\n" +
                                    "## " + parts[1][next_section_pos+4:]
                                )
                            else:
                                # No next section, append to end
                                updated_content = (
                                    parts[0] +
                                    "## Overview\n" +
                                    content
                                )

                            # Write updated content
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(updated_content)

                            logger.info(f"Updated task {task_id} with custom content")

            except Exception as e:
                logger.warning(f"Error updating task content: {e}")
                # Task was created successfully, just couldn't update content

        if task:
            # Increment counter and save settings
            self.settings['task_id_counter'] += 1
            self._save_settings()

            return True, task_id
        else:
            return False, f"Failed to create task from template {template_name}"

    def move_task_to_status(self, task_file: str, new_status: str) -> bool:
        """Move a task to a different status.

        Args:
            task_file: Name of the task file
            new_status: Target status

        Returns:
            True if successful
        """
        # Find current status by looking in all directories
        current_status = None
        all_tasks = self.task_manager.get_all_tasks()

        for status, tasks in all_tasks.items():
            for task in tasks:
                if Path(task.file_path).name == task_file:
                    current_status = status
                    break
            if current_status:
                break

        if not current_status:
            logger.error(f"Task file not found: {task_file}")
            return False

        if current_status == new_status:
            logger.info(f"Task {task_file} is already in status {new_status}")
            return True

        return self.task_manager.move_task(task_file, current_status, new_status)

    def get_task_workflow_suggestions(self, current_status: str) -> List[str]:
        """Get suggested next statuses for a task workflow.

        Args:
            current_status: Current task status

        Returns:
            List of suggested next statuses
        """
        workflow_map = {
            'backlog': ['todo'],
            'todo': ['inprogress', 'backlog'],
            'inprogress': ['testing', 'devdone', 'todo'],
            'testing': ['done', 'inprogress'],
            'devdone': ['done', 'testing'],
            'done': ['archive']
        }

        return workflow_map.get(current_status, [])

    def generate_project_report(self, include_details: bool = False) -> str:
        """Generate a comprehensive project report.

        Args:
            include_details: Whether to include detailed task information

        Returns:
            Formatted project report as string
        """
        dashboard = self.get_project_dashboard()

        report = f"# {dashboard['project_name']} - Project Report\n\n"
        report += f"**Generated:** {dashboard['last_updated']}\n\n"

        # Overview
        report += "## Project Overview\n\n"
        report += f"- **Total Tasks:** {dashboard['total_tasks']}\n"
        report += f"- **Completed Tasks:** {dashboard['completed_tasks']}\n"
        report += f"- **Progress:** {dashboard['progress_percentage']}%\n\n"

        # Task Summary
        report += "## Task Summary by Status\n\n"
        for status, count in dashboard['task_summary'].items():
            status_name = self.settings['statuses'].get(status, status.title())
            report += f"- **{status_name}:** {count}\n"
        report += "\n"

        # Upcoming Deadlines
        if dashboard['upcoming_deadlines']:
            report += "## Upcoming Deadlines\n\n"
            for deadline in dashboard['upcoming_deadlines']:
                report += f"- **{deadline['task']}** ({deadline['priority']}) - Due: {deadline['due_date']}\n"
            report += "\n"

        # Detailed task information
        if include_details:
            report += "## Detailed Task Information\n\n"
            all_tasks = self.task_manager.get_all_tasks()

            for status, tasks in all_tasks.items():
                if not tasks:
                    continue

                status_name = self.settings['statuses'].get(status, status.title())
                report += f"### {status_name}\n\n"

                for task in tasks:
                    report += f"- **{task.title}**\n"
                    if task.priority and task.priority != 'medium':
                        report += f"  - Priority: {task.priority}\n"
                    if task.due_date:
                        report += f"  - Due: {task.due_date}\n"
                    if task.created_date:
                        report += f"  - Created: {task.created_date}\n"
                    report += f"  - File: {Path(task.file_path).name}\n"
                    report += "\n"

        return report

    def archive_completed_tasks(self) -> int:
        """Archive all completed tasks to the archive directory.

        Returns:
            Number of tasks archived
        """
        done_tasks = self.task_manager.get_tasks_by_status('done')
        archived_count = 0

        for task in done_tasks:
            task_file = Path(task.file_path).name
            success = self.task_manager.move_task(task_file, 'done', 'archive')
            if success:
                archived_count += 1

        return archived_count

    def bulk_status_update(self, task_files: List[str], new_status: str) -> Dict[str, bool]:
        """Update status for multiple tasks.

        Args:
            task_files: List of task file names
            new_status: Target status for all tasks

        Returns:
            Dictionary mapping task file to success status
        """
        results = {}

        for task_file in task_files:
            results[task_file] = self.move_task_to_status(task_file, new_status)

        return results