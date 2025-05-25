#!/usr/bin/env python3
"""
Test script for DeepSeek provider integration.

This script tests the DeepSeek provider functionality without requiring an actual API key.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mods.ai.providers import ProviderFactory, DeepSeekProvider
from mods.settings.ai_settings_manager import AISettingsManager


async def test_deepseek_provider_creation():
    """Test creating a DeepSeek provider instance."""
    print("🧪 Testing DeepSeek Provider Creation...")
    
    try:
        # Test with mock configuration
        config = {
            'api_key': 'test_key_123',
            'model': 'deepseek-chat',
            'max_tokens': 4000,
            'temperature': 0.7
        }
        
        provider = DeepSeekProvider(config)
        print(f"✅ DeepSeek provider created successfully")
        print(f"   - Name: {provider.get_name()}")
        print(f"   - Model: {provider.get_current_model()}")
        print(f"   - Available models: {provider.get_available_models()}")
        
        # Test provider info
        info = provider.get_provider_info()
        print(f"   - Provider info: {info['description']}")
        print(f"   - Supports streaming: {info['supports_streaming']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating DeepSeek provider: {e}")
        return False


async def test_provider_factory():
    """Test DeepSeek provider through the factory."""
    print("\n🏭 Testing Provider Factory...")
    
    try:
        factory = ProviderFactory()
        
        # Check if DeepSeek is in the list of providers
        providers = factory.list_providers()
        if 'deepseek' in providers:
            print("✅ DeepSeek found in provider list")
        else:
            print("❌ DeepSeek not found in provider list")
            return False
        
        # Get provider info
        info = factory.get_provider_info('deepseek')
        print(f"   - Provider info: {info}")
        
        # Test configuration
        config = factory.get_provider_config('deepseek')
        print(f"   - Default config keys: {list(config.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing provider factory: {e}")
        return False


async def test_ai_settings_manager():
    """Test DeepSeek integration in AI settings manager."""
    print("\n⚙️ Testing AI Settings Manager...")
    
    try:
        # Create settings manager
        settings_manager = AISettingsManager()
        settings_manager.initialize()
        
        # Test getting DeepSeek settings
        deepseek_settings = settings_manager.get_deepseek_settings()
        print(f"✅ DeepSeek settings retrieved: {list(deepseek_settings.keys())}")
        
        # Test available models
        models = settings_manager.get_available_models_for_provider('deepseek')
        print(f"   - Available models: {models}")
        
        # Test provider status
        status = settings_manager.get_provider_status('deepseek')
        print(f"   - Provider status: {status['name']} - Available: {status['available']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI settings manager: {e}")
        return False


async def test_environment_variables():
    """Test environment variable configuration."""
    print("\n🌍 Testing Environment Variables...")
    
    try:
        # Check if DeepSeek environment variables are recognized
        env_vars = [
            'DEEPSEEK_API_KEY',
            'DEEPSEEK_MODEL', 
            'DEEPSEEK_MAX_TOKENS',
            'DEEPSEEK_TEMPERATURE',
            'DEEPSEEK_TOP_P'
        ]
        
        for var in env_vars:
            value = os.getenv(var, 'not_set')
            print(f"   - {var}: {value}")
        
        print("✅ Environment variables checked")
        return True
        
    except Exception as e:
        print(f"❌ Error checking environment variables: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting DeepSeek Integration Tests...\n")
    
    tests = [
        test_deepseek_provider_creation,
        test_provider_factory,
        test_ai_settings_manager,
        test_environment_variables
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   - Passed: {sum(results)}/{len(results)}")
    print(f"   - Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! DeepSeek integration is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Get a DeepSeek API key from https://platform.deepseek.com/")
        print("   2. Set DEEPSEEK_API_KEY in your .env file")
        print("   3. Configure DeepSeek as your preferred provider")
        print("   4. Test with actual API calls")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 