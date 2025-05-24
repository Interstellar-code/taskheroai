"""
Interface definitions for TaskHero AI modular architecture.

These interfaces define the contracts that all modules must implement
to ensure consistent behavior and proper integration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import logging


class ComponentInterface(ABC):
    """Base interface for all application components."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the component."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources used by the component."""
        pass
    
    @property
    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if the component is initialized."""
        pass


class ManagerInterface(ComponentInterface):
    """Interface for manager components that handle specific functionality areas."""
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the manager."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the manager to its initial state."""
        pass


class ModuleInterface(ABC):
    """Interface for application modules."""
    
    @abstractmethod
    def get_module_info(self) -> Dict[str, str]:
        """Get information about this module."""
        pass
    
    @abstractmethod
    def get_available_commands(self) -> List[str]:
        """Get list of available commands in this module."""
        pass


class ConfigurableInterface(ABC):
    """Interface for components that can be configured."""
    
    @abstractmethod
    def load_config(self, config: Dict[str, Any]) -> None:
        """Load configuration for the component."""
        pass
    
    @abstractmethod
    def save_config(self) -> Dict[str, Any]:
        """Save current configuration."""
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        pass


class LoggableInterface(ABC):
    """Interface for components that support logging."""
    
    @property
    @abstractmethod
    def logger(self) -> logging.Logger:
        """Get the logger instance for this component."""
        pass 