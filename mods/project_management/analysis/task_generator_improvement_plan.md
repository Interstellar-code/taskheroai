# TaskHero AI Task Generator Improvement Implementation Plan

## Overview

This document provides a detailed implementation plan to improve the TaskHero AI task generation system based on the quality analysis comparing TASK-008 (reference) with TASK-066 (AI-generated).

## Priority 1: Critical Fixes (Week 1)

### 1.1 Fix Mermaid Diagram Generation

**Issue**: Invalid journey diagrams being generated for installation tasks
**Files to Modify**: 
- `mods/project_management/mermaid_generator.py`
- `mods/project_management/enhanced_visual_generator.py`

**Implementation Steps**:

1. **Fix diagram type selection logic**:
```python
def _determine_diagram_type(self, task_type: str, description: str) -> DiagramType:
    description_lower = description.lower()
    
    # Priority keywords for specific diagram types
    if any(keyword in description_lower for keyword in ['install', 'setup', 'configure', 'deploy']):
        return DiagramType.FLOWCHART
    elif any(keyword in description_lower for keyword in ['enhance', 'improve', 'modify', 'update']):
        return DiagramType.FLOWCHART
    elif any(keyword in description_lower for keyword in ['user', 'journey', 'experience']):
        return DiagramType.USER_JOURNEY
    else:
        return DiagramType.FLOWCHART  # Default to flowchart
```

2. **Improve user action extraction**:
```python
def _extract_user_actions(self, description: str) -> List[str]:
    # Better parsing logic for meaningful user actions
    actions = []
    sentences = description.split('.')
    for sentence in sentences:
        if any(verb in sentence.lower() for verb in ['run', 'execute', 'configure', 'install', 'setup']):
            # Extract meaningful action from sentence
            action = self._clean_action_text(sentence.strip())
            if action and len(action) > 5:
                actions.append(action)
    
    # Fallback to generic actions if none found
    if not actions:
        actions = ["Start Process", "Configure Settings", "Complete Setup", "Verify Results"]
    
    return actions[:6]  # Limit to 6 actions
```

### 1.2 Fix Metadata Consistency

**Issue**: Task type inconsistency ("Development" vs "DEV")
**Files to Modify**: 
- `mods/project_management/ai_task_creator.py`

**Implementation**:
```python
def _prepare_base_context(self, task_id: str, title: str, description: str, 
                         task_type: str, **kwargs) -> Dict[str, Any]:
    # Standardize task type abbreviations
    task_type_mapping = {
        'Development': 'DEV',
        'Bug Fix': 'BUG', 
        'Test Case': 'TEST',
        'Documentation': 'DOC',
        'Design': 'DES',
        'Research': 'RES'
    }
    
    standardized_task_type = task_type_mapping.get(task_type, task_type.upper()[:3])
    
    context = {
        'task_id': task_id,
        'title': title,
        'description': description,
        'task_type': standardized_task_type,  # Use standardized abbreviation
        'task_type_full': task_type,  # Keep full name for templates that need it
        # ... rest of context
    }
    return context
```

### 1.3 Improve Functional Requirements Generation

**Issue**: Requirements generated as single array instead of structured list
**Files to Modify**: 
- `mods/project_management/ai_task_creator.py`

**Implementation**:
```python
async def _ai_generate_requirements_with_context(self, description: str, context: Dict, enhanced_context) -> List[str]:
    try:
        prompt = f"""Generate specific, testable functional requirements for this task:

Task: {context.get('title', '')}
Description: {description}
Task Type: {context.get('task_type', '')}

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

        response = await self.ai_provider.generate_response(prompt, max_tokens=800, temperature=0.6)
        
        # Parse and structure requirements
        requirements = self._parse_requirements_response(response)
        return requirements
        
    except Exception as e:
        logger.error(f"AI requirements generation failed: {e}")
        return self._generate_fallback_requirements(description, context)

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
```

## Priority 2: Content Quality Improvements (Week 2)

### 2.1 Enhanced Implementation Steps Generation

**Goal**: Generate specific, actionable implementation steps with clear deliverables

**Implementation**:
```python
async def _ai_generate_implementation_steps_with_context(self, description: str, context: Dict, enhanced_context) -> List[Dict[str, Any]]:
    try:
        task_type = context.get('task_type', 'DEV')
        
        # Get task-specific step templates
        step_templates = self._get_step_templates_for_task_type(task_type)
        
        prompt = f"""Generate detailed implementation steps for this {task_type} task:

Task: {context.get('title', '')}
Description: {description}

Create 4-5 implementation phases with specific sub-steps. Each phase should have:
- Clear phase name
- 3-4 specific sub-steps
- Estimated timeline
- Clear deliverables

Format as:
Phase 1: [Phase Name] - Target: [Date]
- Sub-step 1: [Specific action]
- Sub-step 2: [Specific action]
- Sub-step 3: [Specific action]

Generate implementation steps:"""

        response = await self.ai_provider.generate_response(prompt, max_tokens=1000, temperature=0.6)
        
        # Parse into structured format
        steps = self._parse_implementation_steps_response(response, context.get('due_date'))
        return steps
        
    except Exception as e:
        logger.error(f"Implementation steps generation failed: {e}")
        return self._get_fallback_implementation_steps(context.get('due_date'))
```

### 2.2 Context-Aware Content Enhancement

**Goal**: Use codebase context to generate more relevant content

**Implementation**:
```python
async def _enhance_with_codebase_context(self, description: str, context: Dict) -> Dict[str, Any]:
    """Enhance task content using codebase analysis."""
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
```

## Priority 3: Quality Validation System (Week 3)

### 3.1 Task Quality Scoring

**Implementation**:
```python
class TaskQualityValidator:
    """Validates and scores generated task quality."""
    
    def __init__(self):
        self.quality_metrics = {
            'metadata_completeness': 0.15,
            'requirements_specificity': 0.25,
            'implementation_detail': 0.20,
            'technical_depth': 0.15,
            'flow_diagram_validity': 0.10,
            'content_structure': 0.15
        }
    
    def validate_task_quality(self, task_content: str, context: Dict) -> Dict[str, Any]:
        """Validate and score task quality."""
        scores = {}
        
        # Check metadata completeness
        scores['metadata_completeness'] = self._score_metadata(task_content)
        
        # Check requirements specificity
        scores['requirements_specificity'] = self._score_requirements(task_content)
        
        # Check implementation detail
        scores['implementation_detail'] = self._score_implementation_steps(task_content)
        
        # Check technical depth
        scores['technical_depth'] = self._score_technical_content(task_content)
        
        # Check flow diagram validity
        scores['flow_diagram_validity'] = self._score_flow_diagram(task_content)
        
        # Check content structure
        scores['content_structure'] = self._score_structure(task_content)
        
        # Calculate overall score
        overall_score = sum(
            scores[metric] * weight 
            for metric, weight in self.quality_metrics.items()
        )
        
        return {
            'overall_score': overall_score,
            'metric_scores': scores,
            'recommendations': self._generate_improvement_recommendations(scores),
            'quality_level': self._determine_quality_level(overall_score)
        }
```

### 3.2 Template Compliance Checking

**Implementation**:
```python
def validate_template_compliance(self, task_content: str, template_name: str) -> Dict[str, Any]:
    """Check if generated content complies with template structure."""
    
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
    
    compliance_score = (len(found_sections) - len(missing_sections)) / len(required_sections)
    
    return {
        'compliance_score': compliance_score,
        'missing_sections': missing_sections,
        'issues': compliance_issues,
        'recommendations': self._generate_compliance_recommendations(compliance_issues)
    }
```

## Testing Strategy

### Unit Tests
- Test each fix individually
- Validate Mermaid diagram syntax
- Check metadata consistency
- Verify requirements formatting

### Integration Tests  
- Test complete task generation pipeline
- Validate template rendering with fixes
- Check AI enhancement integration

### Quality Tests
- Compare generated tasks against reference standards
- Measure improvement in quality scores
- Validate user acceptance criteria

## Success Metrics

### Immediate (Week 1)
- [ ] 100% valid Mermaid diagrams generated
- [ ] 100% consistent task type abbreviations
- [ ] Properly formatted requirements lists

### Short-term (Month 1)
- [ ] >90% task quality score
- [ ] >85% template compliance
- [ ] >80% user satisfaction with generated tasks

### Long-term (Month 3)
- [ ] Generated tasks indistinguishable from reference quality
- [ ] <10% manual editing required
- [ ] >95% user acceptance rate

## Implementation Timeline

**Week 1**: Critical fixes (Mermaid, metadata, requirements)
**Week 2**: Content quality improvements
**Week 3**: Quality validation system
**Week 4**: Testing and refinement
**Month 2**: Advanced context integration
**Month 3**: AI model fine-tuning and optimization
