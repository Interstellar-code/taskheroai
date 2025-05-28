#!/usr/bin/env python3
"""
AI Task Creation Automation Script

This script automates the task creation process using AI providers configured in the .env file.
It generates tasks for each provider/model combination and stores the results for testing and comparison.

Usage:
    python tests/ai_task_automation.py
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env", override=True)

# Import TaskHero AI modules
try:
    from mods.project_management.ai_task_creator import AITaskCreator
    from mods.project_management.task_manager import TaskManager, TaskPriority, TaskStatus
    from mods.ai.providers.provider_factory import ProviderFactory
    from mods.settings.ai_settings_manager import AISettingsManager
except ImportError as e:
    print(f"Error importing TaskHero AI modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)


@dataclass
class TaskTestCase:
    """Test case for task creation."""
    title: str
    description: str
    task_type: str = "Development"
    priority: str = "medium"
    assigned_to: str = "Developer"
    due_date: Optional[str] = None
    tags: List[str] = None
    dependencies: List[str] = None
    effort_estimate: str = "Medium"
    requirements: str = ""
    acceptance_criteria: str = ""
    additional_notes: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if not self.due_date:
            # Set due date to 1 week from now
            self.due_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    name: str
    model: str
    enabled: bool
    api_key: Optional[str] = None
    host: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7


@dataclass
class TaskCreationResult:
    """Result of task creation attempt."""
    provider: str
    model: str
    success: bool
    task_id: Optional[str] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    quality_score: float = 0.0
    content_length: int = 0


class AITaskAutomation:
    """Main automation class for AI task creation testing."""

    def __init__(self, output_dir: str = "tests"):
        """Initialize the automation system."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organized output
        self.results_dir = self.output_dir / "ai_task_results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.reports_dir = self.output_dir / "automation_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.ai_creator = None
        self.provider_factory = ProviderFactory()
        self.ai_settings = AISettingsManager()
        
        # Test cases
        self.test_cases = self.create_test_cases()
        
        # Results storage
        self.results: List[TaskCreationResult] = []

    def setup_logging(self):
        """Setup logging for the automation."""
        log_file = self.output_dir / f"ai_task_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("AITaskAutomation")
        self.logger.info(f"AI Task Automation started - Log file: {log_file}")

    def create_test_cases(self) -> List[TaskTestCase]:
        """Create a variety of test cases for task creation."""
        test_cases = [
            TaskTestCase(
                title="Implement User Authentication System",
                description="Create a comprehensive user authentication system with login, registration, password reset, and session management. The system should support multiple authentication methods including email/password and OAuth integration.",
                task_type="Development",
                priority="high",
                tags=["authentication", "security", "backend", "api"],
                dependencies=["Database setup", "Security framework configuration"],
                effort_estimate="Large",
                requirements="Support email/password and OAuth authentication, secure session management, password reset functionality",
                acceptance_criteria="Users can register, login, logout, and reset passwords. OAuth integration works with Google and GitHub.",
                additional_notes="Consider implementing 2FA in future iterations"
            ),
            TaskTestCase(
                title="Fix Memory Leak in Data Processing Module",
                description="Investigate and fix a memory leak that occurs during large dataset processing. The issue causes the application to consume excessive memory over time.",
                task_type="Bug Fix",
                priority="critical",
                tags=["bugfix", "performance", "memory", "optimization"],
                dependencies=["Performance profiling tools setup"],
                effort_estimate="Medium",
                requirements="Identify root cause of memory leak and implement fix without breaking existing functionality",
                acceptance_criteria="Memory usage remains stable during long-running data processing tasks",
                additional_notes="Issue reported by multiple users processing datasets larger than 1GB"
            ),
            TaskTestCase(
                title="Create API Documentation",
                description="Write comprehensive API documentation for all REST endpoints including request/response examples, authentication requirements, and error codes.",
                task_type="Documentation",
                priority="medium",
                tags=["documentation", "api", "reference", "developer-experience"],
                dependencies=["API endpoints finalized"],
                effort_estimate="Medium",
                requirements="Document all endpoints with examples, authentication, and error handling",
                acceptance_criteria="Complete API documentation is available and accessible to developers",
                additional_notes="Use OpenAPI/Swagger format for interactive documentation"
            ),
            TaskTestCase(
                title="Setup Automated Testing Pipeline",
                description="Implement a comprehensive automated testing pipeline with unit tests, integration tests, and end-to-end tests. Include code coverage reporting and automated test execution on pull requests.",
                task_type="Test Case",
                priority="high",
                tags=["testing", "automation", "ci-cd", "quality-assurance"],
                dependencies=["CI/CD platform selection"],
                effort_estimate="Large",
                requirements="Automated test execution, code coverage reporting, integration with version control",
                acceptance_criteria="Tests run automatically on code changes with detailed reporting",
                additional_notes="Target 80% code coverage minimum"
            ),
            TaskTestCase(
                title="Design User Dashboard Interface",
                description="Create wireframes and mockups for a user dashboard that displays key metrics, recent activity, and quick action buttons. Focus on usability and responsive design.",
                task_type="Design",
                priority="medium",
                tags=["design", "ui-ux", "dashboard", "wireframes"],
                dependencies=["User research completion"],
                effort_estimate="Medium",
                requirements="Responsive design, accessibility compliance, user-friendly interface",
                acceptance_criteria="Complete wireframes and mockups approved by stakeholders",
                additional_notes="Consider mobile-first design approach"
            )
        ]
        
        return test_cases

    def get_configured_providers(self) -> List[ProviderConfig]:
        """Get all configured AI providers from environment variables."""
        providers = []
        
        # Initialize AI settings
        try:
            self.ai_settings.initialize()
        except Exception as e:
            self.logger.warning(f"Could not initialize AI settings: {e}")
        
        # OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here':
            providers.append(ProviderConfig(
                name="openai",
                model=os.getenv('OPENAI_MODEL', 'gpt-4'),
                enabled=True,
                api_key=openai_key,
                max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4000')),
                temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            ))
        
        # Anthropic
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key and anthropic_key != 'your_anthropic_api_key_here':
            providers.append(ProviderConfig(
                name="anthropic",
                model=os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
                enabled=True,
                api_key=anthropic_key,
                max_tokens=int(os.getenv('ANTHROPIC_MAX_TOKENS', '4000')),
                temperature=float(os.getenv('ANTHROPIC_TEMPERATURE', '0.7'))
            ))
        
        # Ollama
        ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        providers.append(ProviderConfig(
            name="ollama",
            model=os.getenv('OLLAMA_MODEL', 'llama2'),
            enabled=True,
            host=ollama_host,
            max_tokens=int(os.getenv('OLLAMA_MAX_TOKENS', '4000')),
            temperature=float(os.getenv('OLLAMA_TEMPERATURE', '0.7'))
        ))
        
        # OpenRouter
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_key and openrouter_key != 'your_openrouter_api_key_here':
            providers.append(ProviderConfig(
                name="openrouter",
                model=os.getenv('OPENROUTER_MODEL', 'openai/gpt-4'),
                enabled=True,
                api_key=openrouter_key,
                max_tokens=int(os.getenv('OPENROUTER_MAX_TOKENS', '4000')),
                temperature=float(os.getenv('OPENROUTER_TEMPERATURE', '0.7'))
            ))
        
        # DeepSeek (if configured)
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key and deepseek_key != 'your_deepseek_api_key_here':
            providers.append(ProviderConfig(
                name="deepseek",
                model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
                enabled=True,
                api_key=deepseek_key,
                max_tokens=int(os.getenv('DEEPSEEK_MAX_TOKENS', '4000')),
                temperature=float(os.getenv('DEEPSEEK_TEMPERATURE', '0.7'))
            ))
        
        self.logger.info(f"Found {len(providers)} configured AI providers")
        for provider in providers:
            self.logger.info(f"  - {provider.name}: {provider.model}")
        
        return providers

    async def test_provider_availability(self, provider: ProviderConfig) -> bool:
        """Test if a provider is available and working."""
        try:
            self.logger.info(f"Testing provider availability: {provider.name}")
            
            # Create provider instance
            provider_instance = await self.provider_factory.create_provider(provider.name)
            
            if provider_instance:
                # Test with a simple prompt
                test_response = await provider_instance.generate_response(
                    "Hello, please respond with 'OK' if you can process this request.",
                    max_tokens=10,
                    temperature=0.1
                )
                
                if test_response and len(test_response.strip()) > 0:
                    self.logger.info(f"✓ Provider {provider.name} is available")
                    return True
                else:
                    self.logger.warning(f"✗ Provider {provider.name} returned empty response")
                    return False
            else:
                self.logger.warning(f"✗ Could not create provider instance for {provider.name}")
                return False
                
        except Exception as e:
            self.logger.warning(f"✗ Provider {provider.name} test failed: {e}")
            return False

    async def create_task_with_provider(self, test_case: TaskTestCase, provider: ProviderConfig) -> TaskCreationResult:
        """Create a task using a specific provider."""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Creating task '{test_case.title}' with {provider.name} ({provider.model})")
            
            # Initialize AI Task Creator if not already done
            if not self.ai_creator:
                self.ai_creator = AITaskCreator(project_root=str(project_root))
            
            # Create the task using AI enhancement
            success, task_id, file_path = await self.ai_creator.create_enhanced_task(
                title=test_case.title,
                description=test_case.description,
                task_type=test_case.task_type,
                priority=test_case.priority,
                assigned_to=test_case.assigned_to,
                due_date=test_case.due_date,
                tags=test_case.tags,
                dependencies=test_case.dependencies,
                effort_estimate=test_case.effort_estimate,
                use_ai_enhancement=True
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if success:
                # Read the created file to get content length and quality info
                content_length = 0
                quality_score = 0.0
                
                if file_path and os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        content_length = len(content)
                    
                    # Copy the file to our results directory with provider info
                    result_filename = f"{task_id}_{provider.name}_{provider.model.replace('/', '_')}.md"
                    result_path = self.results_dir / result_filename
                    
                    with open(result_path, 'w', encoding='utf-8') as f:
                        f.write(f"<!-- Generated by {provider.name} ({provider.model}) -->\n")
                        f.write(f"<!-- Execution time: {execution_time:.2f}s -->\n")
                        f.write(f"<!-- Content length: {content_length} characters -->\n\n")
                        f.write(content)
                    
                    self.logger.info(f"✓ Task created successfully: {task_id} ({content_length} chars, {execution_time:.2f}s)")
                
                return TaskCreationResult(
                    provider=provider.name,
                    model=provider.model,
                    success=True,
                    task_id=task_id,
                    file_path=str(result_path) if 'result_path' in locals() else file_path,
                    execution_time=execution_time,
                    content_length=content_length,
                    quality_score=quality_score
                )
            else:
                self.logger.error(f"✗ Task creation failed: {file_path}")
                return TaskCreationResult(
                    provider=provider.name,
                    model=provider.model,
                    success=False,
                    error_message=str(file_path),
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"✗ Error creating task with {provider.name}: {e}")
            return TaskCreationResult(
                provider=provider.name,
                model=provider.model,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )

    async def run_automation(self):
        """Run the complete automation process."""
        self.logger.info("Starting AI Task Creation Automation")
        
        # Get configured providers
        providers = self.get_configured_providers()
        
        if not providers:
            self.logger.error("No AI providers configured. Please check your .env file.")
            return
        
        # Test provider availability
        available_providers = []
        for provider in providers:
            if await self.test_provider_availability(provider):
                available_providers.append(provider)
        
        if not available_providers:
            self.logger.error("No AI providers are available. Please check your configuration.")
            return
        
        self.logger.info(f"Testing with {len(available_providers)} available providers")
        
        # Run tests for each combination of test case and provider
        total_tests = len(self.test_cases) * len(available_providers)
        current_test = 0
        
        for test_case in self.test_cases:
            self.logger.info(f"\n--- Testing: {test_case.title} ---")
            
            for provider in available_providers:
                current_test += 1
                self.logger.info(f"Progress: {current_test}/{total_tests}")
                
                result = await self.create_task_with_provider(test_case, provider)
                self.results.append(result)
                
                # Add a small delay between requests to be respectful to APIs
                await asyncio.sleep(1)
        
        # Generate reports
        self.generate_reports()
        
        self.logger.info("AI Task Creation Automation completed")

    def generate_reports(self):
        """Generate comprehensive reports of the automation results."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Summary report
        self.generate_summary_report(timestamp)
        
        # Detailed results
        self.generate_detailed_report(timestamp)
        
        # Provider comparison
        self.generate_provider_comparison(timestamp)
        
        # JSON data export
        self.export_json_data(timestamp)

    def generate_summary_report(self, timestamp: str):
        """Generate a summary report."""
        report_path = self.reports_dir / f"summary_report_{timestamp}.md"
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests
        
        # Calculate statistics
        avg_execution_time = sum(r.execution_time for r in self.results) / total_tests if total_tests > 0 else 0
        avg_content_length = sum(r.content_length for r in self.results if r.success) / successful_tests if successful_tests > 0 else 0
        
        # Provider success rates
        provider_stats = {}
        for result in self.results:
            if result.provider not in provider_stats:
                provider_stats[result.provider] = {'total': 0, 'success': 0}
            provider_stats[result.provider]['total'] += 1
            if result.success:
                provider_stats[result.provider]['success'] += 1
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# AI Task Creation Automation - Summary Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"## Overall Statistics\n\n")
            f.write(f"- **Total Tests**: {total_tests}\n")
            f.write(f"- **Successful**: {successful_tests} ({successful_tests/total_tests*100:.1f}%)\n")
            f.write(f"- **Failed**: {failed_tests} ({failed_tests/total_tests*100:.1f}%)\n")
            f.write(f"- **Average Execution Time**: {avg_execution_time:.2f} seconds\n")
            f.write(f"- **Average Content Length**: {avg_content_length:.0f} characters\n\n")
            
            f.write(f"## Provider Performance\n\n")
            f.write(f"| Provider | Model | Success Rate | Avg Time (s) | Avg Length |\n")
            f.write(f"|----------|-------|--------------|--------------|------------|\n")
            
            for provider, stats in provider_stats.items():
                success_rate = stats['success'] / stats['total'] * 100
                provider_results = [r for r in self.results if r.provider == provider]
                avg_time = sum(r.execution_time for r in provider_results) / len(provider_results)
                successful_results = [r for r in provider_results if r.success]
                avg_length = sum(r.content_length for r in successful_results) / len(successful_results) if successful_results else 0
                
                # Get model name
                model = provider_results[0].model if provider_results else "Unknown"
                
                f.write(f"| {provider} | {model} | {success_rate:.1f}% | {avg_time:.2f} | {avg_length:.0f} |\n")
            
            f.write(f"\n## Test Cases\n\n")
            test_case_names = list(set(tc.title for tc in self.test_cases))
            for test_case in test_case_names:
                case_results = [r for r in self.results if any(tc.title == test_case for tc in self.test_cases)]
                successful_case = len([r for r in case_results if r.success])
                total_case = len(case_results)
                f.write(f"- **{test_case}**: {successful_case}/{total_case} successful\n")
        
        self.logger.info(f"Summary report generated: {report_path}")

    def generate_detailed_report(self, timestamp: str):
        """Generate a detailed report with all results."""
        report_path = self.reports_dir / f"detailed_report_{timestamp}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# AI Task Creation Automation - Detailed Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Group results by test case
            test_cases_dict = {tc.title: tc for tc in self.test_cases}
            
            for test_case_title, test_case in test_cases_dict.items():
                f.write(f"## Test Case: {test_case_title}\n\n")
                f.write(f"**Description**: {test_case.description}\n\n")
                f.write(f"**Type**: {test_case.task_type} | **Priority**: {test_case.priority} | **Effort**: {test_case.effort_estimate}\n\n")
                
                case_results = [r for r in self.results if test_case_title in [tc.title for tc in self.test_cases]]
                
                f.write(f"### Results\n\n")
                f.write(f"| Provider | Model | Status | Time (s) | Length | Task ID | Error |\n")
                f.write(f"|----------|-------|--------|----------|--------|---------|-------|\n")
                
                for result in case_results:
                    status = "✅ Success" if result.success else "❌ Failed"
                    error = result.error_message[:50] + "..." if result.error_message and len(result.error_message) > 50 else (result.error_message or "")
                    
                    f.write(f"| {result.provider} | {result.model} | {status} | {result.execution_time:.2f} | {result.content_length} | {result.task_id or 'N/A'} | {error} |\n")
                
                f.write(f"\n---\n\n")
        
        self.logger.info(f"Detailed report generated: {report_path}")

    def generate_provider_comparison(self, timestamp: str):
        """Generate a provider comparison report."""
        report_path = self.reports_dir / f"provider_comparison_{timestamp}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# AI Provider Comparison Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Get unique providers
            providers = list(set(r.provider for r in self.results))
            
            for provider in providers:
                provider_results = [r for r in self.results if r.provider == provider]
                successful_results = [r for r in provider_results if r.success]
                
                f.write(f"## {provider.title()}\n\n")
                
                if provider_results:
                    model = provider_results[0].model
                    f.write(f"**Model**: {model}\n\n")
                
                f.write(f"**Performance Metrics**:\n")
                f.write(f"- Success Rate: {len(successful_results)}/{len(provider_results)} ({len(successful_results)/len(provider_results)*100:.1f}%)\n")
                
                if successful_results:
                    avg_time = sum(r.execution_time for r in successful_results) / len(successful_results)
                    avg_length = sum(r.content_length for r in successful_results) / len(successful_results)
                    min_time = min(r.execution_time for r in successful_results)
                    max_time = max(r.execution_time for r in successful_results)
                    
                    f.write(f"- Average Execution Time: {avg_time:.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)\n")
                    f.write(f"- Average Content Length: {avg_length:.0f} characters\n")
                
                # List failed tests if any
                failed_results = [r for r in provider_results if not r.success]
                if failed_results:
                    f.write(f"\n**Failed Tests**:\n")
                    for failed in failed_results:
                        f.write(f"- Error: {failed.error_message}\n")
                
                f.write(f"\n---\n\n")
        
        self.logger.info(f"Provider comparison generated: {report_path}")

    def export_json_data(self, timestamp: str):
        """Export all results as JSON for further analysis."""
        json_path = self.reports_dir / f"automation_data_{timestamp}.json"
        
        # Convert results to dictionaries
        results_data = []
        for result in self.results:
            results_data.append(asdict(result))
        
        # Create comprehensive data structure
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_tests": len(self.results),
                "successful_tests": len([r for r in self.results if r.success]),
                "test_cases_count": len(self.test_cases),
                "providers_tested": list(set(r.provider for r in self.results))
            },
            "test_cases": [asdict(tc) for tc in self.test_cases],
            "results": results_data,
            "summary_statistics": {
                "avg_execution_time": sum(r.execution_time for r in self.results) / len(self.results) if self.results else 0,
                "avg_content_length": sum(r.content_length for r in self.results if r.success) / len([r for r in self.results if r.success]) if any(r.success for r in self.results) else 0
            }
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"JSON data exported: {json_path}")

    def print_summary(self):
        """Print a summary to console."""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        
        print(f"\n{'='*60}")
        print(f"AI TASK CREATION AUTOMATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"Failed: {total_tests - successful_tests} ({(total_tests - successful_tests)/total_tests*100:.1f}%)")
        print(f"\nResults saved in: {self.results_dir}")
        print(f"Reports saved in: {self.reports_dir}")
        print(f"{'='*60}")


async def main():
    """Main function to run the automation."""
    print("AI Task Creation Automation Script")
    print("==================================")
    print("This script will test AI task creation with all configured providers.")
    print("Results will be saved in the tests/ directory.\n")
    
    # Initialize automation
    automation = AITaskAutomation()
    
    try:
        # Run the automation
        await automation.run_automation()
        
        # Print summary
        automation.print_summary()
        
    except KeyboardInterrupt:
        print("\nAutomation interrupted by user.")
    except Exception as e:
        print(f"Error running automation: {e}")
        logging.error(f"Automation error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
