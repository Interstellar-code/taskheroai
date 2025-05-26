"""
Menu Manager for TaskHero AI.

Handles menu systems and user interface navigation.
Extracted from the monolithic app.py.
"""

from typing import Any, Dict, Optional
from colorama import Fore, Style

from ..core import BaseManager


class MenuManager(BaseManager):
    """Manager for menu systems and UI navigation."""

    def __init__(self, settings_manager=None, git_manager=None):
        """Initialize the menu manager."""
        super().__init__("MenuManager")
        self.settings_manager = settings_manager
        self.git_manager = git_manager

        # Application state (will be injected)
        self.indexer = None
        self.index_outdated = False
        self.update_available = False
        self.update_info = None

    def _perform_initialization(self) -> None:
        """Initialize the menu manager."""
        self.logger.info("Menu Manager initialized")
        self.update_status("menu_ready", True)

    def set_application_state(self, indexer, index_outdated: bool = False, update_info: dict = None):
        """Set application state for menu display."""
        self.indexer = indexer
        self.index_outdated = index_outdated

        # Update Git status if available
        if update_info:
            self.update_available = update_info.get("update_available", False)
            self.update_info = update_info
        elif self.git_manager:
            # Check for updates if not provided
            try:
                status = self.git_manager.get_update_status()
                last_check = status.get("last_check")
                if last_check:
                    self.update_available = last_check.get("update_available", False)
                    self.update_info = last_check
            except Exception as e:
                self.logger.debug(f"Error checking update status: {e}")

        self.update_status("app_state_set", True)

    def display_main_menu(self) -> None:
        """Display the enhanced main menu with reorganized sections."""
        print("\n" + Fore.CYAN + "=" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "TaskHeroAI - AI-Powered Code & Project Assistant".center(70) + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

        # Update notification
        if self.update_available and self.update_info:
            print(
                Fore.GREEN + Style.BRIGHT + "🎉 [UPDATE AVAILABLE] " + Style.RESET_ALL +
                Fore.YELLOW + "New version ready! Check AI Settings > Git & Updates (option 14 > 15)" + Style.RESET_ALL
            )
            if self.update_info.get("comparison", {}).get("remote_version"):
                remote_version = self.update_info["comparison"]["remote_version"]
                print(Fore.CYAN + f"Available version: {remote_version}" + Style.RESET_ALL)
            print()

        # Status messages
        if not self.indexer:
            print(Fore.YELLOW + "No code indexed yet. Please select option 1 to index code." + Style.RESET_ALL)
        elif self.index_outdated:
            print(
                Fore.RED + Style.BRIGHT + "[INDEX OUTDATED] " + Style.RESET_ALL +
                Fore.YELLOW + "Please select option 1 to update the index." + Style.RESET_ALL
            )

        # Indexing & Embedding Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "📚 Indexing & Embedding" + Style.RESET_ALL)
        print(Fore.GREEN + "1. " + Style.BRIGHT + "💡 Index Code" + Style.RESET_ALL + f" {Fore.CYAN}(Start here){Style.RESET_ALL}")
        print(Fore.GREEN + "2. " + Style.BRIGHT + "📁 View Indexed Files" + Style.RESET_ALL)
        print(Fore.GREEN + "3. " + Style.BRIGHT + "📊 View Project Info" + Style.RESET_ALL)
        print(Fore.GREEN + "4. " + Style.BRIGHT + "🕒 Recent Projects" + Style.RESET_ALL)

        # Chat with Code Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "💬 Chat with Code" + Style.RESET_ALL)
        print(Fore.BLUE + "5. " + Style.BRIGHT + "💬 Chat with AI" + Style.RESET_ALL + f" {Fore.YELLOW}(Expensive){Style.RESET_ALL}")
        print(Fore.BLUE + "6. " + Style.BRIGHT + "🚀 Max Chat Mode" + Style.RESET_ALL + f" {Fore.RED}(Very Expensive){Style.RESET_ALL}")
        print(Fore.BLUE + "7. " + Style.BRIGHT + "🤖 Agent Mode" + Style.RESET_ALL + f" {Fore.GREEN}(Recommended){Style.RESET_ALL}")

        # TaskHero Management Section (TASK-005 Enhanced Features)
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🎯 TaskHero Management" + Style.RESET_ALL)
        print(Fore.MAGENTA + "8. " + Style.BRIGHT + "📋 Task Dashboard" + Style.RESET_ALL + f" {Fore.CYAN}(Full features){Style.RESET_ALL}")
        print(Fore.MAGENTA + "9. " + Style.BRIGHT + "🎯 Kanban Board" + Style.RESET_ALL + f" {Fore.GREEN}(Visual tasks){Style.RESET_ALL}")
        print(Fore.MAGENTA + "10. " + Style.BRIGHT + "➕ Quick Create Task" + Style.RESET_ALL)
        print(Fore.MAGENTA + "11. " + Style.BRIGHT + "👀 Quick View Tasks" + Style.RESET_ALL)
        print(Fore.MAGENTA + "12. " + Style.BRIGHT + "🔍 Search Tasks" + Style.RESET_ALL)

        # Settings & Tools Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "⚙️ Settings & Tools" + Style.RESET_ALL)
        print(Fore.RED + "13. " + Style.BRIGHT + "🗑️ Project Cleanup Manager" + Style.RESET_ALL + f" {Fore.YELLOW}(Delete indices){Style.RESET_ALL}")
        print(Fore.GREEN + "14. " + Style.BRIGHT + "🤖 AI Settings" + Style.RESET_ALL + f" {Fore.CYAN}(Configure providers){Style.RESET_ALL}")
        print(Fore.BLUE + "0. " + Style.BRIGHT + "🚪 Exit" + Style.RESET_ALL)

        print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

        # Show keyboard shortcuts
        print(f"{Fore.CYAN}💡 Quick shortcuts: {Fore.YELLOW}Ctrl+C{Fore.CYAN} = Cancel | {Fore.YELLOW}0{Fore.CYAN} = Exit{Style.RESET_ALL}")

    def get_user_choice(self) -> str:
        """Get user menu choice."""
        print(f"\n{Fore.GREEN}Choose an option:{Style.RESET_ALL}")
        choice = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
        return choice

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        self.logger.info("Screen cleared")

    def _perform_reset(self) -> None:
        """Reset the menu manager."""
        self.indexer = None
        self.index_outdated = False
        self.logger.info("Menu manager reset")