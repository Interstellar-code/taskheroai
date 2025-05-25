"""
Context Analyzer Module for Enhanced AI Task Creation

This module provides context-aware analysis capabilities to improve AI task creation
by analyzing actual codebase files, detecting dependencies, and providing specific
implementation details for better task generation.

Part of TASK-044: Improve AI Task Creation System - Post Phase 4 Analysis
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
import re
import ast
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("TaskHeroAI.ProjectManagement.ContextAnalyzer")


@dataclass
class FileAnalysis:
    """Analysis result for a single file."""
    file_path: str
    file_type: str
    functions: List[str]
    classes: List[str]
    imports: List[str]
    dependencies: List[str]
    complexity_score: float
    last_modified: datetime
    content_preview: str
    key_patterns: List[str]


@dataclass
class ProjectContext:
    """Comprehensive project context for task creation."""
    relevant_files: List[FileAnalysis]
    project_structure: Dict[str, Any]
    dependencies: Dict[str, List[str]]
    patterns: Dict[str, List[str]]
    recommendations: List[str]


class ContextAnalyzer:
    """Enhanced context analyzer for AI task creation improvements."""
    
    def __init__(self, project_root: str):
        """Initialize the context analyzer.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.file_patterns = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.env'],
            'batch': ['.bat', '.cmd', '.sh'],
            'markdown': ['.md', '.rst'],
            'requirements': ['requirements.txt', 'package.json', 'pyproject.toml']
        }
        
        # Cache for analyzed files to improve performance
        self._analysis_cache: Dict[str, FileAnalysis] = {}
        
    def analyze_task_context(self, task_description: str, task_type: str) -> ProjectContext:
        """Analyze project context relevant to a specific task.
        
        Args:
            task_description: Description of the task
            task_type: Type of task (DEV, BUG, TEST, etc.)
            
        Returns:
            ProjectContext with relevant analysis
        """
        try:
            # Extract keywords from task description
            keywords = self._extract_keywords(task_description, task_type)
            
            # Find relevant files based on keywords and task type
            relevant_files = self._find_relevant_files(keywords, task_type)
            
            # Analyze file dependencies
            dependencies = self._analyze_dependencies(relevant_files)
            
            # Extract patterns and recommendations
            patterns = self._extract_patterns(relevant_files, task_type)
            recommendations = self._generate_recommendations(relevant_files, task_description, task_type)
            
            # Build project structure map
            project_structure = self._build_project_structure(relevant_files)
            
            return ProjectContext(
                relevant_files=relevant_files,
                project_structure=project_structure,
                dependencies=dependencies,
                patterns=patterns,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing task context: {e}")
            return ProjectContext([], {}, {}, {}, [])
    
    def _extract_keywords(self, description: str, task_type: str) -> List[str]:
        """Extract relevant keywords from task description."""
        keywords = []
        
        # Basic keyword extraction
        words = re.findall(r'\b\w+\b', description.lower())
        
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add task-type specific keywords
        type_keywords = {
            'DEV': ['implement', 'create', 'build', 'develop', 'add', 'feature'],
            'BUG': ['fix', 'bug', 'error', 'issue', 'problem', 'debug'],
            'TEST': ['test', 'testing', 'validate', 'verify', 'check'],
            'DOC': ['document', 'documentation', 'readme', 'guide'],
            'DES': ['design', 'ui', 'ux', 'interface', 'layout']
        }
        
        if task_type in type_keywords:
            keywords.extend(type_keywords[task_type])
        
        return list(set(keywords))
    
    def _find_relevant_files(self, keywords: List[str], task_type: str) -> List[FileAnalysis]:
        """Find files relevant to the task based on keywords and type."""
        relevant_files = []
        
        # Scan project files
        for file_path in self._scan_project_files():
            try:
                # Check if file is relevant
                if self._is_file_relevant(file_path, keywords, task_type):
                    analysis = self._analyze_file(file_path)
                    if analysis:
                        relevant_files.append(analysis)
                        
            except Exception as e:
                logger.warning(f"Error analyzing file {file_path}: {e}")
                continue
        
        # Sort by relevance score
        relevant_files.sort(key=lambda f: f.complexity_score, reverse=True)
        
        # Limit to top 20 most relevant files
        return relevant_files[:20]
    
    def _scan_project_files(self) -> List[Path]:
        """Scan project directory for relevant files."""
        files = []
        
        # Directories to skip
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.index', 'logs'}
        
        for root, dirs, filenames in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Check if file type is relevant
                if self._is_relevant_file_type(filename):
                    files.append(file_path)
        
        return files
    
    def _is_relevant_file_type(self, filename: str) -> bool:
        """Check if file type is relevant for analysis."""
        for file_type, extensions in self.file_patterns.items():
            for ext in extensions:
                if filename.endswith(ext) or filename == ext.lstrip('.'):
                    return True
        return False
    
    def _is_file_relevant(self, file_path: Path, keywords: List[str], task_type: str) -> bool:
        """Check if a file is relevant to the task."""
        try:
            # Check filename for keywords
            filename_lower = file_path.name.lower()
            for keyword in keywords:
                if keyword in filename_lower:
                    return True
            
            # For install script tasks, prioritize setup files
            if any(word in keywords for word in ['install', 'setup', 'script']):
                if any(pattern in filename_lower for pattern in ['setup', 'install', '.bat', '.sh', '.env', 'requirements']):
                    return True
            
            # Check file content for keywords (for small files)
            if file_path.stat().st_size < 100000:  # Less than 100KB
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    content_lower = content.lower()
                    
                    keyword_count = sum(1 for keyword in keywords if keyword in content_lower)
                    if keyword_count >= 2:  # At least 2 keywords found
                        return True
                        
                except Exception:
                    pass
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking file relevance for {file_path}: {e}")
            return False
    
    def _analyze_file(self, file_path: Path) -> Optional[FileAnalysis]:
        """Analyze a single file for context information."""
        try:
            # Check cache first
            cache_key = str(file_path)
            if cache_key in self._analysis_cache:
                cached = self._analysis_cache[cache_key]
                # Check if file was modified since cache
                if cached.last_modified >= datetime.fromtimestamp(file_path.stat().st_mtime):
                    return cached
            
            # Read file content
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                return None
            
            # Determine file type
            file_type = self._determine_file_type(file_path.name)
            
            # Extract information based on file type
            functions = []
            classes = []
            imports = []
            dependencies = []
            key_patterns = []
            
            if file_type == 'python':
                functions, classes, imports = self._analyze_python_file(content)
                dependencies = self._extract_python_dependencies(imports)
                key_patterns = self._extract_python_patterns(content)
                
            elif file_type == 'batch':
                key_patterns = self._extract_batch_patterns(content)
                dependencies = self._extract_batch_dependencies(content)
                
            elif file_type == 'config':
                dependencies = self._extract_config_dependencies(content, file_path.name)
                key_patterns = self._extract_config_patterns(content)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(content, functions, classes)
            
            # Create content preview
            content_preview = self._create_content_preview(content, file_type)
            
            # Create analysis result
            analysis = FileAnalysis(
                file_path=str(file_path.relative_to(self.project_root)),
                file_type=file_type,
                functions=functions,
                classes=classes,
                imports=imports,
                dependencies=dependencies,
                complexity_score=complexity_score,
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                content_preview=content_preview,
                key_patterns=key_patterns
            )
            
            # Cache the result
            self._analysis_cache[cache_key] = analysis
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Error analyzing file {file_path}: {e}")
            return None
    
    def _determine_file_type(self, filename: str) -> str:
        """Determine the type of file based on extension."""
        for file_type, extensions in self.file_patterns.items():
            for ext in extensions:
                if filename.endswith(ext) or filename == ext.lstrip('.'):
                    return file_type
        return 'unknown'
    
    def _analyze_python_file(self, content: str) -> Tuple[List[str], List[str], List[str]]:
        """Analyze Python file for functions, classes, and imports."""
        functions = []
        classes = []
        imports = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
        except SyntaxError:
            # Fallback to regex for files with syntax errors
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            classes = re.findall(r'class\s+(\w+)\s*[:\(]', content)
            imports = re.findall(r'(?:from\s+(\S+)\s+)?import\s+(\S+)', content)
            imports = [imp[0] or imp[1] for imp in imports]
        
        return functions, classes, imports
    
    def _extract_python_dependencies(self, imports: List[str]) -> List[str]:
        """Extract dependencies from Python imports."""
        dependencies = []
        
        # Common external packages
        external_packages = {
            'requests', 'numpy', 'pandas', 'flask', 'django', 'fastapi',
            'sqlalchemy', 'pytest', 'click', 'jinja2', 'pydantic',
            'anthropic', 'openai', 'groq', 'ollama'
        }
        
        for imp in imports:
            base_package = imp.split('.')[0]
            if base_package in external_packages:
                dependencies.append(base_package)
        
        return list(set(dependencies))
    
    def _extract_python_patterns(self, content: str) -> List[str]:
        """Extract key patterns from Python code."""
        patterns = []
        
        # Check for common patterns
        if 'async def' in content:
            patterns.append('async_functions')
        if 'class.*Exception' in content:
            patterns.append('custom_exceptions')
        if '@dataclass' in content:
            patterns.append('dataclasses')
        if 'logging' in content:
            patterns.append('logging')
        if 'pytest' in content or 'unittest' in content:
            patterns.append('testing')
        if 'click' in content or 'argparse' in content:
            patterns.append('cli')
        if 'flask' in content or 'fastapi' in content:
            patterns.append('web_api')
        
        return patterns
    
    def _extract_batch_patterns(self, content: str) -> List[str]:
        """Extract patterns from batch/shell scripts."""
        patterns = []
        
        if 'python' in content.lower():
            patterns.append('python_execution')
        if 'pip install' in content.lower():
            patterns.append('package_installation')
        if 'venv' in content.lower() or 'virtualenv' in content.lower():
            patterns.append('virtual_environment')
        if 'echo' in content.lower():
            patterns.append('user_feedback')
        if 'if' in content.lower() and 'else' in content.lower():
            patterns.append('conditional_logic')
        if 'set' in content and '=' in content:
            patterns.append('environment_variables')
        
        return patterns
    
    def _extract_batch_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from batch scripts."""
        dependencies = []
        
        # Look for pip install commands
        pip_matches = re.findall(r'pip install\s+([^\s\n]+)', content, re.IGNORECASE)
        dependencies.extend(pip_matches)
        
        # Look for file references
        file_refs = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*\.(?:py|json|env|txt))', content)
        dependencies.extend(file_refs)
        
        return list(set(dependencies))
    
    def _extract_config_dependencies(self, content: str, filename: str) -> List[str]:
        """Extract dependencies from configuration files."""
        dependencies = []
        
        try:
            if filename.endswith('.json'):
                data = json.loads(content)
                if isinstance(data, dict):
                    # Look for common dependency keys
                    for key in ['dependencies', 'devDependencies', 'requires', 'imports']:
                        if key in data:
                            if isinstance(data[key], dict):
                                dependencies.extend(data[key].keys())
                            elif isinstance(data[key], list):
                                dependencies.extend(data[key])
                                
        except json.JSONDecodeError:
            pass
        
        # Look for file references in any config
        file_refs = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*\.(?:py|js|json|env))', content)
        dependencies.extend(file_refs)
        
        return list(set(dependencies))
    
    def _extract_config_patterns(self, content: str) -> List[str]:
        """Extract patterns from configuration files."""
        patterns = []
        
        if 'api' in content.lower():
            patterns.append('api_configuration')
        if 'database' in content.lower() or 'db' in content.lower():
            patterns.append('database_config')
        if 'secret' in content.lower() or 'key' in content.lower():
            patterns.append('secrets_management')
        if 'port' in content.lower() or 'host' in content.lower():
            patterns.append('network_config')
        
        return patterns
    
    def _calculate_complexity_score(self, content: str, functions: List[str], classes: List[str]) -> float:
        """Calculate a complexity score for the file."""
        score = 0.0
        
        # Base score from content length
        score += min(len(content) / 1000, 10)  # Max 10 points for length
        
        # Score from functions and classes
        score += len(functions) * 2
        score += len(classes) * 3
        
        # Score from complexity indicators
        complexity_indicators = ['if', 'for', 'while', 'try', 'except', 'async', 'await']
        for indicator in complexity_indicators:
            score += content.lower().count(indicator) * 0.5
        
        return min(score, 100)  # Cap at 100
    
    def _create_content_preview(self, content: str, file_type: str) -> str:
        """Create a preview of the file content."""
        lines = content.split('\n')
        
        # For Python files, try to get docstring or first few meaningful lines
        if file_type == 'python':
            preview_lines = []
            in_docstring = False
            
            for line in lines[:20]:  # First 20 lines
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                if '"""' in stripped or "'''" in stripped:
                    in_docstring = not in_docstring
                    if not in_docstring:
                        break
                if not in_docstring:
                    preview_lines.append(line)
                    if len(preview_lines) >= 5:
                        break
            
            return '\n'.join(preview_lines[:5])
        
        # For other files, just take first few non-empty lines
        preview_lines = [line for line in lines[:10] if line.strip()]
        return '\n'.join(preview_lines[:5])
    
    def _analyze_dependencies(self, files: List[FileAnalysis]) -> Dict[str, List[str]]:
        """Analyze dependencies between files."""
        dependencies = {}
        
        for file_analysis in files:
            file_deps = []
            
            # Check if other files are referenced
            for other_file in files:
                if other_file.file_path != file_analysis.file_path:
                    # Check if file is imported or referenced
                    other_name = Path(other_file.file_path).stem
                    if other_name in file_analysis.imports or other_name in file_analysis.dependencies:
                        file_deps.append(other_file.file_path)
            
            dependencies[file_analysis.file_path] = file_deps
        
        return dependencies
    
    def _extract_patterns(self, files: List[FileAnalysis], task_type: str) -> Dict[str, List[str]]:
        """Extract common patterns from analyzed files."""
        patterns = {
            'architectural': [],
            'implementation': [],
            'testing': [],
            'configuration': []
        }
        
        all_patterns = []
        for file_analysis in files:
            all_patterns.extend(file_analysis.key_patterns)
        
        # Categorize patterns
        for pattern in set(all_patterns):
            if pattern in ['async_functions', 'web_api', 'cli']:
                patterns['architectural'].append(pattern)
            elif pattern in ['logging', 'custom_exceptions', 'dataclasses']:
                patterns['implementation'].append(pattern)
            elif pattern in ['testing', 'pytest']:
                patterns['testing'].append(pattern)
            elif pattern in ['api_configuration', 'database_config', 'secrets_management']:
                patterns['configuration'].append(pattern)
        
        return patterns
    
    def _generate_recommendations(self, files: List[FileAnalysis], description: str, task_type: str) -> List[str]:
        """Generate specific recommendations based on file analysis."""
        recommendations = []
        
        # Analyze existing files for specific recommendations
        if task_type == 'DEV' and any('install' in desc.lower() or 'setup' in desc.lower() for desc in [description]):
            # For install script tasks
            setup_files = [f for f in files if any(pattern in f.file_path.lower() for pattern in ['setup', 'install', '.bat', '.sh'])]
            if setup_files:
                recommendations.append(f"Enhance existing setup script: {setup_files[0].file_path}")
                recommendations.append("Add user interaction prompts for configuration")
                recommendations.append("Implement settings validation and storage")
            
            config_files = [f for f in files if any(pattern in f.file_path.lower() for pattern in ['.env', '.json', 'config'])]
            if config_files:
                for config_file in config_files:
                    recommendations.append(f"Update configuration file: {config_file.file_path}")
        
        # Add general recommendations based on patterns
        all_patterns = []
        for file_analysis in files:
            all_patterns.extend(file_analysis.key_patterns)
        
        if 'logging' in all_patterns:
            recommendations.append("Implement comprehensive logging for debugging")
        if 'testing' in all_patterns:
            recommendations.append("Add unit tests for new functionality")
        if 'async_functions' in all_patterns:
            recommendations.append("Consider async/await patterns for better performance")
        
        return recommendations
    
    def _build_project_structure(self, files: List[FileAnalysis]) -> Dict[str, Any]:
        """Build a project structure map from analyzed files."""
        structure = {}
        
        for file_analysis in files:
            path_parts = Path(file_analysis.file_path).parts
            current = structure
            
            for part in path_parts[:-1]:  # All except filename
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file info
            filename = path_parts[-1]
            current[filename] = {
                'type': file_analysis.file_type,
                'functions': len(file_analysis.functions),
                'classes': len(file_analysis.classes),
                'complexity': file_analysis.complexity_score
            }
        
        return structure
    
    def get_file_specific_recommendations(self, file_path: str, task_description: str) -> List[str]:
        """Get specific recommendations for a particular file."""
        recommendations = []
        
        try:
            file_analysis = self._analyze_file(Path(self.project_root) / file_path)
            if not file_analysis:
                return recommendations
            
            # File-specific recommendations based on analysis
            if file_analysis.file_type == 'batch':
                recommendations.append(f"Add error handling and user feedback to {file_path}")
                recommendations.append(f"Implement progress indicators in {file_path}")
                if 'conditional_logic' not in file_analysis.key_patterns:
                    recommendations.append(f"Add conditional logic for different scenarios in {file_path}")
            
            elif file_analysis.file_type == 'python':
                if not file_analysis.functions:
                    recommendations.append(f"Consider breaking down {file_path} into functions for better modularity")
                if 'logging' not in file_analysis.key_patterns:
                    recommendations.append(f"Add logging to {file_path} for better debugging")
            
            elif file_analysis.file_type == 'config':
                recommendations.append(f"Validate configuration values in {file_path}")
                recommendations.append(f"Add documentation for configuration options in {file_path}")
            
        except Exception as e:
            logger.warning(f"Error getting file-specific recommendations for {file_path}: {e}")
        
        return recommendations 