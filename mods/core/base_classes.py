"""
Base classes for TaskHero AI modular architecture.

These base classes provide default implementations of core interfaces
and common functionality that can be inherited by specific modules.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .interfaces import (
    ComponentInterface,
    ManagerInterface,
    ConfigurableInterface,
    LoggableInterface,
)


class BaseComponent(ComponentInterface, LoggableInterface):
    """Base component class providing common functionality."""
    
    def __init__(self, name: str, logger_name: Optional[str] = None):
        """
        Initialize the base component.
        
        Args:
            name: Name of the component
            logger_name: Optional custom logger name
        """
        self.name = name
        self._logger = logging.getLogger(logger_name or f"TaskHeroAI.{name}")
        self._initialized = False
        self._creation_time = datetime.now()
    
    @property
    def logger(self) -> logging.Logger:
        """Get the logger instance for this component."""
        return self._logger
    
    @property
    def is_initialized(self) -> bool:
        """Check if the component is initialized."""
        return self._initialized
    
    def initialize(self) -> None:
        """Initialize the component."""
        if self._initialized:
            self.logger.warning(f"Component {self.name} is already initialized")
            return
        
        self.logger.info(f"Initializing component: {self.name}")
        self._perform_initialization()
        self._initialized = True
        self.logger.info(f"Component {self.name} initialized successfully")
    
    def cleanup(self) -> None:
        """Cleanup resources used by the component."""
        if not self._initialized:
            self.logger.warning(f"Component {self.name} is not initialized")
            return
        
        self.logger.info(f"Cleaning up component: {self.name}")
        self._perform_cleanup()
        self._initialized = False
        self.logger.info(f"Component {self.name} cleaned up successfully")
    
    def _perform_initialization(self) -> None:
        """Override this method to implement specific initialization logic."""
        pass
    
    def _perform_cleanup(self) -> None:
        """Override this method to implement specific cleanup logic."""
        pass
    
    def get_component_info(self) -> Dict[str, Any]:
        """Get information about this component."""
        return {
            "name": self.name,
            "initialized": self.is_initialized,
            "creation_time": self._creation_time.isoformat(),
            "uptime_seconds": (datetime.now() - self._creation_time).total_seconds()
        }


class BaseManager(BaseComponent, ManagerInterface, ConfigurableInterface):
    """Base manager class for handling specific functionality areas."""
    
    def __init__(self, name: str, config_file: Optional[str] = None):
        """
        Initialize the base manager.
        
        Args:
            name: Name of the manager
            config_file: Optional path to configuration file
        """
        super().__init__(name)
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._status: Dict[str, Any] = {}
        self._default_config = self.get_default_config()
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the manager."""
        base_status = {
            **self.get_component_info(),
            "config_loaded": bool(self._config),
            "config_file": self.config_file,
        }
        base_status.update(self._status)
        return base_status
    
    def reset(self) -> None:
        """Reset the manager to its initial state."""
        self.logger.info(f"Resetting manager: {self.name}")
        self._perform_reset()
        self._status.clear()
        self.logger.info(f"Manager {self.name} reset successfully")
    
    def load_config(self, config: Dict[str, Any]) -> None:
        """Load configuration for the manager."""
        self.logger.info(f"Loading configuration for manager: {self.name}")
        self._config = {**self._default_config, **config}
        self._apply_config()
        self.logger.info(f"Configuration loaded for manager: {self.name}")
    
    def save_config(self) -> Dict[str, Any]:
        """Save current configuration."""
        return self._config.copy()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "enabled": True,
            "log_level": "INFO",
            "auto_initialize": True,
        }
    
    def _perform_reset(self) -> None:
        """Override this method to implement specific reset logic."""
        pass
    
    def _apply_config(self) -> None:
        """Override this method to apply configuration changes."""
        # Apply common configuration
        if "log_level" in self._config:
            level = getattr(logging, self._config["log_level"].upper(), logging.INFO)
            self.logger.setLevel(level)
    
    def update_status(self, key: str, value: Any) -> None:
        """Update a status value."""
        self._status[key] = value
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default) 