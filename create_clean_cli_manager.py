"""
Script to create a clean CLI manager file by taking the working parts from the original
and properly formatting the broken sections.
"""

# First, let's identify the issue and fix it systematically
print("Creating clean CLI manager file...")

# Read the working sections from temp_app.py to migrate the proper implementations
with open('temp_app.py', 'r', encoding='utf-8') as f:
    temp_content = f.read()

# Start building the clean file content
header = '''"""
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
                    print(f"\\n{Fore.GREEN}✓ Loaded existing project: {Fore.CYAN}{os.path.basename(last_dir)}{Style.RESET_ALL}")
                    
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
'''

# Save the header to a temporary file to start building
with open('mods/cli/cli_manager_clean.py', 'w', encoding='utf-8') as f:
    f.write(header)

print("Created header section...")
print("Now we need to add the remaining methods properly formatted.") 