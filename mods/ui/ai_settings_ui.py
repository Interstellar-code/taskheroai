"""
AI Settings UI for TaskHero AI.

Provides user interface for configuring AI provider settings.
"""

import asyncio
from typing import Dict, Any, Optional, Tuple, List
from colorama import Fore, Style

from ..core import BaseManager
from ..settings import AISettingsManager


class AISettingsUI(BaseManager):
    """User interface for AI settings management."""

    def __init__(self, ai_settings_manager: Optional[AISettingsManager] = None):
        """
        Initialize the AI Settings UI.

        Args:
            ai_settings_manager: AI settings manager instance
        """
        super().__init__("AISettingsUI")
        self.ai_settings_manager = ai_settings_manager or AISettingsManager()

    def _perform_initialization(self) -> None:
        """Initialize the AI Settings UI."""
        self.ai_settings_manager.initialize()
        self.update_status("ai_settings_ui_ready", True)
        self.logger.info("AI Settings UI initialized")

    def display_main_ai_settings_menu(self) -> None:
        """Display the main AI settings menu."""
        print("\n" + Fore.CYAN + "=" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🤖 AI Settings Configuration".center(70) + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

        # Get provider status
        openai_status = self.ai_settings_manager.get_provider_status('openai')
        anthropic_status = self.ai_settings_manager.get_provider_status('anthropic')
        ollama_status = self.ai_settings_manager.get_provider_status('ollama')
        openrouter_status = self.ai_settings_manager.get_provider_status('openrouter')
        deepseek_status = self.ai_settings_manager.get_provider_status('deepseek')

        # Provider Configuration Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "📡 Provider Configuration" + Style.RESET_ALL)

        # OpenAI
        openai_indicator = f"{Fore.GREEN}✓{Style.RESET_ALL}" if openai_status['configured'] else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"1. {Style.BRIGHT}🔵 OpenAI Configuration{Style.RESET_ALL} [{openai_indicator}]")

        # Anthropic
        anthropic_indicator = f"{Fore.GREEN}✓{Style.RESET_ALL}" if anthropic_status['configured'] else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"2. {Style.BRIGHT}🟣 Anthropic Configuration{Style.RESET_ALL} [{anthropic_indicator}]")

        # Ollama
        ollama_indicator = f"{Fore.GREEN}✓{Style.RESET_ALL}" if ollama_status['configured'] else f"{Fore.YELLOW}○{Style.RESET_ALL}"
        print(f"3. {Style.BRIGHT}🟠 Ollama Configuration{Style.RESET_ALL} [{ollama_indicator}] {Fore.CYAN}(Local){Style.RESET_ALL}")

        # OpenRouter
        openrouter_indicator = f"{Fore.GREEN}✓{Style.RESET_ALL}" if openrouter_status['configured'] else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"4. {Style.BRIGHT}🔶 OpenRouter Configuration{Style.RESET_ALL} [{openrouter_indicator}] {Fore.CYAN}(Multi-model){Style.RESET_ALL}")

        # DeepSeek
        deepseek_indicator = f"{Fore.GREEN}✓{Style.RESET_ALL}" if deepseek_status['configured'] else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"5. {Style.BRIGHT}🤖 DeepSeek Configuration{Style.RESET_ALL} [{deepseek_indicator}] {Fore.CYAN}(DeepSeek-V3, R1){Style.RESET_ALL}")

        # Function Assignment Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "⚙️ Function Assignment" + Style.RESET_ALL)
        print(f"6. {Style.BRIGHT}🎯 Configure AI Functions{Style.RESET_ALL} {Fore.CYAN}(Assign providers to tasks){Style.RESET_ALL}")

        # Fallback & Reliability Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🔄 Fallback & Reliability" + Style.RESET_ALL)
        print(f"7. {Style.BRIGHT}⚡ Fallback & Retry Settings{Style.RESET_ALL} {Fore.CYAN}(Provider failover){Style.RESET_ALL}")

        # Testing & Management Section
        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + Style.BRIGHT + "🧪 Testing & Management" + Style.RESET_ALL)
        print(f"8. {Style.BRIGHT}🔍 Test AI Connections{Style.RESET_ALL}")
        print(f"9. {Style.BRIGHT}📊 Provider Status Overview{Style.RESET_ALL}")
        print(f"10. {Style.BRIGHT}🔄 Reset to Defaults{Style.RESET_ALL}")
        print(f"11. {Style.BRIGHT}💾 Export/Import Settings{Style.RESET_ALL}")

        print(Fore.CYAN + "-" * 70 + Style.RESET_ALL)
        print(f"0. {Style.BRIGHT}🔙 Back to Main Menu{Style.RESET_ALL}")

        print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)
        print(f"{Fore.CYAN}💡 Legend: {Fore.GREEN}✓{Style.RESET_ALL} = Configured | {Fore.RED}✗{Style.RESET_ALL} = Not configured | {Fore.YELLOW}○{Style.RESET_ALL} = Local/Available{Style.RESET_ALL}")

    def get_user_choice(self, prompt: str = "Choose an option") -> str:
        """Get user input choice."""
        print(f"\n{Fore.GREEN}{prompt}:{Style.RESET_ALL}")
        choice = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
        return choice

    async def handle_ai_settings_menu(self) -> None:
        """Handle the AI settings menu interaction."""
        while True:
            try:
                self.display_main_ai_settings_menu()
                choice = self.get_user_choice()

                if choice == "1":
                    await self.configure_openai()
                elif choice == "2":
                    await self.configure_anthropic()
                elif choice == "3":
                    await self.configure_ollama()
                elif choice == "4":
                    await self.configure_openrouter()
                elif choice == "5":
                    await self.configure_deepseek()
                elif choice == "6":
                    await self.configure_ai_functions()
                elif choice == "7":
                    await self.configure_fallback_settings()
                elif choice == "8":
                    await self.test_all_connections()
                elif choice == "9":
                    await self.show_provider_status()
                elif choice == "10":
                    await self.reset_provider_defaults()
                elif choice == "11":
                    await self.handle_export_import()
                elif choice == "0":
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter 1-11 or 0 to go back.{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                break
            except Exception as e:
                self.logger.error(f"Error in AI settings menu: {e}")
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def configure_openai(self) -> None:
        """Configure OpenAI provider settings."""
        print(f"\n{Fore.BLUE}🔵 OpenAI Configuration{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)

        current_settings = self.ai_settings_manager.get_openai_settings()

        # Display current settings
        print(f"\n{Fore.YELLOW}Current OpenAI Settings:{Style.RESET_ALL}")
        api_key_display = current_settings.get('API_KEY', '')
        if api_key_display and api_key_display != 'your_openai_api_key_here':
            api_key_display = api_key_display[:8] + "..." + api_key_display[-4:] if len(api_key_display) > 12 else api_key_display
        print(f"API Key: {api_key_display}")
        print(f"Model: {current_settings.get('MODEL', 'gpt-4')}")
        print(f"Max Tokens: {current_settings.get('MAX_TOKENS', '4000')}")
        print(f"Temperature: {current_settings.get('TEMPERATURE', '0.7')}")
        print(f"Top P: {current_settings.get('TOP_P', '1.0')}")
        print(f"Frequency Penalty: {current_settings.get('FREQUENCY_PENALTY', '0.0')}")
        print(f"Presence Penalty: {current_settings.get('PRESENCE_PENALTY', '0.0')}")

        # Configuration options
        new_settings = current_settings.copy()

        if input(f"\n{Fore.GREEN}Update API Key? (y/n): {Style.RESET_ALL}").lower() == 'y':
            api_key = input(f"{Fore.CYAN}Enter OpenAI API Key: {Style.RESET_ALL}").strip()
            if api_key:
                new_settings['API_KEY'] = api_key

        if input(f"{Fore.GREEN}Update Model? (y/n): {Style.RESET_ALL}").lower() == 'y':
            print(f"{Fore.CYAN}Available models: gpt-4, gpt-4-turbo, gpt-3.5-turbo{Style.RESET_ALL}")
            model = input(f"{Fore.CYAN}Enter model [{current_settings.get('MODEL', 'gpt-4')}]: {Style.RESET_ALL}").strip()
            if model:
                new_settings['MODEL'] = model

        if input(f"{Fore.GREEN}Update advanced settings? (y/n): {Style.RESET_ALL}").lower() == 'y':
            max_tokens = input(f"{Fore.CYAN}Max Tokens [{current_settings.get('MAX_TOKENS', '4000')}]: {Style.RESET_ALL}").strip()
            if max_tokens:
                new_settings['MAX_TOKENS'] = max_tokens

            temperature = input(f"{Fore.CYAN}Temperature (0.0-2.0) [{current_settings.get('TEMPERATURE', '0.7')}]: {Style.RESET_ALL}").strip()
            if temperature:
                new_settings['TEMPERATURE'] = temperature

            top_p = input(f"{Fore.CYAN}Top P (0.0-1.0) [{current_settings.get('TOP_P', '1.0')}]: {Style.RESET_ALL}").strip()
            if top_p:
                new_settings['TOP_P'] = top_p

            freq_penalty = input(f"{Fore.CYAN}Frequency Penalty (-2.0-2.0) [{current_settings.get('FREQUENCY_PENALTY', '0.0')}]: {Style.RESET_ALL}").strip()
            if freq_penalty:
                new_settings['FREQUENCY_PENALTY'] = freq_penalty

            presence_penalty = input(f"{Fore.CYAN}Presence Penalty (-2.0-2.0) [{current_settings.get('PRESENCE_PENALTY', '0.0')}]: {Style.RESET_ALL}").strip()
            if presence_penalty:
                new_settings['PRESENCE_PENALTY'] = presence_penalty

        # Save settings
        if self.ai_settings_manager.set_openai_settings(new_settings):
            print(f"{Fore.GREEN}✅ OpenAI settings saved successfully!{Style.RESET_ALL}")

            # Test connection
            if input(f"{Fore.CYAN}Test connection now? (y/n): {Style.RESET_ALL}").lower() == 'y':
                await self.test_provider_connection('openai')
        else:
            print(f"{Fore.RED}❌ Failed to save OpenAI settings.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def configure_anthropic(self) -> None:
        """Configure Anthropic provider settings."""
        print(f"\n{Fore.MAGENTA}🟣 Anthropic Configuration{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)

        current_settings = self.ai_settings_manager.get_anthropic_settings()

        # Display current settings
        print(f"\n{Fore.YELLOW}Current Anthropic Settings:{Style.RESET_ALL}")
        api_key_display = current_settings.get('API_KEY', '')
        if api_key_display and api_key_display != 'your_anthropic_api_key_here':
            api_key_display = api_key_display[:8] + "..." + api_key_display[-4:] if len(api_key_display) > 12 else api_key_display
        print(f"API Key: {api_key_display}")
        print(f"Model: {current_settings.get('MODEL', 'claude-3-sonnet-20240229')}")
        print(f"Max Tokens: {current_settings.get('MAX_TOKENS', '4000')}")
        print(f"Temperature: {current_settings.get('TEMPERATURE', '0.7')}")
        print(f"Top P: {current_settings.get('TOP_P', '1.0')}")
        print(f"Top K: {current_settings.get('TOP_K', '40')}")

        # Configuration options
        new_settings = current_settings.copy()

        if input(f"\n{Fore.GREEN}Update API Key? (y/n): {Style.RESET_ALL}").lower() == 'y':
            api_key = input(f"{Fore.CYAN}Enter Anthropic API Key: {Style.RESET_ALL}").strip()
            if api_key:
                new_settings['API_KEY'] = api_key

        if input(f"{Fore.GREEN}Update Model? (y/n): {Style.RESET_ALL}").lower() == 'y':
            print(f"{Fore.CYAN}Available models: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307{Style.RESET_ALL}")
            model = input(f"{Fore.CYAN}Enter model [{current_settings.get('MODEL', 'claude-3-sonnet-20240229')}]: {Style.RESET_ALL}").strip()
            if model:
                new_settings['MODEL'] = model

        if input(f"{Fore.GREEN}Update advanced settings? (y/n): {Style.RESET_ALL}").lower() == 'y':
            max_tokens = input(f"{Fore.CYAN}Max Tokens [{current_settings.get('MAX_TOKENS', '4000')}]: {Style.RESET_ALL}").strip()
            if max_tokens:
                new_settings['MAX_TOKENS'] = max_tokens

            temperature = input(f"{Fore.CYAN}Temperature (0.0-1.0) [{current_settings.get('TEMPERATURE', '0.7')}]: {Style.RESET_ALL}").strip()
            if temperature:
                new_settings['TEMPERATURE'] = temperature

            top_p = input(f"{Fore.CYAN}Top P (0.0-1.0) [{current_settings.get('TOP_P', '1.0')}]: {Style.RESET_ALL}").strip()
            if top_p:
                new_settings['TOP_P'] = top_p

            top_k = input(f"{Fore.CYAN}Top K (1-100) [{current_settings.get('TOP_K', '40')}]: {Style.RESET_ALL}").strip()
            if top_k:
                new_settings['TOP_K'] = top_k

        # Save settings
        if self.ai_settings_manager.set_anthropic_settings(new_settings):
            print(f"{Fore.GREEN}✅ Anthropic settings saved successfully!{Style.RESET_ALL}")

            # Test connection
            if input(f"{Fore.CYAN}Test connection now? (y/n): {Style.RESET_ALL}").lower() == 'y':
                await self.test_provider_connection('anthropic')
        else:
            print(f"{Fore.RED}❌ Failed to save Anthropic settings.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def configure_ollama(self) -> None:
        """Configure Ollama provider settings."""
        print(f"\n{Fore.YELLOW}🟠 Ollama Configuration{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)

        current_settings = self.ai_settings_manager.get_ollama_settings()

        # Display current settings
        print(f"\n{Fore.YELLOW}Current Ollama Settings:{Style.RESET_ALL}")
        print(f"Host: {current_settings.get('HOST', 'http://localhost:11434')}")
        print(f"Model: {current_settings.get('MODEL', 'llama2')}")
        print(f"Max Tokens: {current_settings.get('MAX_TOKENS', '4000')}")
        print(f"Temperature: {current_settings.get('TEMPERATURE', '0.7')}")
        print(f"Top P: {current_settings.get('TOP_P', '0.95')}")
        print(f"Top K: {current_settings.get('TOP_K', '40')}")

        # Configuration options
        new_settings = current_settings.copy()

        if input(f"\n{Fore.GREEN}Update Host? (y/n): {Style.RESET_ALL}").lower() == 'y':
            host = input(f"{Fore.CYAN}Enter Ollama Host [{current_settings.get('HOST', 'http://localhost:11434')}]: {Style.RESET_ALL}").strip()
            if host:
                new_settings['HOST'] = host

        if input(f"{Fore.GREEN}Update Model? (y/n): {Style.RESET_ALL}").lower() == 'y':
            print(f"{Fore.CYAN}Common models: llama2, llama3.1, codellama, mistral, neural-chat{Style.RESET_ALL}")
            model = input(f"{Fore.CYAN}Enter model [{current_settings.get('MODEL', 'llama2')}]: {Style.RESET_ALL}").strip()
            if model:
                new_settings['MODEL'] = model

        if input(f"{Fore.GREEN}Update advanced settings? (y/n): {Style.RESET_ALL}").lower() == 'y':
            max_tokens = input(f"{Fore.CYAN}Max Tokens [{current_settings.get('MAX_TOKENS', '4000')}]: {Style.RESET_ALL}").strip()
            if max_tokens:
                new_settings['MAX_TOKENS'] = max_tokens

            temperature = input(f"{Fore.CYAN}Temperature (0.0-2.0) [{current_settings.get('TEMPERATURE', '0.7')}]: {Style.RESET_ALL}").strip()
            if temperature:
                new_settings['TEMPERATURE'] = temperature

            top_p = input(f"{Fore.CYAN}Top P (0.0-1.0) [{current_settings.get('TOP_P', '0.95')}]: {Style.RESET_ALL}").strip()
            if top_p:
                new_settings['TOP_P'] = top_p

            top_k = input(f"{Fore.CYAN}Top K (1-100) [{current_settings.get('TOP_K', '40')}]: {Style.RESET_ALL}").strip()
            if top_k:
                new_settings['TOP_K'] = top_k

        # Save settings
        if self.ai_settings_manager.set_ollama_settings(new_settings):
            print(f"{Fore.GREEN}✅ Ollama settings saved successfully!{Style.RESET_ALL}")

            # Test connection
            if input(f"{Fore.CYAN}Test connection now? (y/n): {Style.RESET_ALL}").lower() == 'y':
                await self.test_provider_connection('ollama')
        else:
            print(f"{Fore.RED}❌ Failed to save Ollama settings.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def configure_openrouter(self) -> None:
        """Configure OpenRouter provider settings."""
        print(f"\n{Fore.CYAN}🔶 OpenRouter Configuration{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)

        current_settings = self.ai_settings_manager.get_openrouter_settings()

        # Display current settings
        print(f"\n{Fore.YELLOW}Current OpenRouter Settings:{Style.RESET_ALL}")
        api_key_display = current_settings.get('API_KEY', '')
        if api_key_display and api_key_display != 'your_openrouter_api_key_here':
            api_key_display = api_key_display[:8] + "..." + api_key_display[-4:] if len(api_key_display) > 12 else api_key_display
        print(f"API Key: {api_key_display}")
        print(f"Model: {current_settings.get('MODEL', 'openai/gpt-4')}")
        print(f"Max Tokens: {current_settings.get('MAX_TOKENS', '4000')}")
        print(f"Temperature: {current_settings.get('TEMPERATURE', '0.7')}")
        print(f"Top P: {current_settings.get('TOP_P', '1.0')}")
        print(f"HTTP Referer: {current_settings.get('HTTP_REFERER', 'https://taskhero-ai.com')}")
        print(f"X-Title: {current_settings.get('X_TITLE', 'TaskHeroAI')}")

        # Configuration options
        new_settings = current_settings.copy()

        if input(f"\n{Fore.GREEN}Update API Key? (y/n): {Style.RESET_ALL}").lower() == 'y':
            api_key = input(f"{Fore.CYAN}Enter OpenRouter API Key: {Style.RESET_ALL}").strip()
            if api_key:
                new_settings['API_KEY'] = api_key

        if input(f"{Fore.GREEN}Update Model? (y/n): {Style.RESET_ALL}").lower() == 'y':
            print(f"{Fore.CYAN}Available models: openai/gpt-4, anthropic/claude-3-opus, meta-llama/llama-2-70b-chat{Style.RESET_ALL}")
            model = input(f"{Fore.CYAN}Enter model [{current_settings.get('MODEL', 'openai/gpt-4')}]: {Style.RESET_ALL}").strip()
            if model:
                new_settings['MODEL'] = model

        if input(f"{Fore.GREEN}Update app info? (y/n): {Style.RESET_ALL}").lower() == 'y':
            http_referer = input(f"{Fore.CYAN}HTTP Referer [{current_settings.get('HTTP_REFERER', 'https://taskhero-ai.com')}]: {Style.RESET_ALL}").strip()
            if http_referer:
                new_settings['HTTP_REFERER'] = http_referer

            x_title = input(f"{Fore.CYAN}X-Title [{current_settings.get('X_TITLE', 'TaskHeroAI')}]: {Style.RESET_ALL}").strip()
            if x_title:
                new_settings['X_TITLE'] = x_title

        if input(f"{Fore.GREEN}Update advanced settings? (y/n): {Style.RESET_ALL}").lower() == 'y':
            max_tokens = input(f"{Fore.CYAN}Max Tokens [{current_settings.get('MAX_TOKENS', '4000')}]: {Style.RESET_ALL}").strip()
            if max_tokens:
                new_settings['MAX_TOKENS'] = max_tokens

            temperature = input(f"{Fore.CYAN}Temperature (0.0-2.0) [{current_settings.get('TEMPERATURE', '0.7')}]: {Style.RESET_ALL}").strip()
            if temperature:
                new_settings['TEMPERATURE'] = temperature

            top_p = input(f"{Fore.CYAN}Top P (0.0-1.0) [{current_settings.get('TOP_P', '1.0')}]: {Style.RESET_ALL}").strip()
            if top_p:
                new_settings['TOP_P'] = top_p

        # Save settings
        if self.ai_settings_manager.set_openrouter_settings(new_settings):
            print(f"{Fore.GREEN}✅ OpenRouter settings saved successfully!{Style.RESET_ALL}")

            # Test connection
            if input(f"{Fore.CYAN}Test connection now? (y/n): {Style.RESET_ALL}").lower() == 'y':
                await self.test_provider_connection('openrouter')
        else:
            print(f"{Fore.RED}❌ Failed to save OpenRouter settings.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def configure_deepseek(self) -> None:
        """Configure DeepSeek provider settings."""
        print(f"\n{Fore.CYAN}🤖 DeepSeek Configuration{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)

        current_settings = self.ai_settings_manager.get_deepseek_settings()

        # Display current settings
        print(f"\n{Fore.YELLOW}Current DeepSeek Settings:{Style.RESET_ALL}")
        api_key_display = current_settings.get('API_KEY', '')
        if api_key_display and api_key_display != 'your_deepseek_api_key_here':
            api_key_display = api_key_display[:8] + "..." + api_key_display[-4:] if len(api_key_display) > 12 else api_key_display
        print(f"API Key: {api_key_display}")
        print(f"Model: {current_settings.get('MODEL', 'deepseek-chat')}")
        print(f"Max Tokens: {current_settings.get('MAX_TOKENS', '4000')}")
        print(f"Temperature: {current_settings.get('TEMPERATURE', '0.7')}")
        print(f"Top P: {current_settings.get('TOP_P', '1.0')}")

        # Configuration options
        new_settings = current_settings.copy()

        if input(f"\n{Fore.GREEN}Update API Key? (y/n): {Style.RESET_ALL}").lower() == 'y':
            print(f"{Fore.CYAN}Get your API key from: https://platform.deepseek.com/api_keys{Style.RESET_ALL}")
            api_key = input(f"{Fore.CYAN}Enter DeepSeek API Key: {Style.RESET_ALL}").strip()
            if api_key:
                new_settings['API_KEY'] = api_key

        if input(f"{Fore.GREEN}Update Model? (y/n): {Style.RESET_ALL}").lower() == 'y':
            print(f"{Fore.CYAN}Available models:{Style.RESET_ALL}")
            print(f"  - deepseek-chat (DeepSeek-V3): General purpose, excellent for code")
            print(f"  - deepseek-reasoner (DeepSeek-R1): Advanced reasoning, step-by-step analysis")
            model = input(f"{Fore.CYAN}Enter model [{current_settings.get('MODEL', 'deepseek-chat')}]: {Style.RESET_ALL}").strip()
            if model:
                new_settings['MODEL'] = model

        if input(f"{Fore.GREEN}Update advanced settings? (y/n): {Style.RESET_ALL}").lower() == 'y':
            max_tokens = input(f"{Fore.CYAN}Max Tokens [{current_settings.get('MAX_TOKENS', '4000')}]: {Style.RESET_ALL}").strip()
            if max_tokens:
                new_settings['MAX_TOKENS'] = max_tokens

            temperature = input(f"{Fore.CYAN}Temperature (0.0-1.0) [{current_settings.get('TEMPERATURE', '0.7')}]: {Style.RESET_ALL}").strip()
            if temperature:
                new_settings['TEMPERATURE'] = temperature

            top_p = input(f"{Fore.CYAN}Top P (0.0-1.0) [{current_settings.get('TOP_P', '1.0')}]: {Style.RESET_ALL}").strip()
            if top_p:
                new_settings['TOP_P'] = top_p

        # Save settings
        if self.ai_settings_manager.set_deepseek_settings(new_settings):
            print(f"{Fore.GREEN}✅ DeepSeek settings saved successfully!{Style.RESET_ALL}")

            # Test connection
            if input(f"{Fore.CYAN}Test connection now? (y/n): {Style.RESET_ALL}").lower() == 'y':
                await self.test_provider_connection('deepseek')
        else:
            print(f"{Fore.RED}❌ Failed to save DeepSeek settings.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def configure_fallback_settings(self) -> None:
        """Configure AI provider fallback and retry settings."""
        print(f"\n{Fore.CYAN}⚡ Fallback & Retry Settings{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)

        current_settings = self.ai_settings_manager.get_fallback_settings()

        # Display current settings
        print(f"\n{Fore.YELLOW}Current Fallback Settings:{Style.RESET_ALL}")
        print(f"Enabled: {Fore.GREEN if current_settings['enabled'] else Fore.RED}{current_settings['enabled']}{Style.RESET_ALL}")
        print(f"Auto Switch: {Fore.GREEN if current_settings['auto_switch'] else Fore.RED}{current_settings['auto_switch']}{Style.RESET_ALL}")
        print(f"Retry Attempts: {current_settings['retry_attempts']}")
        print(f"Timeout (seconds): {current_settings['timeout_seconds']}")
        print(f"Fallback Chain: {' → '.join(current_settings['chain'])}")

        # Configuration options
        new_settings = current_settings.copy()

        if input(f"\n{Fore.GREEN}Enable/Disable fallback system? (y/n): {Style.RESET_ALL}").lower() == 'y':
            enabled = input(f"{Fore.CYAN}Enable fallback system? (y/n) [{current_settings['enabled']}]: {Style.RESET_ALL}").lower()
            if enabled in ['y', 'n']:
                new_settings['enabled'] = enabled == 'y'

        if input(f"{Fore.GREEN}Configure auto-switch? (y/n): {Style.RESET_ALL}").lower() == 'y':
            auto_switch = input(f"{Fore.CYAN}Auto-switch on provider failure? (y/n) [{current_settings['auto_switch']}]: {Style.RESET_ALL}").lower()
            if auto_switch in ['y', 'n']:
                new_settings['auto_switch'] = auto_switch == 'y'

        if input(f"{Fore.GREEN}Update retry settings? (y/n): {Style.RESET_ALL}").lower() == 'y':
            retry_attempts = input(f"{Fore.CYAN}Retry attempts (1-10) [{current_settings['retry_attempts']}]: {Style.RESET_ALL}").strip()
            if retry_attempts.isdigit() and 1 <= int(retry_attempts) <= 10:
                new_settings['retry_attempts'] = int(retry_attempts)

            timeout = input(f"{Fore.CYAN}Timeout seconds (10-120) [{current_settings['timeout_seconds']}]: {Style.RESET_ALL}").strip()
            if timeout.isdigit() and 10 <= int(timeout) <= 120:
                new_settings['timeout_seconds'] = int(timeout)

        if input(f"{Fore.GREEN}Configure fallback chain? (y/n): {Style.RESET_ALL}").lower() == 'y':
            print(f"\n{Fore.CYAN}Configure Provider Fallback Chain:{Style.RESET_ALL}")
            print("Available providers: openai, anthropic, ollama, openrouter, deepseek")
            print(f"Current chain: {' → '.join(current_settings['chain'])}")

            new_chain = []
            providers = ['openai', 'anthropic', 'ollama', 'openrouter', 'deepseek']

            print(f"\n{Fore.YELLOW}Select providers in order of preference (press Enter when done):{Style.RESET_ALL}")

            while len(new_chain) < len(providers):
                available = [p for p in providers if p not in new_chain]
                if not available:
                    break

                print(f"\nAvailable providers: {', '.join(available)}")
                choice = input(f"{Fore.CYAN}Add provider (or press Enter to finish): {Style.RESET_ALL}").strip().lower()

                if not choice:
                    break

                if choice in available:
                    new_chain.append(choice)
                    print(f"{Fore.GREEN}Added {choice} to chain{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid provider: {choice}{Style.RESET_ALL}")

            if new_chain:
                new_settings['chain'] = new_chain
                print(f"\n{Fore.GREEN}New fallback chain: {' → '.join(new_chain)}{Style.RESET_ALL}")

        # Save settings
        if self.ai_settings_manager.set_fallback_settings(new_settings):
            print(f"\n{Fore.GREEN}✅ Fallback settings saved successfully!{Style.RESET_ALL}")

            # Show summary
            print(f"\n{Fore.CYAN}Updated Settings Summary:{Style.RESET_ALL}")
            print(f"Fallback: {Fore.GREEN if new_settings['enabled'] else Fore.RED}{new_settings['enabled']}{Style.RESET_ALL}")
            print(f"Auto-switch: {Fore.GREEN if new_settings['auto_switch'] else Fore.RED}{new_settings['auto_switch']}{Style.RESET_ALL}")
            print(f"Retries: {new_settings['retry_attempts']}")
            print(f"Timeout: {new_settings['timeout_seconds']}s")
            print(f"Chain: {' → '.join(new_settings['chain'])}")
        else:
            print(f"\n{Fore.RED}❌ Failed to save fallback settings.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def test_provider_connection(self, provider: str) -> None:
        """Test connection to a specific provider."""
        print(f"\n{Fore.CYAN}🔍 Testing {provider.title()} connection...{Style.RESET_ALL}")

        try:
            success, message = await self.ai_settings_manager.test_provider_connection(provider)

            if success:
                print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}❌ Test failed: {e}{Style.RESET_ALL}")

    async def test_all_connections(self) -> None:
        """Test connections to all providers."""
        print(f"\n{Fore.CYAN}🔍 Testing All AI Provider Connections{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 50 + Style.RESET_ALL)

        try:
            results = await self.ai_settings_manager.test_all_providers()

            for provider, (success, message) in results.items():
                status_icon = f"{Fore.GREEN}✅" if success else f"{Fore.RED}❌"
                print(f"{status_icon} {provider.title()}: {message}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}❌ Testing failed: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def show_provider_status(self) -> None:
        """Show detailed status for all providers."""
        print(f"\n{Fore.CYAN}📊 Provider Status Overview{Style.RESET_ALL}")
        print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

        providers = ['openai', 'anthropic', 'ollama', 'openrouter', 'deepseek']

        for provider in providers:
            status = self.ai_settings_manager.get_provider_status(provider)

            print(f"\n{Fore.YELLOW}{provider.title()} Provider:{Style.RESET_ALL}")
            print(Fore.CYAN + "-" * 30 + Style.RESET_ALL)

            config_status = f"{Fore.GREEN}✅ Configured" if status['configured'] else f"{Fore.RED}❌ Not Configured"
            print(f"Status: {config_status}{Style.RESET_ALL}")

            if status['configured']:
                settings = status['settings']
                for key, value in settings.items():
                    if 'API_KEY' in key and value and value != f'your_{provider}_api_key_here':
                        # Mask API key
                        display_value = value[:8] + "..." + value[-4:] if len(value) > 12 else value
                        print(f"{key}: {display_value}")
                    else:
                        print(f"{key}: {value}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def reset_provider_defaults(self) -> None:
        """Reset provider settings to defaults."""
        print(f"\n{Fore.YELLOW}🔄 Reset Provider to Defaults{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 40 + Style.RESET_ALL)

        print("Available providers:")
        print("1. OpenAI")
        print("2. Anthropic")
        print("3. Ollama")
        print("4. OpenRouter")
        print("5. DeepSeek")
        print("6. All Providers")

        choice = self.get_user_choice("Select provider to reset")

        provider_map = {
            '1': 'openai',
            '2': 'anthropic',
            '3': 'ollama',
            '4': 'openrouter',
            '5': 'deepseek'
        }

        if choice in provider_map:
            provider = provider_map[choice]
            if input(f"{Fore.RED}Are you sure you want to reset {provider.title()} to defaults? (y/n): {Style.RESET_ALL}").lower() == 'y':
                if self.ai_settings_manager.reset_to_defaults(provider):
                    print(f"{Fore.GREEN}✅ {provider.title()} settings reset to defaults.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Failed to reset {provider.title()} settings.{Style.RESET_ALL}")
        elif choice == '6':
            if input(f"{Fore.RED}Are you sure you want to reset ALL providers to defaults? (y/n): {Style.RESET_ALL}").lower() == 'y':
                for provider in ['openai', 'anthropic', 'ollama', 'openrouter', 'deepseek']:
                    if self.ai_settings_manager.reset_to_defaults(provider):
                        print(f"{Fore.GREEN}✅ {provider.title()} reset to defaults.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Failed to reset {provider.title()}.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def handle_export_import(self) -> None:
        """Handle settings export/import."""
        print(f"\n{Fore.CYAN}💾 Export/Import Settings{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 30 + Style.RESET_ALL)

        print("1. Export Settings")
        print("2. Import Settings")

        choice = self.get_user_choice("Select option")

        if choice == '1':
            filename = input(f"{Fore.CYAN}Export filename [ai_settings.json]: {Style.RESET_ALL}").strip() or "ai_settings.json"
            if self.ai_settings_manager.export_settings(filename):
                print(f"{Fore.GREEN}✅ Settings exported to {filename}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Failed to export settings.{Style.RESET_ALL}")

        elif choice == '2':
            filename = input(f"{Fore.CYAN}Import filename: {Style.RESET_ALL}").strip()
            if filename:
                if self.ai_settings_manager.import_settings(filename):
                    print(f"{Fore.GREEN}✅ Settings imported from {filename}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Failed to import settings.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Please specify a filename.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def configure_ai_functions(self) -> None:
        """Configure AI function assignments."""
        print(f"\n{Fore.CYAN}🎯 Configure AI Functions{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 60 + Style.RESET_ALL)

        # Get current assignments
        assignments = self.ai_settings_manager.get_ai_function_assignments()
        descriptions = self.ai_settings_manager.get_function_descriptions()

        # Display current assignments
        print(f"\n{Fore.YELLOW}Current AI Function Assignments:{Style.RESET_ALL}")
        print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

        function_icons = {
            'embedding': '🔍',
            'chat': '💬',
            'task': '📋',
            'description': '📝',
            'agent': '🤖'
        }

        for function, assignment in assignments.items():
            icon = function_icons.get(function, '⚡')
            provider = assignment.get('provider', 'unknown')
            model = assignment.get('model', 'unknown')
            desc = descriptions.get(function, 'No description available')

            print(f"\n{icon} {Fore.YELLOW}{function.title()}{Style.RESET_ALL}")
            print(f"   Provider: {Fore.GREEN}{provider.title()}{Style.RESET_ALL}")
            print(f"   Model: {Fore.CYAN}{model}{Style.RESET_ALL}")
            print(f"   Purpose: {desc}")

        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        # Function selection menu
        while True:
            print(f"\n{Fore.GREEN}Select function to configure:{Style.RESET_ALL}")
            print("1. 🔍 Embedding & Search")
            print("2. 💬 Chat with Code")
            print("3. 📋 Task Management")
            print("4. 📝 Description Generation")
            print("5. 🤖 AI Agent Mode")
            print("0. 🔙 Back to main menu")

            choice = self.get_user_choice("Select function")

            function_map = {
                '1': 'embedding',
                '2': 'chat',
                '3': 'task',
                '4': 'description',
                '5': 'agent'
            }

            if choice == '0':
                break
            elif choice in function_map:
                function = function_map[choice]
                if await self._configure_single_function(function):
                    # Refresh assignments after change
                    assignments = self.ai_settings_manager.get_ai_function_assignments()
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1-5 or 0 to go back.{Style.RESET_ALL}")

    async def _configure_single_function(self, function: str) -> bool:
        """Configure a single AI function assignment."""
        current = self.ai_settings_manager.get_ai_function_assignments().get(function, {})
        current_provider = current.get('provider', 'unknown')
        current_model = current.get('model', 'unknown')
        descriptions = self.ai_settings_manager.get_function_descriptions()

        print(f"\n{Fore.CYAN}Configuring {function.title()}{Style.RESET_ALL}")
        print(f"Purpose: {descriptions.get(function, 'No description')}")
        print(f"Current: {Fore.GREEN}{current_provider}{Style.RESET_ALL} / {Fore.CYAN}{current_model}{Style.RESET_ALL}")
        print("-" * 50)

        # Provider selection
        print(f"\n{Fore.GREEN}Select AI Provider:{Style.RESET_ALL}")
        providers = ['openai', 'anthropic', 'ollama', 'openrouter', 'deepseek']
        for i, provider in enumerate(providers, 1):
            provider_status = self.ai_settings_manager.get_provider_status(provider)
            status_icon = f"{Fore.GREEN}✓" if provider_status['configured'] else f"{Fore.RED}✗"
            print(f"{i}. {status_icon} {provider.title()}{Style.RESET_ALL}")

        provider_choice = self.get_user_choice("Select provider (1-5)")

        try:
            provider_index = int(provider_choice) - 1
            if 0 <= provider_index < len(providers):
                selected_provider = providers[provider_index]
            else:
                print(f"{Fore.RED}Invalid provider choice.{Style.RESET_ALL}")
                return False
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
            return False

        # Model selection
        available_models = self.ai_settings_manager.get_available_models_for_provider(selected_provider)

        print(f"\n{Fore.GREEN}Available models for {selected_provider.title()}:{Style.RESET_ALL}")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model}")

        print(f"{len(available_models) + 1}. ✏️ Enter custom model")

        model_choice = self.get_user_choice(f"Select model (1-{len(available_models) + 1})")

        try:
            model_index = int(model_choice) - 1
            if 0 <= model_index < len(available_models):
                selected_model = available_models[model_index]
            elif model_index == len(available_models):
                # Custom model input
                selected_model = input(f"{Fore.CYAN}Enter custom model name: {Style.RESET_ALL}").strip()
                if not selected_model:
                    print(f"{Fore.RED}Model name cannot be empty.{Style.RESET_ALL}")
                    return False
            else:
                print(f"{Fore.RED}Invalid model choice.{Style.RESET_ALL}")
                return False
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
            return False

        # Confirmation
        print(f"\n{Fore.YELLOW}New assignment:{Style.RESET_ALL}")
        print(f"Function: {Fore.CYAN}{function.title()}{Style.RESET_ALL}")
        print(f"Provider: {Fore.GREEN}{selected_provider.title()}{Style.RESET_ALL}")
        print(f"Model: {Fore.CYAN}{selected_model}{Style.RESET_ALL}")

        confirm = input(f"\n{Fore.GREEN}Save this assignment? (y/n): {Style.RESET_ALL}").lower()

        if confirm == 'y':
            if self.ai_settings_manager.set_ai_function_assignment(function, selected_provider, selected_model):
                print(f"{Fore.GREEN}✅ Assignment saved successfully!{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Failed to save assignment.{Style.RESET_ALL}")
                return False
        else:
            print(f"{Fore.YELLOW}Assignment cancelled.{Style.RESET_ALL}")
            return False

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")