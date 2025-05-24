"""
OpenAI Provider for TaskHero AI.

Integrates with OpenAI's GPT models for AI chat functionality.
"""

import os
import asyncio
from typing import Dict, Any, Optional, AsyncIterator
import logging

try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base_provider import (
    AIProvider, 
    ProviderError, 
    ProviderNotAvailableError, 
    ProviderConfigError,
    ProviderAuthError,
    ProviderRateLimitError
)


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize OpenAI provider."""
        super().__init__("OpenAI", config)
        self.client: Optional[AsyncOpenAI] = None
        self.model = self.config.get('model', 'gpt-4')
        self.api_key = self.config.get('api_key') or os.getenv('OPENAI_API_KEY')
    
    async def _perform_initialization(self) -> bool:
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            self.logger.error("OpenAI library not installed. Install with: pip install openai")
            raise ProviderNotAvailableError("OpenAI library not available")
        
        if not self.api_key:
            self.logger.error("OpenAI API key not found in config or environment")
            raise ProviderConfigError("OpenAI API key required")
        
        try:
            self.client = AsyncOpenAI(api_key=self.api_key)
            
            # Test the connection with a simple request
            await self._test_connection()
            
            self.logger.info(f"OpenAI provider initialized with model: {self.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise ProviderConfigError(f"OpenAI initialization failed: {e}")
    
    async def _test_connection(self) -> None:
        """Test OpenAI API connection."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            self.logger.debug("OpenAI connection test successful")
        except openai.AuthenticationError:
            raise ProviderAuthError("Invalid OpenAI API key")
        except openai.RateLimitError:
            raise ProviderRateLimitError("OpenAI rate limit exceeded")
        except Exception as e:
            raise ProviderError(f"OpenAI connection test failed: {e}")
    
    async def generate_response(
        self, 
        prompt: str, 
        context: str = "", 
        max_tokens: int = 4000,
        temperature: float = 0.7,
        streaming: bool = False
    ) -> str:
        """Generate response using OpenAI."""
        if not self.client:
            raise ProviderNotAvailableError("OpenAI provider not initialized")
        
        # Build messages
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"You are a helpful AI assistant analyzing a codebase. Here's the relevant context:\n\n{context}"
            })
        else:
            messages.append({
                "role": "system", 
                "content": "You are a helpful AI assistant for code analysis and development."
            })
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            if streaming:
                # Use streaming for better UX
                response_text = ""
                async for chunk in self.stream_response(prompt, context, max_tokens, temperature):
                    response_text += chunk
                return response_text
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                return response.choices[0].message.content
                
        except openai.RateLimitError as e:
            self.logger.warning(f"OpenAI rate limit exceeded: {e}")
            raise ProviderRateLimitError(f"Rate limit exceeded: {e}")
        except openai.AuthenticationError as e:
            self.logger.error(f"OpenAI authentication error: {e}")
            raise ProviderAuthError(f"Authentication failed: {e}")
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise ProviderError(f"OpenAI request failed: {e}")
    
    async def stream_response(
        self,
        prompt: str,
        context: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream response from OpenAI."""
        if not self.client:
            raise ProviderNotAvailableError("OpenAI provider not initialized")
        
        # Build messages
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"You are a helpful AI assistant analyzing a codebase. Here's the relevant context:\n\n{context}"
            })
        else:
            messages.append({
                "role": "system",
                "content": "You are a helpful AI assistant for code analysis and development."
            })
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except openai.RateLimitError as e:
            self.logger.warning(f"OpenAI rate limit exceeded: {e}")
            raise ProviderRateLimitError(f"Rate limit exceeded: {e}")
        except openai.AuthenticationError as e:
            self.logger.error(f"OpenAI authentication error: {e}")
            raise ProviderAuthError(f"Authentication failed: {e}")
        except Exception as e:
            self.logger.error(f"OpenAI streaming error: {e}")
            raise ProviderError(f"OpenAI streaming failed: {e}")
    
    async def check_health(self) -> bool:
        """Check OpenAI service health."""
        if not self.client:
            return False
        
        try:
            await self._test_connection()
            return True
        except Exception as e:
            self.logger.warning(f"OpenAI health check failed: {e}")
            return False
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens for OpenAI models."""
        # Rough estimation: ~4 characters per token for GPT models
        return len(text) // 4
    
    def get_models(self) -> list:
        """Get available OpenAI models."""
        return [
            "gpt-4",
            "gpt-4-turbo-preview", 
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
    
    def set_model(self, model: str) -> None:
        """Set the OpenAI model to use."""
        if model in self.get_models():
            self.model = model
            self.config['model'] = model
            self.logger.info(f"OpenAI model changed to: {model}")
        else:
            raise ProviderConfigError(f"Unsupported model: {model}")
    
    def get_current_model(self) -> str:
        """Get currently selected model."""
        return self.model 