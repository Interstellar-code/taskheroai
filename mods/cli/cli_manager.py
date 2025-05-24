"""
CLI Manager for TaskHero AI - WORKING VERSION

Simple, clean implementation without corrupted formatting.
"""

import asyncio
import os
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
    
    def _perform_initialization(self) -> None:
        """Initialize the CLI manager."""
        # Initialize indexer components if we have a last directory
        if self.settings_manager:
            last_dir = self.settings_manager.get_last_directory()
            if last_dir and os.path.isdir(last_dir):
                try:
                    from ..code.indexer import FileIndexer
                    from ..code.decisions import FileSelector, ProjectAnalyzer
                    
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
                    
        self.logger.info("CLI Manager initialized")
        self.update_status("cli_ready", True)
    
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
        """Handle index code option with improved user experience."""
        print("\n" + Fore.CYAN + "=" * 60 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "           Smart Code Indexing System" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
        
        try:
            # Import required modules
            from ..code.indexer import FileIndexer
            from ..code.decisions import FileSelector, ProjectAnalyzer
            
            # Check current project status first
            if self.indexer:
                self._display_current_project_status()
                action = self._get_indexing_action()
                
                if action == "skip":
                    return
                elif action == "switch":
                    directory = self._get_new_directory()
                    if not directory:
                        return
                elif action == "reindex":
                    directory = self.indexer.root_path
                elif action == "delta":
                    directory = self.indexer.root_path
                else:
                    return
            else:
                # No existing indexer, get directory
                directory = self._get_new_directory()
                if not directory:
                    return
            
            # Initialize or reuse indexer
            if not self.indexer or self.indexer.root_path != directory:
                print(f"\n{Fore.CYAN}🔄 Initializing indexer for: {Style.BRIGHT}{os.path.basename(directory)}{Style.RESET_ALL}")
                self.logger.info(f"Creating indexer for directory: {directory}")
                self.indexer = FileIndexer(directory)
                self.file_selector = FileSelector()
                self.project_analyzer = ProjectAnalyzer(self.indexer)
                
                # Set AI manager dependencies when indexer is created
                if self.ai_manager:
                    self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)
            
            # Check what files need indexing
            print(f"{Fore.CYAN}🔍 Analyzing project for indexing requirements...{Style.RESET_ALL}")
            
            try:
                files_to_process = self.indexer.get_outdated_files()
                indexed_files = self.indexer.get_indexed_files()
                index_status = self.indexer.is_index_complete()
            except Exception as e:
                self.logger.error(f"Error scanning files: {e}")
                files_to_process = []
                indexed_files = []
                index_status = {"complete": False, "reason": str(e)}
            
            # Display comprehensive status
            self._display_indexing_status(directory, files_to_process, indexed_files, index_status)
            
            if files_to_process:
                # Ask for confirmation
                confirmation = input(f"\n{Fore.GREEN}Proceed with indexing {len(files_to_process)} files? (y/N): {Style.RESET_ALL}").strip().lower()
                
                if confirmation not in ['y', 'yes']:
                    print(f"{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
                    return
                
                # Perform indexing
                self._perform_indexing(files_to_process, directory)
                
            else:
                print(f"\n{Fore.GREEN}✓ Project is fully indexed - No action needed!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}📁 You can now use chat or agent mode to interact with your codebase.{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error indexing code: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _display_current_project_status(self) -> None:
        """Display current project indexing status."""
        if not self.indexer:
            return
            
        project_name = os.path.basename(self.indexer.root_path)
        print(f"\n{Fore.YELLOW}📂 Current Project: {Style.BRIGHT}{project_name}{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}Path: {self.indexer.root_path}{Style.RESET_ALL}")
        
        try:
            indexed_files = self.indexer.get_indexed_files()
            outdated_files = self.indexer.get_outdated_files()
            index_status = self.indexer.is_index_complete()
            
            print(f"   {Fore.GREEN}Indexed Files: {Style.BRIGHT}{len(indexed_files)}{Style.RESET_ALL}")
            
            if outdated_files:
                print(f"   {Fore.YELLOW}Delta Files: {Style.BRIGHT}{len(outdated_files)}{Style.RESET_ALL} files need updating")
            else:
                print(f"   {Fore.GREEN}Status: {Style.BRIGHT}✓ Up to date{Style.RESET_ALL}")
                
            # Show sample files if there are many
            if len(indexed_files) > 5:
                sample_files = [os.path.basename(f) for f in indexed_files[:3]]
                print(f"   {Fore.CYAN}Sample Files: {', '.join(sample_files)}...{Style.RESET_ALL}")
            elif indexed_files:
                sample_files = [os.path.basename(f) for f in indexed_files[:5]]
                print(f"   {Fore.CYAN}Files: {', '.join(sample_files)}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"   {Fore.RED}Error getting project status: {e}{Style.RESET_ALL}")
    
    def _get_indexing_action(self) -> str:
        """Get user's choice for indexing action."""
        try:
            outdated_files = self.indexer.get_outdated_files()
            
            print(f"\n{Fore.CYAN}Available Actions:{Style.RESET_ALL}")
            
            if outdated_files:
                print(f"   {Fore.GREEN}1.{Style.RESET_ALL} Index delta ({len(outdated_files)} new/changed files)")
            else:
                print(f"   {Fore.GREEN}1.{Style.RESET_ALL} Index delta (no changes detected)")
                
            print(f"   {Fore.GREEN}2.{Style.RESET_ALL} Switch to different project")
            print(f"   {Fore.GREEN}3.{Style.RESET_ALL} Force reindex all files")
            print(f"   {Fore.GREEN}0.{Style.RESET_ALL} Cancel")
            
            choice = input(f"\n{Fore.GREEN}Choose action (1-3, 0=cancel): {Style.RESET_ALL}").strip()
            
            if choice == "1":
                return "delta" if outdated_files else "skip"
            elif choice == "2":
                return "switch"
            elif choice == "3":
                return "reindex"
            else:
                return "skip"
                
        except Exception as e:
            self.logger.error(f"Error getting indexing action: {e}")
            return "skip"
    
    def _get_new_directory(self) -> Optional[str]:
        """Get directory path from user."""
        last_dir = ""
        if self.settings_manager:
            last_dir = self.settings_manager.get_last_directory()
            
        default_dir = last_dir if last_dir else os.getcwd()
        
        print(f"\n{Fore.YELLOW}Enter directory path:")
        print(f"   {Fore.CYAN}Default: {default_dir}{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}Current: {os.getcwd()}{Style.RESET_ALL}")
        
        directory = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip()
        
        if not directory:
            directory = default_dir
            
        if not os.path.isdir(directory):
            print(f"{Fore.RED}Error: '{directory}' is not a valid directory.{Style.RESET_ALL}")
            return None
            
        return directory
    
    def _display_indexing_status(self, directory: str, files_to_process: List[str], 
                                indexed_files: List[str], index_status: Dict[str, Any]) -> None:
        """Display comprehensive indexing status."""
        project_name = os.path.basename(directory)
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📋 Project Analysis: {Style.BRIGHT}{project_name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📁 Directory: {Style.BRIGHT}{directory}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📚 Already Indexed: {Style.BRIGHT}{len(indexed_files)}{Style.NORMAL} files{Style.RESET_ALL}")
        
        if files_to_process:
            print(f"{Fore.YELLOW}🔄 Need Processing: {Style.BRIGHT}{len(files_to_process)}{Style.NORMAL} files{Style.RESET_ALL}")
            
            # Show breakdown of what needs processing
            if len(files_to_process) <= 10:
                print(f"   {Fore.CYAN}Files to process:{Style.RESET_ALL}")
                for file_path in files_to_process:
                    print(f"     {Fore.CYAN}- {os.path.basename(file_path)}{Style.RESET_ALL}")
            else:
                print(f"   {Fore.CYAN}Sample files to process:{Style.RESET_ALL}")
                for file_path in files_to_process[:5]:
                    print(f"     {Fore.CYAN}- {os.path.basename(file_path)}{Style.RESET_ALL}")
                print(f"     {Fore.CYAN}... and {len(files_to_process) - 5} more{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Status: {Style.BRIGHT}All files are up to date{Style.RESET_ALL}")
        
        # Show index status details
        if not index_status.get("complete", False):
            reason = index_status.get("reason", "Unknown")
            print(f"{Fore.YELLOW}ℹ️  Reason: {reason}{Style.RESET_ALL}")
            
            missing_count = index_status.get("missing_count", 0)
            outdated_count = index_status.get("outdated_count", 0)
            ignored_count = index_status.get("ignored_count", 0)
            
            if missing_count > 0:
                print(f"   {Fore.CYAN}Missing from index: {missing_count} files{Style.RESET_ALL}")
            if outdated_count > 0:
                print(f"   {Fore.CYAN}Outdated files: {outdated_count} files{Style.RESET_ALL}")
            if ignored_count > 0:
                print(f"   {Fore.CYAN}Ignored files: {ignored_count} files{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def _perform_indexing(self, files_to_process: List[str], directory: str) -> None:
        """Perform the actual indexing with progress tracking."""
        print(f"\n{Fore.GREEN}🚀 Starting indexing process...{Style.RESET_ALL}")
        
        # Simple progress tracking
        indexed_count = 0
        start_time = time.time()
        
        def progress_callback():
            nonlocal indexed_count
            indexed_count += 1
            percent = int((indexed_count / len(files_to_process)) * 100)
            elapsed = time.time() - start_time
            rate = indexed_count / elapsed if elapsed > 0 else 0
            print(f"\r{Fore.YELLOW}Progress: {percent}% ({indexed_count}/{len(files_to_process)}) | Rate: {rate:.1f} files/sec{Style.RESET_ALL}", end="", flush=True)
            return False
        
        # Index the files
        indexed_files = self.indexer.index_directory(progress_callback)
        elapsed_time = time.time() - start_time
        
        print(f"\n{Fore.GREEN}✅ Indexing completed successfully!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Results:{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}Processed: {Style.BRIGHT}{len(indexed_files)}{Style.NORMAL} files{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}Duration: {Style.BRIGHT}{elapsed_time:.1f}{Style.NORMAL} seconds{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}Rate: {Style.BRIGHT}{len(indexed_files)/elapsed_time:.1f}{Style.NORMAL} files/second{Style.RESET_ALL}")
        
        # Save the directory
        if self.settings_manager:
            self.settings_manager.set_last_directory(directory)
            
        # Update AI manager dependencies after indexing
        if self.ai_manager:
            self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)
            
        self.index_outdated = False
        print(f"\n{Fore.CYAN}🎉 Project is now ready for AI interactions!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📁 Use options 5-7 to chat with your codebase.{Style.RESET_ALL}")
    
    def _handle_exit(self) -> None:
        """Handle exit option."""
        self.running = False
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
    
    # Placeholder methods for options 2-7 (TASK-014)
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
            try:
                asyncio.run(self.ai_manager.agent_mode())
            except Exception as e:
                self.logger.error(f"Agent mode error: {e}")
                print(f"{Fore.RED}Error in agent mode: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}AI Manager not available.{Style.RESET_ALL}")
            
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    # Placeholder methods for TaskHero Management (8-12)
    def _handle_task_dashboard(self) -> None:
        """Handle task dashboard option."""
        print(f"\n{Fore.CYAN}📋 Task Dashboard{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Task management features are available but need integration.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will show comprehensive task dashboard with filtering and management.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_kanban_board(self) -> None:
        """Handle kanban board option."""
        print(f"\n{Fore.CYAN}📌 Kanban Board{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Kanban board features are available but need integration.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will display visual kanban board for task management.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_quick_create_task(self) -> None:
        """Handle quick create task option."""
        print(f"\n{Fore.CYAN}➕ Quick Create Task{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Task creation features are available but need integration.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will provide quick task creation interface.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_quick_view_tasks(self) -> None:
        """Handle quick view tasks option."""
        print(f"\n{Fore.CYAN}👀 Quick View Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Task viewing features are available but need integration.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will show quick overview of current tasks.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_search_tasks(self) -> None:
        """Handle search tasks option."""
        print(f"\n{Fore.CYAN}🔍 Search Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Task search features are available but need integration.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will provide powerful task search and filtering.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_project_cleanup(self) -> None:
        """Handle project cleanup option."""
        print(f"\n{Fore.CYAN}🗑️ Project Cleanup Manager{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Project cleanup features are available but need integration.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Will provide comprehensive cleanup and reset options.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}") 