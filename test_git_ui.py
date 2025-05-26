#!/usr/bin/env python3
"""
Test script for Git Settings UI.
"""

import sys
import os
import asyncio
import importlib.util
from pathlib import Path

def load_module(name, path):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class MockSettingsManager:
    """Mock settings manager for testing."""
    
    def __init__(self):
        self.settings = {
            "git": {
                "auto_check_enabled": True,
                "last_check_timestamp": None,
                "notifications_enabled": True,
                "repository_url": "https://github.com/Interstellar-code/taskheroai",
                "current_version": "1.0.0",
                "last_update_timestamp": None,
                "update_history": []
            }
        }
    
    def get_settings(self):
        return self.settings.copy()
    
    def save_settings(self, settings):
        self.settings = settings
        print(f"✅ Settings saved: {settings.get('git', {})}")

class MockGitManager:
    """Mock Git manager for testing."""
    
    def __init__(self):
        self.settings_manager = MockSettingsManager()
        self.version_manager = None
        
        # Load real version manager
        vm_module = load_module('version_manager', 'mods/git/version_manager.py')
        self.version_manager = vm_module.VersionManager()
    
    def get_update_status(self):
        return {
            "settings": self.settings_manager.get_settings().get("git", {}),
            "last_check": None,
            "version_manager_ready": True,
            "git_available": True,
            "is_git_repo": True
        }
    
    def update_git_setting(self, key, value):
        settings = self.settings_manager.get_settings()
        settings["git"][key] = value
        self.settings_manager.save_settings(settings)
        return True
    
    def check_for_updates(self, force_check=False):
        # Use real version manager
        current = self.version_manager.get_current_version()
        remote = self.version_manager.get_remote_version()
        comparison = self.version_manager.compare_versions(current, remote)
        
        return {
            "success": True,
            "current": current,
            "remote": remote,
            "comparison": comparison,
            "update_available": comparison.get("update_available", False),
            "can_update": comparison.get("can_update", False),
            "message": comparison.get("message", "")
        }

async def test_git_ui():
    """Test the Git Settings UI."""
    print("🧪 Testing Git Settings UI")
    print("=" * 50)
    
    try:
        # Load Git Settings UI module
        print("📦 Loading Git Settings UI...")
        ui_module = load_module('git_settings_ui', 'mods/ui/git_settings_ui.py')
        
        # Create mock Git manager
        git_manager = MockGitManager()
        
        # Create Git Settings UI
        git_ui = ui_module.GitSettingsUI(git_manager)
        
        print("✅ Git Settings UI loaded successfully")
        
        # Test display menu
        print("\n📋 Testing menu display...")
        git_ui.display_git_settings_menu()
        
        print("\n✅ Git Settings UI test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Git Settings UI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_git_ui())
    sys.exit(0 if success else 1)
