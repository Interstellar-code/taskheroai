"""Base analyzer class for code analysis."""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class BaseAnalyzer(ABC):
    """Base class for code analyzers."""
    
    def __init__(self):
        self.supported_extensions: Set[str] = set()
        self.language_name: str = "unknown"
    
    @abstractmethod
    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze file content and extract metadata.
        
        Args:
            content: File content as string
            file_path: Path to the file being analyzed
            
        Returns:
            Dictionary containing analysis results with keys:
            - functions: List of function definitions
            - classes: List of class definitions  
            - imports: List of import statements
            - exports: List of exported items
            - patterns: List of identified code patterns
        """
        pass
    
    def can_analyze(self, file_path: Path) -> bool:
        """Check if this analyzer can handle the given file."""
        return file_path.suffix.lower() in self.supported_extensions
    
    def detect_language(self, content: str, file_path: Path) -> str:
        """Detect the programming language of the file."""
        return self.language_name
    
    def calculate_complexity(self, content: str) -> float:
        """Calculate a basic complexity score for the file."""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Basic complexity metrics
        complexity_indicators = [
            len([line for line in non_empty_lines if 'if ' in line or 'elif ' in line]),
            len([line for line in non_empty_lines if 'for ' in line or 'while ' in line]),
            len([line for line in non_empty_lines if 'try:' in line or 'except' in line]),
            len([line for line in non_empty_lines if 'def ' in line or 'class ' in line]),
        ]
        
        total_complexity = sum(complexity_indicators)
        return min(total_complexity / max(len(non_empty_lines), 1) * 10, 10.0)
    
    def count_lines_of_code(self, content: str) -> int:
        """Count non-empty, non-comment lines of code."""
        lines = content.split('\n')
        code_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped and not self._is_comment_line(stripped):
                code_lines += 1
                
        return code_lines
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if a line is a comment (basic implementation)."""
        # Override in subclasses for language-specific comment detection
        return line.startswith('#') or line.startswith('//')
    
    def extract_patterns(self, content: str) -> List[str]:
        """Extract common code patterns."""
        patterns = []
        
        # Common patterns across languages
        if 'class ' in content:
            patterns.append('object_oriented')
        if 'function ' in content or 'def ' in content:
            patterns.append('functional')
        if 'import ' in content or 'require(' in content:
            patterns.append('modular')
        if 'async ' in content or 'await ' in content:
            patterns.append('asynchronous')
        if 'test' in content.lower() or 'spec' in content.lower():
            patterns.append('testing')
        
        return patterns
    
    def _extract_basic_functions(self, content: str, pattern: str) -> List[Dict[str, Any]]:
        """Extract functions using regex pattern."""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            match = re.search(pattern, line)
            if match:
                functions.append({
                    'name': match.group(1) if match.groups() else 'unknown',
                    'line_number': i,
                    'signature': line.strip(),
                    'args': [],
                    'docstring': None
                })
        
        return functions
    
    def _extract_basic_imports(self, content: str, patterns: List[str]) -> List[Dict[str, Any]]:
        """Extract imports using regex patterns."""
        imports = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    imports.append({
                        'module': match.group(1) if match.groups() else line.strip(),
                        'line_number': i,
                        'statement': line.strip(),
                        'type': 'import'
                    })
                    break
        
        return imports
