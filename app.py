#!/usr/bin/env python
"""
TaskHero AI - Application Entry Point

A clean entry point for the TaskHero AI application that delegates to the modular architecture.
"""

import argparse
import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

import colorama
from colorama import Fore, Style
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

try:
    from mods.banners import display_animated_banner
    from mods.core import ApplicationController
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)


def setup_logging() -> logging.Logger:
    """Set up logging for the application."""
    colorama.init()
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Clean up old logs
    try:
        for file in logs_dir.glob("*"):
            try:
                file.unlink()
            except (PermissionError, OSError):
                pass
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Could not clean up log directory: {e}{Style.RESET_ALL}")
    
    # Create new log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"taskheroai_{timestamp}.log"
    print(f"{Fore.CYAN}Logging to: {Style.BRIGHT}{log_file}{Style.RESET_ALL}")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    return logging.getLogger("TaskHeroAI")


def main():
    """Main application entry point."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="TaskHeroAI Terminal Application")
        parser.add_argument("directory", nargs="?", help="Directory to index")
        parser.add_argument("--serve", type=int, metavar="PORT", help="Run HTTP API server (not implemented in entry point)")
        args = parser.parse_args()
        
        # Handle HTTP server mode
        if args.serve:
            print(f"{Fore.YELLOW}HTTP API server functionality has been moved to separate modules.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please use the HTTP API functionality through the modular interface.{Style.RESET_ALL}")
            return
        
        # Display banner
        display_animated_banner(frame_delay=0.2)
        print(f"{Fore.CYAN}{Style.BRIGHT}Starting TaskHeroAI Terminal Application...{Style.RESET_ALL}")
        
        # Setup logging
        logger = setup_logging()
        logger.info("Starting TaskHeroAI Terminal Application")
        
        # Create and run the application controller
        app_controller = ApplicationController()
        
        # Handle directory argument
        if args.directory:
            if os.path.isdir(args.directory):
                print(f"{Fore.CYAN}Using directory from command line: {Style.BRIGHT}{args.directory}{Style.RESET_ALL}")
                # Set the directory in settings manager after initialization
                app_controller.initialize()
                if app_controller.settings_manager:
                    app_controller.settings_manager.set_last_directory(args.directory)
            else:
                print(f"{Fore.RED}Error: '{args.directory}' is not a valid directory.{Style.RESET_ALL}")
                return
        
        # Run the application
        app_controller.run()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Application terminated by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"\n{Fore.RED}{Style.BRIGHT}CRITICAL ERROR: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}See logs for details.{Style.RESET_ALL}")
        print(f"{Fore.RED}Error details:\n{error_details}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
