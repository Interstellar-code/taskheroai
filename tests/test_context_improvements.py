#!/usr/bin/env python3
"""
Test script to validate the enhanced context selection improvements.

This script tests the new balanced scoring algorithm and diversity selection
to ensure technical queries get better code file representation.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mods.project_management.semantic_search import SemanticSearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_query_intent_classification():
    """Test the query intent classification functionality."""
    print("\n" + "="*60)
    print("TESTING QUERY INTENT CLASSIFICATION")
    print("="*60)
    
    search_engine = SemanticSearchEngine(str(project_root))
    
    test_queries = [
        ("enhance install script", "technical"),
        ("implement new feature", "technical"),
        ("fix bug in authentication", "technical"),
        ("document API endpoints", "documentation"),
        ("create user guide", "documentation"),
        ("task management workflow", "task_management"),
        ("project planning template", "task_management"),
        ("setup development environment", "mixed"),
        ("general project overview", "general")
    ]
    
    for query, expected_intent in test_queries:
        actual_intent = search_engine._classify_query_intent(query.lower())
        status = "✅ PASS" if actual_intent == expected_intent else "❌ FAIL"
        print(f"{status} Query: '{query}' -> Expected: {expected_intent}, Got: {actual_intent}")

def test_file_type_detection():
    """Test the enhanced file type detection."""
    print("\n" + "="*60)
    print("TESTING FILE TYPE DETECTION")
    print("="*60)
    
    search_engine = SemanticSearchEngine(str(project_root))
    
    test_files = [
        ("setup.py", "python"),
        ("install.bat", "script"),
        ("config.json", "config"),
        ("requirements.txt", "dependency"),
        ("task_example.md", "task"),
        ("README.md", "documentation"),
        ("test_module.py", "test"),
        ("deploy.sh", "script"),
        ("package.json", "dependency"),
        ("main.js", "javascript")
    ]
    
    for filename, expected_type in test_files:
        actual_type = search_engine._determine_file_type(filename)
        status = "✅ PASS" if actual_type == expected_type else "❌ FAIL"
        print(f"{status} File: '{filename}' -> Expected: {expected_type}, Got: {actual_type}")

def test_context_search():
    """Test the context search with different query types."""
    print("\n" + "="*60)
    print("TESTING CONTEXT SEARCH RESULTS")
    print("="*60)
    
    search_engine = SemanticSearchEngine(str(project_root))
    
    test_queries = [
        "enhance install script",
        "implement authentication system", 
        "create task management documentation",
        "setup development environment",
        "fix configuration issues"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            result = search_engine.search(query, max_results=8)
            
            if result.chunks:
                print(f"   Found {len(result.chunks)} results in {result.search_time:.3f}s")
                
                # Analyze file type distribution
                file_types = {}
                for chunk in result.chunks:
                    file_types[chunk.file_type] = file_types.get(chunk.file_type, 0) + 1
                
                print(f"   File type distribution: {file_types}")
                
                # Show top 3 results
                print("   Top results:")
                for i, chunk in enumerate(result.chunks[:3]):
                    print(f"     {i+1}. {chunk.file_name} ({chunk.file_type}) - Score: {chunk.relevance_score:.3f}")
            else:
                print("   No results found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_diversity_selection():
    """Test the diversity selection algorithm."""
    print("\n" + "="*60)
    print("TESTING DIVERSITY SELECTION")
    print("="*60)
    
    # This test would require actual embedding data to be meaningful
    # For now, we'll just test that the method exists and can be called
    search_engine = SemanticSearchEngine(str(project_root))
    
    # Create mock chunks for testing
    from mods.project_management.semantic_search import ContextChunk
    
    mock_chunks = [
        ContextChunk("code content", "test.py", "function", 1, 10, 0.9, "test.py", "python"),
        ContextChunk("task content", "task.md", "text", 1, 5, 0.8, "task.md", "task"),
        ContextChunk("config content", "config.json", "config", 1, 3, 0.7, "config.json", "config"),
        ContextChunk("doc content", "README.md", "text", 1, 20, 0.6, "README.md", "documentation"),
    ]
    
    # Set relevance scores
    for i, chunk in enumerate(mock_chunks):
        chunk.relevance_score = 0.9 - (i * 0.1)
    
    try:
        selected = search_engine._select_diverse_chunks(mock_chunks, 3, "enhance install script")
        print(f"✅ Diversity selection works - selected {len(selected)} chunks")
        
        file_types = [chunk.file_type for chunk in selected]
        print(f"   Selected file types: {file_types}")
        
    except Exception as e:
        print(f"❌ Diversity selection failed: {e}")

def main():
    """Run all tests."""
    print("🚀 STARTING CONTEXT SELECTION IMPROVEMENT TESTS")
    print("Testing Phase 1 improvements: Enhanced Relevance Scoring Algorithm")
    
    try:
        test_query_intent_classification()
        test_file_type_detection()
        test_diversity_selection()
        test_context_search()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\nNext steps:")
        print("1. Review the file type distributions in search results")
        print("2. Verify that technical queries now include more code files")
        print("3. Check that task management queries are more balanced")
        print("4. Test with actual task generation to see improvements")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
