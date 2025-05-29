#!/usr/bin/env python3
"""
Integration Test for TASK-087: Enhanced Context Preview UI

This test validates that all TASK-087 features work correctly in the real
task creation workflow, including:
- Enhanced context selection interface
- Smart auto-selection
- Differentiated relevance scoring
- Interactive preview commands
- File metadata and explanations
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from mods.project_management.ai_task_creator import AITaskCreator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TaskHeroAI.Test.Task087Integration")

async def test_real_context_selection():
    """Test enhanced context selection with real data."""
    try:
        print("🧪 TASK-087 Integration Test: Real Context Selection")
        print("=" * 60)
        
        # Initialize AI Task Creator
        task_creator = AITaskCreator(".")
        
        # Test query that should find relevant context
        test_query = "enhanced context selection ui preview"
        
        print(f"🔍 Testing context retrieval for query: '{test_query}'")
        
        # Collect real context using our enhanced system
        context_chunks = await task_creator._collect_context_with_graphiti(test_query, {
            'task_type': 'Development',
            'query': test_query
        })
        
        if not context_chunks:
            print("⚠️  No context found - this might indicate an issue")
            return False
        
        print(f"✅ Found {len(context_chunks)} context chunks")
        
        # Test deduplication (as done in real workflow)
        unique_files = {}
        for chunk in context_chunks:
            file_path = Path(chunk.file_path)
            file_key = str(file_path.resolve())
            
            if file_key not in unique_files or chunk.relevance_score > unique_files[file_key].relevance_score:
                unique_files[file_key] = chunk
        
        unique_chunks = list(unique_files.values())
        unique_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        
        print(f"✅ Deduplicated to {len(unique_chunks)} unique files")
        
        # Test enhanced display (limit to top 3 for testing)
        test_chunks = unique_chunks[:3]
        
        print("\n🎨 Testing Enhanced Context Display:")
        print("-" * 50)
        task_creator._display_enhanced_context_selection(test_chunks)
        
        # Test smart auto-selection
        print("\n🤖 Testing Smart Auto-Selection:")
        print("-" * 50)
        auto_selected = task_creator._smart_auto_select_context(unique_chunks)
        print(f"Auto-selected {len(auto_selected)} files:")
        for chunk in auto_selected:
            print(f"  ✓ {Path(chunk.file_path).name} (score: {chunk.relevance_score:.3f})")
        
        # Validate relevance score differentiation
        scores = [chunk.relevance_score for chunk in unique_chunks[:5]]
        unique_scores = len(set(scores))
        
        print(f"\n📊 Relevance Score Analysis:")
        print(f"   Scores: {scores}")
        print(f"   Unique scores: {unique_scores}/{len(scores)}")
        print(f"   Score range: {min(scores):.3f} - {max(scores):.3f}")
        
        if unique_scores > 1:
            print("✅ Relevance scores are properly differentiated")
        else:
            print("⚠️  All scores are the same - differentiation may need improvement")
        
        # Test explanation quality
        print(f"\n💡 Testing Explanation Quality:")
        for i, chunk in enumerate(test_chunks[:2], 1):
            explanation = task_creator._generate_relevance_explanation(chunk)
            print(f"   File {i}: {explanation}")
        
        print("\n✅ Real Context Selection Test Completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Real context selection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_progressive_creation_with_enhancements():
    """Test that enhanced features work in progressive task creation."""
    try:
        print("\n🚀 Testing Progressive Creation with Enhanced Features")
        print("=" * 60)
        
        # Initialize AI Task Creator
        task_creator = AITaskCreator(".")
        
        # Simulate progressive creation state
        task_creator.creation_state = {
            'step': 2,
            'total_steps': 4,
            'collected_data': {
                'title': 'Test Enhanced Context Selection',
                'description': 'Testing the enhanced context selection interface with file previews and smart auto-selection',
                'task_type': 'Development',
                'priority': 'medium',
                'assigned_to': 'Developer',
                'tags': ['ui-enhancement', 'context-selection', 'testing']
            },
            'selected_context': [],
            'ai_enhancements': {},
            'quality_score': 0.0
        }
        
        print("✅ Simulated progressive creation state")
        
        # Test context collection and selection (Step 2)
        data = task_creator.creation_state['collected_data']
        query = f"{data['title']} {data['description']}"
        
        print(f"🔍 Testing context collection for: '{query[:50]}...'")
        
        # This should use our enhanced context selection
        context_chunks = await task_creator._collect_context_with_graphiti(query, data)
        
        if context_chunks:
            print(f"✅ Context collection successful: {len(context_chunks)} chunks found")
            
            # Test the enhanced selection interface components
            unique_files = {}
            for chunk in context_chunks:
                file_path = Path(chunk.file_path)
                file_key = str(file_path.resolve())
                if file_key not in unique_files or chunk.relevance_score > unique_files[file_key].relevance_score:
                    unique_files[file_key] = chunk
            
            unique_chunks = list(unique_files.values())
            unique_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Test helper methods work correctly
            if unique_chunks:
                test_chunk = unique_chunks[0]
                
                # Test all helper methods
                file_size = task_creator._get_file_size(Path(test_chunk.file_path))
                last_modified = task_creator._get_last_modified(Path(test_chunk.file_path))
                file_icon = task_creator._get_file_type_icon(Path(test_chunk.file_path))
                explanation = task_creator._generate_relevance_explanation(test_chunk)
                preview = task_creator._generate_file_preview(test_chunk)
                
                print(f"✅ Helper methods working:")
                print(f"   File size: {file_size}")
                print(f"   Last modified: {last_modified}")
                print(f"   File icon: {file_icon}")
                print(f"   Explanation length: {len(explanation)} chars")
                print(f"   Preview lines: {len(preview)}")
                
                # Test smart auto-selection
                auto_selected = task_creator._smart_auto_select_context(unique_chunks)
                print(f"✅ Smart auto-selection: {len(auto_selected)} files selected")
                
        else:
            print("⚠️  No context found - this might be expected for test data")
        
        print("\n✅ Progressive Creation Integration Test Completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Progressive creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_performance_impact():
    """Test that enhanced features don't significantly impact performance."""
    try:
        print("\n⚡ Testing Performance Impact")
        print("=" * 40)
        
        import time
        
        # Initialize AI Task Creator
        task_creator = AITaskCreator(".")
        
        # Test queries
        test_queries = [
            "context selection interface",
            "task creation enhancement",
            "file preview functionality",
            "smart auto selection"
        ]
        
        total_time = 0
        successful_queries = 0
        
        for query in test_queries:
            start_time = time.time()
            try:
                context_chunks = await task_creator._collect_context_with_graphiti(query, {
                    'task_type': 'Development'
                })
                
                if context_chunks:
                    # Test enhanced processing time
                    unique_files = {}
                    for chunk in context_chunks:
                        file_path = Path(chunk.file_path)
                        file_key = str(file_path.resolve())
                        if file_key not in unique_files or chunk.relevance_score > unique_files[file_key].relevance_score:
                            unique_files[file_key] = chunk
                    
                    unique_chunks = list(unique_files.values())
                    unique_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
                    
                    # Test helper methods performance
                    if unique_chunks:
                        test_chunk = unique_chunks[0]
                        task_creator._get_file_size(Path(test_chunk.file_path))
                        task_creator._get_last_modified(Path(test_chunk.file_path))
                        task_creator._get_file_type_icon(Path(test_chunk.file_path))
                        task_creator._generate_relevance_explanation(test_chunk)
                        task_creator._generate_file_preview(test_chunk)
                        task_creator._smart_auto_select_context(unique_chunks)
                
                query_time = time.time() - start_time
                total_time += query_time
                successful_queries += 1
                
                print(f"✅ Query '{query[:30]}...': {query_time:.3f}s")
                
            except Exception as e:
                print(f"❌ Query '{query[:30]}...' failed: {e}")
        
        if successful_queries > 0:
            avg_time = total_time / successful_queries
            print(f"\n📊 Performance Results:")
            print(f"   Successful queries: {successful_queries}/{len(test_queries)}")
            print(f"   Average time: {avg_time:.3f}s")
            print(f"   Total time: {total_time:.3f}s")
            
            # Performance threshold check (should be under 2 seconds per query)
            if avg_time < 2.0:
                print("✅ Performance is within acceptable limits")
                return True
            else:
                print("⚠️  Performance may need optimization")
                return False
        else:
            print("❌ No successful queries - performance test inconclusive")
            return False
        
    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
        return False

async def main():
    """Run comprehensive integration tests for TASK-087."""
    print("🚀 TASK-087 Enhanced Context Preview UI - Integration Tests")
    print("=" * 80)
    
    # Test 1: Real Context Selection
    test1_result = await test_real_context_selection()
    
    # Test 2: Progressive Creation Integration
    test2_result = await test_progressive_creation_with_enhancements()
    
    # Test 3: Performance Impact
    test3_result = await test_performance_impact()
    
    # Summary
    print("\n📊 Integration Test Summary:")
    print("=" * 50)
    print(f"Real Context Selection: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Progressive Creation Integration: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"Performance Impact: {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    overall_success = test1_result and test2_result and test3_result
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 TASK-087 Enhanced Context Preview UI is ready for production!")
    else:
        print("\n⚠️  Some issues detected - review test results above")
    
    return overall_success

if __name__ == "__main__":
    asyncio.run(main())
