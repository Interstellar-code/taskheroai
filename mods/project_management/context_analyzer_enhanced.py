#!/usr/bin/env python3
"""
Enhanced Context Analyzer for AI Task Creation

This module provides enhanced context analysis that properly separates:
1. User's primary input (description, requirements)
2. Contextual information from codebase (for reference only)
3. Specific code analysis and recommendations

TASK-044 Enhancement: Better separation of user input vs context
"""

import os
import re
import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
from .path_resolver import get_project_paths

logger = logging.getLogger("TaskHeroAI.ProjectManagement.EnhancedContextAnalyzer")


@dataclass
class CodeAnalysis:
    """Detailed analysis of a specific code file."""
    file_path: str
    file_type: str
    language: str
    functions: List[str]
    classes: List[str]
    imports: List[str]
    key_features: List[str]
    complexity_score: float
    lines_of_code: int
    documentation_quality: str
    specific_patterns: List[str]
    configuration_items: List[str]  # For config files
    dependencies: List[str]
    api_endpoints: List[str]  # For API files
    database_models: List[str]  # For model files


@dataclass
class ContextualRecommendation:
    """Contextual recommendation based on code analysis."""
    category: str  # 'implementation', 'testing', 'integration', 'configuration'
    priority: str  # 'high', 'medium', 'low'
    description: str
    rationale: str
    related_files: List[str]
    code_examples: List[str]


@dataclass
class EnhancedProjectContext:
    """Enhanced project context with better separation."""
    # User's primary input (should remain unchanged)
    user_description: str
    user_requirements: List[str]

    # Contextual analysis (for AI enhancement only)
    relevant_files: List[CodeAnalysis]
    contextual_recommendations: List[ContextualRecommendation]
    implementation_patterns: Dict[str, List[str]]
    technology_stack: Dict[str, str]
    architectural_insights: List[str]
    integration_points: List[str]

    # Specific analysis for the task
    primary_file_analysis: Optional[CodeAnalysis]  # Main file being worked on
    related_file_analyses: List[CodeAnalysis]  # Supporting files

    # Quality metrics
    context_confidence: float
    analysis_completeness: float


class EnhancedContextAnalyzer:
    """Enhanced context analyzer with better separation of concerns."""

    def __init__(self, project_root: str):
        """Initialize the enhanced context analyzer."""
        # Use the centralized path resolver
        self.project_paths = get_project_paths(project_root)
        self.project_root = self.project_paths.project_root
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.bat': 'batch',
            '.sh': 'shell',
            '.md': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.txt': 'text',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css'
        }

        # Patterns for different types of analysis
        self.code_patterns = {
            'api_endpoints': [
                r'@app\.route\([\'"]([^\'"]+)[\'"]',
                r'router\.[get|post|put|delete]+\([\'"]([^\'"]+)[\'"]',
                r'app\.[get|post|put|delete]+\([\'"]([^\'"]+)[\'"]'
            ],
            'database_models': [
                r'class\s+(\w+)\s*\([^)]*Model[^)]*\)',
                r'CREATE\s+TABLE\s+(\w+)',
                r'@dataclass\s*\nclass\s+(\w+)'
            ],
            'configuration': [
                r'([A-Z_]+)\s*=\s*[\'"]?([^\'"]+)[\'"]?',
                r'config\[[\'"]([\w_]+)[\'"]\]',
                r'os\.environ\.get\([\'"]([^\'"]+)[\'"]'
            ],
            'functions': [
                r'def\s+(\w+)\s*\(',
                r'function\s+(\w+)\s*\(',
                r'const\s+(\w+)\s*=\s*\('
            ],
            'classes': [
                r'class\s+(\w+)\s*[:\(]',
                r'class\s+(\w+)\s*{'
            ]
        }

    def analyze_task_context_enhanced(self,
                                    user_description: str,
                                    task_type: str,
                                    specific_files: List[str] = None) -> EnhancedProjectContext:
        """
        Enhanced context analysis with proper separation of user input and context.

        Args:
            user_description: User's original description (kept unchanged)
            task_type: Type of task being created
            specific_files: Specific files to analyze (if known)

        Returns:
            Enhanced project context with separated concerns
        """
        try:
            logger.info(f"Starting enhanced context analysis for task type: {task_type}")

            # Step 1: Preserve user's original input
            user_requirements = self._extract_user_requirements(user_description)

            # Step 2: Identify relevant files for analysis
            if specific_files:
                target_files = [self.project_root / f for f in specific_files if (self.project_root / f).exists()]
            else:
                target_files = self._identify_relevant_files(user_description, task_type)

            # Step 3: Perform detailed code analysis
            relevant_analyses = []
            primary_analysis = None

            for file_path in target_files[:10]:  # Limit to top 10 files
                analysis = self._analyze_code_file(file_path)
                if analysis:
                    relevant_analyses.append(analysis)

                    # Identify primary file (most relevant to user description)
                    if self._is_primary_file(file_path, user_description, task_type):
                        primary_analysis = analysis

            # Step 4: Generate contextual recommendations
            recommendations = self._generate_contextual_recommendations(
                relevant_analyses, user_description, task_type
            )

            # Step 5: Extract implementation patterns
            patterns = self._extract_implementation_patterns(relevant_analyses)

            # Step 6: Analyze technology stack
            tech_stack = self._analyze_technology_stack(relevant_analyses)

            # Step 7: Generate architectural insights
            architectural_insights = self._generate_architectural_insights(relevant_analyses, task_type)

            # Step 8: Identify integration points
            integration_points = self._identify_integration_points(relevant_analyses, user_description)

            # Step 9: Calculate quality metrics
            context_confidence = self._calculate_context_confidence(relevant_analyses, user_description)
            analysis_completeness = self._calculate_analysis_completeness(relevant_analyses)

            return EnhancedProjectContext(
                user_description=user_description,
                user_requirements=user_requirements,
                relevant_files=relevant_analyses,
                contextual_recommendations=recommendations,
                implementation_patterns=patterns,
                technology_stack=tech_stack,
                architectural_insights=architectural_insights,
                integration_points=integration_points,
                primary_file_analysis=primary_analysis,
                related_file_analyses=[a for a in relevant_analyses if a != primary_analysis],
                context_confidence=context_confidence,
                analysis_completeness=analysis_completeness
            )

        except Exception as e:
            logger.error(f"Enhanced context analysis failed: {e}")
            # Return minimal context with user input preserved
            return EnhancedProjectContext(
                user_description=user_description,
                user_requirements=self._extract_user_requirements(user_description),
                relevant_files=[],
                contextual_recommendations=[],
                implementation_patterns={},
                technology_stack={},
                architectural_insights=[],
                integration_points=[],
                primary_file_analysis=None,
                related_file_analyses=[],
                context_confidence=0.0,
                analysis_completeness=0.0
            )

    def _extract_user_requirements(self, description: str) -> List[str]:
        """Extract explicit requirements from user description."""
        requirements = []

        # Look for explicit requirement patterns
        requirement_patterns = [
            r'(?:should|must|need to|required to|has to)\s+([^.!?]+)',
            r'(?:requirement|spec|specification):\s*([^.!?]+)',
            r'(?:implement|create|build|develop)\s+([^.!?]+)',
            r'(?:feature|functionality):\s*([^.!?]+)'
        ]

        for pattern in requirement_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                clean_req = match.strip()
                if len(clean_req) > 10:  # Filter out very short matches
                    requirements.append(clean_req)

        return requirements[:5]  # Limit to top 5 explicit requirements

    def _identify_relevant_files(self, description: str, task_type: str) -> List[Path]:
        """Identify files relevant to the task based on description and type."""
        relevant_files = []

        # Extract keywords from description
        keywords = self._extract_keywords(description)

        # Search for files in the project
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and self._is_code_file(file_path):
                relevance_score = self._calculate_file_relevance(file_path, keywords, task_type)
                if relevance_score > 0.3:  # Threshold for relevance
                    relevant_files.append((file_path, relevance_score))

        # Sort by relevance and return top files
        relevant_files.sort(key=lambda x: x[1], reverse=True)
        return [f[0] for f in relevant_files[:15]]

    def _analyze_code_file(self, file_path: Path) -> Optional[CodeAnalysis]:
        """Perform detailed analysis of a code file."""
        try:
            if not file_path.exists() or file_path.stat().st_size > 1024 * 1024:  # Skip files > 1MB
                return None

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            file_type = self._determine_file_type(file_path)
            language = self.supported_languages.get(file_path.suffix.lower(), 'unknown')

            # Extract code elements based on language
            functions = self._extract_functions(content, language)
            classes = self._extract_classes(content, language)
            imports = self._extract_imports(content, language)

            # Analyze specific features based on file type
            key_features = self._extract_key_features(content, file_path, language)
            configuration_items = self._extract_configuration_items(content, language)
            dependencies = self._extract_dependencies(content, language)
            api_endpoints = self._extract_api_endpoints(content, language)
            database_models = self._extract_database_models(content, language)

            # Calculate metrics
            complexity_score = self._calculate_complexity(content, language)
            lines_of_code = len([line for line in content.split('\n') if line.strip()])
            documentation_quality = self._assess_documentation_quality(content, language)
            specific_patterns = self._identify_specific_patterns(content, file_path)

            return CodeAnalysis(
                file_path=str(file_path.relative_to(self.project_root)),
                file_type=file_type,
                language=language,
                functions=functions,
                classes=classes,
                imports=imports,
                key_features=key_features,
                complexity_score=complexity_score,
                lines_of_code=lines_of_code,
                documentation_quality=documentation_quality,
                specific_patterns=specific_patterns,
                configuration_items=configuration_items,
                dependencies=dependencies,
                api_endpoints=api_endpoints,
                database_models=database_models
            )

        except Exception as e:
            logger.warning(f"Failed to analyze file {file_path}: {e}")
            return None

    def _extract_key_features(self, content: str, file_path: Path, language: str) -> List[str]:
        """Extract key features specific to the file type and content."""
        features = []

        if file_path.name.endswith('.bat'):
            # Batch file specific features
            if 'echo off' in content:
                features.append('Silent execution mode')
            if 'setlocal enabledelayedexpansion' in content:
                features.append('Advanced variable handling')
            if 'call :' in content:
                features.append('Function-based architecture')
            if 'python -m venv' in content:
                features.append('Virtual environment management')
            if 'pip install' in content:
                features.append('Package installation')
            if 'where ' in content:
                features.append('Dependency checking')
            if '.env' in content:
                features.append('Environment configuration')
            if 'errorlevel' in content:
                features.append('Error handling')
            if 'set /p' in content:
                features.append('User interaction')
            if '.done' in content:
                features.append('Setup tracking system')

        elif language == 'python':
            # Python specific features
            if 'async def' in content:
                features.append('Asynchronous programming')
            if 'class ' in content and '(Exception)' in content:
                features.append('Custom exception handling')
            if '@dataclass' in content:
                features.append('Data classes')
            if 'logging' in content:
                features.append('Logging system')
            if 'pathlib' in content:
                features.append('Modern path handling')
            if 'typing' in content:
                features.append('Type annotations')

        elif language == 'javascript':
            # JavaScript specific features
            if 'async ' in content or 'await ' in content:
                features.append('Asynchronous programming')
            if 'export ' in content or 'import ' in content:
                features.append('ES6 modules')
            if 'React' in content:
                features.append('React framework')

        return features

    def _extract_configuration_items(self, content: str, language: str) -> List[str]:
        """Extract configuration items from the file."""
        config_items = []

        # Look for configuration patterns
        for pattern in self.code_patterns['configuration']:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    config_items.append(f"{match[0]}={match[1]}")
                else:
                    config_items.append(match)

        return config_items[:20]  # Limit to top 20 config items

    def _generate_contextual_recommendations(self,
                                           analyses: List[CodeAnalysis],
                                           user_description: str,
                                           task_type: str) -> List[ContextualRecommendation]:
        """Generate contextual recommendations based on code analysis."""
        recommendations = []

        # Analyze patterns across files
        all_patterns = []
        all_features = []
        for analysis in analyses:
            all_patterns.extend(analysis.specific_patterns)
            all_features.extend(analysis.key_features)

        # Generate implementation recommendations
        if task_type.lower() == 'development':
            if 'Error handling' in all_features:
                recommendations.append(ContextualRecommendation(
                    category='implementation',
                    priority='high',
                    description='Implement comprehensive error handling following existing patterns',
                    rationale='Existing codebase shows consistent error handling patterns',
                    related_files=[a.file_path for a in analyses if 'Error handling' in a.key_features],
                    code_examples=[]
                ))

            if 'Setup tracking system' in all_features:
                recommendations.append(ContextualRecommendation(
                    category='implementation',
                    priority='medium',
                    description='Consider implementing progress tracking for multi-step operations',
                    rationale='Existing setup scripts use .done file tracking system',
                    related_files=[a.file_path for a in analyses if 'Setup tracking system' in a.key_features],
                    code_examples=[]
                ))

        # Generate testing recommendations
        test_files = [a for a in analyses if 'test' in a.file_path.lower()]
        if test_files:
            recommendations.append(ContextualRecommendation(
                category='testing',
                priority='high',
                description='Follow existing test patterns and structure',
                rationale=f'Found {len(test_files)} test files with established patterns',
                related_files=[a.file_path for a in test_files],
                code_examples=[]
            ))

        return recommendations

    def _is_primary_file(self, file_path: Path, description: str, task_type: str) -> bool:
        """Determine if this is the primary file being worked on."""
        file_name = file_path.name.lower()
        description_lower = description.lower()

        # Check if file is explicitly mentioned in description
        if file_name in description_lower:
            return True

        # Check for task type specific primary files
        if task_type.lower() == 'development':
            if 'setup' in description_lower and 'setup' in file_name:
                return True
            if 'install' in description_lower and any(word in file_name for word in ['setup', 'install']):
                return True

        return False

    def _calculate_context_confidence(self, analyses: List[CodeAnalysis], description: str) -> float:
        """Calculate confidence in the context analysis."""
        if not analyses:
            return 0.0

        confidence_factors = []

        # Factor 1: Number of relevant files found
        file_count_score = min(len(analyses) / 10.0, 1.0)
        confidence_factors.append(file_count_score)

        # Factor 2: Quality of analysis (based on extracted features)
        feature_score = sum(len(a.key_features) for a in analyses) / (len(analyses) * 10.0)
        confidence_factors.append(min(feature_score, 1.0))

        # Factor 3: Relevance to description
        description_words = set(description.lower().split())
        relevance_scores = []
        for analysis in analyses:
            file_words = set(analysis.file_path.lower().split('/'))
            feature_words = set(' '.join(analysis.key_features).lower().split())
            overlap = len(description_words & (file_words | feature_words))
            relevance_scores.append(overlap / max(len(description_words), 1))

        relevance_score = sum(relevance_scores) / max(len(relevance_scores), 1)
        confidence_factors.append(min(relevance_score, 1.0))

        return sum(confidence_factors) / len(confidence_factors)

    def _calculate_analysis_completeness(self, analyses: List[CodeAnalysis]) -> float:
        """Calculate completeness of the analysis."""
        if not analyses:
            return 0.0

        completeness_factors = []

        for analysis in analyses:
            factors = []

            # Check if we extracted functions
            factors.append(1.0 if analysis.functions else 0.0)

            # Check if we extracted key features
            factors.append(min(len(analysis.key_features) / 5.0, 1.0))

            # Check if we have configuration items (for config files)
            if analysis.language in ['json', 'yaml', 'batch']:
                factors.append(1.0 if analysis.configuration_items else 0.0)

            # Check documentation quality
            factors.append(0.5 if analysis.documentation_quality == 'good' else 0.0)

            completeness_factors.append(sum(factors) / len(factors))

        return sum(completeness_factors) / len(completeness_factors)

    # Additional helper methods (simplified for brevity)
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) > 3][:20]

    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file."""
        return file_path.suffix.lower() in self.supported_languages

    def _calculate_file_relevance(self, file_path: Path, keywords: List[str], task_type: str) -> float:
        """Calculate relevance score for a file."""
        score = 0.0
        file_name = file_path.name.lower()

        # Keyword matching
        for keyword in keywords:
            if keyword in file_name:
                score += 0.2

        # Task type specific scoring
        if task_type.lower() == 'development':
            if any(word in file_name for word in ['setup', 'install', 'config']):
                score += 0.3

        return min(score, 1.0)

    def _determine_file_type(self, file_path: Path) -> str:
        """Determine the type/purpose of the file."""
        name = file_path.name.lower()

        if 'test' in name:
            return 'test'
        elif 'setup' in name or 'install' in name:
            return 'setup'
        elif 'config' in name or name.endswith('.json') or name.endswith('.yaml'):
            return 'configuration'
        elif name.endswith('.md'):
            return 'documentation'
        else:
            return 'source'

    # Simplified extraction methods (would be more comprehensive in full implementation)
    def _extract_functions(self, content: str, language: str) -> List[str]:
        """Extract function names from content."""
        functions = []
        if language == 'python':
            matches = re.findall(r'def\s+(\w+)\s*\(', content)
            functions.extend(matches)
        elif language == 'batch':
            matches = re.findall(r'^:(\w+)', content, re.MULTILINE)
            functions.extend(matches)
        return functions[:20]

    def _extract_classes(self, content: str, language: str) -> List[str]:
        """Extract class names from content."""
        if language == 'python':
            return re.findall(r'class\s+(\w+)\s*[:\(]', content)[:10]
        return []

    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements."""
        if language == 'python':
            imports = re.findall(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', content)
            return [i[0] or i[1] for i in imports][:15]
        return []

    def _extract_dependencies(self, content: str, language: str) -> List[str]:
        """Extract dependencies from content."""
        deps = []
        if 'requirements.txt' in content or 'pip install' in content:
            deps.extend(re.findall(r'pip install\s+([^\s]+)', content))
        return deps[:10]

    def _extract_api_endpoints(self, content: str, language: str) -> List[str]:
        """Extract API endpoints."""
        endpoints = []
        for pattern in self.code_patterns['api_endpoints']:
            endpoints.extend(re.findall(pattern, content))
        return endpoints[:10]

    def _extract_database_models(self, content: str, language: str) -> List[str]:
        """Extract database model names."""
        models = []
        for pattern in self.code_patterns['database_models']:
            models.extend(re.findall(pattern, content))
        return models[:10]

    def _calculate_complexity(self, content: str, language: str) -> float:
        """Calculate code complexity score."""
        lines = content.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]

        # Simple complexity based on control structures
        complexity_keywords = ['if', 'for', 'while', 'try', 'except', 'elif', 'else']
        complexity_count = sum(1 for line in non_empty_lines
                             for keyword in complexity_keywords
                             if keyword in line.lower())

        return min(complexity_count / max(len(non_empty_lines), 1), 1.0)

    def _assess_documentation_quality(self, content: str, language: str) -> str:
        """Assess documentation quality."""
        lines = content.split('\n')
        comment_lines = 0

        if language == 'python':
            comment_lines = sum(1 for line in lines if line.strip().startswith('#') or '"""' in line)
        elif language == 'batch':
            comment_lines = sum(1 for line in lines if line.strip().startswith('::') or line.strip().startswith('REM'))

        ratio = comment_lines / max(len(lines), 1)

        if ratio > 0.2:
            return 'good'
        elif ratio > 0.1:
            return 'fair'
        else:
            return 'poor'

    def _identify_specific_patterns(self, content: str, file_path: Path) -> List[str]:
        """Identify specific patterns in the code."""
        patterns = []

        if file_path.name.endswith('.bat'):
            if 'errorlevel' in content:
                patterns.append('Error level checking')
            if 'setlocal' in content:
                patterns.append('Local variable scoping')
            if 'call :' in content:
                patterns.append('Function calls')
            if '.done' in content:
                patterns.append('Completion tracking')

        return patterns

    def _extract_implementation_patterns(self, analyses: List[CodeAnalysis]) -> Dict[str, List[str]]:
        """Extract implementation patterns from analyses."""
        patterns = {
            'error_handling': [],
            'configuration': [],
            'testing': [],
            'logging': []
        }

        for analysis in analyses:
            if 'Error handling' in analysis.key_features:
                patterns['error_handling'].append(analysis.file_path)
            if analysis.configuration_items:
                patterns['configuration'].append(analysis.file_path)
            if 'test' in analysis.file_path.lower():
                patterns['testing'].append(analysis.file_path)
            if 'Logging system' in analysis.key_features:
                patterns['logging'].append(analysis.file_path)

        return patterns

    def _analyze_technology_stack(self, analyses: List[CodeAnalysis]) -> Dict[str, str]:
        """Analyze the technology stack from the analyses."""
        stack = {}

        languages = [a.language for a in analyses]
        if 'python' in languages:
            stack['backend'] = 'Python'
        if 'javascript' in languages:
            stack['frontend'] = 'JavaScript'
        if 'batch' in languages:
            stack['deployment'] = 'Windows Batch Scripts'

        return stack

    def _generate_architectural_insights(self, analyses: List[CodeAnalysis], task_type: str) -> List[str]:
        """Generate architectural insights."""
        insights = []

        # Analyze file organization
        file_types = [a.file_type for a in analyses]
        if 'setup' in file_types:
            insights.append("Project uses automated setup scripts for deployment")

        if 'configuration' in file_types:
            insights.append("Configuration is externalized using config files")

        # Analyze complexity
        avg_complexity = sum(a.complexity_score for a in analyses) / max(len(analyses), 1)
        if avg_complexity > 0.5:
            insights.append("Codebase has moderate to high complexity")

        return insights

    def _identify_integration_points(self, analyses: List[CodeAnalysis], description: str) -> List[str]:
        """Identify integration points."""
        integration_points = []

        for analysis in analyses:
            if analysis.api_endpoints:
                integration_points.append(f"API endpoints in {analysis.file_path}")
            if analysis.configuration_items:
                integration_points.append(f"Configuration integration in {analysis.file_path}")

        return integration_points