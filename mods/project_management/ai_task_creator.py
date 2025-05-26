"""
AI-Enhanced Task Creator Module

Integrates the enhanced task template with AI capabilities to provide intelligent,
comprehensive task creation with context-aware content generation.

Phase 4B: Real AI Integration - Enhanced with actual LLM provider integration
"""

import os
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio

from .template_engine import TemplateEngine
from .task_manager import TaskManager, TaskPriority, TaskStatus
from .semantic_search import SemanticSearchEngine, ContextChunk, SearchResult
from .context_analyzer import ContextAnalyzer, ProjectContext
from .context_analyzer_enhanced import EnhancedContextAnalyzer, EnhancedProjectContext, CodeAnalysis
from .template_optimizer import TemplateOptimizer
from .task_quality_validator import TaskQualityValidator
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
        self.enhanced_context_analyzer = EnhancedContextAnalyzer(str(self.project_root))
        self.template_optimizer = TemplateOptimizer()
        self.quality_validator = TaskQualityValidator()

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
                # First try to use the configured task provider from environment
                import os
                preferred_provider = os.getenv('AI_TASK_PROVIDER', '').lower()

                if preferred_provider:
                    try:
                        # Try to create the preferred provider
                        self.ai_provider = await self.provider_factory.create_provider(preferred_provider)
                        if self.ai_provider and await self.ai_provider.check_health():
                            self.ai_available = True
                            logger.info(f"AI provider initialized (preferred): {preferred_provider}")
                            return True
                        else:
                            logger.warning(f"Preferred provider {preferred_provider} failed health check, falling back")
                    except Exception as e:
                        logger.warning(f"Failed to initialize preferred provider {preferred_provider}: {e}")

                # Fallback to best available provider
                best_provider = await self.provider_factory.get_best_available_provider()
                if best_provider:
                    self.ai_provider = await self.provider_factory.create_provider(best_provider)
                    self.ai_available = True
                    logger.info(f"AI provider initialized (fallback): {best_provider}")
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

                # TASK-061: Add visual elements and flow diagrams to context
                if ai_enhancements.get('visual_elements'):
                    visual_elements = ai_enhancements['visual_elements']
                    if visual_elements.get('mermaid_diagram'):
                        mermaid_diagram = visual_elements['mermaid_diagram']
                        context['flow_diagram'] = f"```mermaid\n{mermaid_diagram.get('content', '')}\n```"
                        context['flow_description'] = mermaid_diagram.get('description', 'Task flow diagram')
                    if visual_elements.get('ascii_art') and visual_elements['ascii_art'].get('content'):
                        context['ascii_layout'] = visual_elements['ascii_art']['content']

                if ai_enhancements.get('flow_diagrams'):
                    flow_diagrams = ai_enhancements['flow_diagrams']
                    if flow_diagrams:
                        # Use the first flow diagram as the main diagram
                        main_diagram = flow_diagrams[0]
                        if main_diagram.get('content'):
                            # Check if content already has mermaid wrapper
                            content = main_diagram['content']
                            if not content.startswith('```mermaid'):
                                content = f"```mermaid\n{content}\n```"
                            context['flow_diagram'] = content
                            context['flow_description'] = main_diagram.get('title', 'Task flow diagram')

                        # Add additional diagrams if available
                        if len(flow_diagrams) > 1:
                            context['additional_diagrams'] = flow_diagrams[1:]

                # Add Phase 4C metadata
                context['phase4c_enhanced'] = True
                context['selected_context_count'] = len(selected_context) if selected_context else 0

            elif use_ai_enhancement:
                # Traditional AI enhancement
                context = await self._enhance_with_ai(context, description)

            # TASK-044: Always apply template optimization to filter out placeholders and irrelevant sections
            # But preserve AI-generated flow diagrams if they exist
            ai_flow_diagram = context.get('flow_diagram')
            ai_flow_description = context.get('flow_description')

            context = self.template_optimizer.optimize_template_context(
                context, task_type, description
            )

            # TASK-044: Generate task-specific flow diagram only if AI didn't generate one
            if not ai_flow_diagram:
                flow_diagram_context = self.template_optimizer.generate_task_specific_flow_diagram(
                    task_type, description, context
                )
                context.update(flow_diagram_context)
            else:
                # Preserve AI-generated flow diagram and ensure it's shown
                context['flow_diagram'] = ai_flow_diagram
                context['flow_description'] = ai_flow_description
                context['show_flow_diagram'] = True

            # Generate task content using enhanced template
            task_content = self.template_engine.render_template(
                self.enhanced_template,
                context
            )

            # Validate task quality
            quality_result = self.quality_validator.validate_task_quality(task_content, context)

            # Add quality metadata to context for logging
            context['quality_score'] = quality_result['overall_score']
            context['quality_level'] = quality_result['quality_level']
            context['quality_recommendations'] = quality_result['recommendations']

            # Generate filename following naming convention
            filename = self._generate_filename(task_id, task_type, title)

            # Save the task file
            file_path = self._save_task_file(filename, task_content)

            # Phase 4C: Collect quality feedback if enhancements were used
            if ai_enhancements and self.creation_state.get('quality_score'):
                self._collect_quality_feedback(task_id, self.creation_state['quality_score'])

            # Log quality results
            self._log_quality_results(task_id, quality_result)

            logger.info(f"Enhanced task created: {task_id} at {file_path} (Quality: {quality_result['quality_level']}, Score: {quality_result['overall_score']:.2f})")
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
            'show_naming_convention': False,  # TASK-044: Hide naming convention (for AI prompts only)
            'show_metadata_legend': False,    # TASK-044: Hide metadata legend (for AI prompts only)
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

            # Step 1: Enhanced context analysis with proper separation of user input and context
            enhanced_context = self.enhanced_context_analyzer.analyze_task_context_enhanced(
                description, task_type, specific_files=None
            )

            # Step 2: Collect relevant context from embeddings (existing functionality)
            relevant_context = self._collect_embeddings_context(description, context)

            # Step 3: Filter and optimize context for AI processing
            optimized_context = self._optimize_context_for_ai(relevant_context)

            # Phase 4B: Real AI Integration with TASK-044 enhancements
            enhanced_context_dict = context.copy()

            # TASK-044: Enhanced context integration with proper separation
            if enhanced_context.relevant_files:
                # Store contextual information separately (not merged into description)
                enhanced_context_dict['contextual_files'] = [
                    f.file_path for f in enhanced_context.relevant_files[:5]
                ]
                enhanced_context_dict['contextual_recommendations'] = [
                    rec.description for rec in enhanced_context.contextual_recommendations[:5]
                ]

                # Generate implementation analysis based on primary file
                if enhanced_context.primary_file_analysis:
                    enhanced_context_dict['current_implementation'] = self._generate_enhanced_implementation_analysis(
                        enhanced_context.primary_file_analysis, enhanced_context.user_description
                    )

                # Keep user description unchanged, add contextual insights separately
                enhanced_context_dict['detailed_description'] = enhanced_context.user_description
                enhanced_context_dict['contextual_insights'] = self._generate_contextual_insights(enhanced_context)

            # Step 4: Use real AI to enhance different aspects with context
            if description and self.ai_available:
                try:
                    # Enhanced description with AI and file context (keep user description primary)
                    if not enhanced_context_dict.get('detailed_description'):
                        enhanced_context_dict['detailed_description'] = await self._ai_enhance_description_with_context(
                            enhanced_context.user_description, context, enhanced_context
                        )

                    # AI-generated requirements with file context
                    enhanced_context_dict['functional_requirements_list'] = await self._ai_generate_requirements_with_context(
                        enhanced_context.user_description, enhanced_context_dict, enhanced_context
                    )

                    # AI-generated benefits
                    enhanced_context_dict['benefits_list'] = await self._ai_generate_benefits(
                        enhanced_context.user_description, enhanced_context_dict, optimized_context
                    )

                    # AI-generated implementation steps with specific file references
                    enhanced_context_dict['implementation_steps'] = await self._ai_generate_implementation_steps_with_context(
                        enhanced_context.user_description, enhanced_context_dict, enhanced_context
                    )

                    # AI-generated risk assessment
                    enhanced_context_dict['risks'] = await self._ai_generate_risk_assessment(
                        enhanced_context.user_description, enhanced_context_dict, optimized_context
                    )

                    # AI-generated technical considerations
                    tech_considerations = await self._ai_generate_technical_considerations_with_context(
                        enhanced_context.user_description, enhanced_context_dict, enhanced_context
                    )
                    enhanced_context_dict.update(tech_considerations)

                except Exception as ai_error:
                    logger.warning(f"AI enhancement partially failed: {ai_error}")
                    # Fall back to basic enhancement for failed components

            # TASK-044: Template optimization - filter irrelevant sections and customize content
            enhanced_context_dict = self.template_optimizer.optimize_template_context(
                enhanced_context_dict, task_type, description
            )

            # TASK-044: Generate task-specific flow diagram
            flow_diagram_context = self.template_optimizer.generate_task_specific_flow_diagram(
                task_type, description, enhanced_context_dict
            )
            enhanced_context_dict.update(flow_diagram_context)

            # Step 5: Add AI metadata
            enhanced_context_dict['ai_context_used'] = len(relevant_context)
            enhanced_context_dict['ai_enhancement_applied'] = self.ai_available
            enhanced_context_dict['ai_provider_used'] = self.ai_provider.get_name() if self.ai_provider else None
            enhanced_context_dict['task044_enhanced'] = True  # Mark as TASK-044 enhanced
            enhanced_context_dict['context_files_analyzed'] = len(enhanced_context.relevant_files) if enhanced_context.relevant_files else 0

            # TASK-044: Validate template quality
            quality_issues = self.template_optimizer.validate_optimized_template(enhanced_context_dict)
            if quality_issues:
                logger.warning(f"Template quality issues detected: {quality_issues}")
                enhanced_context_dict['quality_issues'] = quality_issues

            return enhanced_context_dict

        except Exception as e:
            logger.warning(f"AI enhancement failed, using default context: {e}")
            return context

    def _generate_enhanced_implementation_analysis(self, primary_file: 'CodeAnalysis', user_description: str) -> str:
        """Generate enhanced implementation analysis based on primary file analysis."""
        try:
            analysis_parts = []

            if primary_file:
                analysis_parts.append("**Current Implementation Analysis:**")
                analysis_parts.append(f"**Primary File**: `{primary_file.file_path}` ({primary_file.language})")

                # Add specific features found
                if primary_file.key_features:
                    analysis_parts.append("\n**Key Features Identified:**")
                    for feature in primary_file.key_features:
                        analysis_parts.append(f"- {feature}")

                # Add functions/methods found
                if primary_file.functions:
                    analysis_parts.append(f"\n**Functions Found**: {', '.join(primary_file.functions[:5])}")
                    if len(primary_file.functions) > 5:
                        analysis_parts.append(f" (and {len(primary_file.functions) - 5} more)")

                # Add configuration items for config files
                if primary_file.configuration_items:
                    analysis_parts.append(f"\n**Configuration Items**: {len(primary_file.configuration_items)} items found")

                # Add complexity assessment
                if primary_file.complexity_score > 0.5:
                    analysis_parts.append(f"\n**Complexity**: Moderate to high ({primary_file.complexity_score:.2f})")
                else:
                    analysis_parts.append(f"\n**Complexity**: Low to moderate ({primary_file.complexity_score:.2f})")

                # Add documentation quality
                analysis_parts.append(f"**Documentation Quality**: {primary_file.documentation_quality.title()}")

            return '\n'.join(analysis_parts) if analysis_parts else "Current implementation will be analyzed during planning phase"

        except Exception as e:
            logger.warning(f"Error generating enhanced implementation analysis: {e}")
            return "Current implementation will be analyzed during planning phase"

    def _generate_contextual_insights(self, enhanced_context: 'EnhancedProjectContext') -> str:
        """Generate contextual insights from enhanced project context."""
        try:
            insights = []

            if enhanced_context.architectural_insights:
                insights.append("**Architectural Insights:**")
                for insight in enhanced_context.architectural_insights:
                    insights.append(f"- {insight}")

            if enhanced_context.implementation_patterns:
                insights.append("\n**Implementation Patterns:**")
                for pattern_type, files in enhanced_context.implementation_patterns.items():
                    if files:
                        insights.append(f"- **{pattern_type.replace('_', ' ').title()}**: {len(files)} files")

            if enhanced_context.technology_stack:
                insights.append("\n**Technology Stack:**")
                for component, tech in enhanced_context.technology_stack.items():
                    insights.append(f"- **{component.title()}**: {tech}")

            return '\n'.join(insights) if insights else "No specific contextual insights available"

        except Exception as e:
            logger.warning(f"Error generating contextual insights: {e}")
            return "No specific contextual insights available"

    async def _ai_enhance_description_with_context(self, user_description: str, context: Dict[str, Any], enhanced_context: 'EnhancedProjectContext') -> str:
        """Enhance description with AI while preserving user's original intent."""
        try:
            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            # Build context information for AI (but keep user description primary)
            context_info = ""
            if enhanced_context.primary_file_analysis:
                primary_file = enhanced_context.primary_file_analysis
                context_info += f"\n\nPrimary file being worked on: {primary_file.file_path}"
                context_info += f"\nFile type: {primary_file.language} ({primary_file.file_type})"
                if primary_file.key_features:
                    context_info += f"\nKey features: {', '.join(primary_file.key_features[:3])}"

            if enhanced_context.contextual_recommendations:
                context_info += "\n\nContextual recommendations:"
                for rec in enhanced_context.contextual_recommendations[:3]:
                    context_info += f"\n- {rec.description}"

            prompt = f"""You are enhancing a task description while preserving the user's original intent and requirements.

User's original description: {user_description}

Task type: {task_type}
Task title: {title}

{context_info}

Please enhance the description by:
1. Keeping the user's original requirements and intent unchanged
2. Adding technical context based on the identified files
3. Providing specific implementation guidance
4. Maintaining clarity and actionability

The enhanced description should start with the user's original intent and add contextual details that help with implementation."""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=self.ai_config['max_response_tokens'],
                temperature=self.ai_config['temperature']
            )

            return response.strip()

        except Exception as e:
            logger.error(f"AI description enhancement with context failed: {e}")
            return user_description  # Return original description on failure

    async def _ai_generate_requirements_with_context(self, user_description: str, context: Dict[str, Any], enhanced_context: 'EnhancedProjectContext') -> List[str]:
        """Generate requirements with enhanced context awareness."""
        try:
            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            # Build context for AI
            context_info = ""
            if enhanced_context.primary_file_analysis:
                primary_file = enhanced_context.primary_file_analysis
                context_info += f"\n\nPrimary file: {primary_file.file_path}"
                if primary_file.functions:
                    context_info += f"\nExisting functions: {', '.join(primary_file.functions[:5])}"
                if primary_file.configuration_items:
                    context_info += f"\nConfiguration items: {len(primary_file.configuration_items)} found"

            prompt = f"""Generate specific, testable functional requirements for this task:

Task: {title}
Description: {user_description}
Task Type: {task_type}

{context_info}

Requirements should be:
- Specific and measurable
- Technically detailed
- Actionable for developers
- Testable/verifiable

Format as a numbered list. Each requirement should start with "The system must" or "The script must".

Example format:
1. The system must validate user input before processing
2. The script must create backup files before making changes
3. The system must provide clear error messages for invalid inputs

Generate 5-8 specific requirements:"""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=800,
                temperature=0.6
            )

            # Parse and structure requirements
            requirements = self._parse_requirements_response(response)
            return requirements if requirements else self._generate_fallback_requirements(user_description, context)

        except Exception as e:
            logger.error(f"AI requirements generation with context failed: {e}")
            return self._generate_fallback_requirements(user_description, context)

    async def _ai_generate_implementation_steps_with_context(self, user_description: str, context: Dict[str, Any], enhanced_context: 'EnhancedProjectContext') -> List[Dict[str, Any]]:
        """Generate implementation steps with enhanced context awareness."""
        try:
            task_type = context.get('task_type', 'Development')
            due_date = context.get('due_date')

            # Build specific context from primary file
            context_info = ""
            if enhanced_context.primary_file_analysis:
                primary_file = enhanced_context.primary_file_analysis
                context_info += f"\n\nPrimary file to modify: {primary_file.file_path}"
                context_info += f"\nFile type: {primary_file.language}"

                if primary_file.key_features:
                    context_info += f"\nExisting features: {', '.join(primary_file.key_features)}"

                if primary_file.functions:
                    context_info += f"\nExisting functions: {', '.join(primary_file.functions[:5])}"

                if primary_file.specific_patterns:
                    context_info += f"\nCode patterns: {', '.join(primary_file.specific_patterns)}"

            # Get task-specific step templates
            step_templates = self._get_step_templates_for_task_type(task_type)

            prompt = f"""Generate detailed implementation steps for this {task_type} task:

Task: {context.get('title', 'Task')}
Description: {user_description}
Task Type: {task_type}

{context_info}

Requirements:
- Create 4-5 implementation phases with specific sub-steps
- Each phase should have clear deliverables and estimated timeline
- Include specific technical details based on the codebase context
- Make steps actionable for developers
- Consider existing code patterns and architecture

Template for each phase:
Phase X: [Clear Phase Name] - Estimated: [Duration]
- [Specific actionable step with technical details]
- [Specific actionable step with technical details]
- [Specific actionable step with technical details]
Deliverables: [Clear deliverable items]

Generate 4-5 implementation phases:"""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=1200,
                temperature=0.6
            )

            # Parse response into structured format
            steps = self._parse_implementation_steps_response(response, due_date)
            return steps if steps else self._generate_fallback_implementation_steps_enhanced(user_description, context)

        except Exception as e:
            logger.error(f"AI implementation steps generation with context failed: {e}")
            return self._generate_fallback_implementation_steps_enhanced(user_description, context)

    async def _ai_generate_technical_considerations_with_context(self, user_description: str, context: Dict[str, Any], enhanced_context: 'EnhancedProjectContext') -> Dict[str, str]:
        """Generate technical considerations with enhanced context awareness."""
        try:
            task_type = context.get('task_type', 'Development')

            # Build context from file analysis
            context_info = ""
            if enhanced_context.primary_file_analysis:
                primary_file = enhanced_context.primary_file_analysis
                context_info += f"\n\nFile analysis context:"
                context_info += f"\n- Primary file: {primary_file.file_path} ({primary_file.language})"
                context_info += f"\n- Complexity score: {primary_file.complexity_score:.2f}"
                context_info += f"\n- Documentation quality: {primary_file.documentation_quality}"

                if primary_file.key_features:
                    context_info += f"\n- Key features: {', '.join(primary_file.key_features)}"

            if enhanced_context.technology_stack:
                context_info += f"\n\nTechnology stack: {enhanced_context.technology_stack}"

            prompt = f"""Provide specific technical considerations for this {task_type} task based on code analysis.

User description: {user_description}

{context_info}

Provide specific guidance on:
1. Implementation approach based on existing code patterns
2. Integration considerations with current architecture
3. Performance implications
4. Maintenance and testing considerations

Keep recommendations specific to the analyzed codebase."""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=600,
                temperature=0.6
            )

            return {
                'technical_considerations': response.strip(),
                'performance_requirements': 'Performance requirements based on existing code patterns and complexity analysis',
                'state_management': 'State management following identified patterns in the codebase',
                'component_architecture': 'Component architecture aligned with existing file structure and patterns'
            }

        except Exception as e:
            logger.error(f"AI technical considerations generation with context failed: {e}")
            return {
                'technical_considerations': 'Consider performance, security, maintainability, and scalability requirements.',
                'performance_requirements': 'Identify performance benchmarks and optimization strategies.',
                'state_management': 'Define how application state will be managed and synchronized.',
                'component_architecture': 'Plan component structure for reusability and maintainability.'
            }

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
        Collect relevant context using enhanced semantic search with intelligent query processing.

        Args:
            description: Task description to search for
            context: Current task context

        Returns:
            List of relevant context chunks
        """
        try:
            task_type = context.get('task_type', 'Development')

            # Phase 2: Enhanced query construction with multiple strategies
            search_queries = self._construct_intelligent_search_queries(description, task_type)

            # Use multi-query search for comprehensive results
            if hasattr(self.semantic_search, 'search_multi_query'):
                # Use the new multi-query search capability
                primary_query = search_queries[0]
                search_result = self.semantic_search.search_multi_query(
                    query=primary_query,
                    max_results=12,  # Slightly increased for better coverage
                    file_types=None
                )
                logger.info(f"Multi-query semantic search found {len(search_result.chunks)} relevant chunks in {search_result.search_time:.3f}s")
            else:
                # Fallback to enhanced single query search
                all_chunks = []
                chunk_ids = set()

                for query in search_queries[:3]:  # Use top 3 queries
                    search_result = self.semantic_search.search(
                        query=query,
                        max_results=8,
                        file_types=None
                    )

                    # Deduplicate chunks
                    for chunk in search_result.chunks:
                        chunk_id = f"{chunk.file_path}:{chunk.start_line}:{chunk.end_line}"
                        if chunk_id not in chunk_ids:
                            chunk_ids.add(chunk_id)
                            all_chunks.append(chunk)

                # Sort by relevance and limit results
                all_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
                search_result.chunks = all_chunks[:10]

                logger.info(f"Enhanced semantic search found {len(search_result.chunks)} relevant chunks from {len(search_queries)} queries")

            return search_result.chunks

        except Exception as e:
            logger.error(f"Error collecting semantic context: {e}")
            return []

    def _construct_intelligent_search_queries(self, description: str, task_type: str) -> List[str]:
        """
        Construct multiple intelligent search queries for comprehensive context retrieval.

        Args:
            description: Task description
            task_type: Type of task

        Returns:
            List of optimized search queries
        """
        queries = []

        # Query 1: Enhanced primary query with task type integration
        primary_query = self._create_enhanced_primary_query(description, task_type)
        queries.append(primary_query)

        # Query 2: Technical implementation focused query
        if task_type.lower() in ['development', 'bug fix', 'enhancement']:
            tech_query = self._create_technical_query(description, task_type)
            if tech_query:
                queries.append(tech_query)

        # Query 3: Configuration and setup focused query
        if any(keyword in description.lower() for keyword in ['setup', 'install', 'configure', 'deploy', 'build']):
            config_query = self._create_configuration_query(description)
            if config_query:
                queries.append(config_query)

        # Query 4: Domain-specific query based on detected patterns
        domain_query = self._create_domain_specific_query(description, task_type)
        if domain_query:
            queries.append(domain_query)

        # Query 5: Simplified core terms query
        core_query = self._create_core_terms_query(description)
        if core_query:
            queries.append(core_query)

        logger.debug(f"Constructed {len(queries)} intelligent search queries for: '{description}'")
        return queries

    def _create_enhanced_primary_query(self, description: str, task_type: str) -> str:
        """Create enhanced primary search query."""
        # Extract key terms and enhance with task type context
        key_terms = self._extract_enhanced_search_terms(description, task_type)

        # Combine with task type for context
        task_context = self._get_task_type_context_terms(task_type)

        enhanced_terms = key_terms + task_context
        return ' '.join(enhanced_terms[:8])  # Limit to 8 terms for focus

    def _create_technical_query(self, description: str, task_type: str) -> str:
        """Create technical implementation focused query."""
        technical_terms = []
        desc_lower = description.lower()

        # Extract technical action words
        technical_actions = ['implement', 'develop', 'create', 'build', 'enhance', 'optimize', 'refactor', 'fix']
        for action in technical_actions:
            if action in desc_lower:
                technical_terms.append(action)

        # Add technical context based on description patterns
        if any(term in desc_lower for term in ['api', 'endpoint', 'service']):
            technical_terms.extend(['api', 'endpoint', 'service', 'interface'])
        if any(term in desc_lower for term in ['database', 'data', 'storage']):
            technical_terms.extend(['database', 'data', 'storage', 'persistence'])
        if any(term in desc_lower for term in ['auth', 'login', 'security']):
            technical_terms.extend(['authentication', 'authorization', 'security'])
        if any(term in desc_lower for term in ['ui', 'interface', 'frontend']):
            technical_terms.extend(['interface', 'frontend', 'ui', 'component'])

        # Add programming language context
        technical_terms.extend(['python', 'javascript', 'implementation', 'code'])

        if technical_terms:
            return ' '.join(list(set(technical_terms))[:6])
        return None

    def _create_configuration_query(self, description: str) -> str:
        """Create configuration and setup focused query."""
        config_terms = []
        desc_lower = description.lower()

        # Extract configuration-related terms
        if 'setup' in desc_lower:
            config_terms.extend(['setup', 'installation', 'configuration', 'initialize'])
        if 'install' in desc_lower:
            config_terms.extend(['install', 'installation', 'setup', 'dependencies'])
        if 'configure' in desc_lower:
            config_terms.extend(['configure', 'configuration', 'settings', 'parameters'])
        if 'deploy' in desc_lower:
            config_terms.extend(['deploy', 'deployment', 'release', 'distribution'])
        if 'build' in desc_lower:
            config_terms.extend(['build', 'compilation', 'package', 'bundle'])

        # Add file type context
        config_terms.extend(['config', 'json', 'yaml', 'script', 'batch'])

        if config_terms:
            return ' '.join(list(set(config_terms))[:6])
        return None

    def _create_domain_specific_query(self, description: str, task_type: str) -> str:
        """Create domain-specific query based on detected patterns."""
        desc_lower = description.lower()
        domain_terms = []

        # Web development domain
        if any(term in desc_lower for term in ['web', 'http', 'server', 'client', 'browser']):
            domain_terms.extend(['web', 'http', 'server', 'client', 'request', 'response'])

        # Testing domain
        elif any(term in desc_lower for term in ['test', 'testing', 'spec', 'validation']):
            domain_terms.extend(['test', 'testing', 'validation', 'verification', 'spec', 'unittest'])

        # Documentation domain
        elif any(term in desc_lower for term in ['document', 'docs', 'guide', 'manual']):
            domain_terms.extend(['documentation', 'guide', 'manual', 'reference', 'readme'])

        # DevOps domain
        elif any(term in desc_lower for term in ['docker', 'container', 'ci', 'cd', 'pipeline']):
            domain_terms.extend(['docker', 'container', 'deployment', 'pipeline', 'automation'])

        if domain_terms:
            return ' '.join(domain_terms[:5])
        return None

    def _create_core_terms_query(self, description: str) -> str:
        """Create simplified query with core terms only."""
        # Extract meaningful terms (longer than 3 characters, not common words)
        words = description.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'these', 'those', 'will', 'should', 'would', 'could'}

        core_terms = [word for word in words if len(word) > 3 and word not in stop_words]

        if len(core_terms) >= 2:
            return ' '.join(core_terms[:4])
        return None

    def _get_task_type_context_terms(self, task_type: str) -> List[str]:
        """Get context terms based on task type."""
        task_type_lower = task_type.lower()

        context_map = {
            'development': ['development', 'implementation', 'code', 'programming'],
            'bug fix': ['fix', 'debug', 'error', 'issue', 'problem'],
            'enhancement': ['enhance', 'improve', 'optimize', 'upgrade'],
            'documentation': ['documentation', 'guide', 'manual', 'reference'],
            'testing': ['test', 'testing', 'validation', 'verification'],
            'design': ['design', 'ui', 'interface', 'layout'],
            'research': ['research', 'analysis', 'investigation', 'study']
        }

        for task_key, terms in context_map.items():
            if task_key in task_type_lower:
                return terms[:2]  # Return top 2 context terms

        return ['development', 'implementation']  # Default context

    def _optimize_context_for_ai(self, relevant_context: List[ContextChunk]) -> List[Dict[str, Any]]:
        """
        Phase 3: Advanced context optimization with dynamic thresholds and intelligent balancing.

        Args:
            relevant_context: List of context chunks from semantic search

        Returns:
            Optimized context list for AI processing
        """
        try:
            if not relevant_context:
                return []

            # Phase 3: Dynamic relevance threshold calculation
            dynamic_threshold = self._calculate_dynamic_relevance_threshold(relevant_context)

            # Phase 3: Advanced context filtering with quality assessment
            filtered_context = self._apply_advanced_context_filtering(relevant_context, dynamic_threshold)

            # Phase 3: Intelligent context balancing
            balanced_context = self._apply_intelligent_context_balancing(filtered_context)

            # Phase 3: Advanced token management with smart truncation
            optimized_context = self._apply_advanced_token_management(balanced_context)

            # Phase 3: Context quality validation
            quality_score = self._validate_context_quality(optimized_context)

            logger.info(f"Phase 3 context optimization: {len(optimized_context)} chunks, quality: {quality_score:.2f}")
            return optimized_context

        except Exception as e:
            logger.error(f"Error in Phase 3 context optimization: {e}")
            return []

    def _calculate_dynamic_relevance_threshold(self, context_chunks: List[ContextChunk]) -> float:
        """
        Calculate dynamic relevance threshold based on context quality distribution.

        Args:
            context_chunks: List of context chunks

        Returns:
            Dynamic relevance threshold
        """
        if not context_chunks:
            return self.ai_config['context_selection_threshold']

        # Calculate relevance score statistics
        scores = [chunk.relevance_score for chunk in context_chunks]
        scores.sort(reverse=True)

        # Calculate percentiles
        total_chunks = len(scores)
        if total_chunks < 3:
            return min(scores) if scores else 0.5

        # Use adaptive threshold based on score distribution
        p75 = scores[int(total_chunks * 0.25)]  # 75th percentile
        p50 = scores[int(total_chunks * 0.5)]   # 50th percentile (median)
        p25 = scores[int(total_chunks * 0.75)]  # 25th percentile

        # Calculate score variance to determine threshold strategy
        score_variance = sum((score - p50) ** 2 for score in scores) / total_chunks

        # Adaptive threshold logic
        if score_variance > 0.1:  # High variance - be more selective
            threshold = max(p75, 0.7)
        elif score_variance > 0.05:  # Medium variance - balanced approach
            threshold = max(p50, 0.6)
        else:  # Low variance - be more inclusive
            threshold = max(p25, 0.4)

        # Ensure minimum quality
        threshold = max(threshold, 0.3)

        logger.debug(f"Dynamic threshold: {threshold:.3f} (variance: {score_variance:.3f})")
        return threshold

    def _apply_advanced_context_filtering(self, context_chunks: List[ContextChunk], threshold: float) -> List[ContextChunk]:
        """
        Apply advanced context filtering with quality assessment.

        Args:
            context_chunks: List of context chunks
            threshold: Dynamic relevance threshold

        Returns:
            Filtered context chunks
        """
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

        logger.debug(f"Advanced filtering: {len(context_chunks)} -> {len(filtered_chunks)} chunks")
        return filtered_chunks

    def _assess_chunk_quality(self, chunk: ContextChunk) -> float:
        """
        Assess the quality of a context chunk.

        Args:
            chunk: Context chunk to assess

        Returns:
            Quality score (0.0 to 1.0)
        """
        score = 0.0
        text = chunk.text.strip()

        # Length assessment
        if 50 <= len(text) <= 2000:
            score += 0.3
        elif 20 <= len(text) < 50:
            score += 0.1
        elif len(text) > 2000:
            score += 0.2

        # Content richness assessment
        lines = text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        if len(non_empty_lines) >= 3:
            score += 0.2

        # Technical content indicators
        technical_indicators = [
            'def ', 'class ', 'function', 'import ', 'from ', 'config',
            'setup', 'install', 'deploy', 'api', 'database', 'auth'
        ]

        technical_count = sum(1 for indicator in technical_indicators if indicator in text.lower())
        score += min(technical_count * 0.1, 0.3)

        # Code structure indicators
        if any(indicator in text for indicator in ['(', ')', '{', '}', '[', ']']):
            score += 0.1

        # Documentation quality indicators
        if chunk.file_type in ['documentation', 'markdown']:
            if any(indicator in text.lower() for indicator in ['example', 'usage', 'how to', 'guide']):
                score += 0.1

        return min(score, 1.0)

    def _is_duplicate_content(self, chunk: ContextChunk, existing_chunks: List[ContextChunk]) -> bool:
        """
        Check if chunk content is duplicate or very similar to existing chunks.

        Args:
            chunk: Chunk to check
            existing_chunks: List of already selected chunks

        Returns:
            True if duplicate content detected
        """
        chunk_text = chunk.text.strip().lower()

        for existing in existing_chunks:
            existing_text = existing.text.strip().lower()

            # Exact duplicate check
            if chunk_text == existing_text:
                return True

            # High similarity check (simple approach)
            if len(chunk_text) > 100 and len(existing_text) > 100:
                # Check for substantial overlap
                chunk_words = set(chunk_text.split())
                existing_words = set(existing_text.split())

                if len(chunk_words) > 0 and len(existing_words) > 0:
                    overlap = len(chunk_words & existing_words)
                    similarity = overlap / min(len(chunk_words), len(existing_words))

                    if similarity > 0.8:  # 80% word overlap
                        return True

        return False

    def _apply_intelligent_context_balancing(self, filtered_chunks: List[ContextChunk]) -> List[ContextChunk]:
        """
        Apply intelligent context balancing to ensure optimal file type distribution.

        Args:
            filtered_chunks: Filtered context chunks

        Returns:
            Balanced context chunks
        """
        if not filtered_chunks:
            return []

        # Sort by relevance score first
        filtered_chunks.sort(key=lambda x: x.relevance_score, reverse=True)

        # Analyze current distribution
        file_type_distribution = {}
        for chunk in filtered_chunks:
            file_type_distribution[chunk.file_type] = file_type_distribution.get(chunk.file_type, 0) + 1

        # Define optimal distribution targets (can be adjusted based on query intent)
        optimal_distribution = {
            'python': 0.3,
            'javascript': 0.2,
            'config': 0.15,
            'script': 0.1,
            'documentation': 0.15,
            'markdown': 0.1
        }

        # Calculate target counts
        total_target_chunks = min(len(filtered_chunks), 12)  # Target 12 chunks max
        target_counts = {}
        for file_type, ratio in optimal_distribution.items():
            target_counts[file_type] = int(total_target_chunks * ratio)

        # Select chunks according to balanced distribution
        balanced_chunks = []
        type_counts = {}

        # First pass: ensure minimum representation of each important type
        for chunk in filtered_chunks:
            file_type = chunk.file_type
            current_count = type_counts.get(file_type, 0)
            target_count = target_counts.get(file_type, 1)

            if current_count < target_count:
                balanced_chunks.append(chunk)
                type_counts[file_type] = current_count + 1

                if len(balanced_chunks) >= total_target_chunks:
                    break

        # Second pass: fill remaining slots with highest relevance chunks
        remaining_slots = total_target_chunks - len(balanced_chunks)
        if remaining_slots > 0:
            used_chunk_ids = {id(chunk) for chunk in balanced_chunks}
            remaining_chunks = [chunk for chunk in filtered_chunks if id(chunk) not in used_chunk_ids]

            balanced_chunks.extend(remaining_chunks[:remaining_slots])

        # Final sort by relevance
        balanced_chunks.sort(key=lambda x: x.relevance_score, reverse=True)

        logger.debug(f"Context balancing: {len(filtered_chunks)} -> {len(balanced_chunks)} chunks")
        return balanced_chunks

    def _apply_advanced_token_management(self, balanced_chunks: List[ContextChunk]) -> List[Dict[str, Any]]:
        """
        Apply advanced token management with smart truncation and optimization.

        Args:
            balanced_chunks: Balanced context chunks

        Returns:
            Token-optimized context list
        """
        if not balanced_chunks:
            return []

        max_context_tokens = self.ai_config['max_context_tokens']
        optimized_context = []
        total_tokens = 0

        # Reserve tokens for essential metadata
        metadata_tokens = 200  # Reserve for file names, types, etc.
        available_tokens = max_context_tokens - metadata_tokens

        for chunk in balanced_chunks:
            # Calculate chunk tokens with improved estimation
            chunk_tokens = self._estimate_chunk_tokens(chunk)

            if total_tokens + chunk_tokens <= available_tokens:
                # Chunk fits completely
                optimized_chunk = self._format_chunk_for_ai(chunk, truncate=False)
                optimized_context.append(optimized_chunk)
                total_tokens += chunk_tokens
            else:
                # Try smart truncation
                remaining_tokens = available_tokens - total_tokens
                if remaining_tokens > 100:  # Minimum viable chunk size
                    truncated_chunk = self._smart_truncate_chunk(chunk, remaining_tokens)
                    if truncated_chunk:
                        optimized_context.append(truncated_chunk)
                        total_tokens += remaining_tokens
                break

        # Add context summary for AI understanding
        context_summary = self._generate_context_summary(optimized_context)

        logger.info(f"Token management: {len(optimized_context)} chunks, ~{total_tokens} tokens")
        return optimized_context

    def _estimate_chunk_tokens(self, chunk: ContextChunk) -> int:
        """
        Improved token estimation for context chunks.

        Args:
            chunk: Context chunk

        Returns:
            Estimated token count
        """
        # More accurate token estimation
        text = chunk.text

        # Base estimation: ~4 characters per token for English text
        base_tokens = len(text) // 4

        # Adjust for code vs text
        if chunk.file_type in ['python', 'javascript', 'config']:
            # Code tends to have more tokens per character due to symbols
            base_tokens = int(base_tokens * 1.2)
        elif chunk.file_type in ['documentation', 'markdown']:
            # Natural language is more efficient
            base_tokens = int(base_tokens * 0.9)

        # Add metadata tokens
        metadata_tokens = 20  # For file name, type, line numbers

        return base_tokens + metadata_tokens

    def _format_chunk_for_ai(self, chunk: ContextChunk, truncate: bool = False) -> Dict[str, Any]:
        """
        Format chunk for AI processing with enhanced metadata.

        Args:
            chunk: Context chunk
            truncate: Whether to truncate content

        Returns:
            Formatted chunk dictionary
        """
        content = chunk.text
        if truncate and len(content) > 1500:
            content = content[:1500] + "...(truncated)"

        return {
            'file_name': chunk.file_name,
            'file_type': chunk.file_type,
            'content': content,
            'relevance_score': chunk.relevance_score,
            'quality_score': getattr(chunk, 'quality_score', 0.0),
            'line_range': f"{chunk.start_line}-{chunk.end_line}",
            'chunk_type': chunk.chunk_type,
            'confidence': chunk.confidence
        }

    def _smart_truncate_chunk(self, chunk: ContextChunk, max_tokens: int) -> Optional[Dict[str, Any]]:
        """
        Smart truncation that preserves important content.

        Args:
            chunk: Context chunk to truncate
            max_tokens: Maximum tokens available

        Returns:
            Truncated chunk or None if not viable
        """
        if max_tokens < 50:  # Not enough space for meaningful content
            return None

        # Calculate max characters (rough estimation)
        max_chars = max_tokens * 3  # Conservative estimate

        text = chunk.text
        if len(text) <= max_chars:
            return self._format_chunk_for_ai(chunk, truncate=False)

        # Smart truncation strategies
        lines = text.split('\n')

        # Strategy 1: Keep complete lines that fit
        truncated_lines = []
        char_count = 0

        for line in lines:
            if char_count + len(line) + 1 <= max_chars - 20:  # Reserve for truncation marker
                truncated_lines.append(line)
                char_count += len(line) + 1
            else:
                break

        if truncated_lines:
            truncated_text = '\n'.join(truncated_lines) + "\n...(truncated)"

            # Create truncated chunk
            truncated_chunk = ContextChunk(
                text=truncated_text,
                file_path=chunk.file_path,
                chunk_type=chunk.chunk_type,
                start_line=chunk.start_line,
                end_line=chunk.start_line + len(truncated_lines),
                confidence=chunk.confidence * 0.8,  # Reduce confidence for truncated content
                file_name=chunk.file_name,
                file_type=chunk.file_type
            )
            truncated_chunk.relevance_score = chunk.relevance_score

            return self._format_chunk_for_ai(truncated_chunk, truncate=False)

        return None

    def _generate_context_summary(self, optimized_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the optimized context for AI understanding.

        Args:
            optimized_context: List of optimized context chunks

        Returns:
            Context summary
        """
        if not optimized_context:
            return {}

        file_types = {}
        total_relevance = 0.0
        files_included = set()

        for chunk in optimized_context:
            file_type = chunk['file_type']
            file_types[file_type] = file_types.get(file_type, 0) + 1
            total_relevance += chunk['relevance_score']
            files_included.add(chunk['file_name'])

        return {
            'total_chunks': len(optimized_context),
            'file_types_distribution': file_types,
            'average_relevance': total_relevance / len(optimized_context),
            'files_included': list(files_included),
            'context_quality': 'high' if total_relevance / len(optimized_context) > 0.7 else 'medium'
        }

    def _validate_context_quality(self, optimized_context: List[Dict[str, Any]]) -> float:
        """
        Validate the quality of the optimized context.

        Args:
            optimized_context: Optimized context chunks

        Returns:
            Quality score (0.0 to 1.0)
        """
        if not optimized_context:
            return 0.0

        # Calculate quality metrics
        total_relevance = sum(chunk['relevance_score'] for chunk in optimized_context)
        avg_relevance = total_relevance / len(optimized_context)

        # File type diversity score
        file_types = set(chunk['file_type'] for chunk in optimized_context)
        diversity_score = min(len(file_types) / 5.0, 1.0)  # Normalize to max 5 types

        # Content quality score
        quality_scores = [chunk.get('quality_score', 0.5) for chunk in optimized_context]
        avg_quality = sum(quality_scores) / len(quality_scores)

        # Combined quality score
        quality_score = (avg_relevance * 0.5) + (diversity_score * 0.3) + (avg_quality * 0.2)

        return min(quality_score, 1.0)

    def _extract_search_terms(self, description: str, task_type: str) -> List[str]:
        """Extract search terms from description and task type (legacy method)."""
        # This method is kept for backward compatibility
        # New intelligent query processing uses _extract_enhanced_search_terms
        return self._extract_enhanced_search_terms(description, task_type)

    def _extract_enhanced_search_terms(self, description: str, task_type: str) -> List[str]:
        """Enhanced search term extraction with intelligent processing."""
        import re

        # Clean and tokenize description
        words = re.findall(r'\b\w+\b', description.lower())

        # Enhanced stop words list
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'we', 'need', 'want', 'like', 'make', 'get', 'use', 'also', 'now',
            'then', 'here', 'there', 'when', 'where', 'how', 'what', 'why', 'who', 'which'
        }

        # Extract meaningful terms with enhanced filtering
        meaningful_words = []
        for word in words:
            if (len(word) > 3 and
                word not in stop_words and
                not word.isdigit() and
                not word.startswith('http')):
                meaningful_words.append(word)

        # Enhanced task type specific terms with technical focus
        enhanced_task_terms = {
            'development': [
                'implement', 'develop', 'code', 'build', 'create', 'program',
                'function', 'class', 'method', 'module', 'component', 'library',
                'algorithm', 'logic', 'structure', 'architecture'
            ],
            'bug fix': [
                'fix', 'debug', 'resolve', 'repair', 'troubleshoot', 'patch',
                'error', 'bug', 'issue', 'problem', 'exception', 'failure',
                'crash', 'malfunction', 'defect'
            ],
            'enhancement': [
                'enhance', 'improve', 'optimize', 'upgrade', 'refactor', 'modernize',
                'performance', 'efficiency', 'speed', 'quality', 'usability'
            ],
            'testing': [
                'test', 'testing', 'validation', 'verification', 'spec', 'unittest',
                'integration', 'coverage', 'assert', 'verify', 'check', 'quality'
            ],
            'documentation': [
                'document', 'documentation', 'guide', 'manual', 'readme', 'reference',
                'tutorial', 'example', 'explanation', 'description'
            ],
            'design': [
                'design', 'interface', 'layout', 'component', 'style', 'theme',
                'ui', 'ux', 'frontend', 'visual', 'appearance'
            ],
            'research': [
                'research', 'analyze', 'investigate', 'study', 'explore', 'evaluate',
                'assessment', 'analysis', 'examination', 'review'
            ]
        }

        # Add task-specific terms
        task_type_lower = task_type.lower()
        for task_key, terms in enhanced_task_terms.items():
            if task_key in task_type_lower:
                meaningful_words.extend(terms[:5])  # Add top 5 task-specific terms
                break

        # Add technical domain terms based on description content
        self._add_technical_domain_terms(meaningful_words, description)

        # Remove duplicates and prioritize by relevance
        unique_terms = list(set(meaningful_words))

        # Sort by technical relevance and length
        unique_terms.sort(key=lambda x: (self._calculate_term_relevance(x, description, task_type), len(x)), reverse=True)

        return unique_terms[:12]  # Increased to 12 for better coverage

    def _add_technical_domain_terms(self, terms: List[str], description: str):
        """Add technical domain-specific terms based on description content."""
        desc_lower = description.lower()

        # Web development terms
        if any(keyword in desc_lower for keyword in ['web', 'http', 'server', 'client', 'browser', 'frontend', 'backend']):
            terms.extend(['web', 'http', 'server', 'client', 'request', 'response', 'endpoint'])

        # Database terms
        if any(keyword in desc_lower for keyword in ['database', 'data', 'storage', 'query', 'sql']):
            terms.extend(['database', 'data', 'storage', 'query', 'persistence', 'model'])

        # Authentication terms
        if any(keyword in desc_lower for keyword in ['auth', 'login', 'security', 'access', 'permission']):
            terms.extend(['authentication', 'authorization', 'security', 'access', 'permission'])

        # API terms
        if any(keyword in desc_lower for keyword in ['api', 'endpoint', 'service', 'rest']):
            terms.extend(['api', 'endpoint', 'service', 'interface', 'rest'])

        # Configuration terms
        if any(keyword in desc_lower for keyword in ['config', 'setup', 'install', 'deploy']):
            terms.extend(['configuration', 'setup', 'installation', 'deployment'])

        # Testing terms
        if any(keyword in desc_lower for keyword in ['test', 'spec', 'unit', 'integration']):
            terms.extend(['testing', 'validation', 'verification', 'spec'])

    def _calculate_term_relevance(self, term: str, description: str, task_type: str) -> float:
        """Calculate relevance score for a search term."""
        score = 0.0
        desc_lower = description.lower()
        task_lower = task_type.lower()

        # Exact match in description
        if term in desc_lower:
            score += 1.0

        # Partial match bonus
        if any(term in word for word in desc_lower.split()):
            score += 0.5

        # Technical term bonus
        technical_terms = {
            'implement', 'develop', 'code', 'build', 'create', 'setup', 'install',
            'configure', 'deploy', 'api', 'database', 'auth', 'test', 'fix'
        }
        if term in technical_terms:
            score += 0.8

        # Task type alignment bonus
        if term in task_lower:
            score += 0.6

        # Length bonus for specific terms
        if len(term) > 6:
            score += 0.3

        return score

    def _calculate_relevance(self, embedding_data: Dict[str, Any], search_terms: List[str], task_type: str) -> float:
        """Calculate relevance score for an embedding file with Phase 4 exact match prioritization."""
        try:
            score = 0.0

            # Get file path and content
            file_path = embedding_data.get('path', '').lower()
            chunks = embedding_data.get('chunks', [])
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path

            # Extract original case file name for exact matching
            original_file_path = embedding_data.get('path', '')
            original_file_name = original_file_path.split('/')[-1] if '/' in original_file_path else original_file_path

            # Determine file type using enhanced classification
            file_type = self._determine_enhanced_file_type(file_name)

            # PHASE 4: Exact Match Prioritization
            exact_match_boost = self._calculate_exact_match_boost(
                original_file_name, file_name, file_path, search_terms, task_type
            )
            score += exact_match_boost

            # File path relevance (reduced weight due to exact match prioritization)
            for term in search_terms:
                if term in file_path:
                    score += 0.1  # Reduced from 0.15 to make room for exact matches

            # Content relevance
            content_text = ""
            for chunk in chunks:
                if isinstance(chunk, dict):
                    content_text += chunk.get('text', '') + " "
                elif isinstance(chunk, str):
                    content_text += chunk + " "

            content_text = content_text.lower()

            # Search term matches in content (maintained weight)
            for term in search_terms:
                if term in content_text:
                    score += 0.15

            # Enhanced file type scoring based on task type
            score += self._calculate_file_type_relevance(file_type, task_type, search_terms)

            # Context diversity bonus (encourage variety)
            if file_type in ['config', 'script', 'setup']:
                score += 0.1  # Boost for often-overlooked but important files

            # PHASE 4: Root directory boost for setup-related queries
            root_boost = self._calculate_root_directory_boost(file_path, search_terms, task_type)
            score += root_boost

            # Phase 4 Debug Logging (can be removed in production)
            if exact_match_boost > 0.5 or root_boost > 0.2:
                logger.debug(f"Phase 4 High Relevance: {original_file_name} - "
                           f"Exact: {exact_match_boost:.3f}, Root: {root_boost:.3f}, "
                           f"Total: {score:.3f}")

            return min(score, 1.0)  # Cap at 1.0

        except Exception as e:
            logger.warning(f"Error calculating relevance: {e}")
            return 0.0

    def _determine_enhanced_file_type(self, file_name: str) -> str:
        """Enhanced file type determination aligned with semantic search."""
        file_name_lower = file_name.lower()

        # Python files
        if file_name_lower.endswith(('.py', '.pyx', '.pyi')):
            return 'python'
        # JavaScript/TypeScript files
        elif file_name_lower.endswith(('.js', '.ts', '.jsx', '.tsx', '.mjs')):
            return 'javascript'
        # Configuration files
        elif file_name_lower.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf')):
            return 'config'
        # Script files
        elif file_name_lower.endswith(('.bat', '.cmd', '.sh', '.ps1', '.bash')):
            return 'script'
        # Setup files
        elif any(keyword in file_name_lower for keyword in ['setup', 'install', 'deploy']):
            return 'setup'
        # Test files
        elif any(keyword in file_name_lower for keyword in ['test', 'spec', 'unittest']):
            return 'test'
        # Task files
        elif 'task' in file_name_lower and file_name_lower.endswith('.md'):
            return 'task'
        # Documentation
        elif file_name_lower.endswith(('.md', '.txt', '.rst')) or any(keyword in file_name_lower for keyword in ['doc', 'readme', 'guide']):
            return 'documentation'
        else:
            return 'other'

    def _calculate_file_type_relevance(self, file_type: str, task_type: str, search_terms: List[str]) -> float:
        """Calculate file type relevance with Phase 4 enhanced scoring."""
        relevance = 0.0
        task_type_lower = task_type.lower()
        search_terms_str = ' '.join(search_terms).lower()

        # Define file type groups
        code_files = ['python', 'javascript']
        config_files = ['config', 'setup', 'script']

        if task_type_lower == 'development':
            if file_type in code_files:
                relevance += 0.2   # Slightly reduced to make room for exact matches
            elif file_type in config_files:
                relevance += 0.25  # Increased: config/setup files are crucial for development
            elif file_type == 'test':
                relevance += 0.15  # Boost for test files
            elif file_type == 'task':
                relevance += 0.05  # Reduced: task docs less important than actual code
            elif file_type == 'documentation':
                relevance += 0.08  # Still valuable for context

        elif task_type_lower in ['bug', 'bug fix']:
            if file_type in code_files:
                relevance += 0.3   # High relevance for bug fixes
            elif file_type == 'test':
                relevance += 0.25  # Tests are crucial for bug fixes
            elif file_type == 'task':
                relevance += 0.1   # Reduced from 0.15

        elif task_type_lower in ['documentation', 'doc']:
            if file_type == 'documentation':
                relevance += 0.3
            elif file_type == 'task':
                relevance += 0.2
            elif file_type in code_files:
                relevance += 0.15  # Code context is still valuable

        else:  # General tasks
            if file_type == 'task':
                relevance += 0.15  # Reduced from 0.2
            elif file_type in code_files:
                relevance += 0.15
            elif file_type in config_files:
                relevance += 0.2   # Increased: config files often more relevant than task docs

        # Enhanced keyword-based bonuses with Phase 4 improvements
        if 'setup' in search_terms_str or 'install' in search_terms_str:
            if file_type in ['setup', 'config', 'script']:
                relevance += 0.2   # Increased from 0.15

        # Windows/Linux specific bonuses
        if 'windows' in search_terms_str and file_type == 'script':
            relevance += 0.15
        if 'linux' in search_terms_str and file_type == 'script':
            relevance += 0.15

        # PowerShell specific bonus
        if 'powershell' in search_terms_str or 'ps1' in search_terms_str:
            if file_type == 'script':
                relevance += 0.2

        return relevance

    def _calculate_exact_match_boost(self, original_file_name: str, file_name: str, file_path: str,
                                   search_terms: List[str], task_type: str) -> float:
        """Phase 4: Calculate massive relevance boost for exact filename matches."""
        boost = 0.0
        search_terms_str = ' '.join(search_terms).lower()
        file_name_lower = file_name.lower()

        # Exact filename matches get massive boost
        for term in search_terms:
            term_lower = term.lower()

            # Perfect filename match (e.g., "setup_windows.bat" for "setup windows")
            if term_lower in file_name_lower:
                # Check if it's a compound match (multiple terms in filename)
                term_parts = term_lower.split('_')
                if len(term_parts) > 1:
                    matches = sum(1 for part in term_parts if part in file_name_lower)
                    if matches == len(term_parts):
                        boost += 0.8  # Massive boost for perfect compound matches
                    elif matches > len(term_parts) / 2:
                        boost += 0.6  # High boost for partial compound matches
                else:
                    boost += 0.5  # High boost for single term matches

        # Special handling for setup-related queries
        if any(setup_term in search_terms_str for setup_term in ['setup', 'install', 'configure']):
            setup_files = ['setup_windows.bat', 'setup_windows.ps1', 'setup_linux.sh', 'setup.py', 'install.bat']
            if any(setup_file in file_name_lower for setup_file in setup_files):
                boost += 0.9  # Maximum boost for setup files in setup queries

        # File extension prioritization based on query context
        extension_boost = self._calculate_extension_priority_boost(file_name_lower, search_terms_str, task_type)
        boost += extension_boost

        # Exact case-sensitive filename matches (even higher priority)
        for term in search_terms:
            if term in original_file_name:  # Case-sensitive match
                boost += 0.3

        return min(boost, 0.95)  # Cap to leave room for other factors

    def _calculate_extension_priority_boost(self, file_name: str, search_terms_str: str, task_type: str) -> float:
        """Calculate boost based on file extension relevance to query context."""
        boost = 0.0

        # Script-related queries should prioritize script files
        if any(script_term in search_terms_str for script_term in ['script', 'setup', 'install', 'run', 'launch']):
            if file_name.endswith(('.bat', '.cmd', '.ps1', '.sh', '.bash')):
                boost += 0.4  # High boost for script files in script queries
            elif file_name.endswith('.py') and any(py_term in search_terms_str for py_term in ['setup', 'install']):
                boost += 0.3  # Boost for Python setup files

        # Configuration queries should prioritize config files
        if any(config_term in search_terms_str for config_term in ['config', 'settings', 'env', 'environment']):
            if file_name.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.env')):
                boost += 0.4

        # Development queries should prioritize code files
        if task_type.lower() == 'development' or any(dev_term in search_terms_str for dev_term in ['code', 'implement', 'develop']):
            if file_name.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                boost += 0.2

        # Windows-specific queries should prioritize Windows files
        if 'windows' in search_terms_str:
            if file_name.endswith(('.bat', '.cmd', '.ps1')):
                boost += 0.5  # Very high boost for Windows scripts in Windows queries

        # Linux-specific queries should prioritize Linux files
        if 'linux' in search_terms_str:
            if file_name.endswith(('.sh', '.bash')):
                boost += 0.5  # Very high boost for Linux scripts in Linux queries

        return boost

    def _calculate_root_directory_boost(self, file_path: str, search_terms: List[str], task_type: str) -> float:
        """Calculate boost for files in root directory for setup-related queries."""
        boost = 0.0
        search_terms_str = ' '.join(search_terms).lower()

        # Check if file is in root directory (no subdirectories)
        is_root_file = '/' not in file_path.strip('/')

        if is_root_file:
            # Setup-related queries get boost for root files
            if any(setup_term in search_terms_str for setup_term in ['setup', 'install', 'configure', 'run', 'launch']):
                boost += 0.3  # Significant boost for root setup files

            # Main application files get boost
            main_files = ['app.py', 'main.py', 'index.py', 'run.py', 'start.py']
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path
            if file_name.lower() in main_files:
                boost += 0.25  # Boost for main application files

            # Configuration files in root get boost
            if any(config_term in search_terms_str for config_term in ['config', 'env', 'settings']):
                config_files = ['.env', '.env.example', 'config.json', 'settings.json']
                if file_name.lower() in config_files:
                    boost += 0.3

        return boost

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

            print("🔄 Generating visual elements...")
            visual_elements = await self._ai_generate_visual_elements(data['description'], context, optimized_context)
            enhancements['visual_elements'] = visual_elements
            print(f"✅ Generated visual elements (Mermaid diagrams, ASCII art)")

            print("🔄 Creating flow diagrams...")
            flow_diagrams = await self._ai_generate_flow_diagrams(data['description'], context, optimized_context)
            enhancements['flow_diagrams'] = flow_diagrams
            print(f"✅ Created {len(flow_diagrams)} flow diagrams")

            print("🔄 Optimizing template structure...")
            template_optimization = await self._ai_optimize_template_structure(data, enhancements)
            enhancements['template_optimization'] = template_optimization
            print("✅ Template structure optimized")

            # Calculate quality score
            quality_score = self._calculate_task_quality(data, enhancements)
            self.creation_state['quality_score'] = quality_score

            print(f"\n📊 AI Enhancement Complete!")
            print(f"   🎯 Quality Score: {quality_score:.1%}")
            print(f"   📝 Enhanced Description: {len(enhanced_desc)} characters")
            print(f"   📋 Requirements: {len(requirements)} items")
            print(f"   🔧 Implementation Steps: {len(impl_steps)} phases")
            print(f"   ⚠️  Risk Assessment: {len(risks)} risks identified")
            print(f"   🎨 Visual Elements: Mermaid diagrams, ASCII art generated")
            print(f"   📊 Flow Diagrams: {len(flow_diagrams)} diagrams created")
            print(f"   🏗️  Template Structure: Optimized for quality")

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

    async def _ai_generate_visual_elements(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate visual elements including Mermaid diagrams and ASCII art."""
        try:
            # Import enhanced visual generator
            from .enhanced_visual_generator import EnhancedVisualGenerator, VisualContext

            visual_generator = EnhancedVisualGenerator()

            # Create visual context
            visual_context = VisualContext(
                task_type=context.get('task_type', 'DEV'),
                title=context.get('title', 'Task'),
                description=description,
                domain=self._extract_domain_from_description(description),
                complexity=context.get('complexity', 'medium'),
                user_personas=context.get('user_personas', []),
                process_steps=context.get('process_steps', []),
                system_components=context.get('system_components', []),
                data_entities=context.get('data_entities', []),
                user_interactions=context.get('user_interactions', [])
            )

            # Generate visual elements
            mermaid_result = visual_generator.generate_task_diagram(visual_context)
            ascii_result = visual_generator.generate_ascii_art(visual_context)
            config_result = visual_generator.generate_interactive_config(visual_context)

            return {
                'mermaid_diagram': mermaid_result,
                'ascii_art': ascii_result,
                'interactive_config': config_result,
                'visual_consistency': visual_generator.validate_visual_consistency([mermaid_result, ascii_result])
            }

        except Exception as e:
            logger.error(f"Visual elements generation failed: {e}")
            return {
                'mermaid_diagram': {'content': 'flowchart TD\n    A[Start] --> B[End]', 'type': 'flowchart'},
                'ascii_art': {'content': 'Visual elements placeholder', 'type': 'generic'},
                'interactive_config': {'sections': []},
                'visual_consistency': {'consistency_score': 0.8}
            }

    async def _ai_generate_flow_diagrams(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate task-specific flow diagrams."""
        try:
            # Import mermaid generator
            from .mermaid_generator import MermaidDiagramGenerator

            mermaid_generator = MermaidDiagramGenerator()
            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            # Generate main flow diagram
            main_diagram = mermaid_generator.generate_task_diagram(task_type, title, description, context)

            # Generate ASCII layout if UI-related
            ascii_layout = mermaid_generator.generate_ascii_layout(task_type, description)

            diagrams = [
                {
                    'type': 'main_flow',
                    'title': 'Task Flow Diagram',
                    'content': main_diagram
                }
            ]

            if ascii_layout and ascii_layout != mermaid_generator._generate_generic_layout():
                diagrams.append({
                    'type': 'ascii_layout',
                    'title': 'UI Layout',
                    'content': ascii_layout
                })

            return diagrams

        except Exception as e:
            logger.error(f"Flow diagrams generation failed: {e}")
            return [
                {
                    'type': 'main_flow',
                    'title': 'Task Flow Diagram',
                    'content': '```mermaid\nflowchart TD\n    A[Start Task] --> B[Complete Task]\n```'
                }
            ]

    async def _ai_optimize_template_structure(self, data: Dict[str, Any], enhancements: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize template structure for better quality and completeness."""
        try:
            # Import enhanced template engine
            from .enhanced_template_engine import EnhancedTemplateEngine

            template_engine = EnhancedTemplateEngine()

            # Validate template completeness
            task_type = data.get('task_type', 'Development')
            description = enhancements.get('description', data.get('description', ''))

            # Generate optimized context
            optimized_context = {
                'task_id': data.get('task_id', 'TASK-XXX'),
                'title': data.get('title', ''),
                'description': description,
                'task_type': task_type,
                'priority': data.get('priority', 'Medium'),
                'complexity': 'medium',
                'user_personas': ['Users', 'Developers', 'Administrators'],
                'system_components': self._extract_system_components(description),
                'user_interactions': self._extract_user_interactions(description),
                'process_steps': self._extract_process_steps(description)
            }

            # Generate enhanced task content
            enhanced_task = template_engine.generate_enhanced_task(
                task_type=task_type,
                title=data.get('title', ''),
                description=description,
                context=optimized_context
            )

            return {
                'quality_score': enhanced_task.get('quality_score', 8.0),
                'sections_generated': list(enhanced_task.get('sections', {}).keys()),
                'template_validation': template_engine.validate_template_completeness(
                    enhanced_task.get('markdown', ''), task_type
                ),
                'optimization_applied': True
            }

        except Exception as e:
            logger.error(f"Template optimization failed: {e}")
            return {
                'quality_score': 7.0,
                'sections_generated': ['metadata', 'overview', 'implementation'],
                'template_validation': {'valid': True, 'completeness_score': 75.0},
                'optimization_applied': False
            }

    def _extract_domain_from_description(self, description: str) -> str:
        """Extract domain from task description for context-aware generation."""
        description_lower = description.lower()

        # Domain mapping based on keywords
        domain_keywords = {
            'web-development': ['web', 'frontend', 'backend', 'html', 'css', 'javascript', 'react', 'vue', 'angular'],
            'data-processing': ['data', 'database', 'sql', 'analytics', 'etl', 'pipeline', 'processing'],
            'ui-design': ['ui', 'ux', 'design', 'interface', 'user experience', 'mockup', 'wireframe'],
            'api-development': ['api', 'rest', 'graphql', 'endpoint', 'service', 'microservice'],
            'testing': ['test', 'testing', 'qa', 'quality assurance', 'automation', 'unit test'],
            'devops': ['deploy', 'deployment', 'ci/cd', 'docker', 'kubernetes', 'infrastructure'],
            'mobile-development': ['mobile', 'ios', 'android', 'app', 'react native', 'flutter'],
            'security': ['security', 'authentication', 'authorization', 'encryption', 'vulnerability']
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return domain

        return 'general'  # Default domain

    def _extract_system_components(self, description: str) -> List[str]:
        """Extract system components from description."""
        components = []
        description_lower = description.lower()

        # Common system components
        component_keywords = {
            'database': ['database', 'db', 'sql', 'mysql', 'postgresql', 'mongodb'],
            'api': ['api', 'rest', 'graphql', 'endpoint', 'service'],
            'frontend': ['frontend', 'ui', 'interface', 'web', 'react', 'vue', 'angular'],
            'backend': ['backend', 'server', 'service', 'microservice'],
            'cache': ['cache', 'redis', 'memcached'],
            'queue': ['queue', 'message', 'rabbitmq', 'kafka'],
            'auth': ['auth', 'authentication', 'authorization', 'login'],
            'storage': ['storage', 'file', 'upload', 's3', 'blob']
        }

        for component, keywords in component_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                components.append(component.title())

        return components if components else ['Application', 'System']

    def _extract_user_interactions(self, description: str) -> List[str]:
        """Extract user interactions from description."""
        interactions = []
        description_lower = description.lower()

        # Common user interactions
        interaction_keywords = {
            'login': ['login', 'sign in', 'authenticate'],
            'navigation': ['navigate', 'menu', 'browse', 'search'],
            'data_entry': ['enter', 'input', 'form', 'submit', 'create'],
            'viewing': ['view', 'display', 'show', 'list', 'browse'],
            'editing': ['edit', 'update', 'modify', 'change'],
            'deletion': ['delete', 'remove', 'clear'],
            'configuration': ['configure', 'settings', 'preferences', 'setup']
        }

        for interaction, keywords in interaction_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                interactions.append(interaction.replace('_', ' ').title())

        return interactions if interactions else ['User Input', 'System Response']

    def _extract_process_steps(self, description: str) -> List[str]:
        """Extract process steps from description."""
        steps = []
        description_lower = description.lower()

        # Common process steps
        step_keywords = {
            'initialization': ['initialize', 'setup', 'start', 'begin'],
            'validation': ['validate', 'verify', 'check', 'confirm'],
            'processing': ['process', 'execute', 'run', 'perform'],
            'storage': ['save', 'store', 'persist', 'write'],
            'notification': ['notify', 'alert', 'inform', 'send'],
            'completion': ['complete', 'finish', 'end', 'done']
        }

        for step, keywords in step_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                steps.append(step.title())

        return steps if steps else ['Start', 'Process', 'Complete']

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
            print()

        if enhancements.get('visual_elements'):
            visual_elements = enhancements['visual_elements']
            print(f"🎨 Visual Elements Generated:")
            if visual_elements.get('mermaid_diagram'):
                print(f"   📊 Mermaid Diagram: {visual_elements['mermaid_diagram'].get('type', 'flowchart')}")
            if visual_elements.get('ascii_art'):
                print(f"   🎭 ASCII Art: {visual_elements['ascii_art'].get('type', 'generic')}")
            if visual_elements.get('visual_consistency'):
                consistency = visual_elements['visual_consistency'].get('consistency_score', 0.8)
                print(f"   ✅ Visual Consistency: {consistency:.1%}")
            print()

        if enhancements.get('flow_diagrams'):
            flow_diagrams = enhancements['flow_diagrams']
            print(f"📊 Flow Diagrams ({len(flow_diagrams)}):")
            for i, diagram in enumerate(flow_diagrams[:2], 1):
                print(f"   {i}. {diagram.get('title', f'Diagram {i}')} ({diagram.get('type', 'unknown')})")
            if len(flow_diagrams) > 2:
                print(f"   ... and {len(flow_diagrams) - 2} more")
            print()

        if enhancements.get('template_optimization'):
            template_opt = enhancements['template_optimization']
            print(f"🏗️  Template Optimization:")
            print(f"   🎯 Quality Score: {template_opt.get('quality_score', 8.0):.1f}/10")
            print(f"   📋 Sections: {len(template_opt.get('sections_generated', []))}")
            validation = template_opt.get('template_validation', {})
            print(f"   ✅ Completeness: {validation.get('completeness_score', 75.0):.0f}%")

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

    def _parse_requirements_response(self, response: str) -> List[str]:
        """Parse AI response into structured requirements list."""
        requirements = []
        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Remove numbering and clean up
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')) or
                        line.startswith('-') or line.startswith('*')):
                # Remove numbering/bullets and clean
                clean_req = re.sub(r'^\d+\.\s*', '', line)
                clean_req = re.sub(r'^[-*]\s*', '', clean_req)
                if clean_req and len(clean_req) > 10:
                    requirements.append(clean_req)

        return requirements[:8]  # Limit to 8 requirements

    def _generate_fallback_requirements(self, description: str, context: Dict[str, Any]) -> List[str]:
        """Generate fallback requirements when AI generation fails."""
        task_type = context.get('task_type', 'Development')

        # Generate basic requirements based on task type
        if 'install' in description.lower() or 'setup' in description.lower():
            return [
                "The system must validate all prerequisites before installation",
                "The script must create backup copies of existing configurations",
                "The installation must provide clear progress indicators",
                "The system must verify successful installation completion",
                "The script must handle installation errors gracefully",
                "The system must provide rollback capability if installation fails"
            ]
        elif 'enhance' in description.lower() or 'improve' in description.lower():
            return [
                "The system must maintain backward compatibility",
                "The enhancement must not break existing functionality",
                "The system must provide performance improvements",
                "The enhancement must include comprehensive testing",
                "The system must document all changes made",
                "The enhancement must follow existing code patterns"
            ]
        elif task_type.lower() == 'bug fix':
            return [
                "The fix must address the root cause of the issue",
                "The system must prevent regression of the bug",
                "The fix must include comprehensive test coverage",
                "The system must maintain existing functionality",
                "The fix must be documented with clear explanations"
            ]
        else:
            return [
                "The system must meet all specified functional requirements",
                "The implementation must follow established coding standards",
                "The system must include appropriate error handling",
                "The implementation must be thoroughly tested",
                "The system must provide clear user feedback",
                "The implementation must be properly documented"
            ]

    def _get_step_templates_for_task_type(self, task_type: str) -> Dict[str, List[str]]:
        """Get task-specific step templates for implementation phases."""
        templates = {
            "Development": {
                "phases": ["Analysis & Design", "Implementation", "Testing", "Integration", "Documentation"],
                "common_steps": [
                    "Review existing codebase and architecture",
                    "Design solution approach and components",
                    "Implement core functionality with error handling",
                    "Write comprehensive unit and integration tests",
                    "Update documentation and code comments"
                ]
            },
            "Bug Fix": {
                "phases": ["Investigation", "Root Cause Analysis", "Fix Implementation", "Testing", "Verification"],
                "common_steps": [
                    "Reproduce the bug and analyze symptoms",
                    "Identify root cause through debugging",
                    "Implement targeted fix with minimal impact",
                    "Test fix thoroughly to prevent regression",
                    "Verify fix resolves original issue"
                ]
            },
            "Enhancement": {
                "phases": ["Requirements Analysis", "Design Enhancement", "Implementation", "Testing", "Deployment"],
                "common_steps": [
                    "Analyze current functionality and limitations",
                    "Design enhanced solution maintaining compatibility",
                    "Implement enhancements with proper validation",
                    "Test enhanced functionality thoroughly",
                    "Deploy with rollback capability"
                ]
            }
        }
        return templates.get(task_type, templates["Development"])

    def _parse_implementation_steps_response(self, response: str, due_date: Optional[str]) -> List[Dict[str, Any]]:
        """Parse AI response into enhanced implementation steps structure."""
        steps = []
        current_phase = None

        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()

            # Match phase headers with various formats
            if (line.startswith('Phase ') and ':' in line) or (line.startswith('**Phase ') and '**' in line):
                if current_phase:
                    steps.append(current_phase)

                # Extract phase title and duration
                phase_text = line.replace('**', '').replace('Phase ', '')
                if ':' in phase_text:
                    phase_parts = phase_text.split(':', 1)
                    phase_title = phase_parts[1].strip()

                    # Extract duration if present
                    duration = "TBD"
                    if ' - Estimated:' in phase_title:
                        title_parts = phase_title.split(' - Estimated:')
                        phase_title = title_parts[0].strip()
                        duration = title_parts[1].strip() if len(title_parts) > 1 else "TBD"

                    current_phase = {
                        'title': phase_title,
                        'completed': False,
                        'in_progress': False,
                        'target_date': due_date,
                        'estimated_duration': duration,
                        'substeps': [],
                        'deliverables': []
                    }

            # Match substeps
            elif line.startswith('- ') and current_phase:
                substep_text = line[2:].strip()
                current_phase['substeps'].append({
                    'description': substep_text,
                    'completed': False
                })

            # Match deliverables
            elif line.startswith('Deliverables:') and current_phase:
                deliverables_text = line.replace('Deliverables:', '').strip()
                if deliverables_text:
                    current_phase['deliverables'] = [d.strip() for d in deliverables_text.split(',')]

        # Add the last phase
        if current_phase:
            steps.append(current_phase)

        return steps[:5]  # Limit to 5 phases

    def _generate_fallback_implementation_steps_enhanced(self, description: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhanced fallback implementation steps based on task context."""
        task_type = context.get('task_type', 'Development')
        due_date = context.get('due_date')

        # Get task-specific templates
        templates = self._get_step_templates_for_task_type(task_type)

        # Generate context-aware steps
        if 'install' in description.lower() or 'setup' in description.lower():
            return self._generate_installation_steps(due_date)
        elif 'enhance' in description.lower() or 'improve' in description.lower():
            return self._generate_enhancement_steps(due_date)
        elif task_type.lower() == 'bug fix':
            return self._generate_bug_fix_steps(due_date)
        else:
            return self._generate_development_steps(due_date)

    def _generate_installation_steps(self, due_date: Optional[str]) -> List[Dict[str, Any]]:
        """Generate installation-specific implementation steps."""
        return [
            {
                'title': 'Prerequisites Validation',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '1 day',
                'substeps': [
                    {'description': 'Verify system requirements and dependencies', 'completed': False},
                    {'description': 'Check compatibility with existing systems', 'completed': False},
                    {'description': 'Prepare installation environment', 'completed': False}
                ],
                'deliverables': ['Prerequisites checklist', 'Environment setup guide']
            },
            {
                'title': 'Installation Implementation',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '2 days',
                'substeps': [
                    {'description': 'Create backup of existing configurations', 'completed': False},
                    {'description': 'Execute installation procedures step by step', 'completed': False},
                    {'description': 'Configure system settings and parameters', 'completed': False}
                ],
                'deliverables': ['Installation scripts', 'Configuration files']
            },
            {
                'title': 'Testing and Validation',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '1 day',
                'substeps': [
                    {'description': 'Test installation functionality', 'completed': False},
                    {'description': 'Validate system integration', 'completed': False},
                    {'description': 'Verify performance and stability', 'completed': False}
                ],
                'deliverables': ['Test results', 'Validation report']
            }
        ]

    def _generate_enhancement_steps(self, due_date: Optional[str]) -> List[Dict[str, Any]]:
        """Generate enhancement-specific implementation steps."""
        return [
            {
                'title': 'Current State Analysis',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '1 day',
                'substeps': [
                    {'description': 'Analyze existing functionality and limitations', 'completed': False},
                    {'description': 'Identify improvement opportunities', 'completed': False},
                    {'description': 'Document current architecture and patterns', 'completed': False}
                ],
                'deliverables': ['Analysis report', 'Architecture documentation']
            },
            {
                'title': 'Enhancement Design',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '2 days',
                'substeps': [
                    {'description': 'Design enhanced solution maintaining compatibility', 'completed': False},
                    {'description': 'Plan implementation approach and timeline', 'completed': False},
                    {'description': 'Identify potential risks and mitigation strategies', 'completed': False}
                ],
                'deliverables': ['Enhancement design document', 'Implementation plan']
            },
            {
                'title': 'Implementation and Testing',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '3 days',
                'substeps': [
                    {'description': 'Implement enhancements with proper validation', 'completed': False},
                    {'description': 'Test enhanced functionality thoroughly', 'completed': False},
                    {'description': 'Ensure backward compatibility is maintained', 'completed': False}
                ],
                'deliverables': ['Enhanced functionality', 'Test suite', 'Compatibility verification']
            }
        ]

    def _generate_bug_fix_steps(self, due_date: Optional[str]) -> List[Dict[str, Any]]:
        """Generate bug fix-specific implementation steps."""
        return [
            {
                'title': 'Bug Investigation',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '1 day',
                'substeps': [
                    {'description': 'Reproduce the bug consistently', 'completed': False},
                    {'description': 'Analyze error logs and symptoms', 'completed': False},
                    {'description': 'Identify affected components and scope', 'completed': False}
                ],
                'deliverables': ['Bug reproduction steps', 'Impact analysis']
            },
            {
                'title': 'Root Cause Analysis',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '1 day',
                'substeps': [
                    {'description': 'Debug code to identify root cause', 'completed': False},
                    {'description': 'Analyze code flow and data handling', 'completed': False},
                    {'description': 'Document findings and fix approach', 'completed': False}
                ],
                'deliverables': ['Root cause analysis', 'Fix strategy document']
            },
            {
                'title': 'Fix Implementation and Verification',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '2 days',
                'substeps': [
                    {'description': 'Implement targeted fix with minimal impact', 'completed': False},
                    {'description': 'Test fix thoroughly to prevent regression', 'completed': False},
                    {'description': 'Verify fix resolves original issue completely', 'completed': False}
                ],
                'deliverables': ['Bug fix implementation', 'Regression test suite', 'Verification report']
            }
        ]

    def _generate_development_steps(self, due_date: Optional[str]) -> List[Dict[str, Any]]:
        """Generate general development implementation steps."""
        return [
            {
                'title': 'Requirements Analysis and Design',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '2 days',
                'substeps': [
                    {'description': 'Review requirements and specifications thoroughly', 'completed': False},
                    {'description': 'Design solution architecture and components', 'completed': False},
                    {'description': 'Plan implementation approach and timeline', 'completed': False}
                ],
                'deliverables': ['Technical specification', 'Architecture design', 'Implementation plan']
            },
            {
                'title': 'Core Implementation',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '3 days',
                'substeps': [
                    {'description': 'Implement core functionality following design', 'completed': False},
                    {'description': 'Add comprehensive error handling and validation', 'completed': False},
                    {'description': 'Integrate with existing systems and components', 'completed': False}
                ],
                'deliverables': ['Core functionality', 'Error handling system', 'Integration points']
            },
            {
                'title': 'Testing and Documentation',
                'completed': False,
                'in_progress': False,
                'target_date': due_date,
                'estimated_duration': '2 days',
                'substeps': [
                    {'description': 'Write comprehensive unit and integration tests', 'completed': False},
                    {'description': 'Update documentation and code comments', 'completed': False},
                    {'description': 'Perform final testing and quality assurance', 'completed': False}
                ],
                'deliverables': ['Test suite', 'Updated documentation', 'Quality assurance report']
            }
        ]

    async def _enhance_with_codebase_context(self, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced context-aware content enhancement using codebase analysis."""
        try:
            # Analyze relevant files
            relevant_files = await self._find_relevant_codebase_files(description, context)

            # Extract patterns and technologies
            tech_stack = self._analyze_technology_stack(relevant_files)
            patterns = self._extract_code_patterns(relevant_files)

            # Generate context-aware enhancements
            enhancements = {
                'technical_considerations': self._generate_tech_considerations(tech_stack, patterns),
                'implementation_patterns': self._suggest_implementation_patterns(patterns),
                'testing_strategy': self._generate_testing_strategy(tech_stack, context),
                'risk_assessment': self._generate_contextual_risks(tech_stack, patterns)
            }

            return enhancements

        except Exception as e:
            logger.error(f"Codebase context enhancement failed: {e}")
            return {}

    async def _find_relevant_codebase_files(self, description: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find relevant codebase files based on task description and context."""
        try:
            # Use semantic search to find relevant files
            relevant_context = self._collect_embeddings_context(description, context)

            # Convert to file analysis format
            relevant_files = []
            for chunk in relevant_context[:10]:  # Top 10 relevant files
                file_info = {
                    'file_path': chunk.file_name,
                    'file_type': chunk.file_type,
                    'content_preview': chunk.text[:500],
                    'relevance_score': chunk.relevance_score,
                    'language': self._detect_language_from_file(chunk.file_name),
                    'functions': self._extract_functions_from_content(chunk.text),
                    'classes': self._extract_classes_from_content(chunk.text),
                    'imports': self._extract_imports_from_content(chunk.text)
                }
                relevant_files.append(file_info)

            return relevant_files

        except Exception as e:
            logger.error(f"Error finding relevant codebase files: {e}")
            return []

    def _analyze_technology_stack(self, relevant_files: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze technology stack from relevant files."""
        tech_stack = {
            'primary_language': 'Python',
            'frameworks': [],
            'libraries': [],
            'databases': [],
            'tools': []
        }

        try:
            # Analyze file types and content
            languages = {}
            frameworks = set()
            libraries = set()

            for file_info in relevant_files:
                language = file_info.get('language', 'unknown')
                if language != 'unknown':
                    languages[language] = languages.get(language, 0) + 1

                # Extract frameworks and libraries from imports
                imports = file_info.get('imports', [])
                for imp in imports:
                    if any(fw in imp.lower() for fw in ['flask', 'django', 'fastapi', 'express', 'react', 'vue', 'angular']):
                        frameworks.add(imp)
                    else:
                        libraries.add(imp)

            # Determine primary language
            if languages:
                tech_stack['primary_language'] = max(languages, key=languages.get)

            tech_stack['frameworks'] = list(frameworks)[:5]
            tech_stack['libraries'] = list(libraries)[:10]

            return tech_stack

        except Exception as e:
            logger.error(f"Error analyzing technology stack: {e}")
            return tech_stack

    def _extract_code_patterns(self, relevant_files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract code patterns from relevant files."""
        patterns = {
            'architectural': [],
            'design': [],
            'testing': [],
            'error_handling': []
        }

        try:
            for file_info in relevant_files:
                content = file_info.get('content_preview', '').lower()

                # Architectural patterns
                if 'class' in content and 'def __init__' in content:
                    patterns['architectural'].append('Object-Oriented Design')
                if 'async def' in content or 'await' in content:
                    patterns['architectural'].append('Async/Await Pattern')
                if 'decorator' in content or '@' in content:
                    patterns['architectural'].append('Decorator Pattern')

                # Design patterns
                if 'factory' in content:
                    patterns['design'].append('Factory Pattern')
                if 'singleton' in content:
                    patterns['design'].append('Singleton Pattern')
                if 'observer' in content:
                    patterns['design'].append('Observer Pattern')

                # Testing patterns
                if 'test_' in content or 'unittest' in content:
                    patterns['testing'].append('Unit Testing')
                if 'mock' in content or 'patch' in content:
                    patterns['testing'].append('Mocking')
                if 'pytest' in content:
                    patterns['testing'].append('Pytest Framework')

                # Error handling patterns
                if 'try:' in content and 'except' in content:
                    patterns['error_handling'].append('Exception Handling')
                if 'logger' in content or 'logging' in content:
                    patterns['error_handling'].append('Logging')
                if 'raise' in content:
                    patterns['error_handling'].append('Custom Exceptions')

            # Remove duplicates
            for category in patterns:
                patterns[category] = list(set(patterns[category]))

            return patterns

        except Exception as e:
            logger.error(f"Error extracting code patterns: {e}")
            return patterns

    def _generate_tech_considerations(self, tech_stack: Dict[str, str], patterns: Dict[str, List[str]]) -> str:
        """Generate technical considerations based on tech stack and patterns."""
        considerations = []

        # Language-specific considerations
        language = tech_stack.get('primary_language', 'Python')
        if language == 'Python':
            considerations.append("Follow PEP 8 style guidelines and Python best practices")
            considerations.append("Use type hints for better code documentation and IDE support")
        elif language == 'JavaScript':
            considerations.append("Follow ES6+ standards and modern JavaScript practices")
            considerations.append("Consider TypeScript for better type safety")

        # Framework considerations
        frameworks = tech_stack.get('frameworks', [])
        if frameworks:
            considerations.append(f"Integrate with existing {', '.join(frameworks)} framework patterns")

        # Pattern-based considerations
        if patterns.get('architectural'):
            considerations.append(f"Follow established architectural patterns: {', '.join(patterns['architectural'])}")

        if patterns.get('testing'):
            considerations.append(f"Maintain existing testing patterns: {', '.join(patterns['testing'])}")

        if patterns.get('error_handling'):
            considerations.append(f"Follow existing error handling patterns: {', '.join(patterns['error_handling'])}")

        return '\n'.join(f"• {consideration}" for consideration in considerations[:8])

    def _suggest_implementation_patterns(self, patterns: Dict[str, List[str]]) -> List[str]:
        """Suggest implementation patterns based on existing codebase patterns."""
        suggestions = []

        # Based on architectural patterns
        if 'Object-Oriented Design' in patterns.get('architectural', []):
            suggestions.append("Use class-based design with clear inheritance hierarchy")

        if 'Async/Await Pattern' in patterns.get('architectural', []):
            suggestions.append("Implement async methods for I/O operations")

        if 'Decorator Pattern' in patterns.get('architectural', []):
            suggestions.append("Use decorators for cross-cutting concerns like logging and validation")

        # Based on design patterns
        if 'Factory Pattern' in patterns.get('design', []):
            suggestions.append("Use factory methods for object creation")

        # Based on testing patterns
        if patterns.get('testing'):
            suggestions.append("Write comprehensive unit tests following existing test patterns")

        # Based on error handling
        if patterns.get('error_handling'):
            suggestions.append("Implement robust error handling with proper logging")

        return suggestions[:6]

    def _generate_testing_strategy(self, tech_stack: Dict[str, str], context: Dict[str, Any]) -> str:
        """Generate testing strategy based on tech stack and context."""
        strategy_parts = []

        language = tech_stack.get('primary_language', 'Python')
        task_type = context.get('task_type', 'Development')

        # Language-specific testing
        if language == 'Python':
            strategy_parts.append("• Use pytest for unit testing with fixtures and parametrized tests")
            strategy_parts.append("• Implement integration tests for API endpoints")
        elif language == 'JavaScript':
            strategy_parts.append("• Use Jest for unit testing with mocking capabilities")
            strategy_parts.append("• Implement end-to-end tests with appropriate testing framework")

        # Task-specific testing
        if task_type == 'Bug Fix':
            strategy_parts.append("• Write regression tests to prevent bug reoccurrence")
            strategy_parts.append("• Test edge cases that may have caused the original bug")
        elif task_type == 'Enhancement':
            strategy_parts.append("• Test backward compatibility with existing functionality")
            strategy_parts.append("• Performance testing to ensure enhancements don't degrade performance")

        # General testing practices
        strategy_parts.append("• Achieve minimum 80% code coverage")
        strategy_parts.append("• Include both positive and negative test cases")

        return '\n'.join(strategy_parts)

    def _generate_contextual_risks(self, tech_stack: Dict[str, str], patterns: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """Generate contextual risks based on tech stack and patterns."""
        risks = []

        # Technology-specific risks
        language = tech_stack.get('primary_language', 'Python')
        if language == 'Python':
            risks.append({
                'description': 'Python version compatibility issues',
                'impact': 'Medium',
                'probability': 'Low',
                'mitigation': 'Test with target Python version and use version-specific features carefully'
            })

        # Pattern-specific risks
        if 'Async/Await Pattern' in patterns.get('architectural', []):
            risks.append({
                'description': 'Async/await complexity and potential deadlocks',
                'impact': 'High',
                'probability': 'Medium',
                'mitigation': 'Careful async design, proper error handling, and thorough testing'
            })

        # Framework risks
        frameworks = tech_stack.get('frameworks', [])
        if frameworks:
            risks.append({
                'description': f'Framework version compatibility with {", ".join(frameworks)}',
                'impact': 'Medium',
                'probability': 'Low',
                'mitigation': 'Check framework version requirements and test integration points'
            })

        # General implementation risks
        risks.append({
            'description': 'Integration complexity with existing codebase',
            'impact': 'Medium',
            'probability': 'Medium',
            'mitigation': 'Thorough analysis of integration points and comprehensive testing'
        })

        return risks[:5]

    def _detect_language_from_file(self, filename: str) -> str:
        """Detect programming language from filename."""
        filename = filename.lower()

        if filename.endswith('.py'):
            return 'Python'
        elif filename.endswith(('.js', '.jsx')):
            return 'JavaScript'
        elif filename.endswith(('.ts', '.tsx')):
            return 'TypeScript'
        elif filename.endswith('.java'):
            return 'Java'
        elif filename.endswith(('.cpp', '.cc', '.cxx')):
            return 'C++'
        elif filename.endswith('.c'):
            return 'C'
        elif filename.endswith('.go'):
            return 'Go'
        elif filename.endswith('.rs'):
            return 'Rust'
        else:
            return 'unknown'

    def _extract_functions_from_content(self, content: str) -> List[str]:
        """Extract function names from content."""
        import re

        functions = []

        # Python functions
        python_functions = re.findall(r'def\s+(\w+)\s*\(', content)
        functions.extend(python_functions)

        # JavaScript functions
        js_functions = re.findall(r'function\s+(\w+)\s*\(', content)
        functions.extend(js_functions)

        # Arrow functions
        arrow_functions = re.findall(r'const\s+(\w+)\s*=\s*\(', content)
        functions.extend(arrow_functions)

        return list(set(functions))[:10]  # Limit to 10 unique functions

    def _extract_classes_from_content(self, content: str) -> List[str]:
        """Extract class names from content."""
        import re

        classes = []

        # Python classes
        python_classes = re.findall(r'class\s+(\w+)(?:\s*\(|\s*:)', content)
        classes.extend(python_classes)

        # JavaScript classes
        js_classes = re.findall(r'class\s+(\w+)(?:\s+extends|\s*{)', content)
        classes.extend(js_classes)

        return list(set(classes))[:5]  # Limit to 5 unique classes

    def _extract_imports_from_content(self, content: str) -> List[str]:
        """Extract import statements from content."""
        import re

        imports = []

        # Python imports
        python_imports = re.findall(r'(?:from\s+(\w+)|import\s+(\w+))', content)
        for imp_tuple in python_imports:
            imports.extend([imp for imp in imp_tuple if imp])

        # JavaScript imports
        js_imports = re.findall(r'import.*?from\s+[\'"]([^\'"]+)[\'"]', content)
        imports.extend(js_imports)

        return list(set(imports))[:10]  # Limit to 10 unique imports

    def _log_quality_results(self, task_id: str, quality_result: Dict[str, Any]) -> None:
        """Log quality validation results for monitoring and improvement."""
        try:
            quality_score = quality_result.get('overall_score', 0.0)
            quality_level = quality_result.get('quality_level', 'unknown')
            recommendations = quality_result.get('recommendations', [])

            # Log overall quality
            if quality_score >= 0.9:
                logger.info(f"Task {task_id}: Excellent quality (Score: {quality_score:.2f})")
            elif quality_score >= 0.7:
                logger.info(f"Task {task_id}: Good quality (Score: {quality_score:.2f})")
            elif quality_score >= 0.5:
                logger.warning(f"Task {task_id}: Acceptable quality (Score: {quality_score:.2f})")
            else:
                logger.warning(f"Task {task_id}: Poor quality (Score: {quality_score:.2f})")

            # Log specific recommendations if any
            if recommendations:
                logger.info(f"Task {task_id}: Quality recommendations: {'; '.join(recommendations[:3])}")

            # Store quality metrics for analysis
            self._store_quality_metrics(task_id, quality_result)

        except Exception as e:
            logger.error(f"Error logging quality results for {task_id}: {e}")

    def _store_quality_metrics(self, task_id: str, quality_result: Dict[str, Any]) -> None:
        """Store quality metrics for analysis and improvement tracking."""
        try:
            import json
            from datetime import datetime

            # Create quality metrics directory
            metrics_dir = self.project_root / "mods" / "project_management" / "metrics"
            metrics_dir.mkdir(parents=True, exist_ok=True)

            # Prepare metrics data
            metrics_data = {
                'task_id': task_id,
                'timestamp': datetime.now().isoformat(),
                'overall_score': quality_result.get('overall_score', 0.0),
                'quality_level': quality_result.get('quality_level', 'unknown'),
                'metric_scores': quality_result.get('metric_scores', {}),
                'recommendations': quality_result.get('recommendations', [])
            }

            # Load existing metrics
            metrics_file = metrics_dir / "quality_metrics.json"
            existing_metrics = []

            if metrics_file.exists():
                try:
                    with open(metrics_file, 'r', encoding='utf-8') as f:
                        existing_metrics = json.load(f)
                except json.JSONDecodeError:
                    existing_metrics = []

            # Add new metrics
            existing_metrics.append(metrics_data)

            # Keep only last 100 entries
            if len(existing_metrics) > 100:
                existing_metrics = existing_metrics[-100:]

            # Save metrics
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(existing_metrics, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.warning(f"Failed to store quality metrics for {task_id}: {e}")

    def get_quality_insights(self) -> Dict[str, Any]:
        """Get insights from collected quality metrics."""
        try:
            import json

            metrics_file = self.project_root / "mods" / "project_management" / "metrics" / "quality_metrics.json"

            if not metrics_file.exists():
                return {
                    'total_tasks': 0,
                    'average_score': 0.0,
                    'quality_distribution': {},
                    'common_issues': [],
                    'improvement_trend': 'no_data'
                }

            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)

            if not metrics_data:
                return {'total_tasks': 0, 'average_score': 0.0}

            # Calculate insights
            total_tasks = len(metrics_data)
            scores = [m.get('overall_score', 0.0) for m in metrics_data]
            average_score = sum(scores) / total_tasks if scores else 0.0

            # Quality distribution
            quality_levels = [m.get('quality_level', 'unknown') for m in metrics_data]
            quality_distribution = {}
            for level in quality_levels:
                quality_distribution[level] = quality_distribution.get(level, 0) + 1

            # Common issues from recommendations
            all_recommendations = []
            for m in metrics_data:
                all_recommendations.extend(m.get('recommendations', []))

            # Count recommendation frequency
            recommendation_counts = {}
            for rec in all_recommendations:
                recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1

            # Get top 5 common issues
            common_issues = sorted(recommendation_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            # Calculate improvement trend (last 10 vs previous 10)
            improvement_trend = 'stable'
            if total_tasks >= 20:
                recent_scores = scores[-10:]
                previous_scores = scores[-20:-10]
                recent_avg = sum(recent_scores) / len(recent_scores)
                previous_avg = sum(previous_scores) / len(previous_scores)

                if recent_avg > previous_avg + 0.05:
                    improvement_trend = 'improving'
                elif recent_avg < previous_avg - 0.05:
                    improvement_trend = 'declining'

            return {
                'total_tasks': total_tasks,
                'average_score': average_score,
                'quality_distribution': quality_distribution,
                'common_issues': [issue[0] for issue in common_issues],
                'improvement_trend': improvement_trend,
                'recent_average': sum(scores[-10:]) / min(10, len(scores)) if scores else 0.0
            }

        except Exception as e:
            logger.error(f"Error getting quality insights: {e}")
            return {'error': str(e)}

    def validate_template_compliance(self, task_content: str, template_name: str) -> Dict[str, Any]:
        """Check if generated content complies with template structure."""
        try:
            required_sections = self._get_required_sections(template_name)
            found_sections = self._extract_sections_from_content(task_content)

            compliance_issues = []
            missing_sections = []

            for section in required_sections:
                if section not in found_sections:
                    missing_sections.append(section)
                    compliance_issues.append(f"Missing required section: {section}")

            # Check section content quality
            for section, content in found_sections.items():
                if len(content.strip()) < 50:  # Minimum content length
                    compliance_issues.append(f"Section '{section}' has insufficient content")

            compliance_score = len(found_sections) / len(required_sections) if required_sections else 1.0

            return {
                'compliance_score': compliance_score,
                'missing_sections': missing_sections,
                'issues': compliance_issues,
                'recommendations': self._generate_compliance_recommendations(compliance_issues)
            }

        except Exception as e:
            logger.error(f"Error validating template compliance: {e}")
            return {'compliance_score': 0.0, 'error': str(e)}

    def _get_required_sections(self, template_name: str) -> List[str]:
        """Get required sections for a template."""
        template_sections = {
            'enhanced_task': [
                'Task Overview', 'Functional Requirements', 'Implementation Steps',
                'Technical Considerations', 'Success Criteria', 'Risk Assessment'
            ],
            'development_task': [
                'Description', 'Requirements', 'Implementation', 'Testing'
            ],
            'bug_fix_task': [
                'Bug Description', 'Root Cause', 'Fix Implementation', 'Testing'
            ]
        }

        return template_sections.get(template_name, [])

    def _extract_sections_from_content(self, content: str) -> Dict[str, str]:
        """Extract sections from task content."""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            # Check for section headers
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)

                # Start new section
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _generate_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations for template compliance issues."""
        recommendations = []

        for issue in issues:
            if 'Missing required section' in issue:
                section = issue.split(': ')[1]
                recommendations.append(f"Add the missing '{section}' section with appropriate content")
            elif 'insufficient content' in issue:
                recommendations.append("Expand section content with more detailed information")

        if not recommendations:
            recommendations.append("Template compliance is good - no major issues found")

        return recommendations