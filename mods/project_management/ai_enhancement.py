"""
AI Enhancement Service Module

Handles AI provider integration and content enhancement for task creation.
Extracted from ai_task_creator.py for better modularity and maintainability.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
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
        
        # AI Enhancement Configuration
        self.ai_config = {
            'max_context_tokens': 8000,
            'max_response_tokens': 2000,
            'temperature': 0.7,
            'use_streaming': False,
            'fallback_enabled': True,
            'context_selection_threshold': 0.6
        }

    async def initialize_provider(self) -> bool:
        """Initialize AI provider for real LLM integration."""
        try:
            if self.ai_provider is None:
                # First try to use the configured task provider from environment
                import os
                preferred_provider = os.getenv('AI_TASK_PROVIDER', '').lower()

                if preferred_provider:
                    try:
                        # Try to create the preferred provider
                        self.ai_provider = await self.provider_factory.create_provider(preferred_provider)
                        if self.ai_provider and await self.ai_provider.check_health():
                            self.ai_available = True
                            logger.info(f"AI provider initialized (preferred): {preferred_provider}")
                            return True
                        else:
                            logger.warning(f"Preferred provider {preferred_provider} failed health check, falling back")
                    except Exception as e:
                        logger.warning(f"Failed to initialize preferred provider {preferred_provider}: {e}")

                # Fallback to best available provider
                best_provider = await self.provider_factory.get_best_available_provider()
                if best_provider:
                    self.ai_provider = await self.provider_factory.create_provider(best_provider)
                    self.ai_available = True
                    logger.info(f"AI provider initialized (fallback): {best_provider}")
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

            prompt = f"""You are enhancing a task description while preserving the user's original intent and requirements.

User's original description: {user_description}

Task type: {task_type}
Task title: {title}

{context_info}

Please enhance the description by:
1. Keeping the user's original requirements and intent unchanged
2. Adding technical context based on the identified files
3. Providing specific implementation guidance
4. Maintaining clarity and actionability

The enhanced description should start with the user's original intent and add contextual details that help with implementation."""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=self.ai_config['max_response_tokens'],
                temperature=self.ai_config['temperature']
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

            prompt = f"""Generate highly specific, measurable, and testable functional requirements for this task:

Task: {title}
Description: {user_description}
Task Type: {task_type}

{context_info}

CRITICAL: Requirements must be:
- SPECIFIC with exact criteria (use numbers, percentages, timeframes)
- MEASURABLE with clear success criteria
- TECHNICALLY DETAILED with implementation specifics
- TESTABLE with verifiable outcomes
- ACTIONABLE for developers

IMPORTANT: Format as a numbered list with each requirement on a new line. Each requirement MUST start with "The system must" or "The script must" and include specific criteria.

ENHANCED EXAMPLES:
1. The system must validate user input within 100ms and reject inputs exceeding 255 characters
2. The script must create timestamped backup files before making changes and verify backup integrity
3. The system must provide specific error messages with error codes (ERR-001 to ERR-999) for each failure type
4. The script must process files in batches of 50 items and display progress percentage every 10%
5. The system must maintain 99.9% uptime during normal operations and log all downtime events

Generate 6-8 highly specific requirements with measurable criteria. DO NOT use Python list format or quotes around requirements:"""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=800,
                temperature=0.6
            )

            # Parse and structure requirements
            requirements = self._parse_requirements_response(response)
            return requirements if requirements else self._generate_fallback_requirements(user_description, context)

        except Exception as e:
            logger.error(f"AI requirements generation with context failed: {e}")
            return self._generate_fallback_requirements(user_description, context)

    async def generate_implementation_steps_with_context(self, user_description: str, context: Dict[str, Any], 
                                                       enhanced_context: EnhancedProjectContext) -> List[Dict[str, Any]]:
        """Generate implementation steps with enhanced context awareness."""
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

            prompt = f"""Generate detailed implementation steps for this {task_type} task:

Task: {context.get('title', 'Task')}
Description: {user_description}
Task Type: {task_type}

{context_info}

Requirements:
- Create 4-5 implementation phases with specific sub-steps
- Each phase should have clear deliverables and estimated timeline
- Include specific technical details based on the codebase context
- Make steps actionable for developers
- Consider existing code patterns and architecture

Template for each phase:
Phase X: [Clear Phase Name] - Estimated: [Duration]
- [Specific actionable step with technical details]
- [Specific actionable step with technical details]
- [Specific actionable step with technical details]
Deliverables: [Clear deliverable items]

Generate 4-5 implementation phases:"""

            response = await self.ai_provider.generate_response(
                prompt,
                max_tokens=1200,
                temperature=0.6
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
            requirements = []
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Remove numbering and clean up
                if line[0].isdigit() and '.' in line[:5]:
                    line = line.split('.', 1)[1].strip()
                elif line.startswith('-'):
                    line = line[1:].strip()
                
                # Ensure it starts with proper format
                if line and (line.startswith('The system must') or line.startswith('The script must') or 
                           line.startswith('The application must') or line.startswith('The component must')):
                    requirements.append(line)
            
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
