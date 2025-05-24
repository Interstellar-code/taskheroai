"""
Base AI Provider class for TaskHero AI.

Defines the interface that all AI providers must implement.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import logging


class AIProvider(ABC):
    """Base class for AI providers."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """
        Initialize the AI provider.
        
        Args:
            name: Provider name
            config: Provider configuration
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"AIProvider.{name}")
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the provider.
        
        Returns:
            True if initialization successful
        """
        try:
            self._initialized = await self._perform_initialization()
            return self._initialized
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name} provider: {e}")
            return False
    
    @abstractmethod
    async def _perform_initialization(self) -> bool:
        """Perform provider-specific initialization."""
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        context: str = "", 
        max_tokens: int = 4000,
        temperature: float = 0.7,
        streaming: bool = False
    ) -> str:
        """
        Generate AI response.
        
        Args:
            prompt: The user prompt
            context: Additional context information
            max_tokens: Maximum tokens to generate
            temperature: Response randomness (0.0-1.0)
            streaming: Whether to use streaming mode
            
        Returns:
            Generated response text
        """
        pass
    
    @abstractmethod
    async def stream_response(
        self,
        prompt: str,
        context: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ):
        """
        Stream AI response in chunks.
        
        Args:
            prompt: The user prompt
            context: Additional context information
            max_tokens: Maximum tokens to generate
            temperature: Response randomness (0.0-1.0)
            
        Yields:
            Response chunks as they become available
        """
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """
        Check if the provider is healthy and available.
        
        Returns:
            True if provider is available
        """
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Estimated token count
        """
        pass
    
    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        return self._initialized
    
    def get_name(self) -> str:
        """Get provider name."""
        return self.name
    
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration."""
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update provider configuration."""
        self.config.update(new_config)
        self.logger.info(f"Updated configuration for {self.name} provider")


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class ProviderNotAvailableError(ProviderError):
    """Raised when provider is not available."""
    pass


class ProviderConfigError(ProviderError):
    """Raised when provider configuration is invalid."""
    pass


class ProviderAuthError(ProviderError):
    """Raised when provider authentication fails."""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""
    pass 