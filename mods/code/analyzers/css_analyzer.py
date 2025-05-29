"""CSS analyzer for enhanced metadata extraction."""

import re
from pathlib import Path
from typing import Any, Dict, List

from .base_analyzer import BaseAnalyzer


class CSSAnalyzer(BaseAnalyzer):
    """Analyzer for CSS files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.css', '.scss', '.sass', '.less', '.styl', '.stylus'}
        self.language_name = 'css'
    
    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze CSS file content."""
        return {
            'functions': self._extract_functions(content),
            'classes': self._extract_classes(content),
            'imports': self._extract_imports(content),
            'exports': self._extract_exports(content),
            'patterns': self._extract_css_patterns(content),
            'selectors': self._extract_selectors(content),
            'variables': self._extract_variables(content),
            'mixins': self._extract_mixins(content),
            'media_queries': self._extract_media_queries(content),
            'keyframes': self._extract_keyframes(content)
        }
    
    def detect_language(self, content: str, file_path: Path) -> str:
        """Detect CSS preprocessor language."""
        extension = file_path.suffix.lower()
        
        if extension == '.scss':
            return 'scss'
        elif extension == '.sass':
            return 'sass'
        elif extension == '.less':
            return 'less'
        elif extension in {'.styl', '.stylus'}:
            return 'stylus'
        else:
            # Check content for preprocessor features
            if '$' in content and '@mixin' in content:
                return 'scss'
            elif '@' in content and 'less' in content.lower():
                return 'less'
            elif re.search(r'^\s*\w+\s*=', content, re.MULTILINE):
                return 'stylus'
            else:
                return 'css'
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract CSS functions and preprocessor functions."""
        functions = []
        lines = content.split('\n')
        
        # SCSS/Sass function patterns
        function_patterns = [
            r'@function\s+(\w+)\s*\(([^)]*)\)',  # @function name(args)
            r'@mixin\s+(\w+)\s*\(([^)]*)\)',     # @mixin name(args)
            r'(\w+)\s*=\s*\(([^)]*)\)\s*->',     # Stylus function
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in function_patterns:
                match = re.search(pattern, stripped)
                if match:
                    func_name = match.group(1)
                    args_str = match.group(2) if len(match.groups()) > 1 else ''
                    
                    # Parse arguments
                    args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
                    
                    # Determine function type
                    if '@function' in stripped:
                        func_type = 'scss_function'
                    elif '@mixin' in stripped:
                        func_type = 'scss_mixin'
                    elif '->' in stripped:
                        func_type = 'stylus_function'
                    else:
                        func_type = 'css_function'
                    
                    functions.append({
                        'name': func_name,
                        'args': args,
                        'line_number': i,
                        'signature': stripped,
                        'type': func_type
                    })
                    break
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract CSS class selectors."""
        classes = []
        
        # CSS class patterns
        class_pattern = r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)'
        class_matches = re.findall(class_pattern, content)
        
        # Remove duplicates and create class objects
        unique_classes = list(set(class_matches))
        
        for class_name in unique_classes:
            # Find line number of first occurrence
            lines = content.split('\n')
            line_number = None
            for i, line in enumerate(lines, 1):
                if f'.{class_name}' in line:
                    line_number = i
                    break
            
            classes.append({
                'name': class_name,
                'type': 'css_class',
                'line_number': line_number,
                'selector': f'.{class_name}'
            })
        
        return classes
    
    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract CSS import statements."""
        imports = []
        lines = content.split('\n')
        
        import_patterns = [
            r'@import\s+["\']([^"\']+)["\']',  # @import "file.css"
            r'@import\s+url\(["\']?([^"\']+)["\']?\)',  # @import url("file.css")
            r'@use\s+["\']([^"\']+)["\']',     # SCSS @use
            r'@forward\s+["\']([^"\']+)["\']', # SCSS @forward
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in import_patterns:
                match = re.search(pattern, stripped)
                if match:
                    import_path = match.group(1)
                    
                    # Determine import type
                    if '@use' in stripped:
                        import_type = 'scss_use'
                    elif '@forward' in stripped:
                        import_type = 'scss_forward'
                    elif 'url(' in stripped:
                        import_type = 'css_url_import'
                    else:
                        import_type = 'css_import'
                    
                    imports.append({
                        'name': import_path,
                        'line_number': i,
                        'statement': stripped,
                        'type': import_type
                    })
                    break
        
        return imports
    
    def _extract_exports(self, content: str) -> List[Dict[str, Any]]:
        """Extract CSS exports (classes, IDs, custom properties)."""
        exports = []
        
        # Extract class selectors
        class_pattern = r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)'
        class_matches = re.findall(class_pattern, content)
        
        for class_name in set(class_matches):
            exports.append({
                'name': class_name,
                'type': 'css_class',
                'selector': f'.{class_name}'
            })
        
        # Extract ID selectors
        id_pattern = r'#([a-zA-Z_-][a-zA-Z0-9_-]*)'
        id_matches = re.findall(id_pattern, content)
        
        for id_name in set(id_matches):
            exports.append({
                'name': id_name,
                'type': 'css_id',
                'selector': f'#{id_name}'
            })
        
        # Extract custom properties (CSS variables)
        custom_prop_pattern = r'--([a-zA-Z_-][a-zA-Z0-9_-]*)'
        custom_prop_matches = re.findall(custom_prop_pattern, content)
        
        for prop_name in set(custom_prop_matches):
            exports.append({
                'name': prop_name,
                'type': 'css_custom_property',
                'selector': f'--{prop_name}'
            })
        
        return exports
    
    def _extract_selectors(self, content: str) -> List[Dict[str, Any]]:
        """Extract all CSS selectors."""
        selectors = []
        
        # Remove comments and strings to avoid false matches
        cleaned_content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        cleaned_content = re.sub(r'["\'][^"\']*["\']', '', cleaned_content)
        
        # Find CSS rules
        rule_pattern = r'([^{}]+)\s*\{'
        rule_matches = re.findall(rule_pattern, cleaned_content)
        
        for rule in rule_matches:
            # Split multiple selectors
            selector_parts = [s.strip() for s in rule.split(',')]
            
            for selector in selector_parts:
                if selector and not selector.startswith('@'):
                    # Categorize selector type
                    selector_type = self._categorize_selector(selector)
                    
                    selectors.append({
                        'selector': selector,
                        'type': selector_type,
                        'specificity': self._calculate_specificity(selector)
                    })
        
        return selectors
    
    def _extract_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract CSS variables and preprocessor variables."""
        variables = []
        lines = content.split('\n')
        
        variable_patterns = [
            r'--([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:\s*([^;]+)',  # CSS custom properties
            r'\$([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:\s*([^;]+)',  # SCSS variables
            r'@([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:\s*([^;]+)',   # LESS variables
            r'([a-zA-Z_-][a-zA-Z0-9_-]*)\s*=\s*([^;]+)',    # Stylus variables
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in variable_patterns:
                match = re.search(pattern, stripped)
                if match:
                    var_name = match.group(1)
                    var_value = match.group(2).strip()
                    
                    # Determine variable type
                    if '--' in stripped:
                        var_type = 'css_custom_property'
                    elif '$' in stripped:
                        var_type = 'scss_variable'
                    elif '@' in stripped:
                        var_type = 'less_variable'
                    else:
                        var_type = 'stylus_variable'
                    
                    variables.append({
                        'name': var_name,
                        'value': var_value,
                        'type': var_type,
                        'line_number': i
                    })
                    break
        
        return variables
    
    def _extract_mixins(self, content: str) -> List[Dict[str, Any]]:
        """Extract CSS preprocessor mixins."""
        mixins = []
        lines = content.split('\n')
        
        mixin_patterns = [
            r'@mixin\s+([a-zA-Z_-][a-zA-Z0-9_-]*)',  # SCSS mixins
            r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)\s*\(',    # LESS mixins
        ]
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            for pattern in mixin_patterns:
                match = re.search(pattern, stripped)
                if match:
                    mixin_name = match.group(1)
                    
                    # Determine mixin type
                    if '@mixin' in stripped:
                        mixin_type = 'scss_mixin'
                    else:
                        mixin_type = 'less_mixin'
                    
                    mixins.append({
                        'name': mixin_name,
                        'type': mixin_type,
                        'line_number': i,
                        'signature': stripped
                    })
                    break
        
        return mixins
    
    def _extract_media_queries(self, content: str) -> List[Dict[str, Any]]:
        """Extract media queries."""
        media_queries = []
        lines = content.split('\n')
        
        media_pattern = r'@media\s+([^{]+)'
        
        for i, line in enumerate(lines, 1):
            match = re.search(media_pattern, line.strip())
            if match:
                media_condition = match.group(1).strip()
                
                media_queries.append({
                    'condition': media_condition,
                    'line_number': i,
                    'type': 'media_query'
                })
        
        return media_queries
    
    def _extract_keyframes(self, content: str) -> List[Dict[str, Any]]:
        """Extract CSS keyframe animations."""
        keyframes = []
        lines = content.split('\n')
        
        keyframe_pattern = r'@(?:keyframes|-webkit-keyframes|-moz-keyframes)\s+([a-zA-Z_-][a-zA-Z0-9_-]*)'
        
        for i, line in enumerate(lines, 1):
            match = re.search(keyframe_pattern, line.strip())
            if match:
                animation_name = match.group(1)
                
                keyframes.append({
                    'name': animation_name,
                    'line_number': i,
                    'type': 'keyframe_animation'
                })
        
        return keyframes
    
    def _extract_css_patterns(self, content: str) -> List[str]:
        """Extract CSS-specific patterns."""
        patterns = []
        
        # Check for CSS features
        if '@media' in content:
            patterns.append('media_queries')
        
        if '@keyframes' in content or 'animation' in content:
            patterns.append('animations')
        
        if 'transform' in content:
            patterns.append('transforms')
        
        if 'transition' in content:
            patterns.append('transitions')
        
        if 'flex' in content or 'grid' in content:
            patterns.append('modern_layout')
        
        if '--' in content:
            patterns.append('css_variables')
        
        if 'calc(' in content:
            patterns.append('calculations')
        
        # Check for preprocessor features
        if '$' in content and '@mixin' in content:
            patterns.append('scss')
        
        if '@' in content and '.mixin' in content:
            patterns.append('less')
        
        if re.search(r'^\s*\w+\s*=', content, re.MULTILINE):
            patterns.append('stylus')
        
        # Check for frameworks
        if 'bootstrap' in content.lower():
            patterns.append('bootstrap')
        
        if 'tailwind' in content.lower():
            patterns.append('tailwind')
        
        # Check for methodologies
        if re.search(r'__\w+|--\w+', content):
            patterns.append('bem_methodology')
        
        return list(set(patterns))
    
    def _categorize_selector(self, selector: str) -> str:
        """Categorize CSS selector type."""
        selector = selector.strip()
        
        if selector.startswith('.'):
            return 'class'
        elif selector.startswith('#'):
            return 'id'
        elif selector.startswith('@'):
            return 'at_rule'
        elif ':' in selector:
            return 'pseudo'
        elif '[' in selector and ']' in selector:
            return 'attribute'
        elif '>' in selector or '+' in selector or '~' in selector:
            return 'combinator'
        elif ' ' in selector:
            return 'descendant'
        else:
            return 'element'
    
    def _calculate_specificity(self, selector: str) -> Dict[str, int]:
        """Calculate CSS selector specificity."""
        # Count IDs, classes, and elements
        id_count = len(re.findall(r'#[a-zA-Z_-][a-zA-Z0-9_-]*', selector))
        class_count = len(re.findall(r'\.[a-zA-Z_-][a-zA-Z0-9_-]*', selector))
        attr_count = len(re.findall(r'\[[^\]]+\]', selector))
        pseudo_count = len(re.findall(r':[a-zA-Z_-][a-zA-Z0-9_-]*', selector))
        element_count = len(re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', selector))
        
        # Adjust element count (subtract classes and pseudo-classes)
        element_count = max(0, element_count - class_count - pseudo_count)
        
        return {
            'ids': id_count,
            'classes': class_count + attr_count + pseudo_count,
            'elements': element_count,
            'total': id_count * 100 + (class_count + attr_count + pseudo_count) * 10 + element_count
        }
    
    def calculate_complexity(self, content: str) -> float:
        """Calculate complexity for CSS based on rules and selectors."""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # CSS complexity factors
        rules = len(re.findall(r'{[^}]*}', content))
        media_queries = len(re.findall(r'@media', content))
        keyframes = len(re.findall(r'@keyframes', content))
        selectors = len(re.findall(r'[^{}]+\s*{', content))
        
        complexity_score = (rules * 0.5 + media_queries * 2.0 + 
                          keyframes * 1.5 + selectors * 0.3)
        
        # Normalize by content length
        if non_empty_lines:
            complexity_score = complexity_score / len(non_empty_lines) * 10
        
        return min(complexity_score, 10.0)
    
    def count_lines_of_code(self, content: str) -> int:
        """Count meaningful content lines in CSS."""
        lines = content.split('\n')
        content_lines = 0
        
        for line in lines:
            stripped = line.strip()
            # Count non-empty lines that aren't just comments
            if stripped and not stripped.startswith('/*') and not stripped.startswith('//'):
                content_lines += 1
        
        return content_lines
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if a line is a CSS comment."""
        return line.strip().startswith('/*') or line.strip().startswith('//')
