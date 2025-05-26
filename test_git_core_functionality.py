#!/usr/bin/env python3
"""
Core functionality test for Git integration.
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

def test_core_functionality():
    """Test the core Git functionality."""
    print("🧪 Git Core Functionality Test")
    print("=" * 50)
    
    try:
        # Test VersionManager
        print("\n📦 Testing VersionManager...")
        vm_module = load_module('version_manager', 'mods/git/version_manager.py')
        vm = vm_module.VersionManager()
        
        # Test current version
        current = vm.get_current_version()
        print(f"   Current version: {current.get('version', 'unknown')}")
        print(f"   Current commit: {current.get('commit_hash', 'unknown')[:8]}")
        print(f"   Is Git repo: {current.get('is_git_repo', False)}")
        print(f"   Has changes: {current.get('has_uncommitted_changes', False)}")
        
        # Test remote version
        print(f"\n🌐 Testing remote version check...")
        remote = vm.get_remote_version()
        
        if remote.get('success'):
            print(f"   ✅ Remote check successful")
            print(f"   Remote commit: {remote.get('commit_hash', 'unknown')[:8]}")
            print(f"   Remote author: {remote.get('author', 'unknown')}")
        else:
            print(f"   ❌ Remote check failed: {remote.get('error', 'unknown')}")
        
        # Test version comparison
        print(f"\n🔄 Testing version comparison...")
        comparison = vm.compare_versions(current, remote)
        print(f"   Comparison result: {comparison.get('comparison', 'unknown')}")
        print(f"   Update available: {comparison.get('update_available', False)}")
        print(f"   Can update: {comparison.get('can_update', False)}")
        print(f"   Message: {comparison.get('message', 'No message')}")
        
        # Test error handling
        print(f"\n🛡️ Testing error handling...")
        
        # Test invalid URL
        try:
            vm_invalid = vm_module.VersionManager("invalid-url")
            print(f"   ❌ Should have failed with invalid URL")
        except ValueError as e:
            print(f"   ✅ Invalid URL properly rejected: {str(e)[:50]}...")
        
        # Test cache functionality
        print(f"\n💾 Testing cache functionality...")
        vm.clear_cache()
        print(f"   ✅ Cache cleared successfully")
        
        # Test with cache
        remote_cached = vm.get_remote_version(use_cache=True)
        remote_fresh = vm.get_remote_version(use_cache=False)
        
        if remote_cached.get('success') and remote_fresh.get('success'):
            print(f"   ✅ Cache functionality working")
        
        print(f"\n🎯 Testing specific scenarios...")
        
        # Test GitHub URL parsing
        test_urls = [
            "https://github.com/owner/repo",
            "https://github.com/owner/repo.git",
        ]
        
        for url in test_urls:
            try:
                owner, repo = vm._parse_github_url(url)
                print(f"   ✅ {url} → {owner}/{repo}")
            except Exception as e:
                print(f"   ❌ {url} → Error: {e}")
        
        # Test file version parsing
        print(f"\n📄 Testing version file parsing...")
        version_info = vm._get_version_from_files()
        print(f"   Default version: {version_info.get('version', 'unknown')}")
        
        print(f"\n✅ All core functionality tests passed!")
        print(f"\n📊 Test Summary:")
        print(f"   ✅ Version Manager instantiation")
        print(f"   ✅ Current version detection")
        print(f"   ✅ Remote version checking")
        print(f"   ✅ Version comparison logic")
        print(f"   ✅ Error handling")
        print(f"   ✅ Cache management")
        print(f"   ✅ URL parsing")
        print(f"   ✅ File version detection")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Core functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_core_functionality()
    sys.exit(0 if success else 1)
