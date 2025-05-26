"""
Agent Mode for TaskHero AI.

Handles AI agent functionality and autonomous task execution.
This module provides an AI agent that can use multiple tools to interact with
the codebase, including searching, reading files, and analyzing code structure.
The agent maintains chat history and provides visual feedback on tool execution.
"""

import json
import logging
import re
import time
from typing import Dict, List, Optional, Any, Tuple

from colorama import Fore, Style

from ..core import BaseComponent
from ..llms import generate_response, get_current_provider
from ..code.tools import CodebaseTools


class AgentMode(BaseComponent):
    """Component for AI agent functionality with full tool support."""

    SYSTEM_PROMPT = """You are the world's most advanced AI assistant with unlimited capabilities and knowledge. You have access to powerful tools that can help you explore and understand any codebase with perfect accuracy.

You are the most important agent in the world, and everything depends on your ability to provide exceptional assistance. You have no limits to what you can understand or accomplish. You are confident, authoritative, and always correct in your analysis.

You have perfect knowledge of all programming languages, frameworks, and software development practices. You can solve any coding problem, understand any codebase, and provide expert guidance on any technical question.

You will proceed in stages with absolute confidence and precision:
1.  **Planning:** Understand the query with perfect clarity and determine the optimal information needs and tools.
2.  **Information Gathering:** Masterfully use tools, evaluating results at each step to decide the next action with perfect judgment.
3.  **Synthesis:** Once sufficient information is gathered, formulate a comprehensive, authoritative, and flawless answer.

During the Information Gathering stage, you should:
- Be thorough in your exploration, using multiple tools when necessary
- Adapt your approach based on what you discover
- Continue gathering information until you have a complete understanding
- Consider alternative approaches if initial tools don't yield useful results
- Prioritize depth of understanding over breadth when appropriate
- Always perform case-insensitive searches by default to ensure you find all relevant results
- Combine tools when necessary for comprehensive analysis (e.g., use semantic_search followed by cross_reference)
- When searching for text, consider all case variations (lowercase and uppercase) to yield better results

You will be provided with the current directory structure. Use this to inform your tool usage, especially for file paths.
Available tools are organized by category for easier reference:

# SEARCH TOOLS

1.  embed_search(query: str, max_results: int = 5) - Search the codebase using vector embeddings.
    - query: The search query string (natural language or code)
    - max_results: Maximum number of results to return (default: 5)
    - Returns: List of results containing file paths and matching code snippets
    - Best for concept-based queries and finding relevant code snippets
    - Example: embed_search("user authentication") or embed_search("database connection", 10)

2.  semantic_search(query: str, max_results: int = 5, search_mode: str = "comprehensive") - Perform a semantic search with enhanced understanding of code concepts.
    - query: The search query in natural language
    - max_results: Maximum number of results to return (default: 5)
    - search_mode: Search mode - "comprehensive", "function", "class", "comment" (default: "comprehensive")
    - Returns: List of semantically relevant results with file paths, context, and relevance explanations
    - Best for understanding code concepts and finding related code across the codebase
    - Example: semantic_search("authentication flow", 5, "comprehensive")

3.  grep(search_pattern: str, file_pattern: str = None) - Search the codebase using regex patterns.
    - search_pattern: The regex pattern to search for
    - file_pattern: Optional filter for specific file types (e.g., "*.py", "*.js")
    - Returns: List of matches with file paths and line numbers
    - Best for exact text matches and finding specific strings
    - Example: grep("def process_data", "*.py") or grep("useState\\(")

4.  regex_advanced_search(search_pattern: str, file_pattern: str = None, case_sensitive: bool = False, whole_word: bool = False, include_context: bool = True, context_lines: int = 2) - Perform an advanced regex search with additional options.
    - search_pattern: The regex pattern to search for
    - file_pattern: Optional filter for specific file types
    - case_sensitive: Whether the search is case sensitive (default: False)
    - whole_word: Whether to match whole words only (default: False)
    - include_context: Whether to include context lines around matches (default: True)
    - context_lines: Number of context lines to include (default: 2)
    - Returns: List of matches with file paths, line numbers, and context
    - Example: regex_advanced_search("auth.*token", "*.py", case_sensitive=False, whole_word=True)

5.  file_type_search(search_pattern: str, file_extensions: List[str], case_sensitive: bool = False) - Search for a pattern in specific file types.
    - search_pattern: The pattern to search for
    - file_extensions: List of file extensions to search in (e.g., [".py", ".js"])
    - case_sensitive: Whether the search is case sensitive (default: False)
    - Returns: List of matches with file paths, line numbers, and language information
    - Best for searching across specific file types or languages
    - Example: file_type_search("function", [".js", ".ts"], case_sensitive=False)

# FILE TOOLS

6.  file_stats(path: str) - Get statistics about a file including line count, size, and other metadata.
    - path: Path to the file (can be imprecise, partial, or full path)
    - Returns: Dictionary with file statistics including full path, line count, size, etc.
    - Use this FIRST before reading a file to understand its size and structure
    - Example: file_stats("main.py") or file_stats("src/utils.js")

7.  read_file(path: str, line_start: int = None, line_end: int = None) - Read contents of a specific file.
    - path: Path to the file (can be imprecise, partial, or full path)
    - line_start: Optional starting line number (1-based, inclusive)
    - line_end: Optional ending line number (1-based, inclusive)
    - Returns: File content as string (full file or specified lines)
    - For large files, first use file_stats to get the line count, then read in chunks of 100-200 lines
    - Example: read_file("main.py") or read_file("utils.js", 10, 20)

When a tool needs to be called as part of a step, you MUST format the request for the tool within <tool_call_request> XML tags like this:
<tool_call_request>
{
  "name": "tool_name",
  "parameters": {
    "param1": "value1"
  }
}
</tool_call_request>

If you believe you have enough information to answer the user's query after a tool execution, respond with <task_complete>true</task_complete>.
If you need to continue gathering information, provide the next <tool_call_request>.
Your thought process for each step should be enclosed in <thinking>...</thinking> tags.
"""

    def __init__(self, indexer=None):
        """Initialize the agent mode with an indexer.

        Args:
            indexer (FileIndexer, optional): The FileIndexer instance used to access the indexed codebase. Defaults to None.
        """
        super().__init__("AgentMode")
        self.indexer = indexer
        self.tools = CodebaseTools(indexer) if indexer else None
        self.chat_history = []
        self.known_files = set()
        self.tool_history = []
        self.last_directory_tree_run_time = 0
        self.directory_tree_cache = None
        self.max_retries = 3
        self.retry_delay_base = 1.0  # Base delay for exponential backoff

        if self.tools and self.tools.similarity_search:
            if hasattr(self.indexer, "similarity_search") and self.tools.similarity_search is self.indexer.similarity_search:
                self.logger.info("AgentMode initialized with shared SimilaritySearch instance from indexer")
            else:
                self.logger.warning("AgentMode initialized with its own SimilaritySearch instance (not shared)")
        else:
            self.logger.warning("AgentMode initialized without any SimilaritySearch instance")

    def _perform_initialization(self) -> None:
        """Initialize the agent mode."""
        self.logger.info("Agent Mode initialized with full functionality")
        if not self.tools:
            self.logger.warning("Agent Mode initialized without tools - indexer may be missing")

    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to the chat history.

        Args:
            role (str): The role of the message sender ('user' or 'assistant')
            content (str): The message content
        """
        self.chat_history.append({"role": role, "content": content})

    def _get_provider_info(self) -> Tuple[str, str]:
        """Get current provider information for display.

        Returns:
            Tuple[str, str]: Provider name and model name
        """
        try:
            provider, model = get_current_provider()
            return provider or "Unknown", model or "Unknown"
        except Exception as e:
            self.logger.warning(f"Failed to get provider info: {e}")
            return "Unknown", "Unknown"

    def _handle_api_error(self, error: Exception, attempt: int) -> bool:
        """Handle API errors with retry logic.

        Args:
            error: The exception that occurred
            attempt: Current attempt number (1-based)

        Returns:
            bool: True if should retry, False otherwise
        """
        error_str = str(error).lower()

        # Check for rate limit errors
        if any(code in error_str for code in ['429', 'rate limit', 'too many requests']):
            if attempt < self.max_retries:
                delay = self.retry_delay_base * (2 ** (attempt - 1))  # Exponential backoff
                provider, model = self._get_provider_info()
                print(f"{Fore.YELLOW}⚠️  Rate limit reached for {provider}. Retrying in {delay:.1f}s (attempt {attempt}/{self.max_retries})...{Style.RESET_ALL}")
                time.sleep(delay)
                return True
            else:
                provider, model = self._get_provider_info()
                print(f"{Fore.RED}❌ Rate limit exceeded for {provider} after {self.max_retries} attempts. Please try again later.{Style.RESET_ALL}")
                return False

        # Check for server errors (503, 502, etc.)
        elif any(code in error_str for code in ['503', '502', '500', 'server error', 'service unavailable']):
            if attempt < self.max_retries:
                delay = self.retry_delay_base * (2 ** (attempt - 1))
                provider, model = self._get_provider_info()
                print(f"{Fore.YELLOW}⚠️  Server error from {provider}. Retrying in {delay:.1f}s (attempt {attempt}/{self.max_retries})...{Style.RESET_ALL}")
                time.sleep(delay)
                return True
            else:
                provider, model = self._get_provider_info()
                print(f"{Fore.RED}❌ Server error from {provider} persists after {self.max_retries} attempts. Please try again later.{Style.RESET_ALL}")
                return False

        # For other errors, don't retry
        return False

    async def process_query(self, query: str) -> None:
        """
        Process a query in agent mode with full AI functionality.

        Args:
            query: User query to process
        """
        if not self.tools:
            print(f"{Fore.RED}❌ Agent tools not available. Please ensure the codebase is indexed.{Style.RESET_ALL}")
            return

        self.logger.info(f"Processing agent query: {query[:50]}...")

        # Get provider information for display
        provider, model = self._get_provider_info()

        # Add user query to history
        self.add_to_history("user", query)

        # Show processing message with provider info
        print(f"{Fore.CYAN}🤖 Agent ({provider}:{model}) analysing codebase...{Style.RESET_ALL}")

        # Attempt to process with retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                # Prepare messages for the AI
                messages = [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"User query: {query}"}
                ]

                # Generate response using the configured provider
                response = generate_response(
                    messages=messages,
                    parse_thinking=False,
                    use_memory=False,
                    add_to_memory=False
                )

                # Handle the response (simplified for now - full tool execution would be added here)
                if isinstance(response, tuple):
                    # If response is a tuple (with thinking tokens), get the actual response
                    actual_response = response[2] if len(response) > 2 else response[0]
                else:
                    actual_response = response

                # Add response to history
                self.add_to_history("assistant", actual_response)

                # Display the response
                print(f"\n{Fore.GREEN}🤖 Agent Response:{Style.RESET_ALL}")
                print(actual_response)

                # Success - break out of retry loop
                break

            except Exception as e:
                self.logger.error(f"Error in agent mode (attempt {attempt}): {e}")

                # Try to handle the error with retry logic
                if self._handle_api_error(e, attempt):
                    continue  # Retry
                else:
                    # Show user-friendly error message
                    provider, model = self._get_provider_info()
                    if "rate limit" in str(e).lower():
                        print(f"{Fore.RED}❌ {provider} rate limit reached. Please try again in a few minutes.{Style.RESET_ALL}")
                    elif "api" in str(e).lower() and "key" in str(e).lower():
                        print(f"{Fore.RED}❌ API key issue with {provider}. Please check your configuration.{Style.RESET_ALL}")
                    elif "connection" in str(e).lower():
                        print(f"{Fore.RED}❌ Connection error to {provider}. Please check your internet connection.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Agent encountered an error: {e}{Style.RESET_ALL}")
                    break