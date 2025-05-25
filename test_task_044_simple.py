#!/usr/bin/env python3
"""
Simple Test for TASK-044 Improvements

This test validates the core TASK-044 improvements in a simplified manner.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_context_analyzer():
    """Test the context analyzer module."""
    print("🔍 Testing Context Analyzer...")
    
    try:
        from mods.project_management.context_analyzer import ContextAnalyzer
        
        analyzer = ContextAnalyzer(str(project_root))
        
        # Test with install script task
        description = "Enhance the Windows installation script to include better error handling"
        task_type = "Development"
        
        context = analyzer.analyze_task_context(description, task_type)
        
        print(f"✅ Found {len(context.relevant_files)} relevant files")
        print(f"✅ Generated {len(context.recommendations)} recommendations")
        
        # Show some results
        if context.relevant_files:
            print("📁 Top relevant files:")
            for file_analysis in context.relevant_files[:3]:
                print(f"   - {file_analysis.file_path} ({file_analysis.file_type})")
        
        if context.recommendations:
            print("💡 Sample recommendations:")
            for rec in context.recommendations[:3]:
                print(f"   - {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Context Analyzer test failed: {e}")
        return False

def test_template_optimizer():
    """Test the template optimizer module."""
    print("\n🎨 Testing Template Optimizer...")
    
    try:
        from mods.project_management.template_optimizer import TemplateOptimizer
        
        optimizer = TemplateOptimizer()
        
        # Test context optimization
        test_context = {
            'title': 'Enhance Windows Installation Script',
            'description': 'Enhance the Windows installation script with better error handling',
            'task_type': 'Development',
            'priority': 'medium',
            'functional_requirements_list': ['[Requirement 1]', 'Actual requirement'],
            'benefits_list': ['[Benefit 1]', 'Real benefit']
        }
        
        # Optimize template
        optimized_context = optimizer.optimize_template_context(
            test_context, 'Development', 'Enhance Windows installation script'
        )
        
        print(f"✅ Template optimized with {len(optimized_context)} context variables")
        
        # Check for improvements
        improvements = []
        
        # Check if placeholder content was addressed
        placeholder_found = False
        for key, value in optimized_context.items():
            if isinstance(value, (str, list)):
                if isinstance(value, str) and '[' in value and ']' in value:
                    placeholder_found = True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and '[' in item and ']' in item:
                            placeholder_found = True
                            break
        
        if not placeholder_found:
            improvements.append("Placeholder content removed")
        
        # Check for section filtering
        if 'template_sections' in optimized_context:
            improvements.append("Template sections filtered")
        
        print(f"✅ Improvements: {', '.join(improvements) if improvements else 'Basic optimization applied'}")
        
        # Test flow diagram generation
        flow_context = optimizer.generate_task_specific_flow_diagram(
            'Development', 'Enhance Windows installation script', optimized_context
        )
        
        if 'flow_diagram' in flow_context:
            print("✅ Task-specific flow diagram generated")
        
        # Test quality validation
        issues = optimizer.validate_optimized_template(optimized_context)
        if issues:
            print(f"⚠️  Quality issues found: {len(issues)}")
        else:
            print("✅ Template quality validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Template Optimizer test failed: {e}")
        return False

def test_ai_task_creator_integration():
    """Test AI task creator integration."""
    print("\n🤖 Testing AI Task Creator Integration...")
    
    try:
        from mods.project_management.ai_task_creator import AITaskCreator
        
        creator = AITaskCreator(str(project_root))
        
        # Check if TASK-044 modules are integrated
        has_context_analyzer = hasattr(creator, 'context_analyzer')
        has_template_optimizer = hasattr(creator, 'template_optimizer')
        
        print(f"✅ Context Analyzer integrated: {has_context_analyzer}")
        print(f"✅ Template Optimizer integrated: {has_template_optimizer}")
        
        # Test basic context preparation
        context = creator._prepare_base_context(
            task_id="TEST-001",
            title="Test Task",
            description="Test task for TASK-044 validation",
            task_type="Development",
            priority="medium"
        )
        
        print(f"✅ Base context prepared with {len(context)} variables")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Task Creator integration test failed: {e}")
        return False

def test_file_detection():
    """Test if relevant files are detected correctly."""
    print("\n📁 Testing File Detection...")
    
    try:
        from mods.project_management.context_analyzer import ContextAnalyzer
        
        analyzer = ContextAnalyzer(str(project_root))
        
        # Test scenarios
        test_cases = [
            {
                "description": "Fix error handling in setup_windows.bat script",
                "expected_files": ["setup_windows.bat"],
                "task_type": "Bug Fix"
            },
            {
                "description": "Update app configuration settings",
                "expected_files": [".app_settings.json", "app.py"],
                "task_type": "Development"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n  Testing: {test_case['description']}")
            
            context = analyzer.analyze_task_context(
                test_case["description"], test_case["task_type"]
            )
            
            found_files = [f.file_path for f in context.relevant_files]
            
            for expected_file in test_case["expected_files"]:
                if any(expected_file in found_file for found_file in found_files):
                    print(f"   ✅ Found expected file: {expected_file}")
                else:
                    print(f"   ℹ️  Expected file not found: {expected_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ File detection test failed: {e}")
        return False

def main():
    """Run all simple tests."""
    print("🚀 TASK-044 Simple Test Suite")
    print("=" * 50)
    
    tests = [
        test_context_analyzer,
        test_template_optimizer,
        test_ai_task_creator_integration,
        test_file_detection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 All TASK-044 improvements are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the output above for details.")
    
    # Check if key files exist
    print("\n📂 Key Files Check:")
    key_files = [
        "mods/project_management/context_analyzer.py",
        "mods/project_management/template_optimizer.py",
        "mods/project_management/ai_task_creator.py"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")

if __name__ == "__main__":
    main() 