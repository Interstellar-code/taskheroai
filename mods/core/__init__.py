"""
Core module for TaskHero AI.

This module contains base classes, interfaces, and shared utilities
that are used across all other modules in the application.
"""

from .base_classes import BaseComponent, BaseManager
from .interfaces import (
    ComponentInterface,
    ManagerInterface,
    ModuleInterface,
    ConfigurableInterface,
)
from .app_controller import ApplicationController

__all__ = [
    "BaseComponent",
    "BaseManager", 
    "ComponentInterface",
    "ManagerInterface",
    "ModuleInterface", 
    "ConfigurableInterface",
    "ApplicationController",
] 