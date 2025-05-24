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
    
    def __init__(self, settings_manager=None):
        """Initialize the menu manager."""
        super().__init__("MenuManager")
        self.settings_manager = settings_manager
        
        # Application state (will be injected)
        self.indexer = None
        self.index_outdated = False
    
    def _perform_initialization(self) -> None:
        """Initialize the menu manager."""
        self.logger.info("Menu Manager initialized")
        self.update_status("menu_ready", True)
    
    def set_application_state(self, indexer, index_outdated: bool = False):
        """Set application state for menu display."""
        self.indexer = indexer
        self.index_outdated = index_outdated
        self.update_status("app_state_set", True)
    
    def display_main_menu(self) -> None:
        """Display the main menu."""
        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "TaskHeroAI - AI-Powered Code & Project Assistant" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

        # Status messages
        if not self.indexer:
            print(Fore.YELLOW + "No code indexed yet. Please select option 1 to index code." + Style.RESET_ALL)
        elif self.index_outdated:
            print(
                Fore.RED + Style.BRIGHT + "[INDEX OUTDATED] " + Style.RESET_ALL +
                Fore.YELLOW + "Please select option 1 to update the index." + Style.RESET_ALL
            )

        # AI Features Section
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "AI Features" + Style.RESET_ALL)
        print(Fore.GREEN + "1. " + Style.BRIGHT + "Index Code" + Style.RESET_ALL)
        print(Fore.GREEN + "2. " + Style.BRIGHT + "Chat with AI (Expensive)" + Style.RESET_ALL)
        print(Fore.GREEN + "3. " + Style.BRIGHT + "Max Chat Mode (Expensive)" + Style.RESET_ALL)
        print(Fore.GREEN + "4. " + Style.BRIGHT + "Agent Mode (Cheapest Option)" + Style.RESET_ALL)

        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
    
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