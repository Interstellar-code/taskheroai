"""
Chat Handler for TaskHero AI.

Handles AI chat functionality and conversation management.
Extracted from the monolithic app.py.
"""

from typing import Any, Dict, List, Tuple, Optional

from ..core import BaseComponent


class ChatHandler(BaseComponent):
    """Handler for AI chat functionality."""
    
    def __init__(self, indexer=None, file_selector=None, project_info=None):
        """Initialize the chat handler."""
        super().__init__("ChatHandler")
        self.indexer = indexer
        self.file_selector = file_selector
        self.project_info = project_info or {}
        self.chat_history: List[Dict[str, str]] = []
    
    def _perform_initialization(self) -> None:
        """Initialize the chat handler."""
        self.logger.info("Chat Handler initialized")
    
    def set_project_info(self, project_info: Dict[str, Any]) -> None:
        """Set project information."""
        self.project_info = project_info
        self.logger.info("Project info updated in ChatHandler")
    
    def process_query(self, query: str, max_chat_mode: bool = False, streaming: bool = False) -> Tuple[str, List[str]]:
        """
        Process a chat query.
        
        Args:
            query: User query
            max_chat_mode: Whether to use max chat mode
            streaming: Whether to use streaming mode
            
        Returns:
            Tuple of (response, relevant_files)
        """
        self.logger.info(f"Processing query: {query[:50]}...")
        
        # For now, return a placeholder response
        response = "This is a placeholder response. Full chat functionality will be implemented in the next phase."
        relevant_files = []
        
        # Add to history
        self.add_to_history("user", query)
        self.add_to_history("assistant", response)
        
        return response, relevant_files
    
    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to chat history."""
        self.chat_history.append({"role": role, "content": content})
        self.logger.debug(f"Added {role} message to history")
    
    def get_chat_history(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent chat history."""
        return self.chat_history[-max_messages:] if max_messages > 0 else self.chat_history
    
    def clear_history(self) -> None:
        """Clear chat history."""
        self.chat_history.clear()
        self.logger.info("Chat history cleared") 