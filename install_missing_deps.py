#!/usr/bin/env python3
"""
Script to check and install missing dependencies for TaskHero AI.
"""

import subprocess
import sys
import os

def check_and_install_package(package_name, import_name=None):
    """Check if a package is installed and install it if missing."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} is already installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is missing. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package_name}: {e}")
            return False

def main():
    """Check and install critical dependencies."""
    print("🔍 Checking TaskHero AI Dependencies")
    print("=" * 50)
    
    # Critical dependencies that were missing
    critical_deps = [
        ("jinja2", "jinja2"),
        ("scikit-learn", "sklearn"),
        ("httpx", "httpx"),
        ("httpx-sse", "httpx_sse"),
        ("python-dotenv", "dotenv"),
        ("colorama", "colorama"),
        ("numpy", "numpy"),
        ("anthropic", "anthropic"),
        ("openai", "openai"),
        ("ollama", "ollama"),
    ]
    
    print("\n📦 Checking critical dependencies...")
    
    failed_installs = []
    
    for package, import_name in critical_deps:
        if not check_and_install_package(package, import_name):
            failed_installs.append(package)
    
    print("\n" + "=" * 50)
    
    if failed_installs:
        print(f"❌ Failed to install: {', '.join(failed_installs)}")
        print("\n💡 Try running:")
        print("  pip install -r requirements.txt")
        print("  or")
        print("  pip install --upgrade pip")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("✅ All critical dependencies are installed!")
        
        # Test imports
        print("\n🧪 Testing imports...")
        try:
            import jinja2
            import sklearn
            import httpx
            import dotenv
            import colorama
            import numpy
            print("✅ All imports successful!")
            
            # Test TaskHero AI modules
            print("\n🧪 Testing TaskHero AI modules...")
            sys.path.insert(0, os.getcwd())
            
            try:
                from mods.ai.providers.deepseek_provider import DeepSeekProvider
                print("✅ DeepSeek provider import successful!")
            except Exception as e:
                print(f"⚠️  DeepSeek provider import issue: {e}")
            
            try:
                from mods.ai.providers.provider_factory import ProviderFactory
                print("✅ Provider factory import successful!")
            except Exception as e:
                print(f"⚠️  Provider factory import issue: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Import test failed: {e}")
            return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 All dependencies are properly installed!")
        print("You can now run TaskHero AI without dependency issues.")
    else:
        print("\n⚠️  Some dependencies are missing or failed to install.")
        print("Please check the errors above and try manual installation.")
    
    sys.exit(0 if success else 1)
