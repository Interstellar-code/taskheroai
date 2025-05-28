#!/usr/bin/env python3
"""
Test Runner for AI Task Creation Automation

This script runs the AI task creation automation and provides additional testing utilities.

Usage:
    python tests/test_ai_task_creation_automation.py [options]
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the automation module
from ai_task_automation import AITaskAutomation, TaskTestCase


class TestRunner:
    """Test runner for AI task creation automation."""
    
    def __init__(self, args):
        """Initialize the test runner."""
        self.args = args
        self.automation = AITaskAutomation()
    
    async def run_quick_test(self):
        """Run a quick test with a single test case."""
        print("Running Quick Test...")
        print("====================")
        
        # Create a simple test case
        quick_test_case = TaskTestCase(
            title="Quick Test - Simple Feature Implementation",
            description="Implement a simple feature for testing AI task creation automation. This is a basic test to verify that the automation system is working correctly.",
            task_type="Development",
            priority="medium",
            tags=["test", "automation", "quick"],
            effort_estimate="Small"
        )
        
        # Override test cases with just the quick test
        self.automation.test_cases = [quick_test_case]
        
        # Run automation
        await self.automation.run_automation()
        
        print("\nQuick test completed!")
    
    async def run_provider_test(self, provider_name: str):
        """Run test with a specific provider only."""
        print(f"Running Provider Test: {provider_name}")
        print("=" * (25 + len(provider_name)))
        
        # Get all providers and filter for the specified one
        all_providers = self.automation.get_configured_providers()
        target_providers = [p for p in all_providers if p.name.lower() == provider_name.lower()]
        
        if not target_providers:
            print(f"Error: Provider '{provider_name}' not found or not configured.")
            print(f"Available providers: {[p.name for p in all_providers]}")
            return
        
        # Test only the specified provider
        provider = target_providers[0]
        
        # Test provider availability first
        if not await self.automation.test_provider_availability(provider):
            print(f"Error: Provider '{provider_name}' is not available.")
            return
        
        # Run tests with just this provider
        print(f"Testing with {provider.name} ({provider.model})")
        
        for i, test_case in enumerate(self.automation.test_cases, 1):
            print(f"\nTest {i}/{len(self.automation.test_cases)}: {test_case.title}")
            result = await self.automation.create_task_with_provider(test_case, provider)
            self.automation.results.append(result)
            
            if result.success:
                print(f"✅ Success - Task ID: {result.task_id}")
            else:
                print(f"❌ Failed - Error: {result.error_message}")
        
        # Generate reports
        self.automation.generate_reports()
        print(f"\nProvider test completed for {provider_name}!")
    
    async def run_custom_test(self, title: str, description: str):
        """Run test with custom task input."""
        print("Running Custom Test...")
        print("=====================")
        
        # Create custom test case
        custom_test_case = TaskTestCase(
            title=title,
            description=description,
            task_type="Development",
            priority="medium",
            tags=["custom", "test"],
            effort_estimate="Medium"
        )
        
        # Override test cases with just the custom test
        self.automation.test_cases = [custom_test_case]
        
        # Run automation
        await self.automation.run_automation()
        
        print("\nCustom test completed!")
    
    async def run_template_test(self, template_file: str):
        """Run test using a template file."""
        print(f"Running Template Test: {template_file}")
        print("=" * (23 + len(template_file)))
        
        template_path = Path(template_file)
        if not template_path.exists():
            print(f"Error: Template file '{template_file}' not found.")
            return
        
        # Read and parse template
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Extract title and description from template
            # This is a simple parser - you could make it more sophisticated
            lines = template_content.split('\n')
            title = "Template Test Task"
            description = "Task created from template file"
            
            # Look for title and description in the template
            for line in lines:
                if line.startswith('# ') and 'title' not in line.lower():
                    title = line[2:].strip()
                elif line.startswith('**Title**:'):
                    title = line.split(':', 1)[1].strip()
                elif line.startswith('**Description**:'):
                    description = line.split(':', 1)[1].strip()
            
            # Create test case from template
            template_test_case = TaskTestCase(
                title=title,
                description=description,
                task_type="Development",
                priority="medium",
                tags=["template", "test"],
                effort_estimate="Medium"
            )
            
            # Override test cases
            self.automation.test_cases = [template_test_case]
            
            # Run automation
            await self.automation.run_automation()
            
            print("\nTemplate test completed!")
            
        except Exception as e:
            print(f"Error reading template file: {e}")
    
    def list_providers(self):
        """List all configured providers."""
        print("Configured AI Providers:")
        print("========================")
        
        providers = self.automation.get_configured_providers()
        
        if not providers:
            print("No providers configured. Please check your .env file.")
            return
        
        for provider in providers:
            print(f"- {provider.name}: {provider.model}")
            if provider.api_key:
                print(f"  API Key: {'*' * 8}...{provider.api_key[-4:]}")
            if provider.host:
                print(f"  Host: {provider.host}")
            print(f"  Max Tokens: {provider.max_tokens}")
            print(f"  Temperature: {provider.temperature}")
            print()
    
    def show_test_cases(self):
        """Show all available test cases."""
        print("Available Test Cases:")
        print("====================")
        
        for i, test_case in enumerate(self.automation.test_cases, 1):
            print(f"{i}. {test_case.title}")
            print(f"   Type: {test_case.task_type} | Priority: {test_case.priority}")
            print(f"   Description: {test_case.description[:100]}...")
            print()
    
    async def run_full_test(self):
        """Run the full automation test suite."""
        print("Running Full Test Suite...")
        print("==========================")
        
        await self.automation.run_automation()
        
        print("\nFull test suite completed!")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="AI Task Creation Automation Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick test with single test case")
    parser.add_argument("--provider", type=str, help="Test specific provider only")
    parser.add_argument("--custom", nargs=2, metavar=("TITLE", "DESCRIPTION"), help="Run custom test with title and description")
    parser.add_argument("--template", type=str, help="Run test using template file")
    parser.add_argument("--list-providers", action="store_true", help="List configured providers")
    parser.add_argument("--list-tests", action="store_true", help="List available test cases")
    parser.add_argument("--full", action="store_true", help="Run full test suite (default)")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(args)
    
    try:
        if args.list_providers:
            runner.list_providers()
        elif args.list_tests:
            runner.show_test_cases()
        elif args.quick:
            await runner.run_quick_test()
        elif args.provider:
            await runner.run_provider_test(args.provider)
        elif args.custom:
            await runner.run_custom_test(args.custom[0], args.custom[1])
        elif args.template:
            await runner.run_template_test(args.template)
        else:
            # Default to full test
            await runner.run_full_test()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error running test: {e}")


if __name__ == "__main__":
    asyncio.run(main())
