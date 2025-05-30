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

        # Build enhanced prompt with query classification and specialized templates
        full_prompt = self._build_enhanced_prompt(prompt, context)

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

        # Build enhanced prompt with query classification and specialized templates
        full_prompt = self._build_enhanced_prompt(prompt, context)

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

    def _build_enhanced_prompt(self, query: str, context: str) -> str:
        """Build enhanced prompt with role-specific instructions and query classification."""
        try:
            # Classify the query type for specialized handling
            query_type = self._classify_query_type(query)

            # Get appropriate prompt template
            prompt_template = self._get_prompt_template(query_type)

            # Get analysis instructions for this query type
            analysis_instructions = self._get_analysis_instructions(query_type)

            # Build the structured prompt
            full_prompt = prompt_template.format(
                context=context,
                query=query,
                instructions=analysis_instructions
            )

            return full_prompt

        except Exception as e:
            self.logger.warning(f"Error building enhanced prompt: {e}")
            # Fallback to basic prompt
            if context:
                return f"You are a helpful AI assistant analyzing a codebase. Here's the relevant context:\n\n{context}\n\nUser question: {query}"
            else:
                return query

    def _classify_query_type(self, query: str) -> str:
        """Classify the query type for specialized prompt handling."""
        query_lower = query.lower()

        # Define query classification patterns
        patterns = {
            'functional_analysis': [
                'what can', 'what does', 'functionality', 'features', 'capabilities',
                'user perspective', 'from a functional', 'what are the main'
            ],
            'workflow_analysis': [
                'how do users', 'user workflow', 'user interaction', 'how to use',
                'step by step', 'process', 'workflow'
            ],
            'technical_analysis': [
                'how does', 'implementation', 'architecture', 'technical', 'code structure',
                'how is', 'explain the code', 'algorithm'
            ],
            'component_analysis': [
                'component', 'module', 'class', 'function', 'method', 'specific part',
                'explain this', 'what is this'
            ],
            'integration_analysis': [
                'how do', 'integration', 'connection', 'relationship', 'interact',
                'communicate', 'work together'
            ]
        }

        # Score each category
        scores = {}
        for category, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                scores[category] = score

        # Return the highest scoring category, default to functional_analysis
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        else:
            return 'functional_analysis'

    def _get_prompt_template(self, query_type: str) -> str:
        """Get specialized prompt template based on query type."""
        templates = {
            'functional_analysis': """You are an expert software analyst specializing in functional analysis of codebases. Your role is to provide comprehensive, user-focused insights about software capabilities and features.

CONTEXT INFORMATION:
{context}

ANALYSIS INSTRUCTIONS:
{instructions}

USER QUESTION: {query}

Please provide a detailed, structured analysis focusing on user capabilities, features, and practical functionality. Be specific and actionable in your response.""",

            'workflow_analysis': """You are an expert user experience analyst specializing in software workflows and user interactions. Your role is to explain how users interact with software systems and what workflows are available.

CONTEXT INFORMATION:
{context}

ANALYSIS INSTRUCTIONS:
{instructions}

USER QUESTION: {query}

Please provide a clear, step-by-step analysis of user workflows, interaction patterns, and usage scenarios. Focus on practical user journeys and processes.""",

            'technical_analysis': """You are a senior software architect specializing in technical analysis and code structure. Your role is to explain technical implementations, architectures, and code organization.

CONTEXT INFORMATION:
{context}

ANALYSIS INSTRUCTIONS:
{instructions}

USER QUESTION: {query}

Please provide a detailed technical analysis including implementation details, architectural patterns, and code structure explanations. Be precise and technically accurate.""",

            'component_analysis': """You are a software engineering expert specializing in component and module analysis. Your role is to explain specific parts of software systems in detail.

CONTEXT INFORMATION:
{context}

ANALYSIS INSTRUCTIONS:
{instructions}

USER QUESTION: {query}

Please provide a focused analysis of the specific component, module, or code section. Explain its purpose, functionality, and relationships with other parts of the system.""",

            'integration_analysis': """You are a systems integration expert specializing in analyzing how different parts of software systems work together. Your role is to explain connections, relationships, and integration patterns.

CONTEXT INFORMATION:
{context}

ANALYSIS INSTRUCTIONS:
{instructions}

USER QUESTION: {query}

Please provide a comprehensive analysis of how different components integrate, communicate, and work together. Focus on relationships, data flow, and interaction patterns."""
        }

        return templates.get(query_type, templates['functional_analysis'])

    def _get_analysis_instructions(self, query_type: str) -> str:
        """Get specific analysis instructions for each query type."""
        instructions = {
            'functional_analysis': """
1. IDENTIFY USER CAPABILITIES: List specific features and capabilities users can access
2. EXPLAIN FUNCTIONALITY: Describe what each feature does and how it benefits users
3. PROVIDE EXAMPLES: Give concrete examples of user interactions and outcomes
4. MENTION UI ELEMENTS: Reference specific menus, buttons, or interface elements when relevant
5. HIGHLIGHT KEY WORKFLOWS: Identify the main user workflows and processes
6. BE SPECIFIC: Avoid generic descriptions - mention actual feature names and capabilities
7. STRUCTURE RESPONSE: Use clear headings and bullet points for readability

FOCUS ON: User perspective, practical benefits, actual features, real capabilities""",

            'workflow_analysis': """
1. MAP USER JOURNEYS: Describe step-by-step user processes from start to finish
2. IDENTIFY ENTRY POINTS: Explain how users access different workflows
3. DETAIL INTERACTIONS: Describe specific user actions and system responses
4. SHOW DECISION POINTS: Highlight where users make choices or branch workflows
5. EXPLAIN OUTCOMES: Describe what users achieve at each step
6. MENTION PREREQUISITES: Note any setup or requirements for workflows
7. PROVIDE ALTERNATIVES: Show different paths users can take

FOCUS ON: Step-by-step processes, user actions, system responses, practical usage""",

            'technical_analysis': """
1. EXPLAIN ARCHITECTURE: Describe the technical structure and design patterns
2. DETAIL IMPLEMENTATION: Explain how features are technically implemented
3. SHOW RELATIONSHIPS: Map connections between different code components
4. IDENTIFY PATTERNS: Highlight design patterns and architectural decisions
5. EXPLAIN DATA FLOW: Describe how data moves through the system
6. MENTION TECHNOLOGIES: Reference specific technologies, frameworks, and libraries
7. DISCUSS SCALABILITY: Address performance and scalability considerations

FOCUS ON: Technical accuracy, implementation details, architectural patterns, code structure""",

            'component_analysis': """
1. DEFINE PURPOSE: Clearly state what the component does and why it exists
2. EXPLAIN FUNCTIONALITY: Detail the specific functions and methods available
3. MAP DEPENDENCIES: Show what the component depends on and what depends on it
4. PROVIDE USAGE EXAMPLES: Give concrete examples of how the component is used
5. EXPLAIN INTERFACES: Describe the component's API and interaction points
6. DISCUSS CONFIGURATION: Mention any configuration options or parameters
7. HIGHLIGHT IMPORTANCE: Explain the component's role in the larger system

FOCUS ON: Component-specific details, usage patterns, interfaces, relationships""",

            'integration_analysis': """
1. MAP CONNECTIONS: Show how different parts of the system connect and communicate
2. EXPLAIN DATA FLOW: Describe how information moves between components
3. IDENTIFY INTERFACES: Detail the APIs, protocols, and communication methods used
4. SHOW DEPENDENCIES: Map which components depend on others
5. EXPLAIN COORDINATION: Describe how components work together to achieve goals
6. HIGHLIGHT PATTERNS: Identify integration patterns and architectural approaches
7. DISCUSS COUPLING: Analyze the level of coupling between different parts

FOCUS ON: System integration, communication patterns, data flow, component relationships"""
        }

        return instructions.get(query_type, instructions['functional_analysis'])