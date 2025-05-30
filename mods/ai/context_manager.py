"""
Codebase Context Manager for TaskHero AI.

Manages extraction and preparation of relevant codebase context for AI responses.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import json


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
        """Find files relevant to the query using enhanced multi-pass selection logic."""
        if not self.indexer:
            return []

        try:
            # Get all indexed files
            indexed_files = self.indexer.get_indexed_files()

            if not indexed_files:
                return []

            # Multi-pass file discovery for better results
            try:
                relevant_files = await self._multi_pass_file_discovery(query, indexed_files, max_files)
                if relevant_files:
                    self.logger.info(f"Multi-pass discovery found {len(relevant_files)} relevant files")
                    return relevant_files[:max_files]
            except Exception as e:
                self.logger.warning(f"Multi-pass file discovery failed: {e}")

            # Enhanced file selection using metadata approach from old system
            try:
                relevant_files = self._enhanced_file_selection(query, indexed_files, max_files)
                if relevant_files:
                    self.logger.info(f"Enhanced selection found {len(relevant_files)} relevant files")
                    return relevant_files[:max_files]
            except Exception as e:
                self.logger.warning(f"Enhanced file selection failed: {e}")

            # Fallback: simple keyword matching
            return self._simple_file_matching(query, indexed_files, max_files)

        except Exception as e:
            self.logger.error(f"Error finding relevant files: {e}")
            return []

    async def _multi_pass_file_discovery(self, query: str, indexed_files: List[str], max_files: int) -> List[str]:
        """Multi-pass file discovery combining multiple strategies for better results."""
        try:
            # Pass 1: Semantic similarity search using embeddings
            semantic_files = await self._semantic_file_search(query, indexed_files, max_files // 2)

            # Pass 2: Enhanced keyword matching with metadata
            keyword_files = await self._enhanced_keyword_search(query, indexed_files, max_files // 2)

            # Pass 3: Project structure importance (core files, main modules)
            important_files = self._get_structurally_important_files(query, indexed_files)

            # Pass 4: Task management context (include relevant task files)
            task_files = await self._get_task_context_files(query)

            # Combine and rank all discovered files
            all_discovered = self._combine_and_rank_files(
                semantic_files, keyword_files, important_files, task_files, max_files
            )

            self.logger.info(f"Multi-pass discovery: semantic={len(semantic_files)}, "
                           f"keyword={len(keyword_files)}, important={len(important_files)}, "
                           f"tasks={len(task_files)}, total={len(all_discovered)}")

            return all_discovered

        except Exception as e:
            self.logger.warning(f"Multi-pass file discovery error: {e}")
            return []

    async def _semantic_file_search(self, query: str, indexed_files: List[str], max_files: int) -> List[str]:
        """Search files using semantic similarity via embeddings."""
        try:
            # Use indexer's similarity search if available
            if hasattr(self.indexer, "similarity_search") and self.indexer.similarity_search:
                similar_files = self.indexer.similarity_search.find_similar_files(query, max_files)
                if similar_files:
                    return [f for f in similar_files if f in indexed_files]

            # Fallback: use file descriptions for semantic matching
            return await self._description_based_search(query, indexed_files, max_files)

        except Exception as e:
            self.logger.debug(f"Semantic search failed: {e}")
            return []

    async def _description_based_search(self, query: str, indexed_files: List[str], max_files: int) -> List[str]:
        """Search files based on their descriptions from metadata."""
        try:
            if not self.indexer or not hasattr(self.indexer, 'index_dir'):
                return []

            metadata_dir = os.path.join(self.indexer.index_dir, "metadata")
            if not os.path.exists(metadata_dir):
                return []

            query_keywords = set(re.findall(r'\w+', query.lower()))
            scored_files = []

            for file_path in indexed_files:
                filename = os.path.basename(file_path)
                metadata_file = os.path.join(metadata_dir, f"{filename}.json")

                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            metadata = json.load(f)

                        description = metadata.get("description", "").lower()
                        if description:
                            # Score based on keyword overlap in description
                            desc_words = set(re.findall(r'\w+', description))
                            overlap = len(query_keywords.intersection(desc_words))
                            if overlap > 0:
                                scored_files.append((file_path, overlap))

                    except Exception as e:
                        self.logger.debug(f"Error reading metadata for {filename}: {e}")

            # Sort by score and return top files
            scored_files.sort(key=lambda x: x[1], reverse=True)
            return [file_path for file_path, _ in scored_files[:max_files]]

        except Exception as e:
            self.logger.debug(f"Description-based search failed: {e}")
            return []

    def _enhanced_file_selection(self, query: str, files: List[str], max_files: int) -> List[str]:
        """Enhanced file selection using metadata and semantic approach."""
        try:
            # Import the file selector from the old system for its robust logic
            from ..code.decisions import FileSelector, FileInfo
            import json
            import os

            # Create file infos like the old system does
            file_infos = []

            if self.indexer and hasattr(self.indexer, 'index_dir'):
                metadata_dir = os.path.join(self.indexer.index_dir, "metadata")
                if os.path.exists(metadata_dir):
                    metadata_files = [f for f in os.listdir(metadata_dir) if f.endswith(".json")]

                    for file in metadata_files:
                        try:
                            with open(os.path.join(metadata_dir, file), "r", encoding="utf-8") as f:
                                metadata = json.load(f)

                            file_info = FileInfo(
                                name=os.path.basename(metadata["path"]),
                                path=metadata["path"],
                                description=metadata.get("description", ""),
                                chunks=[],
                            )

                            # Read file content for chunks
                            try:
                                with open(metadata["path"], "r", encoding="utf-8", errors="replace") as f:
                                    content = f.read()

                                chunks = [
                                    {
                                        "text": content,
                                        "type": "file_content",
                                        "start_line": 1,
                                        "end_line": content.count("\n") + 1,
                                    }
                                ]
                                file_info.chunks = chunks
                            except Exception as e:
                                self.logger.warning(f"Error reading file {metadata['path']}: {e}")

                            file_infos.append(file_info)
                        except Exception as e:
                            self.logger.warning(f"Error processing metadata file {file}: {e}")

            # Use the robust file selector if we have file infos
            if file_infos:
                file_selector = FileSelector()

                # Set up similarity search if available from indexer
                if hasattr(self.indexer, "similarity_search") and self.indexer.similarity_search:
                    file_selector.similarity_search = self.indexer.similarity_search

                selected_files = file_selector.pick_files(query, file_infos)
                if selected_files:
                    return selected_files[:max_files]

            # If no metadata available, fall back to simpler approach
            return self._simple_file_matching(query, files, max_files)

        except Exception as e:
            self.logger.warning(f"Enhanced file selection failed: {e}")
            return self._simple_file_matching(query, files, max_files)

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
        """Format context for AI consumption with enhanced hierarchical structure."""
        return self.format_enhanced_context_for_ai(context, "")

    def format_enhanced_context_for_ai(self, context: CodebaseContext, query: str) -> str:
        """Format context with enhanced structure and hierarchy for better AI comprehension."""
        formatted_parts = []

        # 1. Project Context & Purpose
        project_context = self._format_project_purpose(context)
        if project_context:
            formatted_parts.append(project_context)

        # 2. Query-Specific File Hierarchy
        file_hierarchy = self._format_file_hierarchy(context, query)
        if file_hierarchy:
            formatted_parts.append(file_hierarchy)

        # 3. Core Functionality Analysis
        core_functionality = self._format_core_functionality(context)
        if core_functionality:
            formatted_parts.append(core_functionality)

        # 4. User Workflow Context
        user_workflows = self._format_user_workflows(context)
        if user_workflows:
            formatted_parts.append(user_workflows)

        # 5. Code Examples with Explanations
        code_examples = self._format_code_with_explanations(context)
        if code_examples:
            formatted_parts.append(code_examples)

        return '\n\n'.join(formatted_parts)

    def _format_project_purpose(self, context: CodebaseContext) -> str:
        """Format project purpose and overview section."""
        parts = []

        # Enhanced project summary with purpose
        if context.project_summary:
            parts.append("## 🎯 PROJECT PURPOSE & OVERVIEW")
            parts.append(context.project_summary)

            # Add project type detection
            project_type = self._detect_project_type(context)
            if project_type:
                parts.append(f"\n**Project Type:** {project_type}")

            # Add key capabilities summary
            capabilities = self._extract_key_capabilities(context)
            if capabilities:
                parts.append(f"\n**Key Capabilities:** {', '.join(capabilities)}")

        return '\n'.join(parts) if parts else ""

    def _format_file_hierarchy(self, context: CodebaseContext, query: str) -> str:
        """Format file hierarchy with relevance indicators."""
        parts = []

        if context.relevant_files:
            parts.append(f"## 📁 RELEVANT FILES HIERARCHY ({len(context.relevant_files)} files)")

            # Categorize files by type and importance
            categorized_files = self._categorize_files_by_relevance(context.relevant_files, query)

            for category, files in categorized_files.items():
                if files:
                    parts.append(f"\n### {category}")
                    for file_path in files:
                        filename = os.path.basename(file_path)
                        file_desc = self._get_file_description(file_path)
                        if file_desc:
                            parts.append(f"• **{filename}** - {file_desc[:100]}...")
                        else:
                            parts.append(f"• **{filename}**")

        # Add file structure if available
        if context.file_structure:
            parts.append("\n### Project Structure")
            parts.append(f"```\n{context.file_structure}\n```")

        return '\n'.join(parts) if parts else ""

    def _format_core_functionality(self, context: CodebaseContext) -> str:
        """Format core functionality analysis."""
        parts = []

        # Analyze core functionality from file names and descriptions
        core_features = self._analyze_core_features(context)
        if core_features:
            parts.append("## ⚙️ CORE FUNCTIONALITY")
            for feature, description in core_features.items():
                parts.append(f"### {feature}")
                parts.append(description)

        return '\n'.join(parts) if parts else ""

    def _format_user_workflows(self, context: CodebaseContext) -> str:
        """Format user workflow examples from task context."""
        parts = []

        # Extract workflow information from task files if available
        workflows = self._extract_workflow_examples(context)
        if workflows:
            parts.append("## 👤 USER WORKFLOWS & INTERACTIONS")
            for workflow_name, workflow_desc in workflows.items():
                parts.append(f"### {workflow_name}")
                parts.append(workflow_desc)

        return '\n'.join(parts) if parts else ""

    def _format_code_with_explanations(self, context: CodebaseContext) -> str:
        """Format code examples with detailed explanations."""
        parts = []

        if context.code_snippets:
            parts.append("## 💻 CODE EXAMPLES & IMPLEMENTATION")

            # Group snippets by functionality
            grouped_snippets = self._group_snippets_by_functionality(context.code_snippets)

            for group_name, snippets in grouped_snippets.items():
                parts.append(f"\n### {group_name}")

                for snippet in snippets[:3]:  # Limit to 3 snippets per group
                    filename = snippet['filename']
                    file_desc = self._get_file_description(snippet['file_path'])

                    parts.append(f"\n#### {filename}")
                    if file_desc:
                        parts.append(f"**Purpose:** {file_desc}")

                    if snippet.get('context'):
                        parts.append(f"**Context:** {snippet['context']}")

                    parts.append(f"```python\n{snippet['content']}\n```")

        return '\n'.join(parts) if parts else ""

    def _get_file_description(self, file_path: str) -> str:
        """Get file description from metadata."""
        try:
            if self.indexer and hasattr(self.indexer, 'index_dir'):
                metadata_dir = os.path.join(self.indexer.index_dir, "metadata")
                filename = os.path.basename(file_path)
                metadata_file = os.path.join(metadata_dir, f"{filename}.json")

                if os.path.exists(metadata_file):
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        return metadata.get("description", "")
        except Exception as e:
            self.logger.debug(f"Could not get description for {file_path}: {e}")
        return ""

    def set_limits(self, max_files: int = None, max_tokens: int = None, max_snippet_lines: int = None):
        """Update context limits."""
        if max_files is not None:
            self.max_files = max_files
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if max_snippet_lines is not None:
            self.max_snippet_lines = max_snippet_lines

        self.logger.info(f"Updated limits: max_files={self.max_files}, max_tokens={self.max_tokens}, max_snippet_lines={self.max_snippet_lines}")

    async def _enhanced_keyword_search(self, query: str, indexed_files: List[str], max_files: int) -> List[str]:
        """Enhanced keyword search with metadata and content analysis."""
        try:
            query_keywords = set(re.findall(r'\w+', query.lower()))
            scored_files = []

            for file_path in indexed_files:
                score = 0
                filename = os.path.basename(file_path).lower()

                # Score based on filename matches
                for keyword in query_keywords:
                    if keyword in filename:
                        score += 3  # Higher weight for filename matches
                    if keyword in file_path.lower():
                        score += 1

                # Score based on file content (first few lines)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_lines = ''.join(f.readlines()[:10]).lower()
                        for keyword in query_keywords:
                            if keyword in first_lines:
                                score += 2
                except Exception:
                    pass  # Skip files that can't be read

                # Score based on file metadata description
                if self.indexer and hasattr(self.indexer, 'index_dir'):
                    metadata_dir = os.path.join(self.indexer.index_dir, "metadata")
                    metadata_file = os.path.join(metadata_dir, f"{os.path.basename(file_path)}.json")

                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, "r", encoding="utf-8") as f:
                                metadata = json.load(f)
                            description = metadata.get("description", "").lower()
                            for keyword in query_keywords:
                                if keyword in description:
                                    score += 2
                        except Exception:
                            pass

                if score > 0:
                    scored_files.append((file_path, score))

            # Sort by score and return top files
            scored_files.sort(key=lambda x: x[1], reverse=True)
            return [file_path for file_path, _ in scored_files[:max_files]]

        except Exception as e:
            self.logger.debug(f"Enhanced keyword search failed: {e}")
            return []

    def _get_structurally_important_files(self, query: str, indexed_files: List[str]) -> List[str]:
        """Get structurally important files based on project architecture."""
        try:
            important_files = []
            query_lower = query.lower()

            # Define importance patterns
            core_patterns = [
                'app.py', 'main.py', '__init__.py', 'index.py',
                'manager.py', 'handler.py', 'controller.py',
                'config.py', 'settings.py'
            ]

            # Query-specific important files
            query_patterns = {
                'chat': ['chat_handler.py', 'ai_manager.py', 'context_manager.py'],
                'ai': ['ai_manager.py', 'chat_handler.py', 'providers/', 'context_manager.py'],
                'task': ['task_creator.py', 'task_manager.py', 'project_management/'],
                'index': ['indexer.py', 'file_indexer.py', 'search.py'],
                'ui': ['dashboard.py', 'menu.py', 'interface.py'],
                'code': ['decisions.py', 'file_selector.py', 'analyzer.py']
            }

            # Add core files that exist
            for file_path in indexed_files:
                filename = os.path.basename(file_path).lower()
                if any(pattern in filename for pattern in core_patterns):
                    important_files.append(file_path)

            # Add query-specific files
            for keyword, patterns in query_patterns.items():
                if keyword in query_lower:
                    for file_path in indexed_files:
                        if any(pattern in file_path.lower() for pattern in patterns):
                            if file_path not in important_files:
                                important_files.append(file_path)

            # Limit to reasonable number
            return important_files[:10]

        except Exception as e:
            self.logger.debug(f"Error getting structurally important files: {e}")
            return []

    async def _get_task_context_files(self, query: str) -> List[str]:
        """Get relevant task files for project context."""
        try:
            task_files = []

            # Look for task directories
            task_dirs = [
                'theherotasks',
                'project-tasks',
                'tasks',
                'planning'
            ]

            root_path = getattr(self.indexer, 'root_path', '') if self.indexer else ''
            if not root_path:
                return []

            for task_dir in task_dirs:
                task_path = os.path.join(root_path, task_dir)
                if os.path.exists(task_path):
                    # Get completed tasks for context
                    done_path = os.path.join(task_path, 'done')
                    if os.path.exists(done_path):
                        for file in os.listdir(done_path):
                            if file.endswith('.md'):
                                task_files.append(os.path.join(done_path, file))

                    # Get current tasks if relevant to query
                    todo_path = os.path.join(task_path, 'todo')
                    if os.path.exists(todo_path):
                        query_keywords = set(re.findall(r'\w+', query.lower()))
                        for file in os.listdir(todo_path):
                            if file.endswith('.md'):
                                file_lower = file.lower()
                                if any(keyword in file_lower for keyword in query_keywords):
                                    task_files.append(os.path.join(todo_path, file))

            # Limit to most relevant task files
            return task_files[:5]

        except Exception as e:
            self.logger.debug(f"Error getting task context files: {e}")
            return []

    def _combine_and_rank_files(self, *file_lists, max_files: int) -> List[str]:
        """Combine and rank files from multiple discovery passes."""
        try:
            # Flatten all file lists and count occurrences
            file_scores = {}

            for i, file_list in enumerate(file_lists):
                # Give different weights to different discovery methods
                weights = [3, 2, 2, 1]  # semantic, keyword, important, tasks
                weight = weights[i] if i < len(weights) else 1

                for file_path in file_list:
                    if file_path not in file_scores:
                        file_scores[file_path] = 0
                    file_scores[file_path] += weight

            # Sort by combined score
            ranked_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)

            # Return top files, removing duplicates
            result = []
            seen = set()

            for file_path, score in ranked_files:
                if file_path not in seen and len(result) < max_files:
                    result.append(file_path)
                    seen.add(file_path)

            return result

        except Exception as e:
            self.logger.debug(f"Error combining and ranking files: {e}")
            return []

    def _detect_project_type(self, context: CodebaseContext) -> str:
        """Detect project type from files and structure."""
        try:
            file_patterns = {
                'AI/ML Task Management System': ['ai_manager', 'task_creator', 'chat_handler', 'context_manager'],
                'Web Application': ['app.py', 'flask', 'django', 'fastapi'],
                'Desktop Application': ['tkinter', 'qt', 'gui'],
                'CLI Tool': ['argparse', 'click', 'command'],
                'Library/Framework': ['__init__.py', 'setup.py', 'requirements.txt'],
                'Data Analysis': ['pandas', 'numpy', 'jupyter', 'analysis'],
                'API Service': ['api', 'rest', 'endpoint', 'service']
            }

            file_names = [os.path.basename(f).lower() for f in context.relevant_files]
            file_content = ' '.join(file_names)

            for project_type, patterns in file_patterns.items():
                if any(pattern in file_content for pattern in patterns):
                    return project_type

            return "Software Project"

        except Exception as e:
            self.logger.debug(f"Error detecting project type: {e}")
            return ""

    def _extract_key_capabilities(self, context: CodebaseContext) -> List[str]:
        """Extract key capabilities from project files."""
        try:
            capabilities = set()

            # Capability patterns based on file names and descriptions
            capability_patterns = {
                'AI Chat Integration': ['chat_handler', 'ai_manager', 'ollama', 'openai'],
                'Task Management': ['task_creator', 'task_manager', 'project_management'],
                'File Indexing': ['indexer', 'file_indexer', 'search'],
                'Code Analysis': ['analyzer', 'decisions', 'file_selector'],
                'User Interface': ['dashboard', 'menu', 'interface'],
                'Configuration Management': ['settings', 'config', 'environment'],
                'Data Processing': ['processor', 'parser', 'formatter'],
                'API Integration': ['provider', 'client', 'api']
            }

            file_names = [os.path.basename(f).lower() for f in context.relevant_files]
            file_content = ' '.join(file_names)

            for capability, patterns in capability_patterns.items():
                if any(pattern in file_content for pattern in patterns):
                    capabilities.add(capability)

            return list(capabilities)[:5]  # Limit to top 5

        except Exception as e:
            self.logger.debug(f"Error extracting capabilities: {e}")
            return []

    def _categorize_files_by_relevance(self, files: List[str], query: str) -> Dict[str, List[str]]:
        """Categorize files by their relevance and type."""
        try:
            categories = {
                '🔧 Core System Files': [],
                '🤖 AI & Chat Components': [],
                '📋 Task Management': [],
                '🔍 Search & Indexing': [],
                '🎨 User Interface': [],
                '⚙️ Configuration & Settings': [],
                '📄 Documentation & Tasks': [],
                '🔗 Other Components': []
            }

            category_patterns = {
                '🔧 Core System Files': ['app.py', 'main.py', '__init__.py', 'manager.py'],
                '🤖 AI & Chat Components': ['ai_', 'chat_', 'provider', 'ollama', 'openai', 'context_manager'],
                '📋 Task Management': ['task_', 'project_management', 'planning'],
                '🔍 Search & Indexing': ['index', 'search', 'file_selector', 'decisions'],
                '🎨 User Interface': ['dashboard', 'menu', 'interface', 'ui'],
                '⚙️ Configuration & Settings': ['settings', 'config', 'environment'],
                '📄 Documentation & Tasks': ['.md', 'readme', 'doc', 'TASK-']
            }

            for file_path in files:
                filename = os.path.basename(file_path).lower()
                categorized = False

                for category, patterns in category_patterns.items():
                    if any(pattern.lower() in filename or pattern.lower() in file_path.lower() for pattern in patterns):
                        categories[category].append(file_path)
                        categorized = True
                        break

                if not categorized:
                    categories['🔗 Other Components'].append(file_path)

            # Remove empty categories
            return {k: v for k, v in categories.items() if v}

        except Exception as e:
            self.logger.debug(f"Error categorizing files: {e}")
            return {'Files': files}

    def _analyze_core_features(self, context: CodebaseContext) -> Dict[str, str]:
        """Analyze core features from codebase context."""
        try:
            features = {}

            # Feature detection patterns
            feature_patterns = {
                'AI-Powered Chat System': {
                    'files': ['chat_handler', 'ai_manager', 'context_manager'],
                    'description': 'Provides intelligent chat capabilities with codebase context awareness and multiple AI provider support.'
                },
                'Task Management & Planning': {
                    'files': ['task_creator', 'task_manager', 'project_management'],
                    'description': 'Comprehensive task creation, management, and project planning with AI-enhanced workflows.'
                },
                'Intelligent File Discovery': {
                    'files': ['indexer', 'file_selector', 'decisions', 'search'],
                    'description': 'Advanced file indexing and discovery system with semantic search and relevance scoring.'
                },
                'Multi-Provider AI Integration': {
                    'files': ['provider', 'ollama', 'openai', 'anthropic', 'deepseek'],
                    'description': 'Flexible AI provider system supporting multiple models and services with fallback capabilities.'
                },
                'Interactive Dashboard': {
                    'files': ['dashboard', 'menu', 'interface'],
                    'description': 'User-friendly interface for accessing all system features and managing workflows.'
                }
            }

            file_names = [os.path.basename(f).lower() for f in context.relevant_files]
            file_content = ' '.join(file_names)

            for feature_name, feature_info in feature_patterns.items():
                if any(pattern in file_content for pattern in feature_info['files']):
                    features[feature_name] = feature_info['description']

            return features

        except Exception as e:
            self.logger.debug(f"Error analyzing core features: {e}")
            return {}

    def _extract_workflow_examples(self, context: CodebaseContext) -> Dict[str, str]:
        """Extract workflow examples from task files and documentation."""
        try:
            workflows = {}

            # Look for task files in relevant files
            task_files = [f for f in context.relevant_files if f.endswith('.md') and 'task' in f.lower()]

            if task_files:
                workflows['Task Creation Workflow'] = """
1. User accesses Dashboard (option 10: Create New Task)
2. System guides through task definition with AI assistance
3. Context discovery finds relevant files and documentation
4. AI generates comprehensive task details and implementation plan
5. Task is saved with metadata and assigned priority
6. User can track progress and update status"""

                workflows['AI Chat Workflow'] = """
1. User selects Chat with Code option from Dashboard
2. System initializes AI provider (Ollama, OpenAI, etc.)
3. Context manager discovers relevant files based on query
4. Enhanced prompt engineering optimizes AI interaction
5. AI provides detailed, contextual responses about codebase
6. User can continue conversation with maintained context"""

                workflows['File Discovery Workflow'] = """
1. System indexes project files and generates metadata
2. Multi-pass discovery combines semantic and keyword search
3. File importance scoring based on project structure
4. Task management context integration for better relevance
5. Results ranked and presented with descriptions
6. User gets comprehensive view of relevant codebase sections"""

            return workflows

        except Exception as e:
            self.logger.debug(f"Error extracting workflow examples: {e}")
            return {}

    def _group_snippets_by_functionality(self, snippets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group code snippets by functionality."""
        try:
            groups = {
                'AI & Chat Components': [],
                'Task Management': [],
                'File Processing': [],
                'User Interface': [],
                'Configuration': [],
                'Core System': []
            }

            group_patterns = {
                'AI & Chat Components': ['ai_', 'chat_', 'provider', 'context_manager'],
                'Task Management': ['task_', 'project_management'],
                'File Processing': ['index', 'file_', 'search', 'decisions'],
                'User Interface': ['dashboard', 'menu', 'interface'],
                'Configuration': ['settings', 'config', 'environment'],
                'Core System': ['app.py', 'main.py', 'manager.py']
            }

            for snippet in snippets:
                filename = snippet['filename'].lower()
                grouped = False

                for group_name, patterns in group_patterns.items():
                    if any(pattern in filename for pattern in patterns):
                        groups[group_name].append(snippet)
                        grouped = True
                        break

                if not grouped:
                    groups['Core System'].append(snippet)

            # Remove empty groups
            return {k: v for k, v in groups.items() if v}

        except Exception as e:
            self.logger.debug(f"Error grouping snippets: {e}")
            return {'Code Examples': snippets}