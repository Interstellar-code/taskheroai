#!/usr/bin/env python3
"""
Debug script to test chat functionality directly.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

async def test_chat_functionality():
    """Test the chat functionality step by step."""
    
    print("🔍 Testing Chat Functionality")
    print("=" * 50)
    
    try:
        # Import required modules
        from mods.indexing.indexer import Indexer
        from mods.ai.chat_handler import ChatHandler
        from mods.ai.context_manager import CodebaseContextManager
        from mods.ai.providers.provider_factory import ProviderFactory
        
        print("✅ Modules imported successfully")
        
        # Initialize indexer
        print("\n📁 Initializing indexer...")
        indexer = Indexer()
        
        # Check if we have indexed files
        indexed_files = indexer.get_indexed_files()
        print(f"📊 Found {len(indexed_files)} indexed files")
        
        if len(indexed_files) == 0:
            print("⚠️  No files indexed. Running quick index...")
            await indexer.index_directory(os.getcwd())
            indexed_files = indexer.get_indexed_files()
            print(f"📊 After indexing: {len(indexed_files)} files")
        
        # Initialize context manager
        print("\n🧠 Initializing context manager...")
        context_manager = CodebaseContextManager(indexer)
        
        # Initialize provider factory
        print("\n🏭 Initializing provider factory...")
        provider_factory = ProviderFactory()
        
        # Initialize chat handler
        print("\n💬 Initializing chat handler...")
        chat_handler = ChatHandler(indexer, context_manager, provider_factory)
        
        # Test provider initialization
        print("\n🔌 Testing provider initialization...")
        if await chat_handler.initialize_ai_provider():
            print(f"✅ Provider initialized: {chat_handler.current_provider.get_name()}")
        else:
            print("❌ Failed to initialize any provider")
            return False
        
        # Test simple query
        print("\n🧪 Testing simple query...")
        test_query = "What is the main purpose of this project?"
        
        print(f"Query: {test_query}")
        response, relevant_files = await chat_handler.process_query(test_query)
        
        print(f"\n📝 Response length: {len(response) if response else 0}")
        print(f"📁 Relevant files: {len(relevant_files) if relevant_files else 0}")
        
        if response:
            print(f"\n✅ Response preview: {response[:200]}...")
            if relevant_files:
                print(f"📁 Files: {relevant_files[:3]}")
            return True
        else:
            print("❌ No response received")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_deepseek_specifically():
    """Test DeepSeek provider specifically."""
    
    print("\n🤖 Testing DeepSeek Provider Specifically")
    print("=" * 50)
    
    try:
        from mods.ai.providers.deepseek_provider import DeepSeekProvider
        
        # Initialize provider
        provider = DeepSeekProvider()
        
        print("🔧 Initializing DeepSeek provider...")
        if await provider.initialize():
            print("✅ DeepSeek provider initialized")
        else:
            print("❌ Failed to initialize DeepSeek provider")
            return False
        
        # Test simple generation
        print("\n🧪 Testing simple generation...")
        response = await provider.generate_response(
            prompt="Say hello in one sentence.",
            context="",
            max_tokens=100
        )
        
        if response:
            print(f"✅ Response: {response}")
            return True
        else:
            print("❌ No response from DeepSeek")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Chat Debug Tests")
    
    # Test DeepSeek specifically first
    deepseek_success = asyncio.run(test_deepseek_specifically())
    
    # Test full chat functionality
    chat_success = asyncio.run(test_chat_functionality())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"DeepSeek Provider: {'✅ PASS' if deepseek_success else '❌ FAIL'}")
    print(f"Chat Functionality: {'✅ PASS' if chat_success else '❌ FAIL'}")
    
    if deepseek_success and chat_success:
        print("\n🎉 All tests passed! Chat functionality should work.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
