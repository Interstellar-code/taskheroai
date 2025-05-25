#!/usr/bin/env python3
"""
Simple setup status checker for TaskHero AI
"""

import json
import os
import sys
from datetime import datetime

SETUP_FILE = ".taskhero_setup.json"

def show_status():
    """Show current setup status"""
    if not os.path.exists(SETUP_FILE):
        print("❌ No setup file found. Run setup script first.")
        return
    
    try:
        with open(SETUP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("❌ Setup file is corrupted or unreadable.")
        return
    
    print("🚀 TaskHero AI Setup Status")
    print("=" * 50)
    print(f"📁 Setup file: {SETUP_FILE}")
    print(f"📅 Created: {data.get('created', 'Unknown')}")
    print(f"🔄 Last updated: {data.get('last_updated', 'Unknown')}")
    print()
    
    # Show completed steps
    setup_completed = data.get("setup_completed", {})
    if setup_completed:
        print("✅ Completed Steps:")
        for step, info in setup_completed.items():
            if isinstance(info, dict) and info.get("completed"):
                timestamp = info.get("timestamp", "Unknown")
                print(f"  ✅ {step} ({timestamp})")
            else:
                print(f"  ❌ {step} (not completed)")
    else:
        print("❌ No completed steps found")
    
    print()
    
    # Show configuration
    configuration = data.get("configuration", {})
    if configuration:
        print("⚙️ Configuration:")
        for key, info in configuration.items():
            if isinstance(info, dict):
                value = info.get("value", "Unknown")
                timestamp = info.get("timestamp", "Unknown")
                print(f"  • {key}: {value}")
            else:
                print(f"  • {key}: {info}")
    else:
        print("❌ No configuration found")

def reset_setup():
    """Reset setup progress"""
    if os.path.exists(SETUP_FILE):
        os.remove(SETUP_FILE)
        print(f"✅ Reset complete. Removed {SETUP_FILE}")
    else:
        print("❌ No setup file found to reset.")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        show_status()
        return
    
    command = sys.argv[1].lower()
    
    if command in ["status", "show"]:
        show_status()
    elif command in ["reset", "clear"]:
        reset_setup()
    elif command in ["help", "-h", "--help"]:
        print("TaskHero AI Setup Status Checker")
        print("Usage:")
        print("  python setup_status.py           # Show status")
        print("  python setup_status.py status    # Show status")
        print("  python setup_status.py reset     # Reset setup")
        print("  python setup_status.py help      # Show this help")
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python setup_status.py help' for usage information.")

if __name__ == "__main__":
    main()
