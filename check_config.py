#!/usr/bin/env python3
"""
Configuration Checker for TaskHeroAI

This script checks your current LLM configuration and provides recommendations.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_config():
    """Check and display current configuration."""
    print("🔍 TaskHeroAI Configuration Checker")
    print("=" * 50)
    
    # Embedding Configuration
    print("\n📊 EMBEDDING Configuration:")
    embedding_provider = os.getenv("AI_EMBEDDING_PROVIDER", "openai")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_api_key = os.getenv("AI_EMBEDDING_API_KEY", "")
    
    print(f"  Provider: {embedding_provider}")
    print(f"  Model: {embedding_model}")
    print(f"  API Key: {'✅ Set' if embedding_api_key and embedding_api_key.lower() != 'none' else '❌ Not Set'}")
    
    # Description Configuration
    print("\n📝 DESCRIPTION Configuration:")
    description_provider = os.getenv("AI_DESCRIPTION_PROVIDER", "ollama")
    description_model = os.getenv("DESCRIPTION_MODEL", "llama2")
    description_api_key = os.getenv("AI_DESCRIPTION_API_KEY", "")
    
    print(f"  Provider: {description_provider}")
    print(f"  Model: {description_model}")
    print(f"  API Key: {'✅ Set' if description_api_key and description_api_key.lower() != 'none' else '❌ Not Set'}")
    
    # Chat Configuration
    print("\n💬 CHAT Configuration:")
    chat_provider = os.getenv("AI_CHAT_PROVIDER", "ollama")
    chat_model = os.getenv("CHAT_MODEL", "llama2")
    chat_api_key = os.getenv("AI_CHAT_API_KEY", "")
    
    print(f"  Provider: {chat_provider}")
    print(f"  Model: {chat_model}")
    print(f"  API Key: {'✅ Set' if chat_api_key and chat_api_key.lower() != 'none' else '❌ Not Set'}")
    
    # Ollama Check
    print("\n🦙 OLLAMA Status:")
    if description_provider == "ollama" or chat_provider == "ollama":
        try:
            import ollama
            try:
                # Test Ollama connection
                ollama.list()
                print("  Connection: ✅ Ollama is accessible")
                
                # Check if required models are available
                models = ollama.list()
                model_names = [model['name'] for model in models.get('models', [])]
                
                if description_provider == "ollama":
                    if any(description_model in name for name in model_names):
                        print(f"  Description Model ({description_model}): ✅ Available")
                    else:
                        print(f"  Description Model ({description_model}): ❌ Not found")
                        print(f"    📋 Run: ollama pull {description_model}")
                
                if chat_provider == "ollama":
                    if any(chat_model in name for name in model_names):
                        print(f"  Chat Model ({chat_model}): ✅ Available")
                    else:
                        print(f"  Chat Model ({chat_model}): ❌ Not found")
                        print(f"    📋 Run: ollama pull {chat_model}")
                        
            except Exception as e:
                print(f"  Connection: ❌ Ollama connection failed")
                print(f"    Error: {str(e)}")
                print(f"    📋 Make sure Ollama is running: ollama serve")
                
        except ImportError:
            print("  Ollama Package: ❌ Not installed")
    else:
        print("  Not using Ollama")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if description_provider == "ollama" and (not embedding_api_key or embedding_api_key.lower() == 'none'):
        print("  🚨 You're using Ollama for descriptions but no API key for embeddings")
        print("     Consider setting up OpenAI API key for both embeddings and descriptions")
    
    if description_provider == "ollama":
        print("  💡 If Ollama is causing issues, consider switching to a cloud provider:")
        print("     Set AI_DESCRIPTION_PROVIDER=openai and AI_DESCRIPTION_API_KEY")
    
    if embedding_api_key and embedding_api_key.lower() != 'none' and embedding_provider == "openai":
        print("  ✨ You have OpenAI API key - you can use it for descriptions too!")
        print("     Set AI_DESCRIPTION_PROVIDER=openai to use the same API key")
    
    # Show .env file status
    env_file = Path(".env")
    print(f"\n📄 Environment File:")
    print(f"  .env exists: {'✅' if env_file.exists() else '❌'}")
    if env_file.exists():
        print(f"  Path: {env_file.absolute()}")
    else:
        print("  📋 Create a .env file with your configuration")

if __name__ == "__main__":
    try:
        check_config()
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        sys.exit(1) 