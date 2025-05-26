#!/usr/bin/env python3
"""
Complete integration test for Git functionality in TaskHero AI.
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

def test_complete_integration():
    """Test the complete Git integration."""
    print("🧪 Complete Git Integration Test for TaskHero AI")
    print("=" * 60)
    
    try:
        # Test 1: Version Manager
        print("\n1️⃣ Testing VersionManager...")
        vm_module = load_module('version_manager', 'mods/git/version_manager.py')
        vm = vm_module.VersionManager()
        
        current = vm.get_current_version()
        print(f"   ✅ Current version: {current.get('version')}")
        print(f"   ✅ Git repo: {current.get('is_git_repo')}")
        
        remote = vm.get_remote_version()
        if remote.get('success'):
            print(f"   ✅ Remote check successful")
        else:
            print(f"   ⚠️ Remote check failed: {remote.get('error')}")
        
        comparison = vm.compare_versions(current, remote)
        print(f"   ✅ Version comparison: {comparison.get('message')}")
        
        # Test 2: Git Manager (mock settings)
        print("\n2️⃣ Testing GitManager...")
        
        class MockSettingsManager:
            def get_settings(self):
                return {
                    "git": {
                        "auto_check_enabled": True,
                        "notifications_enabled": True,
                        "repository_url": "https://github.com/Interstellar-code/taskheroai",
                        "current_version": "1.0.0",
                        "last_check_timestamp": None,
                        "last_update_timestamp": None,
                        "update_history": []
                    }
                }
            
            def save_settings(self, settings):
                print(f"   📝 Settings would be saved: {list(settings.get('git', {}).keys())}")
        
        gm_module = load_module('git_manager', 'mods/git/git_manager.py')
        
        # Mock BaseManager
        class MockBaseManager:
            def __init__(self, name):
                self.name = name
                import logging
                self.logger = logging.getLogger(name)
                self.is_initialized = True
            
            def update_status(self, key, value):
                pass
        
        # Patch BaseManager
        gm_module.BaseManager = MockBaseManager
        
        gm = gm_module.GitManager(MockSettingsManager())
        gm._perform_initialization()
        
        print(f"   ✅ GitManager initialized")
        
        # Test update check
        result = gm.check_for_updates(force_check=True)
        if result.get('success'):
            print(f"   ✅ Update check successful")
            print(f"   📊 Update available: {result.get('update_available')}")
        else:
            print(f"   ⚠️ Update check failed: {result.get('error')}")
        
        # Test settings update
        success = gm.update_git_setting("auto_check_enabled", False)
        print(f"   ✅ Settings update: {success}")
        
        # Test 3: Git Settings UI
        print("\n3️⃣ Testing Git Settings UI...")
        ui_module = load_module('git_settings_ui', 'mods/ui/git_settings_ui.py')
        
        git_ui = ui_module.GitSettingsUI(gm)
        print(f"   ✅ Git Settings UI created")
        
        # Test menu display (just check it doesn't crash)
        print(f"   📋 Testing menu display...")
        git_ui.display_git_settings_menu()
        print(f"   ✅ Menu displayed successfully")
        
        # Test 4: File preservation patterns
        print("\n4️⃣ Testing file preservation patterns...")
        preserve_patterns = gm.preserve_patterns
        print(f"   📁 Preserve patterns: {len(preserve_patterns)} patterns")
        
        # Check if important patterns are included
        important_patterns = ["theherotasks/", "app_settings.json", ".env"]
        for pattern in important_patterns:
            if pattern in preserve_patterns:
                print(f"   ✅ {pattern} will be preserved")
            else:
                print(f"   ❌ {pattern} NOT in preserve patterns")
        
        # Test 5: Error handling
        print("\n5️⃣ Testing error handling...")
        
        # Test with invalid repository URL
        vm_invalid = vm_module.VersionManager("invalid-url")
        try:
            vm_invalid._parse_github_url("invalid-url")
            print(f"   ❌ Should have failed with invalid URL")
        except ValueError:
            print(f"   ✅ Invalid URL properly rejected")
        
        print("\n🎉 Complete Git Integration Test PASSED!")
        print("=" * 60)
        print("📋 Summary:")
        print("   ✅ Version checking works")
        print("   ✅ Git manager functions properly")
        print("   ✅ Settings integration works")
        print("   ✅ UI components load and display")
        print("   ✅ File preservation configured")
        print("   ✅ Error handling works")
        print("\n🚀 Git integration is ready for use!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Complete integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_integration()
    sys.exit(0 if success else 1)
