"""
AI Manager for TaskHero AI.

Handles AI integration and AI-powered features.
Extracted from the monolithic app.py.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional, Union

from colorama import Fore, Style

from ..core import BaseManager
from .chat_handler import ChatHandler
from .agent_mode import AgentMode


class AIManager(BaseManager):
    """Manager for AI functionality."""
    
    def __init__(self, settings_manager=None):
        """Initialize the AI manager."""
        super().__init__("AIManager")
        self.settings_manager = settings_manager
        
        # AI Components
        self.chat_handler: Optional[ChatHandler] = None
        self.agent_mode_instance: Optional[AgentMode] = None
        
        # Dependencies (will be injected)
        self.indexer = None
        self.file_selector = None
        self.project_analyzer = None
        self.project_info: Dict[str, Any] = {}
        self.chat_history: List[Dict[str, str]] = []
    
    def _perform_initialization(self) -> None:
        """Initialize the AI manager."""
        self.logger.info("AI Manager initialized - components will be created on demand")
        self.update_status("components_ready", True)
    
    def set_dependencies(self, indexer, file_selector, project_analyzer):
        """Set the required dependencies for AI functionality."""
        self.indexer = indexer
        self.file_selector = file_selector
        self.project_analyzer = project_analyzer
        self.update_status("dependencies_set", True)
        self.logger.info("AI Manager dependencies set")
    
    def is_ready(self) -> bool:
        """Check if AI manager is ready to handle requests."""
        return (self.indexer is not None and 
                self.file_selector is not None and 
                self.project_analyzer is not None)
    
    def chat_with_ai(self, max_chat_mode: bool = False) -> None:
        """
        Start a chat session with AI.
        
        Args:
            max_chat_mode: Whether to use Max Chat mode (token intensive)
        """
        if not self.indexer:
            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            return
        
        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        if max_chat_mode:
            print(Fore.CYAN + Style.BRIGHT + "Max Chat Mode (Token Intensive)" + Style.RESET_ALL)
            print(Fore.RED + "WARNING: This mode sends full file contents to the AI and uses more tokens." + Style.RESET_ALL)
        else:
            print(Fore.CYAN + Style.BRIGHT + "Chat with AI" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(f"{Fore.YELLOW}Type your questions about the codebase. Type '{Fore.RED}exit{Fore.YELLOW}' to return to the main menu.{Style.RESET_ALL}")
        
        self.logger.info("AI Chat session started")
    
    async def agent_mode(self) -> None:
        """Run the AI agent mode for interactive codebase exploration."""
        if not self.indexer:
            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            return
        
        print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "Agent Mode" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(f"{Fore.YELLOW}In Agent Mode, the AI can use tools to explore and understand your codebase.")
        print(f"{Fore.YELLOW}Type your questions about the codebase. Type '{Fore.RED}exit{Fore.YELLOW}' to return to the main menu.{Style.RESET_ALL}")
        
        self.logger.info("Agent Mode session started")
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the current chat history."""
        return self.chat_history.copy()
    
    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        self.chat_history.clear()
        self.logger.info("Chat history cleared")
    
    def _perform_reset(self) -> None:
        """Reset the AI manager."""
        self.clear_chat_history()
        self.chat_handler = None
        self.agent_mode_instance = None
        self.project_info = {}
        self.logger.info("AI Manager reset completed") 