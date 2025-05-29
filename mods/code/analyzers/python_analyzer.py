"""Python code analyzer for enhanced metadata extraction."""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_analyzer import BaseAnalyzer


class PythonAnalyzer(BaseAnalyzer):
    """Analyzer for Python code files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.py', '.pyw'}
        self.language_name = 'python'
    
    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file content using AST parsing."""
        try:
            tree = ast.parse(content)
            
            return {
                'functions': self._extract_functions(tree, content),
                'classes': self._extract_classes(tree, content),
                'imports': self._extract_imports(tree),
                'exports': self._extract_exports(tree, content),
                'patterns': self._extract_python_patterns(tree, content)
            }
        except SyntaxError as e:
            # Fallback to regex-based analysis for malformed Python
            return self._fallback_analysis(content)
    
    def _extract_functions(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions from AST."""
        functions = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Extract arguments
                args = []
                if node.args.args:
                    args.extend([arg.arg for arg in node.args.args])
                if node.args.kwonlyargs:
                    args.extend([arg.arg for arg in node.args.kwonlyargs])
                
                # Get docstring
                docstring = ast.get_docstring(node)
                
                # Determine function type
                func_type = 'async_function' if isinstance(node, ast.AsyncFunctionDef) else 'function'
                if hasattr(node, 'decorator_list') and node.decorator_list:
                    decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
                    if any(dec in ['property', 'staticmethod', 'classmethod'] for dec in decorators):
                        func_type = 'method'
                
                functions.append({
                    'name': node.name,
                    'args': args,
                    'line_number': node.lineno,
                    'end_line': getattr(node, 'end_lineno', node.lineno),
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'docstring': docstring,
                    'type': func_type,
                    'signature': self._get_function_signature(node, lines),
                    'decorators': [self._get_decorator_name(dec) for dec in getattr(node, 'decorator_list', [])]
                })
        
        return functions
    
    def _extract_classes(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions from AST."""
        classes = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Extract base classes
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(self._get_attribute_name(base))
                
                # Extract methods
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append({
                            'name': item.name,
                            'line_number': item.lineno,
                            'is_async': isinstance(item, ast.AsyncFunctionDef),
                            'args': [arg.arg for arg in item.args.args]
                        })
                
                classes.append({
                    'name': node.name,
                    'line_number': node.lineno,
                    'end_line': getattr(node, 'end_lineno', node.lineno),
                    'bases': bases,
                    'methods': methods,
                    'docstring': ast.get_docstring(node),
                    'decorators': [self._get_decorator_name(dec) for dec in getattr(node, 'decorator_list', [])]
                })
        
        return classes
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import statements from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'module': alias.name,
                        'alias': alias.asname,
                        'line_number': node.lineno,
                        'type': 'import',
                        'statement': f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'line_number': node.lineno,
                        'type': 'from_import',
                        'level': node.level,
                        'statement': f"from {module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                    })
        
        return imports
    
    def _extract_exports(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Extract exported items (functions, classes defined at module level)."""
        exports = []
        
        # Look for __all__ definition
        all_exports = self._find_all_exports(tree)
        if all_exports:
            exports.extend(all_exports)
        
        # Extract top-level definitions
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):  # Public functions
                    exports.append({
                        'name': node.name,
                        'type': 'function',
                        'line_number': node.lineno
                    })
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):  # Public classes
                    exports.append({
                        'name': node.name,
                        'type': 'class',
                        'line_number': node.lineno
                    })
        
        return exports
    
    def _extract_python_patterns(self, tree: ast.AST, content: str) -> List[str]:
        """Extract Python-specific patterns."""
        patterns = self.extract_patterns(content)
        
        # Check for specific Python patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                patterns.append('object_oriented')
            if isinstance(node, ast.AsyncFunctionDef):
                patterns.append('asynchronous')
            if isinstance(node, ast.With):
                patterns.append('context_manager')
            if isinstance(node, ast.Try):
                patterns.append('error_handling')
            if isinstance(node, ast.ListComp) or isinstance(node, ast.DictComp):
                patterns.append('comprehensions')
        
        # Check for decorators
        if '@' in content:
            patterns.append('decorators')
        
        # Check for type hints
        if any(hint in content for hint in ['typing.', 'Type[', 'Optional[', 'Union[']):
            patterns.append('type_hints')
        
        return list(set(patterns))  # Remove duplicates
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback analysis using regex for malformed Python."""
        return {
            'functions': self._extract_basic_functions(content, r'def\s+(\w+)\s*\('),
            'classes': self._extract_basic_functions(content, r'class\s+(\w+)'),
            'imports': self._extract_basic_imports(content, [
                r'import\s+(\w+(?:\.\w+)*)',
                r'from\s+(\w+(?:\.\w+)*)\s+import'
            ]),
            'exports': [],
            'patterns': self.extract_patterns(content)
        }
    
    def _get_decorator_name(self, decorator) -> str:
        """Get decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return self._get_attribute_name(decorator)
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return self._get_attribute_name(decorator.func)
        return 'unknown'
    
    def _get_attribute_name(self, node) -> str:
        """Get full attribute name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        return 'unknown'
    
    def _get_function_signature(self, node, lines: List[str]) -> str:
        """Extract function signature from source lines."""
        if node.lineno <= len(lines):
            return lines[node.lineno - 1].strip()
        return f"def {node.name}(...)"
    
    def _find_all_exports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Find __all__ exports definition."""
        exports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            for item in node.value.elts:
                                if isinstance(item, ast.Str):
                                    exports.append({
                                        'name': item.s,
                                        'type': 'explicit_export',
                                        'line_number': node.lineno
                                    })
        
        return exports
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if a line is a Python comment."""
        return line.startswith('#') or (line.startswith('"""') and line.endswith('"""')) or (line.startswith("'''") and line.endswith("'''"))
