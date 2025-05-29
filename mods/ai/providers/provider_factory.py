"""
AI Provider Factory for TaskHero AI.

Manages creation and configuration of AI providers.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from .base_provider import AIProvider, ProviderConfigError
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider
from .openrouter_provider import OpenRouterProvider
from .deepseek_provider import DeepSeekProvider


class ProviderType(Enum):
    """Available AI provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    DEEPSEEK = "deepseek"


class ProviderFactory:
    """Factory for creating and managing AI providers."""

    def __init__(self, environment_manager=None):
        """Initialize the provider factory."""
        self.logger = logging.getLogger("ProviderFactory")
        self.environment_manager = environment_manager
        self._providers: Dict[str, AIProvider] = {}
        self._default_configs = self._load_default_configs()

    def _load_default_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load default configurations for each provider."""
        # Helper function to get environment variable
        def get_env(key: str, default: str = '') -> str:
            if self.environment_manager:
                return self.environment_manager.get_env_var(key, default)
            return os.getenv(key, default)

        return {
            ProviderType.OPENAI.value: {
                'api_key': get_env('OPENAI_API_KEY'),
                'model': get_env('OPENAI_MODEL', 'gpt-4'),
                'max_tokens': int(get_env('OPENAI_MAX_TOKENS', '4000')),
                'temperature': float(get_env('OPENAI_TEMPERATURE', '0.7')),
                'top_p': float(get_env('OPENAI_TOP_P', '1.0')),
                'frequency_penalty': float(get_env('OPENAI_FREQUENCY_PENALTY', '0.0')),
                'presence_penalty': float(get_env('OPENAI_PRESENCE_PENALTY', '0.0'))
            },
            ProviderType.ANTHROPIC.value: {
                'api_key': get_env('ANTHROPIC_API_KEY'),
                'model': get_env('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
                'max_tokens': int(get_env('ANTHROPIC_MAX_TOKENS', '4000')),
                'temperature': float(get_env('ANTHROPIC_TEMPERATURE', '0.7')),
                'top_p': float(get_env('ANTHROPIC_TOP_P', '1.0')),
                'top_k': int(get_env('ANTHROPIC_TOP_K', '40'))
            },
            ProviderType.OLLAMA.value: {
                'host': get_env('OLLAMA_HOST', 'http://localhost:11434'),
                'model': get_env('AI_TASK_MODEL', get_env('OLLAMA_MODEL', 'llama2')),
                'max_tokens': int(get_env('OLLAMA_MAX_TOKENS', '4000')),
                'temperature': float(get_env('OLLAMA_TEMPERATURE', '0.7')),
                'top_p': float(get_env('OLLAMA_TOP_P', '0.95')),
                'top_k': int(get_env('OLLAMA_TOP_K', '40'))
            },
            ProviderType.OPENROUTER.value: {
                'api_key': get_env('OPENROUTER_API_KEY'),
                'model': get_env('OPENROUTER_MODEL', 'openai/gpt-4'),
                'max_tokens': int(get_env('OPENROUTER_MAX_TOKENS', '4000')),
                'temperature': float(get_env('OPENROUTER_TEMPERATURE', '0.7')),
                'top_p': float(get_env('OPENROUTER_TOP_P', '1.0')),
                'http_referer': get_env('OPENROUTER_HTTP_REFERER', 'https://taskhero-ai.com'),
                'x_title': get_env('OPENROUTER_X_TITLE', 'TaskHeroAI')
            },
            ProviderType.DEEPSEEK.value: {
                'api_key': get_env('DEEPSEEK_API_KEY'),
                'model': get_env('DEEPSEEK_MODEL', 'deepseek-chat'),
                'max_tokens': int(get_env('DEEPSEEK_MAX_TOKENS', '4000')),
                'temperature': float(get_env('DEEPSEEK_TEMPERATURE', '0.7')),
                'top_p': float(get_env('DEEPSEEK_TOP_P', '1.0'))
            }
        }

    async def create_provider(
        self,
        provider_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> AIProvider:
        """
        Create an AI provider instance.

        Args:
            provider_type: Type of provider (openai, anthropic, ollama)
            config: Optional custom configuration

        Returns:
            Initialized AI provider

        Raises:
            ProviderConfigError: If provider type is invalid or config is missing
        """
        provider_type = provider_type.lower()

        if provider_type not in [pt.value for pt in ProviderType]:
            raise ProviderConfigError(f"Unknown provider type: {provider_type}")

        # Merge default config with custom config
        provider_config = self._default_configs[provider_type].copy()
        if config:
            provider_config.update(config)

        # Create provider instance
        try:
            if provider_type == ProviderType.OPENAI.value:
                provider = OpenAIProvider(provider_config)
            elif provider_type == ProviderType.ANTHROPIC.value:
                provider = AnthropicProvider(provider_config)
            elif provider_type == ProviderType.OLLAMA.value:
                provider = OllamaProvider(provider_config)
            elif provider_type == ProviderType.OPENROUTER.value:
                provider = OpenRouterProvider(provider_config)
            elif provider_type == ProviderType.DEEPSEEK.value:
                provider = DeepSeekProvider(provider_config)
            else:
                raise ProviderConfigError(f"Provider creation not implemented: {provider_type}")

            # Initialize the provider
            if await provider.initialize():
                self._providers[provider_type] = provider
                self.logger.info(f"Successfully created {provider_type} provider")
                return provider
            else:
                raise ProviderConfigError(f"Failed to initialize {provider_type} provider")

        except Exception as e:
            self.logger.error(f"Error creating {provider_type} provider: {e}")
            raise ProviderConfigError(f"Provider creation failed: {e}")

    async def get_provider(self, provider_type: str) -> Optional[AIProvider]:
        """
        Get an existing provider instance.

        Args:
            provider_type: Type of provider

        Returns:
            Provider instance if exists and healthy, None otherwise
        """
        provider_type = provider_type.lower()
        provider = self._providers.get(provider_type)

        if provider and await provider.check_health():
            return provider

        return None

    async def get_or_create_provider(
        self,
        provider_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> AIProvider:
        """
        Get existing provider or create new one.

        Args:
            provider_type: Type of provider
            config: Optional custom configuration

        Returns:
            AI provider instance
        """
        provider = await self.get_provider(provider_type)
        if provider:
            return provider

        return await self.create_provider(provider_type, config)

    async def get_available_providers(self) -> List[str]:
        """
        Get list of available providers based on configuration.

        Returns:
            List of available provider names
        """
        available = []

        # Check OpenAI
        if self._default_configs[ProviderType.OPENAI.value]['api_key']:
            available.append(ProviderType.OPENAI.value)

        # Check Anthropic
        if self._default_configs[ProviderType.ANTHROPIC.value]['api_key']:
            available.append(ProviderType.ANTHROPIC.value)

        # Check OpenRouter
        if self._default_configs[ProviderType.OPENROUTER.value]['api_key']:
            available.append(ProviderType.OPENROUTER.value)

        # Check DeepSeek
        if self._default_configs[ProviderType.DEEPSEEK.value]['api_key']:
            available.append(ProviderType.DEEPSEEK.value)

        # Check Ollama (always available if server is running)
        available.append(ProviderType.OLLAMA.value)

        return available

    async def get_best_available_provider(self) -> Optional[str]:
        """
        Get the best available provider based on environment configuration.

        Uses AI_PROVIDER_FALLBACK_CHAIN from environment variables to determine priority.
        Falls back to default order if not configured.

        Returns:
            Best available provider name or None
        """
        # Get fallback chain from environment variables
        def get_env(key: str, default: str = '') -> str:
            if self.environment_manager:
                return self.environment_manager.get_env_var(key, default)
            return os.getenv(key, default)

        fallback_chain = get_env('AI_PROVIDER_FALLBACK_CHAIN', '')
        if fallback_chain:
            priority_order = [provider.strip() for provider in fallback_chain.split(',')]
            self.logger.info(f"Using configured fallback chain: {priority_order}")
        else:
            # Default fallback order (still configurable via environment)
            priority_order = [
                ProviderType.DEEPSEEK.value,  # Prefer DeepSeek first as it's often configured
                ProviderType.OPENAI.value,
                ProviderType.ANTHROPIC.value,
                ProviderType.OPENROUTER.value,
                ProviderType.OLLAMA.value
            ]
            self.logger.info(f"Using default fallback chain: {priority_order}")

        available = await self.get_available_providers()
        self.logger.debug(f"Available providers: {available}")

        for provider_type in priority_order:
            if provider_type in available:
                # Try to create/test the provider
                try:
                    self.logger.debug(f"Testing provider: {provider_type}")
                    provider = await self.get_or_create_provider(provider_type)
                    if provider and await provider.check_health():
                        self.logger.info(f"✅ Selected working provider: {provider_type}")
                        return provider_type
                    else:
                        self.logger.warning(f"❌ Provider {provider_type} failed health check")
                except Exception as e:
                    self.logger.warning(f"❌ Provider {provider_type} failed initialization: {e}")
                    continue

        self.logger.error("❌ No working providers found in fallback chain")
        return None

    def get_provider_config(self, provider_type: str) -> Dict[str, Any]:
        """
        Get configuration for a provider type.

        Args:
            provider_type: Type of provider

        Returns:
            Provider configuration
        """
        provider_type = provider_type.lower()
        return self._default_configs.get(provider_type, {})

    def update_provider_config(
        self,
        provider_type: str,
        config: Dict[str, Any]
    ) -> None:
        """
        Update configuration for a provider type.

        Args:
            provider_type: Type of provider
            config: New configuration values
        """
        provider_type = provider_type.lower()
        if provider_type in self._default_configs:
            self._default_configs[provider_type].update(config)

            # Update existing provider if any
            if provider_type in self._providers:
                self._providers[provider_type].update_config(config)

            self.logger.info(f"Updated configuration for {provider_type} provider")

    async def close_all_providers(self) -> None:
        """Close all provider connections."""
        for provider_type, provider in self._providers.items():
            try:
                if hasattr(provider, 'close'):
                    await provider.close()
                self.logger.info(f"Closed {provider_type} provider")
            except Exception as e:
                self.logger.warning(f"Error closing {provider_type} provider: {e}")

        self._providers.clear()

    def list_providers(self) -> List[str]:
        """List all provider types."""
        return [pt.value for pt in ProviderType]

    def get_provider_info(self, provider_type: str) -> Dict[str, Any]:
        """
        Get information about a provider type.

        Args:
            provider_type: Type of provider

        Returns:
            Provider information
        """
        info = {
            ProviderType.OPENAI.value: {
                'name': 'OpenAI GPT',
                'description': 'OpenAI GPT models (GPT-4, GPT-3.5)',
                'requires_api_key': True,
                'supports_streaming': True,
                'cost': 'Pay per token',
                'models': ['gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo']
            },
            ProviderType.ANTHROPIC.value: {
                'name': 'Anthropic Claude',
                'description': 'Anthropic Claude models (Claude-3)',
                'requires_api_key': True,
                'supports_streaming': True,
                'cost': 'Pay per token',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
            },
            ProviderType.OLLAMA.value: {
                'name': 'Ollama Local',
                'description': 'Local AI models via Ollama',
                'requires_api_key': False,
                'supports_streaming': True,
                'cost': 'Free (local)',
                'models': ['llama2', 'codellama', 'mistral', 'neural-chat']
            },
            ProviderType.OPENROUTER.value: {
                'name': 'OpenRouter',
                'description': 'OpenRouter provider',
                'requires_api_key': True,
                'supports_streaming': True,
                'cost': 'Pay per token',
                'models': ['openai/gpt-4']
            },
            ProviderType.DEEPSEEK.value: {
                'name': 'DeepSeek',
                'description': 'DeepSeek AI models (DeepSeek-V3, DeepSeek-R1)',
                'requires_api_key': True,
                'supports_streaming': True,
                'cost': 'Pay per token',
                'models': ['deepseek-chat', 'deepseek-reasoner']
            }
        }

        return info.get(provider_type.lower(), {})

    async def test_all_providers(self) -> Dict[str, bool]:
        """
        Test all available providers.

        Returns:
            Dict mapping provider names to health status
        """
        results = {}
        available = await self.get_available_providers()

        for provider_type in available:
            try:
                provider = await self.get_or_create_provider(provider_type)
                results[provider_type] = await provider.check_health()
            except Exception as e:
                self.logger.warning(f"Failed to test {provider_type}: {e}")
                results[provider_type] = False

        return results