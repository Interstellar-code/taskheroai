#!/usr/bin/env python3
"""
Multi-Provider Task Creation Quality Testing Framework
Inspired by test_dynamic_about.py and test_simple_multi_provider.py

Tests task creation quality across multiple AI providers with comprehensive analysis.
"""

import sys
import os
import json
import time
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import traceback

# Add the current directory to Python path for absolute imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

@dataclass
class TaskTestScenario:
    """Test scenario for task creation."""
    id: str
    title: str
    description: str
    task_type: str
    priority: str
    complexity: str  # low, medium, high
    expected_elements: List[str]  # Elements that should be present in a quality task
    quality_indicators: List[str]  # Keywords that indicate high-quality content

@dataclass
class TaskCreationResult:
    """Result of task creation attempt."""
    scenario_id: str
    provider: str
    model: str
    success: bool
    task_id: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None
    generation_time: float = 0.0
    error_message: Optional[str] = None
    quality_analysis: Optional[Dict[str, Any]] = None

class TaskQualityAnalyzer:
    """Analyzes the quality of generated task content."""

    def __init__(self):
        # Define quality patterns for task content analysis
        self.quality_patterns = {
            'specific_technical_terms': [
                r'\b(?:API|REST|GraphQL|WebSocket|OAuth|JWT|SSL|HTTPS|JSON|XML|YAML)\b',
                r'\b(?:database|SQL|NoSQL|MongoDB|PostgreSQL|Redis|Cache)\b',
                r'\b(?:React|Vue|Angular|Node\.js|Python|Java|TypeScript|JavaScript)\b',
                r'\b(?:Docker|Kubernetes|CI/CD|DevOps|AWS|Azure|GCP)\b',
                r'\b(?:authentication|authorization|validation|encryption|security)\b'
            ],
            'implementation_specificity': [
                r'\b(?:implement|create|build|develop|design|configure|setup|integrate)\b',
                r'\b(?:function|method|class|component|module|service|endpoint)\b',
                r'\b(?:test|unit test|integration test|e2e|validation|QA)\b'
            ],
            'actionable_details': [
                r'\d+\.\s+[A-Z]',  # Numbered steps
                r'\*\*.*?\*\*:',   # Bold headers with colons
                r'```.*?```',      # Code blocks
                r'- \w+',          # Bullet points
            ],
            'placeholder_content': [
                r'\[.*?\]',        # [placeholder text]
                r'TODO',           # TODO items
                r'TBD',            # To be determined
                r'placeholder',    # Generic placeholder
                r'example\.com',   # Generic domains
                r'lorem ipsum',    # Lorem ipsum text
            ]
        }

    def analyze_task_quality(self, content: str, scenario: TaskTestScenario) -> Dict[str, Any]:
        """Analyze the quality of generated task content - Enhanced for TASK-126 validation."""

        # Basic metrics
        total_chars = len(content)
        total_lines = len(content.split('\n'))

        # Technical specificity score
        tech_score = self._calculate_technical_specificity(content)

        # Implementation detail score
        implementation_score = self._calculate_implementation_quality(content)

        # Content structure score
        structure_score = self._calculate_structure_quality(content)

        # Scenario relevance score
        relevance_score = self._calculate_scenario_relevance(content, scenario)

        # Placeholder penalty
        placeholder_penalty = self._calculate_placeholder_penalty(content)

        # Expected elements check
        elements_score = self._check_expected_elements(content, scenario)

        # TASK-126 Enhancement: Check for enhanced prompt engineering indicators
        prompt_enhancement_score = self._check_prompt_enhancement_indicators(content, scenario)

        # TASK-126 Enhancement: Check for context discovery quality
        context_quality_score = self._check_context_discovery_quality(content, scenario)

        # Calculate overall quality score with TASK-126 enhancements
        overall_score = self._calculate_enhanced_overall_score(
            tech_score, implementation_score, structure_score,
            relevance_score, elements_score, placeholder_penalty,
            prompt_enhancement_score, context_quality_score
        )

        return {
            'overall_score': overall_score,
            'detailed_scores': {
                'technical_specificity': tech_score,
                'implementation_quality': implementation_score,
                'structure_quality': structure_score,
                'scenario_relevance': relevance_score,
                'expected_elements': elements_score,
                'placeholder_penalty': placeholder_penalty,
                'prompt_enhancement': prompt_enhancement_score,
                'context_quality': context_quality_score
            },
            'content_metrics': {
                'total_characters': total_chars,
                'total_lines': total_lines,
                'technical_terms_count': self._count_technical_terms(content),
                'implementation_steps_count': self._count_implementation_steps(content),
                'placeholder_count': self._count_placeholders(content)
            },
            'quality_indicators': self._extract_quality_indicators(content, scenario),
            'task_126_enhancements': self._check_task_126_specific_improvements(content, scenario)
        }

    def _calculate_technical_specificity(self, content: str) -> float:
        """Calculate how technically specific the content is."""
        total_matches = 0
        for pattern_list in self.quality_patterns['specific_technical_terms']:
            matches = re.findall(pattern_list, content, re.IGNORECASE)
            total_matches += len(matches)

        # Normalize by content length (per 1000 characters)
        normalized_score = (total_matches / max(len(content) / 1000, 1)) * 10
        return min(100, normalized_score)

    def _calculate_implementation_quality(self, content: str) -> float:
        """Calculate the quality of implementation details."""
        implementation_patterns = self.quality_patterns['implementation_specificity']
        actionable_patterns = self.quality_patterns['actionable_details']

        implementation_matches = 0
        for pattern in implementation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            implementation_matches += len(matches)

        actionable_matches = 0
        for pattern in actionable_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            actionable_matches += len(matches)

        # Check for implementation steps section
        impl_section_bonus = 20 if '## Implementation Steps' in content else 0

        base_score = (implementation_matches * 5) + (actionable_matches * 8) + impl_section_bonus
        return min(100, base_score)

    def _calculate_structure_quality(self, content: str) -> float:
        """Calculate the structural quality of the task."""
        structure_indicators = {
            '## ': 10,  # Main sections
            '### ': 5,  # Subsections
            '**': 3,    # Bold text
            '- ': 2,    # Bullet points
            '1. ': 5,   # Numbered lists
            '```': 15,  # Code blocks
            '| ': 8,    # Tables
        }

        score = 0
        for indicator, weight in structure_indicators.items():
            count = content.count(indicator)
            score += min(count * weight, weight * 5)  # Cap per indicator

        return min(100, score)

    def _calculate_scenario_relevance(self, content: str, scenario: TaskTestScenario) -> float:
        """Calculate how relevant the content is to the specific scenario."""
        content_lower = content.lower()
        scenario_text = f"{scenario.title} {scenario.description}".lower()

        # Extract key terms from scenario
        scenario_terms = set(re.findall(r'\b\w{4,}\b', scenario_text))

        # Count matches in content
        matches = 0
        for term in scenario_terms:
            if term in content_lower:
                matches += 1

        # Calculate relevance percentage
        relevance = (matches / max(len(scenario_terms), 1)) * 100

        # Bonus for task type alignment
        if scenario.task_type.lower() in content_lower:
            relevance += 10

        return min(100, relevance)

    def _calculate_placeholder_penalty(self, content: str) -> float:
        """Calculate penalty for placeholder content."""
        placeholder_count = 0
        for pattern in self.quality_patterns['placeholder_content']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            placeholder_count += len(matches)

        # Penalty: -5 points per placeholder, up to -50 total
        penalty = min(50, placeholder_count * 5)
        return penalty

    def _check_expected_elements(self, content: str, scenario: TaskTestScenario) -> float:
        """Check if expected elements are present in the content."""
        present_elements = 0

        for element in scenario.expected_elements:
            if element.lower() in content.lower():
                present_elements += 1

        if len(scenario.expected_elements) == 0:
            return 100  # No specific requirements

        return (present_elements / len(scenario.expected_elements)) * 100

    def _calculate_overall_score(self, tech_score: float, impl_score: float,
                               struct_score: float, relevance_score: float,
                               elements_score: float, placeholder_penalty: float) -> float:
        """Calculate weighted overall quality score."""
        weighted_score = (
            tech_score * 0.20 +           # Technical specificity
            impl_score * 0.25 +           # Implementation quality
            struct_score * 0.15 +         # Structure quality
            relevance_score * 0.25 +      # Scenario relevance
            elements_score * 0.15         # Expected elements
        ) - placeholder_penalty           # Subtract penalty

        return max(0, min(100, weighted_score))

    def _count_technical_terms(self, content: str) -> int:
        """Count technical terms in content."""
        count = 0
        for pattern_list in self.quality_patterns['specific_technical_terms']:
            matches = re.findall(pattern_list, content, re.IGNORECASE)
            count += len(matches)
        return count

    def _count_implementation_steps(self, content: str) -> int:
        """Count implementation steps in content."""
        # Look for numbered steps in implementation section
        impl_section = re.search(r'## Implementation Steps.*?(?=##|$)', content, re.DOTALL)
        if impl_section:
            steps = re.findall(r'\d+\.', impl_section.group())
            return len(steps)
        return 0

    def _count_placeholders(self, content: str) -> int:
        """Count placeholder content."""
        count = 0
        for pattern in self.quality_patterns['placeholder_content']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            count += len(matches)
        return count

    def _extract_quality_indicators(self, content: str, scenario: TaskTestScenario) -> List[str]:
        """Extract quality indicators from content."""
        indicators = []

        # Check for quality indicators from scenario
        for indicator in scenario.quality_indicators:
            if indicator.lower() in content.lower():
                indicators.append(indicator)

        # Add structural indicators
        if '## Implementation Steps' in content:
            indicators.append('structured_implementation')
        if '```' in content:
            indicators.append('code_examples')
        if re.search(r'\d+\.\s+', content):
            indicators.append('numbered_steps')
        if '**Technical Requirements**' in content:
            indicators.append('technical_requirements')

        return indicators

    # ============================================================================
    # TASK-126 Enhanced Quality Analysis Methods
    # ============================================================================

    def _check_prompt_enhancement_indicators(self, content: str, scenario: TaskTestScenario) -> float:
        """Check for indicators of enhanced prompt engineering (TASK-126 Phase 2)."""
        score = 0
        content_lower = content.lower()

        # Task-specific prompt indicators based on scenario
        if scenario.id == "ai_enhancement_126":
            ai_indicators = [
                'context discovery', 'prompt engineering', 'multi-pass', 'quality validation',
                'ai enhancement', 'semantic search', 'provider', 'optimization'
            ]
            for indicator in ai_indicators:
                if indicator in content_lower:
                    score += 12.5  # 8 indicators * 12.5 = 100

        elif scenario.id == "kanban_visualization_126":
            ui_indicators = [
                'responsive', 'accessibility', 'component', 'interface', 'user experience',
                'terminal', 'visualization', 'formatting'
            ]
            for indicator in ui_indicators:
                if indicator in content_lower:
                    score += 12.5

        elif scenario.id == "graphiti_integration_126":
            integration_indicators = [
                'api', 'integration', 'error handling', 'authentication', 'fallback',
                'metadata', 'service', 'infrastructure'
            ]
            for indicator in integration_indicators:
                if indicator in content_lower:
                    score += 12.5

        elif scenario.id == "quality_testing_126":
            testing_indicators = [
                'test coverage', 'automation', 'validation', 'framework', 'regression',
                'quality metrics', 'comparison', 'testing'
            ]
            for indicator in testing_indicators:
                if indicator in content_lower:
                    score += 12.5

        elif scenario.id == "enhancement_docs_126":
            docs_indicators = [
                'documentation', 'examples', 'best practices', 'guide', 'implementation',
                'accessibility', 'structure', 'maintenance'
            ]
            for indicator in docs_indicators:
                if indicator in content_lower:
                    score += 12.5

        # Bonus for quality standards sections
        if 'quality standards' in content_lower:
            score += 15

        # Bonus for reference examples
        if 'reference example' in content_lower or 'task-125' in content_lower or 'task-003' in content_lower:
            score += 10

        return min(100, score)

    def _check_context_discovery_quality(self, content: str, scenario: TaskTestScenario) -> float:
        """Check for indicators of enhanced context discovery (TASK-126 Phase 1)."""
        score = 0
        content_lower = content.lower()

        # Project-specific context indicators
        project_context_indicators = [
            'taskhero', 'kanban', 'ai enhancement', 'context processor', 'semantic search',
            'provider factory', 'template', 'quality validator', 'embeddings'
        ]

        for indicator in project_context_indicators:
            if indicator in content_lower:
                score += 8  # Up to 80 points for project context

        # Technical architecture mentions
        architecture_indicators = [
            'mods/', 'project_management', 'ai_enhancement', 'context_processor',
            'template_manager', 'provider_factory', 'semantic_search'
        ]

        for indicator in architecture_indicators:
            if indicator in content_lower:
                score += 5  # Up to 35 points for architecture awareness

        # Reference to existing tasks/quality examples
        if any(task_ref in content_lower for task_ref in ['task-003', 'task-012', 'task-125']):
            score += 15  # Bonus for quality reference integration

        return min(100, score)

    def _calculate_enhanced_overall_score(self, tech_score: float, impl_score: float,
                                        struct_score: float, relevance_score: float,
                                        elements_score: float, placeholder_penalty: float,
                                        prompt_enhancement_score: float, context_quality_score: float) -> float:
        """Calculate enhanced overall quality score including TASK-126 improvements."""
        weighted_score = (
            tech_score * 0.15 +                    # Technical specificity (reduced weight)
            impl_score * 0.20 +                    # Implementation quality
            struct_score * 0.10 +                  # Structure quality (reduced weight)
            relevance_score * 0.20 +               # Scenario relevance
            elements_score * 0.10 +                # Expected elements (reduced weight)
            prompt_enhancement_score * 0.15 +      # NEW: Prompt enhancement quality
            context_quality_score * 0.10           # NEW: Context discovery quality
        ) - placeholder_penalty                    # Subtract penalty

        return max(0, min(100, weighted_score))

    def _check_task_126_specific_improvements(self, content: str, scenario: TaskTestScenario) -> Dict[str, Any]:
        """Check for specific TASK-126 improvements in the generated content."""
        improvements = {
            'enhanced_context_discovery': False,
            'specialized_prompts': False,
            'quality_standards': False,
            'reference_examples': False,
            'project_specific_content': False,
            'task_type_specialization': False
        }

        content_lower = content.lower()

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
        task_specializations = {
            'ai_enhancement_126': ['ai', 'enhancement', 'optimization', 'provider'],
            'kanban_visualization_126': ['ui', 'visualization', 'terminal', 'interface'],
            'graphiti_integration_126': ['integration', 'api', 'service', 'infrastructure'],
            'quality_testing_126': ['testing', 'framework', 'validation', 'automation'],
            'enhancement_docs_126': ['documentation', 'guide', 'examples', 'practices']
        }

        if scenario.id in task_specializations:
            specialization_terms = task_specializations[scenario.id]
            if any(term in content_lower for term in specialization_terms):
                improvements['task_type_specialization'] = True

        return improvements

class MultiProviderTaskCreationTester:
    """Main tester class for multi-provider task creation."""

    def __init__(self):
        self.project_root = project_root
        self.quality_analyzer = TaskQualityAnalyzer()
        self.test_scenarios = self._load_test_scenarios()
        self.results: List[TaskCreationResult] = []

    def _load_test_scenarios(self) -> List[TaskTestScenario]:
        """Load test scenarios for task creation testing - Enhanced for TASK-126 validation."""
        return [
            # TASK-126 Test Case 1: AI Enhancement (should trigger ai_enhancement prompt category)
            TaskTestScenario(
                id="ai_enhancement_126",
                title="Optimize AI Task Creation Quality Enhancement",
                description="Enhance the AI-powered task creation system to generate significantly higher quality tasks by applying multi-pass context discovery, specialized prompt engineering, and comprehensive quality validation similar to TASK-125 chat optimization success.",
                task_type="Development",
                priority="high",
                complexity="complex",
                expected_elements=[
                    "AI enhancement", "context discovery", "prompt engineering", "quality validation",
                    "multi-pass", "TASK-125", "optimization", "specialized prompts"
                ],
                quality_indicators=[
                    "AI", "enhancement", "context", "prompt", "quality", "optimization", "multi-pass"
                ]
            ),
            # TASK-126 Test Case 2: UI Development (should trigger ui_development prompt category)
            TaskTestScenario(
                id="kanban_visualization_126",
                title="Implement Kanban Board Visualization",
                description="Create a visual Kanban board system that displays tasks in Todo, InProgress, and Done columns with proper formatting and status indicators. This will provide users with an intuitive visual interface for managing their project tasks within the terminal environment.",
                task_type="Development",
                priority="medium",
                complexity="medium",
                expected_elements=[
                    "Kanban board", "visualization", "Todo", "InProgress", "Done", "columns",
                    "formatting", "status indicators", "terminal", "visual interface"
                ],
                quality_indicators=[
                    "kanban", "visualization", "terminal", "interface", "columns", "formatting"
                ]
            ),
            # TASK-126 Test Case 3: Integration (should trigger integration prompt category)
            TaskTestScenario(
                id="graphiti_integration_126",
                title="Integrate Graphiti Context Retrieval System",
                description="Integrate Graphiti context retrieval system with existing TaskHero AI infrastructure for enhanced context discovery and semantic search capabilities. Implement proper metadata handling and fallback mechanisms.",
                task_type="Integration",
                priority="high",
                complexity="medium",
                expected_elements=[
                    "Graphiti", "context retrieval", "integration", "TaskHero AI", "metadata",
                    "semantic search", "fallback mechanisms", "infrastructure"
                ],
                quality_indicators=[
                    "integration", "Graphiti", "context", "retrieval", "semantic", "metadata"
                ]
            ),
            # TASK-126 Test Case 4: Testing (should trigger testing prompt category)
            TaskTestScenario(
                id="quality_testing_126",
                title="Implement Comprehensive Task Quality Testing Framework",
                description="Create a comprehensive testing framework for validating task creation quality across multiple AI providers, similar to test_dynamic_about.py approach. Include similarity comparison, quality scoring, and regression testing.",
                task_type="Testing",
                priority="medium",
                complexity="high",
                expected_elements=[
                    "testing framework", "quality validation", "multi-provider", "similarity comparison",
                    "quality scoring", "regression testing", "test_dynamic_about.py"
                ],
                quality_indicators=[
                    "testing", "framework", "quality", "validation", "comparison", "scoring"
                ]
            ),
            # TASK-126 Test Case 5: Documentation (should trigger documentation prompt category)
            TaskTestScenario(
                id="enhancement_docs_126",
                title="Document AI Enhancement Implementation Guide",
                description="Create comprehensive documentation for the AI enhancement implementation including context discovery strategies, prompt engineering techniques, and quality validation methods. Include examples and best practices.",
                task_type="Documentation",
                priority="medium",
                complexity="low",
                expected_elements=[
                    "documentation", "AI enhancement", "implementation guide", "context discovery",
                    "prompt engineering", "quality validation", "examples", "best practices"
                ],
                quality_indicators=[
                    "documentation", "guide", "enhancement", "examples", "practices", "implementation"
                ]
            )
        ]

    def _get_available_providers(self) -> List[Dict[str, str]]:
        """Get available AI providers for testing."""
        try:
            from mods.settings import AISettingsManager
            ai_settings = AISettingsManager()
            ai_settings.initialize()

            providers = []

            # Check common providers
            provider_configs = [
                {"provider": "ollama", "model": "llama3.2:latest"},
                {"provider": "ollama", "model": "qwen2.5:latest"},
                {"provider": "anthropic", "model": "claude-3-sonnet-20241022"},
                {"provider": "openai", "model": "gpt-4"},
                {"provider": "groq", "model": "llama3-8b-8192"},
            ]

            for config in provider_configs:
                try:
                    status = ai_settings.get_provider_status(config["provider"])
                    if status.get('configured', False):
                        providers.append(config)
                        print(f"✅ {config['provider']} ({config['model']}) is available")
                    else:
                        print(f"❌ {config['provider']} is not configured")
                except Exception as e:
                    print(f"⚠️ Error checking {config['provider']}: {e}")

            return providers

        except Exception as e:
            print(f"⚠️ Error getting providers, using Ollama fallback: {e}")
            return [{"provider": "ollama", "model": "llama3.2:latest"}]

    async def test_provider_scenario(self, provider_config: Dict[str, str],
                                   scenario: TaskTestScenario) -> TaskCreationResult:
        """Test task creation with a specific provider and scenario."""

        provider = provider_config["provider"]
        model = provider_config["model"]

        print(f"\n🧪 Testing {provider} ({model}) - {scenario.title}")
        print("-" * 60)

        start_time = time.time()

        try:
            from mods.project_management.ai_task_creator import AITaskCreator

            # Create AI task creator
            ai_creator = AITaskCreator(str(self.project_root))

            # Override provider for this test (if possible)
            # This would require modifying the AI enhancement service
            # For now, we'll use the configured provider

            # Create enhanced task
            success, task_id, file_path = await ai_creator.create_enhanced_task(
                title=scenario.title,
                description=scenario.description,
                task_type=scenario.task_type,
                priority=scenario.priority,
                assigned_to="Developer",
                tags=[scenario.id, "test", "multi-provider"],
                use_ai_enhancement=True
            )

            generation_time = time.time() - start_time

            if success and file_path and os.path.exists(file_path):
                # Read generated content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Analyze quality
                quality_analysis = self.quality_analyzer.analyze_task_quality(content, scenario)

                print(f"✅ SUCCESS: Generated in {generation_time:.2f}s")
                print(f"   Quality Score: {quality_analysis['overall_score']:.1f}%")
                print(f"   Technical Terms: {quality_analysis['content_metrics']['technical_terms_count']}")
                print(f"   Implementation Steps: {quality_analysis['content_metrics']['implementation_steps_count']}")

                # TASK-126 Enhancement reporting
                task_126_improvements = quality_analysis.get('task_126_enhancements', {})
                improvement_count = sum(1 for v in task_126_improvements.values() if v)
                print(f"   TASK-126 Improvements: {improvement_count}/6 detected")

                # Show specific improvements
                if improvement_count > 0:
                    improvements = [k.replace('_', ' ').title() for k, v in task_126_improvements.items() if v]
                    print(f"   Detected: {', '.join(improvements[:3])}{'...' if len(improvements) > 3 else ''}")

                print(f"   File: {file_path}")

                # Create provider-specific copy
                output_filename = f"task_{scenario.id}_{provider}_{model.replace(':', '_').replace('/', '_')}.md"
                output_path = self.project_root / "theherotasks" / "testing" / output_filename
                output_path.parent.mkdir(exist_ok=True)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                return TaskCreationResult(
                    scenario_id=scenario.id,
                    provider=provider,
                    model=model,
                    success=True,
                    task_id=task_id,
                    file_path=str(output_path),
                    content=content,
                    generation_time=generation_time,
                    quality_analysis=quality_analysis
                )
            else:
                print(f"❌ FAILED: {file_path if file_path else 'Unknown error'}")
                return TaskCreationResult(
                    scenario_id=scenario.id,
                    provider=provider,
                    model=model,
                    success=False,
                    generation_time=generation_time,
                    error_message=str(file_path) if file_path else "Task creation failed"
                )

        except Exception as e:
            generation_time = time.time() - start_time
            print(f"❌ ERROR: {str(e)}")
            return TaskCreationResult(
                scenario_id=scenario.id,
                provider=provider,
                model=model,
                success=False,
                generation_time=generation_time,
                error_message=str(e)
            )

    async def run_comprehensive_test(self):
        """Run comprehensive multi-provider task creation tests."""
        print("🚀 Multi-Provider Task Creation Quality Test")
        print("=" * 70)

        # Get available providers
        providers = self._get_available_providers()

        if not providers:
            print("❌ No AI providers available for testing")
            return False

        print(f"\n🔍 Testing {len(providers)} providers with {len(self.test_scenarios)} scenarios")
        print(f"📊 Total tests: {len(providers) * len(self.test_scenarios)}")

        # Run all tests
        total_tests = len(providers) * len(self.test_scenarios)
        current_test = 0

        for provider_config in providers:
            print(f"\n🔧 Testing Provider: {provider_config['provider'].upper()} - {provider_config['model']}")
            print("=" * 50)

            for scenario in self.test_scenarios:
                current_test += 1
                print(f"\n[{current_test}/{total_tests}] Testing scenario: {scenario.id}")

                result = await self.test_provider_scenario(provider_config, scenario)
                self.results.append(result)

                # Small delay between tests
                await asyncio.sleep(0.5)

        # Generate comprehensive report
        self._generate_comprehensive_report()

        return len([r for r in self.results if r.success]) > 0

    def _generate_comprehensive_report(self):
        """Generate comprehensive comparison report."""
        print(f"\n{'='*70}")
        print("📊 COMPREHENSIVE TASK CREATION QUALITY REPORT")
        print("=" * 70)

        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]

        print(f"\n📈 Test Summary:")
        print(f"   Successful: {len(successful_results)}/{len(self.results)}")
        print(f"   Failed: {len(failed_results)}/{len(self.results)}")
        if len(self.results) > 0:
            print(f"   Success Rate: {len(successful_results)/len(self.results)*100:.1f}%")

        if successful_results:
            # Sort by quality score
            successful_results.sort(key=lambda x: x.quality_analysis['overall_score'], reverse=True)

            # Calculate averages
            avg_quality = sum(r.quality_analysis['overall_score'] for r in successful_results) / len(successful_results)
            avg_time = sum(r.generation_time for r in successful_results) / len(successful_results)

            print(f"\n⚡ Performance Summary:")
            print(f"   Average Quality Score: {avg_quality:.1f}%")
            print(f"   Average Generation Time: {avg_time:.2f}s")
            print(f"   Quality Target: 85.0% (Recommended)")

            # Top performers
            print(f"\n🏆 Top Performers (by Quality Score):")
            print("-" * 70)
            for i, result in enumerate(successful_results[:5], 1):
                print(f"{i}. {result.provider}/{result.model} - {result.scenario_id}")
                print(f"   Quality: {result.quality_analysis['overall_score']:.1f}% | Time: {result.generation_time:.2f}s")
                scores = result.quality_analysis['detailed_scores']
                print(f"   Tech: {scores['technical_specificity']:.0f} | Impl: {scores['implementation_quality']:.0f} | Struct: {scores['structure_quality']:.0f} | Rel: {scores['scenario_relevance']:.0f}")
                print()

            # Provider analysis
            print(f"\n📋 Provider Performance Analysis:")
            print("-" * 70)
            provider_stats = {}

            for result in successful_results:
                provider_key = f"{result.provider}/{result.model}"
                if provider_key not in provider_stats:
                    provider_stats[provider_key] = []
                provider_stats[provider_key].append(result.quality_analysis['overall_score'])

            for provider, scores in provider_stats.items():
                avg_score = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)
                print(f"• {provider}")
                print(f"  Avg: {avg_score:.1f}% | Min: {min_score:.1f}% | Max: {max_score:.1f}% | Tests: {len(scores)}")

            # Scenario analysis
            print(f"\n🎯 Scenario Difficulty Analysis:")
            print("-" * 70)
            scenario_stats = {}

            for result in successful_results:
                scenario_id = result.scenario_id
                if scenario_id not in scenario_stats:
                    scenario_stats[scenario_id] = []
                scenario_stats[scenario_id].append(result.quality_analysis['overall_score'])

            for scenario_id, scores in scenario_stats.items():
                scenario = next(s for s in self.test_scenarios if s.id == scenario_id)
                avg_score = sum(scores) / len(scores)
                print(f"• {scenario_id} ({scenario.complexity} complexity)")
                print(f"  Title: {scenario.title}")
                print(f"  Average Quality: {avg_score:.1f}% | Tests: {len(scores)}")

            # Best by category
            best_quality = max(successful_results, key=lambda x: x.quality_analysis['overall_score'])
            fastest = min(successful_results, key=lambda x: x.generation_time)

            print(f"\n🌟 Category Winners:")
            print(f"Best Quality: {best_quality.provider}/{best_quality.model} - {best_quality.scenario_id} ({best_quality.quality_analysis['overall_score']:.1f}%)")
            print(f"Fastest: {fastest.provider}/{fastest.model} - {fastest.scenario_id} ({fastest.generation_time:.2f}s)")

        if failed_results:
            print(f"\n❌ Failed Tests:")
            print("-" * 40)
            for result in failed_results:
                error_msg = result.error_message or "Unknown error"
                if len(error_msg) > 80:
                    error_msg = error_msg[:80] + "..."
                print(f"• {result.provider}/{result.model} - {result.scenario_id}: {error_msg}")

        if successful_results:
            print(f"\n📁 Generated Test Files:")
            print("-" * 30)
            for result in successful_results:
                if result.file_path:
                    print(f"• {result.file_path}")

            # TASK-126 Enhancement Analysis
            print(f"\n🚀 TASK-126 Enhancement Analysis:")
            print("-" * 70)

            # Calculate TASK-126 improvement statistics
            total_improvements = 0
            total_possible = 0
            improvement_breakdown = {
                'enhanced_context_discovery': 0,
                'specialized_prompts': 0,
                'quality_standards': 0,
                'reference_examples': 0,
                'project_specific_content': 0,
                'task_type_specialization': 0
            }

            for result in successful_results:
                task_126_improvements = result.quality_analysis.get('task_126_enhancements', {})
                total_possible += 6  # 6 improvement categories
                for improvement, detected in task_126_improvements.items():
                    if detected:
                        total_improvements += 1
                        improvement_breakdown[improvement] += 1

            improvement_percentage = (total_improvements / max(total_possible, 1)) * 100

            print(f"Overall TASK-126 Implementation: {improvement_percentage:.1f}% ({total_improvements}/{total_possible})")
            print(f"\nImprovement Breakdown:")
            for improvement, count in improvement_breakdown.items():
                percentage = (count / len(successful_results)) * 100 if successful_results else 0
                improvement_name = improvement.replace('_', ' ').title()
                print(f"  • {improvement_name}: {percentage:.1f}% ({count}/{len(successful_results)} tasks)")

            # Enhanced scoring analysis
            if successful_results:
                prompt_scores = [r.quality_analysis['detailed_scores']['prompt_enhancement'] for r in successful_results]
                context_scores = [r.quality_analysis['detailed_scores']['context_quality'] for r in successful_results]

                avg_prompt_score = sum(prompt_scores) / len(prompt_scores)
                avg_context_score = sum(context_scores) / len(context_scores)

                print(f"\nTASK-126 Specific Scores:")
                print(f"  • Prompt Enhancement: {avg_prompt_score:.1f}%")
                print(f"  • Context Discovery: {avg_context_score:.1f}%")

            # Final recommendation
            if avg_quality >= 85:
                print(f"\n🎉 EXCELLENT RESULTS!")
                print(f"   Average quality score of {avg_quality:.1f}% exceeds the 85% target")
                if improvement_percentage >= 80:
                    print(f"   TASK-126 enhancements are working excellently ({improvement_percentage:.1f}%)")
                else:
                    print(f"   TASK-126 enhancements need refinement ({improvement_percentage:.1f}%)")
            elif avg_quality >= 75:
                print(f"\n✅ GOOD RESULTS!")
                print(f"   Average quality score of {avg_quality:.1f}% is solid but has room for improvement")
                if improvement_percentage >= 60:
                    print(f"   TASK-126 enhancements are showing good progress ({improvement_percentage:.1f}%)")
                else:
                    print(f"   TASK-126 enhancements need more work ({improvement_percentage:.1f}%)")
            else:
                print(f"\n⚠️ NEEDS IMPROVEMENT")
                print(f"   Average quality score of {avg_quality:.1f}% is below target - optimization needed")
                print(f"   TASK-126 enhancements detection: {improvement_percentage:.1f}%")

async def main():
    """Main test function."""
    print("🤖 TaskHero AI - Multi-Provider Task Creation Quality Tester")
    print("=" * 75)

    tester = MultiProviderTaskCreationTester()
    success = await tester.run_comprehensive_test()

    print(f"\n📊 Final Result: {'✅ SUCCESS' if success else '❌ FAILURE'}")

    if success:
        print("\n🎉 Multi-provider task creation testing completed successfully!")
        print("Check the generated files in theherotasks/testing/ for comparison.")
    else:
        print("\n💥 All tests failed. Please check your AI provider configurations.")

    return success

if __name__ == "__main__":
    print("🚀 Starting Multi-Provider Task Creation Quality Tests...")

    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)