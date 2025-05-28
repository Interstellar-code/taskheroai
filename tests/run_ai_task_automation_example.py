#!/usr/bin/env python3
"""
Example Script for AI Task Creation Automation

This script demonstrates how to use the AI task creation automation system.
It provides a simple interface to test the task creation functionality.

Usage:
    python tests/run_ai_task_automation_example.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env", override=True)


def check_environment():
    """Check if the environment is properly configured."""
    print("Checking Environment Configuration...")
    print("=" * 40)
    
    # Check for .env file
    env_file = project_root / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and configure your AI providers.")
        return False
    
    print("✅ .env file found")
    
    # Check for configured providers
    providers_found = []
    
    # OpenAI
    if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here':
        providers_found.append(f"OpenAI ({os.getenv('OPENAI_MODEL', 'gpt-4')})")
    
    # Anthropic
    if os.getenv('ANTHROPIC_API_KEY') and os.getenv('ANTHROPIC_API_KEY') != 'your_anthropic_api_key_here':
        providers_found.append(f"Anthropic ({os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')})")
    
    # Ollama (always available if running)
    providers_found.append(f"Ollama ({os.getenv('OLLAMA_MODEL', 'llama2')})")
    
    # OpenRouter
    if os.getenv('OPENROUTER_API_KEY') and os.getenv('OPENROUTER_API_KEY') != 'your_openrouter_api_key_here':
        providers_found.append(f"OpenRouter ({os.getenv('OPENROUTER_MODEL', 'openai/gpt-4')})")
    
    # DeepSeek
    if os.getenv('DEEPSEEK_API_KEY') and os.getenv('DEEPSEEK_API_KEY') != 'your_deepseek_api_key_here':
        providers_found.append(f"DeepSeek ({os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')})")
    
    if providers_found:
        print(f"✅ Found {len(providers_found)} configured providers:")
        for provider in providers_found:
            print(f"   - {provider}")
    else:
        print("⚠️  No API-based providers configured (only Ollama will be tested)")
        print("   Consider configuring OpenAI, Anthropic, or other providers for better testing")
    
    print()
    return True


def show_menu():
    """Show the main menu."""
    print("AI Task Creation Automation")
    print("=" * 30)
    print("1. Run Quick Test (Single task, all providers)")
    print("2. Run Full Test Suite (All test cases, all providers)")
    print("3. Test Specific Provider")
    print("4. Create Custom Task")
    print("5. List Configured Providers")
    print("6. View Test Cases")
    print("7. Check Results Directory")
    print("0. Exit")
    print()


async def run_quick_test():
    """Run a quick test."""
    print("\nRunning Quick Test...")
    print("This will create one task using all configured providers.")
    
    try:
        from test_ai_task_creation_automation import TestRunner
        import argparse
        
        # Create mock args for quick test
        args = argparse.Namespace(quick=True)
        runner = TestRunner(args)
        
        await runner.run_quick_test()
        
    except Exception as e:
        print(f"Error running quick test: {e}")


async def run_full_test():
    """Run the full test suite."""
    print("\nRunning Full Test Suite...")
    print("This will create multiple tasks using all configured providers.")
    print("This may take several minutes depending on the number of providers.")
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Test cancelled.")
        return
    
    try:
        from ai_task_automation import AITaskAutomation
        
        automation = AITaskAutomation()
        await automation.run_automation()
        automation.print_summary()
        
    except Exception as e:
        print(f"Error running full test: {e}")


async def test_specific_provider():
    """Test a specific provider."""
    print("\nAvailable Providers:")
    
    try:
        from ai_task_automation import AITaskAutomation
        
        automation = AITaskAutomation()
        providers = automation.get_configured_providers()
        
        if not providers:
            print("No providers configured.")
            return
        
        for i, provider in enumerate(providers, 1):
            print(f"{i}. {provider.name} ({provider.model})")
        
        choice = input(f"\nSelect provider (1-{len(providers)}): ").strip()
        
        try:
            provider_index = int(choice) - 1
            if 0 <= provider_index < len(providers):
                selected_provider = providers[provider_index]
                
                from test_ai_task_creation_automation import TestRunner
                import argparse
                
                args = argparse.Namespace(provider=selected_provider.name)
                runner = TestRunner(args)
                
                await runner.run_provider_test(selected_provider.name)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    except Exception as e:
        print(f"Error testing provider: {e}")


async def create_custom_task():
    """Create a custom task."""
    print("\nCustom Task Creation")
    print("=" * 20)
    
    title = input("Task Title: ").strip()
    if not title:
        print("Title is required.")
        return
    
    description = input("Task Description: ").strip()
    if not description:
        print("Description is required.")
        return
    
    try:
        from test_ai_task_creation_automation import TestRunner
        import argparse
        
        args = argparse.Namespace(custom=[title, description])
        runner = TestRunner(args)
        
        await runner.run_custom_test(title, description)
        
    except Exception as e:
        print(f"Error creating custom task: {e}")


def list_providers():
    """List configured providers."""
    try:
        from test_ai_task_creation_automation import TestRunner
        import argparse
        
        args = argparse.Namespace()
        runner = TestRunner(args)
        runner.list_providers()
        
    except Exception as e:
        print(f"Error listing providers: {e}")


def view_test_cases():
    """View available test cases."""
    try:
        from test_ai_task_creation_automation import TestRunner
        import argparse
        
        args = argparse.Namespace()
        runner = TestRunner(args)
        runner.show_test_cases()
        
    except Exception as e:
        print(f"Error viewing test cases: {e}")


def check_results():
    """Check the results directory."""
    results_dir = Path("tests/ai_task_results")
    reports_dir = Path("tests/automation_reports")
    
    print("\nResults Directory Status:")
    print("=" * 25)
    
    if results_dir.exists():
        task_files = list(results_dir.glob("*.md"))
        print(f"✅ Results directory exists: {results_dir}")
        print(f"   Generated tasks: {len(task_files)}")
        
        if task_files:
            print("   Recent tasks:")
            for task_file in sorted(task_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                print(f"   - {task_file.name}")
    else:
        print(f"❌ Results directory not found: {results_dir}")
    
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*.md")) + list(reports_dir.glob("*.json"))
        print(f"✅ Reports directory exists: {reports_dir}")
        print(f"   Generated reports: {len(report_files)}")
        
        if report_files:
            print("   Recent reports:")
            for report_file in sorted(report_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                print(f"   - {report_file.name}")
    else:
        print(f"❌ Reports directory not found: {reports_dir}")
    
    print()


async def main():
    """Main function."""
    print("TaskHero AI - Task Creation Automation Example")
    print("=" * 45)
    print()
    
    # Check environment
    if not check_environment():
        print("Please fix the environment configuration before proceeding.")
        return
    
    while True:
        show_menu()
        choice = input("Select option: ").strip()
        
        try:
            if choice == "1":
                await run_quick_test()
            elif choice == "2":
                await run_full_test()
            elif choice == "3":
                await test_specific_provider()
            elif choice == "4":
                await create_custom_task()
            elif choice == "5":
                list_providers()
            elif choice == "6":
                view_test_cases()
            elif choice == "7":
                check_results()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        except Exception as e:
            print(f"Error: {e}")
        
        if choice != "0":
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
