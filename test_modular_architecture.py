#!/usr/bin/env python
"""
Test script for the new modular TaskHero AI architecture.

This script tests that all modules can be imported and initialized correctly.
"""

import sys
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_test_logging():
    """Set up logging for testing."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger("ModularTest")

def test_modular_architecture():
    """Test the modular architecture."""
    logger = setup_test_logging()
    
    try:
        logger.info("🧪 Testing TaskHero AI Modular Architecture...")
        
        # Test core module imports
        logger.info("Testing core module imports...")
        from mods.core import (
            BaseComponent, 
            BaseManager, 
            ApplicationController,
            ComponentInterface,
            ManagerInterface
        )
        logger.info("✅ Core module imports successful")
        
        # Test settings module imports
        logger.info("Testing settings module imports...")
        from mods.settings import SettingsManager, ConfigManager, EnvironmentManager
        logger.info("✅ Settings module imports successful")
        
        # Test AI module imports
        logger.info("Testing AI module imports...")
        from mods.ai import AIManager, ChatHandler, AgentMode
        logger.info("✅ AI module imports successful")
        
        # Test UI module imports
        logger.info("Testing UI module imports...")
        from mods.ui import MenuManager, DisplayManager, TerminalInterface
        logger.info("✅ UI module imports successful")
        
        # Test CLI module imports
        logger.info("Testing CLI module imports...")
        from mods.cli import CLIManager, ProjectCLI, TaskCLI
        logger.info("✅ CLI module imports successful")
        
        # Test application controller initialization
        logger.info("Testing application controller initialization...")
        app_controller = ApplicationController()
        app_controller.initialize()
        
        # Get status
        status = app_controller.get_application_status()
        logger.info(f"Application status: {status}")
        
        # Cleanup
        app_controller.cleanup()
        
        logger.info("🎉 All modular architecture tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Modular architecture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_modular_architecture()
    sys.exit(0 if success else 1) 