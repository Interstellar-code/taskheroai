"""
Display Manager for TaskHero AI.

Handles display utilities and terminal output formatting.
Extracted from the monolithic app.py.
"""

import os
from typing import Any, Dict
from colorama import Fore, Style

from ..core import BaseManager


class DisplayManager(BaseManager):
    """Manager for display utilities and terminal output."""
    
    def __init__(self, settings_manager=None):
        """Initialize the display manager."""
        super().__init__("DisplayManager")
        self.settings_manager = settings_manager
    
    def _perform_initialization(self) -> None:
        """Initialize the display manager."""
        self.logger.info("Display Manager initialized")
        self.update_status("display_ready", True)
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def display_file_list(self, files: list, title: str = "Files", max_display: int = 10) -> None:
        """Display a formatted list of files."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{title}:{Style.RESET_ALL}")
        
        if not files:
            print(f"{Fore.YELLOW}No files found{Style.RESET_ALL}")
            return
        
        display_count = min(max_display, len(files))
        for i, file_path in enumerate(files[:display_count], 1):
            file_name = os.path.basename(file_path)
            print(f"{Fore.GREEN}{i}. {Fore.WHITE}{file_name} {Fore.CYAN}({file_path}){Style.RESET_ALL}")
        
        if len(files) > max_display:
            remaining = len(files) - max_display
            print(f"{Fore.YELLOW}+ {remaining} more file{'s' if remaining > 1 else ''}{Style.RESET_ALL}")
    
    def display_status_table(self, items: list, headers: list) -> None:
        """Display a formatted status table."""
        if not items or not headers:
            return
        
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for item in items:
            for i, value in enumerate(item):
                col_widths[i] = max(col_widths[i], len(str(value)))
        
        # Display header
        header = "  ".join(f"{header:<{col_widths[i]}}" for i, header in enumerate(headers))
        print(f"{Fore.CYAN}{header}{Style.RESET_ALL}")
        
        # Display separator
        separator = "  ".join("-" * width for width in col_widths)
        print(f"{Fore.CYAN}{separator}{Style.RESET_ALL}")
        
        # Display items
        for item in items:
            row = "  ".join(f"{str(value):<{col_widths[i]}}" for i, value in enumerate(item))
            print(f"{Fore.WHITE}{row}{Style.RESET_ALL}")
    
    def display_progress_summary(self, total: int, completed: int, operation: str = "processed") -> None:
        """Display a progress summary."""
        percentage = (completed / total * 100) if total > 0 else 0
        print(f"\n{Fore.CYAN}Progress Summary:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{completed}/{total} files {operation} ({percentage:.1f}%){Style.RESET_ALL}")
    
    def _perform_reset(self) -> None:
        """Reset the display manager."""
        self.logger.info("Display manager reset") 