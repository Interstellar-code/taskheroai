#!/usr/bin/env python3
"""
Test script for agent mode tools and response generation.
"""

import asyncio
import os
import sys
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mods.ai.providers.provider_factory import ProviderFactory
from mods.code.tools import CodebaseTools
from mods.code.indexer import FileIndexer

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_agent_tools():
    """Test the agent mode tools and response generation."""
    print("🧪 Testing Agent Mode Tools and Response Generation...")
    
    try:
        # Test 1: Provider Factory
        print("\n1. Testing Provider Factory...")
        factory = ProviderFactory()
        
        # Get best provider
        best_provider = await factory.get_best_available_provider()
        print(f"   Best provider: {best_provider}")
        
        if not best_provider:
            print("   ❌ No providers available")
            return False
            
        # Create provider
        provider = await factory.get_or_create_provider(best_provider)
        if not provider:
            print("   ❌ Failed to create provider")
            return False
            
        print(f"   ✅ Provider created: {provider.name}")
        
        # Test 2: Simple Response Generation
        print("\n2. Testing Simple Response Generation...")
        try:
            response = await provider.generate_response(
                prompt="What tools are available in this application? List them briefly.",
                max_tokens=500,
                temperature=0.7
            )
            
            if response and len(response.strip()) > 0:
                print(f"   ✅ Response generated: {response[:100]}...")
            else:
                print("   ❌ Empty or invalid response")
                return False
                
        except Exception as e:
            print(f"   ❌ Response generation failed: {e}")
            logger.exception("Response generation error details:")
            return False
        
        # Test 3: Tools Integration
        print("\n3. Testing Tools Integration...")
        try:
            # Create a simple indexer for testing
            indexer = FileIndexer()
            indexer.root_path = os.getcwd()
            
            # Create tools
            tools = CodebaseTools(indexer)
            print("   ✅ Tools created successfully")
            
            # Test directory tree
            result = tools.directory_tree(max_depth=2)
            if result and 'tree' in result:
                print(f"   ✅ Directory tree generated: {len(result['tree'])} characters")
            else:
                print(f"   ❌ Directory tree failed: {result}")
                
        except Exception as e:
            print(f"   ❌ Tools integration failed: {e}")
            logger.exception("Tools integration error details:")
            return False
        
        # Test 4: Complex Query Simulation
        print("\n4. Testing Complex Query Simulation...")
        try:
            complex_prompt = """You are an AI agent with access to tools. The user asked: "what are the tools available in the app?"

Based on the codebase structure, please provide a comprehensive answer about the available tools.

Available tools include:
- embed_search: Search using vector embeddings
- directory_tree: Get directory structure
- grep: Search for text patterns
- read_file: Read file contents
- file_stats: Get file statistics
- find_functions: Find function definitions
- find_classes: Find class definitions
- code_analysis: Analyze code structure

Please provide a detailed response about these tools."""

            response = await provider.generate_response(
                prompt=complex_prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            if response and len(response.strip()) > 0:
                print(f"   ✅ Complex response generated: {response[:150]}...")
            else:
                print("   ❌ Complex response failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Complex query failed: {e}")
            logger.exception("Complex query error details:")
            return False
        
        await factory.close_all_providers()
        
        print("\n🎉 All agent mode tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test error details:")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent_tools())
    sys.exit(0 if success else 1)
