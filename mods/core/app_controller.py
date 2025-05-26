"""
Main Application Controller for TaskHero AI.

This controller orchestrates all modules in the refactored architecture,
replacing the monolithic TaskHeroAI class from app.py.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..settings import SettingsManager, EnvironmentManager
from ..ai import AIManager
from ..ui import MenuManager, DisplayManager
from ..cli import CLIManager
from .base_classes import BaseManager


class ApplicationController(BaseManager):
    """Main application controller that orchestrates all modules."""

    def __init__(self):
        """Initialize the application controller."""
        super().__init__("ApplicationController")

        # Core managers
        self.environment_manager: Optional[EnvironmentManager] = None
        self.settings_manager: Optional[SettingsManager] = None
        self.ai_manager: Optional[AIManager] = None
        self.ui_manager: Optional[MenuManager] = None
        self.display_manager: Optional[DisplayManager] = None
        self.cli_manager: Optional[CLIManager] = None

        # Application state
        self.running = False
        self.modules_initialized = False

    def _perform_initialization(self) -> None:
        """Initialize all application modules."""
        try:
            self.logger.info("Starting application initialization...")

            # Initialize core modules in order
            self._initialize_environment()
            self._initialize_settings()
            self._initialize_ai()
            self._initialize_ui()
            self._initialize_cli()

            self.modules_initialized = True
            self.update_status("modules_initialized", True)
            self.logger.info("Application initialization completed successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            self.modules_initialized = False
            raise

    def _initialize_environment(self) -> None:
        """Initialize the environment manager."""
        self.logger.info("Initializing environment manager...")
        self.environment_manager = EnvironmentManager()
        self.environment_manager.initialize()
        self.logger.info("Environment manager initialized")

    def _initialize_settings(self) -> None:
        """Initialize the settings manager."""
        self.logger.info("Initializing settings manager...")
        self.settings_manager = SettingsManager()
        self.settings_manager.initialize()
        self.logger.info("Settings manager initialized")

    def _initialize_ai(self) -> None:
        """Initialize the AI manager."""
        self.logger.info("Initializing AI manager...")
        self.ai_manager = AIManager(self.settings_manager, self.environment_manager)
        self.ai_manager.initialize()
        self.logger.info("AI manager initialized")

    def _initialize_ui(self) -> None:
        """Initialize UI managers."""
        self.logger.info("Initializing UI managers...")
        self.ui_manager = MenuManager(self.settings_manager)
        self.ui_manager.initialize()
        self.display_manager = DisplayManager(self.settings_manager)
        self.display_manager.initialize()
        self.logger.info("UI managers initialized")

    def _initialize_cli(self) -> None:
        """Initialize CLI manager."""
        self.logger.info("Initializing CLI manager...")
        self.cli_manager = CLIManager(
            settings_manager=self.settings_manager,
            ai_manager=self.ai_manager,
            ui_manager=self.ui_manager,
            display_manager=self.display_manager
        )
        self.cli_manager.initialize()
        self.logger.info("CLI manager initialized")

    def run(self) -> None:
        """Run the main application loop."""
        if not self.is_initialized:
            self.initialize()

        if not self.modules_initialized:
            self.logger.error("Cannot run application - modules not properly initialized")
            return

        self.running = True
        self.logger.info("Starting main application loop...")

        try:
            # Show startup info then start the CLI loop
            self._show_startup_info()

            # Run the main CLI loop if CLI manager is available
            if self.cli_manager:
                self.cli_manager.run_main_loop()
            else:
                print("CLI Manager not available - running in demo mode only")

        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Application error: {e}")
        finally:
            self.running = False
            self.shutdown()

    def _show_startup_info(self) -> None:
        """Show startup information."""
        print("\n🎉 TaskHero AI - Modular Architecture Active!")
        print("=" * 50)
        print(f"✅ Settings Manager: {'Initialized' if self.settings_manager and self.settings_manager.is_initialized else 'Not Ready'}")
        print(f"✅ AI Manager: {'Initialized' if self.ai_manager and self.ai_manager.is_initialized else 'Placeholder'}")
        print(f"✅ UI Manager: {'Initialized' if self.ui_manager and self.ui_manager.is_initialized else 'Placeholder'}")
        print(f"✅ CLI Manager: {'Initialized' if self.cli_manager and self.cli_manager.is_initialized else 'Placeholder'}")
        print("=" * 50)

        # Show settings info
        if self.settings_manager:
            status = self.settings_manager.get_status()
            print(f"📁 Settings file: {status.get('settings_file', 'N/A')}")
            print(f"📂 Last directory: {self.settings_manager.get_last_directory() or 'None'}")
            recent_count = len(self.settings_manager.get_recent_projects())
            print(f"🔖 Recent projects: {recent_count}")

        print("\n🚧 Phase 2 in Progress - AI & UI Modules Extracted!")
        print("Next: Extract CLI functionality and complete refactoring")
        print("=" * 50)

    def shutdown(self) -> None:
        """Shutdown the application and cleanup all modules."""
        self.logger.info("Shutting down application...")

        # Cleanup all managers in reverse order
        managers = [
            self.cli_manager,
            self.ui_manager,
            self.display_manager,
            self.ai_manager,
            self.settings_manager
        ]

        for manager in managers:
            if manager and manager.is_initialized:
                try:
                    manager.cleanup()
                    self.logger.info(f"Cleaned up {manager.name}")
                except Exception as e:
                    self.logger.error(f"Error cleaning up {manager.name}: {e}")

        self.modules_initialized = False
        self.logger.info("Application shutdown completed")

    def get_application_status(self) -> Dict[str, Any]:
        """Get comprehensive application status."""
        status = self.get_status()

        # Add module statuses
        modules = {
            "settings": self.settings_manager,
            "ai": self.ai_manager,
            "ui": self.ui_manager,
            "display": self.display_manager,
            "cli": self.cli_manager
        }

        module_status = {}
        for name, manager in modules.items():
            if manager:
                module_status[name] = manager.get_status() if hasattr(manager, 'get_status') else {"initialized": manager.is_initialized}
            else:
                module_status[name] = {"initialized": False, "status": "not_created"}

        status["modules"] = module_status
        status["running"] = self.running
        status["modules_initialized"] = self.modules_initialized

        return status

    def _perform_reset(self) -> None:
        """Reset the application controller."""
        self.shutdown()
        self.running = False
        self.modules_initialized = False