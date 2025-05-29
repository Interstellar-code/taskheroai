"""
Context Processing Module

Handles context analysis, optimization, and embeddings processing for task creation.
Extracted from ai_task_creator.py for better modularity and maintainability.
"""

import logging
from typing import Dict, List, Optional, Any
from .semantic_search import SemanticSearchEngine, ContextChunk, SearchResult
from .context_analyzer import ContextAnalyzer, ProjectContext
from .context_analyzer_enhanced import EnhancedContextAnalyzer, EnhancedProjectContext

logger = logging.getLogger("TaskHeroAI.ProjectManagement.ContextProcessor")


class ContextProcessor:
    """Service for processing and optimizing context for task creation."""

    def __init__(self, project_root: str):
        """Initialize the Context Processor.

        Args:
            project_root: Root directory for project analysis
        """
        self.project_root = project_root
        self.semantic_search = SemanticSearchEngine(project_root)
        self.context_analyzer = ContextAnalyzer(project_root)
        self.enhanced_context_analyzer = EnhancedContextAnalyzer(project_root)

        # Context processing configuration
        self.config = {
            'max_context_tokens': 8000,
            'context_selection_threshold': 0.6,
            'max_context_items': 10,
            'diversity_threshold': 0.8
        }

    def analyze_task_context_enhanced(self, description: str, task_type: str,
                                    specific_files: Optional[List[str]] = None) -> EnhancedProjectContext:
        """Analyze task context using enhanced context analyzer."""
        try:
            return self.enhanced_context_analyzer.analyze_task_context_enhanced(
                description, task_type, specific_files
            )
        except Exception as e:
            logger.error(f"Enhanced context analysis failed: {e}")
            # Fallback to basic context analysis
            basic_context = self.context_analyzer.analyze_project_context(description)
            return self._convert_to_enhanced_context(basic_context)

    def collect_embeddings_context(self, query: str, context: Dict[str, Any]) -> List[ContextChunk]:
        """Collect relevant context from embeddings using semantic search."""
        try:
            # Determine relevant file types based on task type and description
            task_type = context.get('task_type', 'Development')
            relevant_file_types = self._determine_relevant_file_types(query, task_type)

            # Perform semantic search
            search_result = self.semantic_search.search(
                query=query,
                max_results=self.config['max_context_items'] * 2,  # Get more for filtering
                file_types=relevant_file_types
            )

            if not search_result or not search_result.chunks:
                logger.warning(f"No context found for query: {query[:100]}...")
                return []

            # Filter and rank results
            filtered_chunks = self._filter_context_chunks(search_result.chunks, query)

            logger.info(f"Collected {len(filtered_chunks)} context chunks from {len(search_result.chunks)} candidates")
            return filtered_chunks[:self.config['max_context_items']]

        except Exception as e:
            logger.error(f"Context collection failed: {e}")
            return []

    def optimize_context_for_ai(self, relevant_context: List[ContextChunk]) -> List[Dict[str, Any]]:
        """Optimize context for AI processing with dynamic thresholds and intelligent balancing."""
        try:
            if not relevant_context:
                return []

            # Calculate dynamic relevance threshold
            dynamic_threshold = self._calculate_dynamic_relevance_threshold(relevant_context)

            # Apply advanced context filtering
            filtered_context = self._apply_advanced_context_filtering(relevant_context, dynamic_threshold)

            # Apply intelligent context balancing
            balanced_context = self._apply_intelligent_context_balancing(filtered_context)

            # Apply advanced token management
            optimized_context = self._apply_advanced_token_management(balanced_context)

            # Validate context quality
            quality_score = self._validate_context_quality(optimized_context)
            logger.info(f"Context optimization complete. Quality score: {quality_score:.2f}")

            return optimized_context

        except Exception as e:
            logger.error(f"Context optimization failed: {e}")
            return self._convert_chunks_to_dict(relevant_context[:5])  # Fallback

    def _determine_relevant_file_types(self, query: str, task_type: str) -> List[str]:
        """Determine relevant file types based on query, task type, and dynamic project analysis."""
        query_lower = query.lower()

        # Get dynamic file types from project analysis
        dynamic_types = self._get_dynamic_file_types_from_project()

        # Base file types for different task types (enhanced with dynamic discovery)
        type_mapping = {
            'development': dynamic_types.get('code_files', ['.py', '.js', '.ts']) + ['.md'],  # Always include .md for task files
            'documentation': ['.md', '.rst', '.txt', '.doc'] + dynamic_types.get('doc_files', []),
            'configuration': dynamic_types.get('config_files', ['.json', '.yaml', '.yml']) + ['.toml', '.ini', '.cfg'],
            'testing': dynamic_types.get('code_files', ['.py', '.js', '.ts']) + ['.md'],  # Include .md for test documentation
            'design': ['.css', '.scss', '.less', '.html'] + dynamic_types.get('style_files', []),
            'bug fix': dynamic_types.get('code_files', ['.py', '.js', '.ts']) + ['.log', '.md']  # Include .md for bug reports/tasks
        }

        relevant_types = type_mapping.get(task_type.lower(), dynamic_types.get('code_files', ['.py', '.js']) + ['.md'])

        # Add specific types based on query content
        if any(word in query_lower for word in ['config', 'setting', 'environment']):
            relevant_types.extend(['.json', '.yaml', '.yml', '.env'])

        if any(word in query_lower for word in ['test', 'spec', 'unit']):
            relevant_types.extend(['.test.py', '.spec.js', '.test.js'])

        if any(word in query_lower for word in ['style', 'css', 'design']):
            relevant_types.extend(['.css', '.scss', '.html'])

        if any(word in query_lower for word in ['script', 'automation', 'build']):
            relevant_types.extend(['.sh', '.bat', '.ps1', '.py'])

        # PRIORITY: Always include .md for task-related queries
        if any(word in query_lower for word in ['task', 'phase', 'implement', 'feature', 'integration', 'graphiti']):
            if '.md' not in relevant_types:
                relevant_types.append('.md')

        return list(set(relevant_types))  # Remove duplicates

    def _get_dynamic_file_types_from_project(self) -> Dict[str, List[str]]:
        """Get dynamic file types based on actual project analysis (leveraging project report data)."""
        try:
            # Try to get project analysis from indexer/context manager
            dynamic_types = {
                'code_files': [],
                'config_files': [],
                'doc_files': [],
                'style_files': []
            }

            # Check if we have access to project analysis data from semantic search engine
            try:
                # Get file type counts directly from the semantic search engine's loaded chunks
                file_types = self.semantic_search.get_indexed_file_type_counts()

                if file_types:
                    # Categorize file types based on actual project data
                    for ext, count in file_types.items():
                        if count > 0:  # Only include file types that actually exist
                            # Convert internal file type names to common extensions for mapping
                            common_ext = self._map_internal_file_type_to_extension(ext)

                            if common_ext:
                                if common_ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']:
                                    dynamic_types['code_files'].append(common_ext)
                                elif common_ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.env']:
                                    dynamic_types['config_files'].append(common_ext)
                                elif common_ext in ['.md', '.rst', '.txt', '.doc', '.docx']:
                                    dynamic_types['doc_files'].append(common_ext)
                                elif common_ext in ['.css', '.scss', '.sass', '.less']:
                                    dynamic_types['style_files'].append(common_ext)

                    # Sort by most common file types (prioritize what the project actually uses)
                    for category in dynamic_types:
                        dynamic_types[category] = sorted(
                            dynamic_types[category],
                            key=lambda ext: file_types.get(self._map_extension_to_internal_file_type(ext), 0),
                            reverse=True
                        )

                    logger.info(f"Dynamic file types discovered: {dynamic_types}")
                    return dynamic_types

            except Exception as e:
                logger.warning(f"Could not get dynamic file types from semantic search engine: {e}")

            # Fallback to static defaults if dynamic discovery fails
            return {
                'code_files': ['.py', '.js', '.ts', '.java'],
                'config_files': ['.json', '.yaml', '.yml'],
                'doc_files': ['.md', '.rst', '.txt'],
                'style_files': ['.css', '.scss']
            }

        except Exception as e:
            logger.error(f"Dynamic file type discovery failed: {e}")
            # Return safe defaults
            return {
                'code_files': ['.py', '.js'],
                'config_files': ['.json'],
                'doc_files': ['.md'],
                'style_files': ['.css']
            }

    def _map_internal_file_type_to_extension(self, internal_type: str) -> str:
        """Maps internal file type names (from SemanticSearchEngine) to common file extensions."""
        mapping = {
            'python': '.py',
            'javascript': '.js',
            'markdown': '.md',
            'task': '.md', # Tasks are markdown files
            'template': '.md', # Templates are markdown files
            'documentation': '.md', # Documentation can be markdown
            'config': '.json', # Default config to json, could be .yaml, .yml
            'script': '.sh', # Default script to .sh, could be .bat, .ps1
            'html': '.html',
            'stylesheet': '.css',
            'java_family': '.java',
            'cpp': '.cpp',
            'rust': '.rs',
            'go': '.go',
            'php': '.php',
            'ruby': '.rb',
            'build': '.json', # Build files can be various, default to json for now
            'dependency': '.txt', # requirements.txt, package.json, etc.
            'setup': '.sh', # setup scripts
            'test': '.py', # test files
            'other': ''
        }
        return mapping.get(internal_type, '')

    def _map_extension_to_internal_file_type(self, extension: str) -> str:
        """Maps common file extensions to internal file type names (for reverse lookup)."""
        reverse_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.jsx': 'javascript',
            '.tsx': 'javascript',
            '.mjs': 'javascript',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.json': 'config',
            '.yaml': 'config',
            '.yml': 'config',
            '.toml': 'config',
            '.ini': 'config',
            '.cfg': 'config',
            '.conf': 'config',
            '.sh': 'script',
            '.bat': 'script',
            '.cmd': 'script',
            '.ps1': 'script',
            '.bash': 'script',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'stylesheet',
            '.scss': 'stylesheet',
            '.sass': 'stylesheet',
            '.less': 'stylesheet',
            '.java': 'java_family',
            '.kt': 'java_family',
            '.scala': 'java_family',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp',
            '.rs': 'rust',
            '.rlib': 'rust',
            '.go': 'go',
            '.mod': 'go',
            '.php': 'php',
            '.phtml': 'php',
            '.rb': 'ruby',
            '.rake': 'ruby',
            'makefile': 'build',
            'dockerfile': 'build',
            'docker-compose.yml': 'build',
            'docker-compose.yaml': 'build',
            '.gradle': 'build',
            '.maven': 'build',
            '.pom': 'build',
            '.sbt': 'build',
            'requirements.txt': 'dependency',
            'package.json': 'dependency',
            'pipfile': 'dependency',
            'poetry.lock': 'dependency',
            'cargo.toml': 'dependency',
            'setup': 'setup',
            'install': 'setup',
            'deploy': 'setup',
            'test': 'test',
            'spec': 'test',
            'unittest': 'test',
            '.txt': 'documentation',
            '.rst': 'documentation',
            '.adoc': 'documentation',
        }
        # Handle cases where the extension might be a full filename (e.g., 'makefile')
        if extension in reverse_mapping:
            return reverse_mapping[extension]
        # Handle extensions with leading dot
        if extension.startswith('.') and extension in reverse_mapping:
            return reverse_mapping[extension]
        # Fallback for common extensions not explicitly mapped
        if extension.startswith('.'):
            return extension[1:] # Remove dot and return as is
        return extension # Return as is if no dot

    def _filter_context_chunks(self, chunks: List[ContextChunk], query: str) -> List[ContextChunk]:
        """Filter context chunks based on enhanced relevance, quality, and task relationships."""
        filtered_chunks = []
        query_lower = query.lower()

        # Enhanced scoring with task relationship analysis
        enhanced_chunks = self._enhance_chunk_scoring(chunks, query)

        for chunk in enhanced_chunks:
            # Enhanced relevance threshold (lowered to catch more relevant files)
            if chunk.relevance_score < 0.4:
                continue

            # Content quality assessment
            quality_score = self._assess_chunk_quality(chunk)
            if quality_score < 0.3:  # Lowered threshold for better coverage
                continue

            # Duplicate content detection
            if self._is_duplicate_content(chunk, filtered_chunks):
                continue

            # Update chunk with enhanced scores
            chunk.quality_score = quality_score
            filtered_chunks.append(chunk)

        # Sort by combined relevance and quality score
        filtered_chunks.sort(
            key=lambda x: (x.relevance_score * 0.7 + getattr(x, 'quality_score', 0.5) * 0.3),
            reverse=True
        )

        return filtered_chunks

    def _calculate_dynamic_relevance_threshold(self, context_chunks: List[ContextChunk]) -> float:
        """Calculate dynamic relevance threshold based on context quality distribution."""
        if not context_chunks:
            return 0.6

        scores = [chunk.relevance_score for chunk in context_chunks]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)

        # Dynamic threshold: higher when we have high-quality results
        if max_score > 0.8:
            return max(0.7, avg_score * 0.8)
        elif max_score > 0.6:
            return max(0.6, avg_score * 0.7)
        else:
            return max(0.5, avg_score * 0.6)

    def _apply_advanced_context_filtering(self, context_chunks: List[ContextChunk], threshold: float) -> List[ContextChunk]:
        """Apply advanced context filtering with quality assessment."""
        filtered_chunks = []

        for chunk in context_chunks:
            # Basic relevance threshold
            if chunk.relevance_score < threshold:
                continue

            # Content quality assessment
            quality_score = self._assess_chunk_quality(chunk)
            if quality_score < 0.5:
                continue

            # Duplicate content detection
            if self._is_duplicate_content(chunk, filtered_chunks):
                continue

            # Update chunk with quality score
            chunk.quality_score = quality_score
            filtered_chunks.append(chunk)

        return filtered_chunks

    def _apply_intelligent_context_balancing(self, context_chunks: List[ContextChunk]) -> List[ContextChunk]:
        """Apply intelligent context balancing for diversity."""
        if len(context_chunks) <= 5:
            return context_chunks

        balanced_chunks = []
        file_types_seen = set()
        directories_seen = set()

        # First pass: ensure diversity
        for chunk in context_chunks:
            file_ext = chunk.file_path.suffix.lower() if hasattr(chunk.file_path, 'suffix') else ''
            file_dir = str(chunk.file_path.parent) if hasattr(chunk.file_path, 'parent') else ''

            # Prioritize different file types and directories
            if (len(balanced_chunks) < 3 or
                file_ext not in file_types_seen or
                file_dir not in directories_seen):
                balanced_chunks.append(chunk)
                file_types_seen.add(file_ext)
                directories_seen.add(file_dir)

                if len(balanced_chunks) >= self.config['max_context_items']:
                    break

        # Second pass: fill remaining slots with highest relevance
        remaining_slots = self.config['max_context_items'] - len(balanced_chunks)
        if remaining_slots > 0:
            remaining_chunks = [c for c in context_chunks if c not in balanced_chunks]
            remaining_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
            balanced_chunks.extend(remaining_chunks[:remaining_slots])

        return balanced_chunks

    def _apply_advanced_token_management(self, context_chunks: List[ContextChunk]) -> List[Dict[str, Any]]:
        """Apply advanced token management with smart truncation."""
        optimized_context = []
        total_tokens = 0
        max_tokens = self.config['max_context_tokens']

        for chunk in context_chunks:
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            chunk_tokens = len(chunk.text) // 4

            if total_tokens + chunk_tokens > max_tokens:
                # Smart truncation: keep the most relevant parts
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 100:  # Only include if we have meaningful space
                    truncated_text = self._smart_truncate(chunk.text, remaining_tokens * 4)
                    optimized_context.append(self._chunk_to_dict(chunk, truncated_text))
                break

            optimized_context.append(self._chunk_to_dict(chunk))
            total_tokens += chunk_tokens

        return optimized_context

    def _enhance_chunk_scoring(self, chunks: List[ContextChunk], query: str) -> List[ContextChunk]:
        """Enhance chunk scoring with task relationship analysis and contextual relevance."""
        try:
            query_lower = query.lower()

            # Extract key concepts from query
            key_concepts = self._extract_key_concepts(query)

            for chunk in chunks:
                # Start with original relevance score
                enhanced_score = chunk.relevance_score

                # Task relationship bonus
                task_relationship_bonus = self._calculate_task_relationship_score(chunk, query_lower, key_concepts)
                enhanced_score += task_relationship_bonus * 0.3

                # File type relevance bonus
                file_type_bonus = self._calculate_file_type_relevance(chunk, query_lower)
                enhanced_score += file_type_bonus * 0.2

                # Recency bonus for recently modified files
                recency_bonus = self._calculate_recency_bonus(chunk)
                enhanced_score += recency_bonus * 0.1

                # Foundational file bonus (important base files)
                foundational_bonus = self._calculate_foundational_file_bonus(chunk, query_lower)
                enhanced_score += foundational_bonus * 0.4

                # Update the relevance score
                chunk.relevance_score = min(enhanced_score, 1.0)  # Cap at 1.0

            return chunks

        except Exception as e:
            logger.warning(f"Enhanced chunk scoring failed: {e}")
            return chunks

    def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key concepts from the query for better matching."""
        import re

        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}

        # Extract words and technical terms
        words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
        concepts = [word for word in words if word not in stop_words and len(word) > 2]

        # Add technical patterns
        technical_patterns = re.findall(r'\b(?:api|ui|db|sql|js|py|css|html|json|xml|http|rest|graphql|ai|ml|engine|service|module|component|integration|search|retrieval|context|graphiti|task|hero)\b', query.lower())
        concepts.extend(technical_patterns)

        return list(set(concepts))

    def _calculate_task_relationship_score(self, chunk: ContextChunk, query_lower: str, key_concepts: List[str]) -> float:
        """Calculate how related this chunk is to the task being created."""
        score = 0.0
        file_path_lower = chunk.file_path.lower()
        content_lower = chunk.text.lower()

        # Check for direct concept matches in file path
        for concept in key_concepts:
            if concept in file_path_lower:
                score += 0.3
            if concept in content_lower:
                score += 0.2

        # Special bonuses for task-related files
        if 'task' in file_path_lower and any(concept in file_path_lower for concept in key_concepts):
            score += 0.4

        # Bonus for completed tasks that might provide context
        if '/done/' in file_path_lower or '/completed/' in file_path_lower:
            score += 0.3

        # SEMANTIC BOOST: Check for query-relevant content in task files
        if 'task-' in file_path_lower:
            query_terms = query_lower.split()
            content_matches = sum(1 for term in query_terms if term in file_path_lower or term in content_lower)
            if content_matches >= 2:  # Multiple query terms found
                score += 0.5  # Very high boost for semantically relevant task files

        # Bonus for core engine/service files
        if any(term in file_path_lower for term in ['engine', 'service', 'core', 'main', 'base']):
            score += 0.2

        return min(score, 1.0)

    def _calculate_file_type_relevance(self, chunk: ContextChunk, query_lower: str) -> float:
        """Calculate relevance based on file type and query context."""
        file_ext = chunk.file_type.lower() if chunk.file_type else ''

        # Task files are highly relevant for task creation
        if file_ext == '.md' and ('task' in chunk.file_path.lower() or 'todo' in chunk.file_path.lower()):
            return 0.8

        # Python files for development tasks
        if file_ext == '.py' and any(term in query_lower for term in ['implement', 'develop', 'create', 'build']):
            return 0.6

        # Documentation files for understanding context
        if file_ext == '.md' and any(term in query_lower for term in ['documentation', 'guide', 'readme']):
            return 0.5

        # Configuration files for setup/integration tasks
        if file_ext in ['.json', '.yaml', '.yml'] and any(term in query_lower for term in ['config', 'setup', 'integration']):
            return 0.4

        return 0.0

    def _calculate_recency_bonus(self, chunk: ContextChunk) -> float:
        """Calculate bonus for recently modified files."""
        try:
            if not chunk.last_modified:
                return 0.0

            import time
            current_time = time.time()
            days_old = (current_time - chunk.last_modified) / (24 * 60 * 60)

            # Bonus for files modified in the last 30 days
            if days_old <= 7:
                return 0.3
            elif days_old <= 30:
                return 0.2
            elif days_old <= 90:
                return 0.1
            else:
                return 0.0

        except Exception:
            return 0.0

    def _calculate_foundational_file_bonus(self, chunk: ContextChunk, query_lower: str) -> float:
        """Calculate bonus for foundational files that provide important context."""
        file_path_lower = chunk.file_path.lower()

        # Core engine files
        if any(term in file_path_lower for term in ['ai_task_creator', 'task_manager', 'engine', 'core']):
            return 0.5

        # Integration and service files
        if any(term in file_path_lower for term in ['integration', 'service', 'processor', 'retriever']):
            return 0.4

        # Important completed tasks that might be foundational
        if '/done/' in file_path_lower and any(term in file_path_lower for term in ['engine', 'core', 'base', 'foundation']):
            return 0.6

        # Template and configuration files
        if any(term in file_path_lower for term in ['template', 'config', 'setup']):
            return 0.3

        return 0.0

    def _assess_chunk_quality(self, chunk: ContextChunk) -> float:
        """Assess the quality of a context chunk."""
        quality_score = 0.5  # Base score

        # Length-based quality (prefer substantial content)
        if len(chunk.text) > 200:
            quality_score += 0.2
        elif len(chunk.text) < 50:
            quality_score -= 0.2

        # Content-based quality indicators
        text_lower = chunk.text.lower()

        # Positive indicators
        if any(indicator in text_lower for indicator in ['def ', 'class ', 'function', 'method']):
            quality_score += 0.1
        if any(indicator in text_lower for indicator in ['import', 'from', 'require']):
            quality_score += 0.05
        if any(indicator in text_lower for indicator in ['config', 'setting', 'parameter']):
            quality_score += 0.1

        # Negative indicators
        if chunk.text.count('\n') < 2:  # Very short content
            quality_score -= 0.1
        if len(chunk.text.strip()) < 20:  # Almost empty
            quality_score -= 0.3

        return max(0.0, min(1.0, quality_score))

    def _is_duplicate_content(self, chunk: ContextChunk, existing_chunks: List[ContextChunk]) -> bool:
        """Check if chunk content is duplicate of existing chunks."""
        for existing in existing_chunks:
            # Simple similarity check based on text overlap
            if self._calculate_text_similarity(chunk.text, existing.text) > self.config['diversity_threshold']:
                return True
        return False

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity between two strings."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _validate_context_quality(self, optimized_context: List[Dict[str, Any]]) -> float:
        """Validate the quality of optimized context."""
        if not optimized_context:
            return 0.0

        total_score = 0.0
        for ctx in optimized_context:
            # Basic quality metrics
            content_length = len(ctx.get('content', ''))
            relevance = ctx.get('relevance_score', 0.5)

            # Quality score based on content length and relevance
            quality = min(1.0, (content_length / 500) * 0.5 + relevance * 0.5)
            total_score += quality

        return total_score / len(optimized_context)

    def _smart_truncate(self, text: str, max_length: int) -> str:
        """Smart truncation that preserves meaningful content."""
        if len(text) <= max_length:
            return text

        # Try to truncate at sentence boundaries
        sentences = text.split('. ')
        truncated = ""

        for sentence in sentences:
            if len(truncated + sentence + '. ') <= max_length:
                truncated += sentence + '. '
            else:
                break

        if truncated:
            return truncated.strip()

        # Fallback: simple truncation with ellipsis
        return text[:max_length-3] + "..."

    def _chunk_to_dict(self, chunk: ContextChunk, custom_text: str = None) -> Dict[str, Any]:
        """Convert ContextChunk to dictionary format."""
        return {
            'file_name': chunk.file_path.name if hasattr(chunk.file_path, 'name') else str(chunk.file_path),
            'file_path': str(chunk.file_path),
            'file_type': chunk.file_path.suffix if hasattr(chunk.file_path, 'suffix') else '',
            'content': custom_text or chunk.text,
            'relevance_score': chunk.relevance_score,
            'quality_score': getattr(chunk, 'quality_score', 0.5)
        }

    def _convert_chunks_to_dict(self, chunks: List[ContextChunk]) -> List[Dict[str, Any]]:
        """Convert list of ContextChunks to list of dictionaries."""
        return [self._chunk_to_dict(chunk) for chunk in chunks]

    def _convert_to_enhanced_context(self, basic_context: ProjectContext) -> EnhancedProjectContext:
        """Convert basic ProjectContext to EnhancedProjectContext for fallback."""
        # This is a simplified conversion for fallback scenarios
        # In practice, you might want to implement a more sophisticated conversion
        enhanced = EnhancedProjectContext()
        enhanced.user_description = getattr(basic_context, 'description', '')
        enhanced.relevant_files = getattr(basic_context, 'relevant_files', [])
        return enhanced
