"""Markdown analyzer for enhanced metadata extraction."""

import re
from pathlib import Path
from typing import Any, Dict, List

from .base_analyzer import BaseAnalyzer


class MarkdownAnalyzer(BaseAnalyzer):
    """Analyzer for Markdown files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.md', '.markdown', '.mdown', '.mkd'}
        self.language_name = 'markdown'
    
    def analyze_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze Markdown file content."""
        return {
            'functions': [],  # Markdown doesn't have functions
            'classes': [],   # Markdown doesn't have classes
            'imports': self._extract_links_and_references(content),
            'exports': self._extract_headings(content),
            'patterns': self._extract_markdown_patterns(content)
        }
    
    def _extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """Extract headings as 'exports' from Markdown."""
        headings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # ATX-style headings (# ## ###)
            match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                
                headings.append({
                    'name': title,
                    'type': 'heading',
                    'level': level,
                    'line_number': i,
                    'anchor': self._create_anchor(title)
                })
            
            # Setext-style headings (underlined with = or -)
            elif i < len(lines):
                next_line = lines[i].strip() if i < len(lines) else ''
                if re.match(r'^=+$', next_line):
                    headings.append({
                        'name': line.strip(),
                        'type': 'heading',
                        'level': 1,
                        'line_number': i,
                        'anchor': self._create_anchor(line.strip())
                    })
                elif re.match(r'^-+$', next_line):
                    headings.append({
                        'name': line.strip(),
                        'type': 'heading',
                        'level': 2,
                        'line_number': i,
                        'anchor': self._create_anchor(line.strip())
                    })
        
        return headings
    
    def _extract_links_and_references(self, content: str) -> List[Dict[str, Any]]:
        """Extract links and references as 'imports' from Markdown."""
        links = []
        lines = content.split('\n')
        
        # Inline links [text](url)
        inline_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        # Reference links [text][ref] and [ref]: url
        ref_pattern = r'\[([^\]]+)\]\[([^\]]*)\]'
        ref_def_pattern = r'^\[([^\]]+)\]:\s*(.+)$'
        
        for i, line in enumerate(lines, 1):
            # Find inline links
            for match in re.finditer(inline_pattern, line):
                text, url = match.groups()
                links.append({
                    'name': text,
                    'module': url,
                    'line_number': i,
                    'type': 'inline_link',
                    'statement': match.group(0)
                })
            
            # Find reference links
            for match in re.finditer(ref_pattern, line):
                text, ref = match.groups()
                links.append({
                    'name': text,
                    'module': ref or text,  # If ref is empty, use text as ref
                    'line_number': i,
                    'type': 'reference_link',
                    'statement': match.group(0)
                })
            
            # Find reference definitions
            match = re.match(ref_def_pattern, line.strip())
            if match:
                ref, url = match.groups()
                links.append({
                    'name': ref,
                    'module': url.strip(),
                    'line_number': i,
                    'type': 'reference_definition',
                    'statement': line.strip()
                })
        
        # Extract image references
        img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for i, line in enumerate(lines, 1):
            for match in re.finditer(img_pattern, line):
                alt_text, url = match.groups()
                links.append({
                    'name': alt_text or 'image',
                    'module': url,
                    'line_number': i,
                    'type': 'image_link',
                    'statement': match.group(0)
                })
        
        return links
    
    def _extract_markdown_patterns(self, content: str) -> List[str]:
        """Extract Markdown-specific patterns."""
        patterns = []
        
        # Check for various Markdown features
        if re.search(r'```\w*', content):
            patterns.append('code_blocks')
        
        if re.search(r'`[^`]+`', content):
            patterns.append('inline_code')
        
        if re.search(r'^\|.*\|.*$', content, re.MULTILINE):
            patterns.append('tables')
        
        if re.search(r'^\s*[-*+]\s+', content, re.MULTILINE):
            patterns.append('lists')
        
        if re.search(r'^\s*\d+\.\s+', content, re.MULTILINE):
            patterns.append('numbered_lists')
        
        if re.search(r'^\s*>\s+', content, re.MULTILINE):
            patterns.append('blockquotes')
        
        if re.search(r'\*\*[^*]+\*\*|__[^_]+__', content):
            patterns.append('bold_text')
        
        if re.search(r'\*[^*]+\*|_[^_]+_', content):
            patterns.append('italic_text')
        
        if re.search(r'~~[^~]+~~', content):
            patterns.append('strikethrough')
        
        if re.search(r'^\s*---+\s*$', content, re.MULTILINE):
            patterns.append('horizontal_rules')
        
        if re.search(r'!\[.*\]\(.*\)', content):
            patterns.append('images')
        
        if re.search(r'\[.*\]\(.*\)', content):
            patterns.append('links')
        
        # Check for task lists
        if re.search(r'^\s*[-*+]\s+\[[ x]\]\s+', content, re.MULTILINE):
            patterns.append('task_lists')
        
        # Check for footnotes
        if re.search(r'\[\^[^\]]+\]', content):
            patterns.append('footnotes')
        
        # Check for math expressions
        if re.search(r'\$\$.*\$\$|\$.*\$', content):
            patterns.append('math_expressions')
        
        # Check for front matter (YAML/TOML)
        if re.search(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL):
            patterns.append('yaml_frontmatter')
        elif re.search(r'^\+\+\+\s*\n.*?\n\+\+\+\s*\n', content, re.DOTALL):
            patterns.append('toml_frontmatter')
        
        # Check for specific documentation patterns
        if any(word in content.lower() for word in ['api', 'endpoint', 'parameter', 'response']):
            patterns.append('api_documentation')
        
        if any(word in content.lower() for word in ['install', 'setup', 'configuration', 'getting started']):
            patterns.append('setup_documentation')
        
        if any(word in content.lower() for word in ['tutorial', 'guide', 'how to', 'step by step']):
            patterns.append('tutorial')
        
        if any(word in content.lower() for word in ['changelog', 'release notes', 'version', 'what\'s new']):
            patterns.append('changelog')
        
        return list(set(patterns))
    
    def _create_anchor(self, heading: str) -> str:
        """Create a URL anchor from a heading."""
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        anchor = re.sub(r'[^\w\s-]', '', heading.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def calculate_complexity(self, content: str) -> float:
        """Calculate complexity for Markdown based on structure."""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Markdown complexity factors
        headings = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
        links = len(re.findall(r'\[.*?\]\(.*?\)', content))
        code_blocks = len(re.findall(r'```', content)) // 2  # Pairs of ```
        tables = len(re.findall(r'^\|.*\|.*$', content, re.MULTILINE))
        lists = len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE))
        
        complexity_score = (headings * 0.5 + links * 0.3 + code_blocks * 1.0 + 
                          tables * 1.5 + lists * 0.2)
        
        # Normalize by content length
        if non_empty_lines:
            complexity_score = complexity_score / len(non_empty_lines) * 10
        
        return min(complexity_score, 10.0)
    
    def count_lines_of_code(self, content: str) -> int:
        """Count meaningful content lines in Markdown."""
        lines = content.split('\n')
        content_lines = 0
        
        for line in lines:
            stripped = line.strip()
            # Count non-empty lines that aren't just markup
            if stripped and not re.match(r'^[-=]+$', stripped):
                content_lines += 1
        
        return content_lines
    
    def _is_comment_line(self, line: str) -> bool:
        """Markdown doesn't have traditional comments, but HTML comments are possible."""
        return line.strip().startswith('<!--') or '-->' in line
