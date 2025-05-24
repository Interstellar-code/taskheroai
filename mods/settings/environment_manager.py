"""
Environment Manager for TaskHero AI.

Handles environment variables and environment-specific configuration.
"""

import os
import re
import shutil
from typing import Any, Dict, Optional, List, Tuple
from pathlib import Path
from datetime import datetime

from ..core import BaseManager


class EnvironmentManager(BaseManager):
    """Manager for environment variables and environment configuration."""
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialize the environment manager.
        
        Args:
            env_file: Path to the .env file
        """
        super().__init__("EnvironmentManager")
        self.env_file = Path(env_file)
        self.env_vars: Dict[str, str] = {}
        self.backup_dir = Path(".env_backups")
    
    def _perform_initialization(self) -> None:
        """Initialize the environment manager."""
        self.load_env_file()
        self.update_status("env_file_loaded", True)
    
    def load_env_file(self) -> Dict[str, str]:
        """
        Load environment variables from .env file.
        
        Returns:
            Dictionary of environment variables
        """
        self.env_vars = {}
        
        if not self.env_file.exists():
            self.logger.warning(f"Environment file {self.env_file} does not exist")
            return self.env_vars
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.env_vars[key] = value
            
            self.logger.info(f"Loaded {len(self.env_vars)} environment variables from {self.env_file}")
            return self.env_vars
            
        except Exception as e:
            self.logger.error(f"Error loading environment file: {e}")
            return {}
    
    def write_env_file(self, variables: Dict[str, str], backup: bool = True) -> bool:
        """
        Write environment variables to .env file.
        
        Args:
            variables: Dictionary of environment variables to write
            backup: Whether to create a backup before writing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup if requested
            if backup and self.env_file.exists():
                self.backup_env_file()
            
            # Ensure parent directory exists
            self.env_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write("# ========================================\n")
                f.write("# TaskHero AI Configuration\n")
                f.write("# ========================================\n")
                f.write(f"# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Group variables by provider
                openai_vars = {k: v for k, v in variables.items() if k.startswith('OPENAI_')}
                anthropic_vars = {k: v for k, v in variables.items() if k.startswith('ANTHROPIC_')}
                ollama_vars = {k: v for k, v in variables.items() if k.startswith('OLLAMA_')}
                openrouter_vars = {k: v for k, v in variables.items() if k.startswith('OPENROUTER_')}
                ai_vars = {k: v for k, v in variables.items() if k.startswith('AI_') or k.startswith('CHAT_')}
                other_vars = {k: v for k, v in variables.items() 
                             if not any(k.startswith(prefix) for prefix in 
                                      ['OPENAI_', 'ANTHROPIC_', 'OLLAMA_', 'OPENROUTER_', 'AI_', 'CHAT_'])}
                
                # Write OpenAI section
                if openai_vars:
                    f.write("# ========================================\n")
                    f.write("# OPENAI CONFIGURATION\n")
                    f.write("# ========================================\n")
                    for key, value in sorted(openai_vars.items()):
                        f.write(f"{key}={value}\n")
                    f.write("\n")
                
                # Write Anthropic section
                if anthropic_vars:
                    f.write("# ========================================\n")
                    f.write("# ANTHROPIC CONFIGURATION\n")
                    f.write("# ========================================\n")
                    for key, value in sorted(anthropic_vars.items()):
                        f.write(f"{key}={value}\n")
                    f.write("\n")
                
                # Write Ollama section
                if ollama_vars:
                    f.write("# ========================================\n")
                    f.write("# OLLAMA CONFIGURATION\n")
                    f.write("# ========================================\n")
                    for key, value in sorted(ollama_vars.items()):
                        f.write(f"{key}={value}\n")
                    f.write("\n")
                
                # Write OpenRouter section
                if openrouter_vars:
                    f.write("# ========================================\n")
                    f.write("# OPENROUTER CONFIGURATION\n")
                    f.write("# ========================================\n")
                    for key, value in sorted(openrouter_vars.items()):
                        f.write(f"{key}={value}\n")
                    f.write("\n")
                
                # Write AI general settings
                if ai_vars:
                    f.write("# ========================================\n")
                    f.write("# AI GENERAL SETTINGS\n")
                    f.write("# ========================================\n")
                    for key, value in sorted(ai_vars.items()):
                        f.write(f"{key}={value}\n")
                    f.write("\n")
                
                # Write other variables
                if other_vars:
                    f.write("# ========================================\n")
                    f.write("# OTHER SETTINGS\n")
                    f.write("# ========================================\n")
                    for key, value in sorted(other_vars.items()):
                        f.write(f"{key}={value}\n")
                    f.write("\n")
            
            self.env_vars = variables.copy()
            self.logger.info(f"Successfully wrote {len(variables)} environment variables to {self.env_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing environment file: {e}")
            return False
    
    def backup_env_file(self) -> Optional[str]:
        """
        Create a backup of the current .env file.
        
        Returns:
            Path to backup file if successful, None otherwise
        """
        if not self.env_file.exists():
            self.logger.warning("No .env file to backup")
            return None
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f".env.backup.{timestamp}"
            
            # Copy file
            shutil.copy2(self.env_file, backup_path)
            
            self.logger.info(f"Created backup: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return None
    
    def restore_env_file(self, backup_path: str) -> bool:
        """
        Restore .env file from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful, False otherwise
        """
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            self.logger.error(f"Backup file {backup_path} does not exist")
            return False
        
        try:
            # Create backup of current file before restore
            if self.env_file.exists():
                self.backup_env_file()
            
            # Copy backup to .env
            shutil.copy2(backup_file, self.env_file)
            
            # Reload variables
            self.load_env_file()
            
            self.logger.info(f"Restored .env file from {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring from backup: {e}")
            return False
    
    def get_env_var(self, key: str, default: str = "") -> str:
        """
        Get environment variable value.
        
        Args:
            key: Environment variable key
            default: Default value if key not found
            
        Returns:
            Environment variable value
        """
        # Check loaded variables first, then OS environment
        return self.env_vars.get(key, os.getenv(key, default))
    
    def set_env_var(self, key: str, value: str) -> None:
        """
        Set environment variable value.
        
        Args:
            key: Environment variable key
            value: Environment variable value
        """
        self.env_vars[key] = value
        os.environ[key] = value
    
    def validate_env_var(self, key: str, value: str) -> Tuple[bool, str]:
        """
        Validate environment variable value.
        
        Args:
            key: Environment variable key
            value: Environment variable value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation rules
        if not key:
            return False, "Key cannot be empty"
        
        if not re.match(r'^[A-Z_][A-Z0-9_]*$', key):
            return False, "Key must contain only uppercase letters, numbers, and underscores"
        
        # Provider-specific validation
        if key.endswith('_API_KEY'):
            if not value or value == 'your_api_key_here':
                return False, "API key cannot be empty or placeholder"
            if len(value) < 10:
                return False, "API key seems too short"
        
        if key.endswith('_HOST'):
            if not value.startswith(('http://', 'https://')):
                return False, "Host must start with http:// or https://"
        
        if key.endswith('_TEMPERATURE'):
            try:
                temp = float(value)
                if not 0.0 <= temp <= 2.0:
                    return False, "Temperature must be between 0.0 and 2.0"
            except ValueError:
                return False, "Temperature must be a valid number"
        
        if key.endswith('_MAX_TOKENS'):
            try:
                tokens = int(value)
                if tokens <= 0:
                    return False, "Max tokens must be positive"
                if tokens > 100000:
                    return False, "Max tokens seems too large"
            except ValueError:
                return False, "Max tokens must be a valid integer"
        
        return True, ""
    
    def get_provider_vars(self, provider: str) -> Dict[str, str]:
        """
        Get all environment variables for a specific provider.
        
        Args:
            provider: Provider name (openai, anthropic, ollama, openrouter)
            
        Returns:
            Dictionary of provider-specific variables
        """
        prefix = provider.upper() + '_'
        return {k: v for k, v in self.env_vars.items() if k.startswith(prefix)}
    
    def set_provider_vars(self, provider: str, variables: Dict[str, str]) -> bool:
        """
        Set environment variables for a specific provider.
        
        Args:
            provider: Provider name
            variables: Dictionary of variables to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            prefix = provider.upper() + '_'
            
            # Validate all variables first
            for key, value in variables.items():
                full_key = f"{prefix}{key}" if not key.startswith(prefix) else key
                is_valid, error = self.validate_env_var(full_key, value)
                if not is_valid:
                    self.logger.error(f"Validation failed for {full_key}: {error}")
                    return False
            
            # Set variables
            for key, value in variables.items():
                full_key = f"{prefix}{key}" if not key.startswith(prefix) else key
                self.set_env_var(full_key, value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting provider variables: {e}")
            return False
    
    def get_env_bool(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean value from environment variables.
        
        Args:
            key: Environment variable key
            default: Default value if key not found
            
        Returns:
            Boolean value
        """
        value = self.get_env_var(key, str(default)).upper()
        return value in ("TRUE", "YES", "1", "Y", "T")
    
    def list_backups(self) -> List[str]:
        """
        List available backup files.
        
        Returns:
            List of backup file paths
        """
        if not self.backup_dir.exists():
            return []
        
        try:
            backups = []
            for backup_file in self.backup_dir.glob(".env.backup.*"):
                backups.append(str(backup_file))
            
            return sorted(backups, reverse=True)  # Most recent first
            
        except Exception as e:
            self.logger.error(f"Error listing backups: {e}")
            return [] 