"""
Anthropic Claude Provider for TaskHero AI.

Integrates with Anthropic's Claude models for AI chat functionality.
"""

import os
import asyncio
from typing import Dict, Any, Optional, AsyncIterator
import logging

try:
    import anthropic
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base_provider import (
    AIProvider, 
    ProviderError, 
    ProviderNotAvailableError, 
    ProviderConfigError,
    ProviderAuthError,
    ProviderRateLimitError
)


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Anthropic provider."""
        super().__init__("Anthropic", config)
        self.client: Optional[AsyncAnthropic] = None
        self.model = self.config.get('model', 'claude-3-sonnet-20240229')
        self.api_key = self.config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
    
    async def _perform_initialization(self) -> bool:
        """Initialize Anthropic client."""
        if not ANTHROPIC_AVAILABLE:
            self.logger.error("Anthropic library not installed. Install with: pip install anthropic")
            raise ProviderNotAvailableError("Anthropic library not available")
        
        if not self.api_key:
            self.logger.error("Anthropic API key not found in config or environment")
            raise ProviderConfigError("Anthropic API key required")
        
        try:
            self.client = AsyncAnthropic(api_key=self.api_key)
            
            # Test the connection
            await self._test_connection()
            
            self.logger.info(f"Anthropic provider initialized with model: {self.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise ProviderConfigError(f"Anthropic initialization failed: {e}")
    
    async def _test_connection(self) -> None:
        """Test Anthropic API connection."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello"}]
            )
            self.logger.debug("Anthropic connection test successful")
        except anthropic.AuthenticationError:
            raise ProviderAuthError("Invalid Anthropic API key")
        except anthropic.RateLimitError:
            raise ProviderRateLimitError("Anthropic rate limit exceeded")
        except Exception as e:
            raise ProviderError(f"Anthropic connection test failed: {e}")
    
    async def generate_response(
        self, 
        prompt: str, 
        context: str = "", 
        max_tokens: int = 4000,
        temperature: float = 0.7,
        streaming: bool = False
    ) -> str:
        """Generate response using Anthropic Claude."""
        if not self.client:
            raise ProviderNotAvailableError("Anthropic provider not initialized")
        
        # Build the prompt with context
        full_prompt = prompt
        if context:
            full_prompt = f"You are a helpful AI assistant analyzing a codebase. Here's the relevant context:\n\n{context}\n\nUser question: {prompt}"
        
        try:
            if streaming:
                # Use streaming for better UX
                response_text = ""
                async for chunk in self.stream_response(prompt, context, max_tokens, temperature):
                    response_text += chunk
                return response_text
            else:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                
                return response.content[0].text
                
        except anthropic.RateLimitError as e:
            self.logger.warning(f"Anthropic rate limit exceeded: {e}")
            raise ProviderRateLimitError(f"Rate limit exceeded: {e}")
        except anthropic.AuthenticationError as e:
            self.logger.error(f"Anthropic authentication error: {e}")
            raise ProviderAuthError(f"Authentication failed: {e}")
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise ProviderError(f"Anthropic request failed: {e}")
    
    async def stream_response(
        self,
        prompt: str,
        context: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream response from Anthropic Claude."""
        if not self.client:
            raise ProviderNotAvailableError("Anthropic provider not initialized")
        
        # Build the prompt with context
        full_prompt = prompt
        if context:
            full_prompt = f"You are a helpful AI assistant analyzing a codebase. Here's the relevant context:\n\n{context}\n\nUser question: {prompt}"
        
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": full_prompt}]
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except anthropic.RateLimitError as e:
            self.logger.warning(f"Anthropic rate limit exceeded: {e}")
            raise ProviderRateLimitError(f"Rate limit exceeded: {e}")
        except anthropic.AuthenticationError as e:
            self.logger.error(f"Anthropic authentication error: {e}")
            raise ProviderAuthError(f"Authentication failed: {e}")
        except Exception as e:
            self.logger.error(f"Anthropic streaming error: {e}")
            raise ProviderError(f"Anthropic streaming failed: {e}")
    
    async def check_health(self) -> bool:
        """Check Anthropic service health."""
        if not self.client:
            return False
        
        try:
            await self._test_connection()
            return True
        except Exception as e:
            self.logger.warning(f"Anthropic health check failed: {e}")
            return False
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens for Claude models."""
        # Rough estimation: ~4 characters per token for Claude models
        return len(text) // 4
    
    def get_models(self) -> list:
        """Get available Anthropic models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0"
        ]
    
    def set_model(self, model: str) -> None:
        """Set the Anthropic model to use."""
        if model in self.get_models():
            self.model = model
            self.config['model'] = model
            self.logger.info(f"Anthropic model changed to: {model}")
        else:
            raise ProviderConfigError(f"Unsupported model: {model}")
    
    def get_current_model(self) -> str:
        """Get currently selected model."""
        return self.model 