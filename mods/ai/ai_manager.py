"""
AI Manager for TaskHero AI.

Handles AI integration and AI-powered features.
Extracted from the monolithic app.py.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional, Union

from colorama import Fore, Style

from ..core import BaseManager
from .chat_handler import ChatHandler
from .agent_mode import AgentMode
from .response_formatter import ResponseFormatter


class AIManager(BaseManager):
    """Manager for AI functionality."""

    def __init__(self, settings_manager=None, environment_manager=None):
        """Initialize the AI manager."""
        super().__init__("AIManager")
        self.settings_manager = settings_manager
        self.environment_manager = environment_manager

        # AI Components
        self.chat_handler: Optional[ChatHandler] = None
        self.agent_mode_instance: Optional[AgentMode] = None
        self.response_formatter = ResponseFormatter()

        # Dependencies (will be injected)
        self.indexer = None
        self.file_selector = None
        self.project_analyzer = None
        self.project_info: Dict[str, Any] = {}
        self.chat_history: List[Dict[str, str]] = []

    def _perform_initialization(self) -> None:
        """Initialize the AI manager."""
        self.logger.info("AI Manager initialized - components will be created on demand")
        self.update_status("components_ready", True)

    def set_dependencies(self, indexer, file_selector, project_analyzer):
        """Set the required dependencies for AI functionality."""
        self.indexer = indexer
        self.file_selector = file_selector
        self.project_analyzer = project_analyzer
        self.update_status("dependencies_set", True)
        self.logger.info("AI Manager dependencies set")

    def is_ready(self) -> bool:
        """Check if AI manager is ready to handle requests."""
        return (self.indexer is not None and
                self.file_selector is not None and
                self.project_analyzer is not None)

    def chat_with_ai(self, max_chat_mode: bool = False) -> None:
        """
        Start a chat session with AI.

        Args:
            max_chat_mode: Whether to use Max Chat mode (token intensive)
        """
        if not self.is_ready():
            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Use option 1 from the main menu to index your codebase.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        print("\n" + Fore.CYAN + "=" * 60 + Style.RESET_ALL)
        if max_chat_mode:
            print(Fore.CYAN + Style.BRIGHT + "    Max Chat Mode (Token Intensive)" + Style.RESET_ALL)
            print(Fore.RED + "WARNING: This mode sends full file contents to the AI and uses more tokens." + Style.RESET_ALL)
        else:
            print(Fore.CYAN + Style.BRIGHT + "           Chat with AI" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

        # Show project info
        project_name = os.path.basename(self.indexer.root_path)
        indexed_files = self.indexer.get_indexed_files()
        print(f"{Fore.GREEN}📂 Project: {Style.BRIGHT}{project_name}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📚 Indexed Files: {Style.BRIGHT}{len(indexed_files)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}💡 Ask questions about your codebase!")
        print(f"{Fore.YELLOW}Examples:")
        print(f"  • What is the main purpose of this project?")
        print(f"  • Show me the file structure")
        print(f"  • Explain how the CLI manager works")
        print(f"  • Find bugs or code improvements{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Commands:")
        print(f"  • '{Fore.RED}exit{Fore.CYAN}' - Return to main menu")
        print(f"  • '{Fore.RED}help{Fore.CYAN}' - Show available commands")
        print(f"  • '{Fore.RED}clear{Fore.CYAN}' - Clear chat history{Style.RESET_ALL}")

        self.logger.info("AI Chat session started")

        # Initialize chat handler if needed
        if not self.chat_handler:
            self.chat_handler = ChatHandler(self.indexer, self.file_selector, self.project_info, self.environment_manager)
            self.chat_handler.initialize()

        # Main chat loop
        while True:
            try:
                print(f"\n{Fore.GREEN}You: {Style.RESET_ALL}", end="")
                user_input = input().strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() == 'exit':
                    print(f"{Fore.YELLOW}Goodbye! Returning to main menu...{Style.RESET_ALL}")
                    break
                elif user_input.lower() == 'help':
                    self._show_chat_help()
                    continue
                elif user_input.lower() == 'clear':
                    if self.chat_handler:
                        self.chat_handler.clear_history()
                    print(f"{Fore.YELLOW}Chat history cleared.{Style.RESET_ALL}")
                    continue

                # Get provider info for display
                provider_info = None
                if self.chat_handler and self.chat_handler.current_provider:
                    provider_info = self.chat_handler.get_current_provider_info()

                # Process the query with progress indication
                if provider_info:
                    provider_name = provider_info['provider']
                    model_name = provider_info['model']
                    print(f"{Fore.CYAN}AI ({provider_name}:{model_name}): {Style.RESET_ALL}Processing your question...")
                else:
                    print(f"{Fore.CYAN}AI: {Style.RESET_ALL}Processing your question...")

                # Show progress animation
                import threading
                import time

                progress_active = True
                def show_progress():
                    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
                    i = 0
                    while progress_active:
                        if provider_info:
                            provider_name = provider_info['provider']
                            model_name = provider_info['model']
                            print(f"\r{Fore.CYAN}AI ({provider_name}:{model_name}): {chars[i % len(chars)]} Analyzing codebase and generating response...{Style.RESET_ALL}", end="", flush=True)
                        else:
                            print(f"\r{Fore.CYAN}AI: {chars[i % len(chars)]} Analyzing codebase and generating response...{Style.RESET_ALL}", end="", flush=True)
                        time.sleep(0.1)
                        i += 1

                progress_thread = threading.Thread(target=show_progress)
                progress_thread.daemon = True
                progress_thread.start()

                try:
                    response, relevant_files = asyncio.run(self.chat_handler.process_query(
                        user_input,
                        max_chat_mode=max_chat_mode
                    ))

                    # Stop progress animation
                    progress_active = False
                    progress_thread.join(timeout=0.1)
                    print(f"\r{' ' * 80}\r", end="")  # Clear progress line

                    # Format and display response elegantly
                    formatted_response = self.response_formatter.format_response(response, relevant_files)
                    print(f"\n{Fore.CYAN}AI Response:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
                    print(formatted_response)
                    print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")

                    # Show provider info if successful
                    if self.chat_handler.current_provider:
                        provider_info = self.chat_handler.get_current_provider_info()
                        provider_name = provider_info['provider']
                        model_name = provider_info['model']
                        status = provider_info['status']

                        if status == "Fallback":
                            preferred = provider_info['preferred']
                            print(f"\n{Fore.YELLOW}⚠️ Powered by: {provider_name} ({model_name}) - Fallback from {preferred}{Style.RESET_ALL}")
                        else:
                            print(f"\n{Fore.GREEN}✓ Powered by: {provider_name} ({model_name}){Style.RESET_ALL}")

                except Exception as e:
                    # Stop progress animation on error
                    progress_active = False
                    progress_thread.join(timeout=0.1)
                    print(f"\r{' ' * 80}\r", end="")  # Clear progress line

                    self.logger.error(f"Error processing chat query: {e}")
                    error_message = self.response_formatter.format_error(f"I encountered an error processing your request: {e}")
                    print(error_message)

                    # Suggest troubleshooting steps
                    print(f"\n{Fore.YELLOW}💡 Troubleshooting suggestions:")
                    print(f"  • Check your .env file for valid API keys")
                    print(f"  • Verify your internet connection")
                    print(f"  • Try using a different AI provider (option 14 in main menu)")
                    print(f"  • Check the logs for more details{Style.RESET_ALL}")

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Chat interrupted. Returning to main menu...{Style.RESET_ALL}")
                break
            except Exception as e:
                self.logger.error(f"Chat error: {e}")
                print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
                break

    def _show_chat_help(self) -> None:
        """Show help information for chat commands."""
        print(f"\n{Fore.CYAN}📖 Chat Help:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available Commands:")
        print(f"  • 'exit' - Return to main menu")
        print(f"  • 'help' - Show this help message")
        print(f"  • 'clear' - Clear chat history")
        print(f"\nExample Questions:")
        print(f"  • 'What does this project do?'")
        print(f"  • 'Show me the main entry point'")
        print(f"  • 'Explain the file structure'")
        print(f"  • 'Find any potential bugs'")
        print(f"  • 'How does the indexing work?'{Style.RESET_ALL}")

    async def agent_mode(self) -> None:
        """Run the AI agent mode for interactive codebase exploration."""
        if not self.is_ready():
            print(f"\n{Fore.RED}Error: No code has been indexed yet. Please index a directory first.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Use option 1 from the main menu to index your codebase.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        print("\n" + Fore.CYAN + "=" * 60 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "           AI Agent Mode" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

        # Show project info
        project_name = os.path.basename(self.indexer.root_path)
        indexed_files = self.indexer.get_indexed_files()
        print(f"{Fore.GREEN}📂 Project: {Style.BRIGHT}{project_name}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📚 Indexed Files: {Style.BRIGHT}{len(indexed_files)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}🤖 Advanced AI Agent with codebase tools!")
        print(f"{Fore.YELLOW}The AI can explore files, analyze code patterns, and provide deep insights.")
        print(f"\n{Fore.CYAN}Agent Commands:")
        print(f"  • '{Fore.RED}exit{Fore.CYAN}' - Return to main menu")
        print(f"  • '{Fore.RED}help{Fore.CYAN}' - Show available commands")
        print(f"  • '{Fore.RED}analyze{Fore.CYAN}' - Analyze entire project")
        print(f"  • '{Fore.RED}files{Fore.CYAN}' - List project files{Style.RESET_ALL}")

        self.logger.info("Agent Mode session started")

        # Initialize agent mode if needed
        if not self.agent_mode_instance:
            self.agent_mode_instance = AgentMode(self.indexer)
            self.agent_mode_instance.initialize()

        # Main agent loop
        while True:
            try:
                print(f"\n{Fore.GREEN}You: {Style.RESET_ALL}", end="")
                user_input = input().strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() == 'exit':
                    print(f"{Fore.YELLOW}Exiting Agent Mode...{Style.RESET_ALL}")
                    break
                elif user_input.lower() == 'help':
                    self._show_agent_help()
                    continue
                elif user_input.lower() == 'analyze':
                    await self._perform_project_analysis()
                    continue
                elif user_input.lower() == 'files':
                    self._show_project_files()
                    continue

                # Process the query with agent (provider info is handled internally by AgentMode)
                try:
                    await self.agent_mode_instance.process_query(user_input)
                except Exception as e:
                    self.logger.error(f"Error in agent mode: {e}")
                    print(f"{Fore.RED}Agent encountered an error: {e}{Style.RESET_ALL}")

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Agent Mode interrupted. Returning to main menu...{Style.RESET_ALL}")
                break
            except Exception as e:
                self.logger.error(f"Agent mode error: {e}")
                print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
                break

    def _show_agent_help(self) -> None:
        """Show help information for agent commands."""
        print(f"\n{Fore.CYAN}🤖 Agent Help:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Agent Commands:")
        print(f"  • 'exit' - Return to main menu")
        print(f"  • 'help' - Show this help message")
        print(f"  • 'analyze' - Perform full project analysis")
        print(f"  • 'files' - Show project file structure")
        print(f"\nAgent Capabilities:")
        print(f"  • Deep code analysis")
        print(f"  • Pattern recognition")
        print(f"  • Architecture insights")
        print(f"  • Bug detection{Style.RESET_ALL}")

    async def _perform_project_analysis(self) -> None:
        """Perform a comprehensive project analysis."""
        print(f"\n{Fore.CYAN}🔍 Performing project analysis...{Style.RESET_ALL}")

        try:
            # Basic analysis for now
            if self.project_analyzer:
                print(f"{Fore.YELLOW}Analysis capabilities will be enhanced in the next phase.")
                print(f"For now, showing basic project information:{Style.RESET_ALL}")

                indexed_files = self.indexer.get_indexed_files()
                print(f"\n{Fore.GREEN}📊 Project Statistics:")
                print(f"  • Total Files: {len(indexed_files)}")
                print(f"  • Project Root: {self.indexer.root_path}")

                # Show file types
                extensions = {}
                for file_path in indexed_files:
                    ext = os.path.splitext(file_path)[1].lower()
                    extensions[ext] = extensions.get(ext, 0) + 1

                print(f"  • File Types:")
                for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    - {ext or 'no extension'}: {count} files")
                print(f"{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Analysis error: {e}{Style.RESET_ALL}")

    def _show_project_files(self) -> None:
        """Show project file structure."""
        try:
            indexed_files = self.indexer.get_indexed_files()
            print(f"\n{Fore.CYAN}📁 Project Files (showing first 20):{Style.RESET_ALL}")

            for i, file_path in enumerate(indexed_files[:20]):
                relative_path = os.path.relpath(file_path, self.indexer.root_path)
                print(f"  {i+1:2d}. {relative_path}")

            if len(indexed_files) > 20:
                print(f"  ... and {len(indexed_files) - 20} more files")

        except Exception as e:
            print(f"{Fore.RED}Error showing files: {e}{Style.RESET_ALL}")

    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the current chat history."""
        return self.chat_history.copy()

    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        self.chat_history.clear()
        self.logger.info("Chat history cleared")

    def _perform_reset(self) -> None:
        """Reset the AI manager."""
        self.clear_chat_history()
        self.chat_handler = None
        self.agent_mode_instance = None
        self.project_info = {}
        self.logger.info("AI Manager reset completed")