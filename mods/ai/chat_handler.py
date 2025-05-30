"""
Chat Handler for TaskHero AI.

Handles AI chat functionality and conversation management.
Enhanced with real AI provider integration for Task 15.
"""

import asyncio
import os
from typing import Any, Dict, List, Tuple, Optional

from ..core import BaseComponent
from .providers.provider_factory import ProviderFactory
from .context_manager import CodebaseContextManager


class ChatHandler(BaseComponent):
    """Handler for AI chat functionality with real AI integration."""

    def __init__(self, indexer=None, file_selector=None, project_info=None, environment_manager=None):
        """Initialize the chat handler."""
        super().__init__("ChatHandler")
        self.indexer = indexer
        self.file_selector = file_selector
        self.project_info = project_info or {}
        self.environment_manager = environment_manager
        self.chat_history: List[Dict[str, str]] = []

        # AI provider components
        self.provider_factory = ProviderFactory(environment_manager)
        self.context_manager = CodebaseContextManager(indexer)
        self.current_provider = None

        # Configuration - use environment manager if available, fallback to os.getenv
        if self.environment_manager:
            self.preferred_provider = self.environment_manager.get_env_var('AI_CHAT_PROVIDER', 'deepseek')
            self.streaming_enabled = self.environment_manager.get_env_var('CHAT_STREAMING_ENABLED', 'true').lower() == 'true'
            self.max_context_tokens = int(self.environment_manager.get_env_var('CHAT_MAX_CONTEXT_TOKENS', '8000'))
        else:
            self.preferred_provider = os.getenv('AI_CHAT_PROVIDER', 'deepseek')  # Default to DeepSeek
            self.streaming_enabled = os.getenv('CHAT_STREAMING_ENABLED', 'true').lower() == 'true'
            self.max_context_tokens = int(os.getenv('CHAT_MAX_CONTEXT_TOKENS', '8000'))

    def _perform_initialization(self) -> None:
        """Initialize the chat handler."""
        self.logger.info("Enhanced Chat Handler initialized with AI providers")

    async def initialize_ai_provider(self) -> bool:
        """Initialize the AI provider for chat."""
        try:
            self.logger.info(f"Attempting to initialize preferred provider: {self.preferred_provider}")

            # Try to get the preferred provider
            try:
                self.current_provider = await self.provider_factory.get_or_create_provider(
                    self.preferred_provider
                )

                if self.current_provider:
                    # Test health check
                    health_ok = await self.current_provider.check_health()
                    if health_ok:
                        model_name = getattr(self.current_provider, 'model', 'Unknown')
                        self.logger.info(f"✅ Successfully initialized preferred AI provider: {self.current_provider.get_name()} ({model_name})")
                        return True
                    else:
                        self.logger.warning(f"❌ Preferred provider {self.preferred_provider} failed health check")
                        self.current_provider = None

            except Exception as e:
                self.logger.warning(f"❌ Failed to create preferred provider {self.preferred_provider}: {e}")
                self.current_provider = None

            # Fallback to best available provider
            self.logger.info("🔄 Attempting fallback to best available provider...")
            best_provider_type = await self.provider_factory.get_best_available_provider()
            if best_provider_type:
                self.logger.info(f"🔄 Fallback provider selected: {best_provider_type}")
                self.current_provider = await self.provider_factory.get_or_create_provider(
                    best_provider_type
                )
                model_name = getattr(self.current_provider, 'model', 'Unknown')
                self.logger.warning(f"⚠️ Using fallback AI provider: {self.current_provider.get_name()} ({model_name}) - preferred was: {self.preferred_provider}")
                return True

            self.logger.error("❌ No AI providers available")
            return False

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize AI provider: {e}")
            return False

    def set_project_info(self, project_info: Dict[str, Any]) -> None:
        """Set project information."""
        self.project_info = project_info
        self.logger.info("Project info updated in ChatHandler")

    async def process_query(self, query: str, max_chat_mode: bool = False, streaming: bool = False) -> Tuple[str, List[str]]:
        """
        Process a chat query with real AI integration.

        Args:
            query: User query
            max_chat_mode: Whether to use max chat mode (more context)
            streaming: Whether to use streaming mode

        Returns:
            Tuple of (response, relevant_files)
        """
        self.logger.info(f"Processing query: {query[:50]}...")

        try:
            # Initialize AI provider if not done
            if not self.current_provider:
                if not await self.initialize_ai_provider():
                    return self._fallback_response(query)

            # Get codebase context
            context_tokens = self.max_context_tokens * 2 if max_chat_mode else self.max_context_tokens
            context = await self.context_manager.get_relevant_context(query, max_tokens=context_tokens)

            # Format context for AI
            formatted_context = self.context_manager.format_context_for_ai(context)

            # Generate AI response with retry logic
            response = await self._generate_response_with_retry(
                query=query,
                context=formatted_context,
                streaming=streaming and self.streaming_enabled
            )

            # Enhance response quality and formatting
            enhanced_response = self._enhance_response_quality(response, query, context)

            # Add to history
            self.add_to_history("user", query)
            self.add_to_history("assistant", enhanced_response)

            return enhanced_response, context.relevant_files

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return self._fallback_response(query, error=str(e))

    async def _generate_response_with_retry(self, query: str, context: str, streaming: bool = False) -> str:
        """Generate response with retry logic and provider fallback."""
        from .providers.base_provider import ProviderError, ProviderAuthError, ProviderRateLimitError

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                if not self.current_provider:
                    raise ProviderError("No provider available")

                self.logger.debug(f"Attempting to generate response with {self.current_provider.get_name()}")

                response = await self.current_provider.generate_response(
                    prompt=query,
                    context=context,
                    streaming=streaming
                )

                self.logger.debug(f"Received response of length: {len(response) if response else 0}")

                if response and response.strip():
                    return response
                else:
                    raise ProviderError("Empty response from provider")

            except (ProviderAuthError, ProviderRateLimitError) as e:
                self.logger.warning(f"Provider {self.current_provider.get_name()} failed: {e}")
                # Try fallback provider
                if await self._try_fallback_provider():
                    retry_count += 1
                    continue
                else:
                    raise ProviderError(f"All providers failed: {e}")

            except ProviderError as e:
                self.logger.warning(f"Provider error on attempt {retry_count + 1}: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    # Try fallback provider as last resort
                    if await self._try_fallback_provider():
                        retry_count = 0  # Reset retry count for new provider
                        continue
                    else:
                        raise e

            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {retry_count + 1}: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    raise ProviderError(f"Failed after {max_retries} attempts: {e}")

        raise ProviderError("Failed to generate response after all retries")

    async def _try_fallback_provider(self) -> bool:
        """Try to switch to a fallback provider."""
        try:
            # Get best available provider (excluding current one)
            current_provider_name = self.current_provider.get_name().lower() if self.current_provider else ""
            best_provider = await self.provider_factory.get_best_available_provider()

            if best_provider and best_provider.lower() != current_provider_name:
                self.logger.info(f"Switching to fallback provider: {best_provider}")
                self.current_provider = await self.provider_factory.get_or_create_provider(best_provider)
                return self.current_provider is not None

            return False

        except Exception as e:
            self.logger.error(f"Failed to switch to fallback provider: {e}")
            return False

    def _fallback_response(self, query: str, error: str = None) -> Tuple[str, List[str]]:
        """Generate fallback response when AI is not available."""
        if error:
            response = f"I apologize, but I encountered an error processing your question: {error}\n\n"
        else:
            response = "I apologize, but AI chat is currently not available. "

        response += "This could be due to:\n"
        response += "• Missing API keys for AI providers\n"
        response += "• Network connectivity issues\n"
        response += "• Service unavailability\n\n"
        response += "Please check your configuration and try again."

        # Add to history
        self.add_to_history("user", query)
        self.add_to_history("assistant", response)

        return response, []

    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to chat history."""
        self.chat_history.append({"role": role, "content": content})
        self.logger.debug(f"Added {role} message to history")

    def get_chat_history(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent chat history."""
        return self.chat_history[-max_messages:] if max_messages > 0 else self.chat_history

    def clear_history(self) -> None:
        """Clear chat history."""
        self.chat_history.clear()
        self.logger.info("Chat history cleared")

    def set_provider(self, provider_type: str) -> None:
        """Set the preferred AI provider."""
        self.preferred_provider = provider_type
        self.current_provider = None  # Will reinitialize on next query
        self.logger.info(f"AI provider changed to: {provider_type}")

    async def get_available_providers(self) -> List[str]:
        """Get list of available AI providers."""
        return await self.provider_factory.get_available_providers()

    async def test_providers(self) -> Dict[str, bool]:
        """Test all available providers."""
        return await self.provider_factory.test_all_providers()

    def get_current_provider_info(self) -> Dict[str, str]:
        """Get information about the currently active provider."""
        if not self.current_provider:
            return {
                "provider": "None",
                "model": "None",
                "status": "Not initialized"
            }

        model_name = getattr(self.current_provider, 'model', 'Unknown')
        provider_name = self.current_provider.get_name()

        # Check if using fallback
        is_fallback = provider_name.lower() != self.preferred_provider.lower()
        status = "Fallback" if is_fallback else "Preferred"

        return {
            "provider": provider_name,
            "model": model_name,
            "status": status,
            "preferred": self.preferred_provider
        }

    async def close(self) -> None:
        """Close AI provider connections."""
        await self.provider_factory.close_all_providers()
        self.current_provider = None
        self.logger.info("ChatHandler connections closed")

    def _enhance_response_quality(self, response: str, query: str, context) -> str:
        """Enhance response quality with validation and formatting improvements."""
        try:
            # Validate response quality
            quality_score = self._validate_response_quality(response, query, context)

            # Format response with structure
            formatted_response = self._format_response_structure(response)

            # Add follow-up suggestions if appropriate
            enhanced_response = self._add_follow_up_suggestions(formatted_response, query, context)

            # Add quality metadata for debugging
            if quality_score < 0.7:  # If quality is low, add a note
                self.logger.warning(f"Response quality score: {quality_score:.2f} for query: {query[:50]}...")

            return enhanced_response

        except Exception as e:
            self.logger.warning(f"Error enhancing response quality: {e}")
            return response  # Return original response if enhancement fails

    def _validate_response_quality(self, response: str, query: str, context) -> float:
        """Validate response quality and return a score between 0 and 1."""
        try:
            score = 0.0

            # Basic length check (not too short, not too long)
            if 100 <= len(response) <= 5000:
                score += 0.2
            elif len(response) > 50:
                score += 0.1

            # Check for specific mentions of project features
            project_terms = ['taskhero', 'task', 'ai', 'chat', 'dashboard', 'indexing', 'file']
            mentions = sum(1 for term in project_terms if term.lower() in response.lower())
            score += min(mentions * 0.1, 0.3)

            # Check for structured content (headings, lists, etc.)
            if any(marker in response for marker in ['##', '###', '•', '-', '1.', '2.']):
                score += 0.2

            # Check for code examples or technical details
            if any(marker in response for marker in ['```', '`', 'function', 'class', 'method']):
                score += 0.1

            # Check for actionable information
            action_words = ['can', 'allows', 'enables', 'provides', 'supports', 'offers']
            if any(word in response.lower() for word in action_words):
                score += 0.1

            # Check if response addresses the query
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            overlap = len(query_words.intersection(response_words))
            if overlap > 0:
                score += min(overlap * 0.02, 0.1)

            return min(score, 1.0)

        except Exception as e:
            self.logger.debug(f"Error validating response quality: {e}")
            return 0.5  # Default neutral score

    def _format_response_structure(self, response: str) -> str:
        """Format response with better structure and readability."""
        try:
            # If response is already well-structured, return as-is
            if any(marker in response for marker in ['##', '###', '**', '•']):
                return response

            # Split response into paragraphs
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]

            if len(paragraphs) <= 1:
                return response  # Single paragraph, no need to restructure

            # Add structure to multi-paragraph responses
            structured_parts = []

            # First paragraph as introduction
            if paragraphs:
                structured_parts.append(paragraphs[0])

            # Remaining paragraphs as sections
            if len(paragraphs) > 1:
                structured_parts.append("\n## Key Points\n")
                for i, paragraph in enumerate(paragraphs[1:], 1):
                    structured_parts.append(f"**{i}.** {paragraph}")

            return '\n\n'.join(structured_parts)

        except Exception as e:
            self.logger.debug(f"Error formatting response structure: {e}")
            return response

    def _add_follow_up_suggestions(self, response: str, query: str, context) -> str:
        """Add relevant follow-up suggestions based on query and context."""
        try:
            suggestions = []
            query_lower = query.lower()

            # Suggest related queries based on current query
            if 'functionality' in query_lower or 'features' in query_lower:
                suggestions.extend([
                    "How do users typically interact with this system?",
                    "What are the main workflows available?",
                    "How is the AI chat system implemented?"
                ])

            elif 'workflow' in query_lower or 'process' in query_lower:
                suggestions.extend([
                    "What are the technical implementation details?",
                    "How are the different components integrated?",
                    "What configuration options are available?"
                ])

            elif 'technical' in query_lower or 'implementation' in query_lower:
                suggestions.extend([
                    "What user features does this enable?",
                    "How do the components work together?",
                    "What are the main user workflows?"
                ])

            elif 'chat' in query_lower or 'ai' in query_lower:
                suggestions.extend([
                    "How does the context discovery system work?",
                    "What AI providers are supported?",
                    "How is the task management integrated?"
                ])

            # Add general suggestions if no specific ones match
            if not suggestions:
                suggestions = [
                    "What are the main features users can access?",
                    "How do the different components work together?",
                    "What are the key user workflows?"
                ]

            # Limit to 3 suggestions and format them
            if suggestions:
                follow_up_text = "\n\n---\n\n**💡 Related Questions You Might Ask:**\n"
                for i, suggestion in enumerate(suggestions[:3], 1):
                    follow_up_text += f"{i}. {suggestion}\n"

                return response + follow_up_text

            return response

        except Exception as e:
            self.logger.debug(f"Error adding follow-up suggestions: {e}")
            return response