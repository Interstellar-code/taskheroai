#!/usr/bin/env python3
"""
Test Script for Naming Convention Section Removal
Verifies that the naming convention section is not included in generated tasks.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_naming_convention_removal():
    """Test that naming convention section is removed from generated tasks."""
    print("\n🔧 Testing Naming Convention Section Removal...")
    print("=" * 60)
    
    try:
        from mods.project_management.ai_task_creator import AITaskCreator
        
        ai_creator = AITaskCreator()
        
        # Create a test task
        print("📝 Creating test task...")
        
        success, task_id, file_path = await ai_creator.create_enhanced_task(
            title="Test Naming Convention Removal",
            description="Test task to verify naming convention section is not included in output",
            task_type="Development",
            priority="medium",
            tags=["test", "naming-convention"],
            use_ai_enhancement=True
        )
        
        if success and file_path and Path(file_path).exists():
            print(f"✅ Task created: {task_id}")
            print(f"   File: {file_path}")
            
            # Read the generated content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for naming convention section
            naming_convention_present = "## Task Naming Convention" in content
            metadata_legend_present = "### Metadata Legend (for reference only)" in content
            
            print(f"\n📊 Analysis Results:")
            print(f"   Naming Convention section present: {'❌ YES' if naming_convention_present else '✅ NO'}")
            print(f"   Metadata Legend section present: {'❌ YES' if metadata_legend_present else '✅ NO'}")
            
            if not naming_convention_present and not metadata_legend_present:
                print(f"\n🎉 SUCCESS: Naming convention and metadata legend sections properly removed!")
                return True
            else:
                print(f"\n⚠️  ISSUE: Naming convention or metadata legend sections still present")
                
                # Show the problematic content
                if naming_convention_present:
                    print("\nNaming Convention section found:")
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "## Task Naming Convention" in line:
                            for j in range(max(0, i-2), min(len(lines), i+10)):
                                print(f"  {j+1}: {lines[j]}")
                            break
                
                return False
        else:
            print(f"❌ Task creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_optimizer_directly():
    """Test the template optimizer directly to verify flags are set correctly."""
    print("\n🎨 Testing Template Optimizer Directly...")
    print("=" * 60)
    
    try:
        from mods.project_management.template_optimizer import TemplateOptimizer
        
        optimizer = TemplateOptimizer()
        
        # Test context
        test_context = {
            'title': 'Test Task',
            'description': 'Test task for naming convention removal',
            'task_type': 'Development',
            'priority': 'medium'
        }
        
        # Optimize the context
        optimized = optimizer.optimize_template_context(
            test_context, 'Development', 'Test task for naming convention removal'
        )
        
        # Check the flags
        naming_flag = optimized.get('show_naming_convention', True)
        legend_flag = optimized.get('show_metadata_legend', True)
        
        print(f"📊 Template Optimizer Results:")
        print(f"   show_naming_convention: {naming_flag} ({'✅ CORRECT' if not naming_flag else '❌ INCORRECT'})")
        print(f"   show_metadata_legend: {legend_flag} ({'✅ CORRECT' if not legend_flag else '❌ INCORRECT'})")
        
        return not naming_flag and not legend_flag
        
    except Exception as e:
        print(f"❌ Template optimizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the naming convention removal tests."""
    print("🚀 Naming Convention Section Removal Test")
    print("=" * 60)
    print("Testing that naming convention sections are removed from generated tasks...")
    
    # Test 1: Template Optimizer
    optimizer_result = test_template_optimizer_directly()
    
    # Test 2: Full Task Creation
    task_creation_result = await test_naming_convention_removal()
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 60)
    print(f"1. Template Optimizer: {'✅ PASSED' if optimizer_result else '❌ FAILED'}")
    print(f"2. Task Creation: {'✅ PASSED' if task_creation_result else '❌ FAILED'}")
    
    overall_success = optimizer_result and task_creation_result
    
    if overall_success:
        print(f"\n🎉 All tests passed! Naming convention sections are properly removed.")
    else:
        print(f"\n⚠️  Some tests failed. Naming convention sections may still be present.")
    
    return overall_success

if __name__ == "__main__":
    asyncio.run(main()) 