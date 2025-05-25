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
        self.project_root = Path(project_root)
        self.embeddings_dir = self.project_root / ".index" / "embeddings"
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
    
    def _load_chunks_from_embeddings(self) -> List[ContextChunk]:
        """
        Load and process chunks from existing embedding files.
        
        Returns:
            List of ContextChunk objects
        """
        chunks = []
        
        if not self.embeddings_dir.exists():
            logger.warning(f"Embeddings directory not found: {self.embeddings_dir}")
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
        Determine file type based on filename and extension.
        
        Args:
            file_name: Name of the file
            
        Returns:
            File type category
        """
        file_name_lower = file_name.lower()
        
        if file_name_lower.endswith('.py'):
            return 'python'
        elif file_name_lower.endswith('.md'):
            if 'task' in file_name_lower:
                return 'task'
            elif 'template' in file_name_lower:
                return 'template'
            elif 'doc' in file_name_lower or 'readme' in file_name_lower:
                return 'documentation'
            else:
                return 'markdown'
        elif file_name_lower.endswith('.json'):
            return 'config'
        elif file_name_lower.endswith(('.js', '.ts', '.jsx', '.tsx')):
            return 'javascript'
        elif file_name_lower.endswith(('.html', '.htm')):
            return 'html'
        elif file_name_lower.endswith(('.css', '.scss', '.sass')):
            return 'stylesheet'
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
        Preprocess and expand the search query.
        
        Args:
            query: Original search query
            
        Returns:
            Preprocessed and expanded query
        """
        # Clean the query
        query = re.sub(r'[^\w\s-]', ' ', query.lower())
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Expand query with related terms
        expansions = {
            'task': ['task', 'todo', 'work', 'assignment', 'issue'],
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt'],
            'template': ['template', 'format', 'structure', 'layout', 'pattern'],
            'create': ['create', 'generate', 'build', 'make', 'develop'],
            'manage': ['manage', 'handle', 'control', 'organize', 'coordinate'],
            'user': ['user', 'person', 'individual', 'client', 'customer'],
            'system': ['system', 'application', 'platform', 'software', 'program'],
            'interface': ['interface', 'ui', 'frontend', 'gui', 'display'],
            'api': ['api', 'endpoint', 'service', 'rest', 'http'],
            'database': ['database', 'db', 'storage', 'data', 'persistence'],
            'test': ['test', 'testing', 'spec', 'validation', 'verification'],
            'bug': ['bug', 'error', 'issue', 'problem', 'defect'],
            'feature': ['feature', 'functionality', 'capability', 'enhancement'],
            'documentation': ['documentation', 'docs', 'guide', 'manual', 'readme']
        }
        
        # Add related terms to query
        query_terms = query.split()
        expanded_terms = set(query_terms)
        
        for term in query_terms:
            if term in expansions:
                expanded_terms.update(expansions[term][:2])  # Add top 2 related terms
        
        return ' '.join(expanded_terms)
    
    def _calculate_relevance_scores(self, chunks: List[ContextChunk], 
                                  similarities: np.ndarray, 
                                  query: str) -> List[ContextChunk]:
        """
        Calculate enhanced relevance scores for chunks.
        
        Args:
            chunks: List of context chunks
            similarities: Cosine similarity scores
            query: Original search query
            
        Returns:
            List of chunks with updated relevance scores
        """
        query_lower = query.lower()
        
        for i, chunk in enumerate(chunks):
            base_score = similarities[i]
            
            # Boost score based on various factors
            boost_factors = 1.0
            
            # File type relevance
            if 'task' in query_lower and chunk.file_type == 'task':
                boost_factors *= 1.5
            elif 'template' in query_lower and chunk.file_type == 'template':
                boost_factors *= 1.5
            elif 'python' in query_lower and chunk.file_type == 'python':
                boost_factors *= 1.3
            
            # Chunk type relevance
            if chunk.chunk_type == 'function_definition':
                boost_factors *= 1.2
            elif chunk.chunk_type == 'class_definition':
                boost_factors *= 1.1
            
            # Confidence boost
            boost_factors *= chunk.confidence
            
            # Freshness boost (more recent files get slight boost)
            if chunk.last_modified:
                days_old = (time.time() - chunk.last_modified) / (24 * 3600)
                if days_old < 7:  # Files modified in last week
                    boost_factors *= 1.1
                elif days_old < 30:  # Files modified in last month
                    boost_factors *= 1.05
            
            # Text length normalization (prefer substantial chunks)
            text_length = len(chunk.text)
            if 100 <= text_length <= 1000:  # Sweet spot for chunk size
                boost_factors *= 1.1
            elif text_length < 50:  # Too short
                boost_factors *= 0.8
            
            # Apply boosts and update score
            chunk.relevance_score = base_score * boost_factors
        
        return chunks
    
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
        
        # Filter by similarity threshold
        valid_indices = similarities >= self.similarity_threshold
        valid_chunks = [chunks[i] for i in range(len(chunks)) if valid_indices[i]]
        valid_similarities = similarities[valid_indices]
        
        # Calculate enhanced relevance scores
        valid_chunks = self._calculate_relevance_scores(valid_chunks, valid_similarities, query)
        
        # Sort by relevance score (descending)
        valid_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit results
        result_chunks = valid_chunks[:max_results]
        
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