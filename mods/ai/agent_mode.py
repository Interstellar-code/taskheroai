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
import asyncio
from typing import Dict, List, Optional, Any, Tuple

from colorama import Fore, Style

from ..core import BaseComponent
from ..llms import get_current_provider
from ..code.tools import CodebaseTools
from .providers.provider_factory import ProviderFactory


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
- Combine tools when necessary for comprehensive analysis (e.g., use embed_search followed by read_file)
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

2.  directory_tree(max_depth: int = None) - Get directory structure and file listing.
    - max_depth: Optional maximum depth to display (default: None for full tree)
    - Returns: Dictionary with tree structure, file count, and directory count
    - Best for understanding project structure and finding files
    - Example: directory_tree() or directory_tree(2)

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

5.  find_functions(pattern: str, file_pattern: str = None) - Find function definitions matching a pattern.
    - pattern: The pattern to search for in function names
    - file_pattern: Optional filter for specific file types
    - Returns: List of function definitions with file paths, line numbers, and signatures
    - Best for finding specific functions or function patterns
    - Example: find_functions("process_data") or find_functions("auth", "*.py")

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
        self.provider_factory = ProviderFactory()
        self.current_provider = None

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

    async def _get_or_create_provider(self):
        """Get or create the AI provider instance."""
        if self.current_provider is None:
            try:
                # Get the best available provider
                provider_type = await self.provider_factory.get_best_available_provider()
                if provider_type:
                    self.current_provider = await self.provider_factory.get_or_create_provider(provider_type)
                    self.logger.info(f"Agent mode using provider: {provider_type}")
                else:
                    raise Exception("No working AI providers available")
            except Exception as e:
                self.logger.error(f"Failed to initialize AI provider: {e}")
                raise
        return self.current_provider

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
            if self.current_provider:
                provider_name = self.current_provider.name
                model_name = getattr(self.current_provider, 'model', 'Unknown')
                return provider_name, model_name
            else:
                # Fallback to old method
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
                # Get or create the AI provider
                provider = await self._get_or_create_provider()

                # Prepare the prompt
                full_prompt = f"{self.SYSTEM_PROMPT}\n\nUser query: {query}"

                # Generate response using the new provider system
                response = await provider.generate_response(
                    prompt=full_prompt,
                    max_tokens=4000,
                    temperature=0.7
                )

                # The new provider system returns a string directly
                actual_response = response

                # Check if the response contains tool calls and execute them
                if self._contains_tool_call(actual_response):
                    # Execute tools and get updated response
                    final_response = await self._process_tool_calls(actual_response, query)
                    actual_response = final_response

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

    def _contains_tool_call(self, response: str) -> bool:
        """Check if the response contains a tool call request."""
        return "<tool_call_request>" in response and "</tool_call_request>" in response

    def _extract_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract tool call from response."""
        import re
        pattern = r'<tool_call_request>\s*(\{.*?\})\s*</tool_call_request>'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                tool_call = json.loads(match.group(1))
                return tool_call
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse tool call JSON: {e}")
                return None
        return None

    async def _process_tool_calls(self, response: str, original_query: str) -> str:
        """Process tool calls in the response and return updated response."""
        if not self.tools:
            return response

        max_iterations = 5
        current_response = response

        for iteration in range(max_iterations):
            tool_call = self._extract_tool_call(current_response)
            if not tool_call:
                break

            # Execute the tool
            tool_result = self._execute_tool_call(tool_call)

            # Get next action from AI
            next_response = await self._get_next_action(original_query, tool_call, tool_result, current_response)

            # Check if AI wants to continue or is done
            if "<task_complete>true</task_complete>" in next_response:
                # Extract final answer
                final_answer = self._extract_final_answer(next_response)
                return final_answer if final_answer else next_response

            current_response = next_response

        return current_response

    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool call."""
        if not self.tools:
            return {"error": "No tools available"}

        tool_name = tool_call.get('name')
        parameters = tool_call.get('parameters', {})

        # Display tool execution
        print(f"\n{Fore.YELLOW}🔧 Executing: {tool_name}({parameters}){Style.RESET_ALL}")

        try:
            # Map tool calls to actual tool methods
            if tool_name == 'semantic_search':
                query = parameters.get('query', '')
                max_results = parameters.get('max_results', 10)
                search_mode = parameters.get('search_mode', 'comprehensive')
                # semantic_search doesn't exist, use embed_search instead
                return self.tools.embed_search(query, max_results)
            elif tool_name == 'embed_search':
                query = parameters.get('query', '')
                max_results = parameters.get('max_results', 10)
                return self.tools.embed_search(query, max_results)
            elif tool_name == 'grep':
                search_pattern = parameters.get('search_pattern', '')
                file_pattern = parameters.get('file_pattern')
                return self.tools.grep(search_pattern, file_pattern)
            elif tool_name == 'regex_advanced_search':
                search_pattern = parameters.get('search_pattern', '')
                file_pattern = parameters.get('file_pattern')
                case_sensitive = parameters.get('case_sensitive', False)
                whole_word = parameters.get('whole_word', False)
                include_context = parameters.get('include_context', True)
                context_lines = parameters.get('context_lines', 2)
                max_results = parameters.get('max_results', 100)
                return self.tools.regex_advanced_search(search_pattern, file_pattern, case_sensitive, whole_word, include_context, context_lines, max_results)
            elif tool_name == 'read_file':
                path = parameters.get('path', '')
                line_start = parameters.get('line_start')
                line_end = parameters.get('line_end')
                return self.tools.read_file(path, line_start, line_end)
            elif tool_name == 'file_stats':
                path = parameters.get('path', '')
                return self.tools.file_stats(path)
            elif tool_name == 'directory_tree':
                max_depth = parameters.get('max_depth')
                return self.tools.directory_tree(max_depth)
            elif tool_name == 'find_functions':
                pattern = parameters.get('pattern', '')
                file_pattern = parameters.get('file_pattern')
                return self.tools.find_functions(pattern, file_pattern)
            elif tool_name == 'find_classes':
                pattern = parameters.get('pattern', '')
                file_pattern = parameters.get('file_pattern')
                return self.tools.find_classes(pattern, file_pattern)
            elif tool_name == 'code_analysis':
                path = parameters.get('path', '')
                return self.tools.code_analysis(path)
            elif tool_name == 'get_project_description':
                return self.tools.get_project_description()
            elif tool_name == 'get_file_description':
                path = parameters.get('path', '')
                return self.tools.get_file_description(path)
            elif tool_name == 'get_file_metadata':
                path = parameters.get('path', '')
                return self.tools.get_file_metadata(path)
            elif tool_name == 'get_functions':
                file_path = parameters.get('file_path', '')
                return self.tools.get_functions(file_path)
            elif tool_name == 'get_classes':
                file_path = parameters.get('file_path', '')
                return self.tools.get_classes(file_path)
            elif tool_name == 'get_variables':
                file_path = parameters.get('file_path', '')
                return self.tools.get_variables(file_path)
            elif tool_name == 'get_imports':
                file_path = parameters.get('file_path', '')
                return self.tools.get_imports(file_path)
            elif tool_name == 'explain_code':
                path = parameters.get('path', '')
                line_start = parameters.get('line_start')
                line_end = parameters.get('line_end')
                return self.tools.explain_code(path, line_start, line_end)
            # Handle non-existent tools that AI might try to use
            elif tool_name == 'list_files':
                # Convert to directory_tree
                path = parameters.get('path', '.')
                recursive = parameters.get('recursive', True)
                max_depth = None if recursive else 1
                return self.tools.directory_tree(max_depth)
            elif tool_name == 'list_directory':
                # Convert to directory_tree
                path = parameters.get('path', '.')
                return self.tools.directory_tree(max_depth=1)
            elif tool_name == 'file_search':
                # Convert to embed_search
                query = parameters.get('query', '')
                max_results = parameters.get('max_results', 10)
                return self.tools.embed_search(query, max_results)
            else:
                return {"error": f"Unknown tool: {tool_name}. Available tools: embed_search, grep, regex_advanced_search, read_file, file_stats, directory_tree, find_functions, find_classes, code_analysis, get_project_description, get_file_description, get_file_metadata, get_functions, get_classes, get_variables, get_imports, explain_code"}

        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}

    async def _get_next_action(self, original_query: str, tool_call: Dict[str, Any], tool_result: Dict[str, Any], previous_response: str) -> str:
        """Get the next action from the AI after tool execution."""
        try:
            provider = await self._get_or_create_provider()

            prompt = f"""Based on the tool execution result, determine your next action.

Original Query: {original_query}

Previous Response: {previous_response}

Tool Call: {json.dumps(tool_call)}

Tool Result: {json.dumps(tool_result, indent=2)}

If you have enough information to answer the user's query, respond with <task_complete>true</task_complete> followed by your final answer.

If you need more information, provide another <tool_call_request> with the appropriate tool and parameters.

Your response:"""

            response = await provider.generate_response(
                prompt=prompt,
                max_tokens=4000,
                temperature=0.7
            )

            return response

        except Exception as e:
            self.logger.error(f"Error getting next action: {e}")
            return f"<task_complete>true</task_complete>\n\nI encountered an error while processing the tool result: {e}"

    def _extract_final_answer(self, response: str) -> Optional[str]:
        """Extract the final answer from a response."""
        import re
        # Look for content after <task_complete>true</task_complete>
        pattern = r'<task_complete>true</task_complete>\s*(.*)'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None