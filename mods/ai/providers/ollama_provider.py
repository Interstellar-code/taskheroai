"""
Ollama Provider for TaskHero AI.

Integrates with local Ollama models for offline AI chat functionality.
"""

import os
import asyncio
import httpx
import json
from typing import Dict, Any, Optional, AsyncIterator
import logging

from .base_provider import (
    AIProvider,
    ProviderError,
    ProviderNotAvailableError,
    ProviderConfigError,
    ProviderAuthError,
    ProviderRateLimitError
)


class OllamaProvider(AIProvider):
    """Ollama local AI provider implementation."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Ollama provider."""
        super().__init__("Ollama", config)
        self.base_url = self.config.get('host', 'http://localhost:11434')
        self.model = self.config.get('model', 'llama2')
        self.client: Optional[httpx.AsyncClient] = None

    async def _perform_initialization(self) -> bool:
        """Initialize Ollama client."""
        try:
            self.client = httpx.AsyncClient(timeout=30.0)

            # Test connection by checking if Ollama is running
            await self._test_connection()

            # Check if the model is available
            await self._ensure_model_available()

            self.logger.info(f"Ollama provider initialized with model: {self.model}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama provider: {e}")
            if self.client:
                await self.client.aclose()
                self.client = None
            raise ProviderConfigError(f"Ollama initialization failed: {e}")

    async def _test_connection(self) -> None:
        """Test Ollama server connection."""
        try:
            response = await self.client.get(f"{self.base_url}/api/version")
            if response.status_code == 200:
                self.logger.debug("Ollama connection test successful")
            else:
                raise ProviderError(f"Ollama server returned status {response.status_code}")
        except httpx.ConnectError:
            raise ProviderNotAvailableError("Cannot connect to Ollama server. Is it running?")
        except Exception as e:
            raise ProviderError(f"Ollama connection test failed: {e}")

    async def _ensure_model_available(self) -> None:
        """Ensure the specified model is available in Ollama."""
        try:
            # List available models
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                raise ProviderError(f"Failed to list Ollama models: {response.status_code}")

            data = response.json()
            available_models = [model['name'] for model in data.get('models', [])]

            # Check if our model is available
            model_variants = [
                self.model,
                f"{self.model}:latest",
                f"{self.model}:7b",
                f"{self.model}:13b"
            ]

            for variant in model_variants:
                if variant in available_models:
                    self.model = variant
                    self.logger.info(f"Using Ollama model: {variant}")
                    return

            # Model not found, try to pull it
            self.logger.warning(f"Model {self.model} not found. Attempting to pull...")
            await self._pull_model()

        except Exception as e:
            raise ProviderConfigError(f"Failed to ensure model availability: {e}")

    async def _pull_model(self) -> None:
        """Pull the model if it's not available."""
        try:
            pull_data = {"name": self.model}
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json=pull_data,
                timeout=300.0  # 5 minute timeout
            )
            if response.status_code == 200:
                self.logger.info(f"Successfully pulled model: {self.model}")
            else:
                raise ProviderError(f"Failed to pull model {self.model}")
        except asyncio.TimeoutError:
            raise ProviderError(f"Timeout pulling model {self.model}")
        except Exception as e:
            raise ProviderError(f"Error pulling model {self.model}: {e}")

    async def generate_response(
        self,
        prompt: str,
        context: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        streaming: bool = False
    ) -> str:
        """Generate response using Ollama."""
        if not self.client:
            raise ProviderNotAvailableError("Ollama provider not initialized")

        # Build the full prompt with context
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
                # Non-streaming request
                request_data = {
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }

                response = await self.client.post(
                    f"{self.base_url}/api/generate",
                    json=request_data,
                    timeout=120.0
                )
                if response.status_code != 200:
                    raise ProviderError(f"Ollama request failed with status {response.status_code}")

                data = response.json()
                return data.get('response', '')

        except asyncio.TimeoutError:
            raise ProviderError("Ollama request timed out")
        except Exception as e:
            self.logger.error(f"Ollama API error: {e}")
            raise ProviderError(f"Ollama request failed: {e}")

    async def stream_response(
        self,
        prompt: str,
        context: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream response from Ollama."""
        if not self.client:
            raise ProviderNotAvailableError("Ollama provider not initialized")

        # Build the full prompt with context
        full_prompt = prompt
        if context:
            full_prompt = f"You are a helpful AI assistant analyzing a codebase. Here's the relevant context:\n\n{context}\n\nUser question: {prompt}"

        try:
            request_data = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=120.0
            ) as response:
                if response.status_code != 200:
                    raise ProviderError(f"Ollama streaming request failed with status {response.status_code}")

                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue

        except asyncio.TimeoutError:
            raise ProviderError("Ollama streaming request timed out")
        except Exception as e:
            self.logger.error(f"Ollama streaming error: {e}")
            raise ProviderError(f"Ollama streaming failed: {e}")

    async def check_health(self) -> bool:
        """Check Ollama service health."""
        if not self.client:
            return False

        try:
            await self._test_connection()
            return True
        except Exception as e:
            self.logger.warning(f"Ollama health check failed: {e}")
            return False

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens for Ollama models."""
        # Rough estimation: ~4 characters per token (similar to other models)
        return len(text) // 4

    async def get_available_models(self) -> list:
        """Get available Ollama models."""
        if not self.client:
            return []

        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            self.logger.warning(f"Failed to get available models: {e}")

        return []

    def get_common_models(self) -> list:
        """Get list of common Ollama models."""
        return [
            "llama2",
            "llama2:7b",
            "llama2:13b",
            "codellama",
            "codellama:7b",
            "mistral",
            "neural-chat",
            "starling-lm"
        ]

    def set_model(self, model: str) -> None:
        """Set the Ollama model to use."""
        self.model = model
        self.config['model'] = model
        self.logger.info(f"Ollama model changed to: {model}")

    def get_current_model(self) -> str:
        """Get currently selected model."""
        return self.model

    def set_base_url(self, url: str) -> None:
        """Set the Ollama server URL."""
        self.base_url = url
        self.config['host'] = url
        self.logger.info(f"Ollama base URL changed to: {url}")

    async def close(self) -> None:
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None