#!/usr/bin/env python3
"""
Final Verification Test for Naming Convention Section Removal
Comprehensive test to ensure the fix works across all code paths.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_comprehensive_naming_convention_fix():
    """Comprehensive test for naming convention section removal."""
    print("🔍 COMPREHENSIVE NAMING CONVENTION FIX VERIFICATION")
    print("=" * 60)
    
    try:
        from mods.project_management.ai_task_creator import AITaskCreator
        from mods.project_management.template_optimizer import TemplateOptimizer
        
        # Test 1: Template Optimizer Direct Test
        print("\n📊 Test 1: Template Optimizer Direct Test")
        print("-" * 45)
        
        optimizer = TemplateOptimizer()
        test_context = {
            'title': 'Test Task',
            'description': 'Test task for comprehensive verification',
            'task_type': 'Development'
        }
        
        optimized = optimizer.optimize_template_context(
            test_context, 'Development', 'Test task for comprehensive verification'
        )
        
        naming_flag = optimized.get('show_naming_convention', True)
        legend_flag = optimized.get('show_metadata_legend', True)
        
        print(f"   show_naming_convention: {naming_flag} ({'✅ CORRECT' if not naming_flag else '❌ INCORRECT'})")
        print(f"   show_metadata_legend: {legend_flag} ({'✅ CORRECT' if not legend_flag else '❌ INCORRECT'})")
        
        test1_passed = not naming_flag and not legend_flag
        
        # Test 2: AI Task Creator Base Context Test
        print("\n🤖 Test 2: AI Task Creator Base Context Test")
        print("-" * 45)
        
        ai_creator = AITaskCreator()
        base_context = ai_creator._prepare_base_context(
            task_id='TEST-001',
            title='Test Base Context',
            description='Testing base context flags',
            task_type='Development'
        )
        
        base_naming_flag = base_context.get('show_naming_convention', True)
        base_legend_flag = base_context.get('show_metadata_legend', True)
        
        print(f"   Base context show_naming_convention: {base_naming_flag} ({'✅ CORRECT' if not base_naming_flag else '❌ INCORRECT'})")
        print(f"   Base context show_metadata_legend: {base_legend_flag} ({'✅ CORRECT' if not base_legend_flag else '❌ INCORRECT'})")
        
        test2_passed = not base_naming_flag and not base_legend_flag
        
        # Test 3: Full Task Creation Test
        print("\n📝 Test 3: Full Task Creation Test")
        print("-" * 35)
        
        success, task_id, file_path = await ai_creator.create_enhanced_task(
            title="Final Verification Test Task",
            description="This task is created to verify that the naming convention section is completely removed from all generated tasks",
            task_type="Development",
            priority="medium",
            tags=["verification", "test", "naming-convention"],
            use_ai_enhancement=True
        )
        
        if success and file_path and Path(file_path).exists():
            print(f"   ✅ Task created: {task_id}")
            
            # Read and verify content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            naming_convention_present = "## Task Naming Convention" in content
            metadata_legend_present = "### Metadata Legend (for reference only)" in content
            
            print(f"   Naming Convention section: {'❌ FOUND' if naming_convention_present else '✅ NOT FOUND'}")
            print(f"   Metadata Legend section: {'❌ FOUND' if metadata_legend_present else '✅ NOT FOUND'}")
            
            test3_passed = not naming_convention_present and not metadata_legend_present
        else:
            print(f"   ❌ Task creation failed")
            test3_passed = False
        
        # Test 4: Verify Existing Tasks Are Clean
        print("\n🧹 Test 4: Verify Existing Tasks Are Clean")
        print("-" * 40)
        
        task_dirs = [
            "mods/project_management/planning/todo",
            "mods/project_management/planning/inprogress",
            "mods/project_management/planning/testing",
            "mods/project_management/planning/done"
        ]
        
        problematic_tasks = []
        total_tasks = 0
        
        for task_dir in task_dirs:
            task_path = Path(task_dir)
            if task_path.exists():
                for task_file in task_path.glob("TASK-*.md"):
                    total_tasks += 1
                    try:
                        with open(task_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if "## Task Naming Convention" in content:
                            problematic_tasks.append(task_file.name)
                    except Exception as e:
                        print(f"   ⚠️  Error reading {task_file.name}: {e}")
        
        print(f"   Total tasks checked: {total_tasks}")
        print(f"   Problematic tasks found: {len(problematic_tasks)}")
        
        if problematic_tasks:
            print(f"   ❌ Tasks still containing naming convention:")
            for task in problematic_tasks:
                print(f"      - {task}")
        else:
            print(f"   ✅ All existing tasks are clean")
        
        test4_passed = len(problematic_tasks) == 0
        
        # Summary
        print(f"\n📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        tests = [
            ("Template Optimizer", test1_passed),
            ("AI Task Creator Base Context", test2_passed),
            ("Full Task Creation", test3_passed),
            ("Existing Tasks Verification", test4_passed)
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
            print("✅ Naming convention sections are completely removed")
            print("✅ Fix works across all code paths")
            print("✅ Existing tasks are clean")
            print("✅ New tasks are generated without naming convention sections")
        else:
            print("\n⚠️  SOME TESTS FAILED!")
            print("❌ Additional fixes may be needed")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the comprehensive verification test."""
    print("🚀 Final Naming Convention Fix Verification")
    print("Testing all code paths to ensure complete fix...")
    
    success = await test_comprehensive_naming_convention_fix()
    
    if success:
        print("\n✅ VERIFICATION COMPLETE: All naming convention sections removed!")
    else:
        print("\n❌ VERIFICATION FAILED: Additional work needed!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 