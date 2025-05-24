"""
OpenRouter Provider for TaskHero AI.

Provides access to multiple AI models through OpenRouter's unified API.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator

import httpx
from httpx_sse import aconnect_sse

from .base_provider import AIProvider, ProviderConfigError


class OpenRouterProvider(AIProvider):
    """OpenRouter AI provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenRouter provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.api_key = self.config.get('api_key') or os.getenv('OPENROUTER_API_KEY')
        self.model = self.config.get('model', 'openai/gpt-4')
        self.max_tokens = self.config.get('max_tokens', 4000)
        self.temperature = self.config.get('temperature', 0.7)
        self.top_p = self.config.get('top_p', 1.0)
        self.http_referer = self.config.get('http_referer') or os.getenv('OPENROUTER_HTTP_REFERER', 'https://taskhero-ai.com')
        self.x_title = self.config.get('x_title') or os.getenv('OPENROUTER_X_TITLE', 'TaskHeroAI')
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = None
        
        if not self.api_key:
            raise ProviderConfigError("OpenRouter API key is required")
    
    async def initialize(self) -> bool:
        """
        Initialize the OpenRouter provider.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": self.http_referer,
                    "X-Title": self.x_title,
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            # Test the connection
            if await self.check_health():
                self.logger.info("OpenRouter provider initialized successfully")
                return True
            else:
                self.logger.error("OpenRouter provider health check failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenRouter provider: {e}")
            return False
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using OpenRouter API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
            
        Raises:
            ProviderConfigError: If provider not initialized or API error
        """
        if not self.client:
            raise ProviderConfigError("OpenRouter provider not initialized")
        
        try:
            # Prepare request payload
            payload = {
                "model": kwargs.get('model', self.model),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', self.max_tokens),
                "temperature": kwargs.get('temperature', self.temperature),
                "top_p": kwargs.get('top_p', self.top_p),
                "stream": False
            }
            
            # Add optional parameters
            if 'frequency_penalty' in kwargs:
                payload['frequency_penalty'] = kwargs['frequency_penalty']
            if 'presence_penalty' in kwargs:
                payload['presence_penalty'] = kwargs['presence_penalty']
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise ProviderConfigError("Invalid response format from OpenRouter")
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
            raise ProviderConfigError(f"OpenRouter API error: {e.response.status_code}")
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise ProviderConfigError(f"Response generation failed: {e}")
    
    async def stream_response(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """
        Generate a streaming response using OpenRouter API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Yields:
            Response chunks as they arrive
            
        Raises:
            ProviderConfigError: If provider not initialized or API error
        """
        if not self.client:
            raise ProviderConfigError("OpenRouter provider not initialized")
        
        try:
            # Prepare request payload
            payload = {
                "model": kwargs.get('model', self.model),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', self.max_tokens),
                "temperature": kwargs.get('temperature', self.temperature),
                "top_p": kwargs.get('top_p', self.top_p),
                "stream": True
            }
            
            # Add optional parameters
            if 'frequency_penalty' in kwargs:
                payload['frequency_penalty'] = kwargs['frequency_penalty']
            if 'presence_penalty' in kwargs:
                payload['presence_penalty'] = kwargs['presence_penalty']
            
            async with aconnect_sse(
                self.client, 
                "POST", 
                "/chat/completions",
                json=payload
            ) as event_source:
                async for sse in event_source.aiter_sse():
                    if sse.data == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(sse.data)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                    except json.JSONDecodeError:
                        continue
                        
        except httpx.HTTPStatusError as e:
            self.logger.error(f"OpenRouter streaming API error: {e.response.status_code} - {e.response.text}")
            raise ProviderConfigError(f"OpenRouter streaming API error: {e.response.status_code}")
        except Exception as e:
            self.logger.error(f"Error streaming response: {e}")
            raise ProviderConfigError(f"Streaming response failed: {e}")
    
    async def check_health(self) -> bool:
        """
        Check if the OpenRouter provider is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Test with a simple request to models endpoint
            response = await self.client.get("/models")
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"OpenRouter health check failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models from OpenRouter.
        
        Returns:
            List of available model names
        """
        # Common OpenRouter models
        return [
            "openai/gpt-4",
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku",
            "meta-llama/llama-2-70b-chat",
            "google/gemini-pro",
            "mistralai/mixtral-8x7b-instruct",
            "cohere/command-r-plus"
        ]
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary
        """
        if not self.client:
            return {}
        
        try:
            response = await self.client.get("/models")
            if response.status_code == 200:
                models = response.json()
                for model in models.get('data', []):
                    if model.get('id') == model_name:
                        return model
        except Exception as e:
            self.logger.warning(f"Failed to get model info for {model_name}: {e}")
        
        return {}
    
    async def close(self) -> None:
        """Close the provider and cleanup resources."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self.logger.info("OpenRouter provider closed")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get provider information.
        
        Returns:
            Provider information dictionary
        """
        return {
            "name": "OpenRouter",
            "type": "openrouter",
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "api_key_configured": bool(self.api_key),
            "base_url": self.base_url,
            "http_referer": self.http_referer,
            "x_title": self.x_title
        } 