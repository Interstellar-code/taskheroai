"""
Response Formatter for TaskHero AI.

Provides elegant formatting for AI chat responses with syntax highlighting,
structured output, and improved readability.
"""

import re
import os
from typing import List, Dict, Any, Optional
from colorama import Fore, Style, Back


class ResponseFormatter:
    """Formats AI responses for elegant display in the terminal."""
    
    def __init__(self):
        """Initialize the response formatter."""
        self.code_languages = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'cpp': 'cpp',
            'c++': 'cpp',
            'csharp': 'cs',
            'c#': 'cs',
            'php': 'php',
            'ruby': 'rb',
            'go': 'go',
            'rust': 'rs',
            'swift': 'swift',
            'kotlin': 'kt',
            'scala': 'scala',
            'html': 'html',
            'css': 'css',
            'scss': 'scss',
            'json': 'json',
            'xml': 'xml',
            'yaml': 'yaml',
            'yml': 'yaml',
            'markdown': 'md',
            'bash': 'sh',
            'shell': 'sh',
            'sql': 'sql'
        }
    
    def format_response(self, response: str, relevant_files: List[str] = None) -> str:
        """
        Format an AI response for elegant display.
        
        Args:
            response: The AI response text
            relevant_files: List of relevant files (optional)
            
        Returns:
            Formatted response string
        """
        if not response:
            return f"{Fore.RED}No response received{Style.RESET_ALL}"
        
        # Format the main response
        formatted_response = self._format_main_content(response)
        
        # Add relevant files section if provided
        if relevant_files:
            formatted_response += self._format_relevant_files(relevant_files)
        
        return formatted_response
    
    def _format_main_content(self, content: str) -> str:
        """Format the main response content."""
        # Split content into sections
        sections = self._split_into_sections(content)
        formatted_sections = []
        
        for section in sections:
            if self._is_code_block(section):
                formatted_sections.append(self._format_code_block(section))
            elif self._is_file_structure(section):
                formatted_sections.append(self._format_file_structure(section))
            elif self._is_list(section):
                formatted_sections.append(self._format_list(section))
            else:
                formatted_sections.append(self._format_text(section))
        
        return '\n'.join(formatted_sections)
    
    def _split_into_sections(self, content: str) -> List[str]:
        """Split content into logical sections."""
        # Split by code blocks first
        code_block_pattern = r'```[\s\S]*?```'
        sections = []
        last_end = 0
        
        for match in re.finditer(code_block_pattern, content):
            # Add text before code block
            if match.start() > last_end:
                text_section = content[last_end:match.start()].strip()
                if text_section:
                    sections.append(text_section)
            
            # Add code block
            sections.append(match.group())
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(content):
            remaining = content[last_end:].strip()
            if remaining:
                sections.append(remaining)
        
        return sections
    
    def _is_code_block(self, section: str) -> bool:
        """Check if section is a code block."""
        return section.strip().startswith('```') and section.strip().endswith('```')
    
    def _is_file_structure(self, section: str) -> bool:
        """Check if section contains file structure."""
        lines = section.split('\n')
        structure_indicators = ['├──', '└──', '│', '/', '\\', '.py', '.js', '.md']
        return any(indicator in line for line in lines for indicator in structure_indicators)
    
    def _is_list(self, section: str) -> bool:
        """Check if section is a list."""
        lines = section.split('\n')
        list_indicators = ['•', '-', '*', '1.', '2.', '3.']
        return any(line.strip().startswith(indicator) for line in lines for indicator in list_indicators)
    
    def _format_code_block(self, section: str) -> str:
        """Format a code block with syntax highlighting."""
        lines = section.strip().split('\n')
        if len(lines) < 2:
            return section
        
        # Extract language and code
        first_line = lines[0].strip()
        language = first_line[3:].strip() if first_line.startswith('```') else ''
        code_lines = lines[1:-1] if lines[-1].strip() == '```' else lines[1:]
        
        # Format with colors
        formatted = f"\n{Fore.CYAN}┌─ Code Block"
        if language:
            formatted += f" ({language.upper()})"
        formatted += f" {Style.RESET_ALL}\n"
        
        for i, line in enumerate(code_lines):
            line_num = f"{i+1:3d}"
            formatted += f"{Fore.BLUE}│{Fore.YELLOW}{line_num}{Fore.BLUE}│{Style.RESET_ALL} {line}\n"
        
        formatted += f"{Fore.CYAN}└{'─' * 50}{Style.RESET_ALL}\n"
        return formatted
    
    def _format_file_structure(self, section: str) -> str:
        """Format file structure with tree styling."""
        lines = section.split('\n')
        formatted = f"\n{Fore.GREEN}📁 File Structure:{Style.RESET_ALL}\n"
        formatted += f"{Fore.GREEN}{'─' * 40}{Style.RESET_ALL}\n"
        
        for line in lines:
            if not line.strip():
                continue
            
            # Color different parts of the tree
            if '├──' in line or '└──' in line:
                # Directory/file entries
                parts = line.split('──')
                if len(parts) >= 2:
                    prefix = parts[0] + '──'
                    filename = parts[1].strip()
                    
                    if '.' in filename and not filename.endswith('/'):
                        # File
                        formatted += f"{Fore.BLUE}{prefix}{Fore.WHITE}{filename}{Style.RESET_ALL}\n"
                    else:
                        # Directory
                        formatted += f"{Fore.BLUE}{prefix}{Fore.YELLOW}{filename}{Style.RESET_ALL}\n"
                else:
                    formatted += f"{Fore.BLUE}{line}{Style.RESET_ALL}\n"
            elif line.strip().endswith('/'):
                # Directory
                formatted += f"{Fore.YELLOW}{line}{Style.RESET_ALL}\n"
            else:
                # Regular line
                formatted += f"{Fore.WHITE}{line}{Style.RESET_ALL}\n"
        
        formatted += f"{Fore.GREEN}{'─' * 40}{Style.RESET_ALL}\n"
        return formatted
    
    def _format_list(self, section: str) -> str:
        """Format lists with better styling."""
        lines = section.split('\n')
        formatted = ""
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted += "\n"
                continue
            
            # Format different list types
            if stripped.startswith('•'):
                formatted += f"  {Fore.CYAN}•{Style.RESET_ALL} {stripped[1:].strip()}\n"
            elif stripped.startswith('-'):
                formatted += f"  {Fore.CYAN}▸{Style.RESET_ALL} {stripped[1:].strip()}\n"
            elif stripped.startswith('*'):
                formatted += f"  {Fore.CYAN}★{Style.RESET_ALL} {stripped[1:].strip()}\n"
            elif re.match(r'^\d+\.', stripped):
                num_part = re.match(r'^(\d+\.)', stripped).group(1)
                rest = stripped[len(num_part):].strip()
                formatted += f"  {Fore.YELLOW}{num_part}{Style.RESET_ALL} {rest}\n"
            else:
                formatted += f"{line}\n"
        
        return formatted
    
    def _format_text(self, section: str) -> str:
        """Format regular text with emphasis."""
        # Add some basic formatting for emphasis
        text = section
        
        # Bold text (markdown style)
        text = re.sub(r'\*\*(.*?)\*\*', f'{Style.BRIGHT}\\1{Style.RESET_ALL}', text)
        
        # Italic text (markdown style)
        text = re.sub(r'\*(.*?)\*', f'{Style.DIM}\\1{Style.RESET_ALL}', text)
        
        # Inline code
        text = re.sub(r'`(.*?)`', f'{Fore.CYAN}\\1{Style.RESET_ALL}', text)
        
        return text
    
    def _format_relevant_files(self, relevant_files: List[str]) -> str:
        """Format the relevant files section."""
        if not relevant_files:
            return ""
        
        formatted = f"\n{Fore.YELLOW}📁 Relevant Files:{Style.RESET_ALL}\n"
        formatted += f"{Fore.YELLOW}{'─' * 30}{Style.RESET_ALL}\n"
        
        for i, file_path in enumerate(relevant_files[:8]):  # Limit to 8 files
            # Get relative path for display
            filename = os.path.basename(file_path)
            dir_path = os.path.dirname(file_path)
            
            if dir_path:
                formatted += f"  {Fore.CYAN}{i+1:2d}.{Style.RESET_ALL} {Fore.BLUE}{dir_path}/{Style.RESET_ALL}{Fore.WHITE}{filename}{Style.RESET_ALL}\n"
            else:
                formatted += f"  {Fore.CYAN}{i+1:2d}.{Style.RESET_ALL} {Fore.WHITE}{filename}{Style.RESET_ALL}\n"
        
        if len(relevant_files) > 8:
            formatted += f"  {Fore.YELLOW}... and {len(relevant_files) - 8} more files{Style.RESET_ALL}\n"
        
        return formatted
    
    def format_error(self, error_message: str) -> str:
        """Format error messages."""
        return f"\n{Fore.RED}❌ Error: {error_message}{Style.RESET_ALL}\n"
    
    def format_success(self, message: str) -> str:
        """Format success messages."""
        return f"\n{Fore.GREEN}✅ {message}{Style.RESET_ALL}\n"
    
    def format_warning(self, message: str) -> str:
        """Format warning messages."""
        return f"\n{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}\n"
