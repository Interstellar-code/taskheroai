"""
TaskCLI Module - Enhanced CLI Interface for Task Management

Provides quick task creation, interactive dashboard, and enhanced CLI features.
Part of TASK-005 Enhanced CLI Integration implementation.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from colorama import Fore, Style

from ..project_management.task_manager import TaskManager, TaskStatus, TaskPriority, Task


class TaskCLI:
    """Enhanced CLI interface for task management."""

    def __init__(self, settings_manager=None):
        """Initialize TaskCLI with settings integration."""
        self.settings_manager = settings_manager

        # Initialize TaskManager
        self.task_manager = TaskManager()

        # CLI configuration
        self.page_size = 10
        self.auto_refresh = True

        # Status styling
        self.status_styles = {
            'backlog': ('📦', 'bright_black'),
            'todo': ('📝', 'yellow'),
            'inprogress': ('🔄', 'blue'),
            'devdone': ('✅', 'cyan'),
            'testing': ('🧪', 'magenta'),
            'done': ('🎉', 'green'),
            'archive': ('🗃️', 'dim')
        }

        # Priority styling
        self.priority_styles = {
            'critical': ('🔥', 'bold red'),
            'high': ('🔴', 'red'),
            'medium': ('🟡', 'yellow'),
            'low': ('🟢', 'green')
        }

    def quick_create(self, title: str = None, **kwargs) -> Optional[Task]:
        """Quick task creation with smart defaults and parsing."""
        if not title:
            print(f"\n{Fore.CYAN}🚀 Quick Task Creation{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")

            # Get title with smart parsing
            title = input(f"{Fore.GREEN}Task title: {Style.RESET_ALL}").strip()
            if not title:
                print(f"{Fore.YELLOW}Task creation cancelled.{Style.RESET_ALL}")
                return None

        # Parse inline attributes from title
        parsed_attrs = self._parse_task_attributes(title)

        # Merge with provided kwargs
        task_attrs = {**parsed_attrs, **kwargs}

        # Smart defaults
        if 'priority' not in task_attrs:
            task_attrs['priority'] = TaskPriority.MEDIUM
        if 'status' not in task_attrs:
            task_attrs['status'] = TaskStatus.TODO

        # Interactive enhancement if not provided
        if not kwargs:  # Only ask if called interactively
            task_attrs = self._enhance_task_interactively(task_attrs)

        try:
            # Create the task
            task = self.task_manager.create_task(
                title=task_attrs['title'],
                content=task_attrs.get('description', ''),
                priority=task_attrs['priority'],
                status=task_attrs['status'],
                assigned_to=task_attrs.get('assigned_to', 'Developer'),
                due_date=task_attrs.get('due_date'),
                tags=task_attrs.get('tags', [])
            )

            if task:
                print(f"\n{Fore.GREEN}✅ Task created successfully!{Style.RESET_ALL}")
                print(f"   ID: {Fore.CYAN}{task.task_id}{Style.RESET_ALL}")
                print(f"   Title: {task.title}")
                print(f"   Priority: {self._format_priority(task.priority)}")
                print(f"   Status: {self._format_status(task.status)}")
                return task
            else:
                print(f"{Fore.RED}❌ Failed to create task.{Style.RESET_ALL}")
                return None

        except Exception as e:
            print(f"{Fore.RED}❌ Error creating task: {e}{Style.RESET_ALL}")
            return None

    def _parse_task_attributes(self, title: str) -> Dict[str, Any]:
        """Parse inline attributes from task title."""
        import re

        result = {'title': title}

        # Extract priority
        priority_match = re.search(r'--priority\s+(\w+)', title, re.IGNORECASE)
        if priority_match:
            try:
                result['priority'] = TaskPriority.from_string(priority_match.group(1))
                title = re.sub(r'--priority\s+\w+', '', title, flags=re.IGNORECASE).strip()
            except ValueError:
                pass

        # Extract status
        status_match = re.search(r'--status\s+(\w+)', title, re.IGNORECASE)
        if status_match:
            try:
                result['status'] = TaskStatus.from_string(status_match.group(1))
                title = re.sub(r'--status\s+\w+', '', title, flags=re.IGNORECASE).strip()
            except ValueError:
                pass

        # Extract due date
        due_match = re.search(r'--due\s+(\d{4}-\d{2}-\d{2})', title)
        if due_match:
            result['due_date'] = due_match.group(1)
            title = re.sub(r'--due\s+\d{4}-\d{2}-\d{2}', '', title).strip()

        # Extract tags
        tags = re.findall(r'#(\w+)', title)
        if tags:
            result['tags'] = tags
            title = re.sub(r'#\w+', '', title).strip()

        # Extract assignee
        assignee_match = re.search(r'--assign\s+(\w+)', title, re.IGNORECASE)
        if assignee_match:
            result['assigned_to'] = assignee_match.group(1)
            title = re.sub(r'--assign\s+\w+', '', title, flags=re.IGNORECASE).strip()

        # Clean up title
        result['title'] = ' '.join(title.split())  # Remove extra whitespace

        return result

    def _enhance_task_interactively(self, task_attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance task attributes interactively."""
        print(f"\n{Fore.CYAN}📋 Optional Details (press Enter to skip):{Style.RESET_ALL}")

        # Description
        if 'description' not in task_attrs:
            desc = input(f"Description: ").strip()
            if desc:
                task_attrs['description'] = desc

        # Priority if not set
        if 'priority' not in task_attrs:
            priority_input = input(f"Priority (low/medium/high/critical) [medium]: ").strip().lower()
            if priority_input:
                try:
                    task_attrs['priority'] = TaskPriority.from_string(priority_input)
                except ValueError:
                    task_attrs['priority'] = TaskPriority.MEDIUM

        # Due date if not set
        if 'due_date' not in task_attrs:
            due_input = input(f"Due date (YYYY-MM-DD): ").strip()
            if due_input:
                try:
                    # Validate date format
                    datetime.strptime(due_input, "%Y-%m-%d")
                    task_attrs['due_date'] = due_input
                except ValueError:
                    print(f"{Fore.YELLOW}Invalid date format, skipping.{Style.RESET_ALL}")

        # Tags if not set
        if 'tags' not in task_attrs:
            tags_input = input(f"Tags (comma-separated): ").strip()
            if tags_input:
                task_attrs['tags'] = [tag.strip() for tag in tags_input.split(',')]

        return task_attrs

    def show_dashboard(self) -> None:
        """Display interactive task dashboard."""
        print(f"\n{Fore.CYAN}📋 Task Dashboard{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        while True:
            # Get current tasks
            all_tasks = self.task_manager.get_all_tasks()

            # Show summary
            self._show_task_summary(all_tasks)

            # Show recent tasks
            self._show_recent_tasks(all_tasks)

            # Show overdue tasks
            self._show_overdue_tasks(all_tasks)

            # Dashboard menu
            print(f"\n{Fore.CYAN}Dashboard Actions:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}1.{Style.RESET_ALL} Create new task")
            print(f"  {Fore.GREEN}2.{Style.RESET_ALL} View all tasks")
            print(f"  {Fore.GREEN}3.{Style.RESET_ALL} Quick status update")
            print(f"  {Fore.GREEN}4.{Style.RESET_ALL} Search tasks")
            print(f"  {Fore.GREEN}5.{Style.RESET_ALL} Refresh task scan")
            print(f"  {Fore.GREEN}6.{Style.RESET_ALL} Update task folder location")
            print(f"  {Fore.GREEN}0.{Style.RESET_ALL} Back to main menu")

            choice = input(f"\n{Fore.GREEN}Choose action (0-6): {Style.RESET_ALL}").strip()

            if choice == "1":
                self.quick_create()
            elif choice == "2":
                self.show_all_tasks()
            elif choice == "3":
                self.quick_status_update()
            elif choice == "4":
                self.search_tasks_interactive()
            elif choice == "5":
                self.refresh_task_scan()
            elif choice == "6":
                self.update_task_folder_location()
            elif choice == "0":
                break
            else:
                print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
                time.sleep(1)

    def _show_task_summary(self, all_tasks: Dict[str, List[Task]]) -> None:
        """Show task summary by status."""
        print(f"\n{Fore.YELLOW}📊 Summary by Status:{Style.RESET_ALL}")

        total_tasks = sum(len(tasks) for tasks in all_tasks.values())

        for status_str, tasks in all_tasks.items():
            if tasks:  # Only show statuses with tasks
                icon, style = self.status_styles.get(status_str, ('📄', 'white'))
                count = len(tasks)
                percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                print(f"  {icon} {status_str.upper()}: {Fore.WHITE}{count}{Style.RESET_ALL} ({percentage:.1f}%)")

        print(f"  📈 {Fore.WHITE}{Style.BRIGHT}TOTAL: {total_tasks} tasks{Style.RESET_ALL}")

    def _show_recent_tasks(self, all_tasks: Dict[str, List[Task]], limit: int = 5) -> None:
        """Show most recent tasks."""
        print(f"\n{Fore.YELLOW}🕒 Recent Tasks:{Style.RESET_ALL}")

        # Collect all tasks and sort by creation date
        recent_tasks = []
        for tasks in all_tasks.values():
            recent_tasks.extend(tasks)

        # Sort by created date (most recent first)
        recent_tasks.sort(key=lambda t: t.created_date, reverse=True)

        for i, task in enumerate(recent_tasks[:limit]):
            status_icon, status_style = self.status_styles.get(task.status.value, ('📄', 'white'))
            priority_icon, priority_style = self.priority_styles.get(task.priority.value, ('⚪', 'white'))

            print(f"  {i+1}. {status_icon} [{task.task_id}] {task.title[:40]}")
            print(f"     {priority_icon} {task.priority.value.title()} | Created: {task.created_date}")

    def _show_overdue_tasks(self, all_tasks: Dict[str, List[Task]]) -> None:
        """Show overdue tasks."""
        overdue_tasks = []
        today = datetime.now().date()

        for tasks in all_tasks.values():
            for task in tasks:
                if hasattr(task, 'due_date') and task.due_date:
                    try:
                        due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                        if due_date < today and task.status != TaskStatus.DONE:
                            overdue_tasks.append(task)
                    except ValueError:
                        continue

        if overdue_tasks:
            print(f"\n{Fore.RED}⚠️  Overdue Tasks:{Style.RESET_ALL}")
            for i, task in enumerate(overdue_tasks[:3]):  # Show max 3
                days_overdue = (today - datetime.strptime(task.due_date, "%Y-%m-%d").date()).days
                print(f"  {i+1}. {Fore.RED}🔥 [{task.task_id}] {task.title[:40]}")
                print(f"     Due: {task.due_date} ({days_overdue} days overdue)")

    def show_all_tasks(self, status_filter: str = None) -> None:
        """Show all tasks with optional status filtering."""
        all_tasks = self.task_manager.get_all_tasks()

        if status_filter:
            if status_filter in all_tasks:
                tasks_to_show = {status_filter: all_tasks[status_filter]}
            else:
                print(f"{Fore.RED}Invalid status filter: {status_filter}{Style.RESET_ALL}")
                return
        else:
            tasks_to_show = all_tasks

        print(f"\n{Fore.CYAN}📋 All Tasks{' - ' + status_filter.upper() if status_filter else ''}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        total_shown = 0
        for status_str, tasks in tasks_to_show.items():
            if tasks:
                status_icon, style = self.status_styles.get(status_str, ('📄', 'white'))
                print(f"\n{status_icon} {Fore.YELLOW}{status_str.upper()} ({len(tasks)} tasks):{Style.RESET_ALL}")

                for i, task in enumerate(tasks):
                    priority_icon, priority_style = self.priority_styles.get(task.priority.value, ('⚪', 'white'))
                    print(f"  {i+1:2}. {priority_icon} [{task.task_id}] {task.title}")
                    if hasattr(task, 'due_date') and task.due_date:
                        print(f"      📅 Due: {task.due_date}")

                total_shown += len(tasks)

        print(f"\n{Fore.CYAN}Total: {total_shown} tasks shown{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def quick_status_update(self) -> None:
        """Quick task status update interface."""
        print(f"\n{Fore.CYAN}🔄 Quick Status Update{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")

        # Get task ID
        task_id = input(f"{Fore.GREEN}Enter Task ID: {Style.RESET_ALL}").strip().upper()
        if not task_id:
            print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
            return

        # Find task
        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            print(f"{Fore.RED}Task not found: {task_id}{Style.RESET_ALL}")
            return

        # Show current status
        current_icon, current_style = self.status_styles.get(task.status.value, ('📄', 'white'))
        print(f"\nCurrent: {current_icon} {task.status.value.upper()}")
        print(f"Task: {task.title}")

        # Show valid transitions
        valid_transitions = self.task_manager.get_valid_transitions(task_id)
        if not valid_transitions:
            print(f"{Fore.RED}No valid transitions available.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}Available transitions:{Style.RESET_ALL}")
        for i, status in enumerate(valid_transitions, 1):
            icon, style = self.status_styles.get(status.value, ('📄', 'white'))
            print(f"  {i}. {icon} {status.value.upper()}")

        # Get new status
        try:
            choice = int(input(f"\n{Fore.GREEN}Choose new status (1-{len(valid_transitions)}): {Style.RESET_ALL}"))
            if 1 <= choice <= len(valid_transitions):
                new_status = valid_transitions[choice - 1]

                # Update status
                if self.task_manager.move_task_status(task_id, new_status):
                    new_icon, new_style = self.status_styles.get(new_status.value, ('📄', 'white'))
                    print(f"{Fore.GREEN}✅ Status updated: {new_icon} {new_status.value.upper()}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Failed to update status.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")

    def search_tasks_interactive(self) -> None:
        """Interactive task search interface."""
        print(f"\n{Fore.CYAN}🔍 Search Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")

        query = input(f"{Fore.GREEN}Search query: {Style.RESET_ALL}").strip()
        if not query:
            print(f"{Fore.YELLOW}Search cancelled.{Style.RESET_ALL}")
            return

        # Search tasks
        results = self.task_manager.search_tasks(query, search_content=True)

        if results:
            print(f"\n{Fore.GREEN}Found {len(results)} matching tasks:{Style.RESET_ALL}")
            for i, task in enumerate(results, 1):
                status_icon, status_style = self.status_styles.get(task.status.value, ('📄', 'white'))
                priority_icon, priority_style = self.priority_styles.get(task.priority.value, ('⚪', 'white'))

                print(f"  {i:2}. {status_icon} {priority_icon} [{task.task_id}] {task.title}")
                if hasattr(task, 'assigned_to') and task.assigned_to:
                    print(f"      👤 {task.assigned_to}")
        else:
            print(f"{Fore.YELLOW}No tasks found matching '{query}'.{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def _format_status(self, status: TaskStatus) -> str:
        """Format status with icon and color."""
        icon, style = self.status_styles.get(status.value, ('📄', 'white'))
        return f"{icon} {status.value.upper()}"

    def _format_priority(self, priority: TaskPriority) -> str:
        """Format priority with icon and color."""
        icon, style = self.priority_styles.get(priority.value, ('⚪', 'white'))
        return f"{icon} {priority.value.upper()}"

    def refresh_task_scan(self) -> None:
        """Refresh task scan - discover existing tasks and update settings."""
        print(f"\n{Fore.CYAN}🔄 Refresh Task Scan{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Scanning all task folders to discover existing tasks...{Style.RESET_ALL}")

        try:
            # Perform the refresh scan
            scan_result = self.task_manager.refresh_task_scan()

            if scan_result['success']:
                print(f"\n{Fore.GREEN}✅ Task scan completed successfully!{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}📊 Scan Results:{Style.RESET_ALL}")
                print(f"  📁 Tasks discovered: {Fore.WHITE}{scan_result['tasks_found']}{Style.RESET_ALL}")
                print(f"  🔄 Tasks processed: {Fore.WHITE}{scan_result['tasks_processed']}{Style.RESET_ALL}")

                # Show status breakdown
                if scan_result['status_counts']:
                    print(f"\n{Fore.CYAN}📈 Status Breakdown:{Style.RESET_ALL}")
                    for status, count in scan_result['status_counts'].items():
                        icon, style = self.status_styles.get(status, ('📄', 'white'))
                        print(f"  {icon} {status.upper()}: {Fore.WHITE}{count}{Style.RESET_ALL}")

                # Show next task number update
                if 'next_task_number' in scan_result:
                    print(f"\n{Fore.CYAN}🔢 Next Task Number:{Style.RESET_ALL}")
                    print(f"  Updated to: {Fore.WHITE}TASK-{scan_result['next_task_number']:03d}{Style.RESET_ALL}")

                # Show any issues found
                if scan_result.get('issues'):
                    print(f"\n{Fore.YELLOW}⚠️  Issues Found:{Style.RESET_ALL}")
                    for issue in scan_result['issues']:
                        print(f"  • {issue}")

                print(f"\n{Fore.GREEN}🎉 Dashboard summary refreshed!{Style.RESET_ALL}")

            else:
                print(f"\n{Fore.RED}❌ Task scan failed: {scan_result.get('error', 'Unknown error')}{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}❌ Error during task scan: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def update_task_folder_location(self) -> None:
        """Update the task folder location relative to indexed directory."""
        print(f"\n{Fore.CYAN}📁 Update Task Folder Location{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

        try:
            import json
            from pathlib import Path

            # Get current settings
            setup_settings_path = Path(".taskhero_setup.json")
            if not setup_settings_path.exists():
                print(f"{Fore.RED}❌ .taskhero_setup.json not found. Please run setup first.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            with open(setup_settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Get indexed directory (check multiple sources)
            indexed_directory = settings.get('codebase_path') or settings.get('last_directory')
            current_task_path = settings.get('task_storage_path', 'theherotasks')

            if not indexed_directory:
                print(f"{Fore.RED}❌ No indexed directory found in settings.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Please index a directory first.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            # Show current configuration
            print(f"\n{Fore.YELLOW}📋 Current Configuration:{Style.RESET_ALL}")
            print(f"  📂 Indexed Directory: {Fore.WHITE}{indexed_directory}{Style.RESET_ALL}")
            print(f"  📁 Current Task Folder: {Fore.WHITE}{current_task_path}{Style.RESET_ALL}")

            # Calculate current absolute path
            indexed_path = Path(indexed_directory)
            current_absolute_path = indexed_path / current_task_path
            print(f"  🎯 Full Task Path: {Fore.WHITE}{current_absolute_path}{Style.RESET_ALL}")

            # Show options
            print(f"\n{Fore.CYAN}📁 Task Folder Options:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}1.{Style.RESET_ALL} theherotasks (recommended)")
            print(f"  {Fore.GREEN}2.{Style.RESET_ALL} tasks")
            print(f"  {Fore.GREEN}3.{Style.RESET_ALL} project-tasks")
            print(f"  {Fore.GREEN}4.{Style.RESET_ALL} Custom folder name")
            print(f"  {Fore.GREEN}0.{Style.RESET_ALL} Cancel")

            choice = input(f"\n{Fore.GREEN}Choose option (0-4): {Style.RESET_ALL}").strip()

            if choice == "0":
                print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                return
            elif choice == "1":
                new_folder = "theherotasks"
            elif choice == "2":
                new_folder = "tasks"
            elif choice == "3":
                new_folder = "project-tasks"
            elif choice == "4":
                new_folder = input(f"{Fore.GREEN}Enter custom folder name: {Style.RESET_ALL}").strip()
                if not new_folder:
                    print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                    return
                # Validate folder name
                if any(char in new_folder for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
                    print(f"{Fore.RED}❌ Invalid folder name. Please avoid special characters.{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    return
            else:
                print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            # Check if it's the same as current
            if new_folder == current_task_path:
                print(f"{Fore.YELLOW}📁 Task folder is already set to '{new_folder}'.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            # Show what will happen
            new_absolute_path = indexed_path / new_folder
            print(f"\n{Fore.CYAN}📋 Proposed Changes:{Style.RESET_ALL}")
            print(f"  📁 New Task Folder: {Fore.WHITE}{new_folder}{Style.RESET_ALL}")
            print(f"  🎯 New Full Path: {Fore.WHITE}{new_absolute_path}{Style.RESET_ALL}")

            # Ask about migration
            migrate_tasks = False
            if current_absolute_path.exists():
                print(f"\n{Fore.YELLOW}📦 Existing tasks found in current location.{Style.RESET_ALL}")
                migrate_choice = input(f"{Fore.GREEN}Migrate existing tasks to new location? (y/N): {Style.RESET_ALL}").strip().lower()
                migrate_tasks = migrate_choice in ['y', 'yes']

            # Confirm
            print(f"\n{Fore.CYAN}⚠️  Confirmation Required:{Style.RESET_ALL}")
            print(f"  • Update task folder to: {Fore.WHITE}{new_folder}{Style.RESET_ALL}")
            if migrate_tasks:
                print(f"  • Migrate existing tasks: {Fore.GREEN}Yes{Style.RESET_ALL}")
            else:
                print(f"  • Migrate existing tasks: {Fore.RED}No{Style.RESET_ALL}")

            confirm = input(f"\n{Fore.GREEN}Proceed with update? (y/N): {Style.RESET_ALL}").strip().lower()
            if confirm not in ['y', 'yes']:
                print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                return

            # Perform the update
            print(f"\n{Fore.CYAN}🔄 Updating task folder location...{Style.RESET_ALL}")

            if self.task_manager.update_task_storage_path(new_folder, migrate_tasks):
                print(f"{Fore.GREEN}✅ Task folder location updated successfully!{Style.RESET_ALL}")
                print(f"  📁 New location: {Fore.WHITE}{new_absolute_path}{Style.RESET_ALL}")

                if migrate_tasks:
                    print(f"  📦 Tasks migrated successfully")

                print(f"\n{Fore.CYAN}💡 Note: The task folder is now relative to your indexed directory.{Style.RESET_ALL}")
                print(f"This ensures task files are included in your project's indexing.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Failed to update task folder location.{Style.RESET_ALL}")
                print(f"Check the logs for more details.{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}❌ Error updating task folder location: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")