"""
AI Settings Manager for TaskHero AI.

Manages AI provider settings and configuration.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from ..core import BaseManager
from ..ai.providers import ProviderFactory
from .environment_manager import EnvironmentManager


class AISettingsManager(BaseManager):
    """Manager for AI provider settings and configuration."""
    
    def __init__(self, env_manager: Optional[EnvironmentManager] = None):
        """
        Initialize the AI settings manager.
        
        Args:
            env_manager: Environment manager instance
        """
        super().__init__("AISettingsManager")
        self.env_manager = env_manager or EnvironmentManager()
        self.provider_factory = ProviderFactory()
        
        # Default configurations for each provider
        self.default_configs = {
            'openai': {
                'API_KEY': 'your_openai_api_key_here',
                'MODEL': 'gpt-4',
                'MAX_TOKENS': '4000',
                'TEMPERATURE': '0.7',
                'TOP_P': '1.0',
                'FREQUENCY_PENALTY': '0.0',
                'PRESENCE_PENALTY': '0.0'
            },
            'anthropic': {
                'API_KEY': 'your_anthropic_api_key_here',
                'MODEL': 'claude-3-sonnet-20240229',
                'MAX_TOKENS': '4000',
                'TEMPERATURE': '0.7',
                'TOP_P': '1.0',
                'TOP_K': '40'
            },
            'ollama': {
                'HOST': 'http://localhost:11434',
                'MODEL': 'llama2',
                'MAX_TOKENS': '4000',
                'TEMPERATURE': '0.7',
                'TOP_P': '0.95',
                'TOP_K': '40'
            },
            'openrouter': {
                'API_KEY': 'your_openrouter_api_key_here',
                'MODEL': 'openai/gpt-4',
                'MAX_TOKENS': '4000',
                'TEMPERATURE': '0.7',
                'TOP_P': '1.0',
                'HTTP_REFERER': 'https://taskhero-ai.com',
                'X_TITLE': 'TaskHeroAI'
            },
            'deepseek': {
                'API_KEY': 'your_deepseek_api_key_here',
                'MODEL': 'deepseek-chat',
                'MAX_TOKENS': '4000',
                'TEMPERATURE': '0.7',
                'TOP_P': '1.0'
            }
        }
    
    def _perform_initialization(self) -> None:
        """Initialize the AI settings manager."""
        self.env_manager.initialize()
        self.update_status("ai_settings_ready", True)
        self.logger.info("AI Settings Manager initialized")
    
    def get_openai_settings(self) -> Dict[str, Any]:
        """
        Get OpenAI provider settings.
        
        Returns:
            Dictionary of OpenAI settings
        """
        return self._get_provider_settings('openai')
    
    def set_openai_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Set OpenAI provider settings.
        
        Args:
            settings: Dictionary of OpenAI settings
            
        Returns:
            True if successful, False otherwise
        """
        return self._set_provider_settings('openai', settings)
    
    def get_anthropic_settings(self) -> Dict[str, Any]:
        """
        Get Anthropic provider settings.
        
        Returns:
            Dictionary of Anthropic settings
        """
        return self._get_provider_settings('anthropic')
    
    def set_anthropic_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Set Anthropic provider settings.
        
        Args:
            settings: Dictionary of Anthropic settings
            
        Returns:
            True if successful, False otherwise
        """
        return self._set_provider_settings('anthropic', settings)
    
    def get_ollama_settings(self) -> Dict[str, Any]:
        """
        Get Ollama provider settings.
        
        Returns:
            Dictionary of Ollama settings
        """
        return self._get_provider_settings('ollama')
    
    def set_ollama_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Set Ollama provider settings.
        
        Args:
            settings: Dictionary of Ollama settings
            
        Returns:
            True if successful, False otherwise
        """
        return self._set_provider_settings('ollama', settings)
    
    def get_openrouter_settings(self) -> Dict[str, Any]:
        """
        Get OpenRouter provider settings.
        
        Returns:
            Dictionary of OpenRouter settings
        """
        return self._get_provider_settings('openrouter')
    
    def set_openrouter_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Set OpenRouter provider settings.
        
        Args:
            settings: Dictionary of OpenRouter settings
            
        Returns:
            True if successful, False otherwise
        """
        return self._set_provider_settings('openrouter', settings)
    
    def get_deepseek_settings(self) -> Dict[str, Any]:
        """
        Get DeepSeek provider settings.
        
        Returns:
            Dictionary of DeepSeek settings
        """
        return self._get_provider_settings('deepseek')
    
    def set_deepseek_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Set DeepSeek provider settings.
        
        Args:
            settings: Dictionary of DeepSeek settings
            
        Returns:
            True if successful, False otherwise
        """
        return self._set_provider_settings('deepseek', settings)
    
    def _get_provider_settings(self, provider: str) -> Dict[str, Any]:
        """
        Get settings for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Dictionary of provider settings
        """
        try:
            # Get current environment variables
            env_vars = self.env_manager.get_provider_vars(provider)
            
            # Convert to settings format (remove provider prefix)
            prefix = provider.upper() + '_'
            settings = {}
            
            for key, value in env_vars.items():
                if key.startswith(prefix):
                    setting_key = key[len(prefix):]
                    settings[setting_key] = value
            
            # Fill in defaults for missing settings
            defaults = self.default_configs.get(provider, {})
            for key, default_value in defaults.items():
                if key not in settings:
                    settings[key] = default_value
            
            return settings
            
        except Exception as e:
            self.logger.error(f"Error getting {provider} settings: {e}")
            return self.default_configs.get(provider, {}).copy()
    
    def _set_provider_settings(self, provider: str, settings: Dict[str, Any]) -> bool:
        """
        Set settings for a specific provider.
        
        Args:
            provider: Provider name
            settings: Dictionary of settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert settings to environment variables
            prefix = provider.upper() + '_'
            env_vars = {}
            
            for key, value in settings.items():
                env_key = f"{prefix}{key.upper()}"
                env_vars[env_key] = str(value)
            
            # Validate settings
            for env_key, env_value in env_vars.items():
                is_valid, error = self.env_manager.validate_env_var(env_key, env_value)
                if not is_valid:
                    self.logger.error(f"Invalid setting {env_key}: {error}")
                    return False
            
            # Set environment variables
            for env_key, env_value in env_vars.items():
                self.env_manager.set_env_var(env_key, env_value)
            
            # Save to .env file
            all_vars = self.env_manager.env_vars.copy()
            all_vars.update(env_vars)
            
            if self.env_manager.write_env_file(all_vars):
                self.logger.info(f"Successfully updated {provider} settings")
                return True
            else:
                self.logger.error(f"Failed to save {provider} settings to file")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting {provider} settings: {e}")
            return False
    
    async def test_provider_connection(self, provider: str) -> Tuple[bool, str]:
        """
        Test connection to a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Get current settings
            settings = self._get_provider_settings(provider)
            
            # Check if API key is configured (for providers that need it)
            if provider in ['openai', 'anthropic', 'openrouter', 'deepseek']:
                api_key = settings.get('API_KEY', '')
                if not api_key or api_key == f'your_{provider}_api_key_here':
                    return False, f"{provider.title()} API key not configured"
            
            # Convert settings to provider factory format (lowercase keys)
            provider_config = {}
            for key, value in settings.items():
                # Convert uppercase keys to lowercase
                config_key = key.lower()
                
                # Handle special conversions
                if config_key == 'api_key':
                    provider_config['api_key'] = value
                elif config_key == 'max_tokens':
                    try:
                        provider_config['max_tokens'] = int(value)
                    except (ValueError, TypeError):
                        provider_config['max_tokens'] = 4000
                elif config_key in ['temperature', 'top_p', 'frequency_penalty', 'presence_penalty']:
                    try:
                        provider_config[config_key] = float(value)
                    except (ValueError, TypeError):
                        provider_config[config_key] = 0.7 if config_key == 'temperature' else 1.0
                elif config_key == 'top_k':
                    try:
                        provider_config['top_k'] = int(value)
                    except (ValueError, TypeError):
                        provider_config['top_k'] = 40
                else:
                    # For other keys like model, host, http_referer, x_title
                    provider_config[config_key] = value
            
            # Create provider instance
            provider_instance = await self.provider_factory.create_provider(provider, provider_config)
            
            # Test health
            if await provider_instance.check_health():
                if hasattr(provider_instance, 'close'):
                    await provider_instance.close()
                return True, f"{provider.title()} connection successful"
            else:
                if hasattr(provider_instance, 'close'):
                    await provider_instance.close()
                return False, f"{provider.title()} health check failed"
                
        except Exception as e:
            self.logger.error(f"Error testing {provider} connection: {e}")
            return False, f"Connection test failed: {str(e)}"
    
    async def get_available_providers(self) -> List[str]:
        """
        Get list of available providers based on configuration.
        
        Returns:
            List of available provider names
        """
        try:
            return await self.provider_factory.get_available_providers()
        except Exception as e:
            self.logger.error(f"Error getting available providers: {e}")
            return []
    
    def reset_to_defaults(self, provider: str) -> bool:
        """
        Reset provider settings to defaults.
        
        Args:
            provider: Provider name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            defaults = self.default_configs.get(provider, {})
            if not defaults:
                self.logger.error(f"No defaults found for provider: {provider}")
                return False
            
            return self._set_provider_settings(provider, defaults)
            
        except Exception as e:
            self.logger.error(f"Error resetting {provider} to defaults: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """
        Get settings for all providers.
        
        Returns:
            Dictionary with provider names as keys and their settings as values
        """
        all_settings = {}
        
        for provider in ['openai', 'anthropic', 'ollama', 'openrouter', 'deepseek']:
            all_settings[provider] = self._get_provider_settings(provider)
        
        return all_settings
    
    def export_settings(self, file_path: str) -> bool:
        """
        Export all AI settings to a file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            
            settings = self.get_all_settings()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Settings exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """
        Import AI settings from a file.
        
        Args:
            file_path: Path to import file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Import settings for each provider
            success = True
            for provider, provider_settings in settings.items():
                if provider in ['openai', 'anthropic', 'ollama', 'openrouter', 'deepseek']:
                    if not self._set_provider_settings(provider, provider_settings):
                        success = False
                        self.logger.error(f"Failed to import settings for {provider}")
            
            if success:
                self.logger.info(f"Settings imported from {file_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            return False
    
    def get_provider_status(self, provider: str) -> Dict[str, Any]:
        """
        Get status information for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Dictionary with provider status information
        """
        try:
            settings = self._get_provider_settings(provider)
            
            # Check if configured
            configured = True
            if provider in ['openai', 'anthropic', 'openrouter', 'deepseek']:
                api_key = settings.get('API_KEY', '')
                configured = bool(api_key and api_key != f'your_{provider}_api_key_here')
            
            return {
                'name': provider.title(),
                'configured': configured,
                'settings': settings,
                'available': provider in ['openai', 'anthropic', 'ollama', 'openrouter', 'deepseek']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting {provider} status: {e}")
            return {
                'name': provider.title(),
                'configured': False,
                'settings': {},
                'available': False,
                'error': str(e)
            }
    
    async def test_all_providers(self) -> Dict[str, Tuple[bool, str]]:
        """
        Test connections to all configured providers.
        
        Returns:
            Dictionary with provider names as keys and (success, message) tuples as values
        """
        results = {}
        
        for provider in ['openai', 'anthropic', 'ollama', 'openrouter', 'deepseek']:
            try:
                results[provider] = await self.test_provider_connection(provider)
            except Exception as e:
                results[provider] = (False, f"Test failed: {str(e)}")
        
        return results

    # AI Function Assignment Methods
    
    def get_ai_function_assignments(self) -> Dict[str, Dict[str, str]]:
        """
        Get current AI function assignments.
        
        Returns:
            Dictionary with function names as keys and provider/model info as values
        """
        try:
            env_vars = self.env_manager.env_vars
            
            assignments = {
                'embedding': {
                    'provider': env_vars.get('AI_EMBEDDING_PROVIDER', 'openai'),
                    'model': env_vars.get('AI_EMBEDDING_MODEL', 'text-embedding-3-small')
                },
                'chat': {
                    'provider': env_vars.get('AI_CHAT_PROVIDER', 'ollama'),
                    'model': env_vars.get('AI_CHAT_MODEL', 'llama3.2:latest')
                },
                'task': {
                    'provider': env_vars.get('AI_TASK_PROVIDER', 'ollama'),
                    'model': env_vars.get('AI_TASK_MODEL', 'llama3.2:latest')
                },
                'description': {
                    'provider': env_vars.get('AI_DESCRIPTION_PROVIDER', 'ollama'),
                    'model': env_vars.get('AI_DESCRIPTION_MODEL', 'llama3.2:latest')
                },
                'agent': {
                    'provider': env_vars.get('AI_AGENT_PROVIDER', 'ollama'),
                    'model': env_vars.get('AI_AGENT_MODEL', 'llama3.2:latest')
                }
            }
            
            return assignments
            
        except Exception as e:
            self.logger.error(f"Error getting AI function assignments: {e}")
            return {}
    
    def set_ai_function_assignment(self, function: str, provider: str, model: str) -> bool:
        """
        Set AI function assignment.
        
        Args:
            function: Function name (embedding, chat, task, description, agent)
            provider: Provider name (openai, anthropic, ollama, openrouter, deepseek)
            model: Model name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            function_map = {
                'embedding': ('AI_EMBEDDING_PROVIDER', 'AI_EMBEDDING_MODEL'),
                'chat': ('AI_CHAT_PROVIDER', 'AI_CHAT_MODEL'),
                'task': ('AI_TASK_PROVIDER', 'AI_TASK_MODEL'),
                'description': ('AI_DESCRIPTION_PROVIDER', 'AI_DESCRIPTION_MODEL'),
                'agent': ('AI_AGENT_PROVIDER', 'AI_AGENT_MODEL')
            }
            
            if function not in function_map:
                self.logger.error(f"Unknown function: {function}")
                return False
            
            provider_key, model_key = function_map[function]
            
            # Set environment variables
            self.env_manager.set_env_var(provider_key, provider)
            self.env_manager.set_env_var(model_key, model)
            
            # Save to .env file
            if self.env_manager.write_env_file(self.env_manager.env_vars):
                self.logger.info(f"Updated {function} assignment: {provider}/{model}")
                return True
            else:
                self.logger.error(f"Failed to save {function} assignment")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting {function} assignment: {e}")
            return False
    
    def get_available_models_for_provider(self, provider: str) -> List[str]:
        """
        Get available models for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of available model names
        """
        model_lists = {
            'openai': [
                'gpt-4',
                'gpt-4-turbo',
                'gpt-3.5-turbo',
                'text-embedding-3-small',
                'text-embedding-3-large',
                'text-embedding-ada-002'
            ],
            'anthropic': [
                'claude-3-opus-20240229',
                'claude-3-sonnet-20240229',
                'claude-3-haiku-20240307'
            ],
            'ollama': [
                'llama3.2:latest',
                'llama2',
                'codellama',
                'mistral',
                'neural-chat',
                'all-minilm',
                'nomic-embed-text'
            ],
            'openrouter': [
                'openai/gpt-4',
                'openai/gpt-3.5-turbo',
                'anthropic/claude-3-opus',
                'anthropic/claude-3-sonnet',
                'meta-llama/llama-2-70b-chat',
                'google/gemini-pro'
            ],
            'deepseek': [
                'deepseek-chat',
                'deepseek-reasoner'
            ]
        }
        
        return model_lists.get(provider, [])
    
    def get_function_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions for each AI function.
        
        Returns:
            Dictionary with function names as keys and descriptions as values
        """
        return {
            'embedding': 'Document indexing and semantic search - Used for finding relevant code files',
            'chat': 'Interactive chat with codebase - Used for asking questions about your code',
            'task': 'AI-powered task management - Used for generating task descriptions and analysis',
            'description': 'File and project description generation - Used for creating summaries',
            'agent': 'Autonomous AI agent mode - Used for complex multi-step operations'
        } 