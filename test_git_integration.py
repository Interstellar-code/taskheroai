#!/usr/bin/env python3
"""
Test script for Git integration functionality.
"""

import sys
import os
import importlib.util
from pathlib import Path

def load_module(name, path):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_git_integration():
    """Test the Git integration functionality."""
    print("🧪 Testing TaskHero AI Git Integration")
    print("=" * 50)
    
    try:
        # Load modules
        print("📦 Loading Git modules...")
        vm_module = load_module('version_manager', 'mods/git/version_manager.py')
        
        # Test VersionManager
        print("\n🔍 Testing VersionManager...")
        vm = vm_module.VersionManager()
        
        # Get current version
        current = vm.get_current_version()
        print(f"   Current version: {current.get('version', 'unknown')}")
        print(f"   Current commit: {current.get('commit_hash', 'unknown')[:8]}")
        print(f"   Is Git repo: {current.get('is_git_repo', False)}")
        print(f"   Has uncommitted changes: {current.get('has_uncommitted_changes', False)}")
        
        # Test remote version check
        print("\n🌐 Testing remote version check...")
        remote = vm.get_remote_version()
        
        if remote.get('success'):
            print(f"   ✅ Remote check successful")
            print(f"   Remote commit: {remote.get('commit_hash', 'unknown')[:8]}")
            print(f"   Remote version: {remote.get('version', 'unknown')}")
            print(f"   Last commit author: {remote.get('author', 'unknown')}")
        else:
            print(f"   ❌ Remote check failed: {remote.get('error', 'unknown')}")
        
        # Test version comparison
        print("\n🔄 Testing version comparison...")
        comparison = vm.compare_versions(current, remote)
        print(f"   Message: {comparison.get('message', 'unknown')}")
        print(f"   Update available: {comparison.get('update_available', False)}")
        print(f"   Can update: {comparison.get('can_update', False)}")
        
        if comparison.get('update_available'):
            print(f"   🎉 Update available!")
            print(f"   Current: {comparison.get('current_hash', 'unknown')}")
            print(f"   Remote: {comparison.get('remote_hash', 'unknown')}")
        else:
            print(f"   ✅ Up to date")
        
        print("\n✅ Git integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Git integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_git_integration()
    sys.exit(0 if success else 1)
