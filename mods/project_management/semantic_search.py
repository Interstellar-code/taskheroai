#!/usr/bin/env python3
"""
Semantic Search Module for TaskHero AI

This module implements semantic vector search capabilities for enhanced context collection
during AI task creation. It processes existing chunk data and provides similarity-based
context retrieval.

Phase 4A Implementation:
- Semantic vector search with cosine similarity
- Context extraction and ranking
- Query expansion and semantic clustering
- Performance optimization with caching
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import time
from functools import lru_cache
from .path_resolver import get_project_paths

logger = logging.getLogger(__name__)

@dataclass
class ContextChunk:
    """Represents a chunk of context with metadata."""
    text: str
    file_path: str
    chunk_type: str
    start_line: int
    end_line: int
    confidence: float
    relevance_score: float = 0.0
    file_name: str = ""
    file_type: str = ""
    last_modified: Optional[float] = None

@dataclass
class SearchResult:
    """Represents a search result with ranked context chunks."""
    query: str
    chunks: List[ContextChunk]
    total_chunks: int
    search_time: float
    similarity_threshold: float

class SemanticSearchEngine:
    """
    Semantic search engine for context discovery and ranking.

    Features:
    - TF-IDF vectorization with cosine similarity
    - Context chunk processing and ranking
    - Query expansion and semantic clustering
    - Performance optimization with caching
    """

    def __init__(self, project_root: str, similarity_threshold: float = 0.1):
        """
        Initialize the semantic search engine.

        Args:
            project_root: Root directory of the project
            similarity_threshold: Minimum similarity score for results
        """
        # Use the centralized path resolver
        self.project_paths = get_project_paths(project_root)
        self.project_root = self.project_paths.project_root
        self.embeddings_dir = self.project_paths.embeddings_dir
        self.similarity_threshold = similarity_threshold

        # Initialize vectorizer with optimized parameters
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            lowercase=True,
            strip_accents='unicode'
        )

        # Cache for processed chunks and vectors
        self._chunks_cache: Optional[List[ContextChunk]] = None
        self._vectors_cache: Optional[np.ndarray] = None
        self._last_cache_time: float = 0
        self._cache_ttl: float = 300  # 5 minutes cache TTL

        logger.info(f"Initialized SemanticSearchEngine with threshold {similarity_threshold}")
        logger.info(f"Using embeddings directory: {self.embeddings_dir}")

    def _load_chunks_from_embeddings(self) -> List[ContextChunk]:
        """
        Load and process chunks from existing embedding files.

        Returns:
            List of ContextChunk objects
        """
        chunks = []

        if not self.embeddings_dir.exists():
            logger.warning(f"Embeddings directory not found: {self.embeddings_dir}")
            logger.info(f"Project root was set to: {self.project_root}")
            logger.info("Please ensure the project has been indexed and embeddings have been generated.")
            return chunks

        for embedding_file in self.embeddings_dir.glob("*.json"):
            try:
                with open(embedding_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                file_path = data.get('path', str(embedding_file))
                file_name = Path(file_path).name
                file_type = self._determine_file_type(file_name)
                last_modified = embedding_file.stat().st_mtime

                # Process chunks from the file
                for chunk_data in data.get('chunks', []):
                    chunk = ContextChunk(
                        text=chunk_data.get('text', ''),
                        file_path=file_path,
                        chunk_type=chunk_data.get('type', 'unknown'),
                        start_line=chunk_data.get('start_line', 0),
                        end_line=chunk_data.get('end_line', 0),
                        confidence=chunk_data.get('confidence', 1.0),
                        file_name=file_name,
                        file_type=file_type,
                        last_modified=last_modified
                    )

                    # Only include chunks with meaningful text
                    if chunk.text.strip() and len(chunk.text.strip()) > 10:
                        chunks.append(chunk)

            except Exception as e:
                logger.error(f"Error loading embedding file {embedding_file}: {e}")
                continue

        logger.info(f"Loaded {len(chunks)} chunks from {len(list(self.embeddings_dir.glob('*.json')))} files")
        return chunks

    def _determine_file_type(self, file_name: str) -> str:
        """
        Determine file type based on filename and extension for enhanced relevance scoring.

        Args:
            file_name: Name of the file

        Returns:
            File type category
        """
        file_name_lower = file_name.lower()

        # Python files
        if file_name_lower.endswith(('.py', '.pyx', '.pyi')):
            return 'python'

        # JavaScript/TypeScript files
        elif file_name_lower.endswith(('.js', '.ts', '.jsx', '.tsx', '.mjs')):
            return 'javascript'

        # Markdown files with specific categorization
        elif file_name_lower.endswith(('.md', '.markdown')):
            if 'task' in file_name_lower:
                return 'task'
            elif 'template' in file_name_lower:
                return 'template'
            elif any(keyword in file_name_lower for keyword in ['doc', 'readme', 'guide', 'manual']):
                return 'documentation'
            else:
                return 'markdown'

        # Configuration files
        elif file_name_lower.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf')):
            return 'config'

        # Script files
        elif file_name_lower.endswith(('.bat', '.cmd', '.sh', '.ps1', '.bash')):
            return 'script'

        # Web files
        elif file_name_lower.endswith(('.html', '.htm')):
            return 'html'
        elif file_name_lower.endswith(('.css', '.scss', '.sass', '.less')):
            return 'stylesheet'

        # Other programming languages
        elif file_name_lower.endswith(('.java', '.kt', '.scala')):
            return 'java_family'
        elif file_name_lower.endswith(('.cpp', '.cc', '.cxx', '.c', '.h', '.hpp')):
            return 'cpp'
        elif file_name_lower.endswith(('.rs', '.rlib')):
            return 'rust'
        elif file_name_lower.endswith(('.go', '.mod')):
            return 'go'
        elif file_name_lower.endswith(('.php', '.phtml')):
            return 'php'
        elif file_name_lower.endswith(('.rb', '.rake')):
            return 'ruby'

        # Build and project files
        elif file_name_lower in ['makefile', 'dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
            return 'build'
        elif file_name_lower.endswith(('.gradle', '.maven', '.pom', '.sbt')):
            return 'build'
        elif file_name_lower in ['package.json', 'requirements.txt', 'pipfile', 'poetry.lock', 'cargo.toml']:
            return 'dependency'

        # Setup and installation files
        elif any(keyword in file_name_lower for keyword in ['setup', 'install', 'deploy']):
            return 'setup'

        # Test files
        elif any(keyword in file_name_lower for keyword in ['test', 'spec', 'unittest']):
            return 'test'

        # Documentation files
        elif file_name_lower.endswith(('.txt', '.rst', '.adoc')):
            return 'documentation'

        else:
            return 'other'

    def _get_cached_data(self) -> Tuple[Optional[List[ContextChunk]], Optional[np.ndarray]]:
        """
        Get cached chunks and vectors if still valid.

        Returns:
            Tuple of (chunks, vectors) or (None, None) if cache invalid
        """
        current_time = time.time()

        if (self._chunks_cache is not None and
            self._vectors_cache is not None and
            current_time - self._last_cache_time < self._cache_ttl):
            return self._chunks_cache, self._vectors_cache

        return None, None

    def _update_cache(self, chunks: List[ContextChunk], vectors: np.ndarray):
        """
        Update the cache with new data.

        Args:
            chunks: List of context chunks
            vectors: TF-IDF vectors
        """
        self._chunks_cache = chunks
        self._vectors_cache = vectors
        self._last_cache_time = time.time()

    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess and expand the search query with enhanced intelligence.

        Args:
            query: Original search query

        Returns:
            Preprocessed and expanded query
        """
        # Clean the query
        query = re.sub(r'[^\w\s-]', ' ', query.lower())
        query = re.sub(r'\s+', ' ', query).strip()

        # Classify query intent for targeted expansion
        query_intent = self._classify_query_intent(query)

        # Apply intent-specific query enhancement
        enhanced_query = self._enhance_query_by_intent(query, query_intent)

        return enhanced_query

    def _enhance_query_by_intent(self, query: str, intent: str) -> str:
        """
        Enhance query based on classified intent with technical synonyms and context.

        Args:
            query: Original query
            intent: Classified query intent

        Returns:
            Enhanced query with relevant technical terms
        """
        query_terms = query.split()
        enhanced_terms = set(query_terms)

        # Technical expansions with more comprehensive coverage
        technical_expansions = {
            # Development terms
            'implement': ['implement', 'develop', 'code', 'build', 'create', 'program'],
            'enhance': ['enhance', 'improve', 'optimize', 'upgrade', 'refactor', 'modernize'],
            'setup': ['setup', 'install', 'configure', 'initialize', 'deploy', 'provision'],
            'script': ['script', 'automation', 'batch', 'command', 'executable', 'runner'],
            'config': ['config', 'configuration', 'settings', 'parameters', 'options', 'preferences'],
            'fix': ['fix', 'repair', 'resolve', 'debug', 'troubleshoot', 'patch'],
            'test': ['test', 'testing', 'validation', 'verification', 'spec', 'unittest'],

            # System components
            'api': ['api', 'endpoint', 'service', 'interface', 'rest', 'http', 'webservice'],
            'database': ['database', 'db', 'storage', 'persistence', 'data', 'repository'],
            'auth': ['auth', 'authentication', 'authorization', 'login', 'security', 'access'],
            'ui': ['ui', 'interface', 'frontend', 'gui', 'display', 'view', 'component'],
            'backend': ['backend', 'server', 'service', 'api', 'logic', 'processing'],

            # File types and technologies
            'python': ['python', 'py', 'script', 'module', 'package', 'library'],
            'javascript': ['javascript', 'js', 'node', 'npm', 'frontend', 'client'],
            'json': ['json', 'config', 'data', 'format', 'structure', 'schema'],
            'yaml': ['yaml', 'yml', 'config', 'configuration', 'deployment', 'docker'],

            # Operations
            'deploy': ['deploy', 'deployment', 'release', 'publish', 'distribute', 'install'],
            'build': ['build', 'compile', 'package', 'bundle', 'assemble', 'generate'],
            'monitor': ['monitor', 'logging', 'tracking', 'observability', 'metrics', 'alerts'],

            # Documentation
            'document': ['document', 'docs', 'documentation', 'guide', 'manual', 'readme'],
            'guide': ['guide', 'tutorial', 'howto', 'instructions', 'walkthrough', 'example']
        }

        # Documentation-specific expansions
        documentation_expansions = {
            'create': ['create', 'write', 'generate', 'produce', 'develop', 'compose'],
            'explain': ['explain', 'describe', 'clarify', 'detail', 'outline', 'document'],
            'overview': ['overview', 'summary', 'introduction', 'synopsis', 'abstract', 'brief'],
            'guide': ['guide', 'tutorial', 'manual', 'handbook', 'reference', 'documentation']
        }

        # Task management expansions
        task_expansions = {
            'task': ['task', 'work', 'assignment', 'ticket', 'issue', 'item'],
            'project': ['project', 'initiative', 'effort', 'work', 'development', 'implementation'],
            'manage': ['manage', 'organize', 'coordinate', 'handle', 'control', 'oversee'],
            'plan': ['plan', 'planning', 'strategy', 'roadmap', 'schedule', 'timeline'],
            'workflow': ['workflow', 'process', 'procedure', 'pipeline', 'flow', 'sequence']
        }

        # Select appropriate expansion set based on intent
        if intent == 'technical':
            expansion_dict = technical_expansions
            # Add technical context terms
            enhanced_terms.update(['implementation', 'development', 'technical'])
        elif intent == 'documentation':
            expansion_dict = documentation_expansions
            # Add documentation context terms
            enhanced_terms.update(['documentation', 'reference', 'guide'])
        elif intent == 'task_management':
            expansion_dict = task_expansions
            # Add task management context terms
            enhanced_terms.update(['management', 'organization', 'planning'])
        else:
            # Mixed approach for general/mixed queries
            expansion_dict = {**technical_expansions, **documentation_expansions, **task_expansions}

        # Apply expansions
        for term in query_terms:
            if term in expansion_dict:
                # Add top 3 related terms for better coverage
                enhanced_terms.update(expansion_dict[term][:3])

        # Add domain-specific technical terms based on common patterns
        self._add_domain_specific_terms(enhanced_terms, query_terms, intent)

        return ' '.join(enhanced_terms)

    def _add_domain_specific_terms(self, enhanced_terms: set, query_terms: list, intent: str):
        """
        Add domain-specific technical terms based on query patterns.

        Args:
            enhanced_terms: Set of terms to enhance
            query_terms: Original query terms
            intent: Query intent classification
        """
        query_text = ' '.join(query_terms)

        # Web development patterns
        if any(term in query_text for term in ['web', 'http', 'server', 'client']):
            enhanced_terms.update(['web', 'http', 'server', 'client', 'request', 'response'])

        # DevOps patterns
        if any(term in query_text for term in ['deploy', 'docker', 'container', 'ci', 'cd']):
            enhanced_terms.update(['deployment', 'container', 'orchestration', 'pipeline', 'automation'])

        # Data patterns
        if any(term in query_text for term in ['data', 'database', 'storage', 'query']):
            enhanced_terms.update(['data', 'storage', 'persistence', 'query', 'schema', 'model'])

        # Security patterns
        if any(term in query_text for term in ['auth', 'security', 'login', 'access']):
            enhanced_terms.update(['security', 'authentication', 'authorization', 'access', 'permission'])

        # Testing patterns
        if any(term in query_text for term in ['test', 'spec', 'unit', 'integration']):
            enhanced_terms.update(['testing', 'validation', 'verification', 'quality', 'coverage'])

        # Installation/Setup patterns
        if any(term in query_text for term in ['install', 'setup', 'configure', 'init']):
            enhanced_terms.update(['installation', 'configuration', 'initialization', 'environment', 'dependencies'])

    def _calculate_relevance_scores(self, chunks: List[ContextChunk],
                                  similarities: np.ndarray,
                                  query: str) -> List[ContextChunk]:
        """
        Calculate enhanced relevance scores for chunks with balanced file type consideration.

        Args:
            chunks: List of context chunks
            similarities: Cosine similarity scores
            query: Original search query

        Returns:
            List of chunks with updated relevance scores
        """
        query_lower = query.lower()
        query_intent = self._classify_query_intent(query_lower)

        for i, chunk in enumerate(chunks):
            base_score = similarities[i]

            # PHASE 4: Exact Match Prioritization - Add massive boost for exact filename matches
            exact_match_boost = self._calculate_exact_match_boost(chunk, query_lower, query_intent)

            # Calculate boost factors based on query intent and file type
            boost_factors = self._calculate_file_type_boost(chunk, query_lower, query_intent)

            # Chunk type relevance
            boost_factors *= self._calculate_chunk_type_boost(chunk, query_intent)

            # Confidence boost
            boost_factors *= chunk.confidence

            # Freshness boost (more recent files get slight boost)
            boost_factors *= self._calculate_freshness_boost(chunk)

            # Text length normalization (prefer substantial chunks)
            boost_factors *= self._calculate_length_boost(chunk)

            # Apply boosts and update score (exact match boost is additive for maximum impact)
            chunk.relevance_score = (base_score * boost_factors) + exact_match_boost

        return chunks

    def _classify_query_intent(self, query_lower: str) -> str:
        """
        Classify the intent of the query to determine appropriate scoring strategy.

        Args:
            query_lower: Lowercase query string

        Returns:
            Query intent classification: 'technical', 'documentation', 'mixed', or 'general'
        """
        # Technical indicators
        technical_keywords = {
            'implement', 'code', 'function', 'class', 'method', 'algorithm', 'api',
            'setup', 'install', 'config', 'script', 'build', 'deploy', 'debug',
            'enhance', 'improve', 'optimize', 'refactor', 'fix', 'bug', 'error',
            'test', 'testing', 'unit', 'integration', 'validation'
        }

        # Documentation indicators
        documentation_keywords = {
            'document', 'docs', 'readme', 'guide', 'manual', 'tutorial', 'help',
            'explain', 'describe', 'overview', 'summary', 'introduction'
        }

        # Task management indicators
        task_keywords = {
            'task', 'project', 'management', 'planning', 'template', 'workflow'
        }

        query_words = set(query_lower.split())

        technical_score = len(query_words & technical_keywords)
        documentation_score = len(query_words & documentation_keywords)
        task_score = len(query_words & task_keywords)

        # Classify based on keyword presence
        if technical_score > documentation_score and technical_score > task_score:
            return 'technical'
        elif documentation_score > technical_score and documentation_score > task_score:
            return 'documentation'
        elif task_score > 0:
            return 'task_management'
        elif technical_score > 0 and documentation_score > 0:
            return 'mixed'
        else:
            return 'general'

    def _calculate_file_type_boost(self, chunk: ContextChunk, query_lower: str, query_intent: str) -> float:
        """
        Calculate file type boost based on query intent and balanced scoring.

        Args:
            chunk: Context chunk to score
            query_lower: Lowercase query string
            query_intent: Classified query intent

        Returns:
            File type boost factor
        """
        boost = 1.0
        file_type = chunk.file_type

        # Define file type groups for easier scoring
        code_files = ['python', 'javascript', 'java_family', 'cpp', 'rust', 'go', 'php', 'ruby']
        config_files = ['config', 'dependency', 'build']
        script_files = ['script', 'setup']
        doc_files = ['documentation', 'markdown']

        # Intent-based scoring with balanced approach
        if query_intent == 'technical':
            # For technical queries, prioritize code files but don't exclude docs
            if file_type in code_files:
                boost *= 1.4
            elif file_type in config_files + script_files:
                boost *= 1.3  # Configuration and scripts are highly relevant
            elif file_type in doc_files:
                boost *= 1.1  # Still valuable for context
            elif file_type == 'task':
                boost *= 0.9  # Lower priority but not excluded
            elif file_type == 'test':
                boost *= 1.2  # Tests are relevant for technical queries

        elif query_intent == 'documentation':
            # For documentation queries, prioritize docs but include relevant code
            if file_type in doc_files:
                boost *= 1.4
            elif file_type == 'task':
                boost *= 1.2
            elif file_type in code_files:
                boost *= 1.0  # Equal weight for code context
            elif file_type in config_files:
                boost *= 0.9

        elif query_intent == 'task_management':
            # For task management queries, prioritize task files but include code context
            if file_type == 'task':
                boost *= 1.3  # Reduced from 1.5 to be less dominant
            elif file_type == 'template':
                boost *= 1.3
            elif file_type in code_files:
                boost *= 1.2  # Increased to provide better code context
            elif file_type in config_files + script_files:
                boost *= 1.15  # Setup and config files are relevant
            elif file_type in doc_files:
                boost *= 1.1

        elif query_intent == 'mixed':
            # For mixed queries, provide balanced scoring
            if file_type in code_files:
                boost *= 1.2
            elif file_type in doc_files + ['task']:
                boost *= 1.2
            elif file_type in config_files + script_files:
                boost *= 1.15
            elif file_type == 'test':
                boost *= 1.1

        else:  # general
            # For general queries, slight preference for documentation
            if file_type in doc_files:
                boost *= 1.2
            elif file_type in code_files + ['task']:
                boost *= 1.1
            elif file_type in config_files:
                boost *= 1.05

        # Additional specific keyword matching (reduced impact)
        if 'setup' in query_lower or 'install' in query_lower:
            if file_type in ['setup', 'config', 'dependency', 'script'] or 'setup' in chunk.file_name.lower():
                boost *= 1.2

        if 'script' in query_lower:
            if file_type in ['script', 'python', 'javascript'] or chunk.file_name.lower().endswith(('.bat', '.sh', '.ps1')):
                boost *= 1.2

        if 'config' in query_lower or 'configuration' in query_lower:
            if file_type in ['config', 'dependency']:
                boost *= 1.2

        if 'test' in query_lower or 'testing' in query_lower:
            if file_type == 'test':
                boost *= 1.3

        if 'build' in query_lower or 'deploy' in query_lower:
            if file_type in ['build', 'dependency', 'script']:
                boost *= 1.2

        return boost

    def _calculate_chunk_type_boost(self, chunk: ContextChunk, query_intent: str) -> float:
        """
        Calculate chunk type boost based on query intent.

        Args:
            chunk: Context chunk to score
            query_intent: Classified query intent

        Returns:
            Chunk type boost factor
        """
        boost = 1.0
        chunk_type = chunk.chunk_type

        if query_intent == 'technical':
            if chunk_type == 'function_definition':
                boost *= 1.3
            elif chunk_type == 'class_definition':
                boost *= 1.2
            elif chunk_type in ['import_statement', 'config_section']:
                boost *= 1.1
        elif query_intent in ['documentation', 'task_management']:
            if chunk_type in ['documentation_section', 'comment_block']:
                boost *= 1.2
            elif chunk_type == 'function_definition':
                boost *= 1.1  # Still relevant for understanding

        return boost

    def _calculate_freshness_boost(self, chunk: ContextChunk) -> float:
        """Calculate freshness boost based on file modification time."""
        boost = 1.0

        if chunk.last_modified:
            days_old = (time.time() - chunk.last_modified) / (24 * 3600)
            if days_old < 7:  # Files modified in last week
                boost *= 1.1
            elif days_old < 30:  # Files modified in last month
                boost *= 1.05

        return boost

    def _calculate_length_boost(self, chunk: ContextChunk) -> float:
        """Calculate length boost based on chunk text length."""
        text_length = len(chunk.text)

        if 100 <= text_length <= 1000:  # Sweet spot for chunk size
            return 1.1
        elif text_length < 50:  # Too short
            return 0.8
        elif text_length > 2000:  # Too long, might be less focused
            return 0.95
        else:
            return 1.0

    def _calculate_exact_match_boost(self, chunk: ContextChunk, query_lower: str, query_intent: str) -> float:
        """
        Phase 4: Calculate massive relevance boost for exact filename matches.

        Args:
            chunk: Context chunk to score
            query_lower: Lowercase query string
            query_intent: Classified query intent

        Returns:
            Exact match boost score (additive, not multiplicative)
        """
        boost = 0.0
        file_name = chunk.file_name.lower()
        file_path = chunk.file_path.lower()
        query_terms = query_lower.split()

        # Exact filename matching - massive boost for perfect matches
        for term in query_terms:
            if len(term) > 2:  # Skip very short terms
                if term in file_name:
                    # Compound filename matching (e.g., "setup_windows" matches "setup" and "windows")
                    if '_' in file_name or '-' in file_name:
                        file_parts = file_name.replace('_', ' ').replace('-', ' ').split()
                        if term in file_parts:
                            boost += 0.8  # Very high boost for exact component match
                    else:
                        boost += 0.6  # High boost for substring match

        # Special handling for setup-related queries
        if any(setup_term in query_lower for setup_term in ['setup', 'install', 'configure']):
            setup_files = ['setup_windows.bat', 'setup_windows.ps1', 'setup_linux.sh', 'setup.py', 'install.bat']
            if any(setup_file in file_name for setup_file in setup_files):
                boost += 0.9  # Maximum boost for setup files in setup queries

        # Windows/Linux platform-specific matching
        if 'windows' in query_lower and 'windows' in file_name:
            boost += 0.7  # High boost for Windows-specific files
        if 'linux' in query_lower and 'linux' in file_name:
            boost += 0.7  # High boost for Linux-specific files

        # File extension prioritization based on query context
        if file_name.endswith('.bat') and ('windows' in query_lower or 'bat' in query_lower):
            boost += 0.5  # High boost for .bat files in Windows queries
        if file_name.endswith('.ps1') and ('powershell' in query_lower or 'ps1' in query_lower or 'windows' in query_lower):
            boost += 0.5  # High boost for PowerShell files
        if file_name.endswith('.sh') and ('linux' in query_lower or 'bash' in query_lower or 'shell' in query_lower):
            boost += 0.5  # High boost for shell scripts

        # Root directory boost for setup-related queries
        is_root_file = '/' not in chunk.file_path.strip('/') and '\\' not in chunk.file_path.strip('\\')
        if is_root_file and any(setup_term in query_lower for setup_term in ['setup', 'install', 'configure', 'run', 'launch']):
            boost += 0.3  # Significant boost for root setup files

        return boost

    def _select_diverse_chunks(self, chunks: List[ContextChunk], max_results: int, query: str) -> List[ContextChunk]:
        """
        Select chunks with diversity consideration to ensure balanced file type representation.

        Args:
            chunks: Sorted list of chunks by relevance score
            max_results: Maximum number of results to return
            query: Original search query

        Returns:
            List of selected chunks with balanced diversity
        """
        if len(chunks) <= max_results:
            return chunks[:max_results]

        query_intent = self._classify_query_intent(query.lower())
        selected_chunks = []
        file_type_counts = {}

        # Define diversity targets based on query intent
        if query_intent == 'technical':
            # For technical queries, aim for 60% code, 20% config/script, 20% docs
            target_ratios = {
                'code': 0.6,
                'config_script': 0.2,
                'docs': 0.2
            }
        elif query_intent == 'documentation':
            # For documentation queries, aim for 50% docs, 30% code, 20% config
            target_ratios = {
                'docs': 0.5,
                'code': 0.3,
                'config_script': 0.2
            }
        elif query_intent == 'task_management':
            # For task management, aim for 40% task, 30% code, 30% docs
            target_ratios = {
                'task': 0.4,
                'code': 0.3,
                'docs': 0.3
            }
        else:
            # For mixed/general queries, aim for balanced representation
            target_ratios = {
                'code': 0.4,
                'docs': 0.3,
                'config_script': 0.2,
                'task': 0.1
            }

        # Calculate target counts
        target_counts = {category: int(max_results * ratio) for category, ratio in target_ratios.items()}

        # Categorize chunks by type groups
        categorized_chunks = {
            'code': [],
            'docs': [],
            'config_script': [],
            'task': [],
            'other': []
        }

        code_files = ['python', 'javascript', 'java_family', 'cpp', 'rust', 'go', 'php', 'ruby']
        config_script_files = ['config', 'dependency', 'build', 'script', 'setup']
        doc_files = ['documentation', 'markdown']

        for chunk in chunks:
            if chunk.file_type in code_files or chunk.file_type == 'test':
                categorized_chunks['code'].append(chunk)
            elif chunk.file_type in config_script_files:
                categorized_chunks['config_script'].append(chunk)
            elif chunk.file_type in doc_files:
                categorized_chunks['docs'].append(chunk)
            elif chunk.file_type == 'task' or chunk.file_type == 'template':
                categorized_chunks['task'].append(chunk)
            else:
                categorized_chunks['other'].append(chunk)

        # Select chunks according to target ratios, but prioritize relevance within each category
        for category, target_count in target_counts.items():
            available_chunks = categorized_chunks.get(category, [])
            selected_from_category = min(target_count, len(available_chunks))
            selected_chunks.extend(available_chunks[:selected_from_category])

        # Fill remaining slots with highest relevance chunks not yet selected
        remaining_slots = max_results - len(selected_chunks)
        if remaining_slots > 0:
            selected_chunk_ids = {id(chunk) for chunk in selected_chunks}
            remaining_chunks = [chunk for chunk in chunks if id(chunk) not in selected_chunk_ids]
            selected_chunks.extend(remaining_chunks[:remaining_slots])

        # Sort final selection by relevance score
        selected_chunks.sort(key=lambda x: x.relevance_score, reverse=True)

        # Log diversity information
        final_file_types = {}
        for chunk in selected_chunks:
            final_file_types[chunk.file_type] = final_file_types.get(chunk.file_type, 0) + 1

        logger.info(f"Selected diverse context: {final_file_types}")

        return selected_chunks[:max_results]

    def search_multi_query(self, query: str, max_results: int = 10,
                          file_types: Optional[List[str]] = None) -> SearchResult:
        """
        Perform multi-query search using different query variations for comprehensive results.

        Args:
            query: Original search query
            max_results: Maximum number of results to return
            file_types: Optional list of file types to filter by

        Returns:
            SearchResult with aggregated and ranked context chunks
        """
        start_time = time.time()

        # Generate multiple query variations
        query_variations = self._generate_query_variations(query)

        # Collect results from all query variations
        all_chunks = []
        chunk_scores = {}  # Track best score for each chunk

        for variation in query_variations:
            variation_result = self.search(variation, max_results * 2, file_types)

            for chunk in variation_result.chunks:
                chunk_id = f"{chunk.file_path}:{chunk.start_line}:{chunk.end_line}"

                # Keep the best score for each unique chunk
                if chunk_id not in chunk_scores or chunk.relevance_score > chunk_scores[chunk_id]:
                    chunk_scores[chunk_id] = chunk.relevance_score
                    # Update or add chunk
                    existing_chunk = next((c for c in all_chunks if f"{c.file_path}:{c.start_line}:{c.end_line}" == chunk_id), None)
                    if existing_chunk:
                        existing_chunk.relevance_score = chunk.relevance_score
                    else:
                        all_chunks.append(chunk)

        # Sort by relevance and apply diversity selection
        all_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        result_chunks = self._select_diverse_chunks(all_chunks, max_results, query)

        search_time = time.time() - start_time

        logger.info(f"Multi-query search completed: '{query}' -> {len(result_chunks)} results from {len(query_variations)} variations in {search_time:.3f}s")

        return SearchResult(
            query=query,
            chunks=result_chunks,
            total_chunks=len(all_chunks),
            search_time=search_time,
            similarity_threshold=self.similarity_threshold
        )

    def _generate_query_variations(self, query: str) -> List[str]:
        """
        Generate multiple query variations for comprehensive search coverage.

        Args:
            query: Original query

        Returns:
            List of query variations
        """
        variations = [query]  # Always include original
        query_intent = self._classify_query_intent(query.lower())
        query_terms = query.lower().split()

        # Variation 1: Enhanced query (already implemented)
        enhanced_query = self._preprocess_query(query)
        if enhanced_query != query:
            variations.append(enhanced_query)

        # Variation 2: Core technical terms only
        if query_intent == 'technical':
            core_terms = self._extract_core_technical_terms(query_terms)
            if core_terms:
                variations.append(' '.join(core_terms))

        # Variation 3: Domain-specific variation
        domain_variation = self._create_domain_specific_variation(query, query_intent)
        if domain_variation and domain_variation not in variations:
            variations.append(domain_variation)

        # Variation 4: Simplified query (key terms only)
        simplified = self._create_simplified_query(query_terms)
        if simplified and simplified not in variations:
            variations.append(simplified)

        # Variation 5: Context-aware variation
        context_variation = self._create_context_aware_variation(query, query_intent)
        if context_variation and context_variation not in variations:
            variations.append(context_variation)

        logger.debug(f"Generated {len(variations)} query variations for: '{query}'")
        return variations[:5]  # Limit to 5 variations to avoid over-processing

    def _extract_core_technical_terms(self, query_terms: List[str]) -> List[str]:
        """Extract core technical terms from query."""
        technical_terms = {
            'implement', 'develop', 'code', 'build', 'create', 'setup', 'install',
            'configure', 'deploy', 'script', 'function', 'class', 'method', 'api',
            'database', 'auth', 'test', 'fix', 'enhance', 'optimize', 'config'
        }

        core_terms = []
        for term in query_terms:
            if term in technical_terms or len(term) > 6:  # Include longer terms as potentially technical
                core_terms.append(term)

        return core_terms

    def _create_domain_specific_variation(self, query: str, intent: str) -> str:
        """Create domain-specific query variation."""
        query_lower = query.lower()

        # Web development domain
        if any(term in query_lower for term in ['web', 'http', 'server', 'frontend', 'backend']):
            return f"{query} web development http server client"

        # DevOps domain
        elif any(term in query_lower for term in ['deploy', 'docker', 'container', 'ci', 'cd']):
            return f"{query} deployment automation pipeline devops"

        # Data domain
        elif any(term in query_lower for term in ['data', 'database', 'storage', 'query']):
            return f"{query} data storage database persistence"

        # Security domain
        elif any(term in query_lower for term in ['auth', 'security', 'login', 'access']):
            return f"{query} security authentication authorization access"

        # Testing domain
        elif any(term in query_lower for term in ['test', 'spec', 'unit', 'integration']):
            return f"{query} testing validation verification quality"

        return None

    def _create_simplified_query(self, query_terms: List[str]) -> str:
        """Create simplified query with only key terms."""
        # Remove common words and keep meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_terms = [term for term in query_terms if term not in stop_words and len(term) > 2]

        if len(meaningful_terms) >= 2:
            return ' '.join(meaningful_terms[:4])  # Top 4 meaningful terms

        return None

    def _create_context_aware_variation(self, query: str, intent: str) -> str:
        """Create context-aware variation based on intent."""
        if intent == 'technical':
            return f"{query} implementation development code"
        elif intent == 'documentation':
            return f"{query} documentation guide reference"
        elif intent == 'task_management':
            return f"{query} task management planning"
        else:
            return f"{query} project development"

    def search(self, query: str, max_results: int = 10,
               file_types: Optional[List[str]] = None) -> SearchResult:
        """
        Perform semantic search for relevant context chunks.

        Args:
            query: Search query
            max_results: Maximum number of results to return
            file_types: Optional list of file types to filter by

        Returns:
            SearchResult with ranked context chunks
        """
        start_time = time.time()

        # Check cache first
        cached_chunks, cached_vectors = self._get_cached_data()

        if cached_chunks is None or cached_vectors is None:
            # Load and process chunks
            chunks = self._load_chunks_from_embeddings()

            if not chunks:
                return SearchResult(
                    query=query,
                    chunks=[],
                    total_chunks=0,
                    search_time=time.time() - start_time,
                    similarity_threshold=self.similarity_threshold
                )

            # Create TF-IDF vectors
            chunk_texts = [chunk.text for chunk in chunks]
            vectors = self.vectorizer.fit_transform(chunk_texts)

            # Update cache
            self._update_cache(chunks, vectors)
        else:
            chunks, vectors = cached_chunks, cached_vectors

        # Filter by file types if specified
        if file_types:
            filtered_indices = []
            filtered_chunks = []
            for i, chunk in enumerate(chunks):
                if chunk.file_type in file_types:
                    filtered_indices.append(i)
                    filtered_chunks.append(chunk)

            if filtered_indices:
                vectors = vectors[filtered_indices]
                chunks = filtered_chunks

        # Preprocess query
        processed_query = self._preprocess_query(query)

        # Transform query to vector space
        query_vector = self.vectorizer.transform([processed_query])

        # Calculate similarities
        similarities = cosine_similarity(query_vector, vectors).flatten()

        # PHASE 4 FIX: Apply exact match boosts before filtering to ensure exact matches aren't lost
        query_lower = query.lower()
        query_intent = self._classify_query_intent(query_lower)

        # Calculate exact match boosts for all chunks first
        exact_match_boosts = []
        for chunk in chunks:
            boost = self._calculate_exact_match_boost(chunk, query_lower, query_intent)
            exact_match_boosts.append(boost)

        # Apply exact match boosts to similarities for filtering decision
        boosted_similarities = similarities + np.array(exact_match_boosts)

        # Filter by similarity threshold (now considering exact match boosts)
        valid_indices = boosted_similarities >= self.similarity_threshold
        valid_chunks = [chunks[i] for i in range(len(chunks)) if valid_indices[i]]
        valid_similarities = similarities[valid_indices]

        # Calculate enhanced relevance scores (exact match boost will be applied again, but that's fine)
        valid_chunks = self._calculate_relevance_scores(valid_chunks, valid_similarities, query)

        # Sort by relevance score (descending)
        valid_chunks.sort(key=lambda x: x.relevance_score, reverse=True)

        # Apply diversity-aware selection for balanced context
        result_chunks = self._select_diverse_chunks(valid_chunks, max_results, query)

        search_time = time.time() - start_time

        logger.info(f"Search completed: '{query}' -> {len(result_chunks)} results in {search_time:.3f}s")

        return SearchResult(
            query=query,
            chunks=result_chunks,
            total_chunks=len(valid_chunks),
            search_time=search_time,
            similarity_threshold=self.similarity_threshold
        )

    def get_context_summary(self, chunks: List[ContextChunk]) -> Dict[str, Any]:
        """
        Generate a summary of the context chunks.

        Args:
            chunks: List of context chunks

        Returns:
            Dictionary with context summary information
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'file_types': {},
                'chunk_types': {},
                'average_relevance': 0.0,
                'files_covered': []
            }

        file_types = {}
        chunk_types = {}
        files_covered = set()
        total_relevance = 0.0

        for chunk in chunks:
            # Count file types
            file_types[chunk.file_type] = file_types.get(chunk.file_type, 0) + 1

            # Count chunk types
            chunk_types[chunk.chunk_type] = chunk_types.get(chunk.chunk_type, 0) + 1

            # Track files
            files_covered.add(chunk.file_name)

            # Sum relevance
            total_relevance += chunk.relevance_score

        return {
            'total_chunks': len(chunks),
            'file_types': file_types,
            'chunk_types': chunk_types,
            'average_relevance': total_relevance / len(chunks) if chunks else 0.0,
            'files_covered': sorted(list(files_covered))
        }

    def clear_cache(self):
        """Clear the internal cache."""
        self._chunks_cache = None
        self._vectors_cache = None
        self._last_cache_time = 0
        logger.info("Cache cleared")