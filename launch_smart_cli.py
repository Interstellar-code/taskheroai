#!/usr/bin/env python3
"""
Launcher for TaskHero AI Smart CLI Manager.

This script launches the enhanced CLI manager with smart indexing capabilities.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from mods.cli.cli_manager_smart import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the TaskHero AI project root directory.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error launching Smart CLI: {e}")
    sys.exit(1) 