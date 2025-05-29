"""HTML analyzer for enhanced metadata extraction."""

import re
from pathlib import Path
from typing import Any, Dict, List

from .base_analyzer import BaseAnalyzer


class HTMLAnalyzer(BaseAnalyzer):
    """Analyzer for HTML files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.html', '.htm', '.xhtml', '.shtml'}
        self.language_name = 'html'
    
    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze HTML file content."""
        return {
            'functions': self._extract_script_functions(content),
            'classes': self._extract_css_classes(content),
            'imports': self._extract_imports(content),
            'exports': self._extract_exports(content),
            'patterns': self._extract_html_patterns(content),
            'elements': self._extract_html_elements(content),
            'forms': self._extract_forms(content),
            'meta_tags': self._extract_meta_tags(content),
            'scripts': self._extract_scripts(content),
            'styles': self._extract_styles(content)
        }
    
    def _extract_script_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract JavaScript functions from script tags."""
        functions = []
        
        # Find script tags and extract JavaScript functions
        script_pattern = r'<script[^>]*>(.*?)</script>'
        script_matches = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for script_content in script_matches:
            # Extract functions from JavaScript content
            func_patterns = [
                r'function\s+(\w+)\s*\(([^)]*)\)',
                r'(\w+)\s*=\s*function\s*\(([^)]*)\)',
                r'(\w+)\s*:\s*function\s*\(([^)]*)\)',
                r'(\w+)\s*=\s*\(([^)]*)\)\s*=>'
            ]
            
            lines = script_content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern in func_patterns:
                    match = re.search(pattern, line.strip())
                    if match:
                        func_name = match.group(1)
                        args = match.group(2) if len(match.groups()) > 1 else ''
                        
                        functions.append({
                            'name': func_name,
                            'args': [arg.strip() for arg in args.split(',') if arg.strip()],
                            'line_number': i,
                            'context': 'script_tag',
                            'signature': line.strip()
                        })
        
        return functions
    
    def _extract_css_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract CSS classes from style tags and class attributes."""
        classes = []
        
        # Extract from style tags
        style_pattern = r'<style[^>]*>(.*?)</style>'
        style_matches = re.findall(style_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for style_content in style_matches:
            # Extract CSS class definitions
            class_pattern = r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)\s*{'
            class_matches = re.findall(class_pattern, style_content)
            
            for class_name in class_matches:
                classes.append({
                    'name': class_name,
                    'type': 'css_class',
                    'context': 'style_tag'
                })
        
        # Extract from class attributes
        class_attr_pattern = r'class\s*=\s*["\']([^"\']+)["\']'
        class_attr_matches = re.findall(class_attr_pattern, content, re.IGNORECASE)
        
        for class_attr in class_attr_matches:
            class_names = class_attr.split()
            for class_name in class_names:
                if class_name not in [c['name'] for c in classes]:
                    classes.append({
                        'name': class_name,
                        'type': 'css_class',
                        'context': 'class_attribute'
                    })
        
        return classes
    
    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract external resource imports (CSS, JS, images, etc.)."""
        imports = []
        
        # CSS imports
        css_patterns = [
            r'<link[^>]+href\s*=\s*["\']([^"\']+)["\'][^>]*>',
            r'@import\s+["\']([^"\']+)["\']'
        ]
        
        for pattern in css_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                imports.append({
                    'name': match,
                    'type': 'stylesheet',
                    'statement': match
                })
        
        # JavaScript imports
        js_pattern = r'<script[^>]+src\s*=\s*["\']([^"\']+)["\'][^>]*>'
        js_matches = re.findall(js_pattern, content, re.IGNORECASE)
        
        for match in js_matches:
            imports.append({
                'name': match,
                'type': 'script',
                'statement': match
            })
        
        # Image imports
        img_pattern = r'<img[^>]+src\s*=\s*["\']([^"\']+)["\'][^>]*>'
        img_matches = re.findall(img_pattern, content, re.IGNORECASE)
        
        for match in img_matches:
            imports.append({
                'name': match,
                'type': 'image',
                'statement': match
            })
        
        # Other resource imports
        resource_patterns = [
            (r'<iframe[^>]+src\s*=\s*["\']([^"\']+)["\'][^>]*>', 'iframe'),
            (r'<video[^>]+src\s*=\s*["\']([^"\']+)["\'][^>]*>', 'video'),
            (r'<audio[^>]+src\s*=\s*["\']([^"\']+)["\'][^>]*>', 'audio'),
            (r'<source[^>]+src\s*=\s*["\']([^"\']+)["\'][^>]*>', 'source')
        ]
        
        for pattern, resource_type in resource_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                imports.append({
                    'name': match,
                    'type': resource_type,
                    'statement': match
                })
        
        return imports
    
    def _extract_exports(self, content: str) -> List[Dict[str, Any]]:
        """Extract HTML exports (IDs, named anchors, etc.)."""
        exports = []
        
        # Extract IDs
        id_pattern = r'id\s*=\s*["\']([^"\']+)["\']'
        id_matches = re.findall(id_pattern, content, re.IGNORECASE)
        
        for id_name in id_matches:
            exports.append({
                'name': id_name,
                'type': 'id',
                'line_number': None
            })
        
        # Extract named anchors
        anchor_pattern = r'<a[^>]+name\s*=\s*["\']([^"\']+)["\'][^>]*>'
        anchor_matches = re.findall(anchor_pattern, content, re.IGNORECASE)
        
        for anchor_name in anchor_matches:
            exports.append({
                'name': anchor_name,
                'type': 'anchor',
                'line_number': None
            })
        
        return exports
    
    def _extract_html_elements(self, content: str) -> List[Dict[str, Any]]:
        """Extract HTML elements and their structure."""
        elements = []
        
        # Extract all HTML tags
        tag_pattern = r'<(\w+)([^>]*)>'
        tag_matches = re.findall(tag_pattern, content, re.IGNORECASE)
        
        element_counts = {}
        for tag_name, attributes in tag_matches:
            tag_name = tag_name.lower()
            
            if tag_name not in element_counts:
                element_counts[tag_name] = 0
            element_counts[tag_name] += 1
            
            # Parse attributes
            attr_dict = self._parse_attributes(attributes)
            
            elements.append({
                'tag': tag_name,
                'attributes': attr_dict,
                'count': element_counts[tag_name]
            })
        
        return elements
    
    def _extract_forms(self, content: str) -> List[Dict[str, Any]]:
        """Extract form elements and their inputs."""
        forms = []
        
        # Extract form tags
        form_pattern = r'<form([^>]*)>(.*?)</form>'
        form_matches = re.findall(form_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, (form_attrs, form_content) in enumerate(form_matches):
            form_attributes = self._parse_attributes(form_attrs)
            
            # Extract input elements within the form
            input_pattern = r'<(input|textarea|select|button)([^>]*)>'
            input_matches = re.findall(input_pattern, form_content, re.IGNORECASE)
            
            inputs = []
            for input_tag, input_attrs in input_matches:
                input_attributes = self._parse_attributes(input_attrs)
                inputs.append({
                    'tag': input_tag.lower(),
                    'attributes': input_attributes
                })
            
            forms.append({
                'index': i,
                'attributes': form_attributes,
                'inputs': inputs,
                'action': form_attributes.get('action', ''),
                'method': form_attributes.get('method', 'get').lower()
            })
        
        return forms
    
    def _extract_meta_tags(self, content: str) -> List[Dict[str, Any]]:
        """Extract meta tags and their information."""
        meta_tags = []
        
        meta_pattern = r'<meta([^>]*)>'
        meta_matches = re.findall(meta_pattern, content, re.IGNORECASE)
        
        for meta_attrs in meta_matches:
            attributes = self._parse_attributes(meta_attrs)
            
            meta_tags.append({
                'attributes': attributes,
                'name': attributes.get('name', ''),
                'content': attributes.get('content', ''),
                'property': attributes.get('property', '')
            })
        
        return meta_tags
    
    def _extract_scripts(self, content: str) -> List[Dict[str, Any]]:
        """Extract script tags and their information."""
        scripts = []
        
        script_pattern = r'<script([^>]*)>(.*?)</script>'
        script_matches = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, (script_attrs, script_content) in enumerate(script_matches):
            attributes = self._parse_attributes(script_attrs)
            
            scripts.append({
                'index': i,
                'attributes': attributes,
                'src': attributes.get('src', ''),
                'type': attributes.get('type', 'text/javascript'),
                'content_length': len(script_content.strip()),
                'has_content': bool(script_content.strip())
            })
        
        return scripts
    
    def _extract_styles(self, content: str) -> List[Dict[str, Any]]:
        """Extract style tags and their information."""
        styles = []
        
        style_pattern = r'<style([^>]*)>(.*?)</style>'
        style_matches = re.findall(style_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, (style_attrs, style_content) in enumerate(style_matches):
            attributes = self._parse_attributes(style_attrs)
            
            # Count CSS rules
            rule_count = len(re.findall(r'{[^}]*}', style_content))
            
            styles.append({
                'index': i,
                'attributes': attributes,
                'type': attributes.get('type', 'text/css'),
                'content_length': len(style_content.strip()),
                'rule_count': rule_count
            })
        
        return styles
    
    def _extract_html_patterns(self, content: str) -> List[str]:
        """Extract HTML-specific patterns."""
        patterns = []
        
        # Check for various HTML features
        if '<form' in content.lower():
            patterns.append('forms')
        
        if '<table' in content.lower():
            patterns.append('tables')
        
        if '<canvas' in content.lower():
            patterns.append('canvas')
        
        if '<svg' in content.lower():
            patterns.append('svg')
        
        if '<video' in content.lower() or '<audio' in content.lower():
            patterns.append('multimedia')
        
        if 'data-' in content.lower():
            patterns.append('data_attributes')
        
        if 'aria-' in content.lower():
            patterns.append('accessibility')
        
        if '<script' in content.lower():
            patterns.append('javascript')
        
        if '<style' in content.lower() or 'class=' in content.lower():
            patterns.append('css')
        
        if 'bootstrap' in content.lower():
            patterns.append('bootstrap')
        
        if 'jquery' in content.lower():
            patterns.append('jquery')
        
        if 'react' in content.lower():
            patterns.append('react')
        
        if 'vue' in content.lower():
            patterns.append('vue')
        
        if 'angular' in content.lower():
            patterns.append('angular')
        
        # Check for HTML5 semantic elements
        html5_elements = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        if any(f'<{elem}' in content.lower() for elem in html5_elements):
            patterns.append('html5_semantic')
        
        # Check for responsive design
        if 'viewport' in content.lower() or 'media=' in content.lower():
            patterns.append('responsive_design')
        
        # Check for meta tags
        if '<meta' in content.lower():
            patterns.append('meta_tags')
        
        return list(set(patterns))
    
    def _parse_attributes(self, attr_string: str) -> Dict[str, str]:
        """Parse HTML attributes from attribute string."""
        attributes = {}
        
        # Pattern to match attribute="value" or attribute='value' or attribute=value
        attr_pattern = r'(\w+)\s*=\s*(?:["\']([^"\']*)["\']|([^\s>]+))'
        attr_matches = re.findall(attr_pattern, attr_string)
        
        for attr_name, quoted_value, unquoted_value in attr_matches:
            value = quoted_value if quoted_value else unquoted_value
            attributes[attr_name.lower()] = value
        
        # Handle boolean attributes (attributes without values)
        boolean_attr_pattern = r'\b(\w+)(?!\s*=)'
        boolean_matches = re.findall(boolean_attr_pattern, attr_string)
        
        for attr_name in boolean_matches:
            if attr_name.lower() not in attributes:
                attributes[attr_name.lower()] = ''
        
        return attributes
    
    def calculate_complexity(self, content: str) -> float:
        """Calculate complexity for HTML based on structure."""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # HTML complexity factors
        tags = len(re.findall(r'<\w+', content))
        forms = len(re.findall(r'<form', content, re.IGNORECASE))
        scripts = len(re.findall(r'<script', content, re.IGNORECASE))
        styles = len(re.findall(r'<style', content, re.IGNORECASE))
        tables = len(re.findall(r'<table', content, re.IGNORECASE))
        
        complexity_score = (tags * 0.1 + forms * 2.0 + scripts * 1.5 + 
                          styles * 1.0 + tables * 1.0)
        
        # Normalize by content length
        if non_empty_lines:
            complexity_score = complexity_score / len(non_empty_lines) * 10
        
        return min(complexity_score, 10.0)
    
    def count_lines_of_code(self, content: str) -> int:
        """Count meaningful content lines in HTML."""
        lines = content.split('\n')
        content_lines = 0
        
        for line in lines:
            stripped = line.strip()
            # Count non-empty lines that aren't just comments
            if stripped and not stripped.startswith('<!--'):
                content_lines += 1
        
        return content_lines
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if a line is an HTML comment."""
        return line.strip().startswith('<!--') or '-->' in line
