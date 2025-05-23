"""
Test script for TaskHero AI Integration Module

This script demonstrates how the AI integration generates prompts for external AI agents
to consume. It tests all the major prompt generation functions without requiring actual
AI service integration.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the project root to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from taskhero_ai_integration import AIAgentIntegration, AIPromptGenerator
from mods.project_management.task_manager import TaskManager, TaskStatus, TaskPriority

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaskHero.AI.Integration.Test")


async def test_codebase_analysis_prompt():
    """Test codebase analysis prompt generation."""
    print("\n" + "="*60)
    print("Testing Codebase Analysis Prompt Generation")
    print("="*60)
    
    integration = AIAgentIntegration()
    
    # Test different analysis types
    analysis_types = ["task_generation", "code_quality", "architecture"]
    
    for analysis_type in analysis_types:
        print(f"\n--- Testing Analysis Type: {analysis_type} ---")
        
        prompt_data = await integration.generate_prompt(
            "codebase_analysis",
            analysis_type=analysis_type
        )
        
        if "error" in prompt_data:
            print(f"❌ Error: {prompt_data['error']}")
            continue
        
        print(f"✅ Generated prompt for {analysis_type}")
        print(f"Task Type: {prompt_data['task_type']}")
        print(f"Analysis Type: {prompt_data['analysis_type']}")
        print(f"Timestamp: {prompt_data['timestamp']}")
        print(f"Context Keys: {list(prompt_data['context'].keys())}")
        print(f"Expected Output Format: {prompt_data['expected_output']['format']}")
        print(f"Expected Fields: {prompt_data['expected_output']['fields']}")
        
        # Display a preview of the generated prompt
        prompt_preview = prompt_data['prompt'][:300] + "..." if len(prompt_data['prompt']) > 300 else prompt_data['prompt']
        print(f"Prompt Preview: {prompt_preview}")


async def test_task_prioritization_prompt():
    """Test task prioritization prompt generation."""
    print("\n" + "="*60)
    print("Testing Task Prioritization Prompt Generation")
    print("="*60)
    
    integration = AIAgentIntegration()
    
    prompt_data = await integration.generate_prompt("task_prioritization")
    
    if "error" in prompt_data:
        print(f"❌ Error: {prompt_data['error']}")
        return
    
    print("✅ Generated task prioritization prompt")
    print(f"Task Type: {prompt_data['task_type']}")
    print(f"Timestamp: {prompt_data['timestamp']}")
    print(f"Tasks to Prioritize: {len(prompt_data['tasks_to_prioritize'])}")
    print(f"Context Keys: {list(prompt_data['context'].keys())}")
    
    # Show some task examples
    if prompt_data['tasks_to_prioritize']:
        print("\nSample Tasks:")
        for i, task in enumerate(prompt_data['tasks_to_prioritize'][:3]):
            print(f"  {i+1}. {task['id']}: {task['title']} ({task['status']})")


async def test_code_correlation_prompt():
    """Test code-to-task correlation prompt generation."""
    print("\n" + "="*60)
    print("Testing Code-to-Task Correlation Prompt Generation")
    print("="*60)
    
    integration = AIAgentIntegration()
    
    # Test with mock git diff
    mock_git_diff = """
diff --git a/app.py b/app.py
index 1234567..abcdefg 100644
--- a/app.py
+++ b/app.py
@@ -100,6 +100,10 @@ class TaskHeroAI:
         self.project_templates: Optional[ProjectTemplates] = None
         self.project_planner: Optional[ProjectPlanner] = None
 
+        # AI Integration Components
+        self.ai_integration: Optional[AIAgentIntegration] = None
+        logger.info("AI Integration initialized")
+
         self.enable_markdown_rendering: bool = self._get_env_bool("ENABLE_MARKDOWN_RENDERING", True)
         self.show_thinking_blocks: bool = self._get_env_bool("SHOW_THINKING_BLOCKS", False)
         self.enable_streaming_mode: bool = self._get_env_bool("ENABLE_STREAMING_MODE", False)
"""
    
    prompt_data = await integration.generate_prompt(
        "code_correlation",
        git_diff=mock_git_diff
    )
    
    if "error" in prompt_data:
        print(f"❌ Error: {prompt_data['error']}")
        return
    
    print("✅ Generated code correlation prompt")
    print(f"Task Type: {prompt_data['task_type']}")
    print(f"Timestamp: {prompt_data['timestamp']}")
    print(f"Context Keys: {list(prompt_data['context'].keys())}")
    print(f"Recent Tasks: {len(prompt_data['context']['recent_tasks'])}")
    print(f"File Changes Summary: {prompt_data['context']['file_changes_summary']}")


async def test_project_insights_prompt():
    """Test project insights prompt generation."""
    print("\n" + "="*60)
    print("Testing Project Insights Prompt Generation")
    print("="*60)
    
    integration = AIAgentIntegration()
    
    # Test different insight types
    insight_types = ["comprehensive", "velocity", "quality", "risks"]
    
    for insight_type in insight_types:
        print(f"\n--- Testing Insight Type: {insight_type} ---")
        
        prompt_data = await integration.generate_prompt(
            "project_insights",
            insight_type=insight_type
        )
        
        if "error" in prompt_data:
            print(f"❌ Error: {prompt_data['error']}")
            continue
        
        print(f"✅ Generated insights prompt for {insight_type}")
        print(f"Task Type: {prompt_data['task_type']}")
        print(f"Insight Type: {prompt_data['insight_type']}")
        print(f"Context Keys: {list(prompt_data['context'].keys())}")


async def test_task_breakdown_prompt():
    """Test task breakdown prompt generation."""
    print("\n" + "="*60)
    print("Testing Task Breakdown Prompt Generation")
    print("="*60)
    
    # Create a sample complex task
    task_manager = TaskManager()
    
    # Create a mock complex task
    complex_task = task_manager.create_task(
        title="Implement Advanced AI-Powered Project Analytics Dashboard",
        content="""
        # Task: Implement Advanced AI-Powered Project Analytics Dashboard
        
        ## Overview
        Develop a comprehensive analytics dashboard that leverages AI to provide intelligent insights
        about project progress, team performance, and predictive analytics for project planning.
        
        ## Requirements
        - Real-time data visualization with interactive charts and graphs
        - AI-powered trend analysis and predictions
        - Integration with existing task management system
        - Performance metrics tracking and reporting
        - User role-based access control
        - Export functionality for reports
        - Mobile-responsive design
        - API integration for external data sources
        
        ## Technical Considerations
        - Database schema changes for analytics data storage
        - Frontend framework selection (React/Vue/Angular)
        - Backend API design for data aggregation
        - Caching strategies for performance optimization
        - Security implementation for sensitive data
        - Testing framework setup for complex UI components
        """,
        priority=TaskPriority.HIGH,
        status=TaskStatus.TODO
    )
    
    if not complex_task:
        print("❌ Failed to create complex task for testing")
        return
    
    integration = AIAgentIntegration()
    
    prompt_data = await integration.generate_prompt(
        "task_breakdown",
        task=complex_task
    )
    
    if "error" in prompt_data:
        print(f"❌ Error: {prompt_data['error']}")
        return
    
    print("✅ Generated task breakdown prompt")
    print(f"Task Type: {prompt_data['task_type']}")
    print(f"Target Task ID: {prompt_data['target_task']['id']}")
    print(f"Target Task Title: {prompt_data['target_task']['title']}")
    print(f"Complexity Analysis: {prompt_data['context']['complexity_analysis']}")
    print(f"Related Code Files: {len(prompt_data['context']['related_code_files'])}")
    print(f"Similar Tasks: {len(prompt_data['context']['similar_tasks'])}")


async def test_documentation_prompt():
    """Test documentation generation prompt."""
    print("\n" + "="*60)
    print("Testing Documentation Generation Prompt")
    print("="*60)
    
    integration = AIAgentIntegration()
    
    # Test different documentation types
    doc_types = ["project_summary", "api_docs", "user_guide"]
    
    for doc_type in doc_types:
        print(f"\n--- Testing Documentation Type: {doc_type} ---")
        
        prompt_data = await integration.generate_prompt(
            "documentation",
            doc_type=doc_type
        )
        
        if "error" in prompt_data:
            print(f"❌ Error: {prompt_data['error']}")
            continue
        
        print(f"✅ Generated documentation prompt for {doc_type}")
        print(f"Task Type: {prompt_data['task_type']}")
        print(f"Doc Type: {prompt_data['doc_type']}")
        print(f"Context Keys: {list(prompt_data['context'].keys())}")
        print(f"Code Structure: {len(prompt_data['context']['code_structure'])}")
        print(f"Completed Tasks: {len(prompt_data['context']['completed_tasks'])}")


async def test_available_prompt_types():
    """Test getting available prompt types."""
    print("\n" + "="*60)
    print("Testing Available Prompt Types")
    print("="*60)
    
    integration = AIAgentIntegration()
    available_types = integration.get_available_prompt_types()
    
    print("✅ Available prompt types:")
    for i, prompt_type in enumerate(available_types, 1):
        print(f"  {i}. {prompt_type}")


def save_sample_prompt_output(prompt_data: dict, filename: str):
    """Save a sample prompt output to a file for inspection."""
    try:
        output_dir = Path("logs")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"sample_{filename}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(prompt_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Sample output saved to: {output_file}")
        
    except Exception as e:
        print(f"⚠️  Could not save sample output: {e}")


async def generate_sample_outputs():
    """Generate sample outputs for external AI agent consumption."""
    print("\n" + "="*60)
    print("Generating Sample Outputs for External AI Agents")
    print("="*60)
    
    integration = AIAgentIntegration()
    
    # Generate a comprehensive codebase analysis prompt
    print("\n📊 Generating codebase analysis sample...")
    codebase_prompt = await integration.generate_prompt("codebase_analysis")
    save_sample_prompt_output(codebase_prompt, "codebase_analysis")
    
    # Generate a task prioritization prompt
    print("\n📋 Generating task prioritization sample...")
    prioritization_prompt = await integration.generate_prompt("task_prioritization")
    save_sample_prompt_output(prioritization_prompt, "task_prioritization")
    
    # Generate a project insights prompt
    print("\n📈 Generating project insights sample...")
    insights_prompt = await integration.generate_prompt("project_insights")
    save_sample_prompt_output(insights_prompt, "project_insights")
    
    print("\n✅ Sample outputs generated successfully!")
    print("These JSON files can be consumed by your external AI agent using Claude/OpenAI.")


async def main():
    """Main test function."""
    print("TaskHero AI Integration Test Suite")
    print("="*60)
    print("This script demonstrates AI prompt generation for external AI agents.")
    print("No actual AI services are called - only prompt structures are generated.")
    
    try:
        # Test all prompt generation functions
        await test_available_prompt_types()
        await test_codebase_analysis_prompt()
        await test_task_prioritization_prompt()
        await test_code_correlation_prompt()
        await test_project_insights_prompt()
        await test_task_breakdown_prompt()
        await test_documentation_prompt()
        
        # Generate sample outputs
        await generate_sample_outputs()
        
        print("\n" + "="*60)
        print("🎉 All tests completed successfully!")
        print("="*60)
        print("\nNext Steps:")
        print("1. Review the generated sample outputs in the logs/ directory")
        print("2. Feed these prompts to your external AI agent (Claude/OpenAI)")
        print("3. Process the AI responses to enhance your task management")
        print("4. Integrate the insights back into TaskHero AI")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main()) 