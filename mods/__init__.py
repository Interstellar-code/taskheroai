"""
Mods package for TaskHero AI.

This package contains the modular architecture for the TaskHero AI application.
"""

# Import new modular architecture
from . import core
from . import settings
from . import ai
from . import ui
from . import cli

# Legacy modules (commented out during refactoring)
# from . import code
# from . import llms

__all__ = [
    "core",
    "settings", 
    "ai",
    "ui",
    "cli",
    # Legacy modules
    # "llms", 
    # "code"
]
