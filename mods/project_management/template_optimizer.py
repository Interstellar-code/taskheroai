"""
Template Optimizer Module for Enhanced AI Task Creation

This module optimizes task templates by filtering irrelevant sections,
customizing content based on task type, and eliminating placeholder content.

Part of TASK-044: Improve AI Task Creation System - Post Phase 4 Analysis
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("TaskHeroAI.ProjectManagement.TemplateOptimizer")


@dataclass
class TemplateSection:
    """Represents a template section with its metadata."""
    name: str
    required: bool
    task_types: Set[str]  # Task types this section is relevant for
    conditions: List[str]  # Conditions when this section should be included
    priority: int  # Priority for ordering sections


class TemplateOptimizer:
    """Optimizes task templates based on task type and context."""
    
    def __init__(self):
        """Initialize the template optimizer."""
        self.section_definitions = self._define_template_sections()
        self.task_type_mappings = {
            "Development": "DEV",
            "Bug Fix": "BUG", 
            "Test Case": "TEST",
            "Documentation": "DOC",
            "Design": "DES",
            "Research": "RES",
            "Planning": "PLAN"
        }
        
    def _define_template_sections(self) -> Dict[str, TemplateSection]:
        """Define which sections are relevant for which task types."""
        return {
            'naming_convention': TemplateSection(
                name='naming_convention',
                required=True,
                task_types={'DEV', 'BUG', 'TEST', 'DOC', 'DES', 'RES', 'PLAN'},
                conditions=[],
                priority=1
            ),
            'metadata_legend': TemplateSection(
                name='metadata_legend',
                required=True,
                task_types={'DEV', 'BUG', 'TEST', 'DOC', 'DES', 'RES', 'PLAN'},
                conditions=[],
                priority=2
            ),
            'overview': TemplateSection(
                name='overview',
                required=True,
                task_types={'DEV', 'BUG', 'TEST', 'DOC', 'DES', 'RES', 'PLAN'},
                conditions=[],
                priority=3
            ),
            'flow_diagram': TemplateSection(
                name='flow_diagram',
                required=True,
                task_types={'DEV', 'BUG', 'TEST', 'DOC', 'DES'},
                conditions=[],
                priority=4
            ),
            'implementation_status': TemplateSection(
                name='implementation_status',
                required=True,
                task_types={'DEV', 'BUG', 'TEST', 'DOC', 'DES'},
                conditions=[],
                priority=5
            ),
            'detailed_description': TemplateSection(
                name='detailed_description',
                required=True,
                task_types={'DEV', 'BUG', 'TEST', 'DOC', 'DES', 'RES', 'PLAN'},
                conditions=[],
                priority=6
            ),
            'ui_design': TemplateSection(
                name='ui_design',
                required=False,
                task_types={'DES', 'DEV'},
                conditions=['has_ui_component', 'frontend_task', 'interface_design'],
                priority=7
            ),
            'risk_assessment': TemplateSection(
                name='risk_assessment',
                required=True,
                task_types={'DEV', 'BUG', 'DES', 'RES', 'PLAN'},
                conditions=[],
                priority=8
            ),
            'technical_considerations': TemplateSection(
                name='technical_considerations',
                required=True,
                task_types={'DEV', 'BUG', 'TEST'},
                conditions=[],
                priority=9
            ),
            'time_tracking': TemplateSection(
                name='time_tracking',
                required=True,
                task_types={'DEV', 'BUG', 'TEST', 'DOC', 'DES', 'RES', 'PLAN'},
                conditions=[],
                priority=10
            ),
            'references': TemplateSection(
                name='references',
                required=True,
                task_types={'DEV', 'BUG', 'TEST', 'DOC', 'DES', 'RES', 'PLAN'},
                conditions=[],
                priority=11
            ),
            'dependencies': TemplateSection(
                name='dependencies',
                required=True,
                task_types={'DEV', 'BUG', 'TEST', 'DOC', 'DES'},
                conditions=[],
                priority=12
            ),
            'testing': TemplateSection(
                name='testing',
                required=False,
                task_types={'DEV', 'BUG'},
                conditions=['requires_testing', 'development_task'],
                priority=13
            )
        }
    
    def optimize_template_context(self, context: Dict[str, Any], task_type: str, 
                                task_description: str = "") -> Dict[str, Any]:
        """Optimize template context by filtering sections and customizing content.
        
        Args:
            context: Original template context
            task_type: Type of task (Development, Bug Fix, etc.)
            task_description: Description of the task for context analysis
            
        Returns:
            Optimized template context
        """
        try:
            # Convert task type to abbreviation
            task_type_abbrev = self.task_type_mappings.get(task_type, task_type)
            
            # Determine which sections to include
            included_sections = self._determine_included_sections(
                task_type_abbrev, task_description, context
            )
            
            # Filter context based on included sections
            optimized_context = self._filter_context_sections(context, included_sections)
            
            # Customize content based on task type
            optimized_context = self._customize_content_by_task_type(
                optimized_context, task_type_abbrev, task_description
            )
            
            # TASK-044 IMPROVEMENT: Enhanced placeholder content removal
            optimized_context = self._remove_placeholder_content_enhanced(optimized_context)
            
            # TASK-044 IMPROVEMENT: Remove empty or irrelevant sections
            optimized_context = self._remove_empty_sections(optimized_context, task_type_abbrev, task_description)
            
            # TASK-044 IMPROVEMENT: Remove sections with only placeholder content
            optimized_context = self._remove_placeholder_only_sections(optimized_context)
            
            # TASK-044 IMPROVEMENT: Handle flow diagram relevance
            optimized_context = self._handle_flow_diagram_relevance(optimized_context, task_type_abbrev, task_description)
            
            # TASK-044 IMPROVEMENT: Handle UI section relevance
            optimized_context = self._handle_ui_section_relevance(optimized_context, task_type_abbrev, task_description)
            
            # Add section control flags
            optimized_context.update(self._generate_section_flags(included_sections))
            
            logger.info(f"Template optimized for {task_type_abbrev} task with {len(included_sections)} sections")
            return optimized_context
            
        except Exception as e:
            logger.error(f"Error optimizing template context: {e}")
            return context  # Return original context on error
    
    def _determine_included_sections(self, task_type: str, description: str, 
                                   context: Dict[str, Any]) -> Set[str]:
        """Determine which sections should be included in the template."""
        included_sections = set()
        
        for section_name, section_def in self.section_definitions.items():
            # Include if required for this task type
            if section_def.required and task_type in section_def.task_types:
                included_sections.add(section_name)
                continue
            
            # Include if task type matches and no conditions
            if task_type in section_def.task_types and not section_def.conditions:
                included_sections.add(section_name)
                continue
            
            # Check conditions for optional sections
            if section_def.conditions:
                if self._check_section_conditions(section_def.conditions, description, context):
                    included_sections.add(section_name)
        
        return included_sections
    
    def _check_section_conditions(self, conditions: List[str], description: str, 
                                context: Dict[str, Any]) -> bool:
        """Check if conditions are met for including a section."""
        description_lower = description.lower()
        
        for condition in conditions:
            if condition == 'has_ui_component':
                ui_keywords = ['ui', 'interface', 'frontend', 'design', 'layout', 'component']
                if any(keyword in description_lower for keyword in ui_keywords):
                    return True
                    
            elif condition == 'frontend_task':
                frontend_keywords = ['frontend', 'ui', 'ux', 'interface', 'web', 'react', 'vue', 'angular']
                if any(keyword in description_lower for keyword in frontend_keywords):
                    return True
                    
            elif condition == 'interface_design':
                design_keywords = ['design', 'wireframe', 'mockup', 'layout', 'visual']
                if any(keyword in description_lower for keyword in design_keywords):
                    return True
                    
            elif condition == 'requires_testing':
                # Always include testing for development tasks
                return True
                
            elif condition == 'development_task':
                dev_keywords = ['implement', 'create', 'build', 'develop', 'add']
                if any(keyword in description_lower for keyword in dev_keywords):
                    return True
        
        return False
    
    def _filter_context_sections(self, context: Dict[str, Any], 
                               included_sections: Set[str]) -> Dict[str, Any]:
        """Filter context to only include relevant sections."""
        filtered_context = context.copy()
        
        # Section control flags
        section_flags = {
            'show_naming_convention': 'naming_convention' in included_sections,
            'show_metadata_legend': 'metadata_legend' in included_sections,
            'show_implementation_analysis': 'detailed_description' in included_sections,
            'show_ui_design': 'ui_design' in included_sections,
            'show_risk_assessment': 'risk_assessment' in included_sections,
            'show_technical_considerations': 'technical_considerations' in included_sections,
            'show_testing': 'testing' in included_sections
        }
        
        filtered_context.update(section_flags)
        return filtered_context
    
    def _customize_content_by_task_type(self, context: Dict[str, Any], 
                                      task_type: str, description: str) -> Dict[str, Any]:
        """Customize content based on task type."""
        customized_context = context.copy()
        
        # Customize flow diagram based on task type
        if task_type == 'DEV':
            customized_context['flow_description'] = self._generate_dev_flow_description(description)
        elif task_type == 'BUG':
            customized_context['flow_description'] = self._generate_bug_flow_description(description)
        elif task_type == 'TEST':
            customized_context['flow_description'] = self._generate_test_flow_description(description)
        elif task_type == 'DOC':
            customized_context['flow_description'] = self._generate_doc_flow_description(description)
        
        # Customize technical considerations based on task type
        if task_type in ['DEV', 'BUG']:
            customized_context['technical_considerations'] = self._generate_technical_considerations(
                task_type, description
            )
        
        # Customize success criteria based on task type
        customized_context['success_criteria'] = self._generate_success_criteria(task_type, description)
        
        return customized_context
    
    def _generate_dev_flow_description(self, description: str) -> str:
        """Generate development-specific flow description."""
        if 'install' in description.lower() or 'setup' in description.lower():
            return "User workflow for installation and setup process implementation"
        elif 'api' in description.lower():
            return "User workflow for API development and integration"
        elif 'ui' in description.lower() or 'interface' in description.lower():
            return "User workflow for UI component development and interaction"
        else:
            return f"User workflow for {description.lower()} implementation"
    
    def _generate_bug_flow_description(self, description: str) -> str:
        """Generate bug fix-specific flow description."""
        return "User workflow for bug reproduction, diagnosis, and resolution"
    
    def _generate_test_flow_description(self, description: str) -> str:
        """Generate testing-specific flow description."""
        return "User workflow for test case execution and validation"
    
    def _generate_doc_flow_description(self, description: str) -> str:
        """Generate documentation-specific flow description."""
        return "User workflow for documentation creation and review"
    
    def _generate_technical_considerations(self, task_type: str, description: str) -> str:
        """Generate task-type specific technical considerations."""
        considerations = []
        
        if task_type == 'DEV':
            if 'install' in description.lower() or 'setup' in description.lower():
                considerations.extend([
                    "Cross-platform compatibility for installation scripts",
                    "Error handling and recovery mechanisms",
                    "User input validation and sanitization",
                    "Configuration file management and validation"
                ])
            elif 'api' in description.lower():
                considerations.extend([
                    "API versioning and backward compatibility",
                    "Authentication and authorization",
                    "Rate limiting and throttling",
                    "Error handling and status codes"
                ])
            else:
                considerations.extend([
                    "Code modularity and reusability",
                    "Performance optimization",
                    "Error handling and logging",
                    "Testing and validation"
                ])
        
        elif task_type == 'BUG':
            considerations.extend([
                "Root cause analysis and impact assessment",
                "Regression testing to prevent reoccurrence",
                "Backward compatibility maintenance",
                "Performance impact of the fix"
            ])
        
        return '\n'.join(f"- {consideration}" for consideration in considerations)
    
    def _generate_success_criteria(self, task_type: str, description: str) -> List[Dict[str, Any]]:
        """Generate task-type specific success criteria."""
        criteria = []
        
        if task_type == 'DEV':
            if 'install' in description.lower() or 'setup' in description.lower():
                criteria.extend([
                    {"description": "Installation script runs successfully on target platforms", "completed": False},
                    {"description": "User configuration is properly collected and validated", "completed": False},
                    {"description": "Settings are correctly stored in configuration files", "completed": False},
                    {"description": "Application starts successfully after setup", "completed": False}
                ])
            else:
                criteria.extend([
                    {"description": "All functional requirements are implemented", "completed": False},
                    {"description": "Code passes all tests and quality checks", "completed": False},
                    {"description": "Documentation is complete and accurate", "completed": False}
                ])
        
        elif task_type == 'BUG':
            criteria.extend([
                {"description": "Bug is reproduced and root cause identified", "completed": False},
                {"description": "Fix is implemented and tested", "completed": False},
                {"description": "Regression tests pass", "completed": False},
                {"description": "Fix is verified in production environment", "completed": False}
            ])
        
        elif task_type == 'TEST':
            criteria.extend([
                {"description": "Test cases cover all specified scenarios", "completed": False},
                {"description": "Tests execute successfully and provide clear results", "completed": False},
                {"description": "Test documentation is complete", "completed": False}
            ])
        
        elif task_type == 'DOC':
            criteria.extend([
                {"description": "Documentation is accurate and up-to-date", "completed": False},
                {"description": "Content is clear and well-structured", "completed": False},
                {"description": "Examples and code snippets are functional", "completed": False}
            ])
        
        return criteria
    
    def _remove_placeholder_content_enhanced(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced removal of placeholder content with better detection and handling."""
        cleaned_context = context.copy()
        
        # TASK-044 IMPROVEMENT: Remove naming convention section (for AI prompts only)
        cleaned_context['show_naming_convention'] = False
        cleaned_context['show_metadata_legend'] = False
        
        # Define comprehensive placeholder patterns to remove
        placeholder_patterns = {
            # Requirement placeholders
            '[Requirement 1]': '',
            '[Requirement 2]': '',
            '[Requirement 3]': '',
            '[Requirement 4]': '',
            '[Requirement 5]': '',
            
            # Benefit placeholders
            '[Benefit 1]': '',
            '[Benefit 2]': '',
            '[Benefit 3]': '',
            '[Benefit 4]': '',
            '[Benefit 5]': '',
            
            # TASK-044: Default content that should be removed
            'Consider performance, security, maintainability, and scalability requirements.': '',
            'Define how application state will be managed and synchronized.': '',
            'Plan component structure for reusability and maintainability.': '',
            'Identify performance benchmarks and optimization strategies.': '',
            'Current implementation will be analyzed during planning phase': '',
            'Existing components will be mapped and evaluated': '',
            'Current limitations will be identified and addressed': '',
            'New features will be implemented according to requirements': '',
            'Additional enhancements will be considered': '',
            'Future extensibility will be planned': '',
            'Migration strategy will be developed if needed': '',
            'Backward compatibility strategy will be defined': '',
            'Risk mitigation strategies will be implemented': '',
            'Related tasks and technical dependencies will be identified during planning phase.': '',
            'Testing strategy will be developed based on implementation requirements.': '',
            
            # Default UI design content
            'UI design considerations will be defined during implementation phase.': '',
            'Follow TaskHero AI design system color palette': '',
            'Use system default typography standards': '',
            'Follow 8px grid system for consistent spacing': '',
            'Utilize existing component library where applicable': '',
            'Use consistent icon set from design system': '',
            
            # Default technical considerations
            'Data persistence requirements will be defined based on functionality needs': '',
            'State synchronization will follow established patterns': '',
            'Components will be designed for maximum reusability': '',
            'Integration will follow existing architectural patterns': '',
            'Memory usage will be optimized for performance': '',
            'Loading performance will be optimized where applicable': '',
            'Cross-browser compatibility will be ensured': '',
            'Backward compatibility will be maintained where possible': '',
            'Integration compatibility with existing systems will be verified': '',
            
            # Generic placeholders
            '[Current 1]': '',
            '[Current 2]': '',
            '[New 1]': '',
            '[New 2]': '',
            '[Migration notes]': '',
            '[Risk 1]': '',
            '[Risk 2]': '',
            '[High/Medium/Low]': '',
            '[Mitigation approach]': '',
            
            # Template placeholders
            'TASK-XXX': '',
            'DUE-DATE': '',
            'PRIORITY': '',
            'STATUS': '',
            'ASSIGNEE': '',
            'TASK-TYPE': '',
            'SEQUENCE': '',
            'TAGS': '',
            '[Small/Medium/Large]': '',
            '[Epic name if applicable]': '',
            
            # Description placeholders
            '[Concise summary of what this task accomplishes and why it is needed]': '',
            '[Specific functionality that must be implemented or changed]': '',
            '[Why this task is important and what value it provides]': '',
            '[Specific success criterion 1]': '',
            '[Specific success criterion 2]': '',
            '[Specific success criterion 3]': '',
            
            # Implementation placeholders
            '[Main Step Title]': '',
            '[Detailed sub-step description]': '',
            '[Detailed description of the task, including its purpose, benefits, and any relevant background information]': '',
            
            # Technical placeholders
            '[Any technical considerations, potential challenges, or architectural decisions]': '',
            '[State management approach and rationale]': '',
            '[Data persistence requirements]': '',
            '[State synchronization considerations]': '',
            
            # UI placeholders
            '[Brief description of the UI changes and design goals]': '',
            '[Primary: #color, Secondary: #color, etc.]': '',
            '[Font family, sizes, weights]': '',
            '[Padding/margin standards]': '',
            '[shadcn/ui components used]': '',
            '[Icon library and specific icons]': '',
            
            # Reference placeholders
            '[External Documentation/API Reference 1]': '',
            '[External Documentation/API Reference 2]': '',
            '[Internal Codebase Reference 1]': '',
            '[Internal Codebase Reference 2]': '',
            '[Design/Mockup References]': '',
            '[Related Tasks/Issues]': '',
            
            # Time tracking placeholders
            '[X]': '',
            '[To be filled]': '',
            
            # Dependency placeholders
            '[Task ID] - [Task Title] - [Status]': '',
            '[Package/Tool 1] - [Version/Requirement]': '',
            '[Package/Tool 2] - [Version/Requirement]': '',
            
            # Implementation step placeholders
            '[Main Step Title]': '',
            '[Detailed sub-step description]': '',
            'YYYY-MM-DD': '',
            
            # Technical consideration placeholders
            '[State management approach and rationale]': '',
            '[Data persistence requirements]': '',
            '[State synchronization considerations]': '',
            '[Component structure and organization]': '',
            '[Reusability and modularity considerations]': '',
            '[Integration patterns with existing codebase]': '',
            '[Performance requirements and optimizations]': '',
            '[Memory management considerations]': '',
            '[Loading and rendering optimizations]': '',
            '[Browser/platform compatibility requirements]': '',
            '[Backward compatibility with existing features]': '',
            '[Integration compatibility with external systems]': '',
            
            # Description placeholders
            '[Describe current state/implementation]': '',
            '[Key components and their roles]': '',
            '[Current limitations or issues]': '',
            '[Feature 1 and its benefits]': '',
            '[Feature 2 and its benefits]': '',
            '[Feature 3 and its benefits]': '',
            '[Approach for transitioning from current to new]': '',
            '[Backward compatibility considerations]': '',
            '[Risk mitigation strategies]': '',
        }
        
        # Clean string values
        for key, value in cleaned_context.items():
            if isinstance(value, str):
                original_value = value
                for pattern, replacement in placeholder_patterns.items():
                    if pattern in value:
                        value = value.replace(pattern, replacement)
                
                # Remove lines that are only placeholders
                lines = value.split('\n')
                cleaned_lines = []
                for line in lines:
                    line_stripped = line.strip()
                    # Skip lines that are only placeholder patterns
                    if (line_stripped.startswith('[') and line_stripped.endswith(']') and 
                        len(line_stripped) > 10):  # Likely a placeholder
                        continue
                    # Skip lines with placeholder patterns in brackets
                    if ('[' in line_stripped and ']' in line_stripped and 
                        any(placeholder in line_stripped for placeholder in [
                            '[Main Step Title]', '[Detailed sub-step description]',
                            '[State management approach', '[Component structure',
                            '[Performance requirements', '[Browser/platform compatibility',
                            '[Describe current state', '[Feature 1 and its benefits]',
                            '[Approach for transitioning', '[Current 1]', '[New 1]',
                            '[Migration notes]', '[Task ID]', '[Task Title]', '[Status]',
                            '[Package/Tool', '[Version/Requirement]', '[External Documentation',
                            '[Internal Codebase Reference', '[Design/Mockup References]',
                            '[Related Tasks/Issues]', '[X]', '[To be filled]'
                        ])):
                        continue
                    # Skip lines with only dashes or equals (template separators)
                    if line_stripped and not set(line_stripped) <= {'-', '=', ' '}:
                        cleaned_lines.append(line)
                
                cleaned_context[key] = '\n'.join(cleaned_lines).strip()
            
            elif isinstance(value, list):
                # Clean list items and remove empty/placeholder items
                cleaned_list = []
                for item in value:
                    if isinstance(item, str):
                        cleaned_item = item
                        for pattern, replacement in placeholder_patterns.items():
                            cleaned_item = cleaned_item.replace(pattern, replacement)
                        
                        # Only keep non-empty, non-placeholder items
                        cleaned_item = cleaned_item.strip()
                        if (cleaned_item and 
                            not (cleaned_item.startswith('[') and cleaned_item.endswith(']')) and
                            not cleaned_item.lower().startswith('requirement') and
                            not cleaned_item.lower().startswith('benefit')):
                            cleaned_list.append(cleaned_item)
                    elif isinstance(item, dict):
                        # Clean dictionary items
                        cleaned_dict = {}
                        for k, v in item.items():
                            if isinstance(v, str):
                                cleaned_v = v
                                for pattern, replacement in placeholder_patterns.items():
                                    cleaned_v = cleaned_v.replace(pattern, replacement)
                                if cleaned_v.strip():
                                    cleaned_dict[k] = cleaned_v.strip()
                            else:
                                cleaned_dict[k] = v
                        if cleaned_dict:
                            cleaned_list.append(cleaned_dict)
                    else:
                        cleaned_list.append(item)
                
                cleaned_context[key] = cleaned_list
        
        return cleaned_context
    
    def _remove_placeholder_only_sections(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sections that contain only placeholder content."""
        cleaned_context = context.copy()
        
        # Check implementation steps for placeholder-only content
        if 'implementation_steps' in cleaned_context:
            steps = cleaned_context['implementation_steps']
            if isinstance(steps, list):
                cleaned_steps = []
                for step in steps:
                    if isinstance(step, dict):
                        # Check if step title is a placeholder
                        title = step.get('title', '')
                        if (title and not any(placeholder in title for placeholder in [
                            '[Main Step Title]', 'Step 1:', 'Step 2:', 'Step 3:'
                        ])):
                            # Check substeps for placeholder content
                            substeps = step.get('substeps', [])
                            cleaned_substeps = []
                            for substep in substeps:
                                if isinstance(substep, dict):
                                    desc = substep.get('description', '')
                                    if (desc and not any(placeholder in desc for placeholder in [
                                        '[Detailed sub-step description]', '[Sub-step'
                                    ])):
                                        cleaned_substeps.append(substep)
                            
                            if cleaned_substeps:
                                step_copy = step.copy()
                                step_copy['substeps'] = cleaned_substeps
                                cleaned_steps.append(step_copy)
                
                if cleaned_steps:
                    cleaned_context['implementation_steps'] = cleaned_steps
                else:
                    cleaned_context['implementation_steps'] = None
                    cleaned_context['show_implementation_steps'] = False
                    logger.info("Removed implementation steps with only placeholder content")
        
        return cleaned_context
    
    def _remove_empty_sections(self, context: Dict[str, Any], task_type: str, description: str) -> Dict[str, Any]:
        """Remove sections that have no meaningful content."""
        cleaned_context = context.copy()
        
        # Check functional requirements
        if 'functional_requirements_list' in cleaned_context:
            req_list = cleaned_context['functional_requirements_list']
            if not req_list or (isinstance(req_list, list) and len(req_list) == 0):
                # Remove the entire functional requirements section
                cleaned_context['functional_requirements_list'] = None
                cleaned_context['show_functional_requirements'] = False
                logger.info("Removed empty functional requirements section")
        
        # Check benefits list
        if 'benefits_list' in cleaned_context:
            benefits = cleaned_context['benefits_list']
            if not benefits or (isinstance(benefits, list) and len(benefits) == 0):
                cleaned_context['benefits_list'] = None
                cleaned_context['show_benefits'] = False
                logger.info("Removed empty benefits section")
        
        # Check implementation steps
        if 'implementation_steps' in cleaned_context:
            steps = cleaned_context['implementation_steps']
            if not steps or (isinstance(steps, list) and len(steps) == 0):
                cleaned_context['implementation_steps'] = None
                cleaned_context['show_implementation_steps'] = False
                logger.info("Removed empty implementation steps section")
            elif isinstance(steps, list) and len(steps) > 0:
                # TASK-044: Check for generic default implementation steps
                generic_titles = [
                    'Requirements Analysis',
                    'Design and Planning', 
                    'Implementation'
                ]
                
                # If steps match the generic pattern, mark for replacement
                if (len(steps) == 3 and 
                    all(isinstance(step, dict) and step.get('title') in generic_titles for step in steps)):
                    # Check if substeps are also generic
                    generic_substeps = [
                        'Review requirements and specifications',
                        'Identify key stakeholders and dependencies',
                        'Define acceptance criteria',
                        'Create technical design document',
                        'Plan implementation approach',
                        'Identify potential risks and mitigation strategies',
                        'Implement core functionality',
                        'Add error handling and validation',
                        'Write unit tests'
                    ]
                    
                    all_generic = True
                    for step in steps:
                        substeps = step.get('substeps', [])
                        for substep in substeps:
                            if isinstance(substep, dict) and substep.get('description') not in generic_substeps:
                                all_generic = False
                                break
                        if not all_generic:
                            break
                    
                    if all_generic:
                        # Replace with task-specific steps or remove
                        cleaned_context['implementation_steps'] = None
                        cleaned_context['show_implementation_steps'] = False
                        logger.info("Removed generic implementation steps")
        
        # Check risks
        if 'risks' in cleaned_context:
            risks = cleaned_context['risks']
            if not risks or (isinstance(risks, list) and len(risks) == 0):
                cleaned_context['risks'] = None
                cleaned_context['show_risk_assessment'] = False
                logger.info("Removed empty risk assessment section")
        
        # TASK-044: Check for generic flow diagram steps
        if 'flow_steps' in cleaned_context:
            flow_steps = cleaned_context['flow_steps']
            if isinstance(flow_steps, list) and len(flow_steps) > 0:
                # Check if these are the default generic steps
                generic_steps = [
                    'User initiates action',
                    'System validates input', 
                    'Process request',
                    'Return result'
                ]
                
                # If flow steps match the generic pattern, remove them
                if (len(flow_steps) == 4 and 
                    all(isinstance(step, dict) and step.get('title') in generic_steps for step in flow_steps)):
                    cleaned_context['flow_steps'] = None
                    cleaned_context['show_flow_diagram'] = False
                    logger.info("Removed generic flow diagram steps")
        
        return cleaned_context
    
    def _handle_flow_diagram_relevance(self, context: Dict[str, Any], task_type: str, description: str) -> Dict[str, Any]:
        """Handle flow diagram relevance - generate specific diagram or mark as N/A."""
        updated_context = context.copy()
        
        # Determine if flow diagram is relevant
        flow_relevant = self._is_flow_diagram_relevant(task_type, description)
        
        if not flow_relevant:
            # Mark flow diagram as N/A
            updated_context['flow_description'] = "N/A - Flow diagram not applicable for this task type."
            updated_context['show_flow_diagram'] = False
            updated_context['flow_steps'] = []
            logger.info("Flow diagram marked as N/A for task type")
        else:
            # Generate task-specific flow diagram
            flow_context = self.generate_task_specific_flow_diagram(task_type, description, context)
            updated_context.update(flow_context)
            updated_context['show_flow_diagram'] = True
            logger.info("Generated task-specific flow diagram")
        
        return updated_context
    
    def _handle_ui_section_relevance(self, context: Dict[str, Any], task_type: str, description: str) -> Dict[str, Any]:
        """Handle UI section relevance - remove entire UI section if not relevant."""
        updated_context = context.copy()
        
        # Determine if UI design is relevant
        ui_relevant = self._is_ui_design_relevant(task_type, description)
        
        if not ui_relevant:
            # Remove all UI-related variables
            ui_keys_to_remove = [
                'ui_design_overview', 'ui_layout', 'ui_colors', 'ui_typography', 
                'ui_spacing', 'ui_components', 'ui_icons', 'design_references',
                'ui_wireframes', 'ui_mockups', 'ui_design_system'
            ]
            
            for key in ui_keys_to_remove:
                if key in updated_context:
                    del updated_context[key]
            
            # Set UI section flags to False
            updated_context['show_ui_design'] = False
            updated_context['show_wireframes'] = False
            updated_context['show_ui_specifications'] = False
            
            logger.info("Removed UI design section - not relevant for this task type")
        else:
            updated_context['show_ui_design'] = True
            logger.info("Retained UI design section - relevant for this task type")
        
        return updated_context
    
    def _is_flow_diagram_relevant(self, task_type: str, description: str) -> bool:
        """Determine if a flow diagram is relevant for this task."""
        # Flow diagrams are relevant for tasks that involve user interactions or processes
        relevant_task_types = {'DEV', 'DES', 'TEST'}
        
        if task_type not in relevant_task_types:
            return False
        
        # Check description for workflow-related keywords
        workflow_keywords = [
            'workflow', 'process', 'user', 'interaction', 'flow', 'step', 'sequence',
            'journey', 'navigation', 'interface', 'form', 'submit', 'validation',
            'authentication', 'login', 'registration', 'checkout', 'payment'
        ]
        
        description_lower = description.lower()
        has_workflow_keywords = any(keyword in description_lower for keyword in workflow_keywords)
        
        # Special case: Installation and setup scripts DO have user workflows
        installation_keywords = ['install', 'setup', 'script', 'enhance']
        has_installation_keywords = any(keyword in description_lower for keyword in installation_keywords)
        
        # If it's an installation/setup task, it should have a flow diagram
        if has_installation_keywords:
            return True
        
        # Documentation-only tasks typically don't need flow diagrams
        documentation_only_keywords = [
            'documentation', 'readme', 'comment', 'logging', 'monitoring'
        ]
        
        has_documentation_only_keywords = any(keyword in description_lower for keyword in documentation_only_keywords)
        
        # Return True if has workflow keywords and isn't documentation-only
        return has_workflow_keywords and not has_documentation_only_keywords
    
    def _is_ui_design_relevant(self, task_type: str, description: str) -> bool:
        """Determine if UI design sections are relevant for this task."""
        # UI design is primarily relevant for Design and some Development tasks
        if task_type == 'DES':
            return True
        
        if task_type != 'DEV':
            return False
        
        # Check description for UI-related keywords
        ui_keywords = [
            'ui', 'ux', 'interface', 'frontend', 'design', 'layout', 'component',
            'style', 'css', 'html', 'react', 'vue', 'angular', 'web', 'page',
            'form', 'button', 'modal', 'dialog', 'menu', 'navigation', 'dashboard',
            'wireframe', 'mockup', 'prototype', 'visual', 'theme', 'responsive'
        ]
        
        description_lower = description.lower()
        has_ui_keywords = any(keyword in description_lower for keyword in ui_keywords)
        
        # Backend/infrastructure tasks typically don't need UI design
        backend_keywords = [
            'api', 'backend', 'server', 'database', 'sql', 'migration', 'schema',
            'authentication', 'authorization', 'security', 'encryption', 'hash',
            'algorithm', 'data structure', 'performance', 'optimization', 'cache',
            'queue', 'worker', 'job', 'cron', 'schedule', 'batch', 'script',
            'install', 'setup', 'configuration', 'environment', 'deployment',
            'docker', 'kubernetes', 'aws', 'cloud', 'infrastructure'
        ]
        
        has_backend_keywords = any(keyword in description_lower for keyword in backend_keywords)
        
        # Return True if has UI keywords and doesn't have backend keywords
        return has_ui_keywords and not has_backend_keywords
    
    def _generate_section_flags(self, included_sections: Set[str]) -> Dict[str, bool]:
        """Generate template flags for section inclusion."""
        return {
            'show_naming_convention': False,  # Always hide - for AI prompts only
            'show_metadata_legend': False,    # Always hide - for AI prompts only
            'show_implementation_analysis': 'detailed_description' in included_sections,
            'show_ui_design': 'ui_design' in included_sections,
            'show_risk_assessment': 'risk_assessment' in included_sections,
            'show_technical_considerations': 'technical_considerations' in included_sections,
            'show_testing': 'testing' in included_sections,
            'component_mapping': False,  # Disable by default
            'database_changes': False    # Disable by default
        }
    
    def generate_task_specific_flow_diagram(self, task_type: str, description: str, 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate task-specific flow diagram steps."""
        flow_steps = []
        
        if task_type == 'DEV' and ('install' in description.lower() or 'setup' in description.lower()):
            flow_steps = [
                {"title": "User runs installation script"},
                {"title": "System checks prerequisites"},
                {"title": "User provides configuration input"},
                {"title": "System validates and stores settings"},
                {"title": "Application starts successfully"}
            ]
        
        elif task_type == 'BUG':
            flow_steps = [
                {"title": "User reports bug"},
                {"title": "Developer reproduces issue"},
                {"title": "Root cause analysis"},
                {"title": "Fix implementation"},
                {"title": "Testing and verification"}
            ]
        
        elif task_type == 'TEST':
            flow_steps = [
                {"title": "Test case preparation"},
                {"title": "Test execution"},
                {"title": "Result validation"},
                {"title": "Report generation"}
            ]
        
        else:
            # Generic development flow
            flow_steps = [
                {"title": "User initiates task"},
                {"title": "System processes request"},
                {"title": "User reviews results"},
                {"title": "Task completion"}
            ]
        
        return {"flow_steps": flow_steps}
    
    def validate_optimized_template(self, context: Dict[str, Any]) -> List[str]:
        """Validate the optimized template for quality issues."""
        issues = []
        
        # Check for remaining placeholder content
        placeholder_indicators = ['[', ']', 'PLACEHOLDER', 'TODO', 'FIXME']
        for key, value in context.items():
            if isinstance(value, str):
                for indicator in placeholder_indicators:
                    if indicator in value and not key.startswith('ui_'):  # UI sections may have legitimate brackets
                        issues.append(f"Placeholder content found in {key}: {value[:50]}...")
        
        # Check for empty required fields
        required_fields = ['title', 'description', 'task_type', 'priority']
        for field in required_fields:
            if not context.get(field):
                issues.append(f"Required field '{field}' is empty")
        
        # Check for duplicate content
        if context.get('technical_considerations') == context.get('detailed_description'):
            issues.append("Duplicate content found between technical_considerations and detailed_description")
        
        return issues 