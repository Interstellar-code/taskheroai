"""JavaScript/TypeScript code analyzer for enhanced metadata extraction."""

import re
from pathlib import Path
from typing import Any, Dict, List

from .base_analyzer import BaseAnalyzer


class JavaScriptAnalyzer(BaseAnalyzer):
    """Analyzer for JavaScript and TypeScript code files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.js', '.jsx', '.ts', '.tsx', '.mjs'}
        self.language_name = 'javascript'
    
    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file content."""
        return {
            'functions': self._extract_functions(content),
            'classes': self._extract_classes(content),
            'imports': self._extract_imports(content),
            'exports': self._extract_exports(content),
            'patterns': self._extract_js_patterns(content)
        }
    
    def detect_language(self, content: str, file_path: Path) -> str:
        """Detect if this is JavaScript or TypeScript."""
        if file_path.suffix.lower() in {'.ts', '.tsx'}:
            return 'typescript'
        
        # Check for TypeScript-specific syntax
        ts_indicators = [
            r':\s*\w+\s*[=;]',  # Type annotations
            r'interface\s+\w+',  # Interface declarations
            r'type\s+\w+\s*=',   # Type aliases
            r'<\w+>',            # Generic types
            r'as\s+\w+',         # Type assertions
        ]
        
        for pattern in ts_indicators:
            if re.search(pattern, content):
                return 'typescript'
        
        return 'javascript'
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions from JavaScript/TypeScript."""
        functions = []
        lines = content.split('\n')
        
        # Function declaration patterns
        patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)',  # function name()
            r'(\w+)\s*:\s*function\s*\(([^)]*)\)',  # name: function()
            r'(\w+)\s*=\s*function\s*\(([^)]*)\)',  # name = function()
            r'(\w+)\s*=\s*\(([^)]*)\)\s*=>', # name = () =>
            r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>', # const name = () =>
            r'let\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>', # let name = () =>
            r'var\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>', # var name = () =>
            r'async\s+function\s+(\w+)\s*\(([^)]*)\)', # async function
            r'(\w+)\s*\(([^)]*)\)\s*{', # method in object/class
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in patterns:
                match = re.search(pattern, stripped)
                if match:
                    func_name = match.group(1)
                    args_str = match.group(2) if len(match.groups()) > 1 else ''
                    
                    # Parse arguments
                    args = []
                    if args_str.strip():
                        args = [arg.strip().split(':')[0].strip() for arg in args_str.split(',')]
                        args = [arg for arg in args if arg]  # Remove empty args
                    
                    # Determine function type
                    func_type = 'function'
                    if 'async' in stripped:
                        func_type = 'async_function'
                    elif '=>' in stripped:
                        func_type = 'arrow_function'
                    
                    functions.append({
                        'name': func_name,
                        'args': args,
                        'line_number': i,
                        'signature': stripped,
                        'type': func_type,
                        'is_async': 'async' in stripped,
                        'docstring': self._extract_jsdoc(lines, i - 1)
                    })
                    break
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions from JavaScript/TypeScript."""
        classes = []
        lines = content.split('\n')
        
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        
        for i, line in enumerate(lines, 1):
            match = re.search(class_pattern, line.strip())
            if match:
                class_name = match.group(1)
                extends = match.group(2) if match.group(2) else None
                
                # Extract methods from class body
                methods = self._extract_class_methods(lines, i)
                
                classes.append({
                    'name': class_name,
                    'line_number': i,
                    'extends': extends,
                    'methods': methods,
                    'docstring': self._extract_jsdoc(lines, i - 1)
                })
        
        return classes
    
    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract import statements from JavaScript/TypeScript."""
        imports = []
        lines = content.split('\n')
        
        import_patterns = [
            r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # import name from 'module'
            r'import\s+{\s*([^}]+)\s*}\s+from\s+[\'"]([^\'"]+)[\'"]',  # import { name } from 'module'
            r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # import * as name from 'module'
            r'const\s+(\w+)\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',  # const name = require('module')
            r'import\s+[\'"]([^\'"]+)[\'"]',  # import 'module' (side effect)
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in import_patterns:
                match = re.search(pattern, stripped)
                if match:
                    if len(match.groups()) == 2:
                        name, module = match.groups()
                        imports.append({
                            'name': name,
                            'module': module,
                            'line_number': i,
                            'statement': stripped,
                            'type': 'import'
                        })
                    elif len(match.groups()) == 1:
                        # Side effect import
                        module = match.group(1)
                        imports.append({
                            'name': None,
                            'module': module,
                            'line_number': i,
                            'statement': stripped,
                            'type': 'side_effect_import'
                        })
                    break
        
        return imports
    
    def _extract_exports(self, content: str) -> List[Dict[str, Any]]:
        """Extract export statements from JavaScript/TypeScript."""
        exports = []
        lines = content.split('\n')
        
        export_patterns = [
            r'export\s+function\s+(\w+)',  # export function name
            r'export\s+class\s+(\w+)',     # export class name
            r'export\s+const\s+(\w+)',     # export const name
            r'export\s+let\s+(\w+)',       # export let name
            r'export\s+var\s+(\w+)',       # export var name
            r'export\s+{\s*([^}]+)\s*}',   # export { name1, name2 }
            r'export\s+default\s+(\w+)',   # export default name
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in export_patterns:
                match = re.search(pattern, stripped)
                if match:
                    name = match.group(1)
                    
                    # Handle multiple exports in braces
                    if '{' in pattern:
                        names = [n.strip() for n in name.split(',')]
                        for export_name in names:
                            exports.append({
                                'name': export_name,
                                'line_number': i,
                                'type': 'named_export'
                            })
                    else:
                        export_type = 'default_export' if 'default' in stripped else 'named_export'
                        exports.append({
                            'name': name,
                            'line_number': i,
                            'type': export_type
                        })
                    break
        
        return exports
    
    def _extract_js_patterns(self, content: str) -> List[str]:
        """Extract JavaScript/TypeScript specific patterns."""
        patterns = self.extract_patterns(content)
        
        # Check for specific JS/TS patterns
        if 'Promise' in content or '.then(' in content or '.catch(' in content:
            patterns.append('promises')
        if 'async' in content and 'await' in content:
            patterns.append('async_await')
        if 'React' in content or 'jsx' in content.lower():
            patterns.append('react')
        if 'Vue' in content or 'vue' in content.lower():
            patterns.append('vue')
        if 'interface ' in content or 'type ' in content:
            patterns.append('typescript_types')
        if 'Observable' in content or 'rxjs' in content.lower():
            patterns.append('reactive_programming')
        if '.map(' in content or '.filter(' in content or '.reduce(' in content:
            patterns.append('functional_programming')
        
        return list(set(patterns))
    
    def _extract_class_methods(self, lines: List[str], class_start: int) -> List[Dict[str, Any]]:
        """Extract methods from a class definition."""
        methods = []
        in_class = False
        brace_count = 0
        
        for i in range(class_start - 1, len(lines)):
            line = lines[i].strip()
            
            if not in_class and '{' in line:
                in_class = True
                brace_count = line.count('{') - line.count('}')
                continue
            
            if in_class:
                brace_count += line.count('{') - line.count('}')
                
                # Look for method definitions
                method_patterns = [
                    r'(\w+)\s*\([^)]*\)\s*{',  # methodName() {
                    r'async\s+(\w+)\s*\([^)]*\)\s*{',  # async methodName() {
                    r'static\s+(\w+)\s*\([^)]*\)\s*{',  # static methodName() {
                ]
                
                for pattern in method_patterns:
                    match = re.search(pattern, line)
                    if match:
                        method_name = match.group(1)
                        methods.append({
                            'name': method_name,
                            'line_number': i + 1,
                            'is_async': 'async' in line,
                            'is_static': 'static' in line
                        })
                        break
                
                if brace_count <= 0:
                    break
        
        return methods
    
    def _extract_jsdoc(self, lines: List[str], line_index: int) -> str:
        """Extract JSDoc comment before a function/class."""
        if line_index < 0:
            return None
        
        # Look backwards for JSDoc comment
        for i in range(line_index, max(-1, line_index - 10), -1):
            line = lines[i].strip()
            if line.startswith('/**'):
                # Found start of JSDoc, collect until */
                jsdoc_lines = []
                for j in range(i, min(len(lines), i + 20)):
                    jsdoc_lines.append(lines[j])
                    if '*/' in lines[j]:
                        break
                return '\n'.join(jsdoc_lines)
            elif line and not line.startswith('//') and not line.startswith('*'):
                # Hit non-comment line, stop looking
                break
        
        return None
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if a line is a JavaScript comment."""
        return line.startswith('//') or line.startswith('/*') or line.startswith('*')
