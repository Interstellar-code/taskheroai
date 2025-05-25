"""
TaskHeroAI Project Management Module

This module provides project management functionality including:
- Task management (todo, in progress, done, etc.)
- Project planning and templates
- Documentation generation
- AI-enhanced task creation with intelligent content generation
- Template engine with Jinja2 integration
- Integration with AI features for enhanced project management

Originally integrated from TaskHeroMD PowerShell scripts.
Enhanced with AI capabilities and advanced template system.
"""

from .task_manager import TaskManager
from .project_templates import ProjectTemplates
from .project_planner import ProjectPlanner
from .template_engine import TemplateEngine
from .ai_task_creator import AITaskCreator
from .semantic_search import SemanticSearchEngine, ContextChunk, SearchResult

__all__ = [
    'TaskManager', 
    'ProjectTemplates', 
    'ProjectPlanner',
    'TemplateEngine',
    'AITaskCreator',
    'SemanticSearchEngine',
    'ContextChunk',
    'SearchResult'
] 