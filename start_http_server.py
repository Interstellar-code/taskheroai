#!/usr/bin/env python3
"""
HTTP Server Launcher for TaskHero AI

This script starts the HTTP API server using the modular interface.
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

import colorama
from colorama import Fore, Style
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

# Initialize colorama
colorama.init()

def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("TaskHeroAI.HTTPServer")

def start_http_server_direct(port: int = 8000, allow_all_origins: bool = False):
    """Start the HTTP server directly using the modular interface."""
    try:
        # Import the HTTP API module
        from mods.http_api import create_app
        import uvicorn
        
        print(f"{Fore.GREEN}Starting TaskHero AI HTTP API Server...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Port: {port}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Allow all origins: {allow_all_origins}{Style.RESET_ALL}")
        
        # Create the app
        app = create_app(allow_all_origins=allow_all_origins)
        
        # Determine host
        host = "0.0.0.0" if allow_all_origins else "127.0.0.1"
        
        print(f"{Fore.GREEN}HTTP API server starting on {host}:{port}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available endpoints:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}- GET  /api/health{Style.RESET_ALL} - Health check")
        print(f"{Fore.CYAN}- POST /api/initialize{Style.RESET_ALL} - Initialize a directory")
        print(f"{Fore.CYAN}- POST /api/ask{Style.RESET_ALL} - Ask the agent a question")
        print(f"{Fore.CYAN}- POST /api/index/start{Style.RESET_ALL} - Start indexing a directory")
        print(f"{Fore.CYAN}- GET  /api/index/status{Style.RESET_ALL} - Get indexing status")
        print(f"{Fore.CYAN}- GET  /api/tasks{Style.RESET_ALL} - Get all tasks")
        print(f"{Fore.CYAN}- POST /api/tasks{Style.RESET_ALL} - Create new task")
        print(f"{Fore.CYAN}- GET  /api/tasks/{{id}}{Style.RESET_ALL} - Get task details")
        print(f"{Fore.CYAN}- PUT  /api/tasks/{{id}}/status{Style.RESET_ALL} - Update task status")
        print(f"{Fore.CYAN}- GET  /api/kanban{Style.RESET_ALL} - Get kanban board data")
        print(f"{Fore.GREEN}Press Ctrl+C to stop the server{Style.RESET_ALL}")
        
        # Run the server
        uvicorn.run(app, host=host, port=port, log_level="info")
        
    except ImportError as e:
        print(f"{Fore.RED}Error importing required modules: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure uvicorn is installed: pip install uvicorn{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Error starting HTTP server: {e}{Style.RESET_ALL}")
        sys.exit(1)

def start_via_mcp_server(port: int = 8000):
    """Start the HTTP server via the MCP server interface."""
    try:
        # Import MCP server functions
        from mcp_server import start_http_server, is_http_server_running
        
        print(f"{Fore.GREEN}Starting HTTP API server via MCP interface...{Style.RESET_ALL}")
        
        # Check if already running
        if is_http_server_running():
            print(f"{Fore.YELLOW}HTTP API server is already running at http://localhost:{port}{Style.RESET_ALL}")
            return True
        
        # Start the server
        process = start_http_server(port)
        
        # Wait a bit and check if it started
        time.sleep(2)
        if is_http_server_running():
            print(f"{Fore.GREEN}HTTP API server started successfully at http://localhost:{port}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Server is running in the background. Use Ctrl+C to stop this script.{Style.RESET_ALL}")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Stopping HTTP server...{Style.RESET_ALL}")
                if process:
                    process.terminate()
                    process.wait()
                print(f"{Fore.GREEN}HTTP server stopped.{Style.RESET_ALL}")
            
            return True
        else:
            print(f"{Fore.RED}Failed to start HTTP API server{Style.RESET_ALL}")
            return False
            
    except ImportError as e:
        print(f"{Fore.RED}Error importing MCP server modules: {e}{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}Error starting HTTP server via MCP: {e}{Style.RESET_ALL}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="TaskHero AI HTTP Server Launcher")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on (default: 8000)")
    parser.add_argument("--allow-all-origins", action="store_true", help="Allow all origins for HTTP API (not just localhost)")
    parser.add_argument("--method", choices=["direct", "mcp"], default="direct", help="Method to start the server (default: direct)")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting TaskHero AI HTTP Server on port {args.port}")
    
    try:
        if args.method == "direct":
            start_http_server_direct(args.port, args.allow_all_origins)
        else:
            start_via_mcp_server(args.port)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Server stopped by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
