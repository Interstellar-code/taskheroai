"""
CLI Manager for TaskHero AI - BACKUP VERSION

This is a backup of the CLI manager before attempting to fix the compressed code issues.
"""

import asyncio
import os
import threading
import time
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
        
                # Project management components (TASK-005)        self.project_planner = None        self.task_manager = None        self.kanban_board = None        self.task_cli = None
    
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
            elif choice == "0":
                self._handle_exit()
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1-13 or 0 to exit.{Style.RESET_ALL}")
                
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
    
    # Rest of methods would continue...
    def _handle_exit(self) -> None:
        """Handle exit option."""
        self.running = False
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
    
        def _handle_view_files(self) -> None:        """Handle view indexed files option."""        if not self.indexer:            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")            return        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)        print(Fore.CYAN + Style.BRIGHT + "Indexed Files" + Style.RESET_ALL)        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)        try:            self.logger.info("[STAT] Viewing indexed files information")            index_status = self.indexer.is_index_complete()            status_str = "Complete" if index_status["complete"] else "Incomplete"            status_color = Fore.GREEN if index_status["complete"] else Fore.YELLOW            print(f"{Fore.CYAN}Index Status: {status_color}{Style.BRIGHT}{status_str}{Style.RESET_ALL}")            if not index_status["complete"] and "reason" in index_status:                print(f"{Fore.YELLOW}Reason: {index_status['reason']}{Style.RESET_ALL}")            index_dir = self.indexer.index_dir            print(f"\n{Fore.CYAN}Index Directory: {Fore.WHITE}{index_dir}{Style.RESET_ALL}")            if os.path.exists(index_dir):                metadata_dir = os.path.join(index_dir, "metadata")                embeddings_dir = os.path.join(index_dir, "embeddings")                descriptions_dir = os.path.join(index_dir, "descriptions")                print(f"\n{Fore.CYAN}{Style.BRIGHT}Index Directory Structure:{Style.RESET_ALL}")                header = f"  {Fore.CYAN}{'Directory':<15} {'Exists':<10} {'Files':<10} {'Size':<10}{Style.RESET_ALL}"                separator = f"  {Fore.CYAN}{'-'*15} {'-'*10} {'-'*10} {'-'*10}{Style.RESET_ALL}"                print(header)                print(separator)                if os.path.exists(metadata_dir):                    files = [f for f in os.listdir(metadata_dir) if f.endswith(".json")]                    size = sum(os.path.getsize(os.path.join(metadata_dir, f)) for f in files)                    print(                        f"  {Fore.GREEN}{'metadata':<15} {Fore.GREEN}{'Yes':<10} {Fore.YELLOW}{len(files):<10} {Fore.MAGENTA}{self._format_size(size):<10}{Style.RESET_ALL}"                    )                else:                    print(                        f"  {Fore.GREEN}{'metadata':<15} {Fore.RED}{'No':<10} {'-':<10} {'-':<10}{Style.RESET_ALL}"                    )                if os.path.exists(embeddings_dir):                    files = [f for f in os.listdir(embeddings_dir) if f.endswith(".json")]                    size = sum(os.path.getsize(os.path.join(embeddings_dir, f)) for f in files)                    print(                        f"  {Fore.GREEN}{'embeddings':<15} {Fore.GREEN}{'Yes':<10} {Fore.YELLOW}{len(files):<10} {Fore.MAGENTA}{self._format_size(size):<10}{Style.RESET_ALL}"                    )                else:                    print(                        f"  {Fore.GREEN}{'embeddings':<15} {Fore.RED}{'No':<10} {'-':<10} {'-':<10}{Style.RESET_ALL}"                    )                if os.path.exists(descriptions_dir):                    files = [f for f in os.listdir(descriptions_dir) if f.endswith(".txt")]                    size = sum(os.path.getsize(os.path.join(descriptions_dir, f)) for f in files)                    print(                        f"  {Fore.GREEN}{'descriptions':<15} {Fore.GREEN}{'Yes':<10} {Fore.YELLOW}{len(files):<10} {Fore.MAGENTA}{self._format_size(size):<10}{Style.RESET_ALL}"                    )                else:                    print(                        f"  {Fore.GREEN}{'descriptions':<15} {Fore.RED}{'No':<10} {'-':<10} {'-':<10}{Style.RESET_ALL}"                    )            else:                print(f"{Fore.RED}Index directory does not exist.{Style.RESET_ALL}")            print(f"\n{Fore.CYAN}{Style.BRIGHT}Sample Indexed Files:{Style.RESET_ALL}")            try:                sample_files = self.indexer.get_sample_files(5)                if sample_files:                    for i, file in enumerate(sample_files, 1):                        print(f"{Fore.GREEN}{i}. {Fore.WHITE}{file}{Style.RESET_ALL}")                else:                    print(f"{Fore.YELLOW}No files have been indexed yet.{Style.RESET_ALL}")            except Exception as e:                print(f"{Fore.RED}Error retrieving sample files: {e}{Style.RESET_ALL}")            print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")            input()        except Exception as e:            self.logger.error(f"Error viewing indexed files: {e}", exc_info=True)            print(f"{Fore.RED}{Style.BRIGHT}Error viewing indexed files: {e}{Style.RESET_ALL}")            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
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
        """Handle quick create task option."""
        print(f"\n{Fore.CYAN}➕ Quick Create Task{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        if self.task_manager:
            try:
                title = input(f"{Fore.GREEN}Task title: {Style.RESET_ALL}").strip()
                if title:
                    description = input(f"{Fore.GREEN}Description (optional): {Style.RESET_ALL}").strip()
                    
                    task_data = {
                        'title': title,
                        'description': description if description else '',
                        'status': 'todo',
                        'priority': 'medium'
                    }
                    
                    task = self.task_manager.create_task(task_data)
                    print(f"{Fore.GREEN}✓ Created task: {title}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Task creation cancelled.{Style.RESET_ALL}")
                    
            except Exception as e:
                self.logger.error(f"Task creation error: {e}")
                print(f"{Fore.RED}Error creating task: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Task management not available.{Style.RESET_ALL}")
            
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_quick_view_tasks(self) -> None:
        """Handle quick view tasks option."""
        print(f"\n{Fore.CYAN}👀 Quick View Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        if self.task_manager:
            try:
                tasks = self.task_manager.get_all_tasks()
                if tasks:
                    for i, task in enumerate(tasks[:10], 1):  # Show max 10 tasks
                        status = task.get('status', 'unknown')
                        title = task.get('title', 'Untitled')
                        print(f"{Fore.CYAN}{i:2}. [{status.upper()}] {title}{Style.RESET_ALL}")
                        
                    if len(tasks) > 10:
                        print(f"{Fore.YELLOW}... and {len(tasks) - 10} more tasks{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No tasks found.{Style.RESET_ALL}")
                    
            except Exception as e:
                self.logger.error(f"Task viewing error: {e}")
                print(f"{Fore.RED}Error loading tasks: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Task management not available.{Style.RESET_ALL}")
            
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_search_tasks(self) -> None:
        """Handle search tasks option."""
        print(f"\n{Fore.CYAN}🔍 Search Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        if self.task_manager:
            try:
                query = input(f"{Fore.GREEN}Search query: {Style.RESET_ALL}").strip()
                if query:
                    # Simple search in title and description
                    all_tasks = self.task_manager.get_all_tasks()
                    matching_tasks = []
                    
                    for task in all_tasks:
                        title = task.get('title', '').lower()
                        description = task.get('description', '').lower()
                        if query.lower() in title or query.lower() in description:
                            matching_tasks.append(task)
                    
                    if matching_tasks:
                        print(f"\n{Fore.GREEN}Found {len(matching_tasks)} matching tasks:{Style.RESET_ALL}")
                        for i, task in enumerate(matching_tasks, 1):
                            status = task.get('status', 'unknown')
                            title = task.get('title', 'Untitled')
                            print(f"{Fore.CYAN}{i:2}. [{status.upper()}] {title}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}No tasks found matching '{query}'.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Search cancelled.{Style.RESET_ALL}")
                    
            except Exception as e:
                self.logger.error(f"Task search error: {e}")
                print(f"{Fore.RED}Error searching tasks: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Task management not available.{Style.RESET_ALL}")
            
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_project_cleanup(self) -> None:
        """Handle project cleanup option - Enhanced project cleanup manager."""
        print(f"\n{Fore.CYAN}🗑️ Project Cleanup Manager{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        try:
            # Discover all indexed projects
            indexed_projects = self._discover_indexed_projects()
            
            if not indexed_projects:
                print(f"{Fore.YELLOW}No indexed projects found.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Would you like to clean up logs and settings instead?{Style.RESET_ALL}")
                
                choice = input(f"\n{Fore.YELLOW}Clean up logs and settings? (y/N): {Style.RESET_ALL}").strip().lower()
                if choice == 'y':
                    self._clean_logs_and_settings()
                return
            
            print(f"{Fore.CYAN}Select cleanup option:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}1. {Fore.WHITE}Delete a specific project{Style.RESET_ALL}")
            print(f"{Fore.GREEN}2. {Fore.WHITE}Delete multiple projects{Style.RESET_ALL}")
            print(f"{Fore.RED}3. {Fore.WHITE}Delete ALL projects and reset everything{Style.RESET_ALL}")
            print(f"{Fore.GREEN}4. {Fore.WHITE}Clean up logs and settings only{Style.RESET_ALL}")
            print(f"{Fore.GREEN}0. {Fore.WHITE}Cancel{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.YELLOW}Enter your choice (0-4): {Style.RESET_ALL}").strip()
            
            if choice == "0":
                print(f"{Fore.GREEN}✓ Operation cancelled.{Style.RESET_ALL}")
                return
            elif choice == "1":
                self._delete_specific_project(indexed_projects)
            elif choice == "2":
                self._delete_multiple_projects(indexed_projects)
            elif choice == "3":
                self._delete_all_projects_and_reset()
            elif choice == "4":
                self._clean_logs_and_settings()
            else:
                print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
                
        except (ValueError, KeyboardInterrupt):
            print(f"{Fore.GREEN}✓ Operation cancelled.{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"Project cleanup error: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _discover_indexed_projects(self) -> list:
        """Discover all indexed projects by scanning for .index directories."""
        import os
        projects = []
        
        # Check current directory
        if os.path.exists(".index"):
            projects.append({
                "name": os.path.basename(os.getcwd()),
                "path": os.getcwd(),
                "index_dir": ".index",
                "type": "current"
            })
        
        # Check recent projects from settings manager
        if self.settings_manager:
            last_dir = self.settings_manager.get_last_directory()
            if last_dir and os.path.isdir(last_dir):
                index_dir = os.path.join(last_dir, ".index")
                if os.path.exists(index_dir):
                    # Check if already added
                    if not any(p["path"] == last_dir for p in projects):
                        projects.append({
                            "name": os.path.basename(last_dir),
                            "path": last_dir,
                            "index_dir": index_dir,
                            "type": "recent"
                        })
        
        # Sort by name for consistent display
        projects.sort(key=lambda x: x["name"].lower())
        return projects
    
    def _delete_specific_project(self, projects: list) -> None:
        """Delete a specific indexed project."""
        print(f"\n{Fore.CYAN}Select project to delete:{Style.RESET_ALL}")
        
        for i, project in enumerate(projects, 1):
            project_type = "📂" if project["type"] == "current" else "📁"
            print(f"{Fore.GREEN}{i}. {project_type} {Fore.WHITE}{project['name']} {Fore.CYAN}({project['path']}){Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}0. {Fore.WHITE}Cancel{Style.RESET_ALL}")
        
        try:
            choice = input(f"\n{Fore.YELLOW}Enter project number (0-{len(projects)}): {Style.RESET_ALL}").strip()
            
            if choice == "0":
                return
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(projects):
                project = projects[choice_idx]
                self._confirm_and_delete_project(project)
            else:
                print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
                
        except ValueError:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
    
    def _delete_multiple_projects(self, projects: list) -> None:
        """Delete multiple selected projects."""
        print(f"\n{Fore.CYAN}Select projects to delete (comma-separated numbers):{Style.RESET_ALL}")
        
        for i, project in enumerate(projects, 1):
            project_type = "📂" if project["type"] == "current" else "📁"
            print(f"{Fore.GREEN}{i}. {project_type} {Fore.WHITE}{project['name']} {Fore.CYAN}({project['path']}){Style.RESET_ALL}")
        
        try:
            choices = input(f"\n{Fore.YELLOW}Enter project numbers (e.g., 1,3,5) or 'all': {Style.RESET_ALL}").strip()
            
            if not choices:
                return
            
            if choices.lower() == 'all':
                selected_projects = projects
            else:
                choice_numbers = [int(x.strip()) for x in choices.split(',')]
                selected_projects = []
                for num in choice_numbers:
                    if 1 <= num <= len(projects):
                        selected_projects.append(projects[num - 1])
                    else:
                        print(f"{Fore.YELLOW}Warning: Invalid project number {num} ignored.{Style.RESET_ALL}")
            
            if not selected_projects:
                print(f"{Fore.YELLOW}No valid projects selected.{Style.RESET_ALL}")
                return
            
            # Show what will be deleted
            print(f"\n{Fore.YELLOW}Projects to delete:{Style.RESET_ALL}")
            for project in selected_projects:
                print(f"  {Fore.RED}❌ {project['name']} ({project['path']}){Style.RESET_ALL}")
            
            confirm = input(f"\n{Fore.RED}Delete {len(selected_projects)} project(s)? Type 'DELETE' to confirm: {Style.RESET_ALL}").strip()
            
            if confirm == "DELETE":
                self._delete_projects_batch(selected_projects)
            else:
                print(f"{Fore.GREEN}✓ Operation cancelled.{Style.RESET_ALL}")
                
        except ValueError:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
    
    def _confirm_and_delete_project(self, project: dict) -> None:
        """Confirm and delete a single project."""
        print(f"\n{Fore.YELLOW}⚠️  WARNING: This will permanently delete the index for:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Project: {Fore.WHITE}{project['name']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Path: {Fore.WHITE}{project['path']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Index: {Fore.WHITE}{project['index_dir']}{Style.RESET_ALL}")
        
        # Show what will be deleted
        index_size = self._get_directory_size(project['index_dir'])
        print(f"{Fore.CYAN}Size: {Fore.WHITE}{self._format_size(index_size)}{Style.RESET_ALL}")
        
        print(f"\n{Fore.RED}⚠️  This action cannot be undone!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}The source code will NOT be deleted, only the index data.{Style.RESET_ALL}")
        
        confirm = input(f"\n{Fore.YELLOW}Delete this project's index? Type 'DELETE' to confirm: {Style.RESET_ALL}").strip()
        
        if confirm == "DELETE":
            success = self._delete_project_index(project)
            if success:
                # Reset current app state if this is the active project
                if (self.indexer and 
                    hasattr(self.indexer, 'root_path') and 
                    self.indexer.root_path == project['path']):
                    self._reset_app_state()
        else:
            print(f"{Fore.GREEN}✓ Operation cancelled.{Style.RESET_ALL}")
    
    def _delete_projects_batch(self, projects: list) -> None:
        """Delete multiple projects."""
        print(f"\n{Fore.YELLOW}🗑️  Deleting {len(projects)} project(s)...{Style.RESET_ALL}")
        
        deleted_count = 0
        errors = []
        
        for project in projects:
            try:
                if self._delete_project_index(project, show_progress=False):
                    deleted_count += 1
                    print(f"{Fore.GREEN}✓ Deleted: {project['name']}{Style.RESET_ALL}")
                else:
                    errors.append(f"Failed to delete: {project['name']}")
            except Exception as e:
                errors.append(f"Error deleting {project['name']}: {e}")
        
        # Reset app state if current project was deleted
        if (self.indexer and hasattr(self.indexer, 'root_path') and 
            any(p['path'] == self.indexer.root_path for p in projects)):
            self._reset_app_state()
        
        # Show results
        print(f"\n{Fore.CYAN}Deletion complete: {Fore.GREEN}{deleted_count} projects deleted{Style.RESET_ALL}")
        if errors:
            print(f"{Fore.YELLOW}Errors: {len(errors)}{Style.RESET_ALL}")
            for error in errors:
                print(f"  {Fore.RED}❌ {error}{Style.RESET_ALL}")
    
    def _delete_all_projects_and_reset(self) -> None:
        """Delete all projects and reset everything (original clean slate functionality)."""
        print(f"\n{Fore.RED}⚠️  WARNING: This will permanently delete ALL generated data!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}The following will be deleted:{Style.RESET_ALL}")
        
        # List what will be deleted
        items_to_delete = []
        
        # Check for .index directories in current directory and any indexed project
        if self.indexer:
            index_dir = getattr(self.indexer, 'index_dir', '.index')
            if os.path.exists(index_dir):
                items_to_delete.append(f"📁 {index_dir}/ (index data)")
        
        # Check for .index in current directory
        current_index = ".index"
        if os.path.exists(current_index):
            items_to_delete.append(f"📁 {current_index}/ (current directory index)")
        
        # Check for logs directory
        logs_dir = "logs"
        if os.path.exists(logs_dir):
            log_files = []
            try:
                for file in os.listdir(logs_dir):
                    if file.endswith(('.log', '.txt')):
                        log_files.append(file)
            except (PermissionError, OSError):
                log_files = ["(unable to list files)"]
            
            if log_files:
                items_to_delete.append(f"📁 {logs_dir}/ ({len(log_files)} log files)")
        
        # Check for settings file
        settings_path = ".app_settings.json"
        if os.path.exists(settings_path):
            items_to_delete.append(f"📄 {os.path.basename(settings_path)} (app settings)")
        
        if not items_to_delete:
            print(f"{Fore.GREEN}✓ No generated files found to delete.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}The application state is already clean.{Style.RESET_ALL}")
            return
        
        for item in items_to_delete:
            print(f"  {Fore.RED}❌ {item}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Additional actions:{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}🔄 Reset application state (indexer, chat history, etc.){Style.RESET_ALL}")
        
        print(f"\n{Fore.RED}⚠️  This action cannot be undone!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}You will need to re-index your projects after this operation.{Style.RESET_ALL}")
        
        # Get confirmation
        confirmation = input(f"\n{Fore.YELLOW}Are you absolutely sure you want to proceed? Type 'DELETE' to confirm: {Style.RESET_ALL}").strip()
        
        if confirmation != "DELETE":
            print(f"{Fore.GREEN}✓ Operation cancelled. No files were deleted.{Style.RESET_ALL}")
            return
        
        # Final confirmation
        final_confirm = input(f"{Fore.RED}Last chance! Type 'YES' to permanently delete all data: {Style.RESET_ALL}").strip().upper()
        
        if final_confirm != "YES":
            print(f"{Fore.GREEN}✓ Operation cancelled. No files were deleted.{Style.RESET_ALL}")
            return
        
        # Perform the deletion
        print(f"\n{Fore.YELLOW}🗑️  Deleting files...{Style.RESET_ALL}")
        
        deleted_count = 0
        errors = []
        
        try:
            import shutil
            
            # Delete index directories
            for item in [".index"]:
                if os.path.exists(item):
                    try:
                        shutil.rmtree(item)
                        print(f"{Fore.GREEN}✓ Deleted: {item}/{Style.RESET_ALL}")
                        deleted_count += 1
                    except Exception as e:
                        errors.append(f"Failed to delete {item}/: {e}")
            
            # Delete indexer-specific index directory if different
            if self.indexer and hasattr(self.indexer, 'index_dir'):
                index_dir = self.indexer.index_dir
                if os.path.exists(index_dir) and index_dir != ".index":
                    try:
                        shutil.rmtree(index_dir)
                        print(f"{Fore.GREEN}✓ Deleted: {index_dir}/{Style.RESET_ALL}")
                        deleted_count += 1
                    except Exception as e:
                        errors.append(f"Failed to delete {index_dir}/: {e}")
            
            # Delete logs directory
            if os.path.exists("logs"):
                try:
                    shutil.rmtree("logs")
                    print(f"{Fore.GREEN}✓ Deleted: logs/{Style.RESET_ALL}")
                    deleted_count += 1
                except Exception as e:
                    errors.append(f"Failed to delete logs/: {e}")
            
            # Delete settings file
            if os.path.exists(".app_settings.json"):
                try:
                    os.remove(".app_settings.json")
                    print(f"{Fore.GREEN}✓ Deleted: .app_settings.json{Style.RESET_ALL}")
                    deleted_count += 1
                except Exception as e:
                    errors.append(f"Failed to delete .app_settings.json: {e}")
            
            # Reset application state
            self._reset_app_state()
            print(f"{Fore.GREEN}✓ Reset application state{Style.RESET_ALL}")
            
        except Exception as e:
            errors.append(f"Unexpected error during cleanup: {e}")
        
        # Show results
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🧹 Clean Slate Results:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Successfully deleted {deleted_count} items{Style.RESET_ALL}")
        
        if errors:
            print(f"{Fore.YELLOW}⚠️  {len(errors)} errors occurred:{Style.RESET_ALL}")
            for error in errors:
                print(f"  {Fore.RED}❌ {error}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✓ Clean slate complete! The application has been reset.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}You can now index new projects using option 1.{Style.RESET_ALL}")
    
    def _clean_logs_and_settings(self) -> None:
        """Clean up logs and settings only."""
        print(f"\n{Fore.CYAN}Cleaning up logs and settings...{Style.RESET_ALL}")
        
        deleted_count = 0
        errors = []
        
        # Delete logs directory
        if os.path.exists("logs"):
            try:
                import shutil
                shutil.rmtree("logs")
                print(f"{Fore.GREEN}✓ Deleted: logs/{Style.RESET_ALL}")
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete logs/: {e}")
        
        # Delete settings file
        if os.path.exists(".app_settings.json"):
            try:
                os.remove(".app_settings.json")
                print(f"{Fore.GREEN}✓ Deleted: .app_settings.json{Style.RESET_ALL}")
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete .app_settings.json: {e}")
        
        print(f"\n{Fore.GREEN}✓ Cleanup complete: {deleted_count} items deleted{Style.RESET_ALL}")
        if errors:
            print(f"{Fore.YELLOW}Errors: {len(errors)}{Style.RESET_ALL}")
            for error in errors:
                print(f"  {Fore.RED}❌ {error}{Style.RESET_ALL}")
    
    def _delete_project_index(self, project: dict, show_progress: bool = True) -> bool:
        """Delete a project's index directory."""
        try:
            import shutil
            index_dir = project['index_dir']
            if os.path.exists(index_dir):
                shutil.rmtree(index_dir)
                if show_progress:
                    print(f"{Fore.GREEN}✓ Deleted project index: {project['name']}{Style.RESET_ALL}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete project index {project['name']}: {e}")
            return False
    
    def _reset_app_state(self) -> None:
        """Reset application state."""
        self.indexer = None
        self.index_outdated = False
        self.file_selector = None
        self.project_analyzer = None
        self.chat_handler = None
        
        # Reset AI manager dependencies if available
        if self.ai_manager:
            self.ai_manager.set_dependencies(None, None, None)
            
        self.logger.info("Application state reset")
    
    def _get_directory_size(self, directory: str) -> int:
        """Get the total size of a directory."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, IOError):
                        pass
        except (OSError, IOError):
            pass
        return total_size
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}") 