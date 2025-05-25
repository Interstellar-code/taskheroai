#!/usr/bin/env python
"""
Test full app flow with automated input
"""

import sys
import io
from mods.core import ApplicationController

# Simulate user input
test_input = "0\n"  # Exit immediately
sys.stdin = io.StringIO(test_input)

print("Starting full app flow test...")

try:
    # Create and run the application controller
    app_controller = ApplicationController()
    
    print("Running app.run()...")
    app_controller.run()
    print("App run completed successfully!")
    
except Exception as e:
    print(f"Error during run: {e}")
    import traceback
    traceback.print_exc() 