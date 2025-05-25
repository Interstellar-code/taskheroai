#!/usr/bin/env python3
"""
Test Script for Enhanced Context Analysis System
Tests the improved AI task creation with proper separation of user input and context.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_enhanced_context_analysis():
    """Test the enhanced context analysis system."""
    print("🔍 ENHANCED CONTEXT ANALYSIS TEST")
    print("=" * 60)
    
    try:
        from mods.project_management.context_analyzer_enhanced import EnhancedContextAnalyzer
        from mods.project_management.ai_task_creator import AITaskCreator
        
        # Test 1: Enhanced Context Analyzer Direct Test
        print("\n📊 Test 1: Enhanced Context Analyzer")
        print("-" * 40)
        
        analyzer = EnhancedContextAnalyzer(str(project_root))
        
        # Test with setup_windows.bat specific task
        user_description = "Enhance the Windows installation script to make it more interactive and user-friendly"
        task_type = "Development"
        
        enhanced_context = analyzer.analyze_task_context_enhanced(
            user_description, task_type, specific_files=["setup_windows.bat"]
        )
        
        print(f"✅ User description preserved: {enhanced_context.user_description}")
        print(f"✅ User requirements extracted: {len(enhanced_context.user_requirements)} items")
        print(f"✅ Relevant files analyzed: {len(enhanced_context.relevant_files)} files")
        print(f"✅ Primary file identified: {enhanced_context.primary_file_analysis.file_path if enhanced_context.primary_file_analysis else 'None'}")
        print(f"✅ Context confidence: {enhanced_context.context_confidence:.2f}")
        print(f"✅ Analysis completeness: {enhanced_context.analysis_completeness:.2f}")
        
        # Show primary file analysis details
        if enhanced_context.primary_file_analysis:
            primary = enhanced_context.primary_file_analysis
            print(f"\n📄 Primary File Analysis:")
            print(f"   File: {primary.file_path}")
            print(f"   Language: {primary.language}")
            print(f"   Functions: {len(primary.functions)} found")
            print(f"   Key features: {', '.join(primary.key_features[:3])}")
            print(f"   Complexity: {primary.complexity_score:.2f}")
            print(f"   Documentation: {primary.documentation_quality}")
        
        # Show contextual recommendations
        if enhanced_context.contextual_recommendations:
            print(f"\n💡 Contextual Recommendations:")
            for i, rec in enumerate(enhanced_context.contextual_recommendations[:3], 1):
                print(f"   {i}. {rec.description}")
        
        test1_passed = (
            enhanced_context.user_description == user_description and
            enhanced_context.primary_file_analysis is not None and
            enhanced_context.context_confidence > 0.5
        )
        
        # Test 2: AI Task Creator with Enhanced Context
        print(f"\n🤖 Test 2: AI Task Creator with Enhanced Context")
        print("-" * 50)
        
        ai_creator = AITaskCreator()
        
        success, task_id, file_path = await ai_creator.create_enhanced_task(
            title="Enhance Windows Installation Script for Better User Experience",
            description=user_description,
            task_type="Development",
            priority="medium",
            tags=["setup", "windows", "user-experience"],
            use_ai_enhancement=True
        )
        
        if success and file_path and Path(file_path).exists():
            print(f"✅ Task created successfully: {task_id}")
            print(f"✅ File saved at: {file_path}")
            
            # Read and analyze the generated content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if user description is preserved (not contaminated with context)
            user_desc_preserved = user_description in content
            context_not_merged = "setup_windows.bat" in content  # Should reference file but not merge content
            
            print(f"✅ User description preserved: {user_desc_preserved}")
            print(f"✅ Context properly referenced: {context_not_merged}")
            
            # Check for specific improvements
            has_specific_analysis = "Virtual environment management" in content or "Error handling" in content
            has_implementation_details = "batch" in content.lower() or "windows" in content.lower()
            
            print(f"✅ Specific file analysis included: {has_specific_analysis}")
            print(f"✅ Implementation details present: {has_implementation_details}")
            
            test2_passed = success and user_desc_preserved and has_specific_analysis
        else:
            print(f"❌ Task creation failed")
            test2_passed = False
        
        # Test 3: Verify No Context Contamination
        print(f"\n🧹 Test 3: Context Contamination Check")
        print("-" * 40)
        
        # Create a simple task to ensure no contamination
        simple_description = "Add a new feature to improve user experience"
        
        success_simple, task_id_simple, file_path_simple = await ai_creator.create_enhanced_task(
            title="Simple Feature Addition",
            description=simple_description,
            task_type="Development",
            priority="low",
            use_ai_enhancement=True
        )
        
        if success_simple and file_path_simple and Path(file_path_simple).exists():
            with open(file_path_simple, 'r', encoding='utf-8') as f:
                simple_content = f.read()
            
            # Check that the simple description wasn't contaminated with unrelated context
            no_contamination = simple_description in simple_content
            no_unrelated_files = "setup_windows.bat" not in simple_content
            
            print(f"✅ Simple description preserved: {no_contamination}")
            print(f"✅ No unrelated file contamination: {no_unrelated_files}")
            
            test3_passed = no_contamination and no_unrelated_files
        else:
            print(f"❌ Simple task creation failed")
            test3_passed = False
        
        # Summary
        print(f"\n📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        tests = [
            ("Enhanced Context Analyzer", test1_passed),
            ("AI Task Creator with Context", test2_passed),
            ("Context Contamination Check", test3_passed)
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
            print("✅ Enhanced context analysis working correctly")
            print("✅ User input properly separated from context")
            print("✅ Specific file analysis integrated appropriately")
            print("✅ No context contamination detected")
        else:
            print("\n⚠️  SOME TESTS FAILED!")
            print("❌ Enhanced context analysis needs refinement")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Enhanced context analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the enhanced context analysis test."""
    print("🚀 Enhanced Context Analysis System Test")
    print("Testing improved AI task creation with proper context separation...")
    
    success = await test_enhanced_context_analysis()
    
    if success:
        print("\n✅ ENHANCED CONTEXT ANALYSIS: Working correctly!")
    else:
        print("\n❌ ENHANCED CONTEXT ANALYSIS: Needs improvement!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 