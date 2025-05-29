"""PHP analyzer for enhanced metadata extraction."""

import re
from pathlib import Path
from typing import Any, Dict, List

from .base_analyzer import BaseAnalyzer


class PHPAnalyzer(BaseAnalyzer):
    """Analyzer for PHP code files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.php', '.phtml', '.php3', '.php4', '.php5', '.phps'}
        self.language_name = 'php'
    
    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze PHP file content."""
        return {
            'functions': self._extract_functions(content),
            'classes': self._extract_classes(content),
            'imports': self._extract_imports(content),
            'exports': self._extract_exports(content),
            'patterns': self._extract_php_patterns(content),
            'traits': self._extract_traits(content),
            'interfaces': self._extract_interfaces(content),
            'namespaces': self._extract_namespaces(content)
        }
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract PHP function definitions."""
        functions = []
        lines = content.split('\n')
        
        # PHP function patterns
        patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{;]+))?',  # function name(args): returnType
            r'public\s+function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{;]+))?',  # public function
            r'private\s+function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{;]+))?',  # private function
            r'protected\s+function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{;]+))?',  # protected function
            r'static\s+function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{;]+))?',  # static function
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in patterns:
                match = re.search(pattern, stripped)
                if match:
                    func_name = match.group(1)
                    args_str = match.group(2) if len(match.groups()) > 1 else ''
                    return_type = match.group(3) if len(match.groups()) > 2 and match.group(3) else None
                    
                    # Parse arguments
                    args = self._parse_php_arguments(args_str)
                    
                    # Determine visibility and modifiers
                    visibility = 'public'  # default
                    is_static = False
                    
                    if 'private' in stripped:
                        visibility = 'private'
                    elif 'protected' in stripped:
                        visibility = 'protected'
                    
                    if 'static' in stripped:
                        is_static = True
                    
                    functions.append({
                        'name': func_name,
                        'args': args,
                        'line_number': i,
                        'signature': stripped,
                        'visibility': visibility,
                        'is_static': is_static,
                        'return_type': return_type.strip() if return_type else None,
                        'docstring': self._extract_phpdoc(lines, i - 1)
                    })
                    break
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract PHP class definitions."""
        classes = []
        lines = content.split('\n')
        
        # PHP class patterns
        class_patterns = [
            r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?',
            r'abstract\s+class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?',
            r'final\s+class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?',
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in class_patterns:
                match = re.search(pattern, stripped)
                if match:
                    class_name = match.group(1)
                    extends = match.group(2) if len(match.groups()) > 1 else None
                    implements = match.group(3) if len(match.groups()) > 2 else None
                    
                    # Determine class modifiers
                    is_abstract = 'abstract' in stripped
                    is_final = 'final' in stripped
                    
                    # Extract class members
                    properties, methods = self._extract_class_members(lines, i)
                    
                    classes.append({
                        'name': class_name,
                        'line_number': i,
                        'extends': extends,
                        'implements': implements.split(',') if implements else [],
                        'is_abstract': is_abstract,
                        'is_final': is_final,
                        'properties': properties,
                        'methods': methods,
                        'docstring': self._extract_phpdoc(lines, i - 1)
                    })
                    break
        
        return classes
    
    def _extract_traits(self, content: str) -> List[Dict[str, Any]]:
        """Extract PHP trait definitions."""
        traits = []
        lines = content.split('\n')
        
        trait_pattern = r'trait\s+(\w+)'
        
        for i, line in enumerate(lines, 1):
            match = re.search(trait_pattern, line.strip())
            if match:
                trait_name = match.group(1)
                
                # Extract trait methods
                methods = self._extract_trait_methods(lines, i)
                
                traits.append({
                    'name': trait_name,
                    'line_number': i,
                    'methods': methods,
                    'docstring': self._extract_phpdoc(lines, i - 1)
                })
        
        return traits
    
    def _extract_interfaces(self, content: str) -> List[Dict[str, Any]]:
        """Extract PHP interface definitions."""
        interfaces = []
        lines = content.split('\n')
        
        interface_pattern = r'interface\s+(\w+)(?:\s+extends\s+([^{]+))?'
        
        for i, line in enumerate(lines, 1):
            match = re.search(interface_pattern, line.strip())
            if match:
                interface_name = match.group(1)
                extends = match.group(2) if len(match.groups()) > 1 else None
                
                # Extract interface methods
                methods = self._extract_interface_methods(lines, i)
                
                interfaces.append({
                    'name': interface_name,
                    'line_number': i,
                    'extends': extends.split(',') if extends else [],
                    'methods': methods,
                    'docstring': self._extract_phpdoc(lines, i - 1)
                })
        
        return interfaces
    
    def _extract_namespaces(self, content: str) -> List[Dict[str, Any]]:
        """Extract PHP namespace declarations."""
        namespaces = []
        lines = content.split('\n')
        
        namespace_pattern = r'namespace\s+([^;{]+)'
        
        for i, line in enumerate(lines, 1):
            match = re.search(namespace_pattern, line.strip())
            if match:
                namespace_name = match.group(1).strip()
                
                namespaces.append({
                    'name': namespace_name,
                    'line_number': i,
                    'statement': line.strip()
                })
        
        return namespaces
    
    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract PHP use statements and includes."""
        imports = []
        lines = content.split('\n')
        
        import_patterns = [
            r'use\s+([^;]+);',  # use statements
            r'require(?:_once)?\s*\(?[\'"]([^\'"]+)[\'"]',  # require/require_once
            r'include(?:_once)?\s*\(?[\'"]([^\'"]+)[\'"]',  # include/include_once
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in import_patterns:
                match = re.search(pattern, stripped)
                if match:
                    import_name = match.group(1)
                    
                    # Determine import type
                    if stripped.startswith('use'):
                        import_type = 'use_statement'
                        # Handle aliases
                        if ' as ' in import_name:
                            module, alias = import_name.split(' as ', 1)
                            import_name = module.strip()
                            alias = alias.strip()
                        else:
                            alias = None
                    elif 'require' in stripped:
                        import_type = 'require'
                        alias = None
                    elif 'include' in stripped:
                        import_type = 'include'
                        alias = None
                    else:
                        import_type = 'unknown'
                        alias = None
                    
                    imports.append({
                        'name': import_name.strip(),
                        'alias': alias,
                        'line_number': i,
                        'statement': stripped,
                        'type': import_type
                    })
                    break
        
        return imports
    
    def _extract_exports(self, content: str) -> List[Dict[str, Any]]:
        """Extract PHP exports (public classes, functions, constants)."""
        exports = []
        
        # In PHP, exports are typically public classes and functions
        # Extract from already parsed functions and classes
        functions = self._extract_functions(content)
        classes = self._extract_classes(content)
        
        # Add public functions as exports
        for func in functions:
            if func.get('visibility') == 'public' or 'visibility' not in func:
                exports.append({
                    'name': func['name'],
                    'type': 'function',
                    'line_number': func['line_number']
                })
        
        # Add public classes as exports
        for cls in classes:
            exports.append({
                'name': cls['name'],
                'type': 'class',
                'line_number': cls['line_number']
            })
        
        # Extract constants
        const_pattern = r'const\s+(\w+)\s*='
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            match = re.search(const_pattern, line.strip())
            if match:
                exports.append({
                    'name': match.group(1),
                    'type': 'constant',
                    'line_number': i
                })
        
        return exports
    
    def _extract_php_patterns(self, content: str) -> List[str]:
        """Extract PHP-specific patterns."""
        patterns = self.extract_patterns(content)
        
        # PHP-specific patterns
        if 'trait ' in content:
            patterns.append('traits')
        if 'interface ' in content:
            patterns.append('interfaces')
        if 'namespace ' in content:
            patterns.append('namespaces')
        if 'abstract ' in content:
            patterns.append('abstract_classes')
        if 'final ' in content:
            patterns.append('final_classes')
        if 'static ' in content:
            patterns.append('static_methods')
        if '$this->' in content:
            patterns.append('object_oriented')
        if '::' in content:
            patterns.append('static_calls')
        if 'extends ' in content:
            patterns.append('inheritance')
        if 'implements ' in content:
            patterns.append('interface_implementation')
        if 'use ' in content and 'trait' in content:
            patterns.append('trait_usage')
        if '__construct' in content:
            patterns.append('constructors')
        if '__destruct' in content:
            patterns.append('destructors')
        if '__get' in content or '__set' in content:
            patterns.append('magic_methods')
        if 'try {' in content or 'catch (' in content:
            patterns.append('exception_handling')
        
        return list(set(patterns))
    
    def _parse_php_arguments(self, args_str: str) -> List[Dict[str, Any]]:
        """Parse PHP function arguments with type hints."""
        args = []
        if not args_str.strip():
            return args
        
        # Split arguments
        arg_parts = [arg.strip() for arg in args_str.split(',')]
        
        for arg in arg_parts:
            if not arg:
                continue
            
            # Parse argument with type hint and default value
            arg_info = {
                'name': arg,
                'type': None,
                'default': None,
                'is_reference': False,
                'is_variadic': False
            }
            
            # Check for reference parameter
            if '&' in arg:
                arg_info['is_reference'] = True
                arg = arg.replace('&', '').strip()
            
            # Check for variadic parameter
            if '...' in arg:
                arg_info['is_variadic'] = True
                arg = arg.replace('...', '').strip()
            
            # Check for default value
            if '=' in arg:
                arg_part, default_part = arg.split('=', 1)
                arg = arg_part.strip()
                arg_info['default'] = default_part.strip()
            
            # Check for type hint
            parts = arg.split()
            if len(parts) > 1:
                # First part is type hint, second is variable name
                arg_info['type'] = parts[0]
                arg_info['name'] = parts[1]
            else:
                arg_info['name'] = arg
            
            args.append(arg_info)
        
        return args
    
    def _extract_class_members(self, lines: List[str], class_start: int) -> tuple:
        """Extract properties and methods from a PHP class."""
        properties = []
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
                
                # Property pattern
                prop_match = re.search(r'(public|private|protected|static)?\s*(public|private|protected|static)?\s*\$(\w+)', line)
                if prop_match and 'function' not in line:
                    modifiers = [m for m in [prop_match.group(1), prop_match.group(2)] if m]
                    name = prop_match.group(3)
                    
                    properties.append({
                        'name': f'${name}',
                        'modifiers': modifiers,
                        'line_number': i + 1
                    })
                
                # Method pattern
                method_match = re.search(r'(public|private|protected|static|abstract|final)?\s*(public|private|protected|static|abstract|final)?\s*function\s+(\w+)', line)
                if method_match:
                    modifiers = [m for m in [method_match.group(1), method_match.group(2)] if m]
                    name = method_match.group(3)
                    
                    methods.append({
                        'name': name,
                        'modifiers': modifiers,
                        'line_number': i + 1
                    })
                
                if brace_count <= 0:
                    break
        
        return properties, methods
    
    def _extract_trait_methods(self, lines: List[str], trait_start: int) -> List[Dict[str, Any]]:
        """Extract methods from a PHP trait."""
        methods = []
        in_trait = False
        brace_count = 0
        
        for i in range(trait_start - 1, len(lines)):
            line = lines[i].strip()
            
            if not in_trait and '{' in line:
                in_trait = True
                brace_count = line.count('{') - line.count('}')
                continue
            
            if in_trait:
                brace_count += line.count('{') - line.count('}')
                
                # Method pattern
                method_match = re.search(r'(public|private|protected|static)?\s*function\s+(\w+)', line)
                if method_match:
                    visibility = method_match.group(1) or 'public'
                    name = method_match.group(2)
                    
                    methods.append({
                        'name': name,
                        'visibility': visibility,
                        'line_number': i + 1
                    })
                
                if brace_count <= 0:
                    break
        
        return methods
    
    def _extract_interface_methods(self, lines: List[str], interface_start: int) -> List[Dict[str, Any]]:
        """Extract methods from a PHP interface."""
        methods = []
        in_interface = False
        brace_count = 0
        
        for i in range(interface_start - 1, len(lines)):
            line = lines[i].strip()
            
            if not in_interface and '{' in line:
                in_interface = True
                brace_count = line.count('{') - line.count('}')
                continue
            
            if in_interface:
                brace_count += line.count('{') - line.count('}')
                
                # Method signature pattern
                method_match = re.search(r'public\s+function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^;]+))?', line)
                if method_match:
                    name = method_match.group(1)
                    args = method_match.group(2)
                    return_type = method_match.group(3)
                    
                    methods.append({
                        'name': name,
                        'args': args,
                        'return_type': return_type.strip() if return_type else None,
                        'line_number': i + 1
                    })
                
                if brace_count <= 0:
                    break
        
        return methods
    
    def _extract_phpdoc(self, lines: List[str], line_index: int) -> str:
        """Extract PHPDoc comment before a declaration."""
        if line_index < 0:
            return None
        
        # Look backwards for PHPDoc comment
        for i in range(line_index, max(-1, line_index - 10), -1):
            line = lines[i].strip()
            if line.startswith('/**'):
                # Found start of PHPDoc, collect until */
                phpdoc_lines = []
                for j in range(i, min(len(lines), i + 20)):
                    phpdoc_lines.append(lines[j])
                    if '*/' in lines[j]:
                        break
                return '\n'.join(phpdoc_lines)
            elif line and not line.startswith('//') and not line.startswith('*') and not line.startswith('#'):
                # Hit non-comment line, stop looking
                break
        
        return None
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if a line is a PHP comment."""
        return (line.startswith('//') or line.startswith('/*') or 
                line.startswith('*') or line.startswith('#'))
