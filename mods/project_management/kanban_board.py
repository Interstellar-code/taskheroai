"""
Kanban Board Visualization Module

Provides terminal-based Kanban board visualization using rich library.
Supports interactive navigation, task management, and real-time updates.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.box import ROUNDED, DOUBLE, SIMPLE
from rich.rule import Rule
from rich.padding import Padding
from rich.style import Style
from rich import print as rprint

from .task_manager import TaskManager, TaskStatus, TaskPriority, Task

logger = logging.getLogger("TaskHeroAI.ProjectManagement.KanbanBoard")


class KanbanBoard:
    """Interactive terminal-based Kanban board using rich library."""
    
    def __init__(self, task_manager: TaskManager):
        """Initialize Kanban board.
        
        Args:
            task_manager: TaskManager instance for task operations
        """
        self.task_manager = task_manager
        self.console = Console()
        self.selected_column = 0  # Start with backlog
        self.selected_task = 0
        self.show_help = False
        
        # Column definitions with order and styling
        self.columns = [
            {
                'status': 'backlog',
                'title': '📦 BACKLOG',
                'color': 'bright_black',
                'style': 'dim'
            },
            {
                'status': 'todo', 
                'title': '📝 TODO',
                'color': 'yellow',
                'style': 'bold'
            },
            {
                'status': 'inprogress',
                'title': '🔄 IN PROGRESS', 
                'color': 'blue',
                'style': 'bold blue'
            },
            {
                'status': 'testing',
                'title': '🧪 TESTING',
                'color': 'magenta', 
                'style': 'bold magenta'
            },
            {
                'status': 'devdone',
                'title': '✅ DEV DONE',
                'color': 'cyan',
                'style': 'bold cyan'
            },
            {
                'status': 'done',
                'title': '🎉 DONE',
                'color': 'green',
                'style': 'bold green'
            }
        ]
        
        # Priority styling
        self.priority_styles = {
            'critical': ('🔥', 'bold red'),
            'high': ('🔴', 'red'),
            'medium': ('🟡', 'yellow'),
            'low': ('🟢', 'green')
        }
        
    def get_terminal_size(self) -> Tuple[int, int]:
        """Get terminal size with fallback."""
        try:
            import shutil
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except:
            return 120, 30
            
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def create_task_card(self, task: Task, is_selected: bool = False) -> Panel:
        """Create a task card panel.
        
        Args:
            task: Task object to display
            is_selected: Whether this task is currently selected
            
        Returns:
            Rich Panel object representing the task card
        """
        # Priority indicator
        priority_icon, priority_style = self.priority_styles.get(
            task.priority.value if hasattr(task.priority, 'value') else str(task.priority).lower(),
            ('⚪', 'white')
        )
        
        # Task content
        content = []
        
        # Title line with priority
        title_line = Text()
        title_line.append(f"[{task.priority.value[0].upper() if hasattr(task.priority, 'value') else str(task.priority)[0].upper()}] ", style=priority_style)
        title_line.append(task.task_id, style="bold")
        content.append(title_line)
        
        # Task title (truncated if too long)
        task_title = task.title
        if len(task_title) > 35:
            task_title = task_title[:32] + "..."
        content.append(Text(f"📋 {task_title}", style="bold white"))
        
        # Due date if available
        if hasattr(task, 'due_date') and task.due_date:
            due_style = "red" if self._is_overdue(task.due_date) else "cyan"
            content.append(Text(f"📅 Due: {task.due_date}", style=due_style))
        
        # Assignee
        if hasattr(task, 'assigned_to') and task.assigned_to:
            content.append(Text(f"👤 {task.assigned_to}", style="bright_blue"))
        
        # Tags if available
        if hasattr(task, 'tags') and task.tags:
            tags_text = " ".join([f"#{tag}" for tag in task.tags[:3]])  # Show max 3 tags
            if len(tags_text) > 30:
                tags_text = tags_text[:27] + "..."
            content.append(Text(tags_text, style="dim"))
        
        # Combine content
        card_content = "\n".join([str(line) for line in content])
        
        # Card styling
        if is_selected:
            return Panel(
                card_content,
                border_style="bright_cyan",
                box=DOUBLE,
                padding=(0, 1),
                title="[bright_cyan]▶ SELECTED",
                title_align="left"
            )
        else:
            return Panel(
                card_content,
                border_style="white",
                box=ROUNDED,
                padding=(0, 1)
            )
    
    def _is_overdue(self, due_date: str) -> bool:
        """Check if a task is overdue."""
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d")
            return due.date() < datetime.now().date()
        except:
            return False
    
    def create_column_panel(self, column: Dict[str, str], tasks: List[Task], is_selected: bool = False) -> Panel:
        """Create a column panel with tasks.
        
        Args:
            column: Column configuration
            tasks: List of tasks in this column
            is_selected: Whether this column is currently selected
            
        Returns:
            Rich Panel object representing the column
        """
        column_content = []
        
        # Add task cards
        for i, task in enumerate(tasks):
            task_selected = is_selected and i == self.selected_task
            task_card = self.create_task_card(task, task_selected)
            column_content.append(task_card)
        
        # If no tasks, show empty message
        if not tasks:
            empty_panel = Panel(
                Align.center("No tasks", style="dim"),
                border_style="dim",
                box=SIMPLE,
                padding=(1, 1)
            )
            column_content.append(empty_panel)
        
        # Create column content
        content = Columns(column_content, equal=True, expand=False) if len(column_content) > 1 else (column_content[0] if column_content else "")
        
        # Column styling
        border_style = "bright_cyan" if is_selected else column['color']
        box_style = DOUBLE if is_selected else ROUNDED
        
        title = f"{column['title']} ({len(tasks)})"
        if is_selected:
            title = f"▶ {title}"
        
        return Panel(
            content,
            title=title,
            title_align="center",
            border_style=border_style,
            box=box_style,
            padding=(0, 1)
        )
    
    def create_kanban_layout(self, all_tasks: Dict[str, List[Task]]) -> Layout:
        """Create the main Kanban board layout.
        
        Args:
            all_tasks: Dictionary of tasks organized by status
            
        Returns:
            Rich Layout object
        """
        # Create column panels
        column_panels = []
        
        for i, column in enumerate(self.columns):
            status = column['status']
            tasks = all_tasks.get(status, [])
            is_selected = i == self.selected_column
            
            panel = self.create_column_panel(column, tasks, is_selected)
            column_panels.append(panel)
        
        # Create main layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="board", ratio=1),
            Layout(name="footer", size=5),
        )
        
        # Header
        header_text = Text("TaskHero AI - Kanban Board", style="bold bright_cyan", justify="center")
        layout["header"].update(Panel(header_text, box=ROUNDED))
        
        # Board - create columns layout
        board_layout = Layout()
        if len(column_panels) <= 3:
            # Single row for 3 or fewer columns
            board_layout.split_row(*[Layout(panel) for panel in column_panels])
        else:
            # Two rows for more than 3 columns
            top_columns = column_panels[:3]
            bottom_columns = column_panels[3:]
            
            board_layout.split_column(
                Layout(name="top_row"),
                Layout(name="bottom_row")
            )
            
            board_layout["top_row"].split_row(*[Layout(panel) for panel in top_columns])
            board_layout["bottom_row"].split_row(*[Layout(panel) for panel in bottom_columns])
        
        layout["board"].update(board_layout)
        
        # Footer with statistics and controls
        footer_content = self.create_footer(all_tasks)
        layout["footer"].update(Panel(footer_content, title="Controls & Statistics", box=ROUNDED))
        
        return layout
    
    def create_footer(self, all_tasks: Dict[str, List[Task]]) -> str:
        """Create footer with statistics and controls."""
        # Calculate statistics
        total_tasks = sum(len(tasks) for tasks in all_tasks.values())
        completed_tasks = len(all_tasks.get('done', []))
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Statistics line
        stats = f"📊 Total: {total_tasks} | Completed: {completed_tasks} | Progress: {progress:.1f}%"
        
        # Status summary
        status_summary = []
        for column in self.columns:
            status = column['status']
            count = len(all_tasks.get(status, []))
            if count > 0:
                status_summary.append(f"{column['title'].split()[1]}: {count}")
        
        summary_line = " | ".join(status_summary)
        
        # Controls
        controls = "💡 Controls: ← → Navigate Columns | ↑ ↓ Select Tasks | ENTER View Details | M Move | D Delete | Q Quit | H Help"
        
        return f"{stats}\n{summary_line}\n{controls}"
    
    def get_user_input(self) -> str:
        """Get user input for navigation."""
        try:
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':  # Special key prefix on Windows
                    key = msvcrt.getch()
                    if key == b'H':  # Up arrow
                        return 'up'
                    elif key == b'P':  # Down arrow  
                        return 'down'
                    elif key == b'K':  # Left arrow
                        return 'left'
                    elif key == b'M':  # Right arrow
                        return 'right'
                elif key == b'\r':  # Enter
                    return 'enter'
                elif key.lower() == b'q':
                    return 'quit'
                elif key.lower() == b'm':
                    return 'move'
                elif key.lower() == b'd':
                    return 'delete'
                elif key.lower() == b'h':
                    return 'help'
            return None
        except ImportError:
            # Fallback for non-Windows systems
            import select
            import sys
            import tty
            import termios
            
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    tty.cbreak(sys.stdin.fileno())
                    key = sys.stdin.read(1)
                    
                    if key == '\x1b':  # ESC sequence
                        key += sys.stdin.read(2)
                        if key == '\x1b[A':  # Up arrow
                            return 'up'
                        elif key == '\x1b[B':  # Down arrow
                            return 'down'
                        elif key == '\x1b[D':  # Left arrow
                            return 'left'
                        elif key == '\x1b[C':  # Right arrow
                            return 'right'
                    elif key == '\r' or key == '\n':  # Enter
                        return 'enter'
                    elif key.lower() == 'q':
                        return 'quit'
                    elif key.lower() == 'm':
                        return 'move'
                    elif key.lower() == 'd':
                        return 'delete'
                    elif key.lower() == 'h':
                        return 'help'
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            return None
    
    def show_task_details(self, task: Task):
        """Show detailed task information in a popup-style display."""
        self.clear_screen()
        
        # Create detailed task view
        detail_content = []
        
        # Header
        detail_content.append(Rule(f"[bold bright_cyan]Task Details: {task.task_id}[/bold bright_cyan]"))
        detail_content.append("")
        
        # Basic info
        detail_content.append(f"[bold]Title:[/bold] {task.title}")
        detail_content.append(f"[bold]Status:[/bold] {task.status.value.title()}")
        detail_content.append(f"[bold]Priority:[/bold] {task.priority.value.title()}")
        detail_content.append(f"[bold]Created:[/bold] {task.created_date}")
        
        if hasattr(task, 'due_date') and task.due_date:
            due_style = "[red]" if self._is_overdue(task.due_date) else "[cyan]"
            detail_content.append(f"[bold]Due Date:[/bold] {due_style}{task.due_date}[/{due_style.strip('[')}]")
        
        if hasattr(task, 'assigned_to') and task.assigned_to:
            detail_content.append(f"[bold]Assigned To:[/bold] {task.assigned_to}")
        
        if hasattr(task, 'task_type') and task.task_type:
            detail_content.append(f"[bold]Task Type:[/bold] {task.task_type}")
        
        if hasattr(task, 'tags') and task.tags:
            tags_str = ", ".join(task.tags)
            detail_content.append(f"[bold]Tags:[/bold] {tags_str}")
        
        detail_content.append("")
        
        # Content/Description
        if hasattr(task, 'content') and task.content:
            detail_content.append("[bold]Description:[/bold]")
            # Limit content display to avoid overwhelming
            content_lines = task.content.split('\n')[:15]
            for line in content_lines:
                detail_content.append(f"  {line}")
            
            if len(task.content.split('\n')) > 15:
                detail_content.append("  [dim]... (content truncated)[/dim]")
        
        detail_content.append("")
        detail_content.append(Rule("[dim]Press any key to return to board[/dim]"))
        
        # Display the details
        for line in detail_content:
            rprint(line)
        
        # Wait for user input
        input()
    
    def move_task_dialog(self, task: Task) -> bool:
        """Show dialog to move task to different status.
        
        Args:
            task: Task to move
            
        Returns:
            True if task was moved, False otherwise
        """
        current_status = task.status.value
        
        # Show available statuses
        self.console.print(f"\n[bold cyan]Move Task: {task.title}[/bold cyan]")
        self.console.print(f"Current Status: [yellow]{current_status.title()}[/yellow]")
        self.console.print("\nAvailable statuses:")
        
        available_statuses = []
        for i, column in enumerate(self.columns):
            if column['status'] != current_status:
                available_statuses.append(column['status'])
                self.console.print(f"  {i+1}. {column['title']}")
        
        self.console.print(f"  0. Cancel")
        
        # Get user choice
        try:
            choice = Prompt.ask("\nSelect new status", choices=[str(i) for i in range(len(available_statuses) + 1)])
            choice_int = int(choice)
            
            if choice_int == 0:
                return False
            
            if 1 <= choice_int <= len(available_statuses):
                new_status = available_statuses[choice_int - 1]
                
                # Update task status
                new_task_status = TaskStatus.from_string(new_status)
                success = task.update_status(new_task_status, validate=False)
                
                if success:
                    # Save the task
                    if self.task_manager.save_task(task):
                        # Move file to new directory
                        if hasattr(task, 'file_path') and task.file_path:
                            old_path = Path(task.file_path)
                            new_dir = old_path.parent.parent / new_status
                            new_dir.mkdir(exist_ok=True)
                            new_path = new_dir / old_path.name
                            
                            old_path.rename(new_path)
                            task.file_path = str(new_path)
                        
                        self.console.print(f"[green]✅ Task moved to {new_status.title()}[/green]")
                        return True
                    else:
                        self.console.print("[red]❌ Failed to save task[/red]")
                else:
                    self.console.print("[red]❌ Failed to update task status[/red]")
        except (ValueError, KeyboardInterrupt):
            self.console.print("[yellow]Operation cancelled[/yellow]")
        
        return False
    
    def delete_task_dialog(self, task: Task) -> bool:
        """Show dialog to confirm task deletion.
        
        Args:
            task: Task to delete
            
        Returns:
            True if task was deleted, False otherwise
        """
        self.console.print(f"\n[bold red]Delete Task: {task.title}[/bold red]")
        self.console.print(f"Task ID: {task.task_id}")
        self.console.print(f"Status: {task.status.value.title()}")
        
        if Confirm.ask("\n[red]Are you sure you want to delete this task?[/red]", default=False):
            success = self.task_manager.delete_task(task.task_id)
            if success:
                self.console.print("[green]✅ Task deleted successfully[/green]")
                return True
            else:
                self.console.print("[red]❌ Failed to delete task[/red]")
        else:
            self.console.print("[yellow]Deletion cancelled[/yellow]")
        
        return False
    
    def show_help(self):
        """Show help dialog."""
        self.clear_screen()
        
        help_content = [
            Rule("[bold bright_cyan]Kanban Board Help[/bold bright_cyan]"),
            "",
            "[bold]Navigation:[/bold]",
            "  ← →     Navigate between columns",
            "  ↑ ↓     Select tasks within a column",
            "",
            "[bold]Actions:[/bold]",
            "  ENTER   View detailed task information",
            "  M       Move task to different status",
            "  D       Delete task (with confirmation)",
            "  H       Show this help",
            "  Q       Quit Kanban board",
            "",
            "[bold]Columns:[/bold]",
            "  📦 BACKLOG     - Tasks planned for future",
            "  📝 TODO        - Tasks ready to start",
            "  🔄 IN PROGRESS - Tasks currently being worked on",
            "  🧪 TESTING     - Tasks being tested/reviewed",
            "  ✅ DEV DONE    - Development completed, pending final review",
            "  🎉 DONE        - Completed tasks",
            "",
            "[bold]Task Cards Show:[/bold]",
            "  • Priority indicator ([H]igh, [M]edium, [L]ow, [C]ritical)",
            "  • Task ID and title", 
            "  • Due date (red if overdue)",
            "  • Assignee",
            "  • Tags",
            "",
            Rule("[dim]Press any key to return to board[/dim]")
        ]
        
        for line in help_content:
            rprint(line)
        
        input()
    
    def run(self):
        """Run the interactive Kanban board."""
        self.console.print("[bold bright_cyan]Loading Kanban Board...[/bold bright_cyan]")
        
        try:
            while True:
                # Get current tasks
                all_tasks = self.task_manager.get_all_tasks()
                
                # Clear screen and create layout
                self.clear_screen()
                layout = self.create_kanban_layout(all_tasks)
                
                # Display the board
                self.console.print(layout)
                
                # Handle user input
                key = self.get_user_input()
                
                if key == 'quit':
                    break
                elif key == 'left':
                    self.selected_column = max(0, self.selected_column - 1)
                    self.selected_task = 0  # Reset task selection
                elif key == 'right':
                    self.selected_column = min(len(self.columns) - 1, self.selected_column + 1)
                    self.selected_task = 0  # Reset task selection
                elif key == 'up':
                    current_column_status = self.columns[self.selected_column]['status']
                    current_tasks = all_tasks.get(current_column_status, [])
                    if current_tasks:
                        self.selected_task = max(0, self.selected_task - 1)
                elif key == 'down':
                    current_column_status = self.columns[self.selected_column]['status']
                    current_tasks = all_tasks.get(current_column_status, [])
                    if current_tasks:
                        self.selected_task = min(len(current_tasks) - 1, self.selected_task + 1)
                elif key == 'enter':
                    # Show task details
                    current_column_status = self.columns[self.selected_column]['status']
                    current_tasks = all_tasks.get(current_column_status, [])
                    if current_tasks and self.selected_task < len(current_tasks):
                        task = current_tasks[self.selected_task]
                        self.show_task_details(task)
                elif key == 'move':
                    # Move task
                    current_column_status = self.columns[self.selected_column]['status']
                    current_tasks = all_tasks.get(current_column_status, [])
                    if current_tasks and self.selected_task < len(current_tasks):
                        task = current_tasks[self.selected_task]
                        if self.move_task_dialog(task):
                            # Reset selection to avoid out-of-bounds
                            self.selected_task = 0
                elif key == 'delete':
                    # Delete task
                    current_column_status = self.columns[self.selected_column]['status']
                    current_tasks = all_tasks.get(current_column_status, [])
                    if current_tasks and self.selected_task < len(current_tasks):
                        task = current_tasks[self.selected_task]
                        if self.delete_task_dialog(task):
                            # Reset selection to avoid out-of-bounds
                            self.selected_task = 0
                elif key == 'help':
                    self.show_help()
                
                # Small delay to prevent excessive CPU usage
                import time
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            pass
        finally:
            self.console.print("\n[bold bright_cyan]Goodbye! 👋[/bold bright_cyan]")


def launch_kanban_board(task_manager: TaskManager):
    """Launch the Kanban board interface.
    
    Args:
        task_manager: TaskManager instance
    """
    try:
        board = KanbanBoard(task_manager)
        board.run()
    except Exception as e:
        print(f"Error launching Kanban board: {e}")
        logger.error(f"Kanban board error: {e}") 