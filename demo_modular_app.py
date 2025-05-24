#!/usr/bin/env python
"""
Demo script for the new modular TaskHero AI architecture.

This script demonstrates the modular architecture working with the ApplicationController.
"""

import sys
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_demo_logging():
    """Set up logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def main():
    """Run the modular architecture demo."""
    setup_demo_logging()
    
    print("🚀 TaskHero AI - Modular Architecture Demo")
    print("=" * 50)
    
    try:
        # Import the new modular application controller
        from mods.core import ApplicationController
        
        # Create and run the application
        app = ApplicationController()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 