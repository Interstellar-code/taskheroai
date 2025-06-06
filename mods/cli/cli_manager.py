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
from typing import Any, Dict, List, Optional, Tuple
import json

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

        # Git integration (TASK-080)
        self.git_manager = None

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

        # Initialize Git integration (TASK-080)
        self._initialize_git_integration()

        # Pass Git manager to UI manager if available
        if self.ui_manager and self.git_manager:
            self.ui_manager.git_manager = self.git_manager

        self.logger.info("CLI Manager initialized")
        self.update_status("cli_ready", True)

    def _initialize_project_management(self) -> None:
        """Initialize project management components with configurable task storage paths."""
        try:
            from ..project_management.task_manager import TaskManager
            from ..project_management.project_planner import ProjectPlanner
            from ..project_management.kanban_board import KanbanBoard
            from .task_cli import TaskCLI

            # Initialize TaskManager with configurable paths (will read from app_settings.json)
            self.task_manager = TaskManager()

            # Initialize ProjectPlanner with the configured TaskManager
            self.project_planner = ProjectPlanner(task_manager=self.task_manager)

            # Initialize KanbanBoard with the configured TaskManager
            self.kanban_board = KanbanBoard(self.task_manager)

            # Initialize enhanced TaskCLI (TASK-005)
            self.task_cli = TaskCLI(self.settings_manager)

            # Log the task storage path being used
            task_storage_path = self.task_manager.planning_dir
            self.logger.info(f"Project management components initialized with task storage: {task_storage_path}")
            self.logger.info("Enhanced TaskCLI initialized for TASK-005")

        except Exception as e:
            self.logger.warning(f"Project management components not available: {e}")
            # This is not critical, so we continue without PM features

    def _initialize_git_integration(self) -> None:
        """Initialize Git integration components."""
        try:
            from ..git import GitManager

            # Initialize Git manager with settings manager
            self.git_manager = GitManager(self.settings_manager)
            self.git_manager.initialize()

            # Perform startup version check if enabled
            if self.git_manager.is_initialized:
                git_settings = self.git_manager._get_git_settings()
                if git_settings.get("auto_check_enabled", True):
                    try:
                        # Perform background version check
                        update_result = self.git_manager.check_for_updates(force_check=False)
                        if update_result.get("success") and update_result.get("update_available"):
                            self.logger.info("Update available - will be shown in main menu")
                    except Exception as e:
                        self.logger.debug(f"Startup version check failed: {e}")

            self.logger.info("Git integration initialized")

        except Exception as e:
            self.logger.warning(f"Git integration not available: {e}")
            # This is not critical, so we continue without Git features

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
                    # Get update information if Git manager is available
                    update_info = None
                    if self.git_manager:
                        try:
                            status = self.git_manager.get_update_status()
                            update_info = status.get("last_check")
                        except Exception as e:
                            self.logger.debug(f"Error getting update status: {e}")

                    self.ui_manager.set_application_state(self.indexer, self.index_outdated, update_info)
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
            # TaskHero Management Section (8-13)
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
            elif choice == "13":
                self._handle_create_about_document()
            # Settings & Tools Section (14-15)
            elif choice == "14":
                self._handle_project_cleanup()
            elif choice == "15":
                self._handle_ai_settings()
            elif choice == "0":
                self._handle_exit()
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1-15 or 0 to exit.{Style.RESET_ALL}")

        except Exception as e:
            self.logger.error(f"Error handling choice {choice}: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def _handle_index_code(self) -> None:
        """Handle index code option with smart indexing and detailed logging."""
        print("\n" + Fore.CYAN + "=" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🔍 Smart Code Directory Indexing" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

        try:
            # Import required modules
            from ..code.smart_indexer import SmartIndexer
            from ..code.indexer import FileIndexer
            from ..code.decisions import FileSelector, ProjectAnalyzer
            from ..code.indexing_logger import IndexingLogger, PreIndexingAnalyzer

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

            print(f"{Fore.CYAN}Target directory: {Style.BRIGHT}{directory}{Style.RESET_ALL}")

            # Step 1: Smart indexing analysis
            print(f"\n{Fore.GREEN}🔍 Step 1: Smart indexing analysis...{Style.RESET_ALL}")

            # Get AI provider information
            try:
                from ..code.indexer import _get_ai_provider_info
                ai_info = _get_ai_provider_info()
                print(f"{Fore.MAGENTA}🤖 AI Providers: Descriptions via {ai_info['description_full']}, Embeddings via {ai_info['embedding_full']}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}🤖 AI Provider info unavailable{Style.RESET_ALL}")

            # Initialize smart indexer
            smart_indexer = SmartIndexer(directory)

            # Check current indexing status
            status = smart_indexer.get_indexing_status()
            print(f"{Fore.CYAN}Current Status: {status['overall_status'].upper()}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Message: {status['message']}{Style.RESET_ALL}")

            # Show recommendations
            if status['analysis']['recommendations']:
                print(f"\n{Fore.YELLOW}💡 Smart Recommendations:{Style.RESET_ALL}")
                for rec in status['analysis']['recommendations']:
                    print(f"  • {rec}")

            # Get files that actually need indexing
            files_to_index, analysis_info = smart_indexer.get_files_needing_indexing()
            scan_type = analysis_info.get('scan_type', 'unknown')

            print(f"\n{Fore.CYAN}📊 Smart Analysis Results:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Scan type: {scan_type}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Files needing indexing: {len(files_to_index)}{Style.RESET_ALL}")

            if len(files_to_index) == 0:
                print(f"{Fore.GREEN}✅ All files are up to date! No indexing needed.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            # Show sample files
            if files_to_index:
                print(f"\n{Fore.YELLOW}Sample files to index:{Style.RESET_ALL}")
                for file_path in files_to_index[:10]:  # Show first 10
                    rel_path = os.path.relpath(file_path, directory)
                    print(f"  • {rel_path}")

                if len(files_to_index) > 10:
                    print(f"  ... and {len(files_to_index) - 10} more files")

            # Ask for confirmation
            print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
            confirmation = input(f"{Fore.GREEN}Proceed with smart indexing? (y/N): {Style.RESET_ALL}").strip().lower()

            if confirmation not in ['y', 'yes']:
                print(f"{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            # Step 2: Initialize components for smart indexing
            print(f"\n{Fore.GREEN}🚀 Step 2: Initializing smart indexing components...{Style.RESET_ALL}")

            # Initialize or reuse indexer components
            if not self.indexer or self.indexer.root_path != directory:
                self.logger.info(f"Creating indexer for directory: {directory}")
                self.indexer = smart_indexer.indexer  # Use the smart indexer's FileIndexer
                self.file_selector = FileSelector()
                self.project_analyzer = ProjectAnalyzer(self.indexer)

                # Set AI manager dependencies when indexer is created
                if self.ai_manager:
                    self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)

            # Step 3: Perform smart indexing (visual feedback handled by smart_indexer)
            try:
                # Use smart indexing instead of traditional indexing
                result = smart_indexer.smart_index(force_reindex=False)

                if result['status'] == 'no_action_needed':
                    print(f"\n{Fore.GREEN}✅ {result['message']}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}⏱️  Analysis time: {result['processing_time']:.2f} seconds{Style.RESET_ALL}")
                elif result['status'] == 'completed':
                    # Smart indexer already showed detailed progress and completion
                    # Just handle post-processing tasks

                    # Save the directory
                    if self.settings_manager:
                        self.settings_manager.set_last_directory(directory)

                    # Update AI manager dependencies after indexing
                    if self.ai_manager:
                        self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)

                    self.index_outdated = False

                    print(f"\n{Fore.GREEN}🚀 Ready for AI interactions!{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}You can now use chat, max chat, or agent mode to interact with your indexed codebase.{Style.RESET_ALL}")

                elif result['status'] == 'failed':
                    # Smart indexer already showed the error
                    print(f"{Fore.CYAN}⏱️  Time before failure: {result['processing_time']:.2f} seconds{Style.RESET_ALL}")

            except Exception as e:
                print(f"\n{Fore.RED}❌ Error during smart indexing: {str(e)}{Style.RESET_ALL}")
                self.logger.error(f"Smart indexing error: {e}", exc_info=True)

        except Exception as e:
            self.logger.error(f"Error in smart indexing: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def _handle_index_code_old(self) -> None:
        """Handle index code option with pre-analysis and detailed logging (old version)."""
        print("\n" + Fore.CYAN + "=" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🔍 Traditional Code Directory Indexing" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

        try:
            # Import required modules
            from ..code.indexer import FileIndexer
            from ..code.decisions import FileSelector, ProjectAnalyzer
            from ..code.indexing_logger import IndexingLogger, PreIndexingAnalyzer

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

            print(f"{Fore.CYAN}Target directory: {Style.BRIGHT}{directory}{Style.RESET_ALL}")

            # Step 1: Pre-indexing analysis
            print(f"\n{Fore.GREEN}🔍 Step 1: Analyzing directory structure...{Style.RESET_ALL}")

            gitignore_path = os.path.join(directory, '.gitignore')
            if not os.path.exists(gitignore_path):
                gitignore_path = None
                print(f"{Fore.YELLOW}ℹ️  No .gitignore file found - will use default exclusions{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✓ Found .gitignore file{Style.RESET_ALL}")

            # Perform pre-analysis
            analyzer = PreIndexingAnalyzer(directory, gitignore_path)
            analysis = analyzer.analyze()

            # Display pre-analysis results
            self._display_pre_analysis(analysis)

            # Ask for confirmation
            print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
            confirmation = input(f"{Fore.GREEN}Proceed with indexing? (y/N): {Style.RESET_ALL}").strip().lower()

            if confirmation not in ['y', 'yes']:
                print(f"{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            # Step 2: Initialize indexer and logger
            print(f"\n{Fore.GREEN}🚀 Step 2: Initializing indexing components...{Style.RESET_ALL}")

            # Initialize or reuse indexer
            if not self.indexer or self.indexer.root_path != directory:
                self.logger.info(f"Creating indexer for directory: {directory}")
                self.indexer = FileIndexer(directory)
                self.file_selector = FileSelector()
                self.project_analyzer = ProjectAnalyzer(self.indexer)

                # Set AI manager dependencies when indexer is created
                if self.ai_manager:
                    self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)

            # Initialize detailed logger
            indexing_logger = IndexingLogger(directory)
            indexing_logger.log_pre_analysis(analysis)

            print(f"{Fore.GREEN}✓ Indexing logger initialized{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📄 Log file: {indexing_logger.log_file}{Style.RESET_ALL}")

            # Step 3: Get files to process
            print(f"\n{Fore.GREEN}📂 Step 3: Scanning for files to process...{Style.RESET_ALL}")

            try:
                files_to_process = self.indexer.get_outdated_files()
            except Exception as e:
                self.logger.error(f"Error scanning files: {e}")
                files_to_process = []
                indexing_logger.log_file_failed("scan_error", str(e))

            if files_to_process:
                # Step 4: Index files with detailed logging
                print(f"\n{Fore.GREEN}⚡ Step 4: Indexing files...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Files to process: {Style.BRIGHT}{len(files_to_process)}{Style.RESET_ALL}")

                indexed_count = 0
                failed_count = 0
                start_time = time.time()

                def enhanced_progress_callback():
                    nonlocal indexed_count
                    indexed_count += 1
                    percent = int((indexed_count / len(files_to_process)) * 100)
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        rate = indexed_count / elapsed
                        eta = (len(files_to_process) - indexed_count) / rate if rate > 0 else 0
                        print(f"\r{Fore.YELLOW}Progress: {percent}% ({indexed_count}/{len(files_to_process)}) | Rate: {rate:.1f} files/sec | ETA: {eta:.0f}s{Style.RESET_ALL}", end="", flush=True)
                    else:
                        print(f"\r{Fore.YELLOW}Progress: {percent}% ({indexed_count}/{len(files_to_process)}){Style.RESET_ALL}", end="", flush=True)

                    # Log progress periodically
                    if indexed_count % 10 == 0:
                        indexing_logger.log_progress(indexed_count, len(files_to_process))

                    return False

                # Enhanced indexing with detailed logging
                try:
                    indexed_files = []
                    for file_path in files_to_process:
                        try:
                            file_start_time = time.time()

                            # Index the file using proper FileIndexer method
                            metadata = self.indexer.reindex_file(file_path)
                            success = metadata is not None

                            if success:
                                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                                processing_time = time.time() - file_start_time
                                indexing_logger.log_file_indexed(file_path, file_size, processing_time)
                                indexed_files.append(file_path)
                            else:
                                indexing_logger.log_file_failed(file_path, "Indexing failed")
                                failed_count += 1

                        except Exception as file_error:
                            indexing_logger.log_file_failed(file_path, str(file_error))
                            failed_count += 1
                            self.logger.error(f"Error indexing {file_path}: {file_error}")

                        enhanced_progress_callback()

                    print(f"\n{Fore.GREEN}✅ Indexing process completed!{Style.RESET_ALL}")

                except Exception as indexing_error:
                    print(f"\n{Fore.RED}❌ Indexing error: {indexing_error}{Style.RESET_ALL}")
                    indexing_logger.log_file_failed("indexing_process", str(indexing_error))

                # Step 5: Finalize and display results
                print(f"\n{Fore.GREEN}📊 Step 5: Finalizing and generating reports...{Style.RESET_ALL}")

                # Finalize logging
                log_file = indexing_logger.finalize()
                log_summary = indexing_logger.get_log_summary()

                # Display final results
                self._display_indexing_results(log_summary, failed_count)

                # Save the directory
                if self.settings_manager:
                    self.settings_manager.set_last_directory(directory)

                # Update AI manager dependencies after indexing
                if self.ai_manager:
                    self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)

                self.index_outdated = False

            else:
                print(f"{Fore.GREEN}✅ All files are already indexed - no processing needed{Style.RESET_ALL}")
                indexing_logger.finalize()

        except Exception as e:
            self.logger.error(f"Error in enhanced indexing: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def _display_pre_analysis(self, analysis: Dict[str, Any]) -> None:
        """Display pre-indexing analysis results."""
        print(f"\n{Fore.CYAN}📋 Pre-Indexing Analysis Results:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")

        # Overall stats
        total_files = analysis.get('total_files', 0)
        files_to_index = analysis.get('files_to_index', 0)
        files_to_ignore = analysis.get('files_to_ignore', 0)
        total_size = analysis.get('total_size', 0)

        print(f"{Fore.GREEN}📁 Total files found: {Style.BRIGHT}{total_files}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Files to index: {Style.BRIGHT}{files_to_index}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏭️ Files to ignore: {Style.BRIGHT}{files_to_ignore}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Total size to process: {Style.BRIGHT}{self._format_size(total_size)}{Style.RESET_ALL}")

        # Directory breakdown
        directories = analysis.get('directories', {})
        if directories:
            print(f"\n{Fore.CYAN}📂 Directory Breakdown (files to index):{Style.RESET_ALL}")
            sorted_dirs = sorted(directories.items(), key=lambda x: x[1]['file_count'], reverse=True)

            for i, (dir_path, info) in enumerate(sorted_dirs[:10]):  # Show top 10
                file_count = info['file_count']
                if file_count > 0:
                    dir_display = dir_path if dir_path != "." else "(root)"
                    print(f"  {Fore.GREEN}{dir_display:<30}{Style.RESET_ALL}: {Fore.YELLOW}{file_count} files{Style.RESET_ALL}")

            if len(directories) > 10:
                print(f"  {Fore.CYAN}... and {len(directories) - 10} more directories{Style.RESET_ALL}")

        # File types
        file_types = analysis.get('file_types', {})
        if file_types:
            print(f"\n{Fore.CYAN}📄 File Types to Index:{Style.RESET_ALL}")
            sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)

            for i, (file_ext, count) in enumerate(sorted_types[:8]):  # Show top 8
                ext_display = file_ext if file_ext else "(no extension)"
                print(f"  {Fore.CYAN}{ext_display:<15}{Style.RESET_ALL}: {Fore.YELLOW}{count} files{Style.RESET_ALL}")

        # Large files warning
        large_files = analysis.get('large_files', [])
        if large_files:
            print(f"\n{Fore.YELLOW}⚠️  Large Files (>1MB) detected:{Style.RESET_ALL}")
            for large_file in large_files[:3]:  # Show first 3
                size_str = self._format_size(large_file['size'])
                print(f"  {Fore.YELLOW}{large_file['path']:<40}{Style.RESET_ALL}: {Fore.RED}{size_str}{Style.RESET_ALL}")

            if len(large_files) > 3:
                print(f"  {Fore.CYAN}... and {len(large_files) - 3} more large files{Style.RESET_ALL}")

        # Gitignore patterns
        gitignore_patterns = analysis.get('gitignore_patterns', [])
        if gitignore_patterns:
            print(f"\n{Fore.CYAN}🚫 Active .gitignore patterns (first 5):{Style.RESET_ALL}")
            for pattern in gitignore_patterns[:5]:
                print(f"  {Fore.MAGENTA}{pattern}{Style.RESET_ALL}")

    def _display_indexing_results(self, log_summary: Dict[str, Any], failed_count: int) -> None:
        """Display final indexing results."""
        print(f"\n{Fore.CYAN}🎉 Indexing Complete - Final Results:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        stats = log_summary.get('statistics', {})

        # Main statistics
        files_indexed = stats.get('files_indexed', 0)
        files_ignored = stats.get('files_ignored', 0)
        total_size = stats.get('total_size', 0)
        processing_time = stats.get('processing_time', 0)

        print(f"{Fore.GREEN}✅ Files successfully indexed: {Style.BRIGHT}{files_indexed}{Style.RESET_ALL}")
        if failed_count > 0:
            print(f"{Fore.RED}❌ Files failed to index: {Style.BRIGHT}{failed_count}{Style.RESET_ALL}")
        if files_ignored > 0:
            print(f"{Fore.YELLOW}⏭️ Files ignored: {Style.BRIGHT}{files_ignored}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}📊 Total size processed: {Style.BRIGHT}{self._format_size(total_size)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️ Processing time: {Style.BRIGHT}{processing_time:.2f} seconds{Style.RESET_ALL}")

        if processing_time > 0 and files_indexed > 0:
            rate = files_indexed / processing_time
            print(f"{Fore.CYAN}⚡ Average rate: {Style.BRIGHT}{rate:.1f} files/second{Style.RESET_ALL}")

        # File types summary
        file_types = log_summary.get('file_types', {})
        if file_types:
            print(f"\n{Fore.CYAN}📄 File Types Indexed:{Style.RESET_ALL}")
            sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
            for file_ext, count in sorted_types[:5]:  # Show top 5
                ext_display = file_ext if file_ext else "(no extension)"
                print(f"  {Fore.GREEN}{ext_display:<12}{Style.RESET_ALL}: {Fore.YELLOW}{count} files{Style.RESET_ALL}")

        # Log files info
        print(f"\n{Fore.CYAN}📋 Detailed Logs Created:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}📄 Text log: {Style.BRIGHT}{log_summary.get('log_file', 'N/A')}{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}📊 JSON log: {Style.BRIGHT}{log_summary.get('json_file', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💡 Use these logs to review detailed indexing information{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}🚀 Ready for AI interactions!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}You can now use chat, max chat, or agent mode to interact with your indexed codebase.{Style.RESET_ALL}")

    def _handle_exit(self) -> None:
        """Handle exit option."""
        self.running = False
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")

    def _handle_view_files(self) -> None:
        """Handle view indexed files option."""
        if not self.indexer:
            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "📁 Indexed Files" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

        try:
            self.logger.info("[STAT] Viewing indexed files information")

            # Check index status
            index_status = self.indexer.is_index_complete()

            # Determine status message based on the type of incompleteness
            if index_status["complete"]:
                status_str = "Complete"
                status_color = Fore.GREEN
                status_message = "All files are indexed and up to date"
            else:
                missing_count = index_status.get("missing_count", 0)
                outdated_count = index_status.get("outdated_count", 0)

                if missing_count > 0 and outdated_count == 0:
                    if missing_count <= 3:
                        status_str = "Mostly Complete"
                        status_color = Fore.CYAN
                        status_message = f"{missing_count} new files found (not yet indexed)"
                    else:
                        status_str = "Incomplete"
                        status_color = Fore.YELLOW
                        status_message = f"{missing_count} files are not indexed"
                elif outdated_count > 0 and missing_count == 0:
                    status_str = "Needs Update"
                    status_color = Fore.YELLOW
                    status_message = f"{outdated_count} files need updating"
                elif missing_count > 0 and outdated_count > 0:
                    status_str = "Incomplete"
                    status_color = Fore.YELLOW
                    status_message = f"{missing_count} files not indexed, {outdated_count} files need updating"
                else:
                    status_str = "Incomplete"
                    status_color = Fore.YELLOW
                    status_message = index_status.get("reason", "Unknown issue")

            print(f"{Fore.CYAN}Index Status: {status_color}{Style.BRIGHT}{status_str}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Reason: {status_message}{Style.RESET_ALL}")

            # Show index directory info
            index_dir = self.indexer.index_dir
            print(f"\n{Fore.CYAN}Index Directory: {Fore.WHITE}{index_dir}{Style.RESET_ALL}")

            if os.path.exists(index_dir):
                metadata_dir = os.path.join(index_dir, "metadata")
                embeddings_dir = os.path.join(index_dir, "embeddings")
                descriptions_dir = os.path.join(index_dir, "descriptions")

                print(f"\n{Fore.CYAN}{Style.BRIGHT}Index Directory Structure:{Style.RESET_ALL}")
                header = f"  {Fore.CYAN}{'Directory':<15} {'Exists':<10} {'Files':<10} {'Size':<10}{Style.RESET_ALL}"
                separator = f"  {Fore.CYAN}{'-'*15} {'-'*10} {'-'*10} {'-'*10}{Style.RESET_ALL}"
                print(header)
                print(separator)

                # Check metadata directory
                if os.path.exists(metadata_dir):
                    files = [f for f in os.listdir(metadata_dir) if f.endswith(".json")]
                    size = sum(os.path.getsize(os.path.join(metadata_dir, f)) for f in files)
                    print(
                        f"  {Fore.GREEN}{'metadata':<15} {Fore.GREEN}{'Yes':<10} {Fore.YELLOW}{len(files):<10} {Fore.MAGENTA}{self._format_size(size):<10}{Style.RESET_ALL}"
                    )
                else:
                    print(
                        f"  {Fore.GREEN}{'metadata':<15} {Fore.RED}{'No':<10} {'-':<10} {'-':<10}{Style.RESET_ALL}"
                    )

                # Check embeddings directory
                if os.path.exists(embeddings_dir):
                    files = [f for f in os.listdir(embeddings_dir) if f.endswith(".json")]
                    size = sum(os.path.getsize(os.path.join(embeddings_dir, f)) for f in files)
                    print(
                        f"  {Fore.GREEN}{'embeddings':<15} {Fore.GREEN}{'Yes':<10} {Fore.YELLOW}{len(files):<10} {Fore.MAGENTA}{self._format_size(size):<10}{Style.RESET_ALL}"
                    )
                else:
                    print(
                        f"  {Fore.GREEN}{'embeddings':<15} {Fore.RED}{'No':<10} {'-':<10} {'-':<10}{Style.RESET_ALL}"
                    )

                # Check descriptions directory
                if os.path.exists(descriptions_dir):
                    files = [f for f in os.listdir(descriptions_dir) if f.endswith(".txt")]
                    size = sum(os.path.getsize(os.path.join(descriptions_dir, f)) for f in files)
                    print(
                        f"  {Fore.GREEN}{'descriptions':<15} {Fore.GREEN}{'Yes':<10} {Fore.YELLOW}{len(files):<10} {Fore.MAGENTA}{self._format_size(size):<10}{Style.RESET_ALL}"
                    )
                else:
                    print(
                        f"  {Fore.GREEN}{'descriptions':<15} {Fore.RED}{'No':<10} {'-':<10} {'-':<10}{Style.RESET_ALL}"
                    )
            else:
                print(f"{Fore.RED}Index directory does not exist.{Style.RESET_ALL}")

            # Show sample indexed files
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Sample Indexed Files:{Style.RESET_ALL}")
            try:
                sample_files = self.indexer.get_sample_files(10)
                if sample_files:
                    for i, file in enumerate(sample_files, 1):
                        # Show relative path for cleaner display
                        rel_path = os.path.relpath(file, self.indexer.root_path) if os.path.isabs(file) else file
                        print(f"{Fore.GREEN}{i:2d}. {Fore.WHITE}{rel_path}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No files have been indexed yet.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error retrieving sample files: {e}{Style.RESET_ALL}")

            # Show additional stats if available
            try:
                if hasattr(index_status, 'get') and 'missing_count' in index_status:
                    print(f"\n{Fore.CYAN}{Style.BRIGHT}Index Statistics:{Style.RESET_ALL}")
                    if index_status.get('missing_count', 0) > 0:
                        print(f"  {Fore.YELLOW}Missing files: {index_status['missing_count']}{Style.RESET_ALL}")
                    if index_status.get('outdated_count', 0) > 0:
                        print(f"  {Fore.YELLOW}Outdated files: {index_status['outdated_count']}{Style.RESET_ALL}")
                    if index_status.get('ignored_count', 0) > 0:
                        print(f"  {Fore.CYAN}Ignored files: {index_status['ignored_count']}{Style.RESET_ALL}")
            except Exception:
                pass

            # Show recent indexing logs if available
            self._show_recent_indexing_logs()

        except Exception as e:
            self.logger.error(f"Error viewing indexed files: {e}", exc_info=True)
            print(f"{Fore.RED}{Style.BRIGHT}Error viewing indexed files: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def _show_recent_indexing_logs(self) -> None:
        """Show recent indexing logs if available."""
        try:
            logs_dir = "logs"
            if not os.path.exists(logs_dir):
                return

            # Find recent indexing logs
            project_name = os.path.basename(self.indexer.root_path) if self.indexer else "unknown"
            log_files = []

            for file in os.listdir(logs_dir):
                if file.startswith(f"indexing_{project_name}") and file.endswith(".log"):
                    log_path = os.path.join(logs_dir, file)
                    log_files.append((log_path, os.path.getmtime(log_path)))

            if log_files:
                # Sort by modification time (newest first)
                log_files.sort(key=lambda x: x[1], reverse=True)

                print(f"\n{Fore.CYAN}{Style.BRIGHT}📋 Recent Indexing Logs:{Style.RESET_ALL}")

                # Show most recent 3 logs
                for i, (log_path, mtime) in enumerate(log_files[:3]):
                    log_name = os.path.basename(log_path)
                    log_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                    log_size = self._format_size(os.path.getsize(log_path))

                    print(f"  {i+1}. {Fore.GREEN}{log_name}{Style.RESET_ALL}")
                    print(f"     📅 {log_date} | 📊 {log_size}")

                    # Try to show summary from JSON file if available
                    json_file = log_path.replace('.log', '.json')
                    if os.path.exists(json_file):
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                log_data = json.load(f)
                                stats = log_data.get('statistics', {})
                                indexed = stats.get('files_indexed', 0)
                                ignored = stats.get('files_ignored', 0)
                                failed = stats.get('files_failed', 0)
                                processing_time = stats.get('processing_time', 0)

                                print(f"     ✅ {indexed} indexed | ⏭️ {ignored} ignored | ❌ {failed} failed | ⏱️ {processing_time:.1f}s")
                        except Exception:
                            print(f"     📄 Log available for detailed review")
                    print()

                if len(log_files) > 3:
                    print(f"  {Fore.CYAN}... and {len(log_files) - 3} older log files{Style.RESET_ALL}")

                print(f"{Fore.CYAN}💡 Check log files for detailed indexing information and file lists{Style.RESET_ALL}")

        except Exception as e:
            self.logger.debug(f"Error showing recent indexing logs: {e}")

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"

    def _handle_view_project(self) -> None:
        """Handle view project info option with submenu."""
        print(f"\n{Fore.CYAN}📊 View Project Info{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

        if not self.indexer:
            print(f"{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        while True:
            # Display submenu
            print(f"\n{Fore.CYAN}Select an option:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}1. {Style.BRIGHT}📊 Show Project Information{Style.RESET_ALL}")
            print(f"{Fore.GREEN}2. {Style.BRIGHT}🔍 Generate Project Analysis{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}0. {Style.BRIGHT}🔙 Back to Main Menu{Style.RESET_ALL}")

            choice = input(f"\n{Fore.GREEN}Enter your choice (0-2): {Style.RESET_ALL}").strip()

            if choice == "1":
                self._show_project_information()
            elif choice == "2":
                self._handle_create_about_document()
            elif choice == "0":
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 0-2.{Style.RESET_ALL}")

    def _show_project_information(self) -> None:
        """Show detailed project information including analysis and reports."""
        if not self.indexer:
            print(f"{Fore.RED}No project indexed. Please index your project first.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}📊 Project Information{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}Available options:{Style.RESET_ALL}")
        print(f"  1. 📈 Generate AI Project Analysis")
        print(f"  2. 📋 Show Basic Project Stats")
        print(f"  0. ← Back to main menu")

        choice = input(f"\n{Fore.GREEN}Select option (0-2): {Style.RESET_ALL}").strip()

        if choice == "1":
            # Generate AI analysis
            asyncio.run(self._perform_ai_project_analysis())
        elif choice == "2":
            # Show basic stats
            self._show_basic_project_stats()
        elif choice == "0":
            return
        else:
            print(f"{Fore.YELLOW}Invalid choice. Please try again.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    async def _perform_ai_project_analysis(self) -> None:
        """Perform AI-powered project analysis."""
        try:
            print(f"\n{Fore.CYAN}🤖 Generating AI Project Analysis{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

            # Collect project statistics
            print(f"{Fore.YELLOW}📊 Collecting project statistics...{Style.RESET_ALL}")
            stats = self._collect_project_statistics()

            # Generate AI analysis
            print(f"{Fore.YELLOW}🤖 Generating AI analysis...{Style.RESET_ALL}")
            ai_analysis = await self._generate_ai_project_analysis(stats)

            # Display the analysis
            project_name = os.path.basename(self.indexer.root_path)
            self._display_project_report(project_name, self.indexer.root_path, stats, ai_analysis)

        except Exception as e:
            self.logger.error(f"Error performing AI project analysis: {e}")
            print(f"{Fore.RED}Error performing AI project analysis: {e}{Style.RESET_ALL}")

    def _show_basic_project_stats(self) -> None:
        """Show basic project statistics without AI analysis."""
        try:
            print(f"\n{Fore.CYAN}📊 Basic Project Statistics{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

            stats = self._collect_project_statistics()
            
            print(f"\n{Fore.GREEN}📁 Project Overview:{Style.RESET_ALL}")
            print(f"  Total Files: {stats['total_files']}")
            print(f"  Indexed Files: {stats['indexed_files']}")
            print(f"  Total Size: {self._format_size(stats['size_info']['total_size'])}")

            print(f"\n{Fore.GREEN}📄 File Types:{Style.RESET_ALL}")
            for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {ext or 'no extension'}: {count} files")

            print(f"\n{Fore.GREEN}💻 Programming Languages:{Style.RESET_ALL}")
            for lang, count in sorted(stats['language_breakdown'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {lang}: {count} files")

        except Exception as e:
            self.logger.error(f"Error showing basic project stats: {e}")
            print(f"{Fore.RED}Error showing basic project stats: {e}{Style.RESET_ALL}")

    def _collect_project_statistics(self) -> Dict[str, Any]:
        """Collect comprehensive project statistics."""
        stats = {
            'total_files': 0,
            'indexed_files': 0,
            'file_types': {},
            'size_info': {'total_size': 0, 'largest_files': []},
            'directory_structure': {},
            'language_breakdown': {},
            'recent_changes': [],
            'complexity_indicators': {}
        }

        try:
            # Get all indexed files
            sample_files = self.indexer.get_sample_files(100)  # Get more files for analysis
            indexed_files = self.indexer.get_indexed_files() if hasattr(self.indexer, 'get_indexed_files') else sample_files

            stats['indexed_files'] = len(indexed_files)

            # Analyze ALL files in the directory for accurate statistics
            if os.path.exists(self.indexer.root_path):
                for root, dirs, files in os.walk(self.indexer.root_path):
                    # Skip .index and hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

                    # Count all files
                    stats['total_files'] += len(files)

                    # Directory structure analysis
                    rel_path = os.path.relpath(root, self.indexer.root_path)
                    if rel_path != '.' and len(rel_path.split(os.sep)) <= 3:  # Only top 3 levels
                        stats['directory_structure'][rel_path] = len(files)

                    # Analyze files in this directory
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            file_ext = os.path.splitext(file)[1].lower()

                            # Count file types
                            stats['file_types'][file_ext] = stats['file_types'].get(file_ext, 0) + 1

                            # Track total size
                            stats['size_info']['total_size'] += file_size

                            # Track largest files (keep top 10)
                            if len(stats['size_info']['largest_files']) < 10:
                                stats['size_info']['largest_files'].append((file_path, file_size))
                            else:
                                # Replace smallest if current is larger
                                min_size_idx = min(range(len(stats['size_info']['largest_files'])),
                                                 key=lambda i: stats['size_info']['largest_files'][i][1])
                                if file_size > stats['size_info']['largest_files'][min_size_idx][1]:
                                    stats['size_info']['largest_files'][min_size_idx] = (file_path, file_size)

                            # Language breakdown
                            language = self._get_language_from_extension(file_ext)
                            if language:
                                stats['language_breakdown'][language] = stats['language_breakdown'].get(language, 0) + 1

                        except Exception as e:
                            self.logger.debug(f"Error analyzing file {file_path}: {e}")
                            continue

            # Sort largest files
            stats['size_info']['largest_files'].sort(key=lambda x: x[1], reverse=True)

        except Exception as e:
            self.logger.error(f"Error collecting project statistics: {e}")

        return stats

    def _get_language_from_extension(self, ext: str) -> Optional[str]:
        """Map file extension to programming language."""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.kt': 'Kotlin',
            '.swift': 'Swift',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.less': 'LESS',
            '.jsx': 'React JSX',
            '.tsx': 'React TSX',
            '.vue': 'Vue.js',
            '.sql': 'SQL',
            '.sh': 'Shell Script',
            '.ps1': 'PowerShell',
            '.bat': 'Batch Script',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown',
            '.dockerfile': 'Docker',
            '.tf': 'Terraform',
            '.txt': 'Text',
            '.log': 'Log Files',
            '.ini': 'Configuration',
            '.cfg': 'Configuration',
            '.conf': 'Configuration',
            '.env': 'Environment',
            '.gitignore': 'Git',
            '.gitattributes': 'Git',
            '.toml': 'TOML',
            '.lock': 'Lock Files',
            '.sample': 'Sample Files',
            '.example': 'Example Files',
            '.j2': 'Jinja2 Templates',
            '.pyc': 'Python Bytecode',
            '.pyo': 'Python Bytecode',
            '.pyd': 'Python Extension'
        }
        return language_map.get(ext)

    async def _generate_ai_project_analysis(self, stats: Dict[str, Any]) -> str:
        """Generate AI-powered project analysis."""
        if not self.ai_manager:
            return "AI analysis not available - AI Manager not initialized."

        try:
            # Create analysis prompt
            prompt = f"""
Analyze this software project based on the following statistics and provide a comprehensive report:

PROJECT STATISTICS:
- Total Files: {stats['total_files']}
- Indexed Files: {stats['indexed_files']}
- Total Size: {self._format_size(stats['size_info']['total_size'])}

FILE TYPES:
{self._format_dict_for_prompt(stats['file_types'])}

PROGRAMMING LANGUAGES:
{self._format_dict_for_prompt(stats['language_breakdown'])}

DIRECTORY STRUCTURE:
{self._format_dict_for_prompt(stats['directory_structure'])}

LARGEST FILES:
{self._format_largest_files_for_prompt(stats['size_info']['largest_files'])}

Please provide a detailed analysis covering:
1. **Project Type & Architecture**: What kind of project this appears to be
2. **Technology Stack**: Primary languages and frameworks identified
3. **Project Scale**: Size and complexity assessment
4. **Code Organization**: How well the code appears to be structured
5. **Key Insights**: Notable patterns, potential issues, or strengths
6. **Recommendations**: Suggestions for development, maintenance, or AI agent tasks

Format your response in clear sections with bullet points where appropriate.
Keep the analysis concise but insightful, suitable for an AI agent to understand the project quickly.
"""

            # Get AI analysis using the configured AI function assignment
            from ..settings import AISettingsManager
            ai_settings = AISettingsManager()
            ai_settings.initialize()

            # Use the assigned AI provider for description generation
            assignments = ai_settings.get_ai_function_assignments()
            description_assignment = assignments.get('description', {})
            provider = description_assignment.get('provider', 'ollama')
            model = description_assignment.get('model', 'llama3.2:latest')

            print(f"  Using {provider.title()} ({model}) for analysis...")

            # Generate analysis with fallback
            analysis = await self._get_ai_response_with_fallback(prompt, provider, model)
            return analysis

        except Exception as e:
            self.logger.error(f"Error generating AI analysis: {e}")
            return f"Error generating AI analysis: {str(e)}"

    async def _get_ai_response_with_fallback(self, prompt: str, provider: str, model: str) -> str:
        """Get AI response with fallback to other providers if the primary fails."""
        try:
            # Try the primary provider first
            return await self._get_ai_response(prompt, provider, model)
        except Exception as primary_error:
            self.logger.warning(f"Primary provider {provider} failed: {primary_error}")

            # Define fallback providers in order of preference
            fallback_providers = [
                ('ollama', 'llama3.2:latest'),
                ('openai', 'gpt-4'),
                ('anthropic', 'claude-3-sonnet-20240229'),
                ('deepseek', 'deepseek-chat')
            ]

            # Remove the failed provider from fallbacks
            fallback_providers = [(p, m) for p, m in fallback_providers if p != provider]

            for fallback_provider, fallback_model in fallback_providers:
                try:
                    print(f"  Primary provider failed, trying {fallback_provider.title()}...")
                    return await self._get_ai_response(prompt, fallback_provider, fallback_model)
                except Exception as fallback_error:
                    self.logger.warning(f"Fallback provider {fallback_provider} failed: {fallback_error}")
                    continue

            # If all providers fail, return the original error with helpful message
            error_msg = str(primary_error)
            if "API key not configured" in error_msg:
                return f"Error generating analysis: {error_msg}\n\nTo fix this:\n1. Go to AI Settings in the main menu\n2. Configure API keys for at least one provider\n3. Try the analysis again\n\nSupported providers: OpenAI, Anthropic, DeepSeek, Ollama"
            else:
                return f"Error generating analysis: All AI providers failed.\nPrimary error ({provider}): {primary_error}\n\nPlease check your AI provider settings and try again."

    async def _get_ai_response(self, prompt: str, provider: str, model: str) -> str:
        """Get AI response using specified provider and model."""
        try:
            from ..ai.providers import ProviderFactory

            # Create provider configuration with conservative token limits
            provider_config = {
                'model': model,
                'max_tokens': 1500,  # Reduced from 2000 for safer context management
                'temperature': 0.3
            }

            # Add provider-specific config
            if provider == 'openai':
                from ..settings import AISettingsManager
                ai_settings = AISettingsManager()
                ai_settings.initialize()
                openai_settings = ai_settings.get_openai_settings()
                provider_config['api_key'] = openai_settings.get('API_KEY')
                # Further reduce tokens for OpenAI to avoid context issues
                provider_config['max_tokens'] = 1000
            elif provider == 'ollama':
                from ..settings import AISettingsManager
                ai_settings = AISettingsManager()
                ai_settings.initialize()
                ollama_settings = ai_settings.get_ollama_settings()
                provider_config['host'] = ollama_settings.get('HOST', 'http://127.0.0.1:11434')
                # Ollama can handle more tokens
                provider_config['max_tokens'] = 3000
            elif provider == 'deepseek':
                from ..settings import AISettingsManager
                ai_settings = AISettingsManager()
                ai_settings.initialize()
                deepseek_settings = ai_settings.get_deepseek_settings()
                provider_config['api_key'] = deepseek_settings.get('API_KEY')
                # DeepSeek can handle good amount of tokens
                provider_config['max_tokens'] = 2000
                # Validate API key
                if not provider_config['api_key']:
                    raise Exception("DeepSeek API key not configured. Please set up DeepSeek API key in AI settings.")
            elif provider == 'anthropic':
                from ..settings import AISettingsManager
                ai_settings = AISettingsManager()
                ai_settings.initialize()
                anthropic_settings = ai_settings.get_anthropic_settings()
                provider_config['api_key'] = anthropic_settings.get('API_KEY')
                provider_config['max_tokens'] = 1500
                # Validate API key
                if not provider_config['api_key']:
                    raise Exception("Anthropic API key not configured. Please set up Anthropic API key in AI settings.")
            elif provider == 'openrouter':
                from ..settings import AISettingsManager
                ai_settings = AISettingsManager()
                ai_settings.initialize()
                openrouter_settings = ai_settings.get_openrouter_settings()
                provider_config['api_key'] = openrouter_settings.get('API_KEY')
                provider_config['max_tokens'] = 2000
                # Validate API key
                if not provider_config['api_key']:
                    raise Exception("OpenRouter API key not configured. Please set up OpenRouter API key in AI settings.")

            # Create provider factory and get response
            factory = ProviderFactory()
            provider_instance = await factory.create_provider(provider, provider_config)

            response = await provider_instance.generate_response(prompt)

            if hasattr(provider_instance, 'close'):
                await provider_instance.close()

            return response

        except Exception as e:
            self.logger.error(f"Error getting AI response: {e}")
            error_msg = str(e)

            # Provide more helpful error messages
            if "API key not configured" in error_msg:
                return f"Error generating analysis: {error_msg}\n\nTo fix this:\n1. Go to AI Settings in the main menu\n2. Configure your {provider.title()} API key\n3. Try the analysis again"
            elif "authentication failed" in error_msg.lower():
                return f"Error generating analysis: Authentication failed for {provider.title()}\n\nPlease check your API key in AI Settings."
            elif "rate limit" in error_msg.lower():
                return f"Error generating analysis: Rate limit exceeded for {provider.title()}\n\nPlease wait a moment and try again."
            else:
                return f"Error generating analysis: {error_msg}"

    def _format_dict_for_prompt(self, data: Dict[str, Any]) -> str:
        """Format dictionary data for AI prompt."""
        if not data:
            return "None"

        items = []
        for key, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
            items.append(f"  {key}: {value}")
        return "\n".join(items[:10])  # Limit to top 10

    def _format_largest_files_for_prompt(self, files: List[Tuple[str, int]]) -> str:
        """Format largest files for AI prompt."""
        if not files:
            return "None"

        items = []
        for file_path, size in files:
            filename = os.path.basename(file_path)
            items.append(f"  {filename}: {self._format_size(size)}")
        return "\n".join(items)

    def _display_project_report(self, project_name: str, project_path: str,
                               stats: Dict[str, Any], ai_analysis: str) -> None:
        """Display the complete project report."""

        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}📊 PROJECT ANALYSIS REPORT{Style.RESET_ALL}".center(70))
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

        # Basic Info
        print(f"\n{Fore.GREEN}{Style.BRIGHT}📁 Project Information:{Style.RESET_ALL}")
        print(f"  Name: {Fore.WHITE}{project_name}{Style.RESET_ALL}")
        print(f"  Path: {Fore.WHITE}{project_path}{Style.RESET_ALL}")
        print(f"  Total Files: {Fore.YELLOW}{stats['total_files']}{Style.RESET_ALL}")
        print(f"  Indexed Files: {Fore.YELLOW}{stats['indexed_files']}{Style.RESET_ALL}")
        print(f"  Total Size: {Fore.YELLOW}{self._format_size(stats['size_info']['total_size'])}{Style.RESET_ALL}")

        # File Types
        if stats['file_types']:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}📄 File Types:{Style.RESET_ALL}")
            for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:8]:
                ext_display = ext if ext else "(no extension)"
                print(f"  {Fore.CYAN}{ext_display:<12}{Style.RESET_ALL}: {Fore.YELLOW}{count}{Style.RESET_ALL}")

        # Languages
        if stats['language_breakdown']:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}💻 Programming Languages:{Style.RESET_ALL}")
            for lang, count in sorted(stats['language_breakdown'].items(), key=lambda x: x[1], reverse=True)[:6]:
                print(f"  {Fore.CYAN}{lang:<15}{Style.RESET_ALL}: {Fore.YELLOW}{count} files{Style.RESET_ALL}")

        # AI Analysis
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🤖 AI-Powered Analysis:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")

        # Format and display AI analysis
        analysis_lines = ai_analysis.split('\n')
        for line in analysis_lines:
            if line.strip():
                if line.startswith('#'):
                    # Headers
                    print(f"{Fore.YELLOW}{Style.BRIGHT}{line.strip()}{Style.RESET_ALL}")
                elif line.startswith('**') and line.endswith('**'):
                    # Bold text
                    print(f"{Fore.GREEN}{Style.BRIGHT}{line.strip()}{Style.RESET_ALL}")
                elif line.strip().startswith('-') or line.strip().startswith('•'):
                    # Bullet points
                    print(f"  {Fore.WHITE}{line.strip()}{Style.RESET_ALL}")
                else:
                    # Regular text
                    print(f"{Fore.WHITE}{line.strip()}{Style.RESET_ALL}")
            else:
                print()

        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Analysis Complete - Report ready for AI agents{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💡 This report can help AI agents understand your project structure and make informed decisions{Style.RESET_ALL}")

    def _handle_recent_projects(self) -> None:
        """Handle recent projects option with full functionality."""
        print(f"\n{Fore.CYAN}📚 Recent Projects{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

        if not self.settings_manager:
            print(f"{Fore.RED}Error: Settings manager not available.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        recent_projects = self.settings_manager.get_recent_projects()

        if not recent_projects:
            print(f"{Fore.YELLOW}No recent projects found.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Projects will appear here after you index them using option 1.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        # Determine if this is a central installation or single project
        installation_type = self._detect_installation_type()

        print(f"{Fore.CYAN}Installation Type: {Style.BRIGHT}{installation_type}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Found {len(recent_projects)} recent project(s):{Style.RESET_ALL}\n")

        # Display projects with status
        valid_projects = []
        for i, project in enumerate(recent_projects, 1):
            project_path = project.get('path', '')
            project_name = project.get('name', 'Unknown')
            last_accessed = project.get('last_accessed', 'Unknown')

            # Check if project directory still exists
            if not os.path.exists(project_path):
                print(f"{Fore.RED}{i:2d}. ❌ {project_name}{Style.RESET_ALL}")
                print(f"     📁 {project_path}")
                print(f"     ⚠️  Directory no longer exists")
                print()
                continue

            valid_projects.append((i, project))

            # Check indexing status
            index_status = self._get_project_index_status(project_path)
            status_icon, status_text, status_color = self._format_index_status(index_status)

            print(f"{Fore.GREEN}{i:2d}. {status_icon} {Style.BRIGHT}{project_name}{Style.RESET_ALL}")
            print(f"     📁 {project_path}")
            print(f"     🕒 Last accessed: {last_accessed}")
            print(f"     📊 Status: {status_color}{status_text}{Style.RESET_ALL}")

            # Show additional info for indexed projects
            if index_status['indexed']:
                files_count = index_status.get('files_indexed', 0)
                if files_count > 0:
                    print(f"     📄 Files indexed: {files_count}")
            print()

        if not valid_projects:
            print(f"{Fore.YELLOW}All recent projects have been moved or deleted.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Use option 13 (Project Cleanup Manager) to clean up the list.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        # Show menu options
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Options:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}• Enter project number (1-{len(recent_projects)}) to switch to that project{Style.RESET_ALL}")
        print(f"{Fore.BLUE}• Type 'r' + number (e.g., 'r3') to remove a project from recent list{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}• Type 'c' to clear all recent projects{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• Press Enter or type '0' to go back{Style.RESET_ALL}")

        while True:
            choice = input(f"\n{Fore.GREEN}Choose an option: {Style.RESET_ALL}").strip().lower()

            if not choice or choice == '0':
                break

            elif choice == 'c':
                confirm = input(f"{Fore.YELLOW}Clear all recent projects? (y/N): {Style.RESET_ALL}").strip().lower()
                if confirm in ['y', 'yes']:
                    self.settings_manager.clear_recent_projects()
                    print(f"{Fore.GREEN}✅ Recent projects cleared.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.CYAN}Operation cancelled.{Style.RESET_ALL}")

            elif choice.startswith('r') and len(choice) > 1:
                try:
                    project_num = int(choice[1:])
                    if 1 <= project_num <= len(recent_projects):
                        project_to_remove = recent_projects[project_num - 1]
                        project_path = project_to_remove.get('path', '')
                        project_name = project_to_remove.get('name', 'Unknown')

                        confirm = input(f"{Fore.YELLOW}Remove '{project_name}' from recent projects? (y/N): {Style.RESET_ALL}").strip().lower()
                        if confirm in ['y', 'yes']:
                            self.settings_manager.remove_from_recent_projects(project_path)
                            print(f"{Fore.GREEN}✅ Project removed from recent list.{Style.RESET_ALL}")
                            # Refresh the display
                            self._handle_recent_projects()
                            return
                        else:
                            print(f"{Fore.CYAN}Operation cancelled.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Invalid project number. Please enter 1-{len(recent_projects)}.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid format. Use 'r' followed by project number (e.g., 'r3').{Style.RESET_ALL}")

            else:
                try:
                    project_num = int(choice)
                    if 1 <= project_num <= len(recent_projects):
                        selected_project = recent_projects[project_num - 1]
                        project_path = selected_project.get('path', '')
                        project_name = selected_project.get('name', 'Unknown')

                        if os.path.exists(project_path):
                            print(f"\n{Fore.GREEN}🔄 Switching to project: {Style.BRIGHT}{project_name}{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}📁 Path: {project_path}{Style.RESET_ALL}")

                            # Switch to the selected project
                            self._switch_to_project(project_path)
                            break
                        else:
                            print(f"{Fore.RED}❌ Project directory no longer exists: {project_path}{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}Consider removing it from recent projects using 'r{project_num}'.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Invalid project number. Please enter 1-{len(recent_projects)}.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number, 'r' + number, 'c', or press Enter to go back.{Style.RESET_ALL}")

    def _detect_installation_type(self) -> str:
        """Detect if this is a central installation or single project setup."""
        try:
            # Check if we're in a project directory with TaskHero AI as a subdirectory
            current_dir = os.getcwd()
            parent_dir = os.path.dirname(current_dir)

            # If current directory name is 'taskheroai' and parent has other projects
            if os.path.basename(current_dir) == 'taskheroai':
                # Check if parent directory has other subdirectories (potential projects)
                try:
                    parent_contents = [d for d in os.listdir(parent_dir)
                                     if os.path.isdir(os.path.join(parent_dir, d)) and d != 'taskheroai']
                    if len(parent_contents) > 0:
                        return "Project Integration (TaskHero AI integrated into project folder)"
                except (PermissionError, OSError):
                    pass

            # Check if we're in a tools/utilities directory
            if any(keyword in current_dir.lower() for keyword in ['tools', 'utilities', 'bin', 'opt']):
                return "Central Installation (Multi-project analysis tool)"

            # Check if we have multiple recent projects from different base directories
            if self.settings_manager:
                recent_projects = self.settings_manager.get_recent_projects()
                if len(recent_projects) > 1:
                    base_dirs = set()
                    for project in recent_projects:
                        project_path = project.get('path', '')
                        if project_path:
                            # Get the parent directory of the project
                            base_dir = os.path.dirname(project_path)
                            base_dirs.add(base_dir)

                    if len(base_dirs) > 1:
                        return "Central Installation (Multiple project directories detected)"

            return "Single Project Setup (Dedicated to one codebase)"

        except Exception as e:
            self.logger.debug(f"Error detecting installation type: {e}")
            return "Unknown Installation Type"

    def _get_project_index_status(self, project_path: str) -> Dict[str, Any]:
        """Get the indexing status for a specific project."""
        try:
            from ..code.indexer import FileIndexer

            # Create a temporary indexer to check status
            temp_indexer = FileIndexer(project_path)
            index_status = temp_indexer.is_index_complete()

            # Get additional information
            result = {
                'indexed': index_status.get('complete', False),
                'outdated_count': index_status.get('outdated_count', 0),
                'missing_count': index_status.get('missing_count', 0),
                'ignored_count': index_status.get('ignored_count', 0),
                'reason': index_status.get('reason', 'Unknown'),
                'files_indexed': 0
            }

            # Try to get file count if indexed
            if result['indexed']:
                try:
                    sample_files = temp_indexer.get_sample_files(1000)  # Get up to 1000 files
                    result['files_indexed'] = len(sample_files)
                except Exception:
                    pass

            return result

        except Exception as e:
            self.logger.debug(f"Error checking index status for {project_path}: {e}")
            return {
                'indexed': False,
                'outdated_count': 0,
                'missing_count': 0,
                'ignored_count': 0,
                'reason': f'Error checking status: {str(e)}',
                'files_indexed': 0
            }

    def _format_index_status(self, index_status: Dict[str, Any]) -> tuple:
        """Format index status into icon, text, and color."""
        indexed = index_status.get('indexed', False)
        outdated_count = index_status.get('outdated_count', 0)
        missing_count = index_status.get('missing_count', 0)

        if indexed and outdated_count == 0 and missing_count == 0:
            return "✅", "Fully Indexed", Fore.GREEN
        elif indexed and (outdated_count > 0 or missing_count > 0):
            if outdated_count > 0 and missing_count == 0:
                return "🔄", f"Needs Update ({outdated_count} files)", Fore.YELLOW
            elif missing_count > 0 and outdated_count == 0:
                return "⚠️", f"Partially Indexed ({missing_count} new files)", Fore.YELLOW
            else:
                return "⚠️", f"Needs Update ({outdated_count} outdated, {missing_count} new)", Fore.YELLOW
        else:
            return "❌", "Not Indexed", Fore.RED

    def _switch_to_project(self, project_path: str) -> None:
        """Switch the current session to a different project."""
        try:
            from ..code.indexer import FileIndexer
            from ..code.decisions import FileSelector, ProjectAnalyzer

            # Update settings with new directory
            if self.settings_manager:
                self.settings_manager.set_last_directory(project_path)
                # Update recent projects (this will move it to the top)
                self.settings_manager.add_to_recent_projects(project_path)

            # Initialize new indexer components
            self.indexer = FileIndexer(project_path)
            self.file_selector = FileSelector()
            self.project_analyzer = ProjectAnalyzer(self.indexer)

            # Check index status
            index_status = self.indexer.is_index_complete()
            self.index_outdated = not index_status.get('complete', False)

            # Update AI manager dependencies
            if self.ai_manager:
                self.ai_manager.set_dependencies(self.indexer, self.file_selector, self.project_analyzer)

            # Update UI manager state
            if self.ui_manager:
                self.ui_manager.set_application_state(self.indexer, self.index_outdated)

            print(f"{Fore.GREEN}✅ Successfully switched to project!{Style.RESET_ALL}")

            if self.index_outdated:
                print(f"{Fore.YELLOW}⚠️  Index is outdated. Consider reindexing using option 1.{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}📊 Project is fully indexed and ready for analysis.{Style.RESET_ALL}")

            input(f"\n{Fore.CYAN}Press Enter to return to main menu...{Style.RESET_ALL}")

        except Exception as e:
            self.logger.error(f"Error switching to project {project_path}: {e}")
            print(f"{Fore.RED}❌ Error switching to project: {e}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}You can try indexing this project using option 1.{Style.RESET_ALL}")
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
        """Handle quick create task option - Enhanced with AI Task Creator."""
        print(f"\n{Fore.CYAN}➕ Enhanced Task Creation{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

        # Show creation options
        print(f"{Fore.GREEN}Choose creation method:{Style.RESET_ALL}")
        print(f"  1. 🚀 AI-Enhanced Task Creation (Comprehensive)")
        print(f"  2. ⚡ Quick Task Creation (Basic)")
        print(f"  0. ← Back to main menu")

        choice = input(f"\n{Fore.GREEN}Select option (1-2, default 1): {Style.RESET_ALL}").strip()

        if choice == "2":
            self._handle_quick_basic_task()
        elif choice == "0":
            return
        else:  # Default to AI-enhanced
            self._handle_ai_enhanced_task()

    def _handle_ai_enhanced_task(self) -> None:
        """Handle AI-enhanced task creation with Phase 4C progressive wizard."""
        try:
            import asyncio
            from ..project_management.ai_task_creator import AITaskCreator

            print(f"\n{Fore.CYAN}🚀 AI-Enhanced Task Creation - Phase 4C{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✨ Progressive task creation with interactive context selection{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🔍 Semantic search + 🧠 AI enhancement + 👤 User control{Style.RESET_ALL}")
            print()

            # Show creation method options
            print(f"{Fore.CYAN}Choose creation method:{Style.RESET_ALL}")
            print(f"  1. 🚀 Progressive Wizard (Recommended) - Step-by-step with context selection")
            print(f"  2. ⚡ Quick Interactive - Traditional single-step creation")
            print(f"  0. ← Back to main menu")

            choice = input(f"\n{Fore.GREEN}Select option (1-2, default 1): {Style.RESET_ALL}").strip()

            if choice == '0':
                return
            elif choice == '2':
                # Traditional interactive creation
                print(f"\n{Fore.CYAN}🤖 Quick Interactive Task Creation{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

                # Show AI provider information
                try:
                    from ..code.indexer import _get_ai_provider_info
                    ai_info = _get_ai_provider_info()
                    print(f"{Fore.MAGENTA}🤖 AI Provider: {ai_info['description_full']} will enhance your task{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}🤖 AI Provider info unavailable{Style.RESET_ALL}")

                # Initialize AI Task Creator
                ai_creator = AITaskCreator(project_root=str(Path.cwd()))

                # Run traditional interactive creation
                success, task_id, result = asyncio.run(ai_creator.create_task_interactive())
            else:
                # Progressive wizard (default)
                print(f"\n{Fore.CYAN}🚀 Progressive Task Creation Wizard{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

                # Show AI provider information
                try:
                    from ..code.indexer import _get_ai_provider_info
                    ai_info = _get_ai_provider_info()
                    print(f"{Fore.MAGENTA}🤖 AI Provider: {ai_info['description_full']} will enhance your task{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}🤖 AI Provider info unavailable{Style.RESET_ALL}")

                # Initialize AI Task Creator
                ai_creator = AITaskCreator(project_root=str(Path.cwd()))

                # Run progressive creation wizard
                success, task_id, result = asyncio.run(ai_creator.create_task_progressive())

            if success:
                print(f"\n{Fore.GREEN}🎉 AI-Enhanced Task Created Successfully!{Style.RESET_ALL}")
                print(f"   Task ID: {Fore.CYAN}{task_id}{Style.RESET_ALL}")
                print(f"   File: {Path(result).name if result else 'N/A'}")
                print(f"   Location: mods/project_management/planning/todo/")

                if choice != '2':  # Progressive wizard
                    print(f"\n{Fore.CYAN}✨ Task created with Phase 4C enhancements:{Style.RESET_ALL}")
                    print(f"   🔍 Interactive context selection")
                    print(f"   🤖 Progressive AI enhancement")
                    print(f"   📊 Quality scoring and feedback")
                else:
                    print(f"\n{Fore.CYAN}✨ Task enhanced with real AI content generation{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}❌ Task creation failed: {result}{Style.RESET_ALL}")

        except ImportError as e:
            print(f"{Fore.RED}❌ AI Task Creator not available: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Falling back to basic task creation...{Style.RESET_ALL}")
            self._handle_quick_basic_task()
        except Exception as e:
            self.logger.error(f"AI task creation error: {e}")
            print(f"{Fore.RED}❌ Error in AI task creation: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Falling back to basic task creation...{Style.RESET_ALL}")
            self._handle_quick_basic_task()

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def _handle_quick_basic_task(self) -> None:
        """Handle basic quick task creation (original functionality)."""
        try:
            # Use ProjectPlanner if available for enhanced task creation
            if self.project_planner:
                print(f"{Fore.GREEN}⚡ Quick Task Creation{Style.RESET_ALL}")

                # Get basic task info
                title = input(f"{Fore.GREEN}Task title: {Style.RESET_ALL}").strip()
                if not title:
                    print(f"{Fore.YELLOW}Task creation cancelled.{Style.RESET_ALL}")
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
                                print(f"      {Style.DIM}... and {len(tasks) - 5} more{Style.RESET_ALL}")
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
        """Handle project cleanup option with comprehensive cleanup management."""
        print(f"\n{Fore.CYAN}🗑️ Project Cleanup Manager{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  WARNING: This will permanently delete project data!{Style.RESET_ALL}")

        try:
            # Get current project info
            project_root = self.indexer.root_path if self.indexer else os.getcwd()
            project_name = os.path.basename(project_root)

            print(f"\n{Fore.CYAN}📁 Current Project: {Fore.WHITE}{project_name}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📂 Project Path: {Fore.WHITE}{project_root}{Style.RESET_ALL}")

            # Analyze what can be cleaned
            cleanup_analysis = self._analyze_cleanup_targets(project_root, project_name)

            # Display cleanup menu
            while True:
                self._display_cleanup_menu(cleanup_analysis)

                choice = input(f"\n{Fore.GREEN}Select cleanup option (1-9 or 0 to cancel): {Style.RESET_ALL}").strip()

                if choice == "0":
                    print(f"{Fore.YELLOW}Cleanup cancelled.{Style.RESET_ALL}")
                    break
                elif choice == "1":
                    self._cleanup_index_data(project_root)
                elif choice == "2":
                    self._cleanup_deleted_files()
                elif choice == "3":
                    self._cleanup_logs(project_name)
                elif choice == "4":
                    self._cleanup_temp_files(project_root)
                elif choice == "5":
                    self._cleanup_project_settings(project_root)
                elif choice == "6":
                    self._cleanup_ai_cache()
                elif choice == "7":
                    self._cleanup_task_data()
                elif choice == "8":
                    self._selective_cleanup(cleanup_analysis)
                elif choice == "9":
                    self._complete_project_reset(project_root, project_name)
                    break  # Exit after complete reset
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter 1-9 or 0.{Style.RESET_ALL}")

                # Refresh analysis after cleanup
                cleanup_analysis = self._analyze_cleanup_targets(project_root, project_name)

        except Exception as e:
            self.logger.error(f"Error in project cleanup: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def _analyze_cleanup_targets(self, project_root: str, project_name: str) -> Dict[str, Any]:
        """Analyze what can be cleaned up in the project."""
        analysis = {
            "index_data": {"exists": False, "size": 0, "files": 0},
            "deleted_files": {"exists": False, "count": 0},
            "logs": {"exists": False, "size": 0, "files": 0},
            "temp_files": {"exists": False, "size": 0, "files": 0},
            "settings": {"exists": False, "size": 0, "files": 0},
            "ai_cache": {"exists": False, "size": 0, "files": 0},
            "task_data": {"exists": False, "size": 0, "files": 0},
            "total_size": 0
        }

        try:
            # Check index data (.index directory)
            index_dir = os.path.join(project_root, ".index")
            if os.path.exists(index_dir):
                size, files = self._calculate_directory_size(index_dir)
                analysis["index_data"] = {"exists": True, "size": size, "files": files}
                analysis["total_size"] += size

            # Check for deleted files in index (if indexer is available)
            if self.indexer:
                try:
                    index_status = self.indexer.is_index_complete()
                    deleted_count = index_status.get('deleted_count', 0)
                    if deleted_count > 0:
                        analysis["deleted_files"] = {"exists": True, "count": deleted_count}
                except Exception as e:
                    self.logger.debug(f"Error checking for deleted files: {e}")

            # Check logs directory
            logs_dir = "logs"
            if os.path.exists(logs_dir):
                # Count project-specific logs
                project_logs = [f for f in os.listdir(logs_dir)
                               if f.startswith(project_name) or f.startswith("indexing_")]
                if project_logs:
                    total_size = sum(os.path.getsize(os.path.join(logs_dir, f))
                                   for f in project_logs if os.path.isfile(os.path.join(logs_dir, f)))
                    analysis["logs"] = {"exists": True, "size": total_size, "files": len(project_logs)}
                    analysis["total_size"] += total_size

            # Check temp files (common temp patterns)
            temp_patterns = ["*.tmp", "*.temp", "*~", "*.bak", "*.old", "*.orig"]
            temp_size = 0
            temp_count = 0

            for root, dirs, files in os.walk(project_root):
                # Skip .index and other system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]

                for file in files:
                    if any(file.endswith(pattern.replace('*', '')) for pattern in temp_patterns) or file.startswith('.tmp'):
                        file_path = os.path.join(root, file)
                        try:
                            temp_size += os.path.getsize(file_path)
                            temp_count += 1
                        except OSError:
                            pass

            if temp_count > 0:
                analysis["temp_files"] = {"exists": True, "size": temp_size, "files": temp_count}
                analysis["total_size"] += temp_size

            # Check settings files
            settings_files = [".taskhero_setup.json", ".env.backup*", "*.log"]
            settings_size = 0
            settings_count = 0

            for pattern in settings_files:
                if '*' in pattern:
                    # Handle wildcard patterns
                    import glob
                    matches = glob.glob(os.path.join(project_root, pattern))
                    for match in matches:
                        if os.path.isfile(match):
                            try:
                                settings_size += os.path.getsize(match)
                                settings_count += 1
                            except OSError:
                                pass
                else:
                    file_path = os.path.join(project_root, pattern)
                    if os.path.exists(file_path):
                        try:
                            settings_size += os.path.getsize(file_path)
                            settings_count += 1
                        except OSError:
                            pass

            if settings_count > 0:
                analysis["settings"] = {"exists": True, "size": settings_size, "files": settings_count}
                analysis["total_size"] += settings_size

            # Check task management data
            task_dirs = ["taskheromd/project docs", "taskheromd/project planning"]
            task_size = 0
            task_count = 0

            for task_dir in task_dirs:
                task_path = os.path.join(project_root, task_dir)
                if os.path.exists(task_path):
                    size, files = self._calculate_directory_size(task_path)
                    task_size += size
                    task_count += files

            if task_count > 0:
                analysis["task_data"] = {"exists": True, "size": task_size, "files": task_count}
                analysis["total_size"] += task_size

        except Exception as e:
            self.logger.error(f"Error analyzing cleanup targets: {e}")

        return analysis

    def _calculate_directory_size(self, directory: str) -> tuple:
        """Calculate total size and file count of a directory."""
        total_size = 0
        file_count = 0

        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except OSError:
                        pass
        except Exception:
            pass

        return total_size, file_count

    def _display_cleanup_menu(self, analysis: Dict[str, Any]) -> None:
        """Display the cleanup options menu."""
        print(f"\n{Fore.CYAN}🧹 Cleanup Options:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*60}{Style.RESET_ALL}")

        total_recoverable = analysis["total_size"]

        # Option 1: Index Data
        index_info = analysis["index_data"]
        if index_info["exists"]:
            size_str = self._format_size(index_info["size"])
            print(f"{Fore.GREEN}1. 🗂️ Delete Index Data{Style.RESET_ALL} - {size_str} ({index_info['files']} files)")
            print(f"   {Fore.CYAN}   Removes all indexed embeddings, metadata, and descriptions{Style.RESET_ALL}")
        else:
            print(f"{Style.DIM}1. 🗂️ Delete Index Data - No index data found{Style.RESET_ALL}")

        # Option 2: Deleted Files
        deleted_info = analysis["deleted_files"]
        if deleted_info["exists"]:
            print(f"{Fore.GREEN}2. 🗑️ Clean Deleted Files{Style.RESET_ALL} - {deleted_info['count']} deleted files in index")
            print(f"   {Fore.CYAN}   Removes index entries for files that no longer exist{Style.RESET_ALL}")
        else:
            print(f"{Style.DIM}2. 🗑️ Clean Deleted Files - No deleted files found in index{Style.RESET_ALL}")

        # Option 3: Logs
        logs_info = analysis["logs"]
        if logs_info["exists"]:
            size_str = self._format_size(logs_info["size"])
            print(f"{Fore.GREEN}3. 📋 Clear Project Logs{Style.RESET_ALL} - {size_str} ({logs_info['files']} files)")
            print(f"   {Fore.CYAN}   Removes indexing logs and project-specific log files{Style.RESET_ALL}")
        else:
            print(f"{Style.DIM}3. 📋 Clear Project Logs - No logs found{Style.RESET_ALL}")

        # Option 4: Temp Files
        temp_info = analysis["temp_files"]
        if temp_info["exists"]:
            size_str = self._format_size(temp_info["size"])
            print(f"{Fore.GREEN}4. 🗑️ Remove Temp Files{Style.RESET_ALL} - {size_str} ({temp_info['files']} files)")
            print(f"   {Fore.CYAN}   Removes .tmp, .bak, .old, and other temporary files{Style.RESET_ALL}")
        else:
            print(f"{Style.DIM}4. 🗑️ Remove Temp Files - No temp files found{Style.RESET_ALL}")

        # Option 5: Settings
        settings_info = analysis["settings"]
        if settings_info["exists"]:
            size_str = self._format_size(settings_info["size"])
            print(f"{Fore.YELLOW}5. ⚙️ Reset Project Settings{Style.RESET_ALL} - {size_str} ({settings_info['files']} files)")
            print(f"   {Fore.CYAN}   Removes app settings and backup configurations{Style.RESET_ALL}")
        else:
            print(f"{Style.DIM}5. ⚙️ Reset Project Settings - No settings to reset{Style.RESET_ALL}")

        # Option 6: AI Cache
        print(f"{Fore.GREEN}6. 🤖 Clear AI Cache{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}   Clears AI conversation history and cached responses{Style.RESET_ALL}")

        # Option 7: Task Data
        task_info = analysis["task_data"]
        if task_info["exists"]:
            size_str = self._format_size(task_info["size"])
            print(f"{Fore.YELLOW}7. 📋 Clear Task Data{Style.RESET_ALL} - {size_str} ({task_info['files']} files)")
            print(f"   {Fore.CYAN}   Removes task management data and project planning files{Style.RESET_ALL}")
        else:
            print(f"{Style.DIM}7. 📋 Clear Task Data - No task data found{Style.RESET_ALL}")

        # Advanced options
        print(f"\n{Fore.YELLOW}Advanced Options:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}8. 🎯 Selective Cleanup{Style.RESET_ALL} - Choose specific items to delete")
        print(f"{Fore.RED}9. 💥 Complete Project Reset{Style.RESET_ALL} - Delete EVERYTHING and start fresh")

        print(f"\n{Fore.CYAN}0. ❌ Cancel Cleanup{Style.RESET_ALL}")

        if total_recoverable > 0:
            total_str = self._format_size(total_recoverable)
            print(f"\n{Fore.GREEN}💾 Total Space Recoverable: {Style.BRIGHT}{total_str}{Style.RESET_ALL}")

    def _cleanup_index_data(self, project_root: str) -> None:
        """Clean up index data (.index directory)."""
        index_dir = os.path.join(project_root, ".index")

        if not os.path.exists(index_dir):
            print(f"{Fore.YELLOW}No index data found to clean.{Style.RESET_ALL}")
            return

        # Calculate size before deletion
        size, files = self._calculate_directory_size(index_dir)
        size_str = self._format_size(size)

        print(f"\n{Fore.YELLOW}⚠️  About to delete index data:{Style.RESET_ALL}")
        print(f"   📂 Directory: {index_dir}")
        print(f"   📊 Size: {size_str}")
        print(f"   📄 Files: {files}")
        print(f"\n{Fore.RED}This will remove all embeddings, metadata, and descriptions!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}You will need to re-index your code to use AI features.{Style.RESET_ALL}")

        confirm = input(f"\n{Fore.RED}Type 'DELETE' to confirm: {Style.RESET_ALL}").strip()

        if confirm == "DELETE":
            try:
                import shutil
                shutil.rmtree(index_dir)
                print(f"\n{Fore.GREEN}✅ Successfully deleted index data ({size_str} recovered){Style.RESET_ALL}")

                # Reset indexer state
                self.indexer = None
                self.index_outdated = False

                # Clear last directory if it matches
                if self.settings_manager:
                    last_dir = self.settings_manager.get_last_directory()
                    if last_dir == project_root:
                        self.settings_manager.set_last_directory("")

            except Exception as e:
                print(f"{Fore.RED}❌ Error deleting index data: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Index data deletion cancelled.{Style.RESET_ALL}")

    def _cleanup_deleted_files(self) -> None:
        """Clean up deleted files from the index."""
        if not self.indexer:
            print(f"{Fore.YELLOW}No indexer available - cannot clean deleted files.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}🗑️ Cleaning Deleted Files from Index{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")

        try:
            # Check for deleted files
            index_status = self.indexer.is_index_complete()
            deleted_count = index_status.get('deleted_count', 0)

            if deleted_count == 0:
                print(f"{Fore.GREEN}✅ No deleted files found in index.{Style.RESET_ALL}")
                return

            print(f"{Fore.YELLOW}Found {deleted_count} deleted files in index.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}These are files that were indexed but no longer exist on disk.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Cleaning them up will improve search accuracy and reduce index size.{Style.RESET_ALL}")

            confirm = input(f"\n{Fore.GREEN}Clean up {deleted_count} deleted files? (y/N): {Style.RESET_ALL}").strip().lower()

            if confirm in ['y', 'yes']:
                print(f"\n{Fore.CYAN}🧹 Cleaning up deleted files...{Style.RESET_ALL}")

                # Perform the cleanup
                removed_count = self.indexer.cleanup_deleted_files()

                if removed_count > 0:
                    print(f"\n{Fore.GREEN}✅ Successfully cleaned up {removed_count} deleted files from index{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}💡 Index is now more accurate and up-to-date{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.YELLOW}No files were removed during cleanup.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Deleted files cleanup cancelled.{Style.RESET_ALL}")

        except Exception as e:
            self.logger.error(f"Error cleaning deleted files: {e}")
            print(f"{Fore.RED}❌ Error cleaning deleted files: {e}{Style.RESET_ALL}")

    def _cleanup_logs(self, project_name: str) -> None:
        """Clean up project-specific log files."""
        logs_dir = "logs"

        if not os.path.exists(logs_dir):
            print(f"{Fore.YELLOW}No logs directory found.{Style.RESET_ALL}")
            return

        # Find project-specific logs
        project_logs = []
        total_size = 0

        for file in os.listdir(logs_dir):
            if (file.startswith(project_name) or file.startswith("indexing_")) and os.path.isfile(os.path.join(logs_dir, file)):
                file_path = os.path.join(logs_dir, file)
                try:
                    size = os.path.getsize(file_path)
                    project_logs.append((file, file_path, size))
                    total_size += size
                except OSError:
                    pass

        if not project_logs:
            print(f"{Fore.YELLOW}No project logs found to clean.{Style.RESET_ALL}")
            return

        size_str = self._format_size(total_size)

        print(f"\n{Fore.YELLOW}⚠️  About to delete {len(project_logs)} log files:{Style.RESET_ALL}")
        print(f"   📊 Total size: {size_str}")

        # Show first few files
        for i, (filename, _, file_size) in enumerate(project_logs[:5]):
            file_size_str = self._format_size(file_size)
            print(f"   📄 {filename} ({file_size_str})")

        if len(project_logs) > 5:
            print(f"   📄 ... and {len(project_logs) - 5} more files")

        confirm = input(f"\n{Fore.YELLOW}Delete these log files? (y/N): {Style.RESET_ALL}").strip().lower()

        if confirm in ['y', 'yes']:
            deleted_count = 0
            deleted_size = 0

            for filename, file_path, file_size in project_logs:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    deleted_size += file_size
                except Exception as e:
                    print(f"{Fore.RED}❌ Error deleting {filename}: {e}{Style.RESET_ALL}")

            if deleted_count > 0:
                deleted_size_str = self._format_size(deleted_size)
                print(f"\n{Fore.GREEN}✅ Successfully deleted {deleted_count} log files ({deleted_size_str} recovered){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Log cleanup cancelled.{Style.RESET_ALL}")

    def _cleanup_temp_files(self, project_root: str) -> None:
        """Clean up temporary files."""
        temp_patterns = ["*.tmp", "*.temp", "*~", "*.bak", "*.old", "*.orig"]
        temp_files = []
        total_size = 0

        print(f"\n{Fore.CYAN}🔍 Scanning for temporary files...{Style.RESET_ALL}")

        for root, dirs, files in os.walk(project_root):
            # Skip .index and system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]

            for file in files:
                if any(file.endswith(pattern.replace('*', '')) for pattern in temp_patterns) or file.startswith('.tmp'):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        rel_path = os.path.relpath(file_path, project_root)
                        temp_files.append((rel_path, file_path, size))
                        total_size += size
                    except OSError:
                        pass

        if not temp_files:
            print(f"{Fore.GREEN}✅ No temporary files found to clean.{Style.RESET_ALL}")
            return

        size_str = self._format_size(total_size)

        print(f"\n{Fore.YELLOW}Found {len(temp_files)} temporary files ({size_str}):{Style.RESET_ALL}")

        # Show first few files
        for i, (rel_path, _, file_size) in enumerate(temp_files[:8]):
            file_size_str = self._format_size(file_size)
            print(f"   🗑️ {rel_path} ({file_size_str})")

        if len(temp_files) > 8:
            print(f"   🗑️ ... and {len(temp_files) - 8} more files")

        confirm = input(f"\n{Fore.YELLOW}Delete these temporary files? (y/N): {Style.RESET_ALL}").strip().lower()

        if confirm in ['y', 'yes']:
            deleted_count = 0
            deleted_size = 0

            for rel_path, file_path, file_size in temp_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    deleted_size += file_size
                except Exception as e:
                    print(f"{Fore.RED}❌ Error deleting {rel_path}: {e}{Style.RESET_ALL}")

            if deleted_count > 0:
                deleted_size_str = self._format_size(deleted_size)
                print(f"\n{Fore.GREEN}✅ Successfully deleted {deleted_count} temporary files ({deleted_size_str} recovered){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Temporary file cleanup cancelled.{Style.RESET_ALL}")

    def _cleanup_project_settings(self, project_root: str) -> None:
        """Clean up project settings and configuration files."""
        print(f"\n{Fore.RED}⚠️  WARNING: This will reset ALL project settings!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This includes:{Style.RESET_ALL}")
        print(f"   • Application settings")
        print(f"   • Environment backups")
        print(f"   • User preferences")
        print(f"   • AI provider configurations")

        confirm = input(f"\n{Fore.RED}Type 'RESET' to confirm settings reset: {Style.RESET_ALL}").strip()

        if confirm == "RESET":
            settings_files = [
                ".taskhero_setup.json",
                ".env.backup",
                ".env.backup.legacy"
            ]

            deleted_files = []
            deleted_size = 0

            for settings_file in settings_files:
                file_path = os.path.join(project_root, settings_file)
                if os.path.exists(file_path):
                    try:
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files.append(settings_file)
                        deleted_size += size
                    except Exception as e:
                        print(f"{Fore.RED}❌ Error deleting {settings_file}: {e}{Style.RESET_ALL}")

            # Clear env backups directory
            env_backups_dir = os.path.join(project_root, ".env_backups")
            if os.path.exists(env_backups_dir):
                try:
                    import shutil
                    backup_size, _ = self._calculate_directory_size(env_backups_dir)
                    shutil.rmtree(env_backups_dir)
                    deleted_files.append(".env_backups/")
                    deleted_size += backup_size
                except Exception as e:
                    print(f"{Fore.RED}❌ Error deleting .env_backups: {e}{Style.RESET_ALL}")

            if deleted_files:
                size_str = self._format_size(deleted_size)
                print(f"\n{Fore.GREEN}✅ Reset project settings:{Style.RESET_ALL}")
                for file in deleted_files:
                    print(f"   🗑️ {file}")
                print(f"\n{Fore.GREEN}💾 Space recovered: {size_str}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}💡 Settings will be recreated with defaults on next run.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No settings files found to reset.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Settings reset cancelled.{Style.RESET_ALL}")

    def _cleanup_ai_cache(self) -> None:
        """Clear AI cache and conversation history."""
        print(f"\n{Fore.CYAN}🤖 Clearing AI cache and conversation history...{Style.RESET_ALL}")

        # Clear AI manager cache if available
        if self.ai_manager and hasattr(self.ai_manager, 'clear_cache'):
            try:
                self.ai_manager.clear_cache()
                print(f"{Fore.GREEN}✅ AI conversation history cleared{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error clearing AI cache: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}AI cache clearing not available{Style.RESET_ALL}")

        print(f"{Fore.CYAN}💡 AI providers will start fresh on next interaction.{Style.RESET_ALL}")

    def _cleanup_task_data(self) -> None:
        """Clear task management data."""
        print(f"\n{Fore.YELLOW}⚠️  This will delete ALL task management data!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Including:{Style.RESET_ALL}")
        print(f"   • Project planning files")
        print(f"   • Task boards and statuses")
        print(f"   • Task history and metadata")

        confirm = input(f"\n{Fore.RED}Type 'DELETE' to confirm task data deletion: {Style.RESET_ALL}").strip()

        if confirm == "DELETE":
            task_dirs = ["taskheromd/project docs", "taskheromd/project planning"]
            deleted_size = 0
            deleted_dirs = []

            for task_dir in task_dirs:
                if os.path.exists(task_dir):
                    try:
                        import shutil
                        size, _ = self._calculate_directory_size(task_dir)
                        shutil.rmtree(task_dir)
                        deleted_dirs.append(task_dir)
                        deleted_size += size
                    except Exception as e:
                        print(f"{Fore.RED}❌ Error deleting {task_dir}: {e}{Style.RESET_ALL}")

            if deleted_dirs:
                size_str = self._format_size(deleted_size)
                print(f"\n{Fore.GREEN}✅ Deleted task management data:{Style.RESET_ALL}")
                for dir_name in deleted_dirs:
                    print(f"   🗑️ {dir_name}")
                print(f"\n{Fore.GREEN}💾 Space recovered: {size_str}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No task data found to delete.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Task data deletion cancelled.{Style.RESET_ALL}")

    def _selective_cleanup(self, analysis: Dict[str, Any]) -> None:
        """Allow user to selectively choose what to clean."""
        print(f"\n{Fore.CYAN}🎯 Selective Cleanup{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Select items to delete (space-separated numbers):{Style.RESET_ALL}")

        options = []
        option_num = 1

        if analysis["index_data"]["exists"]:
            size_str = self._format_size(analysis["index_data"]["size"])
            options.append(("Index Data", f"🗂️ Index Data ({size_str})", "index_data"))
            print(f"   {option_num}. 🗂️ Index Data ({size_str})")
            option_num += 1

        if analysis["deleted_files"]["exists"]:
            count = analysis["deleted_files"]["count"]
            options.append(("Deleted Files", f"🗑️ Deleted Files ({count} files)", "deleted_files"))
            print(f"   {option_num}. 🗑️ Deleted Files ({count} files)")
            option_num += 1

        if analysis["logs"]["exists"]:
            size_str = self._format_size(analysis["logs"]["size"])
            options.append(("Logs", f"📋 Project Logs ({size_str})", "logs"))
            print(f"   {option_num}. 📋 Project Logs ({size_str})")
            option_num += 1

        if analysis["temp_files"]["exists"]:
            size_str = self._format_size(analysis["temp_files"]["size"])
            options.append(("Temp Files", f"🗑️ Temporary Files ({size_str})", "temp_files"))
            print(f"   {option_num}. 🗑️ Temporary Files ({size_str})")
            option_num += 1

        if analysis["settings"]["exists"]:
            size_str = self._format_size(analysis["settings"]["size"])
            options.append(("Settings", f"⚙️ Project Settings ({size_str})", "settings"))
            print(f"   {option_num}. ⚙️ Project Settings ({size_str})")
            option_num += 1

        if analysis["task_data"]["exists"]:
            size_str = self._format_size(analysis["task_data"]["size"])
            options.append(("Task Data", f"📋 Task Data ({size_str})", "task_data"))
            print(f"   {option_num}. 📋 Task Data ({size_str})")
            option_num += 1

        if not options:
            print(f"{Fore.YELLOW}No cleanup options available.{Style.RESET_ALL}")
            return

        selection = input(f"\n{Fore.GREEN}Enter numbers (e.g., '1 3 5') or 'all': {Style.RESET_ALL}").strip()

        if not selection:
            print(f"{Fore.YELLOW}Selective cleanup cancelled.{Style.RESET_ALL}")
            return

        selected_items = []

        if selection.lower() == 'all':
            selected_items = options
        else:
            try:
                numbers = [int(x) for x in selection.split()]
                for num in numbers:
                    if 1 <= num <= len(options):
                        selected_items.append(options[num - 1])
                    else:
                        print(f"{Fore.RED}Invalid option: {num}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter numbers separated by spaces.{Style.RESET_ALL}")
                return

        if not selected_items:
            print(f"{Fore.YELLOW}No valid items selected.{Style.RESET_ALL}")
            return

        # Show confirmation
        total_size = 0
        for item in selected_items:
            item_type = item[2]
            if item_type == "deleted_files":
                # Deleted files don't have a size, just count
                continue
            elif item_type in analysis and "size" in analysis[item_type]:
                total_size += analysis[item_type]["size"]

        total_size_str = self._format_size(total_size)

        print(f"\n{Fore.YELLOW}⚠️  About to delete:{Style.RESET_ALL}")
        for _, description, _ in selected_items:
            print(f"   {description}")
        if total_size > 0:
            print(f"\n{Fore.GREEN}Total space to recover: {total_size_str}{Style.RESET_ALL}")

        confirm = input(f"\n{Fore.RED}Type 'DELETE' to confirm: {Style.RESET_ALL}").strip()

        if confirm == "DELETE":
            print(f"\n{Fore.CYAN}🧹 Performing selective cleanup...{Style.RESET_ALL}")

            for name, description, item_type in selected_items:
                print(f"\n{Fore.CYAN}Cleaning {name}...{Style.RESET_ALL}")

                if item_type == "index_data":
                    self._cleanup_index_data(os.getcwd())
                elif item_type == "deleted_files":
                    self._cleanup_deleted_files()
                elif item_type == "logs":
                    project_name = os.path.basename(os.getcwd())
                    self._cleanup_logs(project_name)
                elif item_type == "temp_files":
                    self._cleanup_temp_files(os.getcwd())
                elif item_type == "settings":
                    self._cleanup_project_settings(os.getcwd())
                elif item_type == "task_data":
                    self._cleanup_task_data()

            print(f"\n{Fore.GREEN}🎉 Selective cleanup completed!{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Selective cleanup cancelled.{Style.RESET_ALL}")

    def _complete_project_reset(self, project_root: str, project_name: str) -> None:
        """Perform complete project reset - delete everything."""
        print(f"\n{Fore.RED}💥 COMPLETE PROJECT RESET{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.RED}⚠️  DANGER: This will delete ALL project data!{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}This will permanently remove:{Style.RESET_ALL}")
        print(f"   • All index data and embeddings")
        print(f"   • All logs and history")
        print(f"   • All settings and configurations")
        print(f"   • All task management data")
        print(f"   • All temporary and backup files")
        print(f"   • ALL project-related data")

        print(f"\n{Fore.RED}🚨 THIS CANNOT BE UNDONE! 🚨{Style.RESET_ALL}")

        # Three-stage confirmation
        confirm1 = input(f"\n{Fore.RED}Type the project name '{project_name}' to continue: {Style.RESET_ALL}").strip()

        if confirm1 != project_name:
            print(f"{Fore.YELLOW}Project reset cancelled.{Style.RESET_ALL}")
            return

        confirm2 = input(f"\n{Fore.RED}Type 'I UNDERSTAND' to confirm you understand this is permanent: {Style.RESET_ALL}").strip()

        if confirm2 != "I UNDERSTAND":
            print(f"{Fore.YELLOW}Project reset cancelled.{Style.RESET_ALL}")
            return

        confirm3 = input(f"\n{Fore.RED}Type 'DELETE EVERYTHING' for final confirmation: {Style.RESET_ALL}").strip()

        if confirm3 != "DELETE EVERYTHING":
            print(f"{Fore.YELLOW}Project reset cancelled.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.RED}🔥 Performing complete project reset...{Style.RESET_ALL}")

        total_deleted_size = 0
        deleted_items = []

        # Delete index data
        index_dir = os.path.join(project_root, ".index")
        if os.path.exists(index_dir):
            try:
                import shutil
                size, _ = self._calculate_directory_size(index_dir)
                shutil.rmtree(index_dir)
                deleted_items.append(f"Index data ({self._format_size(size)})")
                total_deleted_size += size
            except Exception as e:
                print(f"{Fore.RED}❌ Error deleting index: {e}{Style.RESET_ALL}")

        # Delete logs
        logs_dir = "logs"
        if os.path.exists(logs_dir):
            try:
                import shutil
                size, _ = self._calculate_directory_size(logs_dir)
                shutil.rmtree(logs_dir)
                deleted_items.append(f"All logs ({self._format_size(size)})")
                total_deleted_size += size
            except Exception as e:
                print(f"{Fore.RED}❌ Error deleting logs: {e}{Style.RESET_ALL}")

        # Delete settings files (excluding .taskhero_setup.json)
        settings_patterns = [".env_backups", ".env.backup*"]
        for pattern in settings_patterns:
            if '*' in pattern:
                import glob
                matches = glob.glob(os.path.join(project_root, pattern))
                for match in matches:
                    try:
                        if os.path.isfile(match):
                            size = os.path.getsize(match)
                            os.remove(match)
                            total_deleted_size += size
                        elif os.path.isdir(match):
                            import shutil
                            size, _ = self._calculate_directory_size(match)
                            shutil.rmtree(match)
                            total_deleted_size += size
                    except Exception as e:
                        print(f"{Fore.RED}❌ Error deleting {match}: {e}{Style.RESET_ALL}")
            else:
                file_path = os.path.join(project_root, pattern)
                if os.path.exists(file_path):
                    try:
                        if os.path.isfile(file_path):
                            size = os.path.getsize(file_path)
                            os.remove(file_path)
                            total_deleted_size += size
                        elif os.path.isdir(file_path):
                            import shutil
                            size, _ = self._calculate_directory_size(file_path)
                            shutil.rmtree(file_path)
                            total_deleted_size += size
                    except Exception as e:
                        print(f"{Fore.RED}❌ Error deleting {pattern}: {e}{Style.RESET_ALL}")

        deleted_items.append("All settings and configurations")

        # Delete task data
        task_dirs = ["taskheromd"]
        for task_dir in task_dirs:
            if os.path.exists(task_dir):
                try:
                    import shutil
                    size, _ = self._calculate_directory_size(task_dir)
                    shutil.rmtree(task_dir)
                    deleted_items.append(f"Task data ({self._format_size(size)})")
                    total_deleted_size += size
                except Exception as e:
                    print(f"{Fore.RED}❌ Error deleting {task_dir}: {e}{Style.RESET_ALL}")

        # Reset internal state
        self.indexer = None
        self.index_outdated = False

        if self.settings_manager:
            self.settings_manager.set_last_directory("")

        # Clear AI cache
        if self.ai_manager and hasattr(self.ai_manager, 'clear_cache'):
            try:
                self.ai_manager.clear_cache()
                deleted_items.append("AI cache and history")
            except Exception:
                pass

        total_size_str = self._format_size(total_deleted_size)

        print(f"\n{Fore.GREEN}🎉 COMPLETE PROJECT RESET SUCCESSFUL!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}Deleted items:{Style.RESET_ALL}")
        for item in deleted_items:
            print(f"   ✅ {item}")

        print(f"\n{Fore.GREEN}💾 Total space recovered: {Style.BRIGHT}{total_size_str}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}🚀 Project has been completely reset!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}You can now start fresh by indexing your code again.{Style.RESET_ALL}")

        input(f"\n{Fore.GREEN}Press Enter to return to main menu...{Style.RESET_ALL}")

    def _handle_ai_settings(self) -> None:
        """Handle AI settings option."""
        try:
            from ..ui import AISettingsUI
            from ..settings import AISettingsManager

            print(f"\n{Fore.CYAN}🤖 AI Settings Configuration{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

            # Create AI settings manager and UI
            ai_settings_manager = AISettingsManager()
            ai_settings_ui = AISettingsUI(ai_settings_manager, self.git_manager)

            # Initialize
            ai_settings_ui.initialize()

            # Run the AI settings menu in async context
            asyncio.run(ai_settings_ui.handle_ai_settings_menu())

        except Exception as e:
            self.logger.error(f"Error in AI settings: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def _handle_create_about_document(self) -> None:
        """Handle create about document option."""
        print(f"\n{Fore.CYAN}📝 Create About Document{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

        try:
            # Show simple options
            print(f"\n{Fore.GREEN}Options:{Style.RESET_ALL}")
            print(f"  1. 🚀 Generate about.md (AI-powered)")
            print(f"  0. ← Back to main menu")

            choice = input(f"\n{Fore.GREEN}Select option (1 or 0): {Style.RESET_ALL}").strip()

            if choice == "0":
                print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                return
            elif choice == "1":
                # Generate AI-powered about.md
                print(f"\n{Fore.CYAN}🚀 Generating AI-Powered About Document{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
                
                from ..project_management.about_manager import AboutManager
                
                # Initialize AboutManager with AI and settings managers
                about_manager = AboutManager(
                    project_root=str(Path.cwd()),
                    ai_manager=self.ai_manager,
                    settings_manager=self.settings_manager
                )
                
                # Generate with truly dynamic AI analysis
                success, message, file_path = about_manager.create_dynamic_about()
                
                if success:
                    print(f"\n{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}📁 File saved to: {file_path}{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}❌ {message}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Invalid option. Please select 1 or 0.{Style.RESET_ALL}")

        except Exception as e:
            self.logger.error(f"Error creating about document: {e}")
            print(f"{Fore.RED}Error creating about document: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
