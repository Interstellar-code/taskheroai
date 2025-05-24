#!/usr/bin/env python
"""
Debug script to test where the app hangs
"""

import traceback
import sys
from mods.core import ApplicationController

print("Starting debug test...")

try:
    # Create and initialize
    print("Creating ApplicationController...")
    app_controller = ApplicationController()
    
    print("Initializing ApplicationController...")
    app_controller.initialize()
    
    print("Showing startup info...")
    app_controller._show_startup_info()
    
    print("Checking CLI manager...")
    if app_controller.cli_manager:
        print("CLI manager exists, about to call run_main_loop...")
        print("CLI manager initialized:", app_controller.cli_manager.is_initialized)
        print("UI manager exists:", app_controller.cli_manager.ui_manager is not None)
        
        # Just try to display menu once
        if app_controller.cli_manager.ui_manager:
            print("Trying to display menu...")
            app_controller.cli_manager.ui_manager.display_main_menu()
            print("Menu displayed successfully!")
        else:
            print("ERROR: UI manager is None")
    else:
        print("ERROR: CLI manager is None")
        
    print("Debug test completed successfully!")
    
except Exception as e:
    print(f"Error during debug: {e}")
    traceback.print_exc() 