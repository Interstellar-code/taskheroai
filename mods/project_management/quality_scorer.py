"""
TaskHero AI Quality Scorer

This module provides comprehensive quality scoring for task generation content
based on the defined quality metrics and thresholds.

Author: TaskHero AI Development Team
Created: 2025-05-25
"""

import re
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("TaskHero.QualityScorer")

@dataclass
class QualityScore:
    """Quality score result for a specific dimension."""
    dimension: str
    score: float
    max_score: float
    issues: List[str]
    suggestions: List[str]
    passed_threshold: bool

@dataclass
class OverallQualityResult:
    """Overall quality assessment result."""
    overall_score: float
    dimension_scores: Dict[str, QualityScore]
    passed_minimum_threshold: bool
    improvement_required: bool
    priority_improvements: List[str]

class QualityScorer:
    """
    Comprehensive quality scoring system for TaskHero AI task generation.
    
    Evaluates task content across multiple quality dimensions and provides
    actionable feedback for improvement.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the quality scorer.
        
        Args:
            config_path: Path to quality configuration file
        """
        self.config = self._load_config(config_path)
        self.weights = self.config['dimension_weights']
        self.thresholds = self.config['minimum_thresholds']
        
        logger.info("QualityScorer initialized with configuration")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load quality scoring configuration."""
        default_config = {
            'dimension_weights': {
                'structure_compliance': 0.20,
                'content_quality': 0.25,
                'requirements_excellence': 0.20,
                'visual_elements': 0.15,
                'technical_depth': 0.10,
                'risk_assessment': 0.10
            },
            'minimum_thresholds': {
                'overall': 8.5,
                'structure_compliance': 9.0,
                'content_quality': 8.5,
                'requirements_excellence': 8.5,
                'visual_elements': 8.0,
                'technical_depth': 8.0,
                'risk_assessment': 8.0
            },
            'section_requirements': {
                'metadata': ['task_id', 'created', 'due', 'priority', 'status', 'assigned_to', 'task_type', 'sequence'],
                'overview': ['brief_description', 'functional_requirements', 'purpose_benefits', 'success_criteria'],
                'flow_diagram': ['mermaid_diagram'],
                'implementation_steps': ['detailed_steps', 'sub_steps', 'target_dates'],
                'risk_assessment': ['risk_table', 'mitigation_strategies']
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    default_config.update(custom_config)
            except Exception as e:
                logger.warning(f"Failed to load custom config: {e}, using defaults")
        
        return default_config
    
    def score_task_content(self, content: str, metadata: Dict[str, Any] = None) -> OverallQualityResult:
        """
        Score task content across all quality dimensions.
        
        Args:
            content: Task content as markdown string
            metadata: Additional metadata for scoring context
            
        Returns:
            OverallQualityResult with comprehensive scoring
        """
        try:
            # Parse content into sections
            sections = self._parse_content_sections(content)
            
            # Score each dimension
            dimension_scores = {}
            
            # 1. Structure Compliance (20%)
            dimension_scores['structure_compliance'] = self._score_structure_compliance(sections, content)
            
            # 2. Content Quality (25%)
            dimension_scores['content_quality'] = self._score_content_quality(sections, content)
            
            # 3. Requirements Excellence (20%)
            dimension_scores['requirements_excellence'] = self._score_requirements_excellence(sections)
            
            # 4. Visual Elements (15%)
            dimension_scores['visual_elements'] = self._score_visual_elements(sections, content)
            
            # 5. Technical Depth (10%)
            dimension_scores['technical_depth'] = self._score_technical_depth(sections)
            
            # 6. Risk Assessment (10%)
            dimension_scores['risk_assessment'] = self._score_risk_assessment(sections)
            
            # Calculate overall score
            overall_score = sum(
                score.score * self.weights[dimension]
                for dimension, score in dimension_scores.items()
            )
            
            # Determine if improvements are required
            passed_threshold = overall_score >= self.thresholds['overall']
            improvement_required = overall_score < self.thresholds['overall']
            
            # Generate priority improvements
            priority_improvements = self._generate_priority_improvements(dimension_scores)
            
            result = OverallQualityResult(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                passed_minimum_threshold=passed_threshold,
                improvement_required=improvement_required,
                priority_improvements=priority_improvements
            )
            
            logger.info(f"Quality scoring complete: {overall_score:.2f}/10")
            return result
            
        except Exception as e:
            logger.error(f"Error scoring task content: {e}")
            # Return minimal failing score
            return OverallQualityResult(
                overall_score=0.0,
                dimension_scores={},
                passed_minimum_threshold=False,
                improvement_required=True,
                priority_improvements=["Content parsing failed - manual review required"]
            )
    
    def _parse_content_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown content into sections."""
        sections = {}
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check for section headers
            if line.startswith('#'):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.strip('#').strip().lower()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _score_structure_compliance(self, sections: Dict[str, str], content: str) -> QualityScore:
        """Score template structure compliance."""
        score = 0.0
        max_score = 10.0
        issues = []
        suggestions = []
        
        # Check for required sections
        required_sections = ['metadata', 'overview', 'flow diagram', 'implementation status', 'detailed description']
        present_sections = list(sections.keys())
        
        for section in required_sections:
            if any(section in present_section for present_section in present_sections):
                score += 1.5
            else:
                issues.append(f"Missing required section: {section}")
                suggestions.append(f"Add {section} section with relevant content")
        
        # Check section numbering consistency
        numbered_sections = [line for line in content.split('\n') if re.match(r'^##?\s+\d+\.', line)]
        if len(numbered_sections) >= 3:
            score += 1.0
        else:
            issues.append("Inconsistent or missing section numbering")
            suggestions.append("Use consistent section numbering (1., 2., 3., etc.)")
        
        # Check subsection organization
        subsections = [line for line in content.split('\n') if re.match(r'^###?\s+\d+\.\d+', line)]
        if len(subsections) >= 2:
            score += 1.0
        else:
            issues.append("Poor subsection organization")
            suggestions.append("Use proper subsection numbering (1.1, 1.2, etc.)")
        
        # Check content length per section
        for section_name, section_content in sections.items():
            if len(section_content.strip()) < 50:
                issues.append(f"Section '{section_name}' has insufficient content")
                suggestions.append(f"Expand {section_name} section with more detailed content")
            else:
                score += 0.5
        
        passed_threshold = score >= self.thresholds['structure_compliance']
        
        return QualityScore(
            dimension='structure_compliance',
            score=min(score, max_score),
            max_score=max_score,
            issues=issues,
            suggestions=suggestions,
            passed_threshold=passed_threshold
        )
    
    def _score_content_quality(self, sections: Dict[str, str], content: str) -> QualityScore:
        """Score content quality and specificity."""
        score = 0.0
        max_score = 10.0
        issues = []
        suggestions = []
        
        # Check for generic/template language
        generic_phrases = [
            'this task enhances the system',
            'implement functionality',
            'according to specifications',
            'will be defined during',
            'consider requirements'
        ]
        
        generic_count = sum(1 for phrase in generic_phrases if phrase.lower() in content.lower())
        if generic_count == 0:
            score += 2.0
        elif generic_count <= 2:
            score += 1.0
            issues.append("Some generic language detected")
            suggestions.append("Replace generic phrases with task-specific content")
        else:
            issues.append("Excessive generic/template language")
            suggestions.append("Rewrite content to be more specific and actionable")
        
        # Check for specific, actionable content
        action_words = ['implement', 'create', 'build', 'develop', 'design', 'test', 'validate', 'configure']
        action_count = sum(1 for word in action_words if word.lower() in content.lower())
        if action_count >= 5:
            score += 2.0
        elif action_count >= 3:
            score += 1.0
        else:
            issues.append("Insufficient actionable language")
            suggestions.append("Use more specific action words and implementation details")
        
        # Check for technical specificity
        technical_indicators = ['api', 'database', 'component', 'function', 'class', 'method', 'endpoint', 'interface']
        tech_count = sum(1 for term in technical_indicators if term.lower() in content.lower())
        if tech_count >= 3:
            score += 2.0
        elif tech_count >= 1:
            score += 1.0
        else:
            issues.append("Limited technical specificity")
            suggestions.append("Include more technical details and implementation specifics")
        
        # Check content length and depth
        total_length = len(content)
        if total_length >= 2000:
            score += 2.0
        elif total_length >= 1000:
            score += 1.0
        else:
            issues.append("Content length insufficient for comprehensive task")
            suggestions.append("Expand content with more detailed descriptions and guidance")
        
        # Check for professional tone
        if not re.search(r'\b(TODO|FIXME|placeholder)\b', content, re.IGNORECASE):
            score += 1.0
        else:
            issues.append("Placeholder text or TODO items found")
            suggestions.append("Replace all placeholder text with actual content")
        
        # Check for context-aware content
        if 'taskhero' in content.lower() or 'task hero' in content.lower():
            score += 1.0
        else:
            issues.append("Content lacks project-specific context")
            suggestions.append("Include TaskHero-specific context and integration details")
        
        passed_threshold = score >= self.thresholds['content_quality']
        
        return QualityScore(
            dimension='content_quality',
            score=min(score, max_score),
            max_score=max_score,
            issues=issues,
            suggestions=suggestions,
            passed_threshold=passed_threshold
        )
    
    def _score_requirements_excellence(self, sections: Dict[str, str]) -> QualityScore:
        """Score functional requirements quality."""
        score = 0.0
        max_score = 10.0
        issues = []
        suggestions = []
        
        # Find requirements section
        requirements_content = ""
        for section_name, content in sections.items():
            if 'requirement' in section_name or 'functional' in section_name:
                requirements_content = content
                break
        
        if not requirements_content:
            # Check in overview section
            overview_content = sections.get('overview', '')
            if 'functional requirements' in overview_content.lower():
                # Extract requirements from overview
                lines = overview_content.split('\n')
                in_requirements = False
                req_lines = []
                for line in lines:
                    if 'functional requirements' in line.lower():
                        in_requirements = True
                        continue
                    elif in_requirements and line.startswith('#'):
                        break
                    elif in_requirements:
                        req_lines.append(line)
                requirements_content = '\n'.join(req_lines)
        
        if not requirements_content:
            issues.append("No functional requirements section found")
            suggestions.append("Add comprehensive functional requirements section")
            return QualityScore(
                dimension='requirements_excellence',
                score=0.0,
                max_score=max_score,
                issues=issues,
                suggestions=suggestions,
                passed_threshold=False
            )
        
        # Check for Python list format (major issue)
        if re.search(r'\[\'.*?\'\]', requirements_content):
            issues.append("Requirements in Python list format instead of markdown")
            suggestions.append("Convert requirements to markdown bullet points")
        else:
            score += 3.0
        
        # Check for markdown bullet format
        bullet_requirements = re.findall(r'^[-*]\s+.+', requirements_content, re.MULTILINE)
        if len(bullet_requirements) >= 3:
            score += 2.0
        elif len(bullet_requirements) >= 1:
            score += 1.0
        else:
            issues.append("Requirements not in proper markdown bullet format")
            suggestions.append("Format requirements as markdown bullet points")
        
        # Check requirement specificity
        specific_indicators = ['must', 'shall', 'should', 'will', 'can', 'cannot']
        specific_count = sum(1 for req in bullet_requirements 
                           for indicator in specific_indicators 
                           if indicator in req.lower())
        
        if specific_count >= len(bullet_requirements) * 0.8:
            score += 2.0
        elif specific_count >= len(bullet_requirements) * 0.5:
            score += 1.0
        else:
            issues.append("Requirements lack specificity and clear obligations")
            suggestions.append("Use specific language (must, shall, will) in requirements")
        
        # Check for testable requirements
        testable_indicators = ['verify', 'validate', 'test', 'measure', 'confirm', 'ensure']
        testable_count = sum(1 for req in bullet_requirements 
                           for indicator in testable_indicators 
                           if indicator in req.lower())
        
        if testable_count >= 2:
            score += 2.0
        elif testable_count >= 1:
            score += 1.0
        else:
            issues.append("Requirements are not easily testable")
            suggestions.append("Make requirements more testable with verification criteria")
        
        # Check requirement length (not too verbose)
        avg_length = sum(len(req) for req in bullet_requirements) / max(len(bullet_requirements), 1)
        if 50 <= avg_length <= 150:
            score += 1.0
        else:
            if avg_length > 150:
                issues.append("Requirements are too verbose")
                suggestions.append("Make requirements more concise and focused")
            else:
                issues.append("Requirements are too brief")
                suggestions.append("Provide more detailed requirements")
        
        passed_threshold = score >= self.thresholds['requirements_excellence']
        
        return QualityScore(
            dimension='requirements_excellence',
            score=min(score, max_score),
            max_score=max_score,
            issues=issues,
            suggestions=suggestions,
            passed_threshold=passed_threshold
        )
    
    def _score_visual_elements(self, sections: Dict[str, str], content: str) -> QualityScore:
        """Score visual elements and diagrams."""
        score = 0.0
        max_score = 10.0
        issues = []
        suggestions = []
        
        # Check for Mermaid diagrams
        mermaid_count = len(re.findall(r'```mermaid', content, re.IGNORECASE))
        if mermaid_count >= 1:
            score += 4.0
        else:
            issues.append("No Mermaid diagrams found")
            suggestions.append("Add Mermaid flow diagram for user journey or process flow")
        
        # Check for flowchart specifically
        if 'flowchart' in content.lower():
            score += 2.0
        else:
            issues.append("No flowchart diagram found")
            suggestions.append("Include flowchart diagram for process visualization")
        
        # Check for ASCII art
        ascii_patterns = [r'┌─', r'│', r'└─', r'├─', r'┤', r'┬', r'┴']
        ascii_count = sum(1 for pattern in ascii_patterns if re.search(pattern, content))
        if ascii_count >= 3:
            score += 2.0
        elif ascii_count >= 1:
            score += 1.0
        else:
            issues.append("No ASCII art or visual layouts found")
            suggestions.append("Add ASCII art for UI layouts or visual representations")
        
        # Check for visual descriptions
        visual_keywords = ['diagram', 'chart', 'graph', 'layout', 'wireframe', 'mockup']
        visual_count = sum(1 for keyword in visual_keywords if keyword.lower() in content.lower())
        if visual_count >= 2:
            score += 1.0
        else:
            issues.append("Limited visual element descriptions")
            suggestions.append("Include more visual descriptions and design elements")
        
        # Check for user journey elements
        journey_keywords = ['user', 'journey', 'flow', 'step', 'process', 'workflow']
        journey_count = sum(1 for keyword in journey_keywords if keyword.lower() in content.lower())
        if journey_count >= 3:
            score += 1.0
        else:
            issues.append("Limited user journey visualization")
            suggestions.append("Include user journey or workflow visualization")
        
        passed_threshold = score >= self.thresholds['visual_elements']
        
        return QualityScore(
            dimension='visual_elements',
            score=min(score, max_score),
            max_score=max_score,
            issues=issues,
            suggestions=suggestions,
            passed_threshold=passed_threshold
        )
    
    def _score_technical_depth(self, sections: Dict[str, str]) -> QualityScore:
        """Score technical depth and implementation guidance."""
        score = 0.0
        max_score = 10.0
        issues = []
        suggestions = []
        
        # Combine relevant sections for analysis
        technical_content = ""
        for section_name, content in sections.items():
            if any(keyword in section_name for keyword in ['implementation', 'technical', 'detailed', 'description']):
                technical_content += content + "\n"
        
        if not technical_content:
            issues.append("No technical implementation content found")
            suggestions.append("Add detailed technical implementation guidance")
            return QualityScore(
                dimension='technical_depth',
                score=0.0,
                max_score=max_score,
                issues=issues,
                suggestions=suggestions,
                passed_threshold=False
            )
        
        # Check for implementation steps
        step_patterns = [r'step \d+', r'\d+\.', r'phase \d+']
        step_count = sum(len(re.findall(pattern, technical_content, re.IGNORECASE)) for pattern in step_patterns)
        if step_count >= 5:
            score += 2.0
        elif step_count >= 3:
            score += 1.0
        else:
            issues.append("Insufficient implementation step breakdown")
            suggestions.append("Provide detailed step-by-step implementation guidance")
        
        # Check for sub-steps
        substep_patterns = [r'sub-step', r'\d+\.\d+', r'substep']
        substep_count = sum(len(re.findall(pattern, technical_content, re.IGNORECASE)) for pattern in substep_patterns)
        if substep_count >= 8:
            score += 2.0
        elif substep_count >= 4:
            score += 1.0
        else:
            issues.append("Limited sub-step detail")
            suggestions.append("Break down implementation steps into detailed sub-steps")
        
        # Check for architecture considerations
        arch_keywords = ['architecture', 'component', 'design', 'pattern', 'structure', 'integration']
        arch_count = sum(1 for keyword in arch_keywords if keyword.lower() in technical_content.lower())
        if arch_count >= 3:
            score += 2.0
        elif arch_count >= 1:
            score += 1.0
        else:
            issues.append("Limited architecture considerations")
            suggestions.append("Include architecture and design considerations")
        
        # Check for performance considerations
        perf_keywords = ['performance', 'optimization', 'scalability', 'efficiency', 'memory', 'speed']
        perf_count = sum(1 for keyword in perf_keywords if keyword.lower() in technical_content.lower())
        if perf_count >= 2:
            score += 2.0
        elif perf_count >= 1:
            score += 1.0
        else:
            issues.append("No performance considerations mentioned")
            suggestions.append("Include performance and optimization considerations")
        
        # Check for testing guidance
        test_keywords = ['test', 'testing', 'validation', 'verify', 'unit test', 'integration test']
        test_count = sum(1 for keyword in test_keywords if keyword.lower() in technical_content.lower())
        if test_count >= 2:
            score += 2.0
        elif test_count >= 1:
            score += 1.0
        else:
            issues.append("Limited testing guidance")
            suggestions.append("Include testing strategy and validation approaches")
        
        passed_threshold = score >= self.thresholds['technical_depth']
        
        return QualityScore(
            dimension='technical_depth',
            score=min(score, max_score),
            max_score=max_score,
            issues=issues,
            suggestions=suggestions,
            passed_threshold=passed_threshold
        )
    
    def _score_risk_assessment(self, sections: Dict[str, str]) -> QualityScore:
        """Score risk assessment quality."""
        score = 0.0
        max_score = 10.0
        issues = []
        suggestions = []
        
        # Find risk assessment section
        risk_content = ""
        for section_name, content in sections.items():
            if 'risk' in section_name:
                risk_content = content
                break
        
        if not risk_content:
            issues.append("No risk assessment section found")
            suggestions.append("Add comprehensive risk assessment section")
            return QualityScore(
                dimension='risk_assessment',
                score=0.0,
                max_score=max_score,
                issues=issues,
                suggestions=suggestions,
                passed_threshold=False
            )
        
        # Check for risk table format
        if '|' in risk_content and 'Risk' in risk_content and 'Impact' in risk_content:
            score += 3.0
        else:
            issues.append("Risk assessment not in proper table format")
            suggestions.append("Format risks in a table with Risk, Impact, Probability, Mitigation columns")
        
        # Count number of risks
        risk_rows = len([line for line in risk_content.split('\n') if line.count('|') >= 3 and 'Risk' not in line])
        if risk_rows >= 4:
            score += 2.0
        elif risk_rows >= 2:
            score += 1.0
        else:
            issues.append("Insufficient number of risks identified")
            suggestions.append("Identify at least 4-6 relevant risks for comprehensive assessment")
        
        # Check for impact levels
        impact_levels = ['high', 'medium', 'low']
        impact_count = sum(1 for level in impact_levels if level.lower() in risk_content.lower())
        if impact_count >= 2:
            score += 2.0
        elif impact_count >= 1:
            score += 1.0
        else:
            issues.append("Missing impact level assessments")
            suggestions.append("Include impact levels (High/Medium/Low) for each risk")
        
        # Check for mitigation strategies
        mitigation_keywords = ['mitigation', 'strategy', 'prevent', 'reduce', 'manage', 'address']
        mitigation_count = sum(1 for keyword in mitigation_keywords if keyword.lower() in risk_content.lower())
        if mitigation_count >= 3:
            score += 2.0
        elif mitigation_count >= 1:
            score += 1.0
        else:
            issues.append("Limited mitigation strategies")
            suggestions.append("Provide detailed mitigation strategies for each risk")
        
        # Check for specific, relevant risks
        generic_risks = ['complexity', 'timeline', 'resources', 'dependencies']
        specific_indicators = ['api', 'database', 'integration', 'performance', 'security', 'user']
        specific_count = sum(1 for indicator in specific_indicators if indicator.lower() in risk_content.lower())
        
        if specific_count >= 2:
            score += 1.0
        else:
            issues.append("Risks appear generic rather than task-specific")
            suggestions.append("Include task-specific risks relevant to the implementation")
        
        passed_threshold = score >= self.thresholds['risk_assessment']
        
        return QualityScore(
            dimension='risk_assessment',
            score=min(score, max_score),
            max_score=max_score,
            issues=issues,
            suggestions=suggestions,
            passed_threshold=passed_threshold
        )
    
    def _generate_priority_improvements(self, dimension_scores: Dict[str, QualityScore]) -> List[str]:
        """Generate prioritized list of improvements needed."""
        improvements = []
        
        # Sort dimensions by score (lowest first) and weight (highest first)
        sorted_dimensions = sorted(
            dimension_scores.items(),
            key=lambda x: (x[1].score, -self.weights[x[0]])
        )
        
        for dimension, score in sorted_dimensions:
            if not score.passed_threshold:
                weight_priority = "HIGH" if self.weights[dimension] >= 0.20 else "MEDIUM" if self.weights[dimension] >= 0.15 else "LOW"
                improvements.append(f"{weight_priority} PRIORITY: {dimension.replace('_', ' ').title()} (Score: {score.score:.1f}/10)")
                
                # Add top suggestions
                for suggestion in score.suggestions[:2]:
                    improvements.append(f"  → {suggestion}")
        
        return improvements[:10]  # Limit to top 10 improvements
    
    def generate_improvement_report(self, result: OverallQualityResult) -> str:
        """Generate a detailed improvement report."""
        report = []
        report.append("# TaskHero AI Quality Assessment Report")
        report.append(f"**Overall Score:** {result.overall_score:.2f}/10")
        report.append(f"**Status:** {'✅ PASSED' if result.passed_minimum_threshold else '❌ NEEDS IMPROVEMENT'}")
        report.append("")
        
        # Dimension breakdown
        report.append("## Quality Dimension Scores")
        report.append("")
        for dimension, score in result.dimension_scores.items():
            status = "✅" if score.passed_threshold else "❌"
            report.append(f"### {status} {dimension.replace('_', ' ').title()}")
            report.append(f"**Score:** {score.score:.1f}/10 (Weight: {self.weights[dimension]*100:.0f}%)")
            
            if score.issues:
                report.append("**Issues:**")
                for issue in score.issues:
                    report.append(f"- {issue}")
            
            if score.suggestions:
                report.append("**Suggestions:**")
                for suggestion in score.suggestions:
                    report.append(f"- {suggestion}")
            report.append("")
        
        # Priority improvements
        if result.priority_improvements:
            report.append("## Priority Improvements")
            report.append("")
            for improvement in result.priority_improvements:
                report.append(f"- {improvement}")
            report.append("")
        
        report.append("---")
        report.append("*Generated by TaskHero AI Quality Scorer*")
        
        return "\n".join(report) 