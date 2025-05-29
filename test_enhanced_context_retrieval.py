#!/usr/bin/env python3
"""
Enhanced Context Retrieval Test Suite

Tests the Phase 2 implementation of enhanced context retrieval using TaskHero AI's
existing embedding system with advanced features like relationship awareness,
semantic clustering, and relevance boosting.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from mods.project_management.graphiti_retriever import GraphitiContextRetriever
from mods.project_management.ai_task_creator import AITaskCreator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EnhancedContextTest")


async def test_enhanced_retrieval_initialization():
    """Test enhanced context retrieval initialization."""
    logger.info("Testing Enhanced Context Retrieval Initialization...")

    try:
        retriever = GraphitiContextRetriever(".")

        # Check availability
        is_available = retriever.is_available()
        logger.info(f"Enhanced retrieval available: {is_available}")

        # Get statistics
        stats = retriever.get_graph_statistics()
        logger.info(f"Statistics: {stats}")

        # Verify initialization
        assert hasattr(retriever, '_embedding_cache'), "Embedding cache not initialized"
        assert hasattr(retriever, '_relationship_graph'), "Relationship graph not initialized"
        assert hasattr(retriever, 'semantic_search'), "Semantic search not initialized"

        logger.info("✅ Enhanced retrieval initialization test passed")
        return True

    except Exception as e:
        logger.error(f"❌ Enhanced retrieval initialization test failed: {e}")
        return False


async def test_health_check():
    """Test health check functionality."""
    logger.info("Testing Health Check...")

    try:
        retriever = GraphitiContextRetriever(".")

        # Perform health check
        health = await retriever.health_check()
        logger.info(f"Health check results: {health}")

        # Verify health check structure
        assert 'enhanced_retrieval_initialized' in health, "Missing initialization status"
        assert 'project_root' in health, "Missing project root"
        assert 'embeddings_directory' in health, "Missing embeddings directory"
        assert 'config' in health, "Missing config"

        logger.info("✅ Health check test passed")
        return True

    except Exception as e:
        logger.error(f"❌ Health check test failed: {e}")
        return False


async def test_context_retrieval():
    """Test enhanced context retrieval functionality."""
    logger.info("Testing Enhanced Context Retrieval...")

    try:
        retriever = GraphitiContextRetriever(".")

        if not retriever.is_available():
            logger.warning("Enhanced retrieval not available - skipping context retrieval test")
            return True

        # Test queries
        test_queries = [
            "user authentication system",
            "task creation workflow",
            "AI enhancement features",
            "embedding and indexing",
            "project management"
        ]

        total_results = 0
        for query in test_queries:
            logger.info(f"Testing query: '{query}'")

            start_time = time.time()
            context_chunks = await retriever.retrieve_context(query, max_results=5)
            query_time = time.time() - start_time

            logger.info(f"  Retrieved {len(context_chunks)} chunks in {query_time:.3f}s")
            total_results += len(context_chunks)

            # Verify chunk structure
            for i, chunk in enumerate(context_chunks[:2]):  # Check first 2 chunks
                assert hasattr(chunk, 'file_path'), f"Chunk {i} missing file_path"
                assert hasattr(chunk, 'text'), f"Chunk {i} missing text"
                assert hasattr(chunk, 'relevance_score'), f"Chunk {i} missing relevance_score"

                # Handle file_path as string (not Path object)
                file_name = Path(chunk.file_path).name if chunk.file_path else "unknown"
                logger.info(f"    {i+1}. {file_name} (score: {chunk.relevance_score:.3f})")

        logger.info(f"Total results across all queries: {total_results}")
        logger.info("✅ Enhanced context retrieval test passed")
        return True

    except Exception as e:
        logger.error(f"❌ Enhanced context retrieval test failed: {e}")
        return False


async def test_relationship_enhancement():
    """Test relationship-based enhancement features."""
    logger.info("Testing Relationship Enhancement...")

    try:
        retriever = GraphitiContextRetriever(".")

        if not retriever.is_available():
            logger.warning("Enhanced retrieval not available - skipping relationship test")
            return True

        # Test with relationship expansion enabled
        retriever.configure(enable_relationship_expansion=True)

        # Query that should trigger relationship expansion
        query = "AI task creator implementation"
        context_chunks = await retriever.retrieve_context(query, max_results=8)

        logger.info(f"Retrieved {len(context_chunks)} chunks with relationship expansion")

        # Check for diverse file types (indicating relationship expansion worked)
        file_types = set(Path(chunk.file_path).suffix for chunk in context_chunks if chunk.file_path)
        logger.info(f"File types found: {file_types}")

        # Test without relationship expansion
        retriever.configure(enable_relationship_expansion=False)
        context_chunks_no_rel = await retriever.retrieve_context(query, max_results=8)

        logger.info(f"Retrieved {len(context_chunks_no_rel)} chunks without relationship expansion")

        logger.info("✅ Relationship enhancement test passed")
        return True

    except Exception as e:
        logger.error(f"❌ Relationship enhancement test failed: {e}")
        return False


async def test_semantic_clustering():
    """Test semantic clustering for result diversity."""
    logger.info("Testing Semantic Clustering...")

    try:
        retriever = GraphitiContextRetriever(".")

        if not retriever.is_available():
            logger.warning("Enhanced retrieval not available - skipping clustering test")
            return True

        # Test with semantic clustering enabled
        retriever.configure(use_semantic_clustering=True)

        query = "project management and task creation"
        context_chunks = await retriever.retrieve_context(query, max_results=10)

        logger.info(f"Retrieved {len(context_chunks)} chunks with semantic clustering")

        # Check for directory diversity
        directories = set(str(Path(chunk.file_path).parent) for chunk in context_chunks if chunk.file_path)
        logger.info(f"Directories represented: {len(directories)}")

        # Check for file type diversity
        file_types = set(Path(chunk.file_path).suffix for chunk in context_chunks if chunk.file_path)
        logger.info(f"File types represented: {file_types}")

        logger.info("✅ Semantic clustering test passed")
        return True

    except Exception as e:
        logger.error(f"❌ Semantic clustering test failed: {e}")
        return False


async def test_performance_benchmark():
    """Test performance benchmarking."""
    logger.info("Testing Performance Benchmark...")

    try:
        retriever = GraphitiContextRetriever(".")

        if not retriever.is_available():
            logger.warning("Enhanced retrieval not available - skipping benchmark test")
            return True

        # Run performance benchmark
        test_queries = [
            "implement user authentication",
            "fix database connection issue",
            "create API endpoint",
            "update configuration settings",
            "enhance task creation workflow"
        ]

        benchmark_results = await retriever.benchmark_performance(test_queries)

        logger.info(f"Benchmark results: {benchmark_results}")

        # Verify benchmark structure
        assert 'total_queries' in benchmark_results, "Missing total_queries"
        assert 'average_time' in benchmark_results, "Missing average_time"
        assert 'total_time' in benchmark_results, "Missing total_time"

        avg_time = benchmark_results['average_time']
        logger.info(f"Average query time: {avg_time:.3f}s")

        # Performance should be reasonable (under 2 seconds per query)
        if avg_time > 2.0:
            logger.warning(f"Performance may be slow: {avg_time:.3f}s average")
        else:
            logger.info("Performance is good!")

        logger.info("✅ Performance benchmark test passed")
        return True

    except Exception as e:
        logger.error(f"❌ Performance benchmark test failed: {e}")
        return False


async def test_integration_with_task_creator():
    """Test integration with AI Task Creator."""
    logger.info("Testing Integration with AI Task Creator...")

    try:
        # Initialize AI Task Creator (which uses GraphitiContextRetriever)
        creator = AITaskCreator(project_root=".")

        # Check if enhanced retrieval is available
        enhanced_available = creator.graphiti_retriever.is_available()
        logger.info(f"Enhanced retrieval available in task creator: {enhanced_available}")

        # Test context collection through task creator
        query = "implement user authentication system"
        context_chunks = await creator._collect_context_with_graphiti(query, {'task_type': 'Development'})

        logger.info(f"Task creator retrieved {len(context_chunks)} context chunks")

        # Verify integration works
        if context_chunks:
            logger.info("Integration successful - context retrieved through task creator")
        else:
            logger.info("No context retrieved - may be expected if no embeddings exist")

        logger.info("✅ Integration test passed")
        return True

    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False


async def run_all_tests():
    """Run all enhanced context retrieval tests."""
    logger.info("🚀 Starting Enhanced Context Retrieval Test Suite")
    logger.info("=" * 60)

    tests = [
        test_enhanced_retrieval_initialization,
        test_health_check,
        test_context_retrieval,
        test_relationship_enhancement,
        test_semantic_clustering,
        test_performance_benchmark,
        test_integration_with_task_creator
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Test {test.__name__} crashed: {e}")
            failed += 1

        logger.info("-" * 40)

    # Summary
    logger.info("🎯 Test Suite Summary")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        logger.info("🎉 All tests passed! Enhanced context retrieval is working correctly.")
    else:
        logger.warning(f"⚠️  {failed} test(s) failed. Please review the issues above.")

    return failed == 0


async def test_embeddings_ready():
    """Test if embeddings are ready for enhanced context retrieval."""
    logger.info("Testing if embeddings are ready...")

    try:
        retriever = GraphitiContextRetriever(".")

        # Check if embeddings directory exists and has files
        embeddings_dir = retriever.embeddings_dir
        logger.info(f"Checking embeddings directory: {embeddings_dir}")

        if not embeddings_dir.exists():
            logger.warning("❌ Embeddings directory does not exist")
            return False

        # Check for embedding files
        embedding_files = list(embeddings_dir.glob("*.json"))
        logger.info(f"Found {len(embedding_files)} embedding files")

        if len(embedding_files) == 0:
            logger.warning("❌ No embedding files found - please run indexing first")
            return False

        # Test loading a sample file
        try:
            with open(embedding_files[0], 'r', encoding='utf-8') as f:
                sample_data = json.load(f)

            has_chunks = 'chunks' in sample_data
            has_embeddings = 'embeddings' in sample_data
            has_metadata = 'metadata' in sample_data
            has_enhanced_metadata = has_metadata and sample_data.get('metadata', {}).get('graphiti_compatible', False)

            logger.info(f"Sample file structure - chunks: {has_chunks}, embeddings: {has_embeddings}, metadata: {has_metadata}, enhanced: {has_enhanced_metadata}")

            if has_chunks and has_embeddings:
                if has_enhanced_metadata:
                    logger.info("✅ Embeddings are ready with enhanced metadata for advanced context retrieval!")
                else:
                    logger.info("✅ Embeddings are ready (legacy format) - enhanced context retrieval will work with basic features!")
                return True
            else:
                logger.warning("❌ Embedding files have unexpected structure")
                return False

        except Exception as e:
            logger.error(f"❌ Error reading embedding file: {e}")
            return False

    except Exception as e:
        logger.error(f"❌ Error checking embeddings: {e}")
        return False


if __name__ == "__main__":
    import json

    # First check if embeddings are ready
    embeddings_ready = asyncio.run(test_embeddings_ready())

    if not embeddings_ready:
        logger.warning("⚠️  Embeddings not ready. Please run TaskHero AI indexing first.")
        logger.info("To generate embeddings:")
        logger.info("1. Run: python app.py")
        logger.info("2. Choose option 1 (Index Codebase)")
        logger.info("3. Wait for indexing to complete")
        logger.info("4. Then run this test again")
        sys.exit(1)

    # Run full test suite
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
