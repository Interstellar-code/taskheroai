#!/usr/bin/env python3
"""
Test script for Enhanced Context Preview UI (TASK-087)

This script tests the new enhanced context selection interface with:
- File previews and metadata
- Smart auto-selection
- Relevance explanations
- Interactive preview commands
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from mods.project_management.ai_task_creator import AITaskCreator
from mods.project_management.semantic_search import ContextChunk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TaskHeroAI.Test.EnhancedContextUI")

async def test_enhanced_context_ui():
    """Test the enhanced context selection UI."""
    try:
        print("🧪 Testing Enhanced Context Preview UI (TASK-087)")
        print("=" * 60)
        
        # Initialize AI Task Creator
        task_creator = AITaskCreator(".")
        
        # Create mock context chunks with varied relevance scores
        mock_chunks = [
            ContextChunk(
                text="class AITaskCreator:\n    def __init__(self, project_root):\n        self.project_root = project_root\n        # Enhanced task creation with AI",
                file_path="mods/project_management/ai_task_creator.py",
                chunk_type="code",
                start_line=1,
                end_line=10,
                confidence=0.9,
                relevance_score=0.856,
                file_name="ai_task_creator.py",
                file_type="python"
            ),
            ContextChunk(
                text="def _display_enhanced_context_selection(self, context_chunks):\n    \"\"\"Display enhanced context selection interface.\"\"\"\n    print(\"Enhanced Context Selection\")",
                file_path="mods/project_management/ai_task_creator.py",
                chunk_type="code",
                start_line=631,
                end_line=640,
                confidence=0.95,
                relevance_score=0.923,
                file_name="ai_task_creator.py",
                file_type="python"
            ),
            ContextChunk(
                text="# Enhanced Context Preview UI for Task Creation\n\nThis task implements enhanced context selection with file previews, smart auto-selection, and relevance explanations.",
                file_path="theherotasks/todo/TASK-087-DEV-enhanced-context-preview-ui-for-task-creation.md",
                chunk_type="documentation",
                start_line=1,
                end_line=5,
                confidence=0.8,
                relevance_score=0.734,
                file_name="TASK-087-DEV-enhanced-context-preview-ui-for-task-creation.md",
                file_type="markdown"
            ),
            ContextChunk(
                text="class GraphitiContextRetriever:\n    def __init__(self, project_root):\n        self.project_root = Path(project_root)\n        # Enhanced context retrieval with relationship analysis",
                file_path="mods/project_management/graphiti_retriever.py",
                chunk_type="code",
                start_line=30,
                end_line=40,
                confidence=0.85,
                relevance_score=0.612,
                file_name="graphiti_retriever.py",
                file_type="python"
            ),
            ContextChunk(
                text="{\n  \"setup_completed\": {\n    \"installation\": true,\n    \"configuration\": true\n  },\n  \"codebase_path\": \"C:/laragon/www/subsheroloaded\"",
                file_path=".taskhero_setup.json",
                chunk_type="config",
                start_line=1,
                end_line=8,
                confidence=0.7,
                relevance_score=0.445,
                file_name=".taskhero_setup.json",
                file_type="json"
            )
        ]
        
        print("✅ Created mock context chunks with varied relevance scores")
        print(f"   Scores: {[chunk.relevance_score for chunk in mock_chunks]}")
        
        # Test enhanced context display
        print("\n🎨 Testing Enhanced Context Display Interface:")
        print("-" * 50)
        task_creator._display_enhanced_context_selection(mock_chunks)
        
        # Test smart auto-selection
        print("\n🤖 Testing Smart Auto-Selection:")
        print("-" * 50)
        auto_selected = task_creator._smart_auto_select_context(mock_chunks)
        print(f"Auto-selected {len(auto_selected)} files:")
        for chunk in auto_selected:
            print(f"  ✓ {Path(chunk.file_path).name} (score: {chunk.relevance_score:.3f})")
        
        # Test file preview
        print("\n👀 Testing File Preview:")
        print("-" * 50)
        if mock_chunks:
            task_creator._show_file_preview(mock_chunks[0])
        
        # Test helper methods
        print("\n🔧 Testing Helper Methods:")
        print("-" * 50)
        
        test_chunk = mock_chunks[0]
        file_size = task_creator._get_file_size(Path(test_chunk.file_path))
        last_modified = task_creator._get_last_modified(Path(test_chunk.file_path))
        file_icon = task_creator._get_file_type_icon(Path(test_chunk.file_path))
        explanation = task_creator._generate_relevance_explanation(test_chunk)
        preview = task_creator._generate_file_preview(test_chunk)
        
        print(f"File Size: {file_size}")
        print(f"Last Modified: {last_modified}")
        print(f"File Icon: {file_icon}")
        print(f"Explanation: {explanation}")
        print(f"Preview Lines: {len(preview)}")
        
        print("\n✅ Enhanced Context Preview UI Test Completed Successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced Context UI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_relevance_scoring():
    """Test the enhanced relevance scoring system."""
    try:
        print("\n🎯 Testing Enhanced Relevance Scoring:")
        print("-" * 50)
        
        # Initialize GraphitiContextRetriever
        from mods.project_management.graphiti_retriever import GraphitiContextRetriever
        retriever = GraphitiContextRetriever(".")
        
        # Create test chunk
        test_chunk = ContextChunk(
            text="def create_enhanced_task(self, title, description):\n    # AI-enhanced task creation with context\n    return task_id, file_path",
            file_path="mods/project_management/ai_task_creator.py",
            chunk_type="code",
            start_line=75,
            end_line=85,
            confidence=0.9,
            relevance_score=0.7,
            file_name="ai_task_creator.py",
            file_type="python"
        )
        
        # Test enhanced scoring methods
        base_score = 0.7
        query = "enhanced task creation with AI"
        
        enhanced_score = retriever._calculate_enhanced_relevance_score(test_chunk, base_score, query)
        content_quality = retriever._assess_content_quality(test_chunk)
        semantic_depth = retriever._calculate_semantic_depth(test_chunk, query)
        file_importance = retriever._calculate_file_importance(test_chunk)
        query_specificity = retriever._calculate_query_specificity_bonus(test_chunk, query)
        matched_keywords = retriever._extract_matched_keywords(test_chunk, query)
        
        print(f"Base Score: {base_score:.3f}")
        print(f"Enhanced Score: {enhanced_score:.3f}")
        print(f"Content Quality: {content_quality:.3f}")
        print(f"Semantic Depth: {semantic_depth:.3f}")
        print(f"File Importance: {file_importance:.3f}")
        print(f"Query Specificity: {query_specificity:.3f}")
        print(f"Matched Keywords: {matched_keywords}")
        
        print("\n✅ Enhanced Relevance Scoring Test Completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced relevance scoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting TASK-087 Enhanced Context Preview UI Tests")
    print("=" * 80)
    
    # Test 1: Enhanced Context UI
    ui_test_result = await test_enhanced_context_ui()
    
    # Test 2: Enhanced Relevance Scoring
    scoring_test_result = await test_enhanced_relevance_scoring()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 40)
    print(f"Enhanced Context UI: {'✅ PASS' if ui_test_result else '❌ FAIL'}")
    print(f"Enhanced Relevance Scoring: {'✅ PASS' if scoring_test_result else '❌ FAIL'}")
    
    overall_success = ui_test_result and scoring_test_result
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    asyncio.run(main())
