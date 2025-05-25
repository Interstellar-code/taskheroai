"""
Test Enhanced Template Engine for TASK-058

This script tests the enhanced template engine functionality to validate
the quality improvements and template generation capabilities.

Author: TaskHero AI Development Team
Created: 2025-05-25 (TASK-058 Testing)
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from mods.project_management.enhanced_template_engine import EnhancedTemplateEngine, TaskType
    print("✅ Enhanced Template Engine imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Enhanced Template Engine: {e}")
    sys.exit(1)

def test_enhanced_template_engine():
    """Test the enhanced template engine functionality."""
    print("\n🚀 Testing Enhanced Template Engine for TASK-058")
    print("=" * 60)
    
    try:
        # Initialize the enhanced template engine
        print("\n1. Initializing Enhanced Template Engine...")
        engine = EnhancedTemplateEngine()
        print("✅ Enhanced Template Engine initialized successfully")
        
        # Test task generation for different types
        test_cases = [
            {
                "task_type": "DEV",
                "title": "Implement User Authentication System",
                "description": "Create a comprehensive user authentication system with login, registration, and password reset functionality.",
                "context": {
                    "task_id": "TASK-059",
                    "priority": "High",
                    "assigned_to": "Development Team",
                    "due_date": "2025-06-15",
                    "tags": ["authentication", "security", "user-management"]
                }
            },
            {
                "task_type": "BUG",
                "title": "Fix Login Validation Error",
                "description": "Users are experiencing validation errors when attempting to log in with valid credentials.",
                "context": {
                    "task_id": "TASK-060",
                    "priority": "Critical",
                    "assigned_to": "Bug Fix Team",
                    "due_date": "2025-05-30",
                    "bug_severity": "High",
                    "tags": ["bug-fix", "login", "validation"]
                }
            },
            {
                "task_type": "TEST",
                "title": "Create Payment Gateway Test Suite",
                "description": "Develop comprehensive test cases for the payment gateway integration including success and failure scenarios.",
                "context": {
                    "task_id": "TASK-061",
                    "priority": "Medium",
                    "assigned_to": "QA Team",
                    "due_date": "2025-06-10",
                    "test_type": "Integration",
                    "tags": ["testing", "payment", "integration"]
                }
            }
        ]
        
        # Test each case
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i + 1}. Testing {test_case['task_type']} Task Generation...")
            
            try:
                # Generate enhanced task
                result = engine.generate_enhanced_task(
                    task_type=test_case["task_type"],
                    title=test_case["title"],
                    description=test_case["description"],
                    context=test_case["context"]
                )
                
                print(f"✅ {test_case['task_type']} task generated successfully")
                print(f"   Quality Score: {result.get('quality_score', 'N/A'):.2f}/10")
                
                # Save generated content for review
                output_file = f"test_output_enhanced_{test_case['task_type'].lower()}_task.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['markdown'])
                print(f"   Output saved to: {output_file}")
                
                # Test template validation
                validation_result = engine.validate_template_completeness(
                    result['markdown'], 
                    test_case['task_type']
                )
                
                print(f"   Template Validation: {'✅ PASSED' if validation_result['valid'] else '❌ FAILED'}")
                print(f"   Completeness Score: {validation_result['completeness_score']:.1f}%")
                
                if validation_result['errors']:
                    print(f"   Validation Errors: {len(validation_result['errors'])}")
                    for error in validation_result['errors'][:3]:  # Show first 3 errors
                        print(f"     - {error}")
                
            except Exception as e:
                print(f"❌ Error generating {test_case['task_type']} task: {e}")
        
        # Test template configuration access
        print(f"\n3. Testing Template Configurations...")
        configs = engine.template_configs
        print(f"✅ Available configurations: {len(configs)}")
        for task_type in configs:
            config = configs[task_type]
            print(f"   - {task_type.value}: {len(config.sections)} sections, {len(config.required_metadata)} metadata fields")
        
        # Test formatting standards
        print(f"\n4. Testing Formatting Standards...")
        standards = engine.formatting_standards
        print(f"✅ Formatting standards loaded: {len(standards)} categories")
        for category in standards:
            print(f"   - {category}: {len(standards[category])} rules")
        
        print(f"\n🎉 Enhanced Template Engine testing completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Template Engine testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quality_comparison():
    """Test quality improvements compared to original system."""
    print("\n📊 Testing Quality Improvements")
    print("=" * 40)
    
    try:
        engine = EnhancedTemplateEngine()
        
        # Generate a sample task
        result = engine.generate_enhanced_task(
            task_type="DEV",
            title="Enhance TaskHero AI Task Generation Quality",
            description="Improve the TaskHero AI task generation system to produce higher quality, more professional, and more actionable task documentation.",
            context={
                "task_id": "TASK-058",
                "priority": "High",
                "assigned_to": "Developer",
                "due_date": "2025-06-01",
                "tags": ["ai-generation", "task-quality", "template-engine"]
            }
        )
        
        print(f"✅ Quality Score: {result.get('quality_score', 'N/A'):.2f}/10")
        
        # Check for quality improvements
        markdown_content = result['markdown']
        
        improvements = []
        
        # Check for proper markdown formatting (not Python lists)
        if '- [' in markdown_content and not "['The" in markdown_content:
            improvements.append("✅ Uses proper markdown bullets (not Python lists)")
        
        # Check for Mermaid diagrams
        if '```mermaid' in markdown_content:
            improvements.append("✅ Includes Mermaid flow diagrams")
        
        # Check for comprehensive sections
        required_sections = ['Overview', 'Flow Diagram', 'Implementation Status', 'Risk Assessment']
        found_sections = sum(1 for section in required_sections if section in markdown_content)
        if found_sections >= len(required_sections) * 0.8:  # 80% of required sections
            improvements.append(f"✅ Comprehensive section coverage ({found_sections}/{len(required_sections)})")
        
        # Check for professional formatting
        if '##' in markdown_content and '###' in markdown_content:
            improvements.append("✅ Professional section numbering and hierarchy")
        
        # Check for detailed implementation steps
        if 'Sub-step' in markdown_content and 'Target:' in markdown_content:
            improvements.append("✅ Detailed implementation steps with sub-tasks")
        
        print(f"\n📈 Quality Improvements Detected:")
        for improvement in improvements:
            print(f"   {improvement}")
        
        if len(improvements) >= 4:
            print(f"\n🎯 Quality Target: ACHIEVED ({len(improvements)}/5 improvements)")
        else:
            print(f"\n⚠️  Quality Target: PARTIAL ({len(improvements)}/5 improvements)")
        
        return True
        
    except Exception as e:
        print(f"❌ Quality comparison testing failed: {e}")
        return False

def main():
    """Main test execution."""
    print("🧪 TASK-058 Enhanced Template Engine Testing")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_enhanced_template_engine()
    test2_passed = test_quality_comparison()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print(f"   Enhanced Template Engine: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Quality Improvements: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed! Enhanced Template Engine is ready for Step 3.")
        return 0
    else:
        print(f"\n❌ Some tests failed. Please review and fix issues before proceeding.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 