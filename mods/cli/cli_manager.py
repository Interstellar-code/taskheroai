"""
CLI Manager for TaskHero AI.

Handles command-line interface functionality and main application loop.
Integrates with TASK-005 Enhanced CLI features.
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
        """Handle user menu choice."""
        try:
            if choice == "1":
                self._handle_index_code()
            elif choice == "2":
                self._handle_chat_ai()
            elif choice == "3":
                self._handle_max_chat()
            elif choice == "4":
                self._handle_agent_mode()
            elif choice == "5":
                self._handle_view_files()
            elif choice == "6":
                self._handle_view_project()
            elif choice == "7":
                self._handle_recent_projects()
            elif choice == "8":
                self._handle_task_dashboard()
            elif choice == "9":
                self._handle_toggle_markdown()
            elif choice == "10":
                self._handle_toggle_thinking()
            elif choice == "11":
                self._handle_clear_screen()
            elif choice == "12":
                self._handle_exit()
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1-12.{Style.RESET_ALL}")
                
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
                    
                self.index_outdated = False
                print(f"{Fore.GREEN}✓ Indexing completed successfully!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}📁 You can now use chat or agent mode to interact with your codebase.{Style.RESET_ALL}")
                
            else:
                print(f"{Fore.GREEN}✓ All files are already indexed{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error during indexing: {e}")
            print(f"{Fore.RED}Error during indexing: {e}{Style.RESET_ALL}")
            if "Ollama" in str(e):
                print(f"{Fore.YELLOW}Make sure Ollama is running and accessible at the configured host.{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_chat_ai(self) -> None:
        """Handle chat with AI option."""
        if self.ai_manager:
            self.ai_manager.chat_with_ai(max_chat_mode=False)
        else:
            print(f"{Fore.RED}AI Manager not available{Style.RESET_ALL}")
    
    def _handle_max_chat(self) -> None:
        """Handle max chat mode option."""
        if self.ai_manager:
            self.ai_manager.chat_with_ai(max_chat_mode=True)
        else:
            print(f"{Fore.RED}AI Manager not available{Style.RESET_ALL}")
    
    def _handle_agent_mode(self) -> None:
        """Handle agent mode option."""
        if self.ai_manager:
            asyncio.run(self.ai_manager.agent_mode())
        else:
            print(f"{Fore.RED}AI Manager not available{Style.RESET_ALL}")
    
    def _handle_view_files(self) -> None:
        """Handle view indexed files option."""
        print("📁 View Indexed Files functionality will be implemented in next phase")
        # TODO: Extract from app.py
    
    def _handle_view_project(self) -> None:
        """Handle view project info option."""
        print("📊 View Project Info functionality will be implemented in next phase")
        # TODO: Extract from app.py
    
    def _handle_recent_projects(self) -> None:
        """Handle recent projects option."""
        print("📚 Recent Projects functionality will be implemented in next phase")
        # TODO: Extract from app.py
    
    def _handle_task_dashboard(self) -> None:
        """Handle task management dashboard (TASK-005 enhanced feature)."""
        print(f"{Fore.CYAN}🎯 Task Management Dashboard{Style.RESET_ALL}")
        print("This feature will integrate with TASK-005 Enhanced CLI")
        print("- Quick task creation")
        print("- Task status overview") 
        print("- Kanban board integration")
        # TODO: Integrate with TASK-005 enhanced CLI features
    
    def _handle_toggle_markdown(self) -> None:
        """Handle toggle markdown rendering."""
        if self.settings_manager:
            current = self.settings_manager.get_ui_setting("enable_markdown_rendering", True)
            new_value = not current
            self.settings_manager.set_ui_setting("enable_markdown_rendering", new_value)
            status = f"{Fore.GREEN}Enabled" if new_value else f"{Fore.RED}Disabled"
            print(f"Markdown rendering: {status}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Settings Manager not available{Style.RESET_ALL}")
    
    def _handle_toggle_thinking(self) -> None:
        """Handle toggle thinking blocks."""
        if self.settings_manager:
            current = self.settings_manager.get_ui_setting("show_thinking_blocks", False)
            new_value = not current
            self.settings_manager.set_ui_setting("show_thinking_blocks", new_value)
            status = f"{Fore.GREEN}Enabled" if new_value else f"{Fore.RED}Disabled"
            print(f"Thinking blocks: {status}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Settings Manager not available{Style.RESET_ALL}")
    
    def _handle_clear_screen(self) -> None:
        """Handle clear screen option."""
        if self.ui_manager:
            self.ui_manager.clear_screen()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def _handle_exit(self) -> None:
        """Handle exit option."""
        print(f"{Fore.YELLOW}Exiting TaskHero AI...{Style.RESET_ALL}")
        self.running = False
    
    def set_application_state(self, indexer=None, index_outdated: bool = False):
        """Set application state for CLI operations."""
        self.indexer = indexer
        self.index_outdated = index_outdated
        self.update_status("app_state_set", True)
    
    def _perform_reset(self) -> None:
        """Reset the CLI manager."""
        self.running = False
        self.indexer = None
        self.index_outdated = False
        self.logger.info("CLI manager reset") 