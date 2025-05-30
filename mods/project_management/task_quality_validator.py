"""
TaskHero AI Task Quality Validator

This module provides comprehensive task quality validation and scoring
to ensure generated tasks meet high standards.

Author: TaskHero AI Development Team
Created: 2025-01-XX
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger("TaskHero.TaskQualityValidator")


@dataclass
class QualityMetrics:
    """Quality metrics for task validation."""
    metadata_completeness: float
    requirements_specificity: float
    implementation_detail: float
    technical_depth: float
    flow_diagram_validity: float
    content_structure: float
    overall_score: float


class TaskQualityValidator:
    """Validates and scores generated task quality."""

    def __init__(self):
        """Initialize the task quality validator."""
        self.quality_metrics = {
            'metadata_completeness': 0.15,
            'requirements_specificity': 0.25,
            'implementation_detail': 0.20,
            'technical_depth': 0.15,
            'flow_diagram_validity': 0.10,
            'content_structure': 0.15
        }

        # Quality thresholds
        self.thresholds = {
            'excellent': 0.8,
            'good': 0.6,
            'acceptable': 0.4,
            'poor': 0.2
        }

        logger.info("TaskQualityValidator initialized")

    def validate_task_quality(self, task_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score task quality with TASK-126 Phase 4 enhancements."""
        try:
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

            # TASK-126 Phase 4: Enhanced quality validation metrics
            scores['context_relevance'] = self._score_context_relevance(task_content, context)
            scores['project_specificity'] = self._score_project_specificity(task_content, context)
            scores['placeholder_elimination'] = self._score_placeholder_elimination(task_content)
            scores['reference_quality'] = self._score_reference_quality(task_content, context)

            # TASK-126 Phase 4: Enhanced overall score calculation
            overall_score = self._calculate_enhanced_overall_score(scores, context)

            # TASK-126 Phase 4: Reference task comparison
            reference_comparison = self._compare_against_reference_tasks(task_content, context)

            return {
                'overall_score': overall_score,
                'metric_scores': scores,
                'recommendations': self._generate_enhanced_improvement_recommendations(scores, context),
                'quality_level': self._determine_quality_level(overall_score),
                'reference_comparison': reference_comparison,
                'task_126_enhancements': self._analyze_task_126_improvements(task_content, context),
                'metrics': QualityMetrics(
                    metadata_completeness=scores['metadata_completeness'],
                    requirements_specificity=scores['requirements_specificity'],
                    implementation_detail=scores['implementation_detail'],
                    technical_depth=scores['technical_depth'],
                    flow_diagram_validity=scores['flow_diagram_validity'],
                    content_structure=scores['content_structure'],
                    overall_score=overall_score
                )
            }

        except Exception as e:
            logger.error(f"Error validating task quality: {e}")
            return {
                'overall_score': 0.0,
                'metric_scores': {},
                'recommendations': ['Error occurred during quality validation'],
                'quality_level': 'error'
            }

    def _score_metadata(self, task_content: str) -> float:
        """Score metadata completeness."""
        score = 0.0
        required_fields = [
            'task_id', 'title', 'priority', 'status', 'assignee',
            'due_date', 'description', 'task_type'
        ]

        for field in required_fields:
            if field.lower() in task_content.lower():
                score += 1.0 / len(required_fields)

        # Bonus for additional metadata
        optional_fields = ['tags', 'dependencies', 'estimated_effort']
        for field in optional_fields:
            if field.lower() in task_content.lower():
                score += 0.1

        return min(score, 1.0)

    def _score_requirements(self, task_content: str) -> float:
        """Score requirements specificity and quality."""
        score = 0.0

        # Look for requirements section
        if 'functional requirements' in task_content.lower():
            score += 0.3

        # Count specific requirement patterns
        requirement_patterns = [
            r'the system must',
            r'the script must',
            r'the application must',
            r'must be able to',
            r'shall provide',
            r'should implement'
        ]

        requirement_count = 0
        for pattern in requirement_patterns:
            matches = re.findall(pattern, task_content, re.IGNORECASE)
            requirement_count += len(matches)

        # Score based on number of specific requirements
        if requirement_count >= 5:
            score += 0.4
        elif requirement_count >= 3:
            score += 0.3
        elif requirement_count >= 1:
            score += 0.2

        # Check for measurable/testable requirements
        measurable_patterns = [
            r'\d+%', r'\d+ seconds?', r'\d+ minutes?', r'\d+ hours?',
            r'within \d+', r'at least \d+', r'maximum \d+', r'minimum \d+'
        ]

        measurable_count = 0
        for pattern in measurable_patterns:
            matches = re.findall(pattern, task_content, re.IGNORECASE)
            measurable_count += len(matches)

        if measurable_count >= 2:
            score += 0.3
        elif measurable_count >= 1:
            score += 0.2

        return min(score, 1.0)

    def _score_implementation_steps(self, task_content: str) -> float:
        """Score implementation steps detail and quality."""
        score = 0.0

        # Look for implementation section
        if 'implementation' in task_content.lower():
            score += 0.2

        # Count phases/steps
        phase_patterns = [
            r'phase \d+',
            r'step \d+',
            r'stage \d+',
            r'## \w+',
            r'### \w+'
        ]

        phase_count = 0
        for pattern in phase_patterns:
            matches = re.findall(pattern, task_content, re.IGNORECASE)
            phase_count += len(matches)

        if phase_count >= 4:
            score += 0.4
        elif phase_count >= 3:
            score += 0.3
        elif phase_count >= 2:
            score += 0.2

        # Check for substeps
        substep_patterns = [r'- \w+', r'\* \w+', r'\d+\. \w+']
        substep_count = 0
        for pattern in substep_patterns:
            matches = re.findall(pattern, task_content)
            substep_count += len(matches)

        if substep_count >= 10:
            score += 0.3
        elif substep_count >= 5:
            score += 0.2
        elif substep_count >= 3:
            score += 0.1

        # Check for deliverables
        if 'deliverable' in task_content.lower():
            score += 0.1

        return min(score, 1.0)

    def _score_technical_content(self, task_content: str) -> float:
        """Score technical depth and considerations."""
        score = 0.0

        # Technical sections
        technical_sections = [
            'technical considerations',
            'architecture',
            'performance',
            'security',
            'testing',
            'integration'
        ]

        for section in technical_sections:
            if section in task_content.lower():
                score += 0.15

        # Technical terms and concepts
        technical_terms = [
            'api', 'database', 'framework', 'library', 'algorithm',
            'performance', 'scalability', 'security', 'authentication',
            'authorization', 'validation', 'error handling', 'logging'
        ]

        term_count = 0
        for term in technical_terms:
            if term in task_content.lower():
                term_count += 1

        if term_count >= 5:
            score += 0.3
        elif term_count >= 3:
            score += 0.2
        elif term_count >= 1:
            score += 0.1

        return min(score, 1.0)

    def _score_flow_diagram(self, task_content: str) -> float:
        """Score flow diagram validity and presence."""
        score = 0.0

        # Check for mermaid diagram
        if '```mermaid' in task_content:
            score += 0.5

            # Check for valid diagram types
            valid_types = ['flowchart', 'graph', 'sequenceDiagram', 'journey', 'gantt']
            for diagram_type in valid_types:
                if diagram_type in task_content:
                    score += 0.3
                    break

            # Check for proper syntax elements
            syntax_elements = ['->', '-->', '|', '[', ']', '(', ')']
            for element in syntax_elements:
                if element in task_content:
                    score += 0.05

        # Alternative: ASCII diagrams
        elif any(char in task_content for char in ['┌', '└', '├', '│', '─']):
            score += 0.3

        return min(score, 1.0)

    def _score_structure(self, task_content: str) -> float:
        """Score content structure and organization."""
        score = 0.0

        # Check for proper markdown structure
        if re.search(r'^# ', task_content, re.MULTILINE):
            score += 0.3

        if re.search(r'^## ', task_content, re.MULTILINE):
            score += 0.3

        # Count sections
        section_count = len(re.findall(r'^##? ', task_content, re.MULTILINE))
        if section_count >= 5:
            score += 0.2
        elif section_count >= 3:
            score += 0.15
        elif section_count >= 1:
            score += 0.1

        # Check for lists and organization
        if re.search(r'^- ', task_content, re.MULTILINE):
            score += 0.1

        if re.search(r'^\d+\. ', task_content, re.MULTILINE):
            score += 0.1

        # Check for proper formatting
        if '**' in task_content or '*' in task_content:
            score += 0.05

        return min(score, 1.0)

    def _determine_quality_level(self, overall_score: float) -> str:
        """Determine quality level based on overall score."""
        if overall_score >= self.thresholds['excellent']:
            return 'excellent'
        elif overall_score >= self.thresholds['good']:
            return 'good'
        elif overall_score >= self.thresholds['acceptable']:
            return 'acceptable'
        elif overall_score >= self.thresholds['poor']:
            return 'poor'
        else:
            return 'very_poor'

    def _generate_improvement_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations based on scores."""
        recommendations = []

        if scores.get('metadata_completeness', 0) < 0.7:
            recommendations.append("Add missing metadata fields (tags, dependencies, effort estimates)")

        if scores.get('requirements_specificity', 0) < 0.7:
            recommendations.append("Make requirements more specific and measurable")

        if scores.get('implementation_detail', 0) < 0.7:
            recommendations.append("Add more detailed implementation steps with clear deliverables")

        if scores.get('technical_depth', 0) < 0.7:
            recommendations.append("Include more technical considerations and architectural details")

        if scores.get('flow_diagram_validity', 0) < 0.5:
            recommendations.append("Add or improve flow diagrams for better visualization")

        if scores.get('content_structure', 0) < 0.7:
            recommendations.append("Improve content structure with better organization and formatting")

        return recommendations

    # ============================================================================
    # TASK-126 Phase 4: Enhanced Quality Validation Methods
    # ============================================================================

    def _score_context_relevance(self, task_content: str, context: Dict[str, Any]) -> float:
        """Score how well the task content matches the provided context (TASK-126 Phase 4)."""
        score = 0.0
        content_lower = task_content.lower()

        # Check for user title and description preservation
        title = context.get('title', '').lower()
        description = context.get('description', '').lower()

        if title:
            # Title keywords should appear in content
            title_words = [word for word in title.split() if len(word) > 3]
            title_matches = sum(1 for word in title_words if word in content_lower)
            if title_words:
                score += (title_matches / len(title_words)) * 0.4

        if description:
            # Description keywords should appear in content
            desc_words = [word for word in description.split() if len(word) > 3][:10]  # Top 10 words
            desc_matches = sum(1 for word in desc_words if word in content_lower)
            if desc_words:
                score += (desc_matches / len(desc_words)) * 0.4

        # Check for task type alignment
        task_type = context.get('task_type', '').lower()
        if task_type and task_type in content_lower:
            score += 0.2

        return min(score, 1.0)

    def _score_project_specificity(self, task_content: str, context: Dict[str, Any]) -> float:
        """Score project-specific content and terminology (TASK-126 Phase 4)."""
        score = 0.0
        content_lower = task_content.lower()

        # TaskHero AI specific terminology
        project_terms = [
            'taskhero', 'taskhero ai', 'task hero', 'kanban', 'ai enhancement',
            'context processor', 'semantic search', 'provider factory', 'template',
            'quality validator', 'embeddings', 'mods/', 'project_management'
        ]

        term_matches = sum(1 for term in project_terms if term in content_lower)
        score += min(0.5, term_matches * 0.05)  # Up to 0.5 for project terms

        # Technical architecture mentions
        architecture_terms = [
            'ai_enhancement', 'context_processor', 'template_manager', 'task_quality_validator',
            'provider_factory', 'semantic_search', 'ai_task_creator'
        ]

        arch_matches = sum(1 for term in architecture_terms if term in content_lower)
        score += min(0.3, arch_matches * 0.05)  # Up to 0.3 for architecture

        # File path references
        if any(path in content_lower for path in ['mods/project_management', 'mods/ai', 'theherotasks']):
            score += 0.2

        return min(score, 1.0)

    def _score_placeholder_elimination(self, task_content: str) -> float:
        """Score how well placeholders have been eliminated (TASK-126 Phase 4)."""
        score = 1.0  # Start with perfect score
        content_lower = task_content.lower()

        # Common placeholder patterns
        placeholder_patterns = [
            'will be defined', 'will be determined', 'will be analyzed', 'will be developed',
            'according to specifications', 'based on requirements', 'where applicable',
            'if needed', 'as required', 'tbd', 'to be determined', 'placeholder',
            'example content', 'sample text', 'lorem ipsum', '[insert', '[add',
            'will be implemented', 'will be created', 'will be added'
        ]

        # Penalty for each placeholder found
        for pattern in placeholder_patterns:
            if pattern in content_lower:
                score -= 0.1  # 10% penalty per placeholder type

        # Additional penalty for generic content
        generic_patterns = [
            'the system will', 'the application will', 'this will be',
            'functionality will be', 'features will be', 'implementation will'
        ]

        for pattern in generic_patterns:
            if pattern in content_lower:
                score -= 0.05  # 5% penalty per generic pattern

        return max(0.0, score)

    def _score_reference_quality(self, task_content: str, context: Dict[str, Any]) -> float:
        """Score quality of references to existing tasks and examples (TASK-126 Phase 4)."""
        score = 0.0
        content_lower = task_content.lower()

        # High-quality reference tasks
        quality_references = ['task-003', 'task-012', 'task-125']
        for ref in quality_references:
            if ref in content_lower:
                score += 0.25  # 25% for each quality reference

        # Reference to successful patterns
        pattern_references = [
            'similar to', 'following the pattern', 'based on', 'leveraging',
            'using the approach', 'applying the strategy', 'following the success'
        ]

        for pattern in pattern_references:
            if pattern in content_lower:
                score += 0.1  # 10% for pattern references
                break  # Only count once

        # Specific methodology references
        methodology_refs = [
            'multi-pass', 'context discovery', 'prompt engineering', 'quality validation',
            'specialized templates', 'enhanced scoring'
        ]

        method_matches = sum(1 for method in methodology_refs if method in content_lower)
        score += min(0.3, method_matches * 0.05)  # Up to 30% for methodology

        return min(score, 1.0)

    def _calculate_enhanced_overall_score(self, scores: Dict[str, float], context: Dict[str, Any]) -> float:
        """Calculate enhanced overall score with TASK-126 improvements (Phase 4)."""
        # Original metrics with adjusted weights
        original_weight = 0.7
        enhanced_weight = 0.3

        # Original score calculation
        original_metrics = {
            'metadata_completeness': 0.15,
            'requirements_specificity': 0.25,
            'implementation_detail': 0.20,
            'technical_depth': 0.15,
            'flow_diagram_validity': 0.10,
            'content_structure': 0.15
        }

        original_score = sum(
            scores.get(metric, 0) * weight
            for metric, weight in original_metrics.items()
        )

        # Enhanced metrics calculation
        enhanced_metrics = {
            'context_relevance': 0.35,
            'project_specificity': 0.25,
            'placeholder_elimination': 0.25,
            'reference_quality': 0.15
        }

        enhanced_score = sum(
            scores.get(metric, 0) * weight
            for metric, weight in enhanced_metrics.items()
        )

        # Combine original and enhanced scores
        final_score = (original_score * original_weight) + (enhanced_score * enhanced_weight)

        return min(1.0, final_score)

    def _compare_against_reference_tasks(self, task_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compare task against high-quality reference tasks (TASK-126 Phase 4)."""
        comparison = {
            'similarity_to_task_003': 0.0,
            'similarity_to_task_012': 0.0,
            'similarity_to_task_125': 0.0,
            'overall_reference_similarity': 0.0,
            'quality_indicators_found': []
        }

        content_lower = task_content.lower()

        # Quality indicators from reference tasks
        task_003_indicators = [
            'kanban', 'visualization', 'terminal', 'columns', 'todo', 'inprogress', 'done',
            'color coding', 'status indicators', 'interactive navigation'
        ]

        task_012_indicators = [
            'ai engine', 'enhancement', 'provider', 'optimization', 'quality',
            'context', 'semantic', 'integration', 'fallback'
        ]

        task_125_indicators = [
            'multi-pass', 'context discovery', 'prompt engineering', 'quality validation',
            'specialized templates', 'performance improvement', 'optimization'
        ]

        # Calculate similarities
        comparison['similarity_to_task_003'] = self._calculate_indicator_similarity(content_lower, task_003_indicators)
        comparison['similarity_to_task_012'] = self._calculate_indicator_similarity(content_lower, task_012_indicators)
        comparison['similarity_to_task_125'] = self._calculate_indicator_similarity(content_lower, task_125_indicators)

        # Overall similarity
        comparison['overall_reference_similarity'] = (
            comparison['similarity_to_task_003'] +
            comparison['similarity_to_task_012'] +
            comparison['similarity_to_task_125']
        ) / 3

        # Found quality indicators
        all_indicators = task_003_indicators + task_012_indicators + task_125_indicators
        comparison['quality_indicators_found'] = [
            indicator for indicator in all_indicators if indicator in content_lower
        ]

        return comparison

    def _calculate_indicator_similarity(self, content: str, indicators: List[str]) -> float:
        """Calculate similarity based on indicator presence."""
        if not indicators:
            return 0.0

        matches = sum(1 for indicator in indicators if indicator in content)
        return matches / len(indicators)

    def _analyze_task_126_improvements(self, task_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze specific TASK-126 improvements in the generated content."""
        improvements = {
            'enhanced_context_discovery': False,
            'specialized_prompts': False,
            'quality_standards': False,
            'reference_examples': False,
            'project_specific_content': False,
            'task_type_specialization': False,
            'placeholder_elimination': False,
            'improvement_score': 0.0
        }

        content_lower = task_content.lower()

        # Enhanced context discovery indicators
        if any(term in content_lower for term in ['multi-pass', 'context discovery', 'semantic search', 'relevance']):
            improvements['enhanced_context_discovery'] = True

        # Specialized prompt indicators
        if any(term in content_lower for term in ['specialized', 'prompt engineering', 'template', 'classification']):
            improvements['specialized_prompts'] = True

        # Quality standards indicators
        if any(term in content_lower for term in ['quality standards', 'acceptance criteria', 'metrics', 'validation']):
            improvements['quality_standards'] = True

        # Reference examples indicators
        if any(term in content_lower for term in ['task-003', 'task-012', 'task-125', 'reference example']):
            improvements['reference_examples'] = True

        # Project-specific content indicators
        if any(term in content_lower for term in ['taskhero', 'mods/', 'project_management', 'ai_enhancement']):
            improvements['project_specific_content'] = True

        # Task type specialization indicators
        task_type = context.get('task_type', '').lower()
        if 'development' in task_type:
            specialization_terms = ['ai', 'enhancement', 'optimization', 'ui', 'visualization', 'integration']
            if any(term in content_lower for term in specialization_terms):
                improvements['task_type_specialization'] = True

        # Placeholder elimination check
        placeholder_patterns = ['will be defined', 'will be determined', 'tbd', 'placeholder']
        if not any(pattern in content_lower for pattern in placeholder_patterns):
            improvements['placeholder_elimination'] = True

        # Calculate improvement score
        improvement_count = sum(1 for v in improvements.values() if isinstance(v, bool) and v)
        improvements['improvement_score'] = improvement_count / 7  # 7 improvement categories

        return improvements

    def _generate_enhanced_improvement_recommendations(self, scores: Dict[str, float], context: Dict[str, Any]) -> List[str]:
        """Generate enhanced improvement recommendations including TASK-126 specific suggestions."""
        recommendations = []

        # Original recommendations
        if scores.get('metadata_completeness', 0) < 0.7:
            recommendations.append("Add missing metadata fields (tags, dependencies, effort estimates)")

        if scores.get('requirements_specificity', 0) < 0.7:
            recommendations.append("Make requirements more specific and measurable")

        if scores.get('implementation_detail', 0) < 0.7:
            recommendations.append("Add more detailed implementation steps with clear deliverables")

        if scores.get('technical_depth', 0) < 0.7:
            recommendations.append("Include more technical considerations and architectural details")

        if scores.get('flow_diagram_validity', 0) < 0.5:
            recommendations.append("Add or improve flow diagrams for better visualization")

        if scores.get('content_structure', 0) < 0.7:
            recommendations.append("Improve content structure with better organization and formatting")

        # TASK-126 specific recommendations
        if scores.get('context_relevance', 0) < 0.7:
            recommendations.append("TASK-126: Improve alignment with user title and description - ensure key terms are preserved")

        if scores.get('project_specificity', 0) < 0.7:
            recommendations.append("TASK-126: Add more TaskHero AI specific terminology and architecture references")

        if scores.get('placeholder_elimination', 0) < 0.8:
            recommendations.append("TASK-126: Remove placeholder content and generic patterns - provide specific implementation details")

        if scores.get('reference_quality', 0) < 0.5:
            recommendations.append("TASK-126: Include references to high-quality tasks (TASK-003, TASK-012, TASK-125) and proven methodologies")

        # Enhanced scoring recommendations
        enhanced_score = scores.get('context_relevance', 0) + scores.get('project_specificity', 0) + scores.get('placeholder_elimination', 0) + scores.get('reference_quality', 0)
        if enhanced_score < 2.0:  # Out of 4.0
            recommendations.append("TASK-126: Overall enhancement quality is below target - focus on context relevance and project specificity")

        return recommendations
