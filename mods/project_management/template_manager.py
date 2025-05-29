"""
Template Management Module

Handles template optimization, context preparation, and rendering coordination for task creation.
Extracted from ai_task_creator.py for better modularity and maintainability.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from .template_engine import TemplateEngine
from .template_optimizer import TemplateOptimizer

logger = logging.getLogger("TaskHeroAI.ProjectManagement.TemplateManager")


class TemplateManager:
    """Service for managing templates and context preparation in task creation."""

    def __init__(self, project_root: str):
        """Initialize the Template Manager.
        
        Args:
            project_root: Root directory for project management
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.template_engine = TemplateEngine(project_root)
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

    def prepare_base_context(self, **kwargs) -> Dict[str, Any]:
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
            'brief_description': kwargs.get('description', ''),
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
            'show_naming_convention': False,  # Hide naming convention (for AI prompts only)
            'show_metadata_legend': False,    # Hide metadata legend (for AI prompts only)
            'show_implementation_analysis': True,

            # Default implementation steps
            'implementation_steps': self._generate_default_implementation_steps(due_date),

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

    def optimize_template_context(self, context: Dict[str, Any], task_type: str, description: str) -> Dict[str, Any]:
        """Optimize template context using the template optimizer."""
        try:
            return self.template_optimizer.optimize_template_context(context, task_type, description)
        except Exception as e:
            logger.error(f"Template optimization failed: {e}")
            return context

    def generate_task_specific_flow_diagram(self, task_type: str, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate task-specific flow diagram using the template optimizer."""
        try:
            return self.template_optimizer.generate_task_specific_flow_diagram(task_type, description, context)
        except Exception as e:
            logger.error(f"Flow diagram generation failed: {e}")
            return {
                'flow_diagram': '```mermaid\nflowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]\n```',
                'flow_description': 'Basic task flow',
                'show_flow_diagram': True
            }

    def render_enhanced_task(self, context: Dict[str, Any]) -> str:
        """Render the enhanced task template with the provided context."""
        try:
            return self.template_engine.render_template(self.enhanced_template, context)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            raise

    def validate_optimized_template(self, context: Dict[str, Any]) -> List[str]:
        """Validate the optimized template for quality issues."""
        try:
            return self.template_optimizer.validate_optimized_template(context)
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            return [f"Template validation error: {e}"]

    def generate_filename(self, task_id: str, task_type: str, title: str) -> str:
        """Generate filename following naming convention."""
        try:
            # Get task type abbreviation
            task_prefix = self.task_type_mappings.get(task_type, 'DEV')
            
            # Clean title for filename
            clean_title = self._clean_title_for_filename(title)
            
            # Generate filename: TASK-XXX-TYPE-clean-title.md
            filename = f"{task_id}-{task_prefix}-{clean_title}.md"
            
            return filename
        except Exception as e:
            logger.error(f"Filename generation failed: {e}")
            return f"{task_id}-DEV-task.md"

    def _generate_default_implementation_steps(self, due_date: str) -> List[Dict[str, Any]]:
        """Generate default implementation steps."""
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
        ]

    def _clean_title_for_filename(self, title: str) -> str:
        """Clean title for use in filename."""
        import re
        
        # Convert to lowercase and replace spaces with hyphens
        clean = title.lower().replace(' ', '-')
        
        # Remove special characters except hyphens
        clean = re.sub(r'[^a-z0-9\-]', '', clean)
        
        # Remove multiple consecutive hyphens
        clean = re.sub(r'-+', '-', clean)
        
        # Remove leading/trailing hyphens
        clean = clean.strip('-')
        
        # Limit length
        if len(clean) > 50:
            clean = clean[:50].rstrip('-')
        
        return clean or 'task'
