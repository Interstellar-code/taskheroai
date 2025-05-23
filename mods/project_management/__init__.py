"""
TaskHeroAI Project Management Module

This module provides project management functionality including:
- Task management (todo, in progress, done, etc.)
- Project planning and templates
- Documentation generation
- Integration with AI features for enhanced project management

Originally integrated from TaskHeroMD PowerShell scripts.
"""

from .task_manager import TaskManager
from .project_templates import ProjectTemplates
from .project_planner import ProjectPlanner

__all__ = ['TaskManager', 'ProjectTemplates', 'ProjectPlanner'] 