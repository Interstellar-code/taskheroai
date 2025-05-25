"""
Enhanced Template Engine Module

Provides advanced template management with Jinja2 integration, security sandboxing,
template inheritance, validation, and AI-assisted template generation.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
    StrictUndefined,
    Template,
    TemplateNotFound,
    TemplateSyntaxError,
    UndefinedError
)
from jinja2.sandbox import SandboxedEnvironment

logger = logging.getLogger("TaskHeroAI.ProjectManagement.TemplateEngine")


class TemplateError(Exception):
    """Custom exception for template-related errors."""
    pass


@dataclass
class TemplateMetadata:
    """Template metadata structure."""
    name: str
    title: str
    description: str
    version: str
    category: str
    tags: List[str]
    author: str
    created: str
    modified: str
    requires: List[str]
    variables: List[str]
    is_base: bool = False
    extends: Optional[str] = None


class TemplateEngine:
    """Enhanced template engine with Jinja2 integration and advanced features."""

    def __init__(self, project_root: Optional[str] = None, sandboxed: bool = True):
        """
        Initialize the Template Engine.

        Args:
            project_root: Root directory for project management
            sandboxed: Whether to use sandboxed environment for security
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.templates_dir = self.project_root / "mods" / "project_management" / "templates"
        self.schemas_dir = self.project_root / "mods" / "project_management" / "schemas"
        self.sandboxed = sandboxed

        # Create directories if they don't exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.schemas_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Jinja2 environment
        self._setup_jinja_environment()

        # Template cache for performance
        self._template_cache = {}
        self._metadata_cache = {}

    def _setup_jinja_environment(self):
        """Set up the Jinja2 environment with proper configuration."""
        try:
            # Choose environment type based on security needs
            env_class = SandboxedEnvironment if self.sandboxed else Environment

            self.jinja_env = env_class(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                undefined=StrictUndefined,
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )

            # Add custom filters
            self._register_custom_filters()

            # Add custom globals
            self._register_custom_globals()

            logger.info(f"Template engine initialized with {'sandboxed' if self.sandboxed else 'standard'} environment")

        except Exception as e:
            logger.error(f"Failed to initialize Jinja2 environment: {e}")
            raise

    def _register_custom_filters(self):
        """Register custom Jinja2 filters."""
        self.jinja_env.filters.update({
            'timestamp': lambda x: datetime.now().strftime(x) if x else datetime.now().isoformat(),
            'slugify': lambda x: x.lower().replace(' ', '-').replace('_', '-'),
            'capitalize_words': lambda x: ' '.join(word.capitalize() for word in x.split()),
            'file_extension': lambda x: Path(x).suffix if x else '',
            'file_name': lambda x: Path(x).stem if x else '',
        })

    def _register_custom_globals(self):
        """Register custom global variables and functions."""
        self.jinja_env.globals.update({
            'now': datetime.now,
            'today': datetime.now().strftime('%Y-%m-%d'),
            'current_year': datetime.now().year,
            'current_month': datetime.now().strftime('%B'),
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })

    def get_template_categories(self) -> List[str]:
        """Get available template categories."""
        categories = set()

        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                categories.add(template_dir.name)

        return sorted(list(categories))

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available templates with metadata.

        Args:
            category: Filter by template category

        Returns:
            List of template information dictionaries
        """
        templates = []

        search_dirs = [self.templates_dir / category] if category else [self.templates_dir]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            # Search recursively for template files
            for template_file in search_dir.rglob("*.j2"):
                try:
                    metadata = self.get_template_metadata(str(template_file.relative_to(self.templates_dir)))
                    if metadata:
                        templates.append(asdict(metadata))
                except Exception as e:
                    logger.warning(f"Could not load metadata for {template_file}: {e}")

        return sorted(templates, key=lambda x: (x['category'], x['name']))

    def get_template_metadata(self, template_name: str) -> Optional[TemplateMetadata]:
        """
        Extract metadata from template file.

        Args:
            template_name: Name/path of the template file

        Returns:
            TemplateMetadata object or None if not found
        """
        if template_name in self._metadata_cache:
            return self._metadata_cache[template_name]

        template_path = self.templates_dir / template_name
        if not template_path.exists():
            return None

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata = self._parse_template_metadata(content, template_name)
            self._metadata_cache[template_name] = metadata
            return metadata

        except Exception as e:
            logger.error(f"Error reading template metadata {template_name}: {e}")
            return None

    def _parse_template_metadata(self, content: str, template_name: str) -> TemplateMetadata:
        """Parse metadata from template content."""
        lines = content.split('\n')
        metadata = {
            'name': template_name,
            'title': '',
            'description': '',
            'version': '1.0.0',
            'category': 'general',
            'tags': [],
            'author': 'TaskHero AI',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'modified': datetime.now().strftime('%Y-%m-%d'),
            'requires': [],
            'variables': [],
            'is_base': False,
            'extends': None
        }

        # Parse metadata from comments at the beginning of the file
        in_metadata = False
        for line in lines:
            line = line.strip()

            if line.startswith('{#') and 'METADATA' in line:
                in_metadata = True
                continue
            elif line == '#}' and in_metadata:
                in_metadata = False
                break
            elif in_metadata and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key.lower() in metadata:
                    if key.lower() in ['tags', 'requires', 'variables']:
                        metadata[key.lower()] = [v.strip() for v in value.split(',') if v.strip()]
                    elif key.lower() == 'is_base':
                        metadata[key.lower()] = value.lower() in ['true', 'yes', '1']
                    else:
                        metadata[key.lower()] = value

        # Detect category from path
        path_parts = Path(template_name).parts
        if len(path_parts) > 1:
            metadata['category'] = path_parts[0]

        # Detect variables in template using Jinja2's meta module
        try:
            from jinja2 import meta
            ast = self.jinja_env.parse(content)
            detected_vars = list(meta.find_undeclared_variables(ast))

            # Combine detected variables with those from metadata
            all_variables = list(set(metadata['variables'] + detected_vars))
            metadata['variables'] = all_variables

        except Exception as e:
            logger.debug(f"Could not detect variables in template {template_name}: {e}")

        return TemplateMetadata(**metadata)

    def render_template(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template with the given context.

        Args:
            template_name: Name of the template to render
            context: Context variables for template rendering

        Returns:
            Rendered template content

        Raises:
            TemplateError: If template rendering fails
        """
        if context is None:
            context = {}

        try:
            # Load template
            template = self.jinja_env.get_template(template_name)

            # Start with comprehensive defaults and merge user context
            full_context = self._generate_sample_context()
            full_context.update(context)  # User context overrides defaults

            # Render template
            rendered = template.render(**full_context)

            return rendered

        except TemplateNotFound:
            raise TemplateError(f"Template not found: {template_name}")
        except TemplateSyntaxError as e:
            raise TemplateError(f"Template syntax error in {template_name}: {e}")
        except UndefinedError as e:
            raise TemplateError(f"Undefined variable in template {template_name}: {e}")
        except Exception as e:
            raise TemplateError(f"Template rendering error: {e}")

    def _prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and validate the rendering context."""
        full_context = context.copy()

        # Add default variables if not provided
        defaults = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'generator': 'TaskHero AI Template Engine',
            'project_root': str(self.project_root),
        }

        for key, value in defaults.items():
            if key not in full_context:
                full_context[key] = value

        return full_context

    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validate a template for syntax and completeness.

        Args:
            template_name: Name of the template to validate

        Returns:
            Validation results dictionary
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'metadata': None,
            'variables': [],
            'extends': None
        }

        template_path = self.templates_dir / template_name
        if not template_path.exists():
            result['errors'].append(f"Template file not found: {template_name}")
            return result

        try:
            # Read template content
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse template to check syntax
            template = self.jinja_env.from_string(content)

            # Get metadata
            metadata = self.get_template_metadata(template_name)
            if metadata:
                result['metadata'] = asdict(metadata)

            # Extract variables and extends
            ast = self.jinja_env.parse(content)
            result['variables'] = list(meta.find_undeclared_variables(ast))

            # Check for extends
            for node in ast.find_all(Template):
                if hasattr(node, 'template'):
                    result['extends'] = node.template.value
                    break

            result['valid'] = True
            logger.info(f"Template {template_name} validated successfully")

        except TemplateSyntaxError as e:
            result['errors'].append(f"Syntax error: {e}")
        except Exception as e:
            result['errors'].append(f"Validation error: {e}")

        return result

    def create_template(self,
                       template_name: str,
                       content: str,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new template file.

        Args:
            template_name: Name for the new template
            content: Template content
            metadata: Optional metadata dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            template_path = self.templates_dir / template_name
            template_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare content with metadata header
            if metadata:
                metadata_header = self._create_metadata_header(metadata)
                content = metadata_header + "\n" + content

            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Clear caches
            self._template_cache.pop(template_name, None)
            self._metadata_cache.pop(template_name, None)

            logger.info(f"Template {template_name} created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating template {template_name}: {e}")
            return False

    def _create_metadata_header(self, metadata: Dict[str, Any]) -> str:
        """Create a metadata header for template files."""
        header_lines = ["{# METADATA"]

        for key, value in metadata.items():
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            header_lines.append(f"{key}: {value}")

        header_lines.append("#}")
        return '\n'.join(header_lines)

    def copy_template(self, source_template: str, new_name: str) -> bool:
        """
        Create a copy of an existing template.

        Args:
            source_template: Name of the template to copy
            new_name: Name for the new template

        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = self.templates_dir / source_template
            target_path = self.templates_dir / new_name

            if not source_path.exists():
                logger.error(f"Source template not found: {source_template}")
                return False

            target_path.parent.mkdir(parents=True, exist_ok=True)

            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Template copied from {source_template} to {new_name}")
            return True

        except Exception as e:
            logger.error(f"Error copying template: {e}")
            return False

    def get_template_preview(self, template_name: str, sample_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a preview of the template with sample data.

        Args:
            template_name: Name of the template
            sample_context: Sample context data

        Returns:
            Preview content
        """
        if not sample_context:
            sample_context = self._generate_sample_context()

        try:
            return self.render_template(template_name, sample_context)
        except Exception as e:
            return f"Preview error: {e}"

    def _generate_sample_context(self) -> Dict[str, Any]:
        """Generate comprehensive sample context for template previews."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return {
            # Basic metadata
            'task_id': 'SAMPLE-001',
            'title': 'Sample Title',
            'description': 'Sample description for template preview',
            'priority': 'Medium',
            'status': 'Draft',
            'assignee': 'Sample User',
            'task_type': 'Sample',
            'created': current_date,
            'due_date': current_date,
            'sequence': '1',
            'tags': ['sample', 'template'],
            'estimated_hours': '4',
            'actual_hours': '2',
            'estimated_effort': 'Medium',
            'related_epic': 'Sample Epic',

            # Project-specific variables
            'project_name': 'Sample Project',
            'total_tasks': 10,
            'done_count': 3,
            'testing_count': 2,
            'devdone_count': 2,
            'inprogress_count': 2,
            'todo_count': 1,
            'backlog_count': 0,
            'completion_rate': 70,
            'total_estimated_hours': 40,
            'total_actual_hours': 25,
            'progress_percentage': 65,

            # Report-specific variables
            'report_date': current_date,
            'completed_tasks': 7,
            'completion_percentage': 70,
            'inprogress_tasks': 2,
            'inprogress_percentage': 20,
            'todo_tasks': 1,
            'todo_percentage': 10,
            'overdue_tasks': 0,
            'health_score': 85,
            'executive_summary': 'Sample executive summary for template preview',

            # Task implementation
            'implementation_steps': [
                {
                    'title': 'Sample Step 1',
                    'completed': True,
                    'target_date': current_date,
                    'substeps': [
                        {'description': 'Sample substep 1.1', 'completed': True},
                        {'description': 'Sample substep 1.2', 'completed': False}
                    ]
                }
            ],

            # Dependencies and relationships
            'dependencies': ['SAMPLE-000 - Sample Dependency'],
            'dependent_tasks': ['SAMPLE-002 - Sample Dependent Task'],
            'dependency_type': 'Blocking',

            # Testing and validation
            'testing_strategy': 'Sample testing strategy',
            'test_plan': [
                {'name': 'Sample Test', 'description': 'Sample test description', 'completed': False}
            ],
            'acceptance_criteria': [
                {'description': 'Sample acceptance criterion', 'completed': False}
            ],
            'success_metrics': [
                {'name': 'Sample Metric', 'target': '100%', 'current': '75%'}
            ],

            # Technical details
            'technical_notes': 'Sample technical notes',
            'constraints': ['Sample constraint'],
            'assumptions': ['Sample assumption'],
            'database_changes': 'No database changes required',
            'database_schema': 'Sample schema',
            'architecture_notes': 'Sample architecture notes',
            'performance_considerations': 'Sample performance considerations',
            'security_considerations': 'Sample security considerations',

            # Flow and process
            'flow_description': 'Sample flow description',
            'flow_steps': [
                {'title': 'Sample Flow Step 1'},
                {'title': 'Sample Flow Step 2'}
            ],
            'flow_notes': 'Sample flow notes',
            'show_flow_diagram': True,
            'detailed_description': 'Sample detailed description for template preview',

            # Collections and lists
            'tasks': [
                {
                    'id': 'SAMPLE-001',
                    'status': 'Done',
                    'title': 'Sample Task',
                    'type': 'Sample',
                    'priority': 'Medium',
                    'due_date': current_date,
                    'assignee': 'Sample User',
                    'progress': 100
                }
            ],

            # Kanban board data
            'kanban_backlog': [{'id': 'SAMPLE-B1', 'title': 'Backlog Item'}],
            'kanban_todo': [{'id': 'SAMPLE-T1', 'title': 'Todo Item'}],
            'kanban_inprogress': [{'id': 'SAMPLE-I1', 'title': 'In Progress Item'}],
            'kanban_devdone': [{'id': 'SAMPLE-D1', 'title': 'Dev Done Item'}],
            'kanban_testing': [{'id': 'SAMPLE-TS1', 'title': 'Testing Item'}],
            'kanban_done': [{'id': 'SAMPLE-DN1', 'title': 'Done Item'}],

            # Timeline and milestones
            'timeline_entries': [
                {'date': current_date, 'title': 'Sample Milestone', 'description': 'Sample milestone description'}
            ],
            'milestones': [
                {'name': 'Sample Milestone', 'date': current_date, 'status': 'Complete', 'dependencies': []}
            ],

            # Team and performance
            'task_categories': [
                {'name': 'Development', 'completed': 5, 'total': 8, 'percentage': 63}
            ],
            'team_performance': [
                {'name': 'Sample Team', 'completed_tasks': 5, 'hours_logged': 25}
            ],
            'team_updates': [
                {
                    'name': 'Sample Team Member',
                    'focus_areas': ['Development'],
                    'completed': 'Sample completed work',
                    'current_work': 'Sample current work',
                    'blockers': 'None',
                    'availability': '100%',
                    'achievements': ['Completed Phase 1', 'Improved template system']
                }
            ],

            # Sprint and project management
            'current_sprint': {
                'name': 'Sample Sprint',
                'start_date': current_date,
                'end_date': current_date,
                'goal': 'Sample sprint goal',
                'tasks': ['SAMPLE-001'],
                'progress': 65
            },
            'sprint_name': 'Sample Sprint',
            'velocity': 5,
            'burndown_rate': 2,
            'quality_score': 85,
            'risk_level': 'Low',

            # Blockers and risks
            'blockers': [
                {
                    'severity': 'Low',
                    'title': 'Sample Blocker',
                    'description': 'Sample blocker description',
                    'impact': 'Minimal impact',
                    'mitigation': 'Sample mitigation',
                    'owner': 'Sample Owner',
                    'target_date': current_date
                }
            ],

            # Accomplishments and work
            'accomplishments': [
                {
                    'title': 'Sample Accomplishment',
                    'date': current_date,
                    'description': 'Sample accomplishment description',
                    'impact': 'Sample impact'
                }
            ],
            'current_work': [
                {
                    'title': 'Sample Work Item',
                    'assignee': 'Sample User',
                    'status': 'In Progress',
                    'progress': 50,
                    'due_date': current_date,
                    'blockers': 'None'
                }
            ],

            # Deadlines and scheduling
            'upcoming_deadlines': [
                {
                    'id': 'SAMPLE-001',
                    'title': 'Sample Deadline',
                    'due_date': current_date,
                    'assignee': 'Sample User',
                    'status': 'In Progress',
                    'risk': 'Low'
                }
            ],

            # Charts and visualization data
            'burndown_days': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'burndown_values': [100, 75, 45, 20],
            'initial_tasks': 100,
            'high_priority_completed': 15,
            'medium_priority_completed': 25,
            'low_priority_completed': 10,
            'remaining_tasks': 50,

            # Metrics and KPIs
            'sprint_velocity': 5,
            'cycle_time': 3,
            'defect_rate': 2,
            'team_utilization': 85,
            'customer_satisfaction': 8,
            'code_coverage': 85,
            'test_pass_rate': 95,
            'bug_density': 1,
            'technical_debt': 10,

            # Recommendations and actions
            'recommendations': [
                {
                    'priority': 'Medium',
                    'title': 'Sample Recommendation',
                    'description': 'Sample recommendation description',
                    'impact': 'Sample impact',
                    'timeline': 'Sample timeline'
                }
            ],
            'action_items': [
                {
                    'description': 'Sample Action Item',
                    'owner': 'Sample Owner',
                    'due_date': current_date,
                    'priority': 'Medium',
                    'status': 'Pending'
                }
            ],

            # Distribution and analytics
            'task_distribution': [
                {'name': 'Development', 'count': 5, 'percentage': 50}
            ],

            # References and updates
            'references': ['Sample Reference'],
            'updates': [
                {'date': current_date, 'description': 'Sample update'}
            ],
            'recent_updates': [
                {'date': current_date, 'description': 'Sample recent update'}
            ],

            # Report metadata
            'report_start_date': current_date,
            'report_end_date': current_date,
            'next_report_date': current_date,
            'generator': 'TaskHero AI Template Engine',
            'generated_at': current_datetime
        }