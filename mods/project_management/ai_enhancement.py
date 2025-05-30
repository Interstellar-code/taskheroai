"""
AI Enhancement Service Module

Handles AI provider integration and content enhancement for task creation.
Extracted from ai_task_creator.py for better modularity and maintainability.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from ..ai.providers.provider_factory import ProviderFactory
from ..ai.providers.base_provider import AIProvider
from .context_analyzer_enhanced import EnhancedProjectContext

logger = logging.getLogger("TaskHeroAI.ProjectManagement.AIEnhancement")


class AIEnhancementService:
    """Service for AI-powered content enhancement in task creation."""

    def __init__(self, provider_factory: ProviderFactory):
        """Initialize the AI Enhancement Service.

        Args:
            provider_factory: Factory for creating AI providers
        """
        self.provider_factory = provider_factory
        self.ai_provider: Optional[AIProvider] = None
        self.ai_available = False

        # Load AI Enhancement Configuration from setup file or use defaults
        self.ai_config = self._load_ai_enhancement_config()

        # Current model optimization profile
        self.current_optimization = None

    def _load_ai_enhancement_config(self) -> Dict[str, Any]:
        """Load AI enhancement configuration from setup file or use defaults."""
        try:
            # Try to load from TaskHero setup file
            setup_file = Path('.taskhero_setup.json')
            if setup_file.exists():
                with open(setup_file, 'r', encoding='utf-8') as f:
                    setup_data = json.load(f)
                    ai_enhancement_config = setup_data.get('ai_enhancement_config', {})
                    if ai_enhancement_config:
                        logger.info("Loaded AI enhancement config from .taskhero_setup.json")
                        return ai_enhancement_config
        except Exception as e:
            logger.warning(f"Failed to load AI enhancement config from setup file: {e}")

        # Return default configuration
        return self._get_default_ai_config()

    def _get_default_ai_config(self) -> Dict[str, Any]:
        """Get default AI enhancement configuration."""
        return {
            'max_context_tokens': 6000,
            'max_response_tokens': 1500,
            'temperature': 0.6,
            'use_streaming': False,
            'fallback_enabled': True,
            'context_selection_threshold': 0.6,
            'model_optimizations': self._get_model_optimizations()
        }

    def _get_model_optimizations(self) -> Dict[str, Dict[str, Any]]:
        """Get model-specific optimization profiles."""
        return {
            # OpenAI Models
            'gpt-4': {
                'provider': 'openai',
                'max_context_tokens': 8000,
                'temperature': 0.7,
                'description_tokens': 1200,
                'requirements_tokens': 1000,
                'implementation_tokens': 1500,
                'technical_tokens': 1200,
                'risks_tokens': 800,
                'testing_tokens': 700,
                'quality_tier': 'premium'
            },
            'gpt-4-turbo-preview': {
                'provider': 'openai',
                'max_context_tokens': 7000,
                'temperature': 0.6,
                'description_tokens': 1000,
                'requirements_tokens': 800,
                'implementation_tokens': 1200,
                'technical_tokens': 1000,
                'risks_tokens': 700,
                'testing_tokens': 600,
                'quality_tier': 'balanced'
            },
            'gpt-3.5-turbo': {
                'provider': 'openai',
                'max_context_tokens': 4000,
                'temperature': 0.6,
                'description_tokens': 600,
                'requirements_tokens': 500,
                'implementation_tokens': 800,
                'technical_tokens': 600,
                'risks_tokens': 400,
                'testing_tokens': 400,
                'quality_tier': 'cost_effective'
            },
            # Anthropic Models
            'claude-opus-4-20250514': {
                'provider': 'anthropic',
                'max_context_tokens': 10000,
                'temperature': 0.7,
                'description_tokens': 1500,
                'requirements_tokens': 1200,
                'implementation_tokens': 1800,
                'technical_tokens': 1500,
                'risks_tokens': 1000,
                'testing_tokens': 800,
                'quality_tier': 'premium'
            },
            'claude-sonnet-4-20250514': {
                'provider': 'anthropic',
                'max_context_tokens': 8000,
                'temperature': 0.6,
                'description_tokens': 1000,
                'requirements_tokens': 800,
                'implementation_tokens': 1200,
                'technical_tokens': 1000,
                'risks_tokens': 700,
                'testing_tokens': 600,
                'quality_tier': 'balanced'
            },
            # Ollama Models
            'gemma3:4b': {
                'provider': 'ollama',
                'max_context_tokens': 6000,
                'temperature': 0.6,
                'description_tokens': 800,
                'requirements_tokens': 600,
                'implementation_tokens': 1000,
                'technical_tokens': 800,
                'risks_tokens': 600,
                'testing_tokens': 500,
                'quality_tier': 'local_optimized'
            },
            'llama3.2:latest': {
                'provider': 'ollama',
                'max_context_tokens': 7000,
                'temperature': 0.7,
                'description_tokens': 900,
                'requirements_tokens': 700,
                'implementation_tokens': 1100,
                'technical_tokens': 900,
                'risks_tokens': 650,
                'testing_tokens': 550,
                'quality_tier': 'local_general'
            },
            'codellama:latest': {
                'provider': 'ollama',
                'max_context_tokens': 8000,
                'temperature': 0.5,
                'description_tokens': 1000,
                'requirements_tokens': 800,
                'implementation_tokens': 1400,
                'technical_tokens': 1200,
                'risks_tokens': 700,
                'testing_tokens': 600,
                'quality_tier': 'local_code_focused'
            },
            # DeepSeek Models
            'deepseek-chat': {
                'provider': 'deepseek',
                'max_context_tokens': 7000,
                'temperature': 0.6,
                'description_tokens': 900,
                'requirements_tokens': 700,
                'implementation_tokens': 1100,
                'technical_tokens': 900,
                'risks_tokens': 650,
                'testing_tokens': 550,
                'quality_tier': 'cost_effective'
            },
            'deepseek-reasoner': {
                'provider': 'deepseek',
                'max_context_tokens': 8000,
                'temperature': 0.7,
                'description_tokens': 1100,
                'requirements_tokens': 900,
                'implementation_tokens': 1300,
                'technical_tokens': 1100,
                'risks_tokens': 800,
                'testing_tokens': 700,
                'quality_tier': 'reasoning_focused'
            },
            'deepseek-coder': {
                'provider': 'deepseek',
                'max_context_tokens': 8000,
                'temperature': 0.5,
                'description_tokens': 1000,
                'requirements_tokens': 800,
                'implementation_tokens': 1400,
                'technical_tokens': 1200,
                'risks_tokens': 700,
                'testing_tokens': 600,
                'quality_tier': 'code_specialist'
            },
            # OpenRouter Models
            'google/gemini-2.5-flash-preview-05-20': {
                'provider': 'openrouter',
                'max_context_tokens': 7000,
                'temperature': 0.6,
                'description_tokens': 900,
                'requirements_tokens': 700,
                'implementation_tokens': 1100,
                'technical_tokens': 900,
                'risks_tokens': 650,
                'testing_tokens': 550,
                'quality_tier': 'balanced'
            },
            'google/gemini-2.5-pro-preview': {
                'provider': 'openrouter',
                'max_context_tokens': 9000,
                'temperature': 0.7,
                'description_tokens': 1200,
                'requirements_tokens': 1000,
                'implementation_tokens': 1500,
                'technical_tokens': 1200,
                'risks_tokens': 800,
                'testing_tokens': 700,
                'quality_tier': 'premium'
            },
            'google/gemma-3-12b-it:free': {
                'provider': 'openrouter',
                'max_context_tokens': 5000,
                'temperature': 0.6,
                'description_tokens': 700,
                'requirements_tokens': 550,
                'implementation_tokens': 900,
                'technical_tokens': 700,
                'risks_tokens': 500,
                'testing_tokens': 450,
                'quality_tier': 'free_tier'
            }
        }

    async def initialize_provider(self) -> bool:
        """Initialize AI provider for real LLM integration."""
        try:
            if self.ai_provider is None:
                # First try to use the configured task provider from environment
                import os
                preferred_provider = os.getenv('AI_TASK_PROVIDER', '').lower()
                task_model = os.getenv('AI_TASK_MODEL', '')

                if preferred_provider:
                    try:
                        # Create provider with task-specific configuration
                        config_override = {}
                        if task_model and preferred_provider == 'ollama':
                            config_override['model'] = task_model
                            logger.info(f"Using task-specific model: {task_model}")

                        self.ai_provider = await self.provider_factory.create_provider(
                            preferred_provider, config_override if config_override else None
                        )

                        if self.ai_provider and await self.ai_provider.check_health():
                            self.ai_available = True
                            current_model = getattr(self.ai_provider, 'model', 'unknown')
                            # Load model-specific optimization
                            self._load_model_optimization(current_model)
                            logger.info(f"AI provider initialized (preferred): {preferred_provider} with model: {current_model}")
                            return True
                        else:
                            logger.warning(f"Preferred provider {preferred_provider} failed health check, falling back")
                    except Exception as e:
                        logger.warning(f"Failed to initialize preferred provider {preferred_provider}: {e}")

                # Fallback to best available provider
                best_provider = await self.provider_factory.get_best_available_provider()
                if best_provider:
                    # Apply task model configuration for fallback too
                    config_override = {}
                    if task_model and best_provider == 'ollama':
                        config_override['model'] = task_model

                    self.ai_provider = await self.provider_factory.create_provider(
                        best_provider, config_override if config_override else None
                    )
                    self.ai_available = True
                    current_model = getattr(self.ai_provider, 'model', 'unknown')
                    # Load model-specific optimization
                    self._load_model_optimization(current_model)
                    logger.info(f"AI provider initialized (fallback): {best_provider} with model: {current_model}")
                    return True
                else:
                    logger.warning("No AI providers available - using fallback mode")
                    self.ai_available = False
                    return False
            return self.ai_available
        except Exception as e:
            logger.warning(f"AI provider initialization failed: {e}")
            self.ai_available = False
            return False

    def _load_model_optimization(self, model_name: str) -> None:
        """Load optimization profile for the current model."""
        try:
            model_optimizations = self.ai_config.get('model_optimizations', {})
            if model_name in model_optimizations:
                self.current_optimization = model_optimizations[model_name]
                logger.info(f"Loaded optimization profile for model: {model_name} (tier: {self.current_optimization.get('quality_tier', 'unknown')})")
            else:
                # Use default optimization for unknown models
                self.current_optimization = {
                    'description_tokens': 800,
                    'requirements_tokens': 600,
                    'implementation_tokens': 1000,
                    'technical_tokens': 800,
                    'risks_tokens': 600,
                    'testing_tokens': 500,
                    'temperature': 0.6,
                    'quality_tier': 'default'
                }
                logger.warning(f"No optimization profile found for model: {model_name}, using defaults")
        except Exception as e:
            logger.warning(f"Failed to load model optimization: {e}")
            self.current_optimization = None

    # ============================================================================
    # TASK-126: Phase 2 - Enhanced Prompt Engineering Implementation
    # ============================================================================

    def _classify_task_type_and_complexity(self, title: str, description: str, task_type: str) -> Dict[str, str]:
        """Classify task type and complexity for specialized prompt selection."""
        classification = {
            'primary_type': task_type.lower(),
            'complexity': 'medium',
            'domain': 'general',
            'prompt_category': 'development'
        }

        title_lower = title.lower()
        desc_lower = description.lower()

        # Determine complexity
        complexity_indicators = {
            'simple': ['fix', 'update', 'change', 'modify', 'adjust'],
            'medium': ['implement', 'create', 'develop', 'build', 'add'],
            'complex': ['integrate', 'optimize', 'enhance', 'refactor', 'architecture', 'system']
        }

        for complexity, indicators in complexity_indicators.items():
            if any(indicator in title_lower or indicator in desc_lower for indicator in indicators):
                classification['complexity'] = complexity
                break

        # Determine domain
        if any(term in title_lower or term in desc_lower for term in ['ai', 'ml', 'intelligence', 'enhancement', 'provider']):
            classification['domain'] = 'ai_ml'
        elif any(term in title_lower or term in desc_lower for term in ['ui', 'visualization', 'kanban', 'display', 'interface']):
            classification['domain'] = 'ui_visualization'
        elif any(term in title_lower or term in desc_lower for term in ['api', 'integration', 'service', 'endpoint']):
            classification['domain'] = 'integration'
        elif any(term in title_lower or term in desc_lower for term in ['test', 'testing', 'validation', 'quality']):
            classification['domain'] = 'testing'
        elif any(term in title_lower or term in desc_lower for term in ['doc', 'documentation', 'guide', 'manual']):
            classification['domain'] = 'documentation'

        # Determine prompt category
        if classification['domain'] == 'ai_ml':
            classification['prompt_category'] = 'ai_enhancement'
        elif classification['domain'] == 'ui_visualization':
            classification['prompt_category'] = 'ui_development'
        elif classification['domain'] == 'integration':
            classification['prompt_category'] = 'integration'
        elif classification['domain'] == 'testing':
            classification['prompt_category'] = 'testing'
        elif classification['domain'] == 'documentation':
            classification['prompt_category'] = 'documentation'
        else:
            classification['prompt_category'] = 'development'

        return classification

    def _get_task_prompt_template(self, prompt_category: str, complexity: str) -> str:
        """Get specialized prompt template based on task category and complexity."""
        templates = {
            'ai_enhancement': self._get_ai_enhancement_prompt_template(complexity),
            'ui_development': self._get_ui_development_prompt_template(complexity),
            'integration': self._get_integration_prompt_template(complexity),
            'testing': self._get_testing_prompt_template(complexity),
            'documentation': self._get_documentation_prompt_template(complexity),
            'development': self._get_general_development_prompt_template(complexity)
        }

        return templates.get(prompt_category, templates['development'])

    def _get_ai_enhancement_prompt_template(self, complexity: str) -> str:
        """Get AI enhancement specific prompt template."""
        base_template = """You are an expert AI systems architect and prompt engineer creating comprehensive task descriptions for AI enhancement projects.

ORIGINAL USER REQUEST: {title}
DESCRIPTION: {description}
TASK TYPE: {task_type}

PROJECT CONTEXT:
{context}

QUALITY REFERENCE EXAMPLES:
{reference_examples}

INSTRUCTIONS FOR AI ENHANCEMENT TASKS:

1. PRESERVE the user's original intent and requirements completely
2. EXPAND with AI-specific technical implementation details
3. INCLUDE prompt engineering best practices and optimization strategies
4. PROVIDE clear AI model integration guidance
5. ADDRESS AI performance considerations and quality metrics
6. MAINTAIN focus on measurable AI improvements

ENHANCED DESCRIPTION STRUCTURE:
- Start with the user's original intent
- Add AI-specific technical context (models, providers, optimization)
- Include prompt engineering and context discovery strategies
- Mention AI performance metrics and quality validation
- Address AI integration points and fallback mechanisms
- Provide specific AI-focused acceptance criteria

CRITICAL AI ENHANCEMENT CONSIDERATIONS:
- Context discovery and relevance optimization
- Prompt engineering and template specialization
- AI model performance and quality scoring
- Multi-provider compatibility and fallback strategies
- Response validation and quality assurance
- Performance monitoring and optimization metrics

Generate a comprehensive description that enables any AI engineer to understand and implement this AI enhancement effectively."""

        if complexity == 'complex':
            base_template += """

ADDITIONAL COMPLEXITY CONSIDERATIONS:
- Multi-model optimization strategies
- Advanced prompt engineering techniques
- Comprehensive quality validation frameworks
- Performance benchmarking and regression testing
- Integration with existing AI infrastructure"""

        return base_template

    def _get_ui_development_prompt_template(self, complexity: str) -> str:
        """Get UI development specific prompt template."""
        return """You are an expert UI/UX architect creating comprehensive task descriptions for user interface development projects.

ORIGINAL USER REQUEST: {title}
DESCRIPTION: {description}
TASK TYPE: {task_type}

PROJECT CONTEXT:
{context}

QUALITY REFERENCE EXAMPLES:
{reference_examples}

INSTRUCTIONS FOR UI DEVELOPMENT TASKS:

1. PRESERVE the user's original intent and requirements completely
2. EXPAND with UI/UX specific technical implementation details
3. INCLUDE responsive design and accessibility considerations
4. PROVIDE clear component architecture and interaction patterns
5. ADDRESS performance optimization for UI rendering
6. MAINTAIN focus on user experience and usability

ENHANCED DESCRIPTION STRUCTURE:
- Start with the user's original intent
- Add UI-specific technical context (components, layouts, interactions)
- Include responsive design and accessibility requirements
- Mention performance considerations and optimization strategies
- Address integration with existing UI systems
- Provide specific UI-focused acceptance criteria

CRITICAL UI DEVELOPMENT CONSIDERATIONS:
- Component reusability and modularity
- Responsive design across different screen sizes
- Accessibility compliance (WCAG guidelines)
- Performance optimization (rendering, animations)
- Cross-browser compatibility
- User interaction patterns and feedback

Generate a comprehensive description that enables any UI developer to understand and implement this interface effectively."""

    def _get_integration_prompt_template(self, complexity: str) -> str:
        """Get integration specific prompt template."""
        return """You are an expert systems integration architect creating comprehensive task descriptions for integration projects.

ORIGINAL USER REQUEST: {title}
DESCRIPTION: {description}
TASK TYPE: {task_type}

PROJECT CONTEXT:
{context}

QUALITY REFERENCE EXAMPLES:
{reference_examples}

INSTRUCTIONS FOR INTEGRATION TASKS:

1. PRESERVE the user's original intent and requirements completely
2. EXPAND with integration-specific technical implementation details
3. INCLUDE API design, data flow, and communication protocols
4. PROVIDE clear service architecture and dependency management
5. ADDRESS error handling, retry mechanisms, and fallback strategies
6. MAINTAIN focus on reliability and maintainability

ENHANCED DESCRIPTION STRUCTURE:
- Start with the user's original intent
- Add integration-specific technical context (APIs, protocols, data formats)
- Include error handling and resilience strategies
- Mention performance and scalability considerations
- Address security and authentication requirements
- Provide specific integration-focused acceptance criteria

CRITICAL INTEGRATION CONSIDERATIONS:
- API design and versioning strategies
- Data transformation and validation
- Error handling and retry mechanisms
- Security and authentication protocols
- Performance and scalability requirements
- Monitoring and logging for troubleshooting

Generate a comprehensive description that enables any integration engineer to understand and implement this integration effectively."""

    def _get_testing_prompt_template(self, complexity: str) -> str:
        """Get testing specific prompt template."""
        return """You are an expert QA engineer creating comprehensive task descriptions for testing and quality assurance projects.

ORIGINAL USER REQUEST: {title}
DESCRIPTION: {description}
TASK TYPE: {task_type}

PROJECT CONTEXT:
{context}

QUALITY REFERENCE EXAMPLES:
{reference_examples}

INSTRUCTIONS FOR TESTING TASKS:

1. PRESERVE the user's original intent and requirements completely
2. EXPAND with testing-specific technical implementation details
3. INCLUDE test strategy, coverage requirements, and automation approaches
4. PROVIDE clear test case design and execution guidelines
5. ADDRESS performance testing, security testing, and edge cases
6. MAINTAIN focus on comprehensive quality validation

ENHANCED DESCRIPTION STRUCTURE:
- Start with the user's original intent
- Add testing-specific technical context (frameworks, tools, methodologies)
- Include test coverage and quality metrics
- Mention automation strategies and CI/CD integration
- Address different testing types (unit, integration, e2e)
- Provide specific testing-focused acceptance criteria

CRITICAL TESTING CONSIDERATIONS:
- Test coverage requirements and metrics
- Automation strategy and framework selection
- Performance and load testing requirements
- Security and vulnerability testing
- Edge case identification and validation
- CI/CD integration and reporting

Generate a comprehensive description that enables any QA engineer to understand and implement this testing strategy effectively."""

    def _get_documentation_prompt_template(self, complexity: str) -> str:
        """Get documentation specific prompt template."""
        return """You are an expert technical writer creating comprehensive task descriptions for documentation projects.

ORIGINAL USER REQUEST: {title}
DESCRIPTION: {description}
TASK TYPE: {task_type}

PROJECT CONTEXT:
{context}

QUALITY REFERENCE EXAMPLES:
{reference_examples}

INSTRUCTIONS FOR DOCUMENTATION TASKS:

1. PRESERVE the user's original intent and requirements completely
2. EXPAND with documentation-specific technical implementation details
3. INCLUDE content structure, style guidelines, and accessibility requirements
4. PROVIDE clear information architecture and user journey mapping
5. ADDRESS maintenance strategies and version control
6. MAINTAIN focus on user comprehension and actionability

ENHANCED DESCRIPTION STRUCTURE:
- Start with the user's original intent
- Add documentation-specific technical context (formats, tools, workflows)
- Include content strategy and information architecture
- Mention accessibility and internationalization considerations
- Address maintenance and update procedures
- Provide specific documentation-focused acceptance criteria

CRITICAL DOCUMENTATION CONSIDERATIONS:
- Content structure and information hierarchy
- Style guide compliance and consistency
- Accessibility and readability standards
- Version control and maintenance workflows
- User testing and feedback integration
- Multi-format publishing and distribution

Generate a comprehensive description that enables any technical writer to understand and implement this documentation effectively."""

    def _get_general_development_prompt_template(self, complexity: str) -> str:
        """Get general development prompt template."""
        return """You are an expert software architect creating comprehensive task descriptions for development projects.

ORIGINAL USER REQUEST: {title}
DESCRIPTION: {description}
TASK TYPE: {task_type}

PROJECT CONTEXT:
{context}

QUALITY REFERENCE EXAMPLES:
{reference_examples}

INSTRUCTIONS FOR DEVELOPMENT TASKS:

1. PRESERVE the user's original intent and requirements completely
2. EXPAND with technical implementation details and architectural considerations
3. INCLUDE code quality standards, testing requirements, and performance criteria
4. PROVIDE clear implementation guidance with concrete steps
5. ADDRESS potential challenges, dependencies, and integration points
6. MAINTAIN focus on maintainable, scalable solutions

ENHANCED DESCRIPTION STRUCTURE:
- Start with the user's original intent
- Add technical context and implementation details
- Include architectural considerations and design patterns
- Mention integration points and dependencies
- Address potential risks and mitigation strategies
- Provide specific development-focused acceptance criteria

CRITICAL DEVELOPMENT CONSIDERATIONS:
- Code quality and maintainability standards
- Performance optimization and scalability
- Security considerations and best practices
- Testing strategy and coverage requirements
- Documentation and knowledge transfer
- Deployment and monitoring considerations

Generate a comprehensive description that enables any developer to understand and implement this feature effectively."""

    def _build_enhanced_task_prompt(self, title: str, description: str, task_type: str,
                                  context: str, reference_examples: str = "") -> str:
        """Build enhanced prompt with task-specific instructions and quality guidelines."""
        try:
            # Classify the task for specialized prompt selection
            classification = self._classify_task_type_and_complexity(title, description, task_type)

            # Get appropriate prompt template
            prompt_template = self._get_task_prompt_template(
                classification['prompt_category'],
                classification['complexity']
            )

            # Add quality instructions specific to the task type
            quality_instructions = self._get_quality_instructions(classification['prompt_category'])

            # Build the complete prompt
            enhanced_prompt = prompt_template.format(
                title=title,
                description=description,
                task_type=task_type,
                context=context,
                reference_examples=reference_examples or self._get_default_reference_examples(classification['prompt_category'])
            )

            # Append quality instructions
            enhanced_prompt += f"\n\n{quality_instructions}"

            logger.info(f"Built enhanced prompt for {classification['prompt_category']} task (complexity: {classification['complexity']})")
            return enhanced_prompt

        except Exception as e:
            logger.error(f"Enhanced prompt building failed: {e}")
            # Fallback to basic prompt
            return self._build_fallback_prompt(title, description, task_type, context)

    def _get_quality_instructions(self, prompt_category: str) -> str:
        """Get quality-focused instructions for specific task categories."""
        quality_instructions = {
            'ai_enhancement': """
QUALITY STANDARDS FOR AI ENHANCEMENT TASKS:
✅ MEASURABLE AI IMPROVEMENTS: Include specific metrics (accuracy %, response time, quality scores)
✅ CONTEXT OPTIMIZATION: Detail context discovery strategies and relevance scoring
✅ PROMPT ENGINEERING: Specify prompt templates, classification systems, and optimization techniques
✅ MULTI-PROVIDER SUPPORT: Address compatibility across different AI providers and models
✅ QUALITY VALIDATION: Include comprehensive testing and validation frameworks
✅ PERFORMANCE BENCHMARKS: Define baseline metrics and improvement targets
✅ FALLBACK MECHANISMS: Ensure robust error handling and graceful degradation""",

            'ui_development': """
QUALITY STANDARDS FOR UI DEVELOPMENT TASKS:
✅ RESPONSIVE DESIGN: Specify breakpoints, mobile-first approach, and cross-device compatibility
✅ ACCESSIBILITY: Include WCAG compliance, keyboard navigation, and screen reader support
✅ PERFORMANCE: Define loading time targets, animation performance, and optimization strategies
✅ COMPONENT ARCHITECTURE: Detail reusable components, state management, and data flow
✅ USER EXPERIENCE: Include interaction patterns, feedback mechanisms, and usability testing
✅ CROSS-BROWSER SUPPORT: Specify browser compatibility requirements and testing strategies
✅ DESIGN SYSTEM: Ensure consistency with existing design tokens and style guidelines""",

            'integration': """
QUALITY STANDARDS FOR INTEGRATION TASKS:
✅ API DESIGN: Include versioning, documentation, and backward compatibility strategies
✅ ERROR HANDLING: Define comprehensive error codes, retry mechanisms, and circuit breakers
✅ SECURITY: Specify authentication, authorization, and data encryption requirements
✅ PERFORMANCE: Include throughput targets, latency requirements, and scalability considerations
✅ MONITORING: Define logging, metrics, and alerting for operational visibility
✅ DATA VALIDATION: Specify input validation, transformation rules, and data integrity checks
✅ RESILIENCE: Include timeout handling, graceful degradation, and disaster recovery""",

            'testing': """
QUALITY STANDARDS FOR TESTING TASKS:
✅ COVERAGE REQUIREMENTS: Specify minimum code coverage percentages and critical path testing
✅ TEST AUTOMATION: Include CI/CD integration, automated regression testing, and reporting
✅ PERFORMANCE TESTING: Define load testing scenarios, stress testing, and performance benchmarks
✅ SECURITY TESTING: Include vulnerability scanning, penetration testing, and security validation
✅ TEST DATA MANAGEMENT: Specify test data creation, anonymization, and cleanup procedures
✅ CROSS-ENVIRONMENT TESTING: Include staging, production-like testing, and environment parity
✅ DEFECT MANAGEMENT: Define bug tracking, severity classification, and resolution workflows""",

            'documentation': """
QUALITY STANDARDS FOR DOCUMENTATION TASKS:
✅ CONTENT STRUCTURE: Include clear hierarchy, navigation, and information architecture
✅ ACCESSIBILITY: Specify readability standards, alternative formats, and inclusive language
✅ ACCURACY: Include technical review processes, version control, and update procedures
✅ USER-CENTERED DESIGN: Define user personas, use cases, and task-oriented content
✅ SEARCHABILITY: Include SEO optimization, tagging, and content discoverability
✅ MAINTENANCE: Specify review cycles, content audits, and deprecation procedures
✅ MULTI-FORMAT SUPPORT: Include web, PDF, mobile, and print format considerations""",

            'development': """
QUALITY STANDARDS FOR DEVELOPMENT TASKS:
✅ CODE QUALITY: Include coding standards, code review processes, and static analysis
✅ TESTING STRATEGY: Specify unit tests, integration tests, and end-to-end testing requirements
✅ PERFORMANCE: Define performance targets, optimization strategies, and monitoring
✅ SECURITY: Include secure coding practices, vulnerability assessment, and compliance
✅ MAINTAINABILITY: Specify documentation, code organization, and refactoring considerations
✅ SCALABILITY: Include architecture patterns, resource management, and growth planning
✅ DEPLOYMENT: Define CI/CD pipelines, rollback strategies, and production readiness"""
        }

        return quality_instructions.get(prompt_category, quality_instructions['development'])

    def _get_default_reference_examples(self, prompt_category: str) -> str:
        """Get default reference examples for task categories."""
        examples = {
            'ai_enhancement': """
REFERENCE EXAMPLE - TASK-125 (Chat Performance Enhancement):
- Multi-pass context discovery (semantic, reference, project, quality)
- Specialized prompt templates for different query types
- Quality validation with scoring metrics
- Performance improvements: 15-20 relevant files vs previous 9
- Source weighting system for context prioritization""",

            'ui_development': """
REFERENCE EXAMPLE - TASK-003 (Kanban Board Visualization):
- Terminal-based UI with rich library formatting
- Three-column layout (Todo, InProgress, Done)
- Color coding for priorities and task types
- Interactive navigation with keyboard shortcuts
- Responsive design for different terminal sizes""",

            'integration': """
REFERENCE EXAMPLE - Integration Best Practices:
- RESTful API design with proper HTTP status codes
- Comprehensive error handling with specific error codes
- Authentication and authorization mechanisms
- Rate limiting and throttling strategies
- Monitoring and logging for operational visibility""",

            'testing': """
REFERENCE EXAMPLE - Testing Best Practices:
- Comprehensive test coverage (unit, integration, e2e)
- Automated testing in CI/CD pipelines
- Performance and load testing scenarios
- Security testing and vulnerability assessment
- Test data management and cleanup procedures""",

            'documentation': """
REFERENCE EXAMPLE - Documentation Best Practices:
- Clear information hierarchy and navigation
- Task-oriented content with step-by-step instructions
- Code examples and practical use cases
- Accessibility and readability standards
- Version control and maintenance procedures""",

            'development': """
REFERENCE EXAMPLE - Development Best Practices:
- Clean code principles and design patterns
- Comprehensive testing strategy
- Performance optimization and monitoring
- Security considerations and best practices
- Documentation and knowledge transfer"""
        }

        return examples.get(prompt_category, examples['development'])

    def _build_fallback_prompt(self, title: str, description: str, task_type: str, context: str) -> str:
        """Build fallback prompt when enhanced prompt building fails."""
        return f"""You are an expert technical writer creating comprehensive task descriptions.

ORIGINAL USER REQUEST: {title}
DESCRIPTION: {description}
TASK TYPE: {task_type}

PROJECT CONTEXT:
{context}

Create a detailed, comprehensive task description that preserves the user's original intent while expanding with technical implementation details, clear acceptance criteria, and specific implementation guidance."""

    def _get_optimized_tokens(self, token_type: str) -> int:
        """Get optimized token count for the current model."""
        if self.current_optimization:
            return self.current_optimization.get(token_type, 800)
        return self.ai_config.get('gemma_optimizations', {}).get(token_type, 800)

    def _get_optimized_temperature(self) -> float:
        """Get optimized temperature for the current model."""
        if self.current_optimization:
            return self.current_optimization.get('temperature', 0.6)
        return self.ai_config.get('temperature', 0.6)

    def save_ai_enhancement_config(self) -> bool:
        """Save current AI enhancement configuration to TaskHero setup file."""
        try:
            setup_file = Path('.taskhero_setup.json')
            setup_data = {}

            # Load existing setup data
            if setup_file.exists():
                with open(setup_file, 'r', encoding='utf-8') as f:
                    setup_data = json.load(f)

            # Update AI enhancement configuration
            setup_data['ai_enhancement_config'] = self.ai_config
            setup_data['ai_enhancement_config']['last_updated'] = '2025-05-29'
            setup_data['ai_enhancement_config']['version'] = '1.0'

            # Save updated configuration
            with open(setup_file, 'w', encoding='utf-8') as f:
                json.dump(setup_data, f, indent=2, ensure_ascii=False)

            logger.info("AI enhancement configuration saved to .taskhero_setup.json")
            return True

        except Exception as e:
            logger.error(f"Failed to save AI enhancement config: {e}")
            return False

    async def enhance_description_with_context(self, user_description: str, context: Dict[str, Any],
                                             enhanced_context: EnhancedProjectContext) -> str:
        """Enhance description with AI while preserving user's original intent."""
        try:
            if not await self.initialize_provider():
                return user_description

            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            # Build context information for AI (but keep user description primary)
            context_info = ""
            if enhanced_context.primary_file_analysis:
                primary_file = enhanced_context.primary_file_analysis
                context_info += f"\n\nPrimary file being worked on: {primary_file.file_path}"
                context_info += f"\nFile type: {primary_file.language} ({primary_file.file_type})"
                if primary_file.key_features:
                    context_info += f"\nKey features: {', '.join(primary_file.key_features[:3])}"

            if enhanced_context.contextual_recommendations:
                context_info += "\n\nContextual recommendations:"
                for rec in enhanced_context.contextual_recommendations[:3]:
                    context_info += f"\n- {rec.description}"

            # Build enhanced context string for prompt
            enhanced_context_str = f"Task Type: {task_type}\nTask Title: {title}{context_info}"

            # Use enhanced prompt building with task-specific templates
            prompt = self._build_enhanced_task_prompt(
                title=title,
                description=user_description,
                task_type=task_type,
                context=enhanced_context_str
            )

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=self._get_optimized_tokens('description_tokens'),
                temperature=self._get_optimized_temperature()
            )

            return response.strip()

        except Exception as e:
            logger.error(f"AI description enhancement with context failed: {e}")
            return user_description  # Return original description on failure

    async def generate_requirements_with_context(self, user_description: str, context: Dict[str, Any],
                                                enhanced_context: EnhancedProjectContext) -> List[str]:
        """Generate requirements with enhanced context awareness."""
        try:
            if not await self.initialize_provider():
                return self._generate_fallback_requirements(user_description, context)

            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            # Build context for AI
            context_info = ""
            if enhanced_context.primary_file_analysis:
                primary_file = enhanced_context.primary_file_analysis
                context_info += f"\n\nPrimary file: {primary_file.file_path}"
                if primary_file.functions:
                    context_info += f"\nExisting functions: {', '.join(primary_file.functions[:5])}"
                if primary_file.configuration_items:
                    context_info += f"\nConfiguration items: {len(primary_file.configuration_items)} found"

            prompt = f"""You are a senior business analyst creating comprehensive functional requirements for a development task.

TASK DETAILS:
- Title: {title}
- Description: {user_description}
- Type: {task_type}

TECHNICAL CONTEXT:
{context_info}

REQUIREMENTS GENERATION INSTRUCTIONS:

Generate 6-8 comprehensive functional requirements that are:
✅ SPECIFIC: Include exact criteria, numbers, percentages, timeframes
✅ MEASURABLE: Clear success criteria that can be verified
✅ TECHNICALLY DETAILED: Implementation specifics and constraints
✅ TESTABLE: Verifiable outcomes with clear pass/fail criteria
✅ ACTIONABLE: Developers can implement directly from these requirements

REQUIREMENT FORMAT:
Each requirement must start with "The system must" or "The component must" or "The application must"

ENHANCED REQUIREMENT EXAMPLES:
1. The system must validate user input within 100ms and reject inputs exceeding 255 characters with specific error messages
2. The component must create timestamped backup files before making changes and verify backup integrity using SHA-256 checksums
3. The application must provide specific error messages with error codes (ERR-001 to ERR-999) for each failure type and log all errors
4. The system must process files in batches of 50 items and display progress percentage updates every 10% completion
5. The component must maintain 99.9% uptime during normal operations and log all downtime events with timestamps
6. The application must support concurrent users up to 100 simultaneous connections with response times under 200ms
7. The system must implement role-based access control with at least 3 permission levels (read, write, admin)
8. The component must provide comprehensive audit logging with user actions, timestamps, and data changes

CRITICAL: Generate requirements that are specific to this task's context and technical needs. Include performance criteria, error handling, security considerations, and integration requirements where applicable.

Generate 6-8 requirements now:"""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=self._get_optimized_tokens('requirements_tokens'),
                temperature=self._get_optimized_temperature()
            )

            # Parse and structure requirements
            requirements = self._parse_requirements_response(response)
            return requirements if requirements else self._generate_fallback_requirements(user_description, context)

        except Exception as e:
            logger.error(f"AI requirements generation with context failed: {e}")
            return self._generate_fallback_requirements(user_description, context)

    async def generate_implementation_steps_with_context(self, user_description: str, context: Dict[str, Any],
                                                       enhanced_context: EnhancedProjectContext, reference_task_content: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate implementation steps with enhanced context awareness, adapting from reference if provided."""
        try:
            if not await self.initialize_provider():
                return self._generate_fallback_implementation_steps(user_description, context)

            task_type = context.get('task_type', 'Development')
            due_date = context.get('due_date')

            # Build specific context from primary file
            context_info = ""
            if enhanced_context.primary_file_analysis:
                primary_file = enhanced_context.primary_file_analysis
                context_info += f"\n\nPrimary file to modify: {primary_file.file_path}"
                context_info += f"\nFile type: {primary_file.language}"

                if primary_file.key_features:
                    context_info += f"\nExisting features: {', '.join(primary_file.key_features)}"

                if primary_file.functions:
                    context_info += f"\nExisting functions: {', '.join(primary_file.functions[:5])}"

                if primary_file.specific_patterns:
                    context_info += f"\nCode patterns: {', '.join(primary_file.specific_patterns)}"

            if reference_task_content:
                prompt = f"""You are a senior technical architect creating a comprehensive implementation plan for a development task. Your primary goal is to ADAPT the implementation steps found in the provided reference content to match the user's specific task.

TASK OVERVIEW:
- Title: {context.get('title', 'Task')}
- Description: {user_description}
- Type: {task_type}

TECHNICAL CONTEXT:
{context_info}

HIGH-CONFIDENCE REFERENCE CONTENT (ADAPT IMPLEMENTATION STEPS FROM THIS):
```markdown
{reference_task_content}
```

IMPLEMENTATION PLAN REQUIREMENTS:

Create a detailed 4-5 phase implementation plan with:
🎯 SPECIFIC PHASES: Each phase has clear objectives and scope
📋 DETAILED SUB-STEPS: 3-4 actionable sub-steps per phase
⏱️ REALISTIC TIMELINES: Estimated duration for each phase
🎁 CLEAR DELIVERABLES: Specific outputs and artifacts
🔧 TECHNICAL DETAILS: Code patterns, architecture considerations
✅ VALIDATION CRITERIA: How to verify phase completion

CRITICAL ADAPTATION STRATEGY:
1. Identify and extract implementation phases and sub-steps from the REFERENCE CONTENT.
2. ADAPT these phases and sub-steps to align perfectly with the user's "{context.get('title', 'Task')}" and "{user_description}".
3. Use the REFERENCE's terminology, structure, and level of detail as a guide.
4. DO NOT simply copy-paste. ADAPT and INTEGRATE.
5. Ensure the output is a cohesive, actionable implementation plan for the user's task.
6. Focus on achieving high content similarity with the adapted reference implementation steps.

Generate 4-5 comprehensive implementation phases (ADAPTED from reference, preserving user intent):"""
            else:
                prompt = f"""You are a senior technical architect creating a comprehensive implementation plan for a development task.

TASK OVERVIEW:
- Title: {context.get('title', 'Task')}
- Description: {user_description}
- Type: {task_type}

TECHNICAL CONTEXT:
{context_info}

IMPLEMENTATION PLAN REQUIREMENTS:

Create a detailed 4-5 phase implementation plan with:
🎯 SPECIFIC PHASES: Each phase has clear objectives and scope
📋 DETAILED SUB-STEPS: 3-4 actionable sub-steps per phase
⏱️ REALISTIC TIMELINES: Estimated duration for each phase
🎁 CLEAR DELIVERABLES: Specific outputs and artifacts
🔧 TECHNICAL DETAILS: Code patterns, architecture considerations
✅ VALIDATION CRITERIA: How to verify phase completion

PHASE TEMPLATE FORMAT:
Phase X: [Clear Phase Name] - Estimated: [Duration]
- [Specific actionable step with technical implementation details]
- [Specific actionable step with file/component references]
- [Specific actionable step with testing/validation approach]
- [Specific actionable step with integration considerations]
Deliverables: [Specific deliverable items with acceptance criteria]

ENHANCED PHASE EXAMPLES:

Phase 1: Requirements Analysis & Design - Estimated: 1-2 days
- Analyze existing codebase structure and identify integration points in [specific files]
- Create detailed technical specification document with API contracts and data models
- Design component architecture with clear separation of concerns and dependency injection
- Validate design with stakeholders and document approval criteria
Deliverables: Technical specification document, architecture diagrams, approved design review

Phase 2: Core Implementation - Estimated: 3-4 days
- Implement core business logic in [specific modules] following established patterns
- Create data access layer with proper error handling and transaction management
- Develop API endpoints with input validation, authentication, and rate limiting
- Write comprehensive unit tests achieving 90%+ code coverage
Deliverables: Core functionality implementation, unit test suite, API documentation

CRITICAL: Generate phases that are specific to this task's technical requirements and existing codebase context.

Generate 4-5 comprehensive implementation phases:"""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=self._get_optimized_tokens('implementation_tokens'),
                temperature=self._get_optimized_temperature()
            )

            # Parse response into structured format
            steps = self._parse_implementation_steps_response(response, due_date)
            return steps if steps else self._generate_fallback_implementation_steps(user_description, context)

        except Exception as e:
            logger.error(f"AI implementation steps generation with context failed: {e}")
            return self._generate_fallback_implementation_steps(user_description, context)

    def _parse_requirements_response(self, response: str) -> List[str]:
        """Parse AI response into structured requirements list."""
        try:
            logger.debug(f"Raw requirements response from AI: {response}")
            requirements = []
            lines = response.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Attempt to parse as JSON array first
                if line.startswith('[') and line.endswith(']'):
                    try:
                        json_reqs = json.loads(line)
                        if isinstance(json_reqs, list):
                            for req in json_reqs:
                                if isinstance(req, str) and req.strip():
                                    requirements.append(req.strip())
                            logger.debug(f"Parsed requirements from JSON: {requirements}")
                            return requirements[:8] # Limit to 8 requirements
                    except json.JSONDecodeError:
                        logger.debug("Response is not a valid JSON array, falling back to line-by-line parsing.")
                        pass # Not a JSON array, continue with line-by-line parsing

                # Remove numbering and clean up for non-JSON responses
                if line[0].isdigit() and '.' in line[:5]:
                    line = line.split('.', 1)[1].strip()
                elif line.startswith('-'):
                    line = line[1:].strip()

                # Ensure it starts with proper format
                if line and (line.startswith('The system must') or line.startswith('The script must') or
                           line.startswith('The application must') or line.startswith('The component must')):
                    requirements.append(line)

            logger.debug(f"Parsed requirements line-by-line: {requirements}")
            return requirements[:8]  # Limit to 8 requirements

        except Exception as e:
            logger.warning(f"Failed to parse requirements response: {e}")
            return []

    def _parse_implementation_steps_response(self, response: str, due_date: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured implementation steps."""
        try:
            steps = []
            current_phase = None
            current_substeps = []

            lines = response.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for phase header
                if line.startswith('Phase') and ':' in line:
                    # Save previous phase if exists
                    if current_phase:
                        current_phase['substeps'] = [{'description': step, 'completed': False} for step in current_substeps]
                        steps.append(current_phase)

                    # Start new phase
                    phase_parts = line.split(':', 1)
                    phase_name = phase_parts[1].strip()
                    if ' - Estimated:' in phase_name:
                        phase_name = phase_name.split(' - Estimated:')[0].strip()

                    current_phase = {
                        'title': phase_name,
                        'completed': False,
                        'in_progress': False,
                        'target_date': due_date,
                        'substeps': []
                    }
                    current_substeps = []

                # Check for substeps
                elif line.startswith('-') and current_phase:
                    substep = line[1:].strip()
                    if substep:
                        current_substeps.append(substep)

            # Add final phase
            if current_phase:
                current_phase['substeps'] = [{'description': step, 'completed': False} for step in current_substeps]
                steps.append(current_phase)

            return steps if steps else []

        except Exception as e:
            logger.warning(f"Failed to parse implementation steps response: {e}")
            return []

    def _generate_fallback_requirements(self, description: str, context: Dict[str, Any]) -> List[str]:
        """Generate fallback requirements when AI is not available."""
        task_type = context.get('task_type', 'Development')

        base_requirements = [
            f"The system must implement {description.lower()} according to specifications",
            "The system must handle errors gracefully and provide meaningful error messages",
            "The system must maintain data integrity and consistency",
            "The system must be tested with comprehensive unit and integration tests"
        ]

        if task_type.lower() == 'development':
            base_requirements.extend([
                "The system must follow established coding standards and best practices",
                "The system must be documented with clear API documentation"
            ])

        return base_requirements

    def _generate_fallback_implementation_steps(self, description: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fallback implementation steps when AI is not available."""
        due_date = context.get('due_date')

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
