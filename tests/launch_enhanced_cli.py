#!/usr/bin/env python3
"""
Enhanced CLI Launcher for TaskHero AI

This script launches the Enhanced CLI interface with proper initialization
to ensure the Kanban board and all task management features work correctly.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the Enhanced CLI interface."""
    try:
        # Import necessary modules
        from enhanced_cli import EnhancedCLI
        
        # Create a mock app object with required attributes
        class MockApp:
            def __init__(self):
                self.indexer = None
                self.index_outdated = False
                self.project_planner = None
                self.task_manager = None
                self.enable_markdown_rendering = True
                self.show_thinking_blocks = False
                self.enable_streaming_mode = True
            
            def toggle_markdown_rendering(self):
                self.enable_markdown_rendering = not self.enable_markdown_rendering
                print(f"Markdown rendering: {'Enabled' if self.enable_markdown_rendering else 'Disabled'}")
            
            def toggle_thinking_blocks(self):
                self.show_thinking_blocks = not self.show_thinking_blocks
                print(f"Thinking blocks: {'Enabled' if self.show_thinking_blocks else 'Disabled'}")
            
            def toggle_streaming_mode(self):
                self.enable_streaming_mode = not self.enable_streaming_mode
                print(f"Streaming mode: {'Enabled' if self.enable_streaming_mode else 'Disabled'}")
        
        # Create the app and CLI
        app = MockApp()
        cli = EnhancedCLI(app)
        
        # Main menu loop
        while True:
            cli.display_enhanced_menu()
            
            try:
                choice = input("\nEnter your choice: ").strip()
                
                if choice == "0" or choice.lower() == "exit":
                    print("\n👋 Goodbye!")
                    break
                elif choice == "9":
                    print("\n📋 Task Dashboard would launch here")
                    print("(This requires the full TaskHero AI application)")
                    input("Press Enter to continue...")
                elif choice == "10":
                    cli.launch_kanban_board()
                elif choice == "11":
                    cli.quick_create_task()
                elif choice == "12":
                    cli.quick_view_tasks()
                elif choice == "13":
                    cli.quick_search_tasks()
                elif choice == "14":
                    cli.show_project_overview()
                elif choice == "16":
                    cli.show_settings_menu()
                elif choice == "17":
                    cli.show_help()
                elif choice == "18":
                    os.system('cls' if os.name == 'nt' else 'clear')
                else:
                    print(f"\n❌ Invalid choice: {choice}")
                    print("Please select a valid option (0-18)")
                    input("Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and all dependencies are installed.")
        print("Try running: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 