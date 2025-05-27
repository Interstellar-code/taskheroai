#!/usr/bin/env python
# TaskHero AI Setup Test Script
# Created by setup script on 05/27/2025 22:08:02

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from dotenv import load_dotenv

console = Console()

def main():
    console.print(Panel.fit("TaskHero AI Setup Test", style="cyan"))
    console.print("")

    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"Python version: [green]{py_version}[/green]")

    # Check environment
    load_dotenv()
    env_vars = {
        "AI_CHAT_PROVIDER": os.getenv("AI_CHAT_PROVIDER", "Not set"),
        "AI_CHAT_MODEL": os.getenv("AI_CHAT_MODEL", "Not set"),
        "AI_VISION_PROVIDER": os.getenv("AI_VISION_PROVIDER", "Not set"),
        "AI_VISION_MODEL": os.getenv("AI_VISION_MODEL", "Not set"),
        "OLLAMA_HOST": os.getenv("OLLAMA_HOST", "Not set"),
        "APP_DATA_DIR": os.getenv("APP_DATA_DIR", "Not set"),
    }

    console.print("\nEnvironment Configuration:")
    for key, value in env_vars.items():
        color = "green" if value != "Not set" else "red"
        console.print(f"  {key}: [{color}]{value}[/{color}]")

    # Check data directory
    data_dir = os.getenv("APP_DATA_DIR", "./data")
    if os.path.exists(data_dir):
        console.print(f"\nData directory: [green]{os.path.abspath(data_dir)}[/green]")
    else:
        console.print(f"\nData directory: [red]Not found: {os.path.abspath(data_dir)}[/red]")

    # Check Ollama if configured
    if env_vars["AI_CHAT_PROVIDER"] == "ollama" or env_vars["AI_VISION_PROVIDER"] == "ollama":
        console.print("\nChecking Ollama connection...")
        try:
            import requests
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            response = requests.get(f"{ollama_host}/api/version", timeout=5)
            if response.status_code == 200:
                version = response.json().get("version", "unknown")
                console.print(f"  Ollama connection: [green]Success (version: {version})[/green]")
            else:
                console.print(f"  Ollama connection: [red]Failed (status code: {response.status_code})[/red]")
        except Exception as e:
            console.print(f"  Ollama connection: [red]Error: {str(e)}[/red]")
            console.print("  Make sure Ollama is running and accessible.")

    console.print("\n[cyan]Setup test completed![/cyan]")
    console.print("If you see any issues above, please check the documentation or run the setup script again.")

if __name__ == "__main__":
    main()
