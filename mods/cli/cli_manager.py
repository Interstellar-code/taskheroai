"""
CLI Manager for TaskHero AI - CLEAN VERSION

This module handles the CLI functionality with proper formatting.
"""

import asyncio
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from colorama import Fore, Style
from ..core import BaseManager


class CLIManager(BaseManager):
    """Manager for CLI functionality and main application loop."""
    
    def __init__(self, settings_manager=None, ai_manager=None, ui_manager=None, display_manager=None):
        """Initialize the CLI manager."""
        super().__init__("CLIManager")
        
        # Injected managers
        self.settings_manager = settings_manager
        self.ai_manager = ai_manager
        self.ui_manager = ui_manager
        self.display_manager = display_manager
        
        # Application state
        self.running = False
        self.indexer = None
        self.index_outdated = False
        self.file_selector = None
        self.project_analyzer = None
        self.chat_handler = None
        
        # Project management components (TASK-005)
        self.project_planner = None
        self.task_manager = None
        self.kanban_board = None
        self.task_cli = None
        
        # Recent projects tracking (TASK-014)
        self.recent_projects = []
        self.project_info = {}
    
    def _perform_initialization(self) -> None:
        """Initialize the CLI manager."""
        # Initialize indexer components if we have a last directory
        if self.settings_manager:
            last_dir = self.settings_manager.get_last_directory()
            if last_dir and os.path.isdir(last_dir):
                try:
                    from ..code.indexer import FileIndexer
                    from ..code.decisions import FileSelector, ProjectAnalyzer, ChatHandler
                    
                    self.indexer = FileIndexer(last_dir)
                    self.file_selector = FileSelector()
                    self.project_analyzer = ProjectAnalyzer(self.indexer)
                    
                    # Check index status
                    index_status = self.indexer.is_index_complete()
                    self.index_outdated = not index_status.get('complete', False)
                    
                    self.logger.info(f"Loaded existing project: {last_dir}")
                    print(f"\n{Fore.GREEN}✓ Loaded existing project: {Fore.CYAN}{os.path.basename(last_dir)}{Style.RESET_ALL}")
                    
                    # Set AI manager dependencies for existing project
                    if self.ai_manager:
                        self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)
                    
                    if self.index_outdated:
                        print(f"{Fore.YELLOW}⚠ Index is outdated. Consider reindexing.{Style.RESET_ALL}")
                        
                except Exception as e:
                    self.logger.error(f"Failed to load existing project: {e}")
        
        # Initialize project management components (TASK-005)
        self._initialize_project_management()
                    
        self.logger.info("CLI Manager initialized")
        self.update_status("cli_ready", True)
    
    def _initialize_project_management(self) -> None:
        """Initialize project management components for TASK-005."""
        try:
            from ..project_management.project_planner import ProjectPlanner
            from ..project_management.kanban_board import KanbanBoard
            from .task_cli import TaskCLI
            
            self.project_planner = ProjectPlanner()
            self.task_manager = self.project_planner.task_manager
            self.kanban_board = KanbanBoard(self.task_manager)
            
            # Initialize enhanced TaskCLI (TASK-005)
            self.task_cli = TaskCLI(self.settings_manager)
            
            self.logger.info("Project management components initialized")
            self.logger.info("Enhanced TaskCLI initialized for TASK-005")
            
        except Exception as e:
            self.logger.warning(f"Project management components not available: {e}")
            # This is not critical, so we continue without PM features
    
    def run_main_loop(self) -> None:
        """Run the main application loop."""
        if not self.is_initialized:
            self.initialize()
        
        self.running = True
        self.logger.info("Starting main CLI loop...")
        
        try:
            while self.running:
                # Update menu state
                if self.ui_manager:
                    self.ui_manager.set_application_state(self.indexer, self.index_outdated)
                    self.ui_manager.display_main_menu()
                    
                    choice = self.ui_manager.get_user_choice()
                    self._handle_menu_choice(choice)
                else:
                    print("UI Manager not available")
                    break
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"CLI loop error: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        finally:
            self.running = False
    
    def _handle_menu_choice(self, choice: str) -> None:
        """Handle user menu choice with reorganized menu structure."""
        try:
            # Indexing & Embedding Section (1-4)
            if choice == "1":
                self._handle_index_code()
            elif choice == "2":
                self._handle_view_files()
            elif choice == "3":
                self._handle_view_project()
            elif choice == "4":
                self._handle_recent_projects()
            # Chat with Code Section (5-7)
            elif choice == "5":
                self._handle_chat_ai()
            elif choice == "6":
                self._handle_max_chat()
            elif choice == "7":
                self._handle_agent_mode()
            # TaskHero Management Section (8-12)
            elif choice == "8":
                self._handle_task_dashboard()
            elif choice == "9":
                self._handle_kanban_board()
            elif choice == "10":
                self._handle_quick_create_task()
            elif choice == "11":
                self._handle_quick_view_tasks()
            elif choice == "12":
                self._handle_search_tasks()
            # Settings & Tools Section
            elif choice == "13":
                self._handle_project_cleanup()
            elif choice == "14":
                self._handle_ai_settings()
            elif choice == "0":
                self._handle_exit()
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1-14 or 0 to exit.{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error handling choice {choice}: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    def _handle_index_code(self) -> None:
        """Handle index code option."""
        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Index Code Directory" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        
        try:
            # Import required modules
            from ..code.indexer import FileIndexer
            from ..code.decisions import FileSelector, ProjectAnalyzer
            
            # Get directory to index
            if self.indexer and self.index_outdated:
                directory = self.indexer.root_path
                print(f"{Fore.YELLOW}Using current directory: {Fore.CYAN}{directory}{Style.RESET_ALL}")
            else:
                last_dir = ""
                if self.settings_manager:
                    last_dir = self.settings_manager.get_last_directory()
                    
                default_dir = last_dir if last_dir else os.getcwd()
                print(f"{Fore.YELLOW}Enter directory path {Fore.CYAN}(default: {default_dir}){Fore.YELLOW}:{Style.RESET_ALL}")
                directory = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip()
                
                if not directory:
                    directory = default_dir
                    
                if not os.path.isdir(directory):
                    print(f"{Fore.RED}Error: '{directory}' is not a valid directory.{Style.RESET_ALL}")
                    return
            
            print(f"{Fore.CYAN}Indexing directory: {Style.BRIGHT}{directory}{Style.RESET_ALL}")
            
            # Initialize or reuse indexer
            if not self.indexer or self.indexer.root_path != directory:
                self.logger.info(f"Creating indexer for directory: {directory}")
                self.indexer = FileIndexer(directory)
                self.file_selector = FileSelector()
                self.project_analyzer = ProjectAnalyzer(self.indexer)
                
                # Set AI manager dependencies when indexer is created
                if self.ai_manager:
                    self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)
            
            # Check what files need indexing
            print(f"{Fore.CYAN}Scanning files to be indexed...{Style.RESET_ALL}")
            
            try:
                files_to_process = self.indexer.get_outdated_files()
            except Exception as e:
                self.logger.error(f"Error scanning files: {e}")
                files_to_process = []
            
            if files_to_process:
                print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}📋 Index Summary:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   Directory: {Style.BRIGHT}{directory}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   Files to index: {Style.BRIGHT}{len(files_to_process)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                
                # Ask for confirmation
                confirmation = input(f"\n{Fore.GREEN}Proceed with indexing? (y/N): {Style.RESET_ALL}").strip().lower()
                
                if confirmation not in ['y', 'yes']:
                    print(f"{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
                    return
                
                print(f"{Fore.GREEN}✓ Starting indexing process...{Style.RESET_ALL}")
                
                # Simple progress tracking
                indexed_count = 0
                start_time = time.time()
                
                def progress_callback():
                    nonlocal indexed_count
                    indexed_count += 1
                    percent = int((indexed_count / len(files_to_process)) * 100)
                    print(f"\r{Fore.YELLOW}Progress: {percent}% ({indexed_count}/{len(files_to_process)}){Style.RESET_ALL}", end="", flush=True)
                    return False
                
                # Index the files
                indexed_files = self.indexer.index_directory(progress_callback)
                
                print(f"\n{Fore.GREEN}✓ Indexed {Style.BRIGHT}{len(indexed_files)}{Style.NORMAL} files{Style.RESET_ALL}")
                
                # Save the directory
                if self.settings_manager:
                    self.settings_manager.set_last_directory(directory)
                    
                # Update AI manager dependencies after indexing
                if self.ai_manager:
                    self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)
                    
                self.index_outdated = False
                print(f"{Fore.GREEN}✓ Indexing completed successfully!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}📁 You can now use chat or agent mode to interact with your codebase.{Style.RESET_ALL}")
                
            else:
                print(f"{Fore.GREEN}✓ All files are already indexed{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error indexing code: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_exit(self) -> None:
        """Handle exit option."""
        self.running = False
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
    
    def _handle_view_files(self) -> None:
        """Handle view indexed files option."""
        print(f"\n{Fore.CYAN}📁 View Indexed Files{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This functionality will be implemented in the next phase.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will display all indexed files with metadata and filtering options.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_view_project(self) -> None:
        """Handle view project info option."""
        print(f"\n{Fore.CYAN}📊 View Project Info{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This functionality will be implemented in the next phase.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will display project structure, statistics, and analysis.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_recent_projects(self) -> None:
        """Handle recent projects option."""
        print(f"\n{Fore.CYAN}📚 Recent Projects{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This functionality will be implemented in the next phase.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will show recently indexed projects with quick switching.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_chat_ai(self) -> None:
        """Handle chat with AI option."""
        print(f"\n{Fore.CYAN}💬 Chat with AI{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        if self.ai_manager:
            self.ai_manager.chat_with_ai(max_chat_mode=False)
        else:
            print(f"{Fore.RED}AI Manager not available.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_max_chat(self) -> None:
        """Handle max chat with AI option."""
        print(f"\n{Fore.CYAN}🔥 Max Chat with AI{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.RED}WARNING: This mode uses more tokens and sends full file contents.{Style.RESET_ALL}")
        
        if self.ai_manager:
            self.ai_manager.chat_with_ai(max_chat_mode=True)
        else:
            print(f"{Fore.RED}AI Manager not available.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_agent_mode(self) -> None:
        """Handle agent mode option."""
        print(f"\n{Fore.CYAN}🤖 Agent Mode{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        if self.ai_manager:
            # Agent mode is async, so we need to run it in event loop
            try:
                asyncio.run(self.ai_manager.agent_mode())
            except Exception as e:
                self.logger.error(f"Agent mode error: {e}")
                print(f"{Fore.RED}Error in agent mode: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}AI Manager not available.{Style.RESET_ALL}")
            
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_task_dashboard(self) -> None:
        """Handle task dashboard option - Enhanced with TaskCLI."""
        print(f"\n{Fore.CYAN}📋 Enhanced Task Dashboard{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        try:
            # Initialize TaskCLI if not already done
            if not hasattr(self, 'task_cli') or not self.task_cli:
                from .task_cli import TaskCLI
                self.task_cli = TaskCLI(self.settings_manager)
                print(f"{Fore.GREEN}✓ Enhanced TaskCLI initialized{Style.RESET_ALL}")
            
            # Use enhanced TaskCLI dashboard
            self.task_cli.show_dashboard()
            
        except Exception as e:
            self.logger.error(f"Enhanced task dashboard error: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Falling back to basic dashboard...{Style.RESET_ALL}")
            
            # Fallback to basic dashboard
            if self.task_manager:
                try:
                    all_tasks = self.task_manager.get_all_tasks()
                    print(f"{Fore.GREEN}Total Tasks: {len(all_tasks)}{Style.RESET_ALL}")
                    
                    by_status = {}
                    for task in all_tasks:
                        status = task.get('status', 'unknown')
                        by_status[status] = by_status.get(status, 0) + 1
                    
                    for status, count in by_status.items():
                        print(f"{Fore.CYAN}  {status.title()}: {count}{Style.RESET_ALL}")
                        
                except Exception as fallback_error:
                    print(f"{Fore.RED}Fallback dashboard error: {fallback_error}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Task management not available.{Style.RESET_ALL}")
                
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_kanban_board(self) -> None:
        """Handle kanban board option."""
        print(f"\n{Fore.CYAN}📌 Kanban Board{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        if self.kanban_board:
            try:
                self.kanban_board.run()
            except Exception as e:
                self.logger.error(f"Kanban board error: {e}")
                print(f"{Fore.RED}Error running kanban board: {e}{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Kanban board not available.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_quick_create_task(self) -> None:
        """Handle quick create task option - Enhanced with ProjectPlanner."""
        print(f"\n{Fore.CYAN}➕ Quick Create Task{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        try:
            # Use ProjectPlanner if available for enhanced task creation
            if self.project_planner:
                print(f"{Fore.GREEN}✨ Enhanced task creation with auto-generated ID{Style.RESET_ALL}")
                
                # Get basic task info
                title = input(f"{Fore.GREEN}Task title: {Style.RESET_ALL}").strip()
                if not title:
                    print(f"{Fore.YELLOW}Task creation cancelled.{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                # Optional description
                description = input(f"{Fore.GREEN}Description (optional): {Style.RESET_ALL}").strip()
                
                # Priority selection
                print(f"\n{Fore.CYAN}Priority options:{Style.RESET_ALL}")
                print(f"  1. Low")
                print(f"  2. Medium (default)")
                print(f"  3. High")
                print(f"  4. Critical")
                
                priority_choice = input(f"{Fore.GREEN}Select priority (1-4, default: 2): {Style.RESET_ALL}").strip()
                priority_map = {'1': 'low', '2': 'medium', '3': 'high', '4': 'critical'}
                priority = priority_map.get(priority_choice, 'medium')
                
                # Due date (optional)
                due_date = input(f"{Fore.GREEN}Due date (YYYY-MM-DD, optional): {Style.RESET_ALL}").strip()
                if due_date:
                    try:
                        from datetime import datetime
                        datetime.strptime(due_date, "%Y-%m-%d")  # Validate format
                    except ValueError:
                        print(f"{Fore.YELLOW}Invalid date format, skipping due date.{Style.RESET_ALL}")
                        due_date = None
                
                # Create task using ProjectPlanner
                success, result = self.project_planner.create_new_task(
                    title=title,
                    priority=priority,
                    due_date=due_date,
                    content=description
                )
                
                if success:
                    print(f"\n{Fore.GREEN}✅ Task created successfully!{Style.RESET_ALL}")
                    print(f"   Task ID: {Fore.CYAN}{result}{Style.RESET_ALL}")
                    print(f"   Title: {title}")
                    print(f"   Priority: {priority.title()}")
                    if due_date:
                        print(f"   Due Date: {due_date}")
                else:
                    print(f"{Fore.RED}❌ Failed to create task: {result}{Style.RESET_ALL}")
                    
            # Basic fallback using TaskManager directly
            elif self.task_manager:
                title = input(f"{Fore.GREEN}Task title: {Style.RESET_ALL}").strip()
                if title:
                    description = input(f"{Fore.GREEN}Description (optional): {Style.RESET_ALL}").strip()
                    
                    # Use TaskManager.create_task with proper arguments
                    from ..project_management.task_manager import TaskPriority, TaskStatus
                    
                    task = self.task_manager.create_task(
                        title=title,
                        content=description,
                        priority=TaskPriority.MEDIUM,
                        status=TaskStatus.TODO
                    )
                    
                    if task:
                        print(f"{Fore.GREEN}✅ Created task: {task.task_id} - {title}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Failed to create task{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Task creation cancelled.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Task management not available.{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Task creation error: {e}")
            print(f"{Fore.RED}Error creating task: {e}{Style.RESET_ALL}")
            
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_quick_view_tasks(self) -> None:
        """Handle quick view tasks option - Enhanced with better task display."""
        print(f"\n{Fore.CYAN}👀 Quick View Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        if self.task_manager:
            try:
                all_tasks = self.task_manager.get_all_tasks()
                
                # Count total tasks
                total_tasks = sum(len(tasks) for tasks in all_tasks.values())
                
                if total_tasks > 0:
                    print(f"{Fore.GREEN}📊 Found {total_tasks} tasks:{Style.RESET_ALL}\n")
                    
                    # Status icons for better display
                    status_icons = {
                        'backlog': '📦',
                        'todo': '📝',
                        'inprogress': '🔄',
                        'testing': '🧪',
                        'devdone': '✅',
                        'done': '🎉'
                    }
                    
                    # Priority icons
                    priority_icons = {
                        'critical': '🔥',
                        'high': '🔴',
                        'medium': '🟡',
                        'low': '🟢'
                    }
                    
                    task_count = 0
                    for status, tasks in all_tasks.items():
                        if tasks:
                            status_icon = status_icons.get(status, '📄')
                            print(f"{status_icon} {Fore.YELLOW}{status.upper()} ({len(tasks)} tasks):{Style.RESET_ALL}")
                            
                            for task in tasks[:5]:  # Show max 5 per status
                                task_count += 1
                                if task_count > 15:  # Limit total display to 15 tasks
                                    break
                                
                                # Get task attributes safely
                                priority = getattr(task, 'priority', None)
                                if hasattr(priority, 'value'):
                                    priority_str = priority.value
                                else:
                                    priority_str = str(priority) if priority else 'medium'
                                
                                priority_icon = priority_icons.get(priority_str.lower(), '⚪')
                                
                                # Display task
                                title = getattr(task, 'title', 'Untitled')
                                task_id = getattr(task, 'task_id', 'No ID')
                                
                                print(f"  {priority_icon} [{Fore.CYAN}{task_id}{Style.RESET_ALL}] {title[:50]}")
                                
                                # Show due date if available
                                if hasattr(task, 'due_date') and task.due_date:
                                    print(f"      📅 Due: {task.due_date}")
                            
                            if len(tasks) > 5:
                                print(f"      {Fore.DIM}... and {len(tasks) - 5} more{Style.RESET_ALL}")
                            print()
                    
                    if task_count >= 15 and total_tasks > 15:
                        print(f"{Fore.YELLOW}... showing first 15 of {total_tasks} tasks{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}💡 Use option 12 to search for specific tasks{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No tasks found.{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}💡 Create your first task using option 10!{Style.RESET_ALL}")
                    
            except Exception as e:
                self.logger.error(f"Task viewing error: {e}")
                print(f"{Fore.RED}Error loading tasks: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Task management not available.{Style.RESET_ALL}")
            
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_search_tasks(self) -> None:
        """Handle search tasks option - Enhanced with better search capabilities."""
        print(f"\n{Fore.CYAN}🔍 Search Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        if self.task_manager:
            try:
                query = input(f"{Fore.GREEN}Search query (title/content): {Style.RESET_ALL}").strip()
                if not query:
                    print(f"{Fore.YELLOW}Search cancelled.{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    return
                
                # Try to use TaskManager search method if available
                matching_tasks = []
                if hasattr(self.task_manager, 'search_tasks'):
                    matching_tasks = self.task_manager.search_tasks(query, search_content=True)
                else:
                    # Fallback: Manual search through all tasks
                    all_tasks = self.task_manager.get_all_tasks()
                    
                    for tasks in all_tasks.values():
                        for task in tasks:
                            # Search in title
                            title = getattr(task, 'title', '').lower()
                            
                            # Search in content/description if available
                            content = ''
                            if hasattr(task, 'content'):
                                content = getattr(task, 'content', '').lower()
                            elif hasattr(task, 'description'):
                                content = getattr(task, 'description', '').lower()
                            
                            # Search in task ID
                            task_id = getattr(task, 'task_id', '').lower()
                            
                            if (query.lower() in title or 
                                query.lower() in content or 
                                query.lower() in task_id):
                                matching_tasks.append(task)
                
                if matching_tasks:
                    print(f"\n{Fore.GREEN}🎯 Found {len(matching_tasks)} matching tasks:{Style.RESET_ALL}")
                    
                    # Status and priority icons
                    status_icons = {
                        'backlog': '📦', 'todo': '📝', 'inprogress': '🔄',
                        'testing': '🧪', 'devdone': '✅', 'done': '🎉'
                    }
                    priority_icons = {
                        'critical': '🔥', 'high': '🔴', 'medium': '🟡', 'low': '🟢'
                    }
                    
                    for i, task in enumerate(matching_tasks[:10], 1):  # Show max 10 results
                        # Get task attributes safely
                        title = getattr(task, 'title', 'Untitled')
                        task_id = getattr(task, 'task_id', 'No ID')
                        
                        # Status
                        status = getattr(task, 'status', None)
                        if hasattr(status, 'value'):
                            status_str = status.value
                        else:
                            status_str = str(status) if status else 'unknown'
                        status_icon = status_icons.get(status_str, '📄')
                        
                        # Priority
                        priority = getattr(task, 'priority', None)
                        if hasattr(priority, 'value'):
                            priority_str = priority.value
                        else:
                            priority_str = str(priority) if priority else 'medium'
                        priority_icon = priority_icons.get(priority_str.lower(), '⚪')
                        
                        print(f"  {i:2}. {status_icon} {priority_icon} [{Fore.CYAN}{task_id}{Style.RESET_ALL}] {title[:60]}")
                        print(f"      Status: {status_str.title()} | Priority: {priority_str.title()}")
                        
                        # Show due date if available
                        if hasattr(task, 'due_date') and task.due_date:
                            print(f"      📅 Due: {task.due_date}")
                        
                        # Show assigned to if available
                        if hasattr(task, 'assigned_to') and task.assigned_to:
                            print(f"      👤 Assigned: {task.assigned_to}")
                        
                        print()
                    
                    if len(matching_tasks) > 10:
                        print(f"{Fore.YELLOW}... and {len(matching_tasks) - 10} more matches{Style.RESET_ALL}")
                        
                else:
                    print(f"\n{Fore.YELLOW}❌ No tasks found matching '{query}'.{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}💡 Try searching with different keywords or check task titles{Style.RESET_ALL}")
                    
            except Exception as e:
                self.logger.error(f"Task search error: {e}")
                print(f"{Fore.RED}Error searching tasks: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Task management not available.{Style.RESET_ALL}")
            
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_project_cleanup(self) -> None:
        """Handle project cleanup option."""
        print(f"\n{Fore.CYAN}🗑️ Project Cleanup{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Project cleanup functionality available.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will include options to clean index data and reset projects.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def _handle_ai_settings(self) -> None:
        """Handle AI settings option."""
        try:
            from ..ui import AISettingsUI
            from ..settings import AISettingsManager
            
            print(f"\n{Fore.CYAN}🤖 AI Settings Configuration{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            
            # Create AI settings manager and UI
            ai_settings_manager = AISettingsManager()
            ai_settings_ui = AISettingsUI(ai_settings_manager)
            
            # Initialize
            ai_settings_ui.initialize()
            
            # Run the AI settings menu in async context
            asyncio.run(ai_settings_ui.handle_ai_settings_menu())
            
        except Exception as e:
            self.logger.error(f"Error in AI settings: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
