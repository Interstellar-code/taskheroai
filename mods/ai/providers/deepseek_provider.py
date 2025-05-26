"""
DeepSeek Provider for TaskHero AI.

Provides access to DeepSeek AI models through their unified API.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator

import httpx
from httpx_sse import aconnect_sse

from .base_provider import (
    AIProvider,
    ProviderError,
    ProviderNotAvailableError,
    ProviderConfigError,
    ProviderAuthError,
    ProviderRateLimitError
)


class DeepSeekProvider(AIProvider):
    """DeepSeek AI provider implementation."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize DeepSeek provider."""
        super().__init__("DeepSeek", config)
        self.api_key = self.config.get('api_key') or os.getenv('DEEPSEEK_API_KEY')
        self.model = self.config.get('model', 'deepseek-chat')
        self.base_url = "https://api.deepseek.com"
        self.client: Optional[httpx.AsyncClient] = None

        if not self.api_key:
            raise ProviderConfigError("DeepSeek API key is required")

    async def _perform_initialization(self) -> bool:
        """Initialize the DeepSeek provider."""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )

            # Test the connection
            if await self.check_health():
                self.logger.info("DeepSeek provider initialized successfully")
                return True
            else:
                self.logger.error("DeepSeek provider health check failed")
                return False

        except Exception as e:
            self.logger.error(f"Failed to initialize DeepSeek provider: {e}")
            return False

    async def generate_response(
        self,
        prompt: str,
        context: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        streaming: bool = False
    ) -> str:
        """
        Generate a response using DeepSeek API.

        Args:
            prompt: The user prompt
            context: Additional context information
            max_tokens: Maximum tokens to generate
            temperature: Response randomness (0.0-1.0)
            streaming: Whether to use streaming mode

        Returns:
            Generated response text

        Raises:
            ProviderConfigError: If provider not initialized or API error
        """
        if not self.client:
            raise ProviderNotAvailableError("DeepSeek provider not initialized")

        # Build the full prompt with context using proper message format
        if context:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant analyzing a codebase. Use the provided context to answer questions accurately and helpfully."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {prompt}"}
            ]
        else:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]

        try:
            # Prepare request payload with proper model validation
            model_name = self.model
            if model_name == "DeepSeek-R1":
                model_name = "deepseek-reasoner"
            elif model_name not in ["deepseek-chat", "deepseek-reasoner"]:
                model_name = "deepseek-chat"  # Default fallback

            payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": min(max_tokens, 8000),  # DeepSeek limit
                "temperature": max(0.0, min(1.0, temperature)),  # Clamp temperature
                "stream": False
            }

            self.logger.debug(f"DeepSeek API request: {model_name} with {len(messages)} messages")

            response = await self.client.post("/v1/chat/completions", json=payload)
            response.raise_for_status()

            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                if content:
                    return content.strip()
                else:
                    raise ProviderError("Empty response from DeepSeek API")
            else:
                self.logger.error(f"Invalid DeepSeek response format: {result}")
                raise ProviderError("Invalid response format from DeepSeek")

        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = error_data.get('error', {}).get('message', str(e.response.text))
            except:
                error_detail = str(e.response.text)

            if e.response.status_code == 401:
                raise ProviderAuthError(f"DeepSeek API authentication failed: {error_detail}")
            elif e.response.status_code == 429:
                raise ProviderRateLimitError(f"DeepSeek API rate limit exceeded: {error_detail}")
            elif e.response.status_code == 400:
                self.logger.error(f"DeepSeek API bad request: {error_detail}")
                raise ProviderError(f"DeepSeek API bad request: {error_detail}")
            else:
                self.logger.error(f"DeepSeek API error {e.response.status_code}: {error_detail}")
                raise ProviderError(f"DeepSeek API error {e.response.status_code}: {error_detail}")
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise ProviderError(f"Response generation failed: {e}")

    async def stream_response(
        self,
        prompt: str,
        context: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Stream response from DeepSeek API.

        Args:
            prompt: The user prompt
            context: Additional context information
            max_tokens: Maximum tokens to generate
            temperature: Response randomness (0.0-1.0)

        Yields:
            Response chunks as they become available

        Raises:
            ProviderConfigError: If provider not initialized or API error
        """
        if not self.client:
            raise ProviderNotAvailableError("DeepSeek provider not initialized")

        # Build the full prompt with context using proper message format
        if context:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant analyzing a codebase. Use the provided context to answer questions accurately and helpfully."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {prompt}"}
            ]
        else:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]

        try:
            # Prepare request payload with proper model validation
            model_name = self.model
            if model_name == "DeepSeek-R1":
                model_name = "deepseek-reasoner"
            elif model_name not in ["deepseek-chat", "deepseek-reasoner"]:
                model_name = "deepseek-chat"  # Default fallback

            payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": min(max_tokens, 8000),  # DeepSeek limit
                "temperature": max(0.0, min(1.0, temperature)),  # Clamp temperature
                "stream": True
            }

            async with aconnect_sse(
                self.client,
                "POST",
                "/v1/chat/completions",
                json=payload
            ) as event_source:
                async for sse in event_source.aiter_sse():
                    if sse.data == "[DONE]":
                        break

                    try:
                        data = json.loads(sse.data)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta and delta['content']:
                                yield delta['content']
                    except json.JSONDecodeError:
                        continue

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ProviderAuthError("DeepSeek API authentication failed")
            elif e.response.status_code == 429:
                raise ProviderRateLimitError("DeepSeek API rate limit exceeded")
            else:
                self.logger.error(f"DeepSeek streaming API error: {e.response.status_code} - {e.response.text}")
                raise ProviderError(f"DeepSeek streaming API error: {e.response.status_code}")
        except Exception as e:
            self.logger.error(f"Error streaming response: {e}")
            raise ProviderError(f"Streaming response failed: {e}")

    async def check_health(self) -> bool:
        """
        Check if the DeepSeek provider is healthy.

        Returns:
            True if healthy, False otherwise
        """
        if not self.client:
            self.logger.warning("DeepSeek health check failed: client not initialized")
            return False

        try:
            # Use the configured model for health check
            model_name = self.model
            if model_name == "DeepSeek-R1":
                model_name = "deepseek-reasoner"
            elif model_name not in ["deepseek-chat", "deepseek-reasoner"]:
                model_name = "deepseek-chat"  # Default fallback

            # Test with a simple chat completion request
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }

            self.logger.debug(f"DeepSeek health check using model: {model_name}")
            response = await self.client.post("/v1/chat/completions", json=payload)

            if response.status_code == 200:
                self.logger.debug("DeepSeek health check passed")
                return True
            else:
                self.logger.warning(f"DeepSeek health check failed with status {response.status_code}: {response.text}")
                return False

        except httpx.HTTPStatusError as e:
            self.logger.warning(f"DeepSeek health check HTTP error {e.response.status_code}: {e.response.text}")
            return False
        except Exception as e:
            self.logger.warning(f"DeepSeek health check failed: {e}")
            return False

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for DeepSeek models.

        Args:
            text: Text to analyze

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token (similar to other models)
        return len(text) // 4

    def get_available_models(self) -> List[str]:
        """
        Get list of available models from DeepSeek.

        Returns:
            List of available model names
        """
        return [
            "deepseek-chat",
            "deepseek-reasoner"
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

    def get_common_models(self) -> List[str]:
        """Get list of common DeepSeek models."""
        return [
            "deepseek-chat",
            "deepseek-reasoner"
        ]

    def set_model(self, model: str) -> None:
        """Set the DeepSeek model to use."""
        self.model = model
        self.config['model'] = model
        self.logger.info(f"DeepSeek model changed to: {model}")

    def get_current_model(self) -> str:
        """Get currently selected model."""
        return self.model

    async def close(self) -> None:
        """Close the provider and cleanup resources."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self.logger.info("DeepSeek provider closed")

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the DeepSeek provider.

        Returns:
            Provider information dictionary
        """
        return {
            'name': 'DeepSeek',
            'description': 'DeepSeek AI models (DeepSeek-V3, DeepSeek-R1)',
            'requires_api_key': True,
            'supports_streaming': True,
            'cost': 'Pay per token',
            'models': self.get_available_models(),
            'base_url': self.base_url,
            'current_model': self.model
        }