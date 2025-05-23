#!/usr/bin/env python
"""
VerbalCodeAI - Terminal Application

A simple terminal-based interface for the VerbalCodeAI code assistant.
Also provides an HTTP API server when run with the --serve option.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import re

import colorama
import uvicorn
from colorama import Fore, Style
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

try:
    from mods.banners import display_animated_banner
    from mods.llms import get_current_provider
    from mods.code.agent_mode import AgentMode
    from mods.code.decisions import ChatHandler, FileSelector, ProjectAnalyzer
    from mods.code.indexer import FileIndexer
    from mods.http_api import create_app
    from mods.terminal_ui import StreamingResponseHandler, display_response
    from mods.terminal_utils import (
        clear_screen,
        create_progress_bar,
        create_spinner,
        get_terminal_size,
        render_markdown,
    )
    from mods.project_management import TaskManager, ProjectTemplates, ProjectPlanner
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)


def setup_logging() -> logging.Logger:
    """Set up logging for the application.

    Returns:
        logging.Logger: The logger for the application.
    """
    colorama.init()

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    try:
        for file in logs_dir.glob("*"):
            try:
                file.unlink()
            except (PermissionError, OSError):
                pass
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Could not clean up log directory: {e}{Style.RESET_ALL}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"verbalcodeai_{timestamp}.log"
    print(f"{Fore.CYAN}Logging to: {Style.BRIGHT}{log_file}{Style.RESET_ALL}")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    class StatisticsFilter(logging.Filter):
        """Filter log records to separate statistics and errors."""

        def filter(self, record: logging.LogRecord) -> bool:
            """Filter log records to separate statistics and errors.

            Args:
                record (logging.LogRecord): The log record to filter.

            Returns:
                bool: True if the record should be included, False otherwise.
            """
            return (hasattr(record, "msg") and "[STAT]" in str(record.msg)) or record.levelno >= logging.ERROR

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(StatisticsFilter())
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    try:
        indexer_log_file = logs_dir / f"indexer_{timestamp}.log"
        indexer_handler = logging.FileHandler(indexer_log_file, mode="w", encoding="utf-8")
        indexer_handler.setLevel(logging.DEBUG)
        indexer_handler.setFormatter(file_formatter)
        logging.getLogger("VerbalCodeAI.Indexer").addHandler(indexer_handler)
    except (PermissionError, OSError) as e:
        print(f"{Fore.YELLOW}Warning: Could not create indexer log file: {e}{Style.RESET_ALL}")
        logging.getLogger("VerbalCodeAI.Indexer").addHandler(file_handler)

    logging.getLogger("VerbalCodeAI").setLevel(logging.DEBUG)
    logging.getLogger("VerbalCodeAI.Indexer").setLevel(logging.DEBUG)

    return logging.getLogger("VerbalCodeAI")


class VerbalCodeAI:
    """Main application class for the VerbalCodeAI terminal interface."""

    def __init__(self) -> None:
        """Initialize the application."""
        load_dotenv()

        self.logger: logging.Logger = logging.getLogger("VerbalCodeAI")
        self.indexer: Optional[FileIndexer] = None
        self.file_selector: Optional[FileSelector] = None
        self.project_analyzer: Optional[ProjectAnalyzer] = None
        self.chat_handler: Optional[ChatHandler] = None
        self.settings_path: str = os.path.join(os.path.dirname(__file__), ".app_settings.json")
        self.last_directory: str = self._load_last_directory()
        self.project_info: Dict[str, Any] = {}
        self.recent_projects: List[Dict[str, str]] = self._load_recent_projects()
        self.index_outdated: bool = False
        self.chat_history: List[Dict[str, str]] = []
        self.agent_mode_instance: Optional[AgentMode] = None
        
        # Project Management Components
        self.task_manager: Optional[TaskManager] = None
        self.project_templates: Optional[ProjectTemplates] = None
        self.project_planner: Optional[ProjectPlanner] = None

        self.enable_markdown_rendering: bool = self._get_env_bool("ENABLE_MARKDOWN_RENDERING", True)
        self.show_thinking_blocks: bool = self._get_env_bool("SHOW_THINKING_BLOCKS", False)
        self.enable_streaming_mode: bool = self._get_env_bool("ENABLE_STREAMING_MODE", False)

    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean value from environment variables.

        Args:
            key (str): The environment variable key.
            default (bool): The default value if the key is not found. Defaults to False.

        Returns:
            bool: The boolean value.
        """
        value: str = os.getenv(key, str(default)).upper()
        return value in ("TRUE", "YES", "1", "Y", "T")

    def _load_last_directory(self) -> str:
        """Load the last indexed directory from settings.

        Returns:
            str: The last indexed directory.
        """
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    settings: Dict[str, Any] = json.load(f)
                    return settings.get("last_directory", "")
            return ""
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return ""

    def _save_last_directory(self, directory: str) -> None:
        """Save the last indexed directory to settings.

        Args:
            directory (str): The directory to save.
        """
        try:
            settings: Dict[str, Any] = {}
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    settings = json.load(f)
            settings["last_directory"] = directory
            self._add_to_recent_projects(directory)

            with open(self.settings_path, "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")

    def _load_recent_projects(self) -> List[Dict[str, str]]:
        """Load the list of recent projects from settings.

        Returns:
            List[Dict[str, str]]: List of recent projects with path and timestamp.
        """
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    settings: Dict[str, Any] = json.load(f)
                    return settings.get("recent_projects", [])
            return []
        except Exception as e:
            self.logger.error(f"Error loading recent projects: {e}")
            return []

    def _add_to_recent_projects(self, directory: str) -> None:
        """Add a directory to the recent projects list.

        Args:
            directory (str): The directory to add.
        """
        try:
            project_entry: Dict[str, str] = {
                "path": directory,
                "name": os.path.basename(directory),
                "timestamp": datetime.now().isoformat(),
            }

            self.recent_projects = [p for p in self.recent_projects if p.get("path") != directory]
            self.recent_projects.insert(0, project_entry)
            self.recent_projects = self.recent_projects[:10]

            settings: Dict[str, Any] = {}
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    settings = json.load(f)

            settings["recent_projects"] = self.recent_projects

            with open(self.settings_path, "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error adding to recent projects: {e}")

    def display_menu(self) -> None:
        """Display the main menu."""
        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "TaskHeroAI - AI-Powered Code & Project Assistant" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

        if not self.indexer:
            print(Fore.YELLOW + "No code indexed yet. Please select option 1 to index code." + Style.RESET_ALL)
        elif self.index_outdated:
            print(
                Fore.RED
                + Style.BRIGHT
                + "[INDEX OUTDATED] "
                + Style.RESET_ALL
                + Fore.YELLOW
                + "Please select option 1 to update the index."
                + Style.RESET_ALL
            )

        print(
            Fore.YELLOW
            + "WARNING: Consider using a smaller OpenRouter model for descriptions (Free One) to reduce costs."
            + Style.RESET_ALL
        )
        print(
            Fore.YELLOW
            + "WARNING: Chat with AI and Max Chat Mode are expensive. Use Agent Mode for cheaper and faster responses."
            + Style.RESET_ALL
        )
        
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "AI Features" + Style.RESET_ALL)
        print(Fore.GREEN + "1. " + Style.BRIGHT + "Index Code" + Style.RESET_ALL)
        print(Fore.GREEN + "2. " + Style.BRIGHT + "Chat with AI (Expensive)" + Style.RESET_ALL)
        print(Fore.GREEN + "3. " + Style.BRIGHT + "Max Chat Mode (Expensive)" + Style.RESET_ALL)
        print(Fore.GREEN + "4. " + Style.BRIGHT + "Agent Mode (Cheapest Option)" + Style.RESET_ALL)
        print(Fore.GREEN + "5. " + Style.BRIGHT + "Force Reindex" + Style.RESET_ALL)
        print(Fore.GREEN + "6. " + Style.BRIGHT + "View Indexed Files" + Style.RESET_ALL)
        print(Fore.GREEN + "7. " + Style.BRIGHT + "View Project Info" + Style.RESET_ALL)
        print(Fore.GREEN + "8. " + Style.BRIGHT + "Recent Projects" + Style.RESET_ALL)
        
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Project Management" + Style.RESET_ALL)
        print(Fore.MAGENTA + "9. " + Style.BRIGHT + "📋 Task Management Dashboard" + Style.RESET_ALL)
        
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Maintenance" + Style.RESET_ALL)
        print(Fore.RED + "10. " + Style.BRIGHT + "🗑️  Project Cleanup Manager" + Style.RESET_ALL)

        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Settings" + Style.RESET_ALL)

        markdown_status: str = (
            f"{Fore.GREEN}Enabled{Style.RESET_ALL}"
            if self.enable_markdown_rendering
            else f"{Fore.RED}Disabled{Style.RESET_ALL}"
        )
        print(f"{Fore.GREEN}11. {Style.BRIGHT}Toggle Markdown Rendering{Style.RESET_ALL} [{markdown_status}]")

        thinking_status: str = (
            f"{Fore.GREEN}Enabled{Style.RESET_ALL}"
            if self.show_thinking_blocks
            else f"{Fore.RED}Disabled{Style.RESET_ALL}"
        )
        print(f"{Fore.GREEN}12. {Style.BRIGHT}Toggle Thinking Blocks{Style.RESET_ALL} [{thinking_status}]")

        streaming_status: str = (
            f"{Fore.GREEN}Enabled{Style.RESET_ALL}"
            if self.enable_streaming_mode
            else f"{Fore.RED}Disabled{Style.RESET_ALL}"
        )
        print(f"{Fore.GREEN}13. {Style.BRIGHT}Toggle Streaming Mode{Style.RESET_ALL} [{streaming_status}]")

        print(f"{Fore.GREEN}14. {Style.BRIGHT}Clear Screen{Style.RESET_ALL}")
        print(f"{Fore.GREEN}15. {Style.BRIGHT}Exit{Style.RESET_ALL}")

        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

    def index_directory(self, force_reindex: bool = False) -> None:
        """Index a directory.

        Args:
            force_reindex (bool): Whether to force reindexing of all files. Defaults to False.
        """
        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(
            Fore.CYAN
            + Style.BRIGHT
            + ("Force Reindex Directory" if force_reindex else "Index Code Directory")
            + Style.RESET_ALL
        )
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

        if self.indexer and (self.index_outdated or force_reindex):
            directory: str = self.indexer.root_path
            print(f"{Fore.YELLOW}Using current directory: {Fore.CYAN}{directory}{Style.RESET_ALL}")
        else:
            default_dir: str = self.last_directory if self.last_directory else os.getcwd()
            print(
                f"{Fore.YELLOW}Enter directory path {Fore.CYAN}(default: {default_dir}){Fore.YELLOW}:{Style.RESET_ALL}"
            )
            directory: str = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip()

            if not directory:
                directory = default_dir

            if not os.path.isdir(directory):
                print(f"{Fore.RED}Error: '{directory}' is not a valid directory.{Style.RESET_ALL}")
                return

        print(f"{Fore.CYAN}Indexing directory: {Style.BRIGHT}{directory}{Style.RESET_ALL}")

        try:
            if not self.indexer or self.indexer.root_path != directory:
                self.logger.info(f"Creating indexer for directory: {directory}")
                self.indexer: FileIndexer = FileIndexer(directory)

                self.file_selector: FileSelector = FileSelector()

                self.project_analyzer: ProjectAnalyzer = ProjectAnalyzer(self.indexer)
                self.chat_handler: ChatHandler = ChatHandler(self.indexer, self.file_selector)
            else:
                self.logger.info(f"Using existing indexer for directory: {directory}")

            index_status: Dict[str, Any] = self.indexer.is_index_complete()
            self.index_outdated: bool = not index_status.get("complete", False)

            # Pre-scan files and get user confirmation
            print(f"{Fore.CYAN}Scanning files to be indexed...{Style.RESET_ALL}")
            
            spinner = create_spinner()
            stop_spinner_flag: List[bool] = [False]

            def spin_fn():
                while not stop_spinner_flag[0]:
                    spinner()
                    time.sleep(0.1)

            spinner_thread: threading.Thread = threading.Thread(target=spin_fn)
            spinner_thread.daemon = True
            spinner_thread.start()
            stop_spinner_flag[0] = False

            try:
                if force_reindex:
                    files_to_process: List[str] = self.indexer._get_all_indexable_files()
                    operation_type = "reindex"
                else:
                    files_to_process = self.indexer.get_outdated_files()
                    operation_type = "index"
            except Exception as e:
                self.logger.error(f"Error scanning files: {e}", exc_info=True)
                files_to_process = []
                operation_type = "index"
            finally:
                stop_spinner_flag[0] = True
                if spinner_thread.is_alive():
                    spinner_thread.join(timeout=1.0)
                terminal_width, _ = get_terminal_size()
                sys.stdout.write("\r" + " " * terminal_width + "\r")
                sys.stdout.flush()

            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Create file list log
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_list_path = logs_dir / f"files_to_{operation_type}_{timestamp}.txt"
            
            try:
                with open(file_list_path, 'w', encoding='utf-8') as f:
                    f.write(f"Files to {operation_type} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Directory: {directory}\n")
                    f.write(f"Total files: {len(files_to_process)}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for file_path in files_to_process:
                        # Make path relative to directory for better readability
                        try:
                            rel_path = os.path.relpath(file_path, directory)
                            f.write(f"{rel_path}\n")
                        except ValueError:
                            # If relpath fails, use the full path
                            f.write(f"{file_path}\n")
                
                print(f"{Fore.GREEN}File list saved to: {Fore.CYAN}{file_list_path}{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Could not save file list: {e}{Style.RESET_ALL}")

            # Display summary and ask for confirmation
            if files_to_process:
                print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}📋 {operation_type.title()} Summary:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   Directory: {Style.BRIGHT}{directory}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   Files to {operation_type}: {Style.BRIGHT}{len(files_to_process)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   File list saved to: {Style.BRIGHT}{file_list_path.name}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                
                # Ask for thread count
                default_threads = int(os.getenv("MAX_THREADS", "8"))
                print(f"\n{Fore.YELLOW}🧵 Thread Configuration:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   Current default: {Style.BRIGHT}{default_threads}{Style.NORMAL} threads{Style.RESET_ALL}")
                thread_input = input(f"{Fore.GREEN}Enter number of threads to use (1-32, default {default_threads}): {Style.RESET_ALL}").strip()
                
                if thread_input:
                    try:
                        thread_count = int(thread_input)
                        if 1 <= thread_count <= 32:
                            # Temporarily set the thread count for this session
                            os.environ["MAX_THREADS"] = str(thread_count)
                            print(f"{Fore.GREEN}✓ Using {thread_count} threads for this operation{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}⚠ Invalid thread count. Using default: {default_threads}{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.YELLOW}⚠ Invalid input. Using default: {default_threads}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}Using default: {default_threads} threads{Style.RESET_ALL}")
                
                # Ask for confirmation
                print(f"\n{Fore.YELLOW}⚠ This may take some time depending on the number of files and your system performance.{Style.RESET_ALL}")
                confirmation = input(f"{Fore.GREEN}Do you want to proceed with {operation_type}ing? (y/N): {Style.RESET_ALL}").strip().lower()
                
                if confirmation not in ['y', 'yes']:
                    print(f"{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
                    return
                    
                print(f"{Fore.GREEN}✓ Proceeding with {operation_type}ing {len(files_to_process)} files...{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✓ No files need to be {operation_type}ed. Index is up to date!{Style.RESET_ALL}")
                return

            self.logger.info("Starting indexing process")
            print(f"\n{Fore.CYAN}Starting {operation_type}ing process...{Style.RESET_ALL}")

            outdated_files: List[str] = []
            indexed_files: List[str] = []

            # Progress tracking variables
            indexed_count: List[int] = [0]
            start_time: float = time.time()
            total_files: int = len(files_to_process)
            activity_chars: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            activity_index: List[int] = [0]
            last_update_time: List[float] = [time.time()]
            recent_completion_times: List[float] = []  # Track recent completion times
            heartbeat_active: List[bool] = [True]

            def progress_callback() -> bool:
                """Enhanced callback function to report indexing progress.
                
                This gets called each time a file is completed.
                    
                Returns:
                    bool: Always returns False.
                """
                nonlocal recent_completion_times
                
                indexed_count[0] += 1
                current_time = time.time()
                
                # Track completion times for better ETA calculation
                recent_completion_times.append(current_time)
                # Keep only last 10 completion times for rolling average
                if len(recent_completion_times) > 10:
                    recent_completion_times.pop(0)
                
                last_update_time[0] = current_time
                
                elapsed: float = current_time - start_time
                
                # Calculate files per second using recent completions for more accurate ETA
                if len(recent_completion_times) >= 2:
                    recent_window = recent_completion_times[-1] - recent_completion_times[0]
                    files_in_window = len(recent_completion_times) - 1
                    files_per_second = files_in_window / recent_window if recent_window > 0 else 0
                else:
                    files_per_second = indexed_count[0] / elapsed if elapsed > 0 else 0
                
                # Calculate ETA with better logic
                remaining_files = total_files - indexed_count[0]
                if files_per_second > 0 and remaining_files > 0:
                    eta_seconds = remaining_files / files_per_second
                    # Cap unrealistic ETAs
                    if eta_seconds > 7200:  # More than 2 hours
                        eta_str = "calculating..."
                    elif eta_seconds > 3600:  # More than 1 hour
                        eta_str = f"{int(eta_seconds / 3600)}h {int((eta_seconds % 3600) / 60)}m"
                    elif eta_seconds > 60:  # More than 1 minute
                        eta_str = f"{int(eta_seconds / 60)}m {int(eta_seconds % 60)}s"
                    else:
                        eta_str = f"{int(eta_seconds)}s"
                else:
                    eta_str = "calculating..."
                
                # Progress calculation
                percent: int = int((indexed_count[0] / total_files) * 100) if total_files > 0 else 0
                
                # Progress bar
                terminal_width: int
                terminal_width, _ = get_terminal_size()
                bar_width: int = min(40, terminal_width - 70 if terminal_width > 90 else 20)
                
                filled_width: int = 0
                if total_files > 0:
                    filled_width = int(bar_width * indexed_count[0] / total_files)
                
                bar: str = f"{Fore.GREEN}{'█' * filled_width}{Fore.WHITE}{'░' * (bar_width - filled_width)}"
                
                # Activity indicator
                if indexed_count[0] == total_files:
                    activity = f"{Fore.GREEN}✓{Style.RESET_ALL}"
                    heartbeat_active[0] = False  # Stop heartbeat when complete
                else:
                    activity_index[0] = (activity_index[0] + 1) % len(activity_chars)
                    activity = f"{Fore.YELLOW}{activity_chars[activity_index[0]]}{Style.RESET_ALL}"
                
                # Elapsed time display
                elapsed_str = f"{int(elapsed / 60)}m {int(elapsed % 60)}s" if elapsed >= 60 else f"{int(elapsed)}s"
                
                # Clear line and write progress
                sys.stdout.write("\r" + " " * terminal_width)
                
                # Create the progress line with better formatting
                progress_line = (
                    f"\r{activity} [{bar}{Fore.CYAN}] {Fore.YELLOW}{percent}%{Fore.CYAN} | "
                    f"{Style.BRIGHT}{indexed_count[0]}/{total_files}{Style.NORMAL} files | "
                    f"{Fore.MAGENTA}{files_per_second:.1f}/s{Fore.CYAN} | "
                    f"⏱️ {Fore.GREEN}{elapsed_str}{Fore.CYAN} | "
                    f"ETA: {Fore.YELLOW}{eta_str}{Style.RESET_ALL}"
                )
                
                sys.stdout.write(progress_line)
                sys.stdout.flush()
                
                # Add newline when complete
                if indexed_count[0] == total_files:
                    sys.stdout.write("\n")
                    sys.stdout.flush()

                return False

            # Start a heartbeat thread for activity indication between file completions
            heartbeat_thread = None
            
            def heartbeat_worker():
                """Background thread to show activity even when no files are completing"""
                while heartbeat_active[0] and indexed_count[0] < total_files:
                    current_time = time.time()
                    time_since_last_update = current_time - last_update_time[0]
                    
                    # Only show heartbeat if it's been more than 2 seconds since last file completion
                    if time_since_last_update > 2.0:
                        elapsed = current_time - start_time
                        elapsed_str = f"{int(elapsed / 60)}m {int(elapsed % 60)}s" if elapsed >= 60 else f"{int(elapsed)}s"
                        
                        # Calculate files per second
                        if len(recent_completion_times) >= 2:
                            recent_window = recent_completion_times[-1] - recent_completion_times[0]
                            files_in_window = len(recent_completion_times) - 1
                            files_per_second = files_in_window / recent_window if recent_window > 0 else 0
                        else:
                            files_per_second = indexed_count[0] / elapsed if elapsed > 0 else 0
                        
                        percent = int((indexed_count[0] / total_files) * 100) if total_files > 0 else 0
                        
                        # Heartbeat activity indicator
                        activity_index[0] = (activity_index[0] + 1) % len(activity_chars)
                        activity = f"{Fore.CYAN}{activity_chars[activity_index[0]]}{Style.RESET_ALL}"
                        
                        # Progress bar
                        terminal_width, _ = get_terminal_size()
                        bar_width = min(40, terminal_width - 70 if terminal_width > 90 else 20)
                        filled_width = int(bar_width * indexed_count[0] / total_files) if total_files > 0 else 0
                        bar = f"{Fore.GREEN}{'█' * filled_width}{Fore.WHITE}{'░' * (bar_width - filled_width)}"
                        
                        # Show "processing..." status
                        progress_line = (
                            f"\r{activity} [{bar}{Fore.CYAN}] {Fore.YELLOW}{percent}%{Fore.CYAN} | "
                            f"{Style.BRIGHT}{indexed_count[0]}/{total_files}{Style.NORMAL} files | "
                            f"{Fore.MAGENTA}{files_per_second:.1f}/s{Fore.CYAN} | "
                            f"⏱️ {Fore.GREEN}{elapsed_str}{Fore.CYAN} | "
                            f"{Fore.BLUE}Processing...{Style.RESET_ALL}"
                        )
                        
                        sys.stdout.write("\r" + " " * terminal_width)
                        sys.stdout.write(progress_line)
                        sys.stdout.flush()
                    
                    time.sleep(0.5)  # Update heartbeat every 0.5 seconds
            
            # Start heartbeat thread
            heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
            heartbeat_thread.start()

            if force_reindex:
                self.logger.info("Force reindexing all files")
                if total_files > 0:
                    try:
                        indexed_files = self.indexer.force_reindex_all(progress_callback)
                    finally:
                        # Stop heartbeat thread
                        heartbeat_active[0] = False
                        if heartbeat_thread and heartbeat_thread.is_alive():
                            heartbeat_thread.join(timeout=1.0)
                        
                        terminal_width, _ = get_terminal_size()
                        sys.stdout.write("\r" + " " * terminal_width + "\r")
                        sys.stdout.flush()
                else:
                    # Stop heartbeat thread
                    heartbeat_active[0] = False
                    if heartbeat_thread and heartbeat_thread.is_alive():
                        heartbeat_thread.join(timeout=1.0)
                    indexed_files = []

                self.logger.info(f"[STAT] Force reindexed {len(indexed_files)} files")
                print(
                    f"{Fore.GREEN}✓ Force reindexed {Style.BRIGHT}{len(indexed_files)}{Style.NORMAL} files{Style.RESET_ALL}"
                )
            else:
                if files_to_process:
                    try:
                        indexed_files = self.indexer.index_directory(progress_callback)
                    finally:
                        # Stop heartbeat thread
                        heartbeat_active[0] = False
                        if heartbeat_thread and heartbeat_thread.is_alive():
                            heartbeat_thread.join(timeout=1.0)
                        
                        terminal_width, _ = get_terminal_size()
                        sys.stdout.write("\r" + " " * terminal_width + "\r")
                        sys.stdout.flush()

                    self.logger.info(f"[STAT] Indexed {len(indexed_files)} files")
                    print(
                        f"{Fore.GREEN}✓ Indexed {Style.BRIGHT}{len(indexed_files)}{Style.NORMAL} files{Style.RESET_ALL}"
                    )
                else:
                    # Stop heartbeat thread
                    heartbeat_active[0] = False
                    if heartbeat_thread and heartbeat_thread.is_alive():
                        heartbeat_thread.join(timeout=1.0)
                    print(f"{Fore.GREEN}✓ All files are already indexed{Style.RESET_ALL}")

            self._save_last_directory(directory)

            if indexed_files:
                self.index_outdated = False
                print(f"{Fore.GREEN}✓ Indexing completed successfully!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}📁 You can now use chat or agent mode to interact with your codebase.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No new files were indexed.{Style.RESET_ALL}")

        except Exception as e:
            # Stop heartbeat thread in case of error
            try:
                heartbeat_active[0] = False
                if heartbeat_thread and heartbeat_thread.is_alive():
                    heartbeat_thread.join(timeout=1.0)
            except:
                pass  # Ignore cleanup errors
            
            self.logger.error(f"Error during indexing: {e}", exc_info=True)
            print(f"{Fore.RED}Error during indexing: {e}{Style.RESET_ALL}")
            if "Ollama" in str(e):
                print(f"{Fore.YELLOW}Make sure Ollama is running and accessible at the configured host.{Style.RESET_ALL}")

    async def agent_mode(self) -> None:
        """Run the AI agent mode for interactive codebase exploration."""
        if not self.indexer:
            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            return

        if not self.agent_mode_instance:
            self.agent_mode_instance: AgentMode = AgentMode(self.indexer)

        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Agent Mode" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(f"{Fore.YELLOW}In Agent Mode, the AI can use tools to explore and understand your codebase.")
        print(f"{Fore.YELLOW}Available tools:")
        print(f"{Fore.YELLOW}  Search tools: embed_search, semantic_search, grep, regex_advanced_search, file_type_search")
        print(f"{Fore.YELLOW}  File tools: read_file, file_stats, directory_tree, get_file_description, get_file_metadata")
        print(f"{Fore.YELLOW}  Code analysis: find_functions, find_classes, find_usage, cross_reference, code_analysis,")
        print(f"{Fore.YELLOW}                 get_functions, get_classes, get_variables, get_imports, explain_code")
        print(f"{Fore.YELLOW}  Version control: git_history, version_control_search, search_imports")
        print(f"{Fore.YELLOW}  Project tools: get_project_description, get_instructions, create_instructions_template")
        print(f"{Fore.YELLOW}  Memory tools: add_memory, get_memories, search_memories")
        print(f"{Fore.YELLOW}  System tools: run_command, read_terminal, kill_terminal, list_terminals")
        print(f"{Fore.YELLOW}  Helper tools: ask_buddy (with context-aware second opinions)")
        print(f"{Fore.YELLOW}  Web tools: google_search, ddg_search, bing_news_search, fetch_webpage, get_base_knowledge")
        print(
            f"{Fore.YELLOW}Type your questions about the codebase. Type '{Fore.RED}exit{Fore.YELLOW}' to return to the main menu.{Style.RESET_ALL}"
        )

        while True:
            provider, model = get_current_provider()
            print(
                f"\n{Fore.YELLOW}Current provider: {Fore.CYAN}{provider.upper()}"
                f"{Fore.YELLOW}, model: {Fore.CYAN}{model}{Style.RESET_ALL}"
            )
            print(
                f"\n{Fore.GREEN}Your question (or '{Fore.RED}exit{Fore.GREEN}' to return to menu):{Style.RESET_ALL}"
            )
            user_input: str = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()

            if user_input.lower() == "exit":
                break

            if not user_input:
                continue

            try:
                print(f"\n{Fore.YELLOW}Processing your question with Agent Mode...{Style.RESET_ALL}")
                self.logger.info(f"[STAT] Processing question in Agent Mode: {user_input[:50]}...")

                await self.agent_mode_instance.process_query(user_input)

            except Exception as e:
                self.logger.error(f"Error in Agent Mode: {e}", exc_info=True)
                print(f"\n{Fore.RED}Error in Agent Mode: {e}{Style.RESET_ALL}")

    def chat_with_ai(self, max_chat_mode: bool = False) -> None:
        """Chat with the AI about code.

        Args:
            max_chat_mode (bool): Whether to use Max Chat mode, which sends full file contents to the AI. Defaults to False.
        """
        if not self.indexer:
            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            return

        # Ensure all required components are initialized
        if not self.file_selector:
            self.logger.info("Initializing FileSelector")
            self.file_selector = FileSelector()

        if not self.project_analyzer:
            self.logger.info("Initializing ProjectAnalyzer")
            self.project_analyzer = ProjectAnalyzer(self.indexer)

        if not self.chat_handler:
            self.logger.info("Initializing ChatHandler")
            try:
                self.chat_handler = ChatHandler(self.indexer, self.file_selector, self.project_info)
            except Exception as e:
                self.logger.error(f"Failed to initialize ChatHandler: {e}")
                print(f"\n{Fore.RED}Error: Failed to initialize chat system: {e}{Style.RESET_ALL}")
                return

        if not self.project_info:
            print(f"\n{Fore.YELLOW}Loading project information before starting chat...{Style.RESET_ALL}")
            try:
                self.project_info = self.project_analyzer.load_project_info()
                if not self.project_info:
                    print(f"\n{Fore.YELLOW}Collecting project information before starting chat...{Style.RESET_ALL}")
                    self.project_info = self.project_analyzer.collect_project_info()
                
                # Update chat handler with project info
                self.chat_handler.set_project_info(self.project_info)
            except Exception as e:
                self.logger.error(f"Failed to load/collect project info: {e}")
                print(f"\n{Fore.YELLOW}Warning: Could not load project information: {e}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Continuing without project context...{Style.RESET_ALL}")
                self.project_info = {}

        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        if max_chat_mode:
            print(Fore.CYAN + Style.BRIGHT + "Max Chat Mode (Token Intensive)" + Style.RESET_ALL)
            print(
                Fore.RED + "WARNING: This mode sends full file contents to the AI and uses more tokens." + Style.RESET_ALL
            )
        else:
            print(Fore.CYAN + Style.BRIGHT + "Chat with AI" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(
            f"{Fore.YELLOW}Type your questions about the codebase. Type '{Fore.RED}exit{Fore.YELLOW}' to return to the main menu.{Style.RESET_ALL}"
        )

        while True:
            print(
                f"\n{Fore.GREEN}Your question (or '{Fore.RED}exit{Fore.GREEN}' to return to menu):{Style.RESET_ALL}"
            )
            user_input: str = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()

            if user_input.lower() == "exit":
                break

            if not user_input:
                continue

            try:
                print(f"\n{Fore.YELLOW}Processing your question...{Style.RESET_ALL}")
                self.logger.info(f"[STAT] Processing question: {user_input[:50]}...")

                response: Union[str, Any]
                relevant_files: List[str]
                response, relevant_files = self.chat_handler.process_query(
                    user_input,
                    max_chat_mode=max_chat_mode,
                    streaming=self.enable_streaming_mode,
                )

                if relevant_files:
                    print(f"\n{Fore.CYAN}{Style.BRIGHT}Relevant Files:{Style.RESET_ALL}")
                    display_count: int = min(5, len(relevant_files))
                    for i, file_path in enumerate(relevant_files[:display_count], 1):
                        file_name: str = os.path.basename(file_path)
                        print(f"{Fore.GREEN}{i}. {Fore.WHITE}{file_name} {Fore.CYAN}({file_path}){Style.RESET_ALL}")

                    if len(relevant_files) > 5:
                        remaining: int = len(relevant_files) - 5
                        print(f"{Fore.YELLOW}+ {remaining} more file{'s' if remaining > 1 else ''}{Style.RESET_ALL}")

                    if max_chat_mode:
                        print(
                            f"\n{Fore.YELLOW}Including full content of {len(relevant_files)} files in the context.{Style.RESET_ALL}"
                        )
                else:
                    print(
                        f"{Fore.YELLOW}No relevant files found. Generating response based on general knowledge.{Style.RESET_ALL}"
                    )

                terminal_width: int
                terminal_width, _ = get_terminal_size()
                print(f"\n{Fore.CYAN}{Style.BRIGHT}AI Response:{Style.RESET_ALL}")
                print(Fore.CYAN + "-" * min(terminal_width, 80) + Style.RESET_ALL)

                if self.enable_streaming_mode:
                    self.logger.info("[STAT] Processing streaming AI response")

                    handler: StreamingResponseHandler = StreamingResponseHandler(
                        enable_markdown_rendering=self.enable_markdown_rendering,
                        show_thinking_blocks=self.show_thinking_blocks,
                        logger=self.logger,
                    )

                    def on_complete(complete_response: str):
                        self.chat_handler.add_to_history("assistant", complete_response)

                    try:
                        asyncio.run(handler.process_stream(response, on_complete))

                        self.logger.info("[STAT] Streaming AI response completed successfully")
                    except Exception as e:
                        self.logger.error(f"Error processing streaming response: {e}")
                        print(f"\n{Fore.RED}Error processing response: {e}{Style.RESET_ALL}")
                else:
                    self.logger.info("[STAT] AI response generated successfully")

                    display_response(
                        response,
                        enable_markdown_rendering=self.enable_markdown_rendering,
                        show_thinking_blocks=self.show_thinking_blocks,
                    )

                print(Fore.CYAN + "-" * min(terminal_width, 80) + Style.RESET_ALL)

                self.chat_history = self.chat_handler.get_chat_history(max_messages=10)

            except Exception as e:
                self.logger.error(f"Error generating response: {e}", exc_info=True)
                print(f"\n{Fore.RED}{Style.BRIGHT}Error generating response: {e}{Style.RESET_ALL}")

    def view_indexed_files(self) -> None:
        """View information about indexed files."""
        if not self.indexer:
            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            return

        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Indexed Files" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

        try:
            self.logger.info("[STAT] Viewing indexed files information")

            index_status: Dict[str, Any] = self.indexer.is_index_complete()
            status_str: str = "Complete" if index_status["complete"] else "Incomplete"
            status_color: str = Fore.GREEN if index_status["complete"] else Fore.YELLOW
            print(f"{Fore.CYAN}Index Status: {status_color}{Style.BRIGHT}{status_str}{Style.RESET_ALL}")

            if not index_status["complete"] and "reason" in index_status:
                print(f"{Fore.YELLOW}Reason: {index_status['reason']}{Style.RESET_ALL}")

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

            print(f"\n{Fore.CYAN}{Style.BRIGHT}Sample Indexed Files:{Style.RESET_ALL}")
            try:
                sample_files = self.indexer.get_sample_files(5)
                if sample_files:
                    for i, file in enumerate(sample_files, 1):
                        print(f"{Fore.GREEN}{i}. {Fore.WHITE}{file}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No files have been indexed yet.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error retrieving sample files: {e}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            input()

        except Exception as e:
            self.logger.error(f"Error viewing indexed files: {e}", exc_info=True)
            print(f"{Fore.RED}{Style.BRIGHT}Error viewing indexed files: {e}{Style.RESET_ALL}")

    def view_project_info(self) -> None:
        """View information about the project."""
        if not self.indexer:
            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            return

        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Project Information" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

        if not hasattr(self, "project_info") or not self.project_info:
            print(f"{Fore.YELLOW}No project information available yet.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Collecting project information...{Style.RESET_ALL}")

            if not self.project_analyzer:
                self.project_analyzer = ProjectAnalyzer(self.indexer)

            self.project_info = self.project_analyzer.load_project_info()
            if not self.project_info:
                self.project_info = self.project_analyzer.collect_project_info()

            if self.chat_handler:
                self.chat_handler.set_project_info(self.project_info)

        if not self.project_info:
            print(f"{Fore.RED}Failed to collect project information.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            input()
            return

        print(f"\n{Fore.CYAN}{Style.BRIGHT}Project Summary:{Style.RESET_ALL}")

        terminal_width, _ = get_terminal_size()

        markdown_content = "# Project Summary\n\n"

        # Enhanced field mapping for better display
        enhanced_fields = [
            ("Project Name", "project_name"),
            ("Type", "project_type"),
            ("Purpose", "purpose"),
            ("Target Audience", "target_audience"),
            ("Complexity Level", "complexity_level"),
            ("Languages", "languages"),
            ("Frameworks & Tools", "frameworks"),
            ("Architecture", "architecture"),
            ("Core Features", "core_features"),
            ("Project Structure", "structure"),
            ("Data Handling", "data_handling"),
            ("User Interface", "user_interface"),
            ("Development Setup", "development_setup"),
            ("Integration", "integration"),
            ("Notable Aspects", "notable_aspects"),
            ("Other Notes", "other_notes"),
        ]

        for display_name, field_name in enhanced_fields:
            if field_name in self.project_info and self.project_info[field_name]:
                value = self.project_info[field_name]
                if isinstance(value, list):
                    if len(value) > 0:  # Only show if list has content
                        markdown_content += f"## {display_name}\n\n"
                        for item in value:
                            markdown_content += f"• {item}\n"
                        markdown_content += "\n"
                else:
                    # Clean up the value and ensure it's meaningful
                    if value and value.strip() and value.lower() not in ['unknown', 'n/a', 'none']:
                        markdown_content += f"## {display_name}\n\n{value}\n\n"

        # Add analysis metadata if available
        if 'analysis_metadata' in self.project_info:
            metadata = self.project_info['analysis_metadata']
            markdown_content += "## Analysis Details\n\n"
            markdown_content += f"• **Files Analyzed:** {metadata.get('files_analyzed', 'N/A')}\n"
            markdown_content += f"• **Analysis Date:** {metadata.get('analysis_date', 'N/A')[:19].replace('T', ' ')}\n"
            
            if 'files_by_category' in metadata:
                categories = metadata['files_by_category']
                total_files = sum(categories.values())
                if total_files > 0:
                    markdown_content += f"• **Total Project Files:** {total_files}\n"
                    markdown_content += f"• **File Categories:** "
                    cat_details = []
                    for cat, count in categories.items():
                        if count > 0:
                            cat_details.append(f"{count} {cat.replace('_', ' ')}")
                    markdown_content += ", ".join(cat_details) + "\n"
            markdown_content += "\n"

        rendered_content = render_markdown(markdown_content, width=terminal_width-2)
        print(rendered_content)

        print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()

        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Indexed Files" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

        try:
            self.logger.info("[STAT] Viewing indexed files information")

            index_status = self.indexer.is_index_complete()
            status_str = "Complete" if index_status["complete"] else "Incomplete"
            status_color = Fore.GREEN if index_status["complete"] else Fore.YELLOW
            print(f"{Fore.CYAN}Index Status: {status_color}{Style.BRIGHT}{status_str}{Style.RESET_ALL}")

            if not index_status["complete"] and "reason" in index_status:
                print(f"{Fore.YELLOW}Reason: {index_status['reason']}{Style.RESET_ALL}")

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

            print(f"\n{Fore.CYAN}{Style.BRIGHT}Sample Indexed Files:{Style.RESET_ALL}")
            try:
                sample_files = self.indexer.get_sample_files(5)
                if sample_files:
                    for i, file in enumerate(sample_files, 1):
                        print(f"{Fore.GREEN}{i}. {Fore.WHITE}{file}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No files have been indexed yet.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error retrieving sample files: {e}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            input()

        except Exception as e:
            self.logger.error(f"Error viewing indexed files: {e}", exc_info=True)
            print(f"{Fore.RED}{Style.BRIGHT}Error viewing indexed files: {e}{Style.RESET_ALL}")

    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format.

        Args:
            size_bytes (int): Size in bytes.

        Returns:
            str: Human-readable size.
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        if size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def collect_project_info(self, batch_size: int = 10) -> Dict[str, Any]:
        """Collect and analyze project information to provide context for AI responses.

        This method is now a wrapper around the ProjectAnalyzer.collect_project_info method.

        Args:
            batch_size (int): Number of files to process in each batch. Defaults to 10.

        Returns:
            Dict[str, Any]: Dictionary containing project information.
        """
        if not self.indexer:
            self.logger.warning("Cannot collect project info: No code has been indexed yet")
            return {}

        if not self.project_analyzer:
            self.project_analyzer = ProjectAnalyzer(self.indexer)

        project_info = self.project_analyzer.collect_project_info(batch_size)

        if self.chat_handler:
            self.chat_handler.set_project_info(project_info)

        self.project_info = project_info

        if project_info:
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Project Summary:{Style.RESET_ALL}")
            if "project_name" in project_info:
                print(f"{Fore.WHITE}Project: {Fore.GREEN}{project_info['project_name']}{Style.RESET_ALL}")
            if "purpose" in project_info:
                print(f"{Fore.WHITE}Purpose: {Fore.YELLOW}{project_info['purpose']}{Style.RESET_ALL}")
            if "languages" in project_info and project_info["languages"]:
                print(f"{Fore.WHITE}Languages: {Fore.MAGENTA}{', '.join(project_info['languages'])}{Style.RESET_ALL}")
            if "frameworks" in project_info and project_info["frameworks"]:
                print(f"{Fore.WHITE}Frameworks: {Fore.BLUE}{', '.join(project_info['frameworks'])}{Style.RESET_ALL}")

        return project_info

    def view_recent_projects(self) -> None:
        """View and select from recent projects."""
        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Recent Projects" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

        if not self.recent_projects:
            print(f"{Fore.YELLOW}No recent projects found.{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            input()
            return

        print(f"{Fore.YELLOW}Select a project to load:{Style.RESET_ALL}")

        for i, project in enumerate(self.recent_projects, 1):
            name = project.get("name", os.path.basename(project.get("path", "Unknown")))
            path = project.get("path", "Unknown")
            timestamp = project.get("timestamp", "Unknown")

            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pass

            print(f"{Fore.GREEN}{i}. {Fore.WHITE}{name} {Fore.CYAN}({path}) {Fore.YELLOW}[{timestamp}]{Style.RESET_ALL}")

        print(f"{Fore.GREEN}0. {Fore.WHITE}Cancel{Style.RESET_ALL}")

        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}Enter your choice (0-{len(self.recent_projects)}): {Style.RESET_ALL}").strip()

                if choice == "0":
                    return

                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(self.recent_projects):
                    selected_project = self.recent_projects[choice_idx]
                    project_path = selected_project.get("path")

                    if os.path.isdir(project_path):
                        print(f"{Fore.GREEN}Loading project: {project_path}{Style.RESET_ALL}")
                        
                        # Set the last directory and reinitialize everything
                        self.last_directory = project_path
                        self._save_last_directory(project_path)
                        
                        # Initialize all components for the selected project
                        try:
                            self.indexer = FileIndexer(project_path)
                            self.file_selector = FileSelector()
                            self.project_analyzer = ProjectAnalyzer(self.indexer)
                            
                            # Check if index exists and is complete
                            index_status = self.indexer.is_index_complete()
                            if index_status.get('complete', False):
                                print(f"{Fore.GREEN}✓ Loaded project with complete index{Style.RESET_ALL}")
                                
                                # Load project info if available
                                try:
                                    self.project_info = self.project_analyzer.load_project_info()
                                    if not self.project_info:
                                        self.project_info = {}
                                except Exception as e:
                                    self.logger.warning(f"Could not load project info: {e}")
                                    self.project_info = {}
                            else:
                                print(f"{Fore.YELLOW}⚠ Project has incomplete index. Consider reindexing.{Style.RESET_ALL}")
                                self.index_outdated = True
                                self.project_info = {}
                            
                            # Initialize chat handler
                            try:
                                self.chat_handler = ChatHandler(self.indexer, self.file_selector, self.project_info)
                            except Exception as e:
                                self.logger.warning(f"Could not initialize chat handler: {e}")
                                self.chat_handler = None
                            
                            print(f"{Fore.GREEN}✓ Project loaded successfully!{Style.RESET_ALL}")
                            
                        except Exception as e:
                            print(f"{Fore.RED}Error loading project: {e}{Style.RESET_ALL}")
                            # Reset components on error
                            self.indexer = None
                            self.file_selector = None
                            self.project_analyzer = None
                            self.chat_handler = None
                            self.project_info = {}
                        
                        return
                    else:
                        print(f"{Fore.RED}Error: Directory no longer exists: {project_path}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter a number between 0 and {len(self.recent_projects)}.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")

    def clean_slate(self) -> None:
        """Enhanced project cleanup - manage individual projects or reset all data."""
        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🗑️  PROJECT CLEANUP MANAGER" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        
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
        
        try:
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
    
    def _discover_indexed_projects(self) -> List[Dict[str, str]]:
        """Discover all indexed projects by scanning for .index directories."""
        projects = []
        
        # Check current directory
        if os.path.exists(".index"):
            projects.append({
                "name": os.path.basename(os.getcwd()),
                "path": os.getcwd(),
                "index_dir": ".index",
                "type": "current"
            })
        
        # Check recent projects
        for recent_project in self.recent_projects:
            project_path = recent_project.get("path")
            if project_path and os.path.isdir(project_path):
                index_dir = os.path.join(project_path, ".index")
                if os.path.exists(index_dir):
                    # Check if already added
                    if not any(p["path"] == project_path for p in projects):
                        projects.append({
                            "name": recent_project.get("name", os.path.basename(project_path)),
                            "path": project_path,
                            "index_dir": index_dir,
                            "type": "recent"
                        })
        
        # Sort by name for consistent display
        projects.sort(key=lambda x: x["name"].lower())
        return projects
    
    def _delete_specific_project(self, projects: List[Dict[str, str]]) -> None:
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
    
    def _delete_multiple_projects(self, projects: List[Dict[str, str]]) -> None:
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
    
    def _confirm_and_delete_project(self, project: Dict[str, str]) -> None:
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
                # Remove from recent projects if it exists there
                self._remove_from_recent_projects(project['path'])
                
                # Reset current app state if this is the active project
                if (self.indexer and 
                    hasattr(self.indexer, 'root_path') and 
                    self.indexer.root_path == project['path']):
                    self._reset_app_state()
        else:
            print(f"{Fore.GREEN}✓ Operation cancelled.{Style.RESET_ALL}")
    
    def _delete_projects_batch(self, projects: List[Dict[str, str]]) -> None:
        """Delete multiple projects."""
        print(f"\n{Fore.YELLOW}🗑️  Deleting {len(projects)} project(s)...{Style.RESET_ALL}")
        
        deleted_count = 0
        errors = []
        
        for project in projects:
            try:
                if self._delete_project_index(project, show_progress=False):
                    deleted_count += 1
                    self._remove_from_recent_projects(project['path'])
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
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Successfully deleted {deleted_count} project(s){Style.RESET_ALL}")
        
        if errors:
            print(f"{Fore.YELLOW}⚠️  {len(errors)} error(s) occurred:{Style.RESET_ALL}")
            for error in errors:
                print(f"  {Fore.RED}❌ {error}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()
    
    def _delete_all_projects_and_reset(self) -> None:
        """Delete all projects and reset everything (original clean slate functionality)."""
        print(f"\n{Fore.RED}⚠️  WARNING: This will permanently delete ALL generated data!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}The following will be deleted:{Style.RESET_ALL}")
        
        # List what will be deleted
        items_to_delete = []
        
        # Check for .index directories in current directory and any indexed project
        if self.indexer:
            index_dir = self.indexer.index_dir
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
        if os.path.exists(self.settings_path):
            items_to_delete.append(f"📄 {os.path.basename(self.settings_path)} (app settings)")
        
        # Check for any other index directories that might exist
        for item in os.listdir('.'):
            if os.path.isdir(item) and item.startswith('.index'):
                if f"📁 {item}/" not in [x.split()[1] for x in items_to_delete]:
                    items_to_delete.append(f"📁 {item}/ (orphaned index)")
        
        # Check recent projects for their indices
        for recent_project in self.recent_projects:
            project_path = recent_project.get("path")
            if project_path and os.path.isdir(project_path):
                index_dir = os.path.join(project_path, ".index")
                if os.path.exists(index_dir):
                    project_name = recent_project.get("name", os.path.basename(project_path))
                    items_to_delete.append(f"📁 {index_dir}/ ({project_name} index)")
        
        if not items_to_delete:
            print(f"{Fore.GREEN}✓ No generated files found to delete.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}The application state is already clean.{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            input()
            return
        
        for item in items_to_delete:
            print(f"  {Fore.RED}❌ {item}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Additional actions:{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}🔄 Reset application state (indexer, chat history, etc.){Style.RESET_ALL}")
        print(f"  {Fore.CYAN}📝 Clear recent projects list{Style.RESET_ALL}")
        
        print(f"\n{Fore.RED}⚠️  This action cannot be undone!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}You will need to re-index your projects after this operation.{Style.RESET_ALL}")
        
        # Get confirmation
        confirmation = input(f"\n{Fore.YELLOW}Are you absolutely sure you want to proceed? Type 'DELETE' to confirm: {Style.RESET_ALL}").strip()
        
        if confirmation != "DELETE":
            print(f"{Fore.GREEN}✓ Operation cancelled. No files were deleted.{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            input()
            return
        
        # Final confirmation
        final_confirm = input(f"{Fore.RED}Last chance! Type 'YES' to permanently delete all data: {Style.RESET_ALL}").strip().upper()
        
        if final_confirm != "YES":
            print(f"{Fore.GREEN}✓ Operation cancelled. No files were deleted.{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            input()
            return
        
        # Perform the deletion
        print(f"\n{Fore.YELLOW}🗑️  Deleting files...{Style.RESET_ALL}")
        
        deleted_count = 0
        errors = []
        
        try:
            # Delete index directories
            for item in [".index"]:
                if os.path.exists(item):
                    try:
                        import shutil
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
                        import shutil
                        shutil.rmtree(index_dir)
                        print(f"{Fore.GREEN}✓ Deleted: {index_dir}/{Style.RESET_ALL}")
                        deleted_count += 1
                    except Exception as e:
                        errors.append(f"Failed to delete {index_dir}/: {e}")
            
            # Delete recent project indices
            for recent_project in self.recent_projects:
                project_path = recent_project.get("path")
                if project_path and os.path.isdir(project_path):
                    index_dir = os.path.join(project_path, ".index")
                    if os.path.exists(index_dir):
                        try:
                            import shutil
                            shutil.rmtree(index_dir)
                            project_name = recent_project.get("name", os.path.basename(project_path))
                            print(f"{Fore.GREEN}✓ Deleted: {project_name} index{Style.RESET_ALL}")
                            deleted_count += 1
                        except Exception as e:
                            errors.append(f"Failed to delete {project_name} index: {e}")
            
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
            if os.path.exists(self.settings_path):
                try:
                    os.remove(self.settings_path)
                    print(f"{Fore.GREEN}✓ Deleted: {os.path.basename(self.settings_path)}{Style.RESET_ALL}")
                    deleted_count += 1
                except Exception as e:
                    errors.append(f"Failed to delete {self.settings_path}: {e}")
            
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
        print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()
    
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
        if os.path.exists(self.settings_path):
            try:
                os.remove(self.settings_path)
                print(f"{Fore.GREEN}✓ Deleted: {os.path.basename(self.settings_path)}{Style.RESET_ALL}")
                deleted_count += 1
                # Reset recent projects since settings are gone
                self.recent_projects = []
            except Exception as e:
                errors.append(f"Failed to delete {self.settings_path}: {e}")
        
        # Show results
        print(f"\n{Fore.GREEN}✅ Successfully cleaned up {deleted_count} items{Style.RESET_ALL}")
        
        if errors:
            print(f"{Fore.YELLOW}⚠️  {len(errors)} errors occurred:{Style.RESET_ALL}")
            for error in errors:
                print(f"  {Fore.RED}❌ {error}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()
    
    def _delete_project_index(self, project: Dict[str, str], show_progress: bool = True) -> bool:
        """Delete a project's index directory."""
        try:
            if os.path.exists(project['index_dir']):
                import shutil
                shutil.rmtree(project['index_dir'])
                if show_progress:
                    print(f"{Fore.GREEN}✓ Deleted project index: {project['name']}{Style.RESET_ALL}")
                return True
            else:
                if show_progress:
                    print(f"{Fore.YELLOW}⚠ Index not found: {project['name']}{Style.RESET_ALL}")
                return False
        except Exception as e:
            if show_progress:
                print(f"{Fore.RED}❌ Error deleting {project['name']}: {e}{Style.RESET_ALL}")
            return False
    
    def _remove_from_recent_projects(self, project_path: str) -> None:
        """Remove a project from the recent projects list."""
        self.recent_projects = [p for p in self.recent_projects if p.get('path') != project_path]
        try:
            # Save updated recent projects
            settings = {}
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    settings = json.load(f)
            
            settings["recent_projects"] = self.recent_projects
            settings["last_directory"] = ""  # Clear last directory if it was this project
            
            with open(self.settings_path, "w") as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to update recent projects: {e}")
    
    def _reset_app_state(self) -> None:
        """Reset the application state."""
        self.indexer = None
        self.file_selector = None
        self.project_analyzer = None
        self.chat_handler = None
        self.project_info = {}
        self.index_outdated = False
        self.chat_history = []
        self.agent_mode_instance = None
        self.last_directory = ""
    
    def _get_directory_size(self, directory: str) -> int:
        """Get the total size of a directory."""
        total_size = 0
        if os.path.exists(directory):
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        return total_size

    def toggle_markdown_rendering(self) -> None:
        """Toggle markdown rendering on/off."""
        self.enable_markdown_rendering = not self.enable_markdown_rendering
        status = "enabled" if self.enable_markdown_rendering else "disabled"
        print(f"\n{Fore.CYAN}Markdown rendering is now {Fore.GREEN if self.enable_markdown_rendering else Fore.RED}{status}{Style.RESET_ALL}")

        self._update_env_setting("ENABLE_MARKDOWN_RENDERING", str(self.enable_markdown_rendering).upper())

        print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()

    def toggle_thinking_blocks(self) -> None:
        """Toggle showing thinking blocks on/off."""
        self.show_thinking_blocks = not self.show_thinking_blocks
        status = "enabled" if self.show_thinking_blocks else "disabled"
        print(f"\n{Fore.CYAN}Showing thinking blocks is now {Fore.GREEN if self.show_thinking_blocks else Fore.RED}{status}{Style.RESET_ALL}")

        self._update_env_setting("SHOW_THINKING_BLOCKS", str(self.show_thinking_blocks).upper())

        print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()

    def toggle_streaming_mode(self) -> None:
        """Toggle streaming mode on/off."""
        self.enable_streaming_mode = not self.enable_streaming_mode
        status = "enabled" if self.enable_streaming_mode else "disabled"
        print(f"\n{Fore.CYAN}Streaming mode is now {Fore.GREEN if self.enable_streaming_mode else Fore.RED}{status}{Style.RESET_ALL}")

        self._update_env_setting("ENABLE_STREAMING_MODE", str(self.enable_streaming_mode).upper())

        print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()

    def _update_env_setting(self, key: str, value: str) -> None:
        """Update a setting in the .env file.

        Args:
            key (str): The key to update.
            value (str): The new value.
        """
        try:
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            if not os.path.exists(env_path):
                self.logger.warning(f"Cannot update {key} in .env file: File not found")
                return

            with open(env_path, "r") as f:
                lines = f.readlines()

            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    updated = True
                    break

            if not updated:
                lines.append(f"{key}={value}\n")

            with open(env_path, "w") as f:
                f.writelines(lines)

            self.logger.info(f"Updated {key}={value} in .env file")
        except Exception as e:
            self.logger.error(f"Error updating {key} in .env file: {e}")

    def run(self) -> None:
        """Run the application."""
        # Try to initialize indexer from last directory if available
        if not self.indexer and self.last_directory and os.path.isdir(self.last_directory):
            self.logger.info(f"Attempting to load previous project from: {self.last_directory}")
            try:
                # Initialize indexer with the last directory
                self.indexer = FileIndexer(self.last_directory)
                
                # Initialize other required components
                self.file_selector = FileSelector()
                self.project_analyzer = ProjectAnalyzer(self.indexer)
                
                # Check if index exists and is complete
                index_status = self.indexer.is_index_complete()
                if index_status.get('complete', False):
                    self.logger.info(f"Successfully loaded existing index from: {self.last_directory}")
                    print(f"\n{Fore.GREEN}✓ Loaded existing project: {Fore.CYAN}{os.path.basename(self.last_directory)}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Path: {self.last_directory}{Style.RESET_ALL}")
                    
                    # Load project info if available
                    try:
                        self.project_info = self.project_analyzer.load_project_info()
                        if self.project_info:
                            self.logger.info("Loaded existing project information")
                        else:
                            self.logger.info("No existing project information found")
                    except Exception as e:
                        self.logger.warning(f"Could not load project info: {e}")
                        self.project_info = {}
                    
                    # Initialize chat handler with all components
                    try:
                        self.chat_handler = ChatHandler(self.indexer, self.file_selector, self.project_info)
                        self.logger.info("Initialized chat handler")
                    except Exception as e:
                        self.logger.warning(f"Could not initialize chat handler: {e}")
                        self.chat_handler = None
                    
                    # Update recent projects list
                    self._add_to_recent_projects(self.last_directory)
                else:
                    self.logger.warning(f"Index exists but is incomplete or outdated in: {self.last_directory}")
                    self.index_outdated = True
                    print(f"\n{Fore.YELLOW}⚠ Found incomplete index in: {Fore.CYAN}{os.path.basename(self.last_directory)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Consider reindexing to ensure completeness.{Style.RESET_ALL}")
                    
                    # Still initialize basic components even if incomplete
                    try:
                        self.chat_handler = ChatHandler(self.indexer, self.file_selector, {})
                        self.logger.info("Initialized chat handler for incomplete index")
                    except Exception as e:
                        self.logger.warning(f"Could not initialize chat handler: {e}")
                        self.chat_handler = None
                    
                    # Still add to recent projects even if incomplete
                    self._add_to_recent_projects(self.last_directory)
                    
            except Exception as e:
                self.logger.error(f"Failed to load indexer from {self.last_directory}: {e}")
                print(f"\n{Fore.RED}Failed to load previous project from: {self.last_directory}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Error: {e}{Style.RESET_ALL}")
                # Reset all components if loading fails
                self.indexer = None
                self.file_selector = None
                self.project_analyzer = None
                self.chat_handler = None
        
        # First time setup or failed to load previous project
        if not self.indexer and not self.last_directory:
            print(f"\n{Fore.YELLOW}Welcome to VerbalCodeAI! Let's start by indexing a code directory.{Style.RESET_ALL}")
            self.index_directory()
        elif not self.indexer and self.recent_projects:
            print(f"\n{Fore.YELLOW}Would you like to load a recent project? (y/n){Style.RESET_ALL}")
            choice = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip().lower()
            if choice in ("y", "yes"):
                self.view_recent_projects()

        while True:
            if self.indexer:
                index_status = self.indexer.is_index_complete()
                self.index_outdated = not index_status.get('complete', False)

            self.display_menu()
            choice = input(f"{Fore.YELLOW}Enter your choice (1-15): {Style.RESET_ALL}").strip()

            actions = {
                "1": lambda: self.index_directory(),
                "2": lambda: self.chat_with_ai(),
                "3": lambda: self.chat_with_ai(max_chat_mode=True),
                "4": lambda: asyncio.run(self.agent_mode()),
                "5": lambda: self.index_directory(force_reindex=True),
                "6": lambda: self.view_indexed_files(),
                "7": lambda: self.view_project_info(),
                "8": lambda: self.view_recent_projects(),
                "9": lambda: self.project_management_dashboard(),
                "10": lambda: self.clean_slate(),
                "11": lambda: self.toggle_markdown_rendering(),
                "12": lambda: self.toggle_thinking_blocks(),
                "13": lambda: self.toggle_streaming_mode(),
                "14": lambda: clear_screen(),
            }

            if choice in actions or choice == "15":
                if choice == "15":
                    clear_screen()
                    print(f"\n{Fore.GREEN}Exiting TaskHeroAI. Goodbye!{Style.RESET_ALL}")
                    break
                else:
                    clear_screen()
                    actions[choice]()
            else:
                print(f"\n{Fore.RED}Invalid choice. Please enter a number between 1 and 15.{Style.RESET_ALL}")

    def project_management_dashboard(self) -> None:
        """Display the project management dashboard."""
        print("\n" + Fore.CYAN + "=" * 60 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "📋 TaskHeroAI - Project Management Dashboard" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
        
        # Initialize project management components if not already done
        if not self.project_planner:
            self.project_planner = ProjectPlanner()
            self.task_manager = self.project_planner.task_manager
            self.project_templates = self.project_planner.templates
        
        try:
            # Get dashboard data
            dashboard = self.project_planner.get_project_dashboard()
            
            # Display project overview
            print(f"\n{Fore.YELLOW}🏠 Project: {Style.BRIGHT}{dashboard['project_name']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 Progress: {Style.BRIGHT}{dashboard['progress_percentage']}%{Style.RESET_ALL} " +
                  f"({dashboard['completed_tasks']}/{dashboard['total_tasks']} tasks)")
            print(f"{Fore.CYAN}🕒 Last Updated: {dashboard['last_updated']}{Style.RESET_ALL}")
            
            # Display task summary
            print(f"\n{Fore.CYAN}📈 Task Summary:{Style.RESET_ALL}")
            task_summary = dashboard['task_summary']
            status_colors = {
                'todo': Fore.YELLOW,
                'inprogress': Fore.BLUE, 
                'testing': Fore.MAGENTA,
                'devdone': Fore.GREEN,
                'done': Fore.GREEN + Style.BRIGHT,
                'backlog': Fore.WHITE
            }
            
            for status, count in task_summary.items():
                color = status_colors.get(status, Fore.WHITE)
                status_name = self.project_planner.settings['statuses'].get(status, status.title())
                print(f"  {color}• {status_name}: {count}{Style.RESET_ALL}")
            
            # Display upcoming deadlines if any
            if dashboard['upcoming_deadlines']:
                print(f"\n{Fore.RED}⚠️  Upcoming Deadlines:{Style.RESET_ALL}")
                for deadline in dashboard['upcoming_deadlines'][:3]:  # Show top 3
                    priority_color = Fore.RED if deadline['priority'] == 'high' else Fore.YELLOW
                    print(f"  {priority_color}• {deadline['task']} - Due: {deadline['due_date']}{Style.RESET_ALL}")
            
            # Display available templates
            templates = dashboard.get('available_templates', [])
            if templates:
                print(f"\n{Fore.CYAN}📄 Available Templates: {len(templates)}{Style.RESET_ALL}")
            
            # Menu options
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}1. {Style.BRIGHT}View All Tasks{Style.RESET_ALL}")
            print(f"{Fore.GREEN}2. {Style.BRIGHT}Create New Task{Style.RESET_ALL}")
            print(f"{Fore.GREEN}3. {Style.BRIGHT}Move Task Status{Style.RESET_ALL}")
            print(f"{Fore.GREEN}4. {Style.BRIGHT}Search Tasks{Style.RESET_ALL}")
            print(f"{Fore.GREEN}5. {Style.BRIGHT}Generate Project Report{Style.RESET_ALL}")
            print(f"{Fore.GREEN}6. {Style.BRIGHT}Manage Templates{Style.RESET_ALL}")
            print(f"{Fore.GREEN}7. {Style.BRIGHT}Archive Completed Tasks{Style.RESET_ALL}")
            print(f"{Fore.GREEN}8. {Style.BRIGHT}Project Settings{Style.RESET_ALL}")
            print(f"{Fore.GREEN}9. {Style.BRIGHT}Back to Main Menu{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            
            while True:
                try:
                    choice = input(f"\n{Fore.GREEN}Choose an option (1-9): {Style.RESET_ALL}").strip()
                    
                    if choice == "1":
                        self._view_all_tasks()
                    elif choice == "2":
                        self._create_new_task()
                    elif choice == "3":
                        self._move_task_status()
                    elif choice == "4":
                        self._search_tasks()
                    elif choice == "5":
                        self._generate_project_report()
                    elif choice == "6":
                        self._manage_templates()
                    elif choice == "7":
                        self._archive_completed_tasks()
                    elif choice == "8":
                        self._project_settings()
                    elif choice == "9":
                        break
                    else:
                        print(f"{Fore.RED}Invalid choice. Please select 1-9.{Style.RESET_ALL}")
                        
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Returning to main menu...{Style.RESET_ALL}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Error in project management dashboard: {e}")
            print(f"{Fore.RED}Error loading project management dashboard: {e}{Style.RESET_ALL}")

    def _view_all_tasks(self) -> None:
        """Display all tasks organized by status."""
        print(f"\n{Fore.CYAN}📋 All Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        all_tasks = self.task_manager.get_all_tasks()
        
        for status, tasks in all_tasks.items():
            if not tasks:
                continue
                
            status_name = self.project_planner.settings['statuses'].get(status, status.title())
            print(f"\n{Fore.YELLOW}{status_name} ({len(tasks)}){Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'-'*30}{Style.RESET_ALL}")
            
            for i, task in enumerate(tasks, 1):
                priority_indicator = ""
                if task.priority and task.priority != 'medium':
                    priority_indicator = f" [{task.priority.upper()}]"
                
                print(f"  {i}. {task.title}{priority_indicator}")
                if task.due_date:
                    print(f"     📅 Due: {task.due_date}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def _create_new_task(self) -> None:
        """Create a new task from user input."""
        print(f"\n{Fore.CYAN}📝 Create New Task{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*30}{Style.RESET_ALL}")
        
        try:
            title = input(f"{Fore.GREEN}Task title: {Style.RESET_ALL}").strip()
            if not title:
                print(f"{Fore.RED}Task title cannot be empty.{Style.RESET_ALL}")
                return
            
            # Ask for priority
            print(f"\n{Fore.CYAN}Priority levels:{Style.RESET_ALL}")
            print("1. Low")
            print("2. Medium (default)")
            print("3. High") 
            print("4. Critical")
            
            priority_choice = input(f"{Fore.GREEN}Select priority (1-4, default 2): {Style.RESET_ALL}").strip()
            priority_map = {"1": "low", "2": "medium", "3": "high", "4": "critical"}
            priority = priority_map.get(priority_choice, "medium")
            
            # Ask for due date (optional)
            due_date = input(f"{Fore.GREEN}Due date (YYYY-MM-DD, optional): {Style.RESET_ALL}").strip()
            if due_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
                print(f"{Fore.YELLOW}Invalid date format, skipping due date.{Style.RESET_ALL}")
                due_date = None
            
            # Create the task
            success, result = self.project_planner.create_new_task(
                title=title,
                priority=priority,
                due_date=due_date if due_date else None
            )
            
            if success:
                print(f"{Fore.GREEN}✅ Task created successfully: {result}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Task file: {result.lower()}-{title.lower().replace(' ', '-')}.md{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Failed to create task: {result}{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
            print(f"{Fore.RED}Error creating task: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def _move_task_status(self) -> None:
        """Move a task to a different status."""
        print(f"\n{Fore.CYAN}🔄 Move Task Status{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*30}{Style.RESET_ALL}")
        
        # Show all tasks with numbers
        all_tasks = self.task_manager.get_all_tasks()
        task_list = []
        task_index = 1
        
        for status, tasks in all_tasks.items():
            if not tasks:
                continue
                
            status_name = self.project_planner.settings['statuses'].get(status, status.title())
            print(f"\n{Fore.YELLOW}{status_name}:{Style.RESET_ALL}")
            
            for task in tasks:
                task_file = Path(task.file_path).name
                print(f"  {task_index}. {task.title}")
                print(f"     File: {task_file}")
                task_list.append((task_file, status, task.title))
                task_index += 1
        
        if not task_list:
            print(f"{Fore.YELLOW}No tasks found.{Style.RESET_ALL}")
            input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        try:
            task_choice = input(f"\n{Fore.GREEN}Select task number (1-{len(task_list)}): {Style.RESET_ALL}").strip()
            task_num = int(task_choice) - 1
            
            if task_num < 0 or task_num >= len(task_list):
                print(f"{Fore.RED}Invalid task number.{Style.RESET_ALL}")
                return
            
            task_file, current_status, task_title = task_list[task_num]
            
            # Show available statuses
            print(f"\n{Fore.CYAN}Move '{task_title}' to:{Style.RESET_ALL}")
            statuses = list(self.project_planner.settings['statuses'].items())
            for i, (status, name) in enumerate(statuses, 1):
                marker = " (current)" if status == current_status else ""
                print(f"  {i}. {name}{marker}")
            
            status_choice = input(f"{Fore.GREEN}Select new status (1-{len(statuses)}): {Style.RESET_ALL}").strip()
            status_num = int(status_choice) - 1
            
            if status_num < 0 or status_num >= len(statuses):
                print(f"{Fore.RED}Invalid status number.{Style.RESET_ALL}")
                return
            
            new_status = statuses[status_num][0]
            new_status_name = statuses[status_num][1]
            
            if new_status == current_status:
                print(f"{Fore.YELLOW}Task is already in {new_status_name} status.{Style.RESET_ALL}")
                return
            
            # Move the task
            success = self.project_planner.move_task_to_status(task_file, new_status)
            
            if success:
                print(f"{Fore.GREEN}✅ Task moved to {new_status_name} successfully!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Failed to move task.{Style.RESET_ALL}")
                
        except (ValueError, IndexError):
            print(f"{Fore.RED}Invalid selection.{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"Error moving task: {e}")
            print(f"{Fore.RED}Error moving task: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def _search_tasks(self) -> None:
        """Search for tasks."""
        print(f"\n{Fore.CYAN}🔍 Search Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*20}{Style.RESET_ALL}")
        
        query = input(f"{Fore.GREEN}Enter search query: {Style.RESET_ALL}").strip()
        if not query:
            print(f"{Fore.RED}Search query cannot be empty.{Style.RESET_ALL}")
            input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        try:
            results = self.task_manager.search_tasks(query)
            
            if results:
                print(f"\n{Fore.GREEN}Found {len(results)} matching tasks:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'-'*40}{Style.RESET_ALL}")
                
                for i, task in enumerate(results, 1):
                    print(f"{i}. {task.title}")
                    print(f"   Status: {task.status}")
                    if task.priority and task.priority != 'medium':
                        print(f"   Priority: {task.priority}")
                    if task.due_date:
                        print(f"   Due: {task.due_date}")
                    print()
            else:
                print(f"{Fore.YELLOW}No tasks found matching '{query}'.{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error searching tasks: {e}")
            print(f"{Fore.RED}Error searching tasks: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def _generate_project_report(self) -> None:
        """Generate and display a project report."""
        print(f"\n{Fore.CYAN}📊 Generate Project Report{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*30}{Style.RESET_ALL}")
        
        try:
            include_details = input(f"{Fore.GREEN}Include detailed task information? (y/n, default n): {Style.RESET_ALL}").strip().lower() == 'y'
            
            print(f"\n{Fore.CYAN}Generating report...{Style.RESET_ALL}")
            report = self.project_planner.generate_project_report(include_details=include_details)
            
            # Display the report
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            if self.enable_markdown_rendering:
                render_markdown(report)
            else:
                print(report)
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            
            # Ask if user wants to save the report
            save_report = input(f"\n{Fore.GREEN}Save report to file? (y/n): {Style.RESET_ALL}").strip().lower() == 'y'
            
            if save_report:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = f"project_report_{timestamp}.md"
                
                try:
                    with open(report_file, 'w', encoding='utf-8') as f:
                        f.write(report)
                    print(f"{Fore.GREEN}✅ Report saved to: {report_file}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error saving report: {e}{Style.RESET_ALL}")
                    
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            print(f"{Fore.RED}Error generating report: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def _manage_templates(self) -> None:
        """Manage project templates."""
        print(f"\n{Fore.CYAN}📄 Template Management{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*25}{Style.RESET_ALL}")
        
        try:
            templates = self.project_templates.get_available_templates()
            
            if templates:
                print(f"\n{Fore.GREEN}Available templates:{Style.RESET_ALL}")
                for i, template in enumerate(templates, 1):
                    print(f"  {i}. {template}")
            else:
                print(f"{Fore.YELLOW}No templates found.{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}Template actions:{Style.RESET_ALL}")
            print("1. View template details")
            print("2. Create document from template")
            print("3. Back to dashboard")
            
            choice = input(f"\n{Fore.GREEN}Choose action (1-3): {Style.RESET_ALL}").strip()
            
            if choice == "1" and templates:
                self._view_template_details(templates)
            elif choice == "2" and templates:
                self._create_from_template(templates)
            elif choice == "3":
                return
            else:
                print(f"{Fore.RED}Invalid choice or no templates available.{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error managing templates: {e}")
            print(f"{Fore.RED}Error managing templates: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def _view_template_details(self, templates: List[str]) -> None:
        """View details of a selected template."""
        try:
            template_choice = input(f"{Fore.GREEN}Select template number (1-{len(templates)}): {Style.RESET_ALL}").strip()
            template_num = int(template_choice) - 1
            
            if template_num < 0 or template_num >= len(templates):
                print(f"{Fore.RED}Invalid template number.{Style.RESET_ALL}")
                return
            
            template_name = templates[template_num]
            template_info = self.project_templates.get_template_info(template_name)
            
            if template_info:
                print(f"\n{Fore.CYAN}Template Details:{Style.RESET_ALL}")
                print(f"Name: {template_info['name']}")
                print(f"Title: {template_info['title']}")
                print(f"Description: {template_info['description']}")
                print(f"Size: {template_info['size']} bytes")
                print(f"Modified: {template_info['modified']}")
            else:
                print(f"{Fore.RED}Could not load template information.{Style.RESET_ALL}")
                
        except (ValueError, IndexError):
            print(f"{Fore.RED}Invalid selection.{Style.RESET_ALL}")

    def _create_from_template(self, templates: List[str]) -> None:
        """Create a document from a template."""
        try:
            template_choice = input(f"{Fore.GREEN}Select template number (1-{len(templates)}): {Style.RESET_ALL}").strip()
            template_num = int(template_choice) - 1
            
            if template_num < 0 or template_num >= len(templates):
                print(f"{Fore.RED}Invalid template number.{Style.RESET_ALL}")
                return
            
            template_name = templates[template_num]
            output_path = input(f"{Fore.GREEN}Output file path: {Style.RESET_ALL}").strip()
            
            if not output_path:
                print(f"{Fore.RED}Output path cannot be empty.{Style.RESET_ALL}")
                return
            
            # Basic replacements - could be expanded
            replacements = {}
            author = input(f"{Fore.GREEN}Author name (optional): {Style.RESET_ALL}").strip()
            if author:
                replacements["AUTHOR"] = author
            
            success = self.project_templates.create_document_from_template(
                template_name, output_path, replacements
            )
            
            if success:
                print(f"{Fore.GREEN}✅ Document created successfully: {output_path}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Failed to create document.{Style.RESET_ALL}")
                
        except (ValueError, IndexError):
            print(f"{Fore.RED}Invalid selection.{Style.RESET_ALL}")

    def _archive_completed_tasks(self) -> None:
        """Archive all completed tasks."""
        print(f"\n{Fore.CYAN}📦 Archive Completed Tasks{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*30}{Style.RESET_ALL}")
        
        try:
            done_tasks = self.task_manager.get_tasks_by_status('done')
            
            if not done_tasks:
                print(f"{Fore.YELLOW}No completed tasks to archive.{Style.RESET_ALL}")
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            print(f"\n{Fore.CYAN}Found {len(done_tasks)} completed tasks:{Style.RESET_ALL}")
            for task in done_tasks:
                print(f"  • {task.title}")
            
            confirm = input(f"\n{Fore.GREEN}Archive all completed tasks? (y/n): {Style.RESET_ALL}").strip().lower() == 'y'
            
            if confirm:
                archived_count = self.project_planner.archive_completed_tasks()
                print(f"{Fore.GREEN}✅ Archived {archived_count} tasks successfully!{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Archive operation cancelled.{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error archiving tasks: {e}")
            print(f"{Fore.RED}Error archiving tasks: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def _project_settings(self) -> None:
        """Display and modify project settings."""
        print(f"\n{Fore.CYAN}⚙️  Project Settings{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*25}{Style.RESET_ALL}")
        
        try:
            settings = self.project_planner.settings
            
            print(f"\n{Fore.GREEN}Current Settings:{Style.RESET_ALL}")
            print(f"Project Name: {settings.get('project_name', 'Unknown')}")
            print(f"Task ID Prefix: {settings.get('task_id_prefix', 'TASK')}")
            print(f"Next Task ID: {settings.get('task_id_prefix', 'TASK')}-{settings.get('task_id_counter', 1):03d}")
            print(f"Default Template: {settings.get('default_task_template', 'task-template.md')}")
            
            print(f"\n{Fore.CYAN}Modify settings:{Style.RESET_ALL}")
            print("1. Change project name")
            print("2. Change task ID prefix")
            print("3. Reset task counter")
            print("4. Back to dashboard")
            
            choice = input(f"\n{Fore.GREEN}Choose option (1-4): {Style.RESET_ALL}").strip()
            
            if choice == "1":
                new_name = input(f"{Fore.GREEN}New project name: {Style.RESET_ALL}").strip()
                if new_name:
                    settings['project_name'] = new_name
                    self.project_planner._save_settings()
                    print(f"{Fore.GREEN}✅ Project name updated.{Style.RESET_ALL}")
                    
            elif choice == "2":
                new_prefix = input(f"{Fore.GREEN}New task ID prefix: {Style.RESET_ALL}").strip().upper()
                if new_prefix:
                    settings['task_id_prefix'] = new_prefix
                    self.project_planner._save_settings()
                    print(f"{Fore.GREEN}✅ Task ID prefix updated.{Style.RESET_ALL}")
                    
            elif choice == "3":
                confirm = input(f"{Fore.YELLOW}Reset task counter to 1? (y/n): {Style.RESET_ALL}").strip().lower() == 'y'
                if confirm:
                    settings['task_id_counter'] = 1
                    self.project_planner._save_settings()
                    print(f"{Fore.GREEN}✅ Task counter reset.{Style.RESET_ALL}")
                    
            elif choice == "4":
                return
            else:
                print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Error managing settings: {e}")
            print(f"{Fore.RED}Error managing settings: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")


def run_http_server(port: int, allow_all_origins: bool = None) -> None:
    """Run the HTTP API server.

    Args:
        port: Port number to listen on
        allow_all_origins: Whether to allow all origins or only localhost.
                          If None, reads from environment variable.
    """
    app_instance = VerbalCodeAI()

    if allow_all_origins is None:
        allow_all_origins = app_instance._get_env_bool("HTTP_ALLOW_ALL_ORIGINS", False)

    app = create_app(allow_all_origins=allow_all_origins)

    host = "0.0.0.0" if allow_all_origins else "127.0.0.1"

    print(f"{Fore.GREEN}Starting HTTP API server on {host}:{port}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Available endpoints:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}- GET  /api/health{Style.RESET_ALL} - Health check")
    print(f"{Fore.CYAN}- POST /api/initialize{Style.RESET_ALL} - Initialize a directory")
    print(f"{Fore.CYAN}- POST /api/ask{Style.RESET_ALL} - Ask the agent a question")
    print(f"{Fore.CYAN}- POST /api/index/start{Style.RESET_ALL} - Start indexing a directory")
    print(f"{Fore.CYAN}- GET  /api/index/status{Style.RESET_ALL} - Get indexing status")

    if allow_all_origins:
        print(f"{Fore.RED}WARNING: Server is accessible from any IP address.{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Server is only accessible from localhost.{Style.RESET_ALL}")

    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="TaskHeroAI Terminal Application")
        parser.add_argument("directory", nargs="?", help="Directory to index")
        parser.add_argument("--serve", type=int, metavar="PORT", help="Run HTTP API server on specified port")
        parser.add_argument("--allow-all-origins", action="store_true", help="Allow all origins for HTTP API (not just localhost)")
        args = parser.parse_args()

        if args.serve:
            logger = setup_logging()
            logger.info(f"Starting TaskHeroAI HTTP API Server on port {args.serve}")

            run_http_server(args.serve, args.allow_all_origins)
            sys.exit(0)

        display_animated_banner(frame_delay=0.2)

        print(f"{Fore.CYAN}{Style.BRIGHT}Starting TaskHeroAI Terminal Application...{Style.RESET_ALL}")

        logger = setup_logging()
        logger.info("Starting TaskHeroAI Terminal Application")

        app = VerbalCodeAI()

        if args.directory:
            directory = args.directory
            if os.path.isdir(directory):
                print(f"{Fore.CYAN}Using directory from command line: {Style.BRIGHT}{directory}{Style.RESET_ALL}")
                app.indexer = FileIndexer(directory)
                app._save_last_directory(directory)

                index_status = app.indexer.is_index_complete()
                app.index_outdated = not index_status.get('complete', False)
                if app.index_outdated:
                    print(f"{Fore.YELLOW}Index is outdated. Consider reindexing.{Style.RESET_ALL}")

        app.run()

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Application terminated by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"\n{Fore.RED}{Style.BRIGHT}CRITICAL ERROR: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}See logs for details.{Style.RESET_ALL}")
        print(f"{Fore.RED}Error details:\n{error_details}{Style.RESET_ALL}")
        sys.exit(1)
