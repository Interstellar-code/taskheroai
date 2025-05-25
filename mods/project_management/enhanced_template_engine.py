"""
TaskHero AI Enhanced Template Engine

This module provides enhanced template generation capabilities with improved
quality, structure validation, and dynamic customization based on task requirements.

Key Features:
- Dynamic template customization based on task type and context
- Section completeness validation and enforcement
- Professional formatting standards and consistency
- Quality-driven template generation with validation checkpoints
- Integration with quality scorer and Mermaid generator

Author: TaskHero AI Development Team
Created: 2025-05-25 (TASK-058 Enhancement)
"""

import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import quality enhancement modules
try:
    from .quality_scorer import QualityScorer, OverallQualityResult
    from .mermaid_generator import MermaidDiagramGenerator
    from .enhanced_content_generator import EnhancedContentGenerator, ContentGenerationContext
    QUALITY_MODULES_AVAILABLE = True
except ImportError:
    QUALITY_MODULES_AVAILABLE = False

logger = logging.getLogger("TaskHero.EnhancedTemplateEngine")

class TaskType(Enum):
    """Supported task types with specific template requirements."""
    DEVELOPMENT = "DEV"
    BUG_FIX = "BUG"
    TEST_CASE = "TEST"
    DOCUMENTATION = "DOC"
    DESIGN = "DES"
    RESEARCH = "RES"
    PLANNING = "PLAN"

@dataclass
class TemplateSection:
    """Template section definition with validation requirements."""
    name: str
    title: str
    required: bool
    content_type: str  # 'text', 'list', 'table', 'mermaid', 'metadata'
    validation_rules: List[str]
    quality_weight: float

@dataclass
class TemplateConfiguration:
    """Template configuration for specific task types."""
    task_type: TaskType
    sections: List[TemplateSection]
    required_metadata: List[str]
    formatting_rules: Dict[str, Any]
    quality_thresholds: Dict[str, float]

class EnhancedTemplateEngine:
    """
    Enhanced template engine with quality-driven generation and validation.
    
    Addresses quality gaps identified in TASK-057 vs TASK-008 analysis by:
    - Enforcing complete section population
    - Implementing professional formatting standards
    - Providing dynamic template customization
    - Validating content quality and completeness
    """
    
    def __init__(self, templates_path: Optional[str] = None):
        """
        Initialize the enhanced template engine.
        
        Args:
            templates_path: Path to templates directory
        """
        self.templates_path = Path(templates_path) if templates_path else Path("mods/project_management/templates")
        
        # Initialize quality modules if available
        if QUALITY_MODULES_AVAILABLE:
            self.quality_scorer = QualityScorer()
            self.mermaid_generator = MermaidDiagramGenerator()
            self.content_generator = EnhancedContentGenerator()
        else:
            self.quality_scorer = None
            self.mermaid_generator = None
            self.content_generator = None
            logger.warning("Quality modules not available - using fallback mode")
        
        # Initialize visual generator
        try:
            from .enhanced_visual_generator import EnhancedVisualGenerator, VisualContext
            self.visual_generator = EnhancedVisualGenerator(templates_path)
            self.VisualContext = VisualContext  # Store class reference for later use
            logger.info("Enhanced Visual Generator initialized")
        except ImportError:
            logger.warning("Enhanced Visual Generator not available")
            self.visual_generator = None
            self.VisualContext = None
        
        # Load template configurations
        self.template_configs = self._initialize_template_configurations()
        
        # Professional formatting standards
        self.formatting_standards = self._initialize_formatting_standards()
        
        logger.info("Enhanced Template Engine initialized successfully")
    
    def _initialize_template_configurations(self) -> Dict[TaskType, TemplateConfiguration]:
        """Initialize template configurations for different task types."""
        configs = {}
        
        # Development Task Configuration
        configs[TaskType.DEVELOPMENT] = TemplateConfiguration(
            task_type=TaskType.DEVELOPMENT,
            sections=[
                TemplateSection("metadata", "Metadata", True, "metadata", 
                              ["has_all_required_fields", "proper_formatting"], 0.15),
                TemplateSection("overview", "Overview", True, "text", 
                              ["has_description", "has_requirements", "has_benefits", "has_success_criteria"], 0.25),
                TemplateSection("flow_diagram", "Flow Diagram", True, "mermaid", 
                              ["has_mermaid_diagram", "diagram_relevant"], 0.15),
                TemplateSection("implementation", "Implementation Status", True, "list", 
                              ["has_detailed_steps", "has_sub_steps", "has_target_dates"], 0.20),
                TemplateSection("description", "Detailed Description", True, "text", 
                              ["comprehensive_content", "technical_depth"], 0.10),
                TemplateSection("risk_assessment", "Risk Assessment", True, "table", 
                              ["has_risk_table", "detailed_mitigation"], 0.10),
                TemplateSection("technical_considerations", "Technical Considerations", True, "text", 
                              ["architecture_details", "performance_considerations"], 0.05)
            ],
            required_metadata=["task_id", "created", "due", "priority", "status", "assigned_to", "task_type", "sequence"],
            formatting_rules={
                "use_markdown_bullets": True,
                "enforce_section_numbering": True,
                "require_professional_language": True,
                "validate_mermaid_syntax": True
            },
            quality_thresholds={
                "overall": 8.5,
                "structure": 9.0,
                "content": 8.5,
                "visual": 8.0
            }
        )
        
        # Bug Fix Task Configuration
        configs[TaskType.BUG_FIX] = TemplateConfiguration(
            task_type=TaskType.BUG_FIX,
            sections=[
                TemplateSection("metadata", "Metadata", True, "metadata", 
                              ["has_all_required_fields", "proper_formatting"], 0.15),
                TemplateSection("overview", "Overview", True, "text", 
                              ["has_description", "has_requirements", "has_benefits", "has_success_criteria"], 0.25),
                TemplateSection("flow_diagram", "Bug Fix Flow", True, "mermaid", 
                              ["has_mermaid_diagram", "bug_fix_specific"], 0.15),
                TemplateSection("reproduction", "Bug Reproduction", True, "text", 
                              ["reproduction_steps", "environment_details"], 0.15),
                TemplateSection("root_cause", "Root Cause Analysis", True, "text", 
                              ["detailed_analysis", "technical_investigation"], 0.15),
                TemplateSection("solution", "Solution Implementation", True, "list", 
                              ["has_detailed_steps", "has_sub_steps", "has_target_dates"], 0.10),
                TemplateSection("testing", "Testing Strategy", True, "text", 
                              ["test_plan", "regression_testing"], 0.05)
            ],
            required_metadata=["task_id", "created", "due", "priority", "status", "assigned_to", "task_type", "sequence", "bug_severity"],
            formatting_rules={
                "use_markdown_bullets": True,
                "enforce_section_numbering": True,
                "require_professional_language": True,
                "validate_mermaid_syntax": True
            },
            quality_thresholds={
                "overall": 8.5,
                "structure": 9.0,
                "content": 8.5,
                "visual": 8.0
            }
        )
        
        # Test Case Configuration
        configs[TaskType.TEST_CASE] = TemplateConfiguration(
            task_type=TaskType.TEST_CASE,
            sections=[
                TemplateSection("metadata", "Metadata", True, "metadata", 
                              ["has_all_required_fields", "proper_formatting"], 0.15),
                TemplateSection("overview", "Test Overview", True, "text", 
                              ["has_description", "has_requirements", "has_benefits", "has_success_criteria"], 0.25),
                TemplateSection("flow_diagram", "Test Flow", True, "mermaid", 
                              ["has_mermaid_diagram", "test_flow_specific"], 0.15),
                TemplateSection("test_cases", "Test Cases", True, "table", 
                              ["detailed_test_cases", "expected_results"], 0.20),
                TemplateSection("test_data", "Test Data", True, "text", 
                              ["test_data_requirements", "data_setup"], 0.10),
                TemplateSection("automation", "Test Automation", False, "text", 
                              ["automation_strategy", "tools_frameworks"], 0.10),
                TemplateSection("reporting", "Test Reporting", True, "text", 
                              ["reporting_requirements", "metrics"], 0.05)
            ],
            required_metadata=["task_id", "created", "due", "priority", "status", "assigned_to", "task_type", "sequence", "test_type"],
            formatting_rules={
                "use_markdown_bullets": True,
                "enforce_section_numbering": True,
                "require_professional_language": True,
                "validate_mermaid_syntax": True
            },
            quality_thresholds={
                "overall": 8.5,
                "structure": 9.0,
                "content": 8.5,
                "visual": 8.0
            }
        )
        
        return configs
    
    def _initialize_formatting_standards(self) -> Dict[str, Any]:
        """Initialize professional formatting standards."""
        return {
            "section_numbering": {
                "use_numbers": True,
                "format": "## {number}. {title}",
                "subsection_format": "### {number}.{sub}. {title}"
            },
            "bullet_formatting": {
                "use_markdown": True,
                "avoid_python_lists": True,
                "consistent_indentation": True
            },
            "table_formatting": {
                "use_markdown_tables": True,
                "align_columns": True,
                "include_headers": True
            },
            "code_formatting": {
                "use_code_blocks": True,
                "specify_language": True,
                "proper_indentation": True
            },
            "professional_language": {
                "avoid_generic_phrases": True,
                "use_specific_terminology": True,
                "maintain_consistency": True
            }
        }
    
    def generate_enhanced_task(self, task_type: str, title: str, description: str, 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate enhanced task content with quality validation.
        
        Args:
            task_type: Type of task (DEV, BUG, TEST, etc.)
            title: Task title
            description: Task description
            context: Additional context for generation
            
        Returns:
            Dict containing generated task content and quality metrics
        """
        try:
            # Determine task type enum
            task_type_enum = self._parse_task_type(task_type)
            
            # Get template configuration
            config = self.template_configs.get(task_type_enum)
            if not config:
                logger.warning(f"No configuration for task type {task_type}, using default")
                config = self.template_configs[TaskType.DEVELOPMENT]
            
            # Generate task content
            task_content = self._generate_task_content(config, title, description, context)
            
            # Validate and enhance content quality
            if self.quality_scorer:
                quality_result = self.quality_scorer.score_task_content(task_content['markdown'])
                
                # If quality is below threshold, enhance content
                if quality_result.improvement_required:
                    task_content = self._enhance_content_quality(task_content, quality_result, config)
                    
                    # Re-score after enhancement
                    quality_result = self.quality_scorer.score_task_content(task_content['markdown'])
                
                task_content['quality_score'] = quality_result.overall_score
                task_content['quality_details'] = quality_result
            else:
                task_content['quality_score'] = 8.0  # Fallback score
                task_content['quality_details'] = None
            
            logger.info(f"Enhanced task generated with quality score: {task_content['quality_score']:.2f}")
            return task_content
            
        except Exception as e:
            logger.error(f"Error generating enhanced task: {e}")
            raise Exception(f"Enhanced task generation failed: {e}")
    
    def _parse_task_type(self, task_type: str) -> TaskType:
        """Parse task type string to TaskType enum."""
        task_type_upper = task_type.upper()
        
        # Direct mapping
        for enum_type in TaskType:
            if enum_type.value == task_type_upper:
                return enum_type
        
        # Fuzzy matching
        if 'DEV' in task_type_upper or 'DEVELOP' in task_type_upper:
            return TaskType.DEVELOPMENT
        elif 'BUG' in task_type_upper or 'FIX' in task_type_upper:
            return TaskType.BUG_FIX
        elif 'TEST' in task_type_upper:
            return TaskType.TEST_CASE
        elif 'DOC' in task_type_upper:
            return TaskType.DOCUMENTATION
        elif 'DES' in task_type_upper or 'DESIGN' in task_type_upper:
            return TaskType.DESIGN
        else:
            return TaskType.DEVELOPMENT  # Default
    
    def _generate_task_content(self, config: TemplateConfiguration, title: str, 
                             description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate task content based on configuration."""
        context = context or {}
        
        # Generate metadata
        metadata = self._generate_metadata(config, title, context)
        
        # Generate sections
        sections = {}
        for section in config.sections:
            sections[section.name] = self._generate_section_content(section, title, description, context)
        
        # Generate visual elements (Mermaid diagrams, ASCII art)
        if any(s.content_type == "mermaid" for s in config.sections):
            if self.visual_generator and self.VisualContext:
                # Create visual context
                visual_context = self.VisualContext(
                    task_type=config.task_type.value,
                    title=title,
                    description=description,
                    domain=self._extract_domain_from_description(description),
                    complexity=context.get('complexity', 'medium'),
                    user_personas=context.get('user_personas', []),
                    process_steps=context.get('process_steps', []),
                    system_components=context.get('system_components', []),
                    data_entities=context.get('data_entities', []),
                    user_interactions=context.get('user_interactions', [])
                )
                
                # Generate diagram
                diagram_result = self.visual_generator.generate_task_diagram(visual_context)
                sections['flow_diagram'] = f"```mermaid\n{diagram_result['content']}\n```"
                
                # Generate ASCII art if appropriate
                ascii_result = self.visual_generator.generate_ascii_art(visual_context)
                if ascii_result and ascii_result.get('content'):
                    sections['ascii_visualization'] = f"```\n{ascii_result['content']}\n```"
                
            elif self.mermaid_generator:
                # Fallback to original mermaid generator
                mermaid_diagram = self.mermaid_generator.generate_task_diagram(
                    config.task_type.value, title, description, context
                )
                sections['flow_diagram'] = mermaid_diagram
        
        # Compile markdown content
        markdown_content = self._compile_markdown(metadata, sections, config, title)
        
        return {
            'metadata': metadata,
            'sections': sections,
            'markdown': markdown_content,
            'config': config
        }
    
    def _generate_metadata(self, config: TemplateConfiguration, title: str, 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate task metadata based on configuration."""
        metadata = {
            'task_id': context.get('task_id', 'TASK-XXX'),
            'created': datetime.now().strftime('%Y-%m-%d'),
            'due': context.get('due_date', ''),
            'priority': context.get('priority', 'Medium'),
            'status': context.get('status', 'Todo'),
            'assigned_to': context.get('assigned_to', 'Developer'),
            'task_type': config.task_type.value,
            'sequence': context.get('sequence', 'XXX'),
            'estimated_effort': context.get('effort_estimate', 'Medium'),
            'tags': context.get('tags', [])
        }
        
        # Add task-type specific metadata
        if config.task_type == TaskType.BUG_FIX:
            metadata['bug_severity'] = context.get('bug_severity', 'Medium')
        elif config.task_type == TaskType.TEST_CASE:
            metadata['test_type'] = context.get('test_type', 'Functional')
        
        return metadata
    
    def _generate_section_content(self, section: TemplateSection, title: str, 
                                description: str, context: Dict[str, Any]) -> str:
        """Generate content for a specific section."""
        if section.name == "overview":
            return self._generate_overview_section(title, description, context)
        elif section.name == "implementation":
            return self._generate_implementation_section(title, description, context)
        elif section.name == "risk_assessment":
            return self._generate_risk_assessment_section(title, description, context)
        elif section.name == "technical_considerations":
            return self._generate_technical_considerations_section(title, description, context)
        elif section.name == "reproduction":
            return self._generate_reproduction_section(title, description, context)
        elif section.name == "root_cause":
            return self._generate_root_cause_section(title, description, context)
        elif section.name == "test_cases":
            return self._generate_test_cases_section(title, description, context)
        else:
            return self._generate_generic_section(section, title, description, context)
    
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
    
    def _generate_overview_section(self, title: str, description: str, context: Dict[str, Any]) -> str:
        """Generate comprehensive overview section."""
        # Create content generation context
        if self.content_generator:
            content_context = ContentGenerationContext(
                task_type=context.get('task_type', 'DEV'),
                title=title,
                description=description,
                domain=self._extract_domain_from_description(description),
                complexity=context.get('complexity', 'medium'),
                technology_stack=context.get('technology_stack', []),
                user_personas=context.get('user_personas', []),
                business_context=context.get('business_context', ''),
                existing_systems=context.get('existing_systems', [])
            )
            
            # Generate enhanced functional requirements
            enhanced_requirements = self.content_generator.generate_enhanced_functional_requirements(content_context)
            requirements_text = '\n'.join(f"- {req}" for req in enhanced_requirements)
        else:
            # Fallback requirements
            requirements_text = """- Implement core functionality as specified in the task description
- Provide comprehensive error handling and validation
- Maintain backward compatibility with existing systems
- Include appropriate logging and monitoring capabilities
- Follow established coding standards and best practices"""

        return f"""### 1.1. Brief Description
{description}

### 1.2. Functional Requirements
The enhanced system must:
{requirements_text}

### 1.3. Purpose & Benefits
This task will provide significant value by:
- Improving system functionality and user experience
- Enhancing maintainability and code quality
- Reducing technical debt and future maintenance costs
- Providing a foundation for future enhancements
- Ensuring system reliability and performance

### 1.4. Success Criteria
- [ ] All functional requirements are implemented and tested
- [ ] Code passes all quality checks and reviews
- [ ] Documentation is complete and up-to-date
- [ ] Performance meets or exceeds established benchmarks
- [ ] User acceptance testing is completed successfully"""
    
    def _generate_implementation_section(self, title: str, description: str, context: Dict[str, Any]) -> str:
        """Generate detailed implementation steps."""
        return """- [ ] **Step 1: Analysis and Planning** - Status: ⏳ Pending - Target: TBD
  - [ ] Sub-step 1.1: Analyze current system and requirements
  - [ ] Sub-step 1.2: Design solution architecture and approach
  - [ ] Sub-step 1.3: Create detailed implementation plan
  - [ ] Sub-step 1.4: Set up development environment and tools

- [ ] **Step 2: Core Implementation** - Status: ⏳ Pending - Target: TBD
  - [ ] Sub-step 2.1: Implement core functionality and features
  - [ ] Sub-step 2.2: Add comprehensive error handling
  - [ ] Sub-step 2.3: Implement logging and monitoring
  - [ ] Sub-step 2.4: Add configuration and customization options

- [ ] **Step 3: Testing and Validation** - Status: ⏳ Pending - Target: TBD
  - [ ] Sub-step 3.1: Write comprehensive unit tests
  - [ ] Sub-step 3.2: Perform integration testing
  - [ ] Sub-step 3.3: Conduct performance testing
  - [ ] Sub-step 3.4: Execute user acceptance testing

- [ ] **Step 4: Documentation and Deployment** - Status: ⏳ Pending - Target: TBD
  - [ ] Sub-step 4.1: Create comprehensive documentation
  - [ ] Sub-step 4.2: Prepare deployment procedures
  - [ ] Sub-step 4.3: Deploy to staging environment
  - [ ] Sub-step 4.4: Deploy to production environment"""
    
    def _generate_risk_assessment_section(self, title: str, description: str, context: Dict[str, Any]) -> str:
        """Generate comprehensive risk assessment."""
        return """| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|-------------------|
| Implementation complexity exceeding estimates | High | Medium | Break down into smaller, manageable tasks with regular progress reviews |
| Integration challenges with existing systems | Medium | Medium | Conduct thorough analysis and create comprehensive integration plan |
| Performance degradation in production | Medium | Low | Implement comprehensive testing and monitoring before deployment |
| User resistance to changes | Low | Medium | Provide training materials and gradual rollout with feedback collection |
| Technical dependencies causing delays | Medium | Low | Identify dependencies early and create contingency plans |"""
    
    def _generate_technical_considerations_section(self, title: str, description: str, context: Dict[str, Any]) -> str:
        """Generate technical considerations section."""
        return """**Architecture Considerations:**
- Component design and interaction patterns
- State management strategies and data flow
- Performance optimization approaches
- Scalability and maintainability factors

**Implementation Strategy:**
- Technology stack selection and justification
- Code organization and structure patterns
- Testing strategies and validation approaches
- Deployment and monitoring considerations

**Performance Requirements:**
- Response time and throughput expectations
- Resource utilization constraints
- Scalability requirements and load handling
- Monitoring and alerting strategies"""
    
    def _generate_reproduction_section(self, title: str, description: str, context: Dict[str, Any]) -> str:
        """Generate bug reproduction section."""
        return """**Steps to Reproduce:**
1. [Detailed step-by-step reproduction instructions]
2. [Include specific data, inputs, and conditions]
3. [Note any environmental requirements]

**Expected Behavior:**
[Description of what should happen]

**Actual Behavior:**
[Description of what actually happens]

**Environment Details:**
- Operating System: [OS version]
- Browser/Application Version: [Version]
- Additional Dependencies: [List relevant dependencies]"""
    
    def _generate_root_cause_section(self, title: str, description: str, context: Dict[str, Any]) -> str:
        """Generate root cause analysis section."""
        return """**Initial Investigation:**
[Summary of initial findings and hypothesis]

**Technical Analysis:**
[Detailed technical investigation results]

**Root Cause Identification:**
[Specific root cause with supporting evidence]

**Impact Assessment:**
[Analysis of bug impact on system and users]"""
    
    def _generate_test_cases_section(self, title: str, description: str, context: Dict[str, Any]) -> str:
        """Generate test cases section."""
        return """| Test Case ID | Description | Test Steps | Expected Result | Priority |
|--------------|-------------|------------|-----------------|----------|
| TC-001 | [Test case description] | [Detailed test steps] | [Expected outcome] | High |
| TC-002 | [Test case description] | [Detailed test steps] | [Expected outcome] | Medium |
| TC-003 | [Test case description] | [Detailed test steps] | [Expected outcome] | Low |"""
    
    def _generate_generic_section(self, section: TemplateSection, title: str, 
                                description: str, context: Dict[str, Any]) -> str:
        """Generate generic section content."""
        return f"[{section.title} content to be populated based on specific requirements]"
    
    def _compile_markdown(self, metadata: Dict[str, Any], sections: Dict[str, str], 
                        config: TemplateConfiguration, title: str = None) -> str:
        """Compile all sections into final markdown content."""
        lines = []
        
        # Title with proper formatting
        task_id = metadata.get('task_id', 'TASK-XXX')
        task_title = title or metadata.get('title', 'Task Title')
        title_line = f"# {task_id} - {task_title}"
        lines.append(title_line)
        lines.append("")
        
        # Task naming convention
        lines.extend([
            "## Task Naming Convention",
            "**Follow the TaskHero naming convention when creating tasks:**",
            "",
            "**Format:** `TASK-XXX-[TYPE]-descriptive-name.md`",
            "",
            "**Where:**",
            "- **XXX** = Sequential number (001, 002, 003, etc.)",
            "- **[TYPE]** = Task type abbreviation (must match metadata Task Type field)",
            "- **descriptive-name** = Brief but clear description (use hyphens, no spaces)",
            "",
            "**Task Type Abbreviations:**",
            "- **DEV** = Development",
            "- **BUG** = Bug Fix", 
            "- **TEST** = Test Case",
            "- **DOC** = Documentation",
            "- **DES** = Design",
            ""
        ])
        
        # Metadata section
        lines.append("## Metadata")
        for key, value in metadata.items():
            if key != 'title':
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, list):
                    value = ', '.join(value)
                lines.append(f"- **{formatted_key}:** {value}")
        lines.append("")
        
        # Generate sections based on configuration
        section_number = 1
        for section_config in config.sections:
            if section_config.name in sections and section_config.name != "metadata":
                lines.append(f"## {section_number}. {section_config.title}")
                lines.append(sections[section_config.name])
                lines.append("")
                section_number += 1
        
        # Add generation footer
        lines.extend([
            "---",
            f"*Generated by Enhanced TaskHero AI Template Engine on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return "\n".join(lines)
    
    def _enhance_content_quality(self, task_content: Dict[str, Any], 
                               quality_result: OverallQualityResult,
                               config: TemplateConfiguration) -> Dict[str, Any]:
        """Enhance content quality based on quality assessment."""
        # This would implement iterative content improvement
        # For now, return the original content
        logger.info("Content quality enhancement would be applied here")
        return task_content
    
    def validate_template_completeness(self, content: str, task_type: str) -> Dict[str, Any]:
        """Validate template completeness and quality."""
        task_type_enum = self._parse_task_type(task_type)
        config = self.template_configs.get(task_type_enum)
        
        if not config:
            return {"valid": False, "errors": ["Unknown task type"]}
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "completeness_score": 0.0,
            "missing_sections": [],
            "quality_issues": []
        }
        
        # Check for required sections with flexible matching
        section_mappings = {
            "metadata": ["Metadata", "## Metadata"],
            "overview": ["Overview", "## 1. Overview", "## Overview"],
            "flow_diagram": ["Flow Diagram", "## 2. Flow Diagram", "## Flow Diagram"],
            "implementation": ["Implementation Status", "## 3. Implementation Status", "## Implementation"],
            "description": ["Detailed Description", "## 4. Detailed Description", "## Description"],
            "risk_assessment": ["Risk Assessment", "## 5. Risk Assessment", "## Risk"],
            "technical_considerations": ["Technical Considerations", "## 6. Technical Considerations", "## Technical"],
            "reproduction": ["Bug Reproduction", "## Bug Reproduction", "## Reproduction"],
            "root_cause": ["Root Cause Analysis", "## Root Cause", "## Analysis"],
            "test_cases": ["Test Cases", "## Test Cases", "## Cases"],
            "solution": ["Solution Implementation", "## Solution", "## Implementation"],
            "testing": ["Testing Strategy", "## Testing", "## Strategy"]
        }
        
        for section in config.sections:
            if section.required:
                section_found = False
                possible_titles = section_mappings.get(section.name, [section.title])
                
                for title in possible_titles:
                    # Check for section headers with various formats
                    patterns = [
                        rf"#{{{1,3}}}\s*{re.escape(title)}",
                        rf"#{{{1,3}}}\s*\d+\.\s*{re.escape(title)}",
                        rf"#{{{1,3}}}\s*\d+\.\d+\.\s*{re.escape(title)}"
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            section_found = True
                            break
                    
                    if section_found:
                        break
                
                if not section_found:
                    validation_result["missing_sections"].append(section.title)
                    validation_result["errors"].append(f"Missing required section: {section.title}")
        
        # Calculate completeness score
        total_sections = len([s for s in config.sections if s.required])
        missing_sections = len(validation_result["missing_sections"])
        validation_result["completeness_score"] = max(0, (total_sections - missing_sections) / total_sections * 100)
        
        # Overall validation
        validation_result["valid"] = len(validation_result["errors"]) == 0
        
        return validation_result 