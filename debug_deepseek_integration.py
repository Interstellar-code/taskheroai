#!/usr/bin/env python3
"""
Comprehensive debug script for DeepSeek integration issues.
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
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

async def test_deepseek_step_by_step():
    """Test DeepSeek integration step by step."""
    
    print("🔍 DeepSeek Integration Debug")
    print("=" * 60)
    
    # Step 1: Check environment variables
    print("\n📋 Step 1: Environment Variables")
    print("-" * 30)
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    model = os.getenv('DEEPSEEK_MODEL')
    max_tokens = os.getenv('DEEPSEEK_MAX_TOKENS')
    temperature = os.getenv('DEEPSEEK_TEMPERATURE')
    
    print(f"API Key: {'✅ Set' if api_key else '❌ Missing'} ({api_key[:10]}...{api_key[-4:] if api_key else 'None'})")
    print(f"Model: {model}")
    print(f"Max Tokens: {max_tokens}")
    print(f"Temperature: {temperature}")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY is missing!")
        return False
    
    # Step 2: Test provider factory configuration
    print("\n🏭 Step 2: Provider Factory Configuration")
    print("-" * 40)
    
    try:
        from mods.ai.providers.provider_factory import ProviderFactory
        
        factory = ProviderFactory()
        deepseek_config = factory.get_provider_config('deepseek')
        
        print(f"Factory Config:")
        for key, value in deepseek_config.items():
            if 'api_key' in key.lower():
                print(f"  {key}: {'✅ Set' if value else '❌ Missing'}")
            else:
                print(f"  {key}: {value}")
        
        available_providers = await factory.get_available_providers()
        print(f"\nAvailable providers: {available_providers}")
        print(f"DeepSeek available: {'✅ Yes' if 'deepseek' in available_providers else '❌ No'}")
        
    except Exception as e:
        print(f"❌ Provider factory error: {e}")
        return False
    
    # Step 3: Test direct DeepSeek provider creation
    print("\n🤖 Step 3: Direct DeepSeek Provider")
    print("-" * 35)
    
    try:
        from mods.ai.providers.deepseek_provider import DeepSeekProvider
        
        # Create with factory config
        provider = DeepSeekProvider(deepseek_config)
        print("✅ Provider created with factory config")
        
        # Test initialization
        if await provider.initialize():
            print("✅ Provider initialized successfully")
        else:
            print("❌ Provider initialization failed")
            return False
        
        # Test health check
        if await provider.check_health():
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
        
        # Test simple generation
        response = await provider.generate_response(
            prompt="Say hello in one sentence.",
            context="",
            max_tokens=50
        )
        
        if response:
            print(f"✅ Generation test: {response[:100]}...")
        else:
            print("❌ Generation test failed")
            return False
            
    except Exception as e:
        print(f"❌ Direct provider test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Test through provider factory
    print("\n🏭 Step 4: Provider Factory Creation")
    print("-" * 35)
    
    try:
        provider_from_factory = await factory.create_provider('deepseek')
        print("✅ Provider created through factory")
        
        response = await provider_from_factory.generate_response(
            prompt="What is 2+2?",
            context="",
            max_tokens=50
        )
        
        if response:
            print(f"✅ Factory provider test: {response[:100]}...")
        else:
            print("❌ Factory provider test failed")
            return False
            
    except Exception as e:
        print(f"❌ Factory provider test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Test chat handler integration
    print("\n💬 Step 5: Chat Handler Integration")
    print("-" * 35)
    
    try:
        from mods.indexing.indexer import Indexer
        from mods.ai.chat_handler import ChatHandler
        
        # Create minimal indexer
        indexer = Indexer()
        
        # Create chat handler
        chat_handler = ChatHandler(indexer, None, {})
        chat_handler.initialize()
        print("✅ Chat handler created")
        
        # Test provider initialization
        if await chat_handler.initialize_ai_provider():
            provider_name = chat_handler.current_provider.get_name()
            print(f"✅ Chat handler provider: {provider_name}")
            
            # Test query processing
            response, files = await chat_handler.process_query("Hello, how are you?")
            
            if response:
                print(f"✅ Chat handler test: {response[:100]}...")
                return True
            else:
                print("❌ Chat handler returned no response")
                return False
        else:
            print("❌ Chat handler provider initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Chat handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting DeepSeek Integration Debug")
    
    success = asyncio.run(test_deepseek_step_by_step())
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! DeepSeek integration is working.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n💡 Common solutions:")
        print("  • Verify DEEPSEEK_API_KEY is correct")
        print("  • Check internet connection")
        print("  • Ensure model name is correct (deepseek-chat or deepseek-reasoner)")
        print("  • Check DeepSeek API status")
