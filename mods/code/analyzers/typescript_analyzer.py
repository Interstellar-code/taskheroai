"""TypeScript-specific analyzer for enhanced metadata extraction."""

import re
from pathlib import Path
from typing import Any, Dict, List

from .base_analyzer import BaseAnalyzer


class TypeScriptAnalyzer(BaseAnalyzer):
    """Analyzer specifically for TypeScript code files."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.ts', '.tsx'}
        self.language_name = 'typescript'

    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze TypeScript file content with type-specific features."""
        return {
            'functions': self._extract_functions(content),
            'classes': self._extract_classes(content),
            'imports': self._extract_imports(content),
            'exports': self._extract_exports(content),
            'patterns': self._extract_typescript_patterns(content),
            'interfaces': self._extract_interfaces(content),
            'types': self._extract_type_aliases(content),
            'enums': self._extract_enums(content)
        }

    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract TypeScript function definitions with type annotations."""
        functions = []
        lines = content.split('\n')

        # TypeScript function patterns with type annotations
        patterns = [
            r'function\s+(\w+)\s*(<[^>]*>)?\s*\(([^)]*)\)\s*:\s*([^{;]+)',  # function name<T>(args): ReturnType
            r'(\w+)\s*:\s*\(([^)]*)\)\s*=>\s*([^;,}]+)',  # name: (args) => ReturnType
            r'(\w+)\s*=\s*\(([^)]*)\)\s*:\s*([^=]+)\s*=>', # name = (args): ReturnType =>
            r'async\s+function\s+(\w+)\s*(<[^>]*>)?\s*\(([^)]*)\)\s*:\s*([^{;]+)', # async function
            r'(\w+)\s*(<[^>]*>)?\s*\(([^)]*)\)\s*:\s*([^{;]+)\s*{', # method with return type
        ]

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            for pattern in patterns:
                match = re.search(pattern, stripped)
                if match:
                    groups = match.groups()
                    func_name = groups[0]

                    # Extract type parameters, arguments, and return type
                    type_params = groups[1] if len(groups) > 1 and groups[1] else None
                    args_str = groups[2] if len(groups) > 2 else ''
                    return_type = groups[3] if len(groups) > 3 else 'any'

                    # Parse typed arguments
                    args = self._parse_typed_arguments(args_str)

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
                        'type_parameters': type_params,
                        'return_type': return_type.strip(),
                        'docstring': self._extract_jsdoc(lines, i - 1)
                    })
                    break

        return functions

    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract TypeScript class definitions with type information."""
        classes = []
        lines = content.split('\n')

        # TypeScript class patterns
        class_pattern = r'class\s+(\w+)(?:\s*<([^>]+)>)?(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?'

        for i, line in enumerate(lines, 1):
            match = re.search(class_pattern, line.strip())
            if match:
                class_name = match.group(1)
                type_params = match.group(2)
                extends = match.group(3)
                implements = match.group(4)

                # Extract class members
                properties, methods = self._extract_class_members(lines, i)

                classes.append({
                    'name': class_name,
                    'line_number': i,
                    'type_parameters': type_params,
                    'extends': extends,
                    'implements': implements.split(',') if implements else [],
                    'properties': properties,
                    'methods': methods,
                    'docstring': self._extract_jsdoc(lines, i - 1)
                })

        return classes

    def _extract_interfaces(self, content: str) -> List[Dict[str, Any]]:
        """Extract TypeScript interface definitions."""
        interfaces = []
        lines = content.split('\n')

        interface_pattern = r'interface\s+(\w+)(?:\s*<([^>]+)>)?(?:\s+extends\s+([^{]+))?'

        for i, line in enumerate(lines, 1):
            match = re.search(interface_pattern, line.strip())
            if match:
                interface_name = match.group(1)
                type_params = match.group(2)
                extends = match.group(3)

                # Extract interface members
                members = self._extract_interface_members(lines, i)

                interfaces.append({
                    'name': interface_name,
                    'line_number': i,
                    'type_parameters': type_params,
                    'extends': extends.split(',') if extends else [],
                    'members': members,
                    'docstring': self._extract_jsdoc(lines, i - 1)
                })

        return interfaces

    def _extract_type_aliases(self, content: str) -> List[Dict[str, Any]]:
        """Extract TypeScript type alias definitions."""
        types = []
        lines = content.split('\n')

        type_pattern = r'type\s+(\w+)(?:\s*<([^>]+)>)?\s*=\s*([^;]+)'

        for i, line in enumerate(lines, 1):
            match = re.search(type_pattern, line.strip())
            if match:
                type_name = match.group(1)
                type_params = match.group(2)
                type_definition = match.group(3)

                types.append({
                    'name': type_name,
                    'line_number': i,
                    'type_parameters': type_params,
                    'definition': type_definition.strip(),
                    'docstring': self._extract_jsdoc(lines, i - 1)
                })

        return types

    def _extract_enums(self, content: str) -> List[Dict[str, Any]]:
        """Extract TypeScript enum definitions."""
        enums = []
        lines = content.split('\n')

        enum_pattern = r'enum\s+(\w+)'

        for i, line in enumerate(lines, 1):
            match = re.search(enum_pattern, line.strip())
            if match:
                enum_name = match.group(1)

                # Extract enum members
                members = self._extract_enum_members(lines, i)

                enums.append({
                    'name': enum_name,
                    'line_number': i,
                    'members': members,
                    'docstring': self._extract_jsdoc(lines, i - 1)
                })

        return enums

    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract TypeScript import statements with type imports."""
        imports = []
        lines = content.split('\n')

        import_patterns = [
            r'import\s+type\s+{\s*([^}]+)\s*}\s+from\s+[\'"]([^\'"]+)[\'"]',  # import type { Type } from 'module'
            r'import\s+{\s*([^}]+)\s*}\s+from\s+[\'"]([^\'"]+)[\'"]',  # import { name } from 'module'
            r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # import name from 'module'
            r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # import * as name from 'module'
            r'import\s+[\'"]([^\'"]+)[\'"]',  # import 'module' (side effect)
        ]

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            for pattern in import_patterns:
                match = re.search(pattern, stripped)
                if match:
                    groups = match.groups()

                    if 'import type' in stripped:
                        import_type = 'type_import'
                    elif len(groups) == 2:
                        import_type = 'named_import'
                    elif len(groups) == 1:
                        import_type = 'side_effect_import'
                    else:
                        import_type = 'default_import'

                    imports.append({
                        'name': groups[0] if len(groups) > 1 else None,
                        'module': groups[-1],
                        'line_number': i,
                        'statement': stripped,
                        'type': import_type,
                        'is_type_only': 'import type' in stripped
                    })
                    break

        return imports

    def _extract_exports(self, content: str) -> List[Dict[str, Any]]:
        """Extract TypeScript export statements."""
        exports = []
        lines = content.split('\n')

        export_patterns = [
            r'export\s+function\s+(\w+)',  # export function name
            r'export\s+class\s+(\w+)',     # export class name
            r'export\s+interface\s+(\w+)', # export interface name
            r'export\s+type\s+(\w+)',      # export type name
            r'export\s+enum\s+(\w+)',      # export enum name
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

    def _extract_typescript_patterns(self, content: str) -> List[str]:
        """Extract TypeScript-specific patterns."""
        patterns = self.extract_patterns(content)

        # TypeScript-specific patterns
        if 'interface ' in content:
            patterns.append('interfaces')
        if 'type ' in content and '=' in content:
            patterns.append('type_aliases')
        if 'enum ' in content:
            patterns.append('enums')
        if 'generic' in content or '<T>' in content or '<T,' in content:
            patterns.append('generics')
        if 'implements ' in content:
            patterns.append('interface_implementation')
        if 'abstract ' in content:
            patterns.append('abstract_classes')
        if 'readonly ' in content:
            patterns.append('readonly_properties')
        if 'private ' in content or 'protected ' in content or 'public ' in content:
            patterns.append('access_modifiers')
        if 'decorator' in content or '@' in content:
            patterns.append('decorators')
        if 'namespace ' in content:
            patterns.append('namespaces')

        return list(set(patterns))

    def _parse_typed_arguments(self, args_str: str) -> List[Dict[str, Any]]:
        """Parse TypeScript function arguments with type annotations."""
        args = []
        if not args_str.strip():
            return args

        # Split arguments considering nested types
        arg_parts = self._split_arguments(args_str)

        for arg in arg_parts:
            arg = arg.strip()
            if not arg:
                continue

            # Parse argument with type annotation
            if ':' in arg:
                name_part, type_part = arg.split(':', 1)
                name = name_part.strip()
                arg_type = type_part.strip()

                # Check for optional parameters
                is_optional = name.endswith('?')
                if is_optional:
                    name = name[:-1]

                # Check for default values
                default_value = None
                if '=' in type_part:
                    type_part, default_value = type_part.split('=', 1)
                    arg_type = type_part.strip()
                    default_value = default_value.strip()

                args.append({
                    'name': name,
                    'type': arg_type,
                    'optional': is_optional,
                    'default': default_value
                })
            else:
                # Argument without type annotation
                args.append({
                    'name': arg,
                    'type': 'any',
                    'optional': False,
                    'default': None
                })

        return args

    def _split_arguments(self, args_str: str) -> List[str]:
        """Split arguments considering nested generic types."""
        args = []
        current_arg = ""
        bracket_count = 0

        for char in args_str:
            if char in '<([':
                bracket_count += 1
            elif char in '>)]':
                bracket_count -= 1
            elif char == ',' and bracket_count == 0:
                args.append(current_arg.strip())
                current_arg = ""
                continue

            current_arg += char

        if current_arg.strip():
            args.append(current_arg.strip())

        return args

    def _extract_class_members(self, lines: List[str], class_start: int) -> tuple:
        """Extract properties and methods from a TypeScript class."""
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

                # Property pattern: name: type = value;
                prop_match = re.search(r'(private|protected|public|readonly)?\s*(\w+)\s*:\s*([^=;]+)(?:\s*=\s*([^;]+))?', line)
                if prop_match and not '(' in line:
                    modifier = prop_match.group(1)
                    name = prop_match.group(2)
                    prop_type = prop_match.group(3).strip()
                    default_value = prop_match.group(4)

                    properties.append({
                        'name': name,
                        'type': prop_type,
                        'modifier': modifier,
                        'default': default_value,
                        'line_number': i + 1
                    })

                # Method pattern
                method_match = re.search(r'(private|protected|public|static|async)?\s*(\w+)\s*\([^)]*\)', line)
                if method_match and '{' in line:
                    modifier = method_match.group(1)
                    name = method_match.group(2)

                    methods.append({
                        'name': name,
                        'modifier': modifier,
                        'line_number': i + 1,
                        'is_async': 'async' in line,
                        'is_static': 'static' in line
                    })

                if brace_count <= 0:
                    break

        return properties, methods

    def _extract_interface_members(self, lines: List[str], interface_start: int) -> List[Dict[str, Any]]:
        """Extract members from a TypeScript interface."""
        members = []
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

                # Property or method signature
                member_match = re.search(r'(\w+)(\?)?\s*:\s*([^;,}]+)', line)
                if member_match:
                    name = member_match.group(1)
                    is_optional = member_match.group(2) == '?'
                    member_type = member_match.group(3).strip()

                    members.append({
                        'name': name,
                        'type': member_type,
                        'optional': is_optional,
                        'line_number': i + 1
                    })

                if brace_count <= 0:
                    break

        return members

    def _extract_enum_members(self, lines: List[str], enum_start: int) -> List[Dict[str, Any]]:
        """Extract members from a TypeScript enum."""
        members = []
        in_enum = False
        brace_count = 0

        for i in range(enum_start - 1, len(lines)):
            line = lines[i].strip()

            if not in_enum and '{' in line:
                in_enum = True
                brace_count = line.count('{') - line.count('}')
                continue

            if in_enum:
                brace_count += line.count('{') - line.count('}')

                # Enum member pattern
                member_match = re.search(r'(\w+)(?:\s*=\s*([^,}]+))?', line)
                if member_match and not line.startswith('//'):
                    name = member_match.group(1)
                    value = member_match.group(2)

                    members.append({
                        'name': name,
                        'value': value.strip() if value else None,
                        'line_number': i + 1
                    })

                if brace_count <= 0:
                    break

        return members

    def _extract_jsdoc(self, lines: List[str], line_index: int) -> str:
        """Extract JSDoc comment before a declaration."""
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
