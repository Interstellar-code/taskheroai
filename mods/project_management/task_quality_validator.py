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
        """Validate and score task quality."""
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

            # Calculate overall score
            overall_score = sum(
                scores[metric] * weight
                for metric, weight in self.quality_metrics.items()
            )

            return {
                'overall_score': overall_score,
                'metric_scores': scores,
                'recommendations': self._generate_improvement_recommendations(scores),
                'quality_level': self._determine_quality_level(overall_score),
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
