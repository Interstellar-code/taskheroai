"""
AI-Enhanced Task Creator Module

Integrates the enhanced task template with AI capabilities to provide intelligent,
comprehensive task creation with context-aware content generation.

Phase 4B: Real AI Integration - Enhanced with actual LLM provider integration
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio

from .template_engine import TemplateEngine
from .task_manager import TaskManager, TaskPriority, TaskStatus
from .semantic_search import SemanticSearchEngine, ContextChunk, SearchResult
from .context_analyzer import ContextAnalyzer, ProjectContext
from .template_optimizer import TemplateOptimizer
from ..ai.providers.provider_factory import ProviderFactory
from ..ai.providers.base_provider import AIProvider

logger = logging.getLogger("TaskHeroAI.ProjectManagement.AITaskCreator")


class AITaskCreator:
    """AI-enhanced task creation with intelligent content generation."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the AI Task Creator.
        
        Args:
            project_root: Root directory for project management
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.template_engine = TemplateEngine(project_root)
        self.task_manager = TaskManager(project_root)
        
        # Phase 4B: Real AI Integration
        self.provider_factory = ProviderFactory()
        self.ai_provider: Optional[AIProvider] = None
        self.ai_available = False
        
        self.semantic_search = SemanticSearchEngine(str(self.project_root))
        
        # TASK-044: Enhanced context analysis and template optimization
        self.context_analyzer = ContextAnalyzer(str(self.project_root))
        self.template_optimizer = TemplateOptimizer()
        
        # Enhanced task template path
        self.enhanced_template = "tasks/enhanced_task.j2"
        
        # Task type mappings for filename generation
        self.task_type_mappings = {
            "Development": "DEV",
            "Bug Fix": "BUG", 
            "Test Case": "TEST",
            "Documentation": "DOC",
            "Design": "DES",
            "Research": "RES",
            "Planning": "PLAN"
        }
        
        # Phase 4B: AI Enhancement Configuration
        self.ai_config = {
            'max_context_tokens': 8000,
            'max_response_tokens': 2000,
            'temperature': 0.7,
            'use_streaming': False,  # For now, disable streaming in task creation
            'fallback_enabled': True,
            'context_selection_threshold': 0.6
        }
        
        # Phase 4C: User Experience Enhancements
        self.phase4c_config = {
            'enable_context_selection': True,
            'enable_progressive_creation': True,
            'enable_quality_feedback': True,
            'context_preview_length': 150,
            'max_context_items': 10,
            'quality_threshold': 0.7
        }
        
        # Phase 4C: Task creation state for progressive wizard
        self.creation_state = {
            'step': 0,
            'total_steps': 4,
            'collected_data': {},
            'selected_context': [],
            'ai_enhancements': {},
            'quality_score': 0.0
        }
        
    async def _initialize_ai_provider(self) -> bool:
        """Initialize AI provider for real LLM integration."""
        try:
            if self.ai_provider is None:
                # Get best available provider
                best_provider = await self.provider_factory.get_best_available_provider()
                if best_provider:
                    self.ai_provider = await self.provider_factory.create_provider(best_provider)
                    self.ai_available = True
                    logger.info(f"AI provider initialized: {best_provider}")
                    return True
                else:
                    logger.warning("No AI providers available - using fallback mode")
                    self.ai_available = False
                    return False
            return self.ai_available
        except Exception as e:
            logger.warning(f"AI provider initialization failed: {e}")
            self.ai_available = False
            return False
    
    async def create_enhanced_task(self, 
                           title: str,
                           description: str = "",
                           task_type: str = "Development",
                           priority: str = "medium",
                           assigned_to: str = "Developer",
                           due_date: Optional[str] = None,
                           tags: List[str] = None,
                           dependencies: List[str] = None,
                           effort_estimate: str = "Medium",
                           use_ai_enhancement: bool = True,
                           selected_context: List[ContextChunk] = None,
                           ai_enhancements: Dict[str, Any] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create an enhanced task using the enhanced_task.j2 template with AI assistance.
        
        Args:
            title: Task title
            description: Task description/requirements
            task_type: Type of task (Development, Bug Fix, etc.)
            priority: Task priority (low, medium, high, critical)
            assigned_to: Who the task is assigned to
            due_date: Due date in YYYY-MM-DD format
            tags: List of tags for the task
            dependencies: List of dependent task IDs
            effort_estimate: Effort estimate (Small, Medium, Large)
            use_ai_enhancement: Whether to use AI for content enhancement
            
        Returns:
            Tuple of (success, task_id, file_path or error_message)
        """
        try:
            # Generate task ID
            task_id = self._generate_task_id()
            
            # Prepare basic context
            context = self._prepare_base_context(
                task_id=task_id,
                title=title,
                description=description,
                task_type=task_type,
                priority=priority,
                assigned_to=assigned_to,
                due_date=due_date,
                tags=tags or [],
                dependencies=dependencies or [],
                effort_estimate=effort_estimate
            )
            
            # Phase 4C: Use provided AI enhancements or generate new ones
            if ai_enhancements:
                # Use pre-generated enhancements from progressive creation
                if ai_enhancements.get('description'):
                    context['description'] = ai_enhancements['description']
                if ai_enhancements.get('requirements'):
                    context['functional_requirements'] = ai_enhancements['requirements']
                if ai_enhancements.get('implementation_steps'):
                    context['implementation_steps'] = ai_enhancements['implementation_steps']
                if ai_enhancements.get('risks'):
                    context['risks'] = ai_enhancements['risks']
                
                # Add Phase 4C metadata
                context['phase4c_enhanced'] = True
                context['selected_context_count'] = len(selected_context) if selected_context else 0
                
            elif use_ai_enhancement:
                # Traditional AI enhancement
                context = await self._enhance_with_ai(context, description)
            
            # Generate task content using enhanced template
            task_content = self.template_engine.render_template(
                self.enhanced_template, 
                context
            )
            
            # Generate filename following naming convention
            filename = self._generate_filename(task_id, task_type, title)
            
            # Save the task file
            file_path = self._save_task_file(filename, task_content)
            
            # Phase 4C: Collect quality feedback if enhancements were used
            if ai_enhancements and self.creation_state.get('quality_score'):
                self._collect_quality_feedback(task_id, self.creation_state['quality_score'])
            
            logger.info(f"Enhanced task created: {task_id} at {file_path}")
            return True, task_id, str(file_path)
            
        except Exception as e:
            logger.error(f"Error creating enhanced task: {e}")
            return False, "", str(e)
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        # Get existing task IDs to find the next number
        existing_tasks = self.task_manager.get_all_tasks()
        max_id = 0
        
        for status_tasks in existing_tasks.values():
            for task in status_tasks:
                # Extract number from task ID (e.g., TASK-015 -> 15)
                if task.task_id.startswith("TASK-"):
                    try:
                        task_num = int(task.task_id.split("-")[1])
                        max_id = max(max_id, task_num)
                    except (IndexError, ValueError):
                        continue
        
        return f"TASK-{max_id + 1:03d}"
    
    def _prepare_base_context(self, **kwargs) -> Dict[str, Any]:
        """Prepare the base context for template rendering."""
        # Convert tags and dependencies to proper format
        tags = kwargs.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        dependencies = kwargs.get('dependencies', [])
        if isinstance(dependencies, str):
            dependencies = [dep.strip() for dep in dependencies.split(',') if dep.strip()]
        
        # Calculate due date if not provided
        due_date = kwargs.get('due_date')
        if not due_date:
            # Default to 1 week from now for medium effort, adjust based on effort
            effort = kwargs.get('effort_estimate', 'Medium').lower()
            days_map = {'small': 3, 'medium': 7, 'large': 14}
            days = days_map.get(effort, 7)
            due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get task type abbreviation
        task_type = kwargs.get('task_type', 'Development')
        task_prefix = self.task_type_mappings.get(task_type, 'DEV')
        
        return {
            'task_id': kwargs.get('task_id'),
            'title': kwargs.get('title'),
            'description': kwargs.get('description', ''),
            'brief_description': kwargs.get('description', '')[:200] + '...' if len(kwargs.get('description', '')) > 200 else kwargs.get('description', ''),
            'priority': kwargs.get('priority', 'medium').title(),
            'status': 'Todo',
            'assignee': kwargs.get('assigned_to', 'Developer'),
            'task_type': task_type,
            'task_prefix': task_prefix,
            'due_date': due_date,
            'created': datetime.now().strftime('%Y-%m-%d'),
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'tags': tags,
            'dependencies': dependencies,
            'estimated_effort': kwargs.get('effort_estimate', 'Medium'),
            'sequence': int(kwargs.get('task_id', 'TASK-001').split('-')[1]) if kwargs.get('task_id') else 1,
            'related_epic': kwargs.get('related_epic', 'TaskHero AI Project'),
            
            # Enhanced template specific fields
            'show_naming_convention': True,
            'show_metadata_legend': True,
            'show_implementation_analysis': True,
            
            # Default implementation steps
            'implementation_steps': [
                {
                    'title': 'Requirements Analysis',
                    'completed': False,
                    'in_progress': False,
                    'target_date': due_date,
                    'substeps': [
                        {'description': 'Review requirements and specifications', 'completed': False},
                        {'description': 'Identify key stakeholders and dependencies', 'completed': False},
                        {'description': 'Define acceptance criteria', 'completed': False}
                    ]
                },
                {
                    'title': 'Design and Planning',
                    'completed': False,
                    'in_progress': False,
                    'target_date': due_date,
                    'substeps': [
                        {'description': 'Create technical design document', 'completed': False},
                        {'description': 'Plan implementation approach', 'completed': False},
                        {'description': 'Identify potential risks and mitigation strategies', 'completed': False}
                    ]
                },
                {
                    'title': 'Implementation',
                    'completed': False,
                    'in_progress': False,
                    'target_date': due_date,
                    'substeps': [
                        {'description': 'Implement core functionality', 'completed': False},
                        {'description': 'Add error handling and validation', 'completed': False},
                        {'description': 'Write unit tests', 'completed': False}
                    ]
                }
            ],
            
            # Default success criteria
            'success_criteria': [
                {'description': 'All functional requirements are implemented', 'completed': False},
                {'description': 'Code passes all tests and quality checks', 'completed': False},
                {'description': 'Documentation is complete and accurate', 'completed': False}
            ],
            
            # Flow diagram steps
            'flow_steps': [
                {'title': 'User initiates action'},
                {'title': 'System validates input'},
                {'title': 'Process request'},
                {'title': 'Return result'}
            ],
            
            # Default technical considerations
            'technical_considerations': 'Consider performance, security, maintainability, and scalability requirements.',
            'state_management': 'Define how application state will be managed and synchronized.',
            'component_architecture': 'Plan component structure for reusability and maintainability.',
            'performance_requirements': 'Identify performance benchmarks and optimization strategies.',
            
            # Default risk assessment
            'risks': [
                {
                    'description': 'Technical complexity higher than estimated',
                    'impact': 'Medium',
                    'probability': 'Low',
                    'mitigation': 'Break down into smaller tasks, seek technical review'
                },
                {
                    'description': 'Dependencies not available on time',
                    'impact': 'High',
                    'probability': 'Medium',
                    'mitigation': 'Identify alternative approaches, communicate early with dependencies'
                }
            ],
            
            # Additional template variables
            'functional_requirements': f'Implement {kwargs.get("title", "functionality").lower()} according to specifications',
            'functional_requirements_list': None,
            'benefits_list': None,
            'flow_description': f'User workflow for {kwargs.get("title", "task")} implementation',
            'detailed_description': kwargs.get('description', ''),
            'purpose_benefits': f'This task enhances the TaskHero AI system by implementing {kwargs.get("title", "functionality").lower()}.',
            
            # UI Design variables
            'ui_design_overview': 'UI design considerations will be defined during implementation phase.',
            'ui_layout': None,
            'ui_colors': 'Follow TaskHero AI design system color palette',
            'ui_typography': 'Use system default typography standards',
            'ui_spacing': 'Follow 8px grid system for consistent spacing',
            'ui_components': 'Utilize existing component library where applicable',
            'ui_icons': 'Use consistent icon set from design system',
            'design_references': None,
            
            # Technical considerations variables
            'data_persistence': 'Data persistence requirements will be defined based on functionality needs',
            'state_sync': 'State synchronization will follow established patterns',
            'reusability': 'Components will be designed for maximum reusability',
            'integration_patterns': 'Integration will follow existing architectural patterns',
            'memory_management': 'Memory usage will be optimized for performance',
            'loading_optimizations': 'Loading performance will be optimized where applicable',
            'browser_compatibility': 'Cross-browser compatibility will be ensured',
            'backward_compatibility_notes': 'Backward compatibility will be maintained where possible',
            'integration_compatibility': 'Integration compatibility with existing systems will be verified',
            
            # Implementation analysis variables
            'current_implementation': 'Current implementation will be analyzed during planning phase',
            'current_components': 'Existing components will be mapped and evaluated',
            'current_limitations': 'Current limitations will be identified and addressed',
            'new_features': 'New features will be implemented according to requirements',
            'new_features_2': 'Additional enhancements will be considered',
            'new_features_3': 'Future extensibility will be planned',
            'migration_approach': 'Migration strategy will be developed if needed',
            'backward_compatibility': 'Backward compatibility strategy will be defined',
            'risk_mitigation': 'Risk mitigation strategies will be implemented',
            'component_mapping': None,
            
            # Database and schema variables
            'database_changes': None,
            'database_schema': None,
            
            # Time and reference variables
            'estimated_hours': None,
            'actual_hours': None,
            'references': None,
            'updates': None,
            'dependent_tasks': None,
            'technical_dependencies': None,
            'dependency_type': 'Related tasks and technical dependencies will be identified during planning phase.',
            'testing_overview': 'Testing strategy will be developed based on implementation requirements.',
            'testing_strategy': None,
            'test_cases': None
        }
    
    async def _enhance_with_ai(self, context: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Enhance the context using AI capabilities with real LLM integration and TASK-044 improvements."""
        try:
            if not await self._initialize_ai_provider():
                logger.info("AI enhancement not available, using default context")
                return context
            
            # TASK-044: Enhanced context analysis
            task_type = context.get('task_type', 'Development')
            
            # Step 1: Analyze project context for specific file references and recommendations
            project_context = self.context_analyzer.analyze_task_context(description, task_type)
            
            # Step 2: Collect relevant context from embeddings (existing functionality)
            relevant_context = self._collect_embeddings_context(description, context)
            
            # Step 3: Filter and optimize context for AI processing
            optimized_context = self._optimize_context_for_ai(relevant_context)
            
            # Phase 4B: Real AI Integration with TASK-044 enhancements
            enhanced_context = context.copy()
            
            # TASK-044: Add specific file references and recommendations
            if project_context.relevant_files:
                enhanced_context['relevant_files'] = [
                    f.file_path for f in project_context.relevant_files[:5]  # Top 5 most relevant
                ]
                enhanced_context['file_recommendations'] = project_context.recommendations[:10]
                
                # Add specific implementation details based on actual files
                enhanced_context['current_implementation'] = self._generate_current_implementation_analysis(
                    project_context
                )
                
                # Add specific file references in description
                enhanced_context['detailed_description'] = self._enhance_description_with_file_context(
                    description, project_context
                )
            
            # Step 4: Use real AI to enhance different aspects with context
            if description and self.ai_available:
                try:
                    # Enhanced description with AI and file context
                    if not enhanced_context.get('detailed_description'):
                        enhanced_context['detailed_description'] = await self._ai_enhance_description(
                            description, context, optimized_context
                        )
                    
                    # AI-generated requirements with file context
                    enhanced_context['functional_requirements_list'] = await self._ai_generate_requirements(
                        description, enhanced_context, optimized_context
                    )
                    
                    # AI-generated benefits
                    enhanced_context['benefits_list'] = await self._ai_generate_benefits(
                        description, enhanced_context, optimized_context
                    )
                    
                    # AI-generated implementation steps with specific file references
                    enhanced_context['implementation_steps'] = await self._ai_generate_implementation_steps(
                        description, enhanced_context, optimized_context
                    )
                    
                    # AI-generated risk assessment
                    enhanced_context['risks'] = await self._ai_generate_risk_assessment(
                        description, enhanced_context, optimized_context
                    )
                    
                    # AI-generated technical considerations
                    tech_considerations = await self._ai_generate_technical_considerations(
                        description, enhanced_context, optimized_context
                    )
                    enhanced_context.update(tech_considerations)
                    
                except Exception as ai_error:
                    logger.warning(f"AI enhancement partially failed: {ai_error}")
                    # Fall back to basic enhancement for failed components
            
            # TASK-044: Template optimization - filter irrelevant sections and customize content
            enhanced_context = self.template_optimizer.optimize_template_context(
                enhanced_context, task_type, description
            )
            
            # TASK-044: Generate task-specific flow diagram
            flow_diagram_context = self.template_optimizer.generate_task_specific_flow_diagram(
                task_type, description, enhanced_context
            )
            enhanced_context.update(flow_diagram_context)
            
            # Step 5: Add AI metadata
            enhanced_context['ai_context_used'] = len(relevant_context)
            enhanced_context['ai_enhancement_applied'] = self.ai_available
            enhanced_context['ai_provider_used'] = self.ai_provider.get_name() if self.ai_provider else None
            enhanced_context['task044_enhanced'] = True  # Mark as TASK-044 enhanced
            enhanced_context['context_files_analyzed'] = len(project_context.relevant_files)
            
            # TASK-044: Validate template quality
            quality_issues = self.template_optimizer.validate_optimized_template(enhanced_context)
            if quality_issues:
                logger.warning(f"Template quality issues detected: {quality_issues}")
                enhanced_context['quality_issues'] = quality_issues
            
            return enhanced_context
            
        except Exception as e:
            logger.warning(f"AI enhancement failed, using default context: {e}")
            return context
    
    def _generate_current_implementation_analysis(self, project_context: ProjectContext) -> str:
        """Generate analysis of current implementation based on project context."""
        try:
            analysis_parts = []
            
            if project_context.relevant_files:
                analysis_parts.append("**Current Implementation Analysis:**")
                
                # Analyze file types and patterns
                file_types = {}
                for file_analysis in project_context.relevant_files:
                    file_type = file_analysis.file_type
                    if file_type not in file_types:
                        file_types[file_type] = []
                    file_types[file_type].append(file_analysis.file_path)
                
                for file_type, files in file_types.items():
                    analysis_parts.append(f"- **{file_type.title()} files**: {', '.join(files[:3])}")
                    if len(files) > 3:
                        analysis_parts.append(f"  (and {len(files) - 3} more)")
                
                # Add patterns found
                if project_context.patterns:
                    analysis_parts.append("\n**Implementation Patterns Found:**")
                    for category, patterns in project_context.patterns.items():
                        if patterns:
                            analysis_parts.append(f"- **{category.title()}**: {', '.join(patterns)}")
                
                # Add dependencies
                if project_context.dependencies:
                    analysis_parts.append("\n**File Dependencies:**")
                    for file_path, deps in list(project_context.dependencies.items())[:3]:
                        if deps:
                            analysis_parts.append(f"- `{file_path}` depends on: {', '.join(deps[:2])}")
            
            return '\n'.join(analysis_parts) if analysis_parts else "Current implementation will be analyzed during planning phase"
            
        except Exception as e:
            logger.warning(f"Error generating current implementation analysis: {e}")
            return "Current implementation will be analyzed during planning phase"
    
    def _enhance_description_with_file_context(self, description: str, project_context: ProjectContext) -> str:
        """Enhance description with specific file references and context."""
        try:
            enhanced_parts = [description]
            
            if project_context.relevant_files:
                enhanced_parts.append("\n**Relevant Files Identified:**")
                
                for file_analysis in project_context.relevant_files[:5]:  # Top 5 files
                    file_info = f"- `{file_analysis.file_path}` ({file_analysis.file_type})"
                    
                    # Add function/class info if available
                    if file_analysis.functions:
                        file_info += f" - Functions: {', '.join(file_analysis.functions[:3])}"
                    if file_analysis.classes:
                        file_info += f" - Classes: {', '.join(file_analysis.classes[:2])}"
                    
                    enhanced_parts.append(file_info)
            
            if project_context.recommendations:
                enhanced_parts.append("\n**Specific Recommendations:**")
                for rec in project_context.recommendations[:5]:
                    enhanced_parts.append(f"- {rec}")
            
            return '\n'.join(enhanced_parts)
            
        except Exception as e:
            logger.warning(f"Error enhancing description with file context: {e}")
            return description
    
    def _collect_embeddings_context(self, description: str, context: Dict[str, Any]) -> List[ContextChunk]:
        """
        Collect relevant context using semantic search.
        
        Args:
            description: Task description to search for
            context: Current task context
            
        Returns:
            List of relevant context chunks
        """
        try:
            # Create search query from description and task type
            task_type = context.get('task_type', 'Development')
            search_query = f"{description} {task_type}"
            
            # Perform semantic search
            search_result = self.semantic_search.search(
                query=search_query,
                max_results=10,
                file_types=None  # Search all file types
            )
            
            logger.info(f"Semantic search found {len(search_result.chunks)} relevant chunks in {search_result.search_time:.3f}s")
            
            return search_result.chunks
            
        except Exception as e:
            logger.error(f"Error collecting semantic context: {e}")
            return []
    
    def _optimize_context_for_ai(self, relevant_context: List[ContextChunk]) -> List[Dict[str, Any]]:
        """
        Optimize context chunks for AI processing by filtering and formatting.
        
        Args:
            relevant_context: List of context chunks from semantic search
            
        Returns:
            Optimized context list for AI processing
        """
        try:
            # Filter by relevance threshold
            filtered_context = [
                chunk for chunk in relevant_context 
                if chunk.relevance_score >= self.ai_config['context_selection_threshold']
            ]
            
            # Sort by relevance score
            filtered_context.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Limit context to prevent token overflow
            max_chunks = 10
            optimized_context = []
            total_tokens = 0
            
            for chunk in filtered_context[:max_chunks]:
                # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
                chunk_tokens = len(chunk.text) // 4
                
                if total_tokens + chunk_tokens > self.ai_config['max_context_tokens']:
                    break
                
                optimized_context.append({
                    'file_name': chunk.file_name,
                    'file_type': chunk.file_type,
                    'content': chunk.text[:1000],  # Limit chunk size
                    'relevance_score': chunk.relevance_score,
                    'line_start': getattr(chunk, 'line_start', None),
                    'line_end': getattr(chunk, 'line_end', None)
                })
                
                total_tokens += chunk_tokens
            
            logger.info(f"Optimized context: {len(optimized_context)} chunks, ~{total_tokens} tokens")
            return optimized_context
            
        except Exception as e:
            logger.error(f"Error optimizing context for AI: {e}")
            return []
    
    def _extract_search_terms(self, description: str, task_type: str) -> List[str]:
        """Extract search terms from description and task type."""
        # Basic keyword extraction (could be enhanced with NLP)
        import re
        
        # Clean and tokenize description
        words = re.findall(r'\b\w+\b', description.lower())
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract meaningful terms
        meaningful_words = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Add task type specific terms
        task_terms = {
            'development': ['implement', 'create', 'build', 'develop', 'code', 'function', 'class', 'method'],
            'bug': ['fix', 'error', 'bug', 'issue', 'problem', 'debug', 'resolve'],
            'test': ['test', 'testing', 'unit', 'integration', 'coverage', 'assert', 'verify'],
            'documentation': ['document', 'docs', 'readme', 'guide', 'manual', 'api', 'reference'],
            'design': ['design', 'ui', 'ux', 'interface', 'layout', 'component', 'style'],
            'research': ['research', 'analyze', 'investigate', 'study', 'explore', 'evaluate']
        }
        
        if task_type in task_terms:
            meaningful_words.extend(task_terms[task_type])
        
        # Return unique terms, prioritizing longer ones
        unique_terms = list(set(meaningful_words))
        unique_terms.sort(key=len, reverse=True)
        
        return unique_terms[:10]  # Top 10 search terms
    
    def _calculate_relevance(self, embedding_data: Dict[str, Any], search_terms: List[str], task_type: str) -> float:
        """Calculate relevance score for an embedding file."""
        try:
            score = 0.0
            
            # Get file path and content
            file_path = embedding_data.get('path', '').lower()
            chunks = embedding_data.get('chunks', [])
            
            # File path relevance
            for term in search_terms:
                if term in file_path:
                    score += 0.2
            
            # Task type relevance
            if task_type in file_path:
                score += 0.3
            
            # Content relevance
            content_text = ""
            for chunk in chunks:
                if isinstance(chunk, dict):
                    content_text += chunk.get('text', '') + " "
                elif isinstance(chunk, str):
                    content_text += chunk + " "
            
            content_text = content_text.lower()
            
            # Search term matches in content
            for term in search_terms:
                if term in content_text:
                    score += 0.1
            
            # Bonus for task-related files
            if any(keyword in file_path for keyword in ['task', 'project', 'management', 'planning']):
                score += 0.2
            
            # Bonus for code files if development task
            if task_type == 'development' and any(ext in file_path for ext in ['.py', '.js', '.ts', '.java', '.cpp']):
                score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.warning(f"Error calculating relevance: {e}")
            return 0.0
    
    def _extract_content_preview(self, embedding_data: Dict[str, Any]) -> str:
        """Extract a preview of the content from embedding data."""
        try:
            chunks = embedding_data.get('chunks', [])
            if not chunks:
                return "No content preview available"
            
            # Get first chunk text
            first_chunk = chunks[0]
            if isinstance(first_chunk, dict):
                text = first_chunk.get('text', '')
            elif isinstance(first_chunk, str):
                text = first_chunk
            else:
                text = str(first_chunk)
            
            # Return first 200 characters
            return text[:200] + "..." if len(text) > 200 else text
            
        except Exception as e:
            logger.warning(f"Error extracting content preview: {e}")
            return "Content preview unavailable"
    
    def _determine_file_type(self, filename: str) -> str:
        """Determine file type from filename."""
        filename = filename.lower()
        
        if any(ext in filename for ext in ['.py', '.pyx']):
            return 'python'
        elif any(ext in filename for ext in ['.js', '.jsx', '.ts', '.tsx']):
            return 'javascript'
        elif any(ext in filename for ext in ['.md', '.markdown']):
            return 'markdown'
        elif any(ext in filename for ext in ['.json', '.yaml', '.yml']):
            return 'config'
        elif any(ext in filename for ext in ['.html', '.css', '.scss']):
            return 'web'
        elif 'task' in filename:
            return 'task'
        elif 'test' in filename:
            return 'test'
        elif 'doc' in filename:
            return 'documentation'
        else:
            return 'other'
    
    async def _ai_enhance_description(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> str:
        """Use real AI to enhance the task description with codebase context."""
        try:
            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')
            
            # Build context-aware prompt
            context_info = ""
            if relevant_context:
                context_info = "\n\nRelevant codebase context:\n"
                for ctx in relevant_context[:5]:
                    context_info += f"- {ctx['file_name']} ({ctx['file_type']}): {ctx['content'][:200]}...\n"
            
            prompt = f"""You are an expert software project manager creating a comprehensive task description for a {task_type} task titled "{title}".

Original description: {description}

{context_info}

Please enhance this task description with:
1. Clear overview and objectives
2. Technical context based on the codebase
3. Key implementation considerations
4. Expected deliverables
5. Integration points with existing system

Provide a detailed, professional description that would help a developer understand exactly what needs to be implemented. Focus on technical accuracy and actionable details."""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=self.ai_config['max_response_tokens'],
                temperature=self.ai_config['temperature']
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"AI description enhancement failed: {e}")
            # Fallback to basic enhancement
            return f"{description}\n\nThis {context.get('task_type', 'development')} task requires careful implementation following established patterns and best practices."
    
    async def _ai_generate_requirements(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> List[str]:
        """Generate functional requirements using AI analysis."""
        try:
            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')
            
            # Build context for AI
            context_info = ""
            if relevant_context:
                context_info = "\n\nCodebase context:\n"
                for ctx in relevant_context[:3]:
                    context_info += f"- {ctx['file_name']}: {ctx['content'][:150]}...\n"
            
            prompt = f"""As a technical analyst, generate specific functional requirements for this {task_type} task: "{title}"

Description: {description}

{context_info}

Generate 5-8 specific, measurable functional requirements that:
1. Are testable and verifiable
2. Consider the existing codebase patterns
3. Address {task_type.lower()}-specific concerns
4. Include integration requirements
5. Cover error handling and edge cases

Format as a simple list, one requirement per line starting with "- "."""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=800,
                temperature=0.6
            )
            
            # Parse response into list
            requirements = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    requirements.append(line[2:])
                elif line and not line.startswith('#'):
                    requirements.append(line)
            
            return requirements[:8] if requirements else self._get_fallback_requirements(task_type)
            
        except Exception as e:
            logger.error(f"AI requirements generation failed: {e}")
            return self._get_fallback_requirements(context.get('task_type', 'Development'))
    
    def _get_fallback_requirements(self, task_type: str) -> List[str]:
        """Fallback requirements when AI generation fails."""
        base = [
            "System must handle the described functionality correctly",
            "Implementation must be robust and handle edge cases",
            "Performance must meet established benchmarks"
        ]
        
        if task_type == 'Development':
            base.extend([
                "Code must follow established architectural patterns",
                "Integration with existing systems must be seamless"
            ])
        elif task_type == 'Bug Fix':
            base.extend([
                "Root cause must be identified and addressed",
                "Fix must not introduce new issues or regressions"
            ])
        
        return base
    
    async def _ai_generate_benefits(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> List[str]:
        """Generate benefits and value proposition using AI."""
        try:
            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')
            
            prompt = f"""As a business analyst, identify the key benefits and value proposition for this {task_type} task: "{title}"

Description: {description}

Generate 4-6 specific benefits that this task will provide:
1. Business value and impact
2. Technical improvements
3. User experience enhancements
4. Long-term strategic value
5. Risk reduction or mitigation

Format as a simple list, one benefit per line starting with "- "."""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=600,
                temperature=0.6
            )
            
            # Parse response into list
            benefits = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    benefits.append(line[2:])
                elif line and not line.startswith('#'):
                    benefits.append(line)
            
            return benefits[:6] if benefits else self._get_fallback_benefits()
            
        except Exception as e:
            logger.error(f"AI benefits generation failed: {e}")
            return self._get_fallback_benefits()
    
    def _get_fallback_benefits(self) -> List[str]:
        """Fallback benefits when AI generation fails."""
        return [
            "Improves overall system functionality and user experience",
            "Enhances code quality and maintainability",
            "Reduces technical debt and future maintenance costs",
            "Supports project goals and business objectives"
        ]
    
    async def _ai_generate_implementation_steps(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate implementation steps using AI analysis."""
        try:
            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')
            due_date = context.get('due_date')
            
            prompt = f"""As a technical project manager, create detailed implementation steps for this {task_type} task: "{title}"

Description: {description}

Generate 3-5 major implementation phases with specific sub-steps for each phase. Consider:
1. Requirements analysis and planning
2. Design and architecture
3. Implementation and development
4. Testing and validation
5. Deployment and documentation

For each phase, provide:
- Phase title
- 2-4 specific sub-steps
- Clear deliverables

Format as:
Phase 1: [Title]
- [Sub-step 1]
- [Sub-step 2]
- [Sub-step 3]

Phase 2: [Title]
- [Sub-step 1]
- [Sub-step 2]"""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=1000,
                temperature=0.6
            )
            
            # Parse response into structured format
            steps = self._parse_implementation_steps(response, due_date)
            return steps if steps else self._get_fallback_implementation_steps(due_date)
            
        except Exception as e:
            logger.error(f"AI implementation steps generation failed: {e}")
            return self._get_fallback_implementation_steps(context.get('due_date'))
    
    def _parse_implementation_steps(self, response: str, due_date: Optional[str]) -> List[Dict[str, Any]]:
        """Parse AI response into implementation steps structure."""
        steps = []
        current_phase = None
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('Phase ') and ':' in line:
                if current_phase:
                    steps.append(current_phase)
                
                phase_title = line.split(':', 1)[1].strip()
                current_phase = {
                    'title': phase_title,
                    'completed': False,
                    'in_progress': False,
                    'target_date': due_date,
                    'substeps': []
                }
            elif line.startswith('- ') and current_phase:
                current_phase['substeps'].append({
                    'description': line[2:],
                    'completed': False
                })
        
        if current_phase:
            steps.append(current_phase)
        
        return steps[:5]  # Limit to 5 phases
    
    def _get_fallback_implementation_steps(self, due_date: Optional[str]) -> List[Dict[str, Any]]:
        """Fallback implementation steps when AI generation fails."""
        return [
            {
                'title': 'Requirements Analysis',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'substeps': [
                    {'description': 'Review requirements and specifications', 'completed': False},
                    {'description': 'Identify key stakeholders and dependencies', 'completed': False},
                    {'description': 'Define acceptance criteria', 'completed': False}
                ]
            },
            {
                'title': 'Implementation',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'substeps': [
                    {'description': 'Implement core functionality', 'completed': False},
                    {'description': 'Add error handling and validation', 'completed': False},
                    {'description': 'Write unit tests', 'completed': False}
                ]
            }
        ]
    
    async def _ai_generate_risk_assessment(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Generate risk assessment using AI analysis."""
        try:
            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')
            
            prompt = f"""As a risk analyst, identify potential risks for this {task_type} task: "{title}"

Description: {description}

Identify 3-5 specific risks with:
1. Risk description
2. Impact level (Low/Medium/High)
3. Probability (Low/Medium/High)
4. Mitigation strategy

Format as:
Risk: [Description]
Impact: [Level]
Probability: [Level]
Mitigation: [Strategy]

---"""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=800,
                temperature=0.6
            )
            
            # Parse response into risk structure
            risks = self._parse_risk_assessment(response)
            return risks if risks else self._get_fallback_risks()
            
        except Exception as e:
            logger.error(f"AI risk assessment generation failed: {e}")
            return self._get_fallback_risks()
    
    def _parse_risk_assessment(self, response: str) -> List[Dict[str, str]]:
        """Parse AI response into risk assessment structure."""
        risks = []
        current_risk = {}
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('Risk:'):
                if current_risk:
                    risks.append(current_risk)
                current_risk = {'description': line[5:].strip()}
            elif line.startswith('Impact:') and current_risk:
                current_risk['impact'] = line[7:].strip()
            elif line.startswith('Probability:') and current_risk:
                current_risk['probability'] = line[12:].strip()
            elif line.startswith('Mitigation:') and current_risk:
                current_risk['mitigation'] = line[11:].strip()
            elif line == '---' and current_risk:
                risks.append(current_risk)
                current_risk = {}
        
        if current_risk and len(current_risk) >= 4:
            risks.append(current_risk)
        
        return risks[:5]  # Limit to 5 risks
    
    def _get_fallback_risks(self) -> List[Dict[str, str]]:
        """Fallback risks when AI generation fails."""
        return [
            {
                'description': 'Technical complexity higher than estimated',
                'impact': 'Medium',
                'probability': 'Low',
                'mitigation': 'Break down into smaller tasks, seek technical review'
            },
            {
                'description': 'Dependencies not available on time',
                'impact': 'High',
                'probability': 'Medium',
                'mitigation': 'Identify alternative approaches, communicate early with dependencies'
            }
        ]
    
    async def _ai_generate_technical_considerations(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate technical considerations using AI analysis."""
        try:
            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')
            
            prompt = f"""As a technical architect, provide technical considerations for this {task_type} task: "{title}"

Description: {description}

Provide specific guidance on:
1. Performance considerations
2. Security implications
3. Scalability requirements
4. Integration challenges
5. Maintainability concerns

Keep each consideration concise but specific to this task."""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=600,
                temperature=0.6
            )
            
            return {
                'technical_considerations': response.strip(),
                'performance_requirements': 'Performance requirements will be defined based on AI analysis and system constraints',
                'state_management': 'State management approach will follow AI-recommended patterns for this task type',
                'component_architecture': 'Component architecture will be designed based on AI analysis of existing patterns'
            }
            
        except Exception as e:
            logger.error(f"AI technical considerations generation failed: {e}")
            return {
                'technical_considerations': 'Consider performance, security, maintainability, and scalability requirements.',
                'performance_requirements': 'Identify performance benchmarks and optimization strategies.',
                'state_management': 'Define how application state will be managed and synchronized.',
                'component_architecture': 'Plan component structure for reusability and maintainability.'
            }
    
    def _generate_filename(self, task_id: str, task_type: str, title: str) -> str:
        """Generate filename following TaskHero naming convention."""
        # Get task type abbreviation
        task_prefix = self.task_type_mappings.get(task_type, 'DEV')
        
        # Clean title for filename
        clean_title = title.lower()
        clean_title = ''.join(c if c.isalnum() or c in ' -_' else '' for c in clean_title)
        clean_title = '-'.join(clean_title.split())
        clean_title = clean_title[:50]  # Limit length
        
        return f"{task_id}-{task_prefix}-{clean_title}.md"
    
    def _save_task_file(self, filename: str, content: str) -> Path:
        """Save the task file to the appropriate directory."""
        # Save to todo directory by default
        todo_dir = self.project_root / "mods" / "project_management" / "planning" / "todo"
        todo_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = todo_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    async def create_task_interactive(self) -> Tuple[bool, str, Optional[str]]:
        """Create a task through interactive prompts."""
        try:
            print("\n🚀 Enhanced Task Creation Wizard")
            print("=" * 50)
            
            # Collect basic information
            title = input("📝 Task Title: ").strip()
            if not title:
                return False, "", "Task title is required"
            
            print("\n📋 Task Type:")
            for i, task_type in enumerate(self.task_type_mappings.keys(), 1):
                print(f"  {i}. {task_type}")
            
            task_type_choice = input("Select task type (1-7, default 1): ").strip()
            task_types = list(self.task_type_mappings.keys())
            try:
                task_type = task_types[int(task_type_choice) - 1] if task_type_choice else task_types[0]
            except (ValueError, IndexError):
                task_type = task_types[0]
            
            print(f"\n⚡ Priority:")
            priorities = ["Low", "Medium", "High", "Critical"]
            for i, priority in enumerate(priorities, 1):
                print(f"  {i}. {priority}")
            
            priority_choice = input("Select priority (1-4, default 2): ").strip()
            try:
                priority = priorities[int(priority_choice) - 1] if priority_choice else "Medium"
            except (ValueError, IndexError):
                priority = "Medium"
            
            assigned_to = input("\n👤 Assigned to (default: Developer): ").strip() or "Developer"
            
            due_date = input("\n📅 Due date (YYYY-MM-DD, optional): ").strip()
            if due_date and not self._validate_date(due_date):
                print("⚠️  Invalid date format, using auto-calculated due date")
                due_date = None
            
            tags_input = input("\n🏷️  Tags (comma-separated, optional): ").strip()
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []
            
            dependencies_input = input("\n🔗 Dependencies (comma-separated task IDs, optional): ").strip()
            dependencies = [dep.strip() for dep in dependencies_input.split(',') if dep.strip()] if dependencies_input else []
            
            print(f"\n💪 Effort Estimate:")
            efforts = ["Small (1-8h)", "Medium (1-3d)", "Large (1w+)"]
            for i, effort in enumerate(efforts, 1):
                print(f"  {i}. {effort}")
            
            effort_choice = input("Select effort (1-3, default 2): ").strip()
            effort_map = {"1": "Small", "2": "Medium", "3": "Large"}
            effort_estimate = effort_map.get(effort_choice, "Medium")
            
            print(f"\n📝 Task Description:")
            print("Enter a detailed description (press Enter twice to finish):")
            description_lines = []
            while True:
                line = input()
                if line == "" and description_lines and description_lines[-1] == "":
                    break
                description_lines.append(line)
            
            description = '\n'.join(description_lines).strip()
            
            use_ai = input(f"\n🤖 Use AI enhancement? (y/n, default y): ").strip().lower() != 'n'
            
            print(f"\n📊 Task Summary:")
            print(f"  Title: {title}")
            print(f"  Type: {task_type}")
            print(f"  Priority: {priority}")
            print(f"  Assigned to: {assigned_to}")
            print(f"  Due date: {due_date or 'Auto-calculated'}")
            print(f"  Tags: {', '.join(tags) if tags else 'None'}")
            print(f"  Dependencies: {', '.join(dependencies) if dependencies else 'None'}")
            print(f"  Effort: {effort_estimate}")
            print(f"  AI Enhancement: {'Yes' if use_ai else 'No'}")
            print(f"  Description: {len(description)} characters")
            
            confirm = input(f"\n✅ Create this task? (y/n, default y): ").strip().lower()
            if confirm == 'n':
                return False, "", "Task creation cancelled by user"
            
            # Create the task
            return await self.create_enhanced_task(
                title=title,
                description=description,
                task_type=task_type,
                priority=priority.lower(),
                assigned_to=assigned_to,
                due_date=due_date,
                tags=tags,
                dependencies=dependencies,
                effort_estimate=effort_estimate,
                use_ai_enhancement=use_ai
            )
            
        except KeyboardInterrupt:
            return False, "", "Task creation cancelled by user"
        except Exception as e:
            logger.error(f"Error in interactive task creation: {e}")
            return False, "", str(e)
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date format."""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    # Phase 4C: Interactive Context Selection Methods
    
    def _display_context_selection_interface(self, relevant_context: List[ContextChunk], description: str) -> List[ContextChunk]:
        """
        Phase 4C: Display interactive context selection interface.
        
        Args:
            relevant_context: List of relevant context chunks
            description: Task description for context
            
        Returns:
            List of user-selected context chunks
        """
        if not self.phase4c_config['enable_context_selection'] or not relevant_context:
            return relevant_context[:5]  # Default selection
        
        print(f"\n🔍 Context Discovery Results")
        print("=" * 60)
        print(f"Found {len(relevant_context)} relevant files for your task:")
        print(f"Task: {description[:100]}...")
        print()
        
        # Display context options with preview
        for i, chunk in enumerate(relevant_context[:self.phase4c_config['max_context_items']], 1):
            # Determine selection status (auto-select top 3)
            selected = "☑️" if i <= 3 else "☐"
            
            # File type icon
            file_icons = {
                'python': '🐍',
                'javascript': '📜',
                'markdown': '📝',
                'json': '📋',
                'yaml': '⚙️',
                'template': '📄',
                'config': '🔧',
                'test': '🧪'
            }
            icon = file_icons.get(chunk.file_type, '📄')
            
            print(f"{selected} {i}. {chunk.file_name} ({chunk.relevance_score:.2f} relevance)")
            
            # Content preview
            preview = chunk.text[:self.phase4c_config['context_preview_length']]
            if len(chunk.text) > self.phase4c_config['context_preview_length']:
                preview += "..."
            print(f"   📄 \"{preview}\"")
            
            # File metadata
            print(f"   {icon} {chunk.file_type.title()} | 📊 {len(chunk.text)} chars | 🕒 Line {chunk.start_line}-{chunk.end_line}")
            print()
        
        # User selection interface
        print("📝 Selection Options:")
        print("   • Enter numbers (1,2,3) to select specific files")
        print("   • Type 'all' to include all files")
        print("   • Type 'none' to skip context selection")
        print("   • Type 'top3' for recommended selection (default)")
        print("   • Type 'preview X' to see full content of file X")
        
        while True:
            selection = input(f"\n🎯 Select context files (default: top3): ").strip().lower()
            
            if not selection or selection == 'top3':
                return relevant_context[:3]
            elif selection == 'all':
                return relevant_context[:self.phase4c_config['max_context_items']]
            elif selection == 'none':
                return []
            elif selection.startswith('preview '):
                try:
                    file_num = int(selection.split()[1])
                    if 1 <= file_num <= len(relevant_context):
                        self._show_context_preview(relevant_context[file_num - 1])
                        continue
                    else:
                        print(f"❌ Invalid file number. Choose 1-{len(relevant_context)}")
                        continue
                except (ValueError, IndexError):
                    print("❌ Invalid preview command. Use 'preview X' where X is file number")
                    continue
            else:
                # Parse number selection
                try:
                    selected_indices = []
                    for num_str in selection.replace(',', ' ').split():
                        num = int(num_str)
                        if 1 <= num <= len(relevant_context):
                            selected_indices.append(num - 1)
                        else:
                            print(f"❌ Invalid file number: {num}. Choose 1-{len(relevant_context)}")
                            break
                    else:
                        # All numbers valid
                        if selected_indices:
                            return [relevant_context[i] for i in selected_indices]
                        else:
                            print("❌ No valid file numbers provided")
                            continue
                except ValueError:
                    print("❌ Invalid selection. Use numbers, 'all', 'none', or 'top3'")
                    continue
    
    def _show_context_preview(self, chunk: ContextChunk) -> None:
        """Show full context preview for a specific chunk."""
        print(f"\n📄 Full Preview: {chunk.file_name}")
        print("=" * 60)
        print(f"File Type: {chunk.file_type}")
        print(f"Lines: {chunk.start_line}-{chunk.end_line}")
        print(f"Relevance: {chunk.relevance_score:.3f}")
        print(f"Confidence: {chunk.confidence:.3f}")
        print()
        print("Content:")
        print("-" * 40)
        print(chunk.text)
        print("-" * 40)
        input("\nPress Enter to continue...")
    
    def _explain_context_relevance(self, chunk: ContextChunk, description: str) -> str:
        """
        Phase 4C: Provide explanation for why context is relevant.
        
        Args:
            chunk: Context chunk to explain
            description: Task description
            
        Returns:
            Explanation string
        """
        explanations = []
        
        # File type relevance
        if chunk.file_type == 'python' and 'development' in description.lower():
            explanations.append("Python code file relevant for development task")
        elif chunk.file_type == 'test' and any(word in description.lower() for word in ['test', 'testing', 'bug']):
            explanations.append("Test file relevant for testing/bug fix task")
        elif chunk.file_type == 'markdown' and 'documentation' in description.lower():
            explanations.append("Documentation file relevant for documentation task")
        
        # Content relevance
        common_words = set(description.lower().split()) & set(chunk.text.lower().split())
        if len(common_words) > 3:
            explanations.append(f"Contains {len(common_words)} matching keywords")
        
        # Relevance score explanation
        if chunk.relevance_score > 0.8:
            explanations.append("High semantic similarity to task description")
        elif chunk.relevance_score > 0.6:
            explanations.append("Good semantic similarity to task description")
        else:
            explanations.append("Moderate semantic similarity to task description")
        
        return " • ".join(explanations) if explanations else "General codebase context"
    
    # Phase 4C: Progressive Task Creation Wizard Methods
    
    async def create_task_progressive(self) -> Tuple[bool, str, Optional[str]]:
        """
        Phase 4C: Progressive task creation wizard with multi-step enhancement.
        
        Returns:
            Tuple of (success, task_id, file_path)
        """
        if not self.phase4c_config['enable_progressive_creation']:
            return await self.create_task_interactive()
        
        try:
            # Initialize creation state
            self.creation_state = {
                'step': 0,
                'total_steps': 4,
                'collected_data': {},
                'selected_context': [],
                'ai_enhancements': {},
                'quality_score': 0.0
            }
            
            print(f"\n🚀 Progressive AI Task Creation Wizard")
            print("=" * 60)
            print(f"📋 Multi-step intelligent task creation with AI enhancement")
            print(f"🎯 {self.creation_state['total_steps']} steps to create the perfect task")
            print()
            
            # Step 1: Basic Information Collection
            if not await self._progressive_step_1_basic_info():
                return False, "", "Task creation cancelled in step 1"
            
            # Step 2: Context Discovery and Selection
            if not await self._progressive_step_2_context_selection():
                return False, "", "Task creation cancelled in step 2"
            
            # Step 3: AI Enhancement and Preview
            if not await self._progressive_step_3_ai_enhancement():
                return False, "", "Task creation cancelled in step 3"
            
            # Step 4: Final Review and Creation
            return await self._progressive_step_4_final_creation()
            
        except KeyboardInterrupt:
            return False, "", "Task creation cancelled by user"
        except Exception as e:
            logger.error(f"Error in progressive task creation: {e}")
            return False, "", str(e)
    
    async def _progressive_step_1_basic_info(self) -> bool:
        """Step 1: Collect basic task information."""
        self.creation_state['step'] = 1
        
        print(f"📝 Step 1 of {self.creation_state['total_steps']}: Basic Information")
        print("=" * 50)
        
        # Collect basic information (similar to interactive but with progress tracking)
        title = input("📝 Task Title: ").strip()
        if not title:
            print("❌ Task title is required")
            return False
        
        print("\n📋 Task Type:")
        for i, task_type in enumerate(self.task_type_mappings.keys(), 1):
            print(f"  {i}. {task_type}")
        
        task_type_choice = input("Select task type (1-7, default 1): ").strip()
        task_types = list(self.task_type_mappings.keys())
        try:
            task_type = task_types[int(task_type_choice) - 1] if task_type_choice else task_types[0]
        except (ValueError, IndexError):
            task_type = task_types[0]
        
        print(f"\n⚡ Priority:")
        priorities = ["Low", "Medium", "High", "Critical"]
        for i, priority in enumerate(priorities, 1):
            print(f"  {i}. {priority}")
        
        priority_choice = input("Select priority (1-4, default 2): ").strip()
        try:
            priority = priorities[int(priority_choice) - 1] if priority_choice else "Medium"
        except (ValueError, IndexError):
            priority = "Medium"
        
        assigned_to = input("\n👤 Assigned to (default: Developer): ").strip() or "Developer"
        
        due_date = input("\n📅 Due date (YYYY-MM-DD, optional): ").strip()
        if due_date and not self._validate_date(due_date):
            print("⚠️  Invalid date format, using auto-calculated due date")
            due_date = None
        
        tags_input = input("\n🏷️  Tags (comma-separated, optional): ").strip()
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []
        
        dependencies_input = input("\n🔗 Dependencies (comma-separated task IDs, optional): ").strip()
        dependencies = [dep.strip() for dep in dependencies_input.split(',') if dep.strip()] if dependencies_input else []
        
        print(f"\n💪 Effort Estimate:")
        efforts = ["Small (1-8h)", "Medium (1-3d)", "Large (1w+)"]
        for i, effort in enumerate(efforts, 1):
            print(f"  {i}. {effort}")
        
        effort_choice = input("Select effort (1-3, default 2): ").strip()
        effort_map = {"1": "Small", "2": "Medium", "3": "Large"}
        effort_estimate = effort_map.get(effort_choice, "Medium")
        
        print(f"\n📝 Task Description:")
        print("Enter a detailed description (press Enter twice to finish):")
        description_lines = []
        while True:
            line = input()
            if line == "" and description_lines and description_lines[-1] == "":
                break
            description_lines.append(line)
        
        description = '\n'.join(description_lines).strip()
        
        # Store collected data
        self.creation_state['collected_data'] = {
            'title': title,
            'task_type': task_type,
            'priority': priority,
            'assigned_to': assigned_to,
            'due_date': due_date,
            'tags': tags,
            'dependencies': dependencies,
            'effort_estimate': effort_estimate,
            'description': description
        }
        
        # Show step summary
        print(f"\n✅ Step 1 Complete - Basic Information Collected")
        print(f"   📝 Title: {title}")
        print(f"   📋 Type: {task_type}")
        print(f"   ⚡ Priority: {priority}")
        print(f"   📝 Description: {len(description)} characters")
        
        return True
    
    async def _progressive_step_2_context_selection(self) -> bool:
        """Step 2: Context discovery and user selection."""
        self.creation_state['step'] = 2
        
        print(f"\n🔍 Step 2 of {self.creation_state['total_steps']}: Context Discovery & Selection")
        print("=" * 60)
        
        data = self.creation_state['collected_data']
        description = data['description']
        
        print(f"🔍 Searching for relevant context...")
        print(f"Task: {data['title']}")
        print(f"Type: {data['task_type']}")
        
        # Collect relevant context using semantic search
        relevant_context = self._collect_embeddings_context(description, data)
        
        if relevant_context:
            print(f"✅ Found {len(relevant_context)} relevant files")
            
            # Interactive context selection
            selected_context = self._display_context_selection_interface(relevant_context, description)
            self.creation_state['selected_context'] = selected_context
            
            print(f"\n✅ Step 2 Complete - Context Selected")
            print(f"   📁 Selected {len(selected_context)} files for AI enhancement")
            
            if selected_context:
                print("   🎯 Selected files:")
                for chunk in selected_context[:3]:
                    print(f"     • {chunk.file_name} ({chunk.relevance_score:.2f})")
                if len(selected_context) > 3:
                    print(f"     ... and {len(selected_context) - 3} more")
        else:
            print("⚠️  No relevant context found - proceeding without context")
            self.creation_state['selected_context'] = []
        
        return True
    
    async def _progressive_step_3_ai_enhancement(self) -> bool:
        """Step 3: AI enhancement with real-time feedback."""
        self.creation_state['step'] = 3
        
        print(f"\n🤖 Step 3 of {self.creation_state['total_steps']}: AI Enhancement & Preview")
        print("=" * 60)
        
        data = self.creation_state['collected_data']
        selected_context = self.creation_state['selected_context']
        
        # Initialize AI provider
        print("🚀 Initializing AI provider...")
        ai_available = await self._initialize_ai_provider()
        
        if ai_available:
            print("✅ AI provider ready")
            
            # Show enhancement progress
            print(f"\n🤖 AI is analyzing your task with selected context...")
            
            # Prepare context for AI
            context = self._prepare_base_context(**data)
            optimized_context = self._optimize_context_for_ai(selected_context)
            
            # AI Enhancement with progress indicators
            enhancements = {}
            
            print("🔄 Enhancing description...")
            enhanced_desc = await self._ai_enhance_description(data['description'], context, optimized_context)
            enhancements['description'] = enhanced_desc
            print("✅ Description enhanced")
            
            print("🔄 Generating requirements...")
            requirements = await self._ai_generate_requirements(data['description'], context, optimized_context)
            enhancements['requirements'] = requirements
            print(f"✅ Generated {len(requirements)} requirements")
            
            print("🔄 Generating implementation steps...")
            impl_steps = await self._ai_generate_implementation_steps(data['description'], context, optimized_context)
            enhancements['implementation_steps'] = impl_steps
            print(f"✅ Generated {len(impl_steps)} implementation steps")
            
            print("🔄 Analyzing risks...")
            risks = await self._ai_generate_risk_assessment(data['description'], context, optimized_context)
            enhancements['risks'] = risks
            print(f"✅ Identified {len(risks)} potential risks")
            
            # Calculate quality score
            quality_score = self._calculate_task_quality(data, enhancements)
            self.creation_state['quality_score'] = quality_score
            
            print(f"\n📊 AI Enhancement Complete!")
            print(f"   🎯 Quality Score: {quality_score:.1%}")
            print(f"   📝 Enhanced Description: {len(enhanced_desc)} characters")
            print(f"   📋 Requirements: {len(requirements)} items")
            print(f"   🔧 Implementation Steps: {len(impl_steps)} phases")
            print(f"   ⚠️  Risk Assessment: {len(risks)} risks identified")
            
            self.creation_state['ai_enhancements'] = enhancements
            
            # Preview option
            preview = input(f"\n👀 Preview enhanced content? (y/n, default n): ").strip().lower()
            if preview == 'y':
                self._show_enhancement_preview(enhancements)
            
            # Refinement option
            refine = input(f"\n🔧 Refine any enhancements? (y/n, default n): ").strip().lower()
            if refine == 'y':
                await self._refine_enhancements(enhancements)
            
        else:
            print("⚠️  AI provider not available - using fallback enhancements")
            enhancements = self._get_fallback_enhancements(data)
            self.creation_state['ai_enhancements'] = enhancements
            self.creation_state['quality_score'] = 0.6  # Default quality score
        
        print(f"\n✅ Step 3 Complete - AI Enhancement Applied")
        return True
    
    async def _progressive_step_4_final_creation(self) -> Tuple[bool, str, Optional[str]]:
        """Step 4: Final review and task creation."""
        self.creation_state['step'] = 4
        
        print(f"\n✅ Step 4 of {self.creation_state['total_steps']}: Final Review & Creation")
        print("=" * 60)
        
        data = self.creation_state['collected_data']
        enhancements = self.creation_state['ai_enhancements']
        quality_score = self.creation_state['quality_score']
        
        # Final summary
        print(f"📊 Task Creation Summary:")
        print(f"   📝 Title: {data['title']}")
        print(f"   📋 Type: {data['task_type']}")
        print(f"   ⚡ Priority: {data['priority']}")
        print(f"   👤 Assigned to: {data['assigned_to']}")
        print(f"   📅 Due date: {data['due_date'] or 'Auto-calculated'}")
        print(f"   🏷️  Tags: {', '.join(data['tags']) if data['tags'] else 'None'}")
        print(f"   🔗 Dependencies: {', '.join(data['dependencies']) if data['dependencies'] else 'None'}")
        print(f"   💪 Effort: {data['effort_estimate']}")
        print(f"   📁 Context files: {len(self.creation_state['selected_context'])}")
        print(f"   🤖 AI Enhanced: {'Yes' if enhancements else 'No'}")
        print(f"   🎯 Quality Score: {quality_score:.1%}")
        
        # Quality feedback
        if quality_score >= self.phase4c_config['quality_threshold']:
            print(f"\n🎉 Excellent! Your task meets high quality standards.")
        elif quality_score >= 0.5:
            print(f"\n👍 Good task quality. Consider adding more details for better results.")
        else:
            print(f"\n⚠️  Task quality could be improved. Consider refining the description.")
        
        # Final confirmation
        confirm = input(f"\n✅ Create this enhanced task? (y/n, default y): ").strip().lower()
        if confirm == 'n':
            return False, "", "Task creation cancelled by user"
        
        # Create the task with all enhancements
        return await self.create_enhanced_task(
            title=data['title'],
            description=enhancements.get('description', data['description']),
            task_type=data['task_type'],
            priority=data['priority'].lower(),
            assigned_to=data['assigned_to'],
            due_date=data['due_date'],
            tags=data['tags'],
            dependencies=data['dependencies'],
            effort_estimate=data['effort_estimate'],
            use_ai_enhancement=True,
            selected_context=self.creation_state['selected_context'],
            ai_enhancements=enhancements
        ) 
    
    # Phase 4C: Quality Feedback Loop Methods
    
    def _calculate_task_quality(self, data: Dict[str, Any], enhancements: Dict[str, Any]) -> float:
        """
        Phase 4C: Calculate task quality score based on completeness and AI enhancements.
        
        Args:
            data: Basic task data
            enhancements: AI-generated enhancements
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0
        
        # Basic information completeness (30%)
        if data.get('title') and len(data['title']) > 10:
            score += 0.1
        if data.get('description') and len(data['description']) > 50:
            score += 0.1
        if data.get('tags'):
            score += 0.05
        if data.get('due_date'):
            score += 0.05
        
        # AI enhancement quality (40%)
        if enhancements.get('description') and len(enhancements['description']) > len(data.get('description', '')):
            score += 0.1
        if enhancements.get('requirements') and len(enhancements['requirements']) >= 3:
            score += 0.1
        if enhancements.get('implementation_steps') and len(enhancements['implementation_steps']) >= 3:
            score += 0.1
        if enhancements.get('risks') and len(enhancements['risks']) >= 2:
            score += 0.1
        
        # Context utilization (20%)
        context_count = len(self.creation_state.get('selected_context', []))
        if context_count > 0:
            score += min(0.2, context_count * 0.05)
        
        # Task type appropriateness (10%)
        task_type = data.get('task_type', '').lower()
        description = data.get('description', '').lower()
        if any(keyword in description for keyword in self._get_task_type_keywords(task_type)):
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_task_type_keywords(self, task_type: str) -> List[str]:
        """Get relevant keywords for task type validation."""
        keywords_map = {
            'development': ['implement', 'create', 'build', 'develop', 'code', 'function', 'class', 'api'],
            'bug fix': ['fix', 'bug', 'error', 'issue', 'problem', 'debug', 'resolve'],
            'test case': ['test', 'testing', 'verify', 'validate', 'check', 'assert', 'coverage'],
            'documentation': ['document', 'docs', 'readme', 'guide', 'manual', 'explain', 'describe'],
            'design': ['design', 'ui', 'ux', 'interface', 'layout', 'mockup', 'wireframe'],
            'research': ['research', 'investigate', 'analyze', 'study', 'explore', 'evaluate'],
            'planning': ['plan', 'strategy', 'roadmap', 'timeline', 'schedule', 'organize']
        }
        return keywords_map.get(task_type.lower(), [])
    
    def _show_enhancement_preview(self, enhancements: Dict[str, Any]) -> None:
        """Show preview of AI enhancements."""
        print(f"\n📄 Enhancement Preview")
        print("=" * 50)
        
        if enhancements.get('description'):
            print(f"📝 Enhanced Description:")
            print(f"   {enhancements['description'][:200]}...")
            print()
        
        if enhancements.get('requirements'):
            print(f"📋 Generated Requirements ({len(enhancements['requirements'])}):")
            for i, req in enumerate(enhancements['requirements'][:3], 1):
                print(f"   {i}. {req}")
            if len(enhancements['requirements']) > 3:
                print(f"   ... and {len(enhancements['requirements']) - 3} more")
            print()
        
        if enhancements.get('implementation_steps'):
            print(f"🔧 Implementation Steps ({len(enhancements['implementation_steps'])}):")
            for i, step in enumerate(enhancements['implementation_steps'][:3], 1):
                step_title = step.get('title', f'Step {i}')
                print(f"   {i}. {step_title}")
            if len(enhancements['implementation_steps']) > 3:
                print(f"   ... and {len(enhancements['implementation_steps']) - 3} more")
            print()
        
        if enhancements.get('risks'):
            print(f"⚠️  Risk Assessment ({len(enhancements['risks'])}):")
            for i, risk in enumerate(enhancements['risks'][:2], 1):
                risk_desc = risk.get('description', f'Risk {i}')
                print(f"   {i}. {risk_desc}")
            if len(enhancements['risks']) > 2:
                print(f"   ... and {len(enhancements['risks']) - 2} more")
        
        input("\nPress Enter to continue...")
    
    async def _refine_enhancements(self, enhancements: Dict[str, Any]) -> None:
        """Allow user to refine AI enhancements."""
        print(f"\n🔧 Enhancement Refinement")
        print("=" * 50)
        print("Which enhancement would you like to refine?")
        print("  1. Description")
        print("  2. Requirements")
        print("  3. Implementation Steps")
        print("  4. Risk Assessment")
        print("  0. Skip refinement")
        
        choice = input("Select option (1-4, default 0): ").strip()
        
        if choice == '1' and enhancements.get('description'):
            print(f"\nCurrent description:")
            print(f"{enhancements['description']}")
            
            new_desc = input(f"\nEnter refined description (or press Enter to keep current): ").strip()
            if new_desc:
                enhancements['description'] = new_desc
                print("✅ Description updated")
        
        elif choice == '2' and enhancements.get('requirements'):
            print(f"\nCurrent requirements:")
            for i, req in enumerate(enhancements['requirements'], 1):
                print(f"  {i}. {req}")
            
            add_req = input(f"\nAdd additional requirement (or press Enter to skip): ").strip()
            if add_req:
                enhancements['requirements'].append(add_req)
                print("✅ Requirement added")
        
        elif choice == '3' and enhancements.get('implementation_steps'):
            print(f"\nCurrent implementation steps:")
            for i, step in enumerate(enhancements['implementation_steps'], 1):
                step_title = step.get('title', f'Step {i}')
                print(f"  {i}. {step_title}")
            
            print("Refinement options not implemented yet")
        
        elif choice == '4' and enhancements.get('risks'):
            print(f"\nCurrent risks:")
            for i, risk in enumerate(enhancements['risks'], 1):
                risk_desc = risk.get('description', f'Risk {i}')
                print(f"  {i}. {risk_desc}")
            
            print("Risk refinement options not implemented yet")
    
    def _get_fallback_enhancements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback enhancements when AI is not available."""
        task_type = data.get('task_type', 'Development')
        
        return {
            'description': data.get('description', ''),
            'requirements': self._get_fallback_requirements(task_type),
            'implementation_steps': self._get_fallback_implementation_steps(data.get('due_date')),
            'risks': self._get_fallback_risks()
        }
    
    def _collect_quality_feedback(self, task_id: str, quality_score: float) -> None:
        """
        Phase 4C: Collect user feedback for quality improvement.
        
        Args:
            task_id: Created task ID
            quality_score: Calculated quality score
        """
        if not self.phase4c_config['enable_quality_feedback']:
            return
        
        print(f"\n📊 Quality Feedback Collection")
        print("=" * 50)
        print(f"Task {task_id} created with quality score: {quality_score:.1%}")
        
        feedback = input(f"Rate your satisfaction (1-5, optional): ").strip()
        if feedback and feedback.isdigit() and 1 <= int(feedback) <= 5:
            satisfaction = int(feedback)
            
            # Store feedback for future improvements
            feedback_data = {
                'task_id': task_id,
                'quality_score': quality_score,
                'user_satisfaction': satisfaction,
                'timestamp': datetime.now().isoformat()
            }
            
            self._store_quality_feedback(feedback_data)
            print(f"✅ Thank you for your feedback!")
        
        # Suggestions for improvement
        if quality_score < self.phase4c_config['quality_threshold']:
            print(f"\n💡 Suggestions for better tasks:")
            print(f"   • Provide more detailed descriptions")
            print(f"   • Include specific requirements")
            print(f"   • Add relevant tags and dependencies")
            print(f"   • Select more relevant context files")
    
    def _store_quality_feedback(self, feedback_data: Dict[str, Any]) -> None:
        """Store quality feedback for analysis."""
        try:
            feedback_dir = self.project_root / "mods" / "project_management" / "feedback"
            feedback_dir.mkdir(parents=True, exist_ok=True)
            
            feedback_file = feedback_dir / "quality_feedback.json"
            
            # Load existing feedback
            existing_feedback = []
            if feedback_file.exists():
                try:
                    with open(feedback_file, 'r', encoding='utf-8') as f:
                        existing_feedback = json.load(f)
                except json.JSONDecodeError:
                    existing_feedback = []
            
            # Add new feedback
            existing_feedback.append(feedback_data)
            
            # Keep only last 100 feedback entries
            if len(existing_feedback) > 100:
                existing_feedback = existing_feedback[-100:]
            
            # Save feedback
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(existing_feedback, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Failed to store quality feedback: {e}")
    
    def _get_quality_insights(self) -> Dict[str, Any]:
        """Get insights from collected quality feedback."""
        try:
            feedback_file = self.project_root / "mods" / "project_management" / "feedback" / "quality_feedback.json"
            
            if not feedback_file.exists():
                return {}
            
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedback_data = json.load(f)
            
            if not feedback_data:
                return {}
            
            # Calculate insights
            total_tasks = len(feedback_data)
            avg_quality = sum(f['quality_score'] for f in feedback_data) / total_tasks
            avg_satisfaction = sum(f.get('user_satisfaction', 3) for f in feedback_data) / total_tasks
            
            high_quality_tasks = sum(1 for f in feedback_data if f['quality_score'] >= 0.7)
            high_satisfaction_tasks = sum(1 for f in feedback_data if f.get('user_satisfaction', 3) >= 4)
            
            return {
                'total_tasks': total_tasks,
                'average_quality_score': avg_quality,
                'average_satisfaction': avg_satisfaction,
                'high_quality_percentage': high_quality_tasks / total_tasks * 100,
                'high_satisfaction_percentage': high_satisfaction_tasks / total_tasks * 100
            }
            
        except Exception as e:
            logger.warning(f"Failed to get quality insights: {e}")
            return {} 