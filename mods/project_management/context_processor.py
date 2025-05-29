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

            # Check if we have access to project analysis data
            try:
                from ..ai.context_manager import ContextManager
                context_manager = ContextManager(str(self.project_root))

                # Get project info which includes file type analysis
                project_info = context_manager.get_project_info()

                if project_info and 'file_types' in project_info:
                    file_types = project_info['file_types']

                    # Categorize file types based on actual project data
                    for ext, count in file_types.items():
                        if count > 0:  # Only include file types that actually exist
                            ext_lower = ext.lower()

                            # Code files (prioritize by count)
                            if ext_lower in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']:
                                dynamic_types['code_files'].append(ext_lower)

                            # Configuration files
                            elif ext_lower in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.env']:
                                dynamic_types['config_files'].append(ext_lower)

                            # Documentation files
                            elif ext_lower in ['.md', '.rst', '.txt', '.doc', '.docx']:
                                dynamic_types['doc_files'].append(ext_lower)

                            # Style files
                            elif ext_lower in ['.css', '.scss', '.sass', '.less']:
                                dynamic_types['style_files'].append(ext_lower)

                    # Sort by most common file types (prioritize what the project actually uses)
                    for category in dynamic_types:
                        dynamic_types[category] = sorted(
                            dynamic_types[category],
                            key=lambda ext: file_types.get(ext, 0),
                            reverse=True
                        )

                    logger.info(f"Dynamic file types discovered: {dynamic_types}")
                    return dynamic_types

            except Exception as e:
                logger.warning(f"Could not get dynamic file types from project analysis: {e}")

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

    def _filter_context_chunks(self, chunks: List[ContextChunk], query: str) -> List[ContextChunk]:
        """Filter context chunks based on relevance and quality."""
        filtered_chunks = []
        query_lower = query.lower()

        for chunk in chunks:
            # Basic relevance threshold
            if chunk.relevance_score < self.config['context_selection_threshold']:
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
