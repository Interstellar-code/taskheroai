"""
AI module for TaskHero AI.

This module handles AI integration, chat functionality, and AI-powered
features like task prioritization and project insights.
"""

from .ai_manager import AIManager
from .chat_handler import ChatHandler
from .agent_mode import AgentMode

__all__ = [
    "AIManager",
    "ChatHandler", 
    "AgentMode",
] 