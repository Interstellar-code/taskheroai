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
            
            # Remove placeholder content
            optimized_context = self._remove_placeholder_content(optimized_context)
            
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
    
    def _remove_placeholder_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or replace placeholder content with meaningful defaults."""
        cleaned_context = context.copy()
        
        # Define placeholder patterns to remove or replace
        placeholder_patterns = {
            '[Requirement 1]': '',
            '[Requirement 2]': '',
            '[Requirement 3]': '',
            '[Benefit 1]': '',
            '[Benefit 2]': '',
            '[Benefit 3]': '',
            '[Current 1]': '',
            '[Current 2]': '',
            '[New 1]': '',
            '[New 2]': '',
            '[Migration notes]': '',
            '[Risk 1]': '',
            '[Risk 2]': '',
            '[High/Medium/Low]': '',
            '[Mitigation approach]': ''
        }
        
        # Clean string values
        for key, value in cleaned_context.items():
            if isinstance(value, str):
                for pattern, replacement in placeholder_patterns.items():
                    if pattern in value:
                        cleaned_context[key] = value.replace(pattern, replacement).strip()
            
            elif isinstance(value, list):
                # Clean list items
                cleaned_list = []
                for item in value:
                    if isinstance(item, str):
                        cleaned_item = item
                        for pattern, replacement in placeholder_patterns.items():
                            cleaned_item = cleaned_item.replace(pattern, replacement)
                        if cleaned_item.strip():  # Only keep non-empty items
                            cleaned_list.append(cleaned_item.strip())
                    else:
                        cleaned_list.append(item)
                cleaned_context[key] = cleaned_list
        
        return cleaned_context
    
    def _generate_section_flags(self, included_sections: Set[str]) -> Dict[str, bool]:
        """Generate template flags for section inclusion."""
        return {
            'show_naming_convention': 'naming_convention' in included_sections,
            'show_metadata_legend': 'metadata_legend' in included_sections,
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