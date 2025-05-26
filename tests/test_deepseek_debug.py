#!/usr/bin/env python3
"""
Debug script to test DeepSeek API directly.
"""

import os
import asyncio
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_deepseek_api():
    """Test DeepSeek API directly."""
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test different endpoints and models
    base_url = "https://api.deepseek.com"
    
    async with httpx.AsyncClient(
        base_url=base_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        timeout=30.0
    ) as client:
        
        # Test 1: Check models endpoint
        print("\n🧪 Test 1: Checking available models...")
        try:
            response = await client.get("/models")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                models = response.json()
                print(f"Available models: {len(models.get('data', []))}")
                for model in models.get('data', [])[:3]:
                    print(f"  - {model.get('id', 'Unknown')}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"❌ Models endpoint failed: {e}")
        
        # Test 2: Simple chat completion with deepseek-chat
        print("\n🧪 Test 2: Testing deepseek-chat model...")
        try:
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello in one sentence."}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            print(f"Request payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post("/v1/chat/completions", json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Response: {result['choices'][0]['message']['content']}")
                return True
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Chat completion failed: {e}")
        
        # Test 3: Test deepseek-reasoner model
        print("\n🧪 Test 3: Testing deepseek-reasoner model...")
        try:
            payload = {
                "model": "deepseek-reasoner",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is 2+2?"}
                ],
                "max_tokens": 100,
                "temperature": 0.1
            }
            
            response = await client.post("/v1/chat/completions", json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Response: {result['choices'][0]['message']['content']}")
                return True
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Reasoner model failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🔍 DeepSeek API Debug Test")
    print("=" * 50)
    
    success = asyncio.run(test_deepseek_api())
    
    if success:
        print("\n✅ DeepSeek API is working!")
    else:
        print("\n❌ DeepSeek API has issues. Check your API key and network connection.")
