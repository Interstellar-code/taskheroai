"""
Codebase Context Manager for TaskHero AI.

Manages extraction and preparation of relevant codebase context for AI responses.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging


@dataclass
class CodebaseContext:
    """Container for codebase context information."""
    relevant_files: List[str]
    code_snippets: List[Dict[str, Any]]
    project_summary: str
    file_structure: str
    total_tokens: int


class CodebaseContextManager:
    """Manages codebase context for AI responses."""

    def __init__(self, indexer=None, file_selector=None):
        """
        Initialize the context manager.

        Args:
            indexer: File indexer instance
            file_selector: File selector instance
        """
        self.indexer = indexer
        self.file_selector = file_selector
        self.logger = logging.getLogger("CodebaseContextManager")

        # Context limits
        self.max_files = 10
        self.max_tokens = 8000
        self.max_snippet_lines = 50

    async def get_relevant_context(
        self,
        query: str,
        max_files: Optional[int] = None,
        max_tokens: Optional[int] = None
    ) -> CodebaseContext:
        """
        Get relevant codebase context for a query.

        Args:
            query: User query to find context for
            max_files: Maximum number of files to include
            max_tokens: Maximum tokens to use for context

        Returns:
            CodebaseContext with relevant information
        """
        max_files = max_files or self.max_files
        max_tokens = max_tokens or self.max_tokens

        try:
            # Get relevant files based on query
            relevant_files = await self._find_relevant_files(query, max_files)

            # Extract code snippets from files
            code_snippets = await self._extract_code_snippets(relevant_files, query)

            # Generate project summary
            project_summary = await self._generate_project_summary()

            # Generate file structure
            file_structure = await self._generate_file_structure()

            # Calculate and limit tokens
            context = CodebaseContext(
                relevant_files=relevant_files,
                code_snippets=code_snippets,
                project_summary=project_summary,
                file_structure=file_structure,
                total_tokens=0
            )

            # Optimize context to fit token limit
            context = self._optimize_context_for_tokens(context, max_tokens)

            self.logger.info(f"Generated context with {len(relevant_files)} files, {context.total_tokens} tokens")
            return context

        except Exception as e:
            self.logger.error(f"Error generating context: {e}")
            # Return minimal context on error
            return CodebaseContext(
                relevant_files=[],
                code_snippets=[],
                project_summary="Error: Could not load project context",
                file_structure="",
                total_tokens=50
            )

    async def _find_relevant_files(self, query: str, max_files: int) -> List[str]:
        """Find files relevant to the query."""
        if not self.indexer:
            return []

        try:
            # Get all indexed files
            indexed_files = self.indexer.get_indexed_files()

            if not indexed_files:
                return []

            # Use file selector if available for intelligent selection
            if self.file_selector:
                try:
                    selected = self.file_selector.select_files_for_query(query, indexed_files, max_files)
                    if selected:
                        return selected[:max_files]
                except Exception as e:
                    self.logger.warning(f"File selector failed: {e}")

            # Fallback: simple keyword matching
            return self._simple_file_matching(query, indexed_files, max_files)

        except Exception as e:
            self.logger.error(f"Error finding relevant files: {e}")
            return []

    def _simple_file_matching(self, query: str, files: List[str], max_files: int) -> List[str]:
        """Simple keyword-based file matching."""
        query_keywords = re.findall(r'\w+', query.lower())
        scored_files = []

        for file_path in files:
            score = 0
            filename = os.path.basename(file_path).lower()

            # Score based on keyword matches in filename
            for keyword in query_keywords:
                if keyword in filename:
                    score += 2
                if keyword in file_path.lower():
                    score += 1

            # Boost important files
            if any(important in filename for important in ['main', 'app', 'index', 'manager']):
                score += 1

            if score > 0:
                scored_files.append((file_path, score))

        # Sort by score and return top files
        scored_files.sort(key=lambda x: x[1], reverse=True)
        return [file_path for file_path, _ in scored_files[:max_files]]

    async def _extract_code_snippets(self, file_paths: List[str], query: str) -> List[Dict[str, Any]]:
        """Extract relevant code snippets from files."""
        snippets = []

        for file_path in file_paths:
            try:
                # Read file content
                if self.indexer and hasattr(self.indexer, 'get_file_content'):
                    content = self.indexer.get_file_content(file_path)
                else:
                    # Direct file reading
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                if not content:
                    continue

                # Extract relevant sections
                relevant_sections = self._find_relevant_sections(content, query)

                for section in relevant_sections:
                    snippets.append({
                        'file_path': file_path,
                        'filename': os.path.basename(file_path),
                        'content': section['content'],
                        'start_line': section.get('start_line', 1),
                        'end_line': section.get('end_line', 1),
                        'context': section.get('context', '')
                    })

            except Exception as e:
                self.logger.warning(f"Error reading file {file_path}: {e}")
                continue

        return snippets

    def _find_relevant_sections(self, content: str, query: str) -> List[Dict[str, Any]]:
        """Find relevant sections within file content."""
        lines = content.split('\n')
        query_keywords = re.findall(r'\w+', query.lower())

        # If file is small, return the whole thing
        if len(lines) <= self.max_snippet_lines:
            return [{
                'content': content,
                'start_line': 1,
                'end_line': len(lines),
                'context': 'Full file content'
            }]

        # Find lines with keyword matches
        relevant_line_groups = []
        current_group = []

        for i, line in enumerate(lines):
            line_lower = line.lower()
            has_keyword = any(keyword in line_lower for keyword in query_keywords)

            if has_keyword or (current_group and i - current_group[-1] <= 3):
                current_group.append(i)
            else:
                if current_group:
                    relevant_line_groups.append(current_group)
                    current_group = []

        if current_group:
            relevant_line_groups.append(current_group)

        # Convert line groups to sections
        sections = []
        for group in relevant_line_groups:
            start_line = max(0, group[0] - 5)  # Include some context
            end_line = min(len(lines), group[-1] + 5)

            if end_line - start_line > self.max_snippet_lines:
                end_line = start_line + self.max_snippet_lines

            section_content = '\n'.join(lines[start_line:end_line])
            sections.append({
                'content': section_content,
                'start_line': start_line + 1,
                'end_line': end_line,
                'context': f'Lines {start_line + 1}-{end_line}'
            })

        # If no relevant sections found, return beginning of file
        if not sections:
            end_line = min(self.max_snippet_lines, len(lines))
            sections.append({
                'content': '\n'.join(lines[:end_line]),
                'start_line': 1,
                'end_line': end_line,
                'context': 'Beginning of file'
            })

        return sections

    async def _generate_project_summary(self) -> str:
        """Generate a summary of the project."""
        if not self.indexer:
            return "Project context not available"

        try:
            root_path = getattr(self.indexer, 'root_path', '')
            project_name = os.path.basename(root_path) if root_path else "Unknown Project"

            indexed_files = self.indexer.get_indexed_files()
            file_count = len(indexed_files)

            # Analyze file types
            file_types = {}
            for file_path in indexed_files:
                ext = os.path.splitext(file_path)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1

            # Generate summary
            summary = f"Project: {project_name}\n"
            summary += f"Location: {root_path}\n"
            summary += f"Total indexed files: {file_count}\n"

            if file_types:
                # Sort by count and show top file types
                sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
                summary += "Main file types: "
                type_strs = [f"{ext or 'no-ext'}({count})" for ext, count in sorted_types[:5]]
                summary += ", ".join(type_strs)

                # Add language detection
                languages = self._detect_languages(file_types)
                if languages:
                    summary += f"\nPrimary languages: {', '.join(languages)}"

            return summary

        except Exception as e:
            self.logger.warning(f"Error generating project summary: {e}")
            return "Error generating project summary"

    def _detect_languages(self, file_types: Dict[str, int]) -> List[str]:
        """Detect programming languages from file extensions."""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.less': 'LESS',
            '.vue': 'Vue.js',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML'
        }

        detected = []
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            if ext in language_map and count > 0:
                detected.append(language_map[ext])
                if len(detected) >= 3:  # Limit to top 3 languages
                    break

        return detected

    def get_file_type_counts(self) -> Dict[str, int]:
        """
        Returns a dictionary of file extensions and their counts in the indexed files.
        """
        if not self.indexer:
            return {}
        
        file_types = {}
        try:
            indexed_files = self.indexer.get_indexed_files()
            for file_path in indexed_files:
                ext = os.path.splitext(file_path)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        except Exception as e:
            self.logger.warning(f"Error getting file type counts: {e}")
        return file_types

    async def _generate_file_structure(self) -> str:
        """Generate an elegant file structure overview."""
        if not self.indexer:
            return ""

        try:
            indexed_files = self.indexer.get_indexed_files()
            if not indexed_files:
                return ""

            # Build a hierarchical tree structure
            root_path = getattr(self.indexer, 'root_path', '')
            structure_lines = []

            # Create a tree structure
            tree = {}
            for file_path in indexed_files:
                if root_path:
                    rel_path = os.path.relpath(file_path, root_path)
                else:
                    rel_path = file_path

                # Split path into parts
                parts = rel_path.split(os.sep)
                current = tree

                # Build nested structure
                for i, part in enumerate(parts):
                    if part not in current:
                        current[part] = {} if i < len(parts) - 1 else None
                    if i < len(parts) - 1:
                        current = current[part]

            # Format tree structure elegantly
            def format_tree(node, prefix="", is_last=True, max_depth=3, current_depth=0):
                if current_depth >= max_depth:
                    return []

                lines = []
                items = list(node.items()) if isinstance(node, dict) else []

                for i, (name, subtree) in enumerate(items):
                    is_last_item = i == len(items) - 1

                    # Choose appropriate tree characters
                    if current_depth == 0:
                        connector = ""
                        new_prefix = ""
                    else:
                        connector = "└── " if is_last_item else "├── "
                        new_prefix = prefix + ("    " if is_last_item else "│   ")

                    lines.append(f"{prefix}{connector}{name}")

                    # Recursively format subdirectories
                    if isinstance(subtree, dict) and subtree:
                        lines.extend(format_tree(subtree, new_prefix, is_last_item, max_depth, current_depth + 1))

                return lines

            structure_lines = format_tree(tree)

            # Limit output size
            if len(structure_lines) > 30:
                structure_lines = structure_lines[:30]
                structure_lines.append("... (truncated for brevity)")

            return '\n'.join(structure_lines)

        except Exception as e:
            self.logger.warning(f"Error generating file structure: {e}")
            return ""

    def _optimize_context_for_tokens(self, context: CodebaseContext, max_tokens: int) -> CodebaseContext:
        """Optimize context to fit within token limit."""
        # Estimate tokens (rough: 4 chars per token)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4

        # Calculate current token usage
        total_tokens = 0
        total_tokens += estimate_tokens(context.project_summary)
        total_tokens += estimate_tokens(context.file_structure)

        for snippet in context.code_snippets:
            total_tokens += estimate_tokens(snippet['content'])

        context.total_tokens = total_tokens

        # If within limit, return as-is
        if total_tokens <= max_tokens:
            return context

        # Reduce context to fit
        self.logger.info(f"Reducing context from {total_tokens} to {max_tokens} tokens")

        # Keep essential info, reduce snippets
        essential_tokens = estimate_tokens(context.project_summary) + estimate_tokens(context.file_structure)
        available_for_snippets = max_tokens - essential_tokens

        # Select most important snippets that fit
        optimized_snippets = []
        used_tokens = 0

        for snippet in context.code_snippets:
            snippet_tokens = estimate_tokens(snippet['content'])
            if used_tokens + snippet_tokens <= available_for_snippets:
                optimized_snippets.append(snippet)
                used_tokens += snippet_tokens
            else:
                # Try to include a truncated version
                max_chars = (available_for_snippets - used_tokens) * 4
                if max_chars > 100:
                    truncated_content = snippet['content'][:max_chars] + "...(truncated)"
                    snippet['content'] = truncated_content
                    optimized_snippets.append(snippet)
                break

        context.code_snippets = optimized_snippets
        context.total_tokens = essential_tokens + used_tokens

        return context

    def format_context_for_ai(self, context: CodebaseContext) -> str:
        """Format context for AI consumption."""
        formatted_parts = []

        # Project summary
        if context.project_summary:
            formatted_parts.append(f"## Project Overview\n{context.project_summary}")

        # File structure
        if context.file_structure:
            formatted_parts.append(f"## File Structure\n{context.file_structure}")

        # Code snippets
        if context.code_snippets:
            formatted_parts.append("## Relevant Code")
            for snippet in context.code_snippets:
                file_info = f"### {snippet['filename']}"
                if snippet.get('context'):
                    file_info += f" ({snippet['context']})"

                formatted_parts.append(f"{file_info}\n```\n{snippet['content']}\n```")

        return '\n\n'.join(formatted_parts)

    def set_limits(self, max_files: int = None, max_tokens: int = None, max_snippet_lines: int = None):
        """Update context limits."""
        if max_files is not None:
            self.max_files = max_files
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if max_snippet_lines is not None:
            self.max_snippet_lines = max_snippet_lines

        self.logger.info(f"Updated limits: max_files={self.max_files}, max_tokens={self.max_tokens}, max_snippet_lines={self.max_snippet_lines}")
