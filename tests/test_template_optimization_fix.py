#!/usr/bin/env python3
"""
Test Script for Template Optimization Fix
Tests that placeholder content and default sections are properly removed.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_template_optimization_fix():
    """Test the template optimization fix."""
    print("🔧 TEMPLATE OPTIMIZATION FIX TEST")
    print("=" * 60)
    
    try:
        from mods.project_management.ai_task_creator import AITaskCreator
        
        # Test 1: Create a task without AI enhancement to test template optimization
        print("\n📊 Test 1: Template Optimization without AI Enhancement")
        print("-" * 50)
        
        ai_creator = AITaskCreator()
        
        success, task_id, file_path = await ai_creator.create_enhanced_task(
            title="Test Template Optimization",
            description="This is a test task to verify that placeholder content is removed",
            task_type="Development",
            priority="medium",
            tags=["test", "template", "optimization"],
            use_ai_enhancement=False  # This should still apply template optimization
        )
        
        if success and file_path and Path(file_path).exists():
            print(f"✅ Task created successfully: {task_id}")
            print(f"✅ File saved at: {file_path}")
            
            # Read and analyze the generated content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for problematic placeholder content
            placeholder_issues = []
            
            # Check for default technical considerations
            if "Consider performance, security, maintainability, and scalability requirements." in content:
                placeholder_issues.append("Default technical considerations found")
            
            # Check for default flow diagram
            if "User initiates action" in content and "System validates input" in content:
                placeholder_issues.append("Generic flow diagram found")
            
            # Check for default implementation analysis
            if "Current implementation will be analyzed during planning phase" in content:
                placeholder_issues.append("Default implementation analysis found")
            
            # Check for default UI design content
            if "UI design considerations will be defined during implementation phase" in content:
                placeholder_issues.append("Default UI design content found")
            
            # Check for default state management
            if "Define how application state will be managed and synchronized" in content:
                placeholder_issues.append("Default state management content found")
            
            # Check for naming convention section (should be hidden)
            if "Task Naming Convention" in content:
                placeholder_issues.append("Naming convention section visible (should be hidden)")
            
            print(f"\n📋 Placeholder Content Analysis:")
            if placeholder_issues:
                print("❌ Issues found:")
                for issue in placeholder_issues:
                    print(f"   - {issue}")
                test1_passed = False
            else:
                print("✅ No placeholder content found - optimization working!")
                test1_passed = True
            
            # Show a sample of the content
            print(f"\n📄 Content Sample (first 500 chars):")
            print("-" * 40)
            print(content[:500] + "...")
            print("-" * 40)
            
        else:
            print(f"❌ Task creation failed")
            test1_passed = False
        
        # Test 2: Create a task with AI enhancement to ensure it still works
        print(f"\n🤖 Test 2: Template Optimization with AI Enhancement")
        print("-" * 50)
        
        success2, task_id2, file_path2 = await ai_creator.create_enhanced_task(
            title="Test AI Enhanced Template Optimization",
            description="Enhance the Windows installation script to make it more interactive",
            task_type="Development",
            priority="medium",
            tags=["ai", "enhancement", "test"],
            use_ai_enhancement=True
        )
        
        if success2 and file_path2 and Path(file_path2).exists():
            print(f"✅ AI-enhanced task created: {task_id2}")
            
            with open(file_path2, 'r', encoding='utf-8') as f:
                ai_content = f.read()
            
            # Check that AI enhancement worked but placeholders are still removed
            ai_placeholder_issues = []
            
            if "Consider performance, security, maintainability, and scalability requirements." in ai_content:
                ai_placeholder_issues.append("Default technical considerations found in AI-enhanced task")
            
            if "User initiates action" in ai_content and "System validates input" in ai_content:
                ai_placeholder_issues.append("Generic flow diagram found in AI-enhanced task")
            
            print(f"\n📋 AI-Enhanced Task Analysis:")
            if ai_placeholder_issues:
                print("❌ Issues found:")
                for issue in ai_placeholder_issues:
                    print(f"   - {issue}")
                test2_passed = False
            else:
                print("✅ AI-enhanced task properly optimized!")
                test2_passed = True
            
        else:
            print(f"❌ AI-enhanced task creation failed")
            test2_passed = False
        
        # Summary
        print(f"\n📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        tests = [
            ("Template Optimization (No AI)", test1_passed),
            ("Template Optimization (With AI)", test2_passed)
        ]
        
        passed_tests = sum(1 for _, passed in tests if passed)
        total_tests = len(tests)
        
        for i, (test_name, passed) in enumerate(tests, 1):
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{i}. {test_name}: {status}")
        
        overall_success = passed_tests == total_tests
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
        
        if overall_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Template optimization working correctly")
            print("✅ Placeholder content properly removed")
            print("✅ Default sections filtered out")
        else:
            print("\n⚠️  SOME TESTS FAILED!")
            print("❌ Template optimization needs further refinement")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Template optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the template optimization fix test."""
    print("🚀 Template Optimization Fix Test")
    print("Testing that placeholder content and default sections are properly removed...")
    
    success = await test_template_optimization_fix()
    
    if success:
        print("\n✅ TEMPLATE OPTIMIZATION: Working correctly!")
    else:
        print("\n❌ TEMPLATE OPTIMIZATION: Needs further fixes!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 