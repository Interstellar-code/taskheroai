"""
AI-Enhanced Task Creator Module - Optimized

Optimized central orchestrator that delegates to modular components.
Maintains backward compatibility while dramatically reducing code complexity.

Phase 0: Modularization - Extracted components into focused modules
Phase 1: Graphiti Integration - Enhanced with graph-based context retrieval
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Import modular components
from .ai_enhancement import AIEnhancementService
from .context_processor import ContextProcessor
from .template_manager import TemplateManager
from .graphiti_retriever import GraphitiContextRetriever
from .task_manager import TaskManager
from .task_quality_validator import TaskQualityValidator
from .semantic_search import ContextChunk
from ..ai.providers.provider_factory import ProviderFactory

logger = logging.getLogger("TaskHeroAI.ProjectManagement.AITaskCreator")


class AIEnhancementProgressTracker:
    """Tracks progress of AI enhancement steps with detailed feedback."""

    def __init__(self):
        self.steps_completed = 0
        self.total_steps = 0
        self.current_step = ""
        self.step_results = {}
        self.start_time = None

    def start_step(self, step_description: str) -> None:
        """Start a new enhancement step."""
        self.current_step = step_description
        print(f"{step_description}")

    def complete_step(self, completion_message: str) -> None:
        """Complete the current step."""
        self.steps_completed += 1
        self.step_results[self.current_step] = "completed"
        print(f"{completion_message}")

    def fail_step(self, failure_message: str) -> None:
        """Mark current step as failed."""
        self.step_results[self.current_step] = "failed"
        print(f"{failure_message}")

    def update_progress(self, message: str) -> None:
        """Update progress within a step."""
        print(f"   {message}")

    def get_completion_rate(self) -> float:
        """Get completion rate as percentage."""
        if self.total_steps == 0:
            return 0.0
        return (self.steps_completed / self.total_steps) * 100


class AITaskCreator:
    """Optimized AI-enhanced task creation with modular delegation."""

    def __init__(self, project_root: Optional[str] = None):
        """Initialize the AI Task Creator with modular components.

        Args:
            project_root: Root directory for project management
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()

        # Initialize core components
        self.task_manager = TaskManager(project_root)
        self.quality_validator = TaskQualityValidator()

        # Initialize modular services
        self.ai_enhancement = AIEnhancementService(ProviderFactory())
        self.context_processor = ContextProcessor(str(self.project_root))
        self.template_manager = TemplateManager(project_root)

        # Initialize context retrieval (Graphiti + fallback)
        self.graphiti_retriever = GraphitiContextRetriever(str(self.project_root))

        # Configuration with TASK-126 enhancements
        self.config = {
            'use_graphiti': True,
            'fallback_to_semantic': True,
            'enable_ai_enhancement': True,
            'enable_progressive_creation': True,
            'quality_threshold': 0.7,
            'max_context_items': 10,
            # TASK-126 specific configurations
            'enable_task_126_enhancements': True,
            'enhanced_context_discovery': True,
            'specialized_prompt_engineering': True,
            'intelligent_template_processing': True,
            'comprehensive_quality_validation': True,
            'task_126_quality_threshold': 0.8
        }

        # Phase 4C: Task creation state for progressive wizard
        self.creation_state = {
            'step': 0,
            'total_steps': 4,
            'collected_data': {},
            'selected_context': [],
            'ai_enhancements': {},
            'quality_score': 0.0
        }

    async def _initialize_ai_provider(self) -> bool:
        """Initialize AI provider using the modular AI enhancement service."""
        return await self.ai_enhancement.initialize_provider()

    async def create_enhanced_task(self,
                                 title: str,
                                 description: str = "",
                                 task_type: str = "Development",
                                 priority: str = "medium",
                                 assigned_to: str = "Developer",
                                 due_date: Optional[str] = None,
                                 tags: List[str] = None,
                                 dependencies: List[str] = None,
                                 effort_estimate: str = "Medium",
                                 use_ai_enhancement: bool = True,
                                 selected_context: List[ContextChunk] = None,
                                 ai_enhancements: Dict[str, Any] = None) -> Tuple[bool, str, Optional[str]]:
        """Create an enhanced task using modular components.

        Args:
            title: Task title
            description: Task description/requirements
            task_type: Type of task (Development, Bug Fix, etc.)
            priority: Task priority (low, medium, high, critical)
            assigned_to: Who the task is assigned to
            due_date: Due date in YYYY-MM-DD format
            tags: List of tags for the task
            dependencies: List of dependent task IDs
            effort_estimate: Effort estimate (Small, Medium, Large)
            use_ai_enhancement: Whether to use AI for content enhancement
            selected_context: Pre-selected context chunks
            ai_enhancements: Pre-generated AI enhancements

        Returns:
            Tuple of (success, task_id, file_path or error_message)
        """
        try:
            # Step 1: Generate task ID
            task_id = self._generate_task_id()

            # Step 2: Enhanced metadata generation (simplified for optimization)
            enhanced_tags = tags or []
            enhanced_dependencies = dependencies or []
            enhanced_effort = effort_estimate

            # Step 3: Prepare base context using template manager
            context = self.template_manager.prepare_base_context(
                task_id=task_id,
                title=title,
                description=description,
                task_type=task_type,
                priority=priority,
                assigned_to=assigned_to,
                due_date=due_date,
                tags=enhanced_tags,
                dependencies=enhanced_dependencies,
                effort_estimate=enhanced_effort
            )

            # Step 4: Handle pre-generated AI enhancements (Phase 4C compatibility)
            if ai_enhancements:
                context = self._apply_ai_enhancements(context, ai_enhancements)
            elif use_ai_enhancement and self.config['enable_ai_enhancement']:
                # Step 5: TASK-126 Enhanced AI processing with all phases
                context = await self._enhance_with_task_126_ai(context, description)

            # Step 6: Template optimization using template manager
            ai_flow_diagram = context.get('flow_diagram')
            context = self.template_manager.optimize_template_context(context, task_type, description)

            # Step 7: Generate flow diagram if not already present
            if not ai_flow_diagram:
                flow_diagram_context = self.template_manager.generate_task_specific_flow_diagram(
                    task_type, description, context
                )
                context.update(flow_diagram_context)

            # Step 8: Ensure all template sections are properly populated
            context = self._ensure_template_completeness(context)

            # Step 8: Render task content using template manager
            task_content = self.template_manager.render_enhanced_task(context)

            # Step 9: Validate quality
            quality_result = self.quality_validator.validate_task_quality(task_content, context)

            # Step 10: Generate filename and save
            filename = self.template_manager.generate_filename(task_id, task_type, title)
            file_path = self._save_task_file(filename, task_content)

            # Step 11: Enhanced logging with TASK-126 metrics
            task_126_enhanced = context.get('task_126_enhanced', False)
            if task_126_enhanced:
                task_126_analysis = quality_result.get('task_126_enhancements', {})
                improvement_score = task_126_analysis.get('improvement_score', 0)
                reference_comparison = quality_result.get('reference_comparison', {})
                overall_similarity = reference_comparison.get('overall_reference_similarity', 0)

                logger.info(f"TASK-126 Enhanced task created: {task_id} at {file_path}")
                logger.info(f"  Quality: {quality_result['quality_level']} (Score: {quality_result['overall_score']:.1%})")
                logger.info(f"  TASK-126 Improvements: {improvement_score:.1%}")
                logger.info(f"  Reference Similarity: {overall_similarity:.1%}")

                # Log phase completion status
                phases_completed = []
                if context.get('task_126_phase_1_completed'): phases_completed.append("Context Discovery")
                if context.get('task_126_phase_2_completed'): phases_completed.append("Prompt Engineering")
                if context.get('task_126_phase_3_ready'): phases_completed.append("Template Processing")
                if context.get('task_126_phase_4_ready'): phases_completed.append("Quality Validation")

                logger.info(f"  TASK-126 Phases: {', '.join(phases_completed)}")
            else:
                logger.info(f"Enhanced task created: {task_id} at {file_path} (Quality: {quality_result['quality_level']}, Score: {quality_result['overall_score']:.2f})")

            return True, task_id, str(file_path)

        except Exception as e:
            logger.error(f"Error creating enhanced task: {e}")
            return False, "", str(e)

    def _apply_ai_enhancements(self, context: Dict[str, Any], ai_enhancements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply pre-generated AI enhancements to context (Phase 4C compatibility)."""
        # Enhanced description
        if ai_enhancements.get('detailed_description'):
            context['detailed_description'] = ai_enhancements['detailed_description']
        elif ai_enhancements.get('description'):
            context['detailed_description'] = ai_enhancements['description']

        # Requirements (support both list and string formats)
        if ai_enhancements.get('functional_requirements_list'):
            context['functional_requirements_list'] = ai_enhancements['functional_requirements_list']
            context['functional_requirements'] = ""  # Force template to use list
        elif ai_enhancements.get('requirements'):
            context['functional_requirements'] = ai_enhancements['requirements']

        # Implementation steps
        if ai_enhancements.get('implementation_steps'):
            context['implementation_steps'] = ai_enhancements['implementation_steps']

        # Risk analysis
        if ai_enhancements.get('risks'):
            context['risks'] = ai_enhancements['risks']

        # Visual elements
        if ai_enhancements.get('mermaid_diagram'):
            context['mermaid_diagram'] = ai_enhancements['mermaid_diagram']
            context['has_mermaid_diagram'] = True

        if ai_enhancements.get('ascii_art'):
            context['ascii_art'] = ai_enhancements['ascii_art']
            context['has_ascii_art'] = True

        # Flow diagrams
        if ai_enhancements.get('flow_diagram'):
            context['flow_diagram'] = ai_enhancements['flow_diagram']
        if ai_enhancements.get('flow_diagram_list'):
            context['flow_diagram_list'] = ai_enhancements['flow_diagram_list']

        # AI enhancement metadata
        if ai_enhancements.get('ai_context_used'):
            context['ai_context_used'] = ai_enhancements['ai_context_used']
        if ai_enhancements.get('graphiti_used'):
            context['graphiti_used'] = ai_enhancements['graphiti_used']
        if ai_enhancements.get('modular_enhanced'):
            context['modular_enhanced'] = ai_enhancements['modular_enhanced']

        # Mark as AI enhanced
        context['ai_enhancement_applied'] = True
        context['phase4c_enhanced'] = True

        return context

    async def _enhance_with_modular_ai(self, context: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Enhanced AI processing using modular components with Graphiti integration."""
        try:
            # Step 1: Enhanced context analysis using context processor
            task_type = context.get('task_type', 'Development')
            enhanced_context = self.context_processor.analyze_task_context_enhanced(
                description, task_type, specific_files=None
            )

            # Step 2: Collect relevant context using Graphiti or fallback
            title = context.get('title', '')
            combined_text = f"{title} {description}" if title else description

            # Include tags for enhanced context discovery
            tags = context.get('tags', [])
            if tags:
                tags_text = ' '.join(tags)
                combined_text = f"{combined_text} {tags_text}"

            # Try Graphiti first, fallback to semantic search
            relevant_context = await self._collect_context_with_graphiti(combined_text, context)

            # Step 3: Use AI enhancement service for content generation
            enhanced_context_dict = context.copy()

            try:
                # Enhanced description with AI and context
                if not enhanced_context_dict.get('detailed_description'):
                    enhanced_context_dict['detailed_description'] = await self.ai_enhancement.enhance_description_with_context(
                        description, context, enhanced_context
                    )

                # AI-generated requirements with context
                requirements_list = await self.ai_enhancement.generate_requirements_with_context(
                    description, enhanced_context_dict, enhanced_context
                )
                enhanced_context_dict['functional_requirements_list'] = requirements_list

                # Clear functional_requirements to force template to use list
                if requirements_list:
                    enhanced_context_dict['functional_requirements'] = ""

                # AI-generated implementation steps with context
                enhanced_context_dict['implementation_steps'] = await self.ai_enhancement.generate_implementation_steps_with_context(
                    description, enhanced_context_dict, enhanced_context
                )

                # Generate comprehensive technical considerations
                enhanced_context_dict.update(await self._generate_enhanced_technical_context(
                    description, enhanced_context_dict, enhanced_context
                ))

                # Generate enhanced risk assessment
                enhanced_context_dict['risks'] = await self._generate_enhanced_risks(
                    description, enhanced_context_dict, enhanced_context
                )

                # Generate testing strategy
                enhanced_context_dict.update(await self._generate_testing_context(
                    description, enhanced_context_dict, enhanced_context
                ))

            except Exception as ai_error:
                logger.warning(f"AI enhancement partially failed: {ai_error}")

            # Step 4: Add metadata
            enhanced_context_dict['ai_context_used'] = len(relevant_context)
            enhanced_context_dict['ai_enhancement_applied'] = True
            enhanced_context_dict['graphiti_used'] = self.config['use_graphiti'] and self.graphiti_retriever.is_available()
            enhanced_context_dict['modular_enhanced'] = True
            enhanced_context_dict['context_files_analyzed'] = len(enhanced_context.relevant_files) if enhanced_context.relevant_files else 0

            return enhanced_context_dict

        except Exception as e:
            logger.warning(f"Modular AI enhancement failed, using default context: {e}")
            return context

    async def _enhance_with_task_126_ai(self, context: Dict[str, Any], description: str) -> Dict[str, Any]:
        """TASK-126 Enhanced AI processing with all four phases integrated."""
        try:
            if not self.config.get('enable_task_126_enhancements', True):
                # Fallback to original modular AI enhancement
                return await self._enhance_with_modular_ai(context, description)

            logger.info("🚀 TASK-126: Starting enhanced AI processing with all phases")

            # Phase 1: Enhanced Context Discovery
            if self.config.get('enhanced_context_discovery', True):
                logger.info("📋 TASK-126 Phase 1: Enhanced Context Discovery")
                enhanced_context_chunks = await self._task_126_phase_1_context_discovery(context, description)
                context['task_126_context_chunks'] = len(enhanced_context_chunks)
                context['task_126_phase_1_completed'] = True
            else:
                enhanced_context_chunks = []

            # Phase 2: Specialized Prompt Engineering
            if self.config.get('specialized_prompt_engineering', True):
                logger.info("🤖 TASK-126 Phase 2: Specialized Prompt Engineering")
                enhanced_context = await self._task_126_phase_2_prompt_engineering(context, description, enhanced_context_chunks)
                context.update(enhanced_context)
                context['task_126_phase_2_completed'] = True

            # Phase 3: Intelligent Template Processing (handled by template_manager.optimize_template_context)
            # This will be called later in the main workflow
            context['task_126_phase_3_ready'] = True

            # Phase 4: Quality Validation Enhancement (handled by quality_validator.validate_task_quality)
            # This will be called later in the main workflow
            context['task_126_phase_4_ready'] = True

            # Add TASK-126 metadata
            context['task_126_enhanced'] = True
            context['task_126_version'] = '1.0'
            context['task_126_phases_enabled'] = {
                'enhanced_context_discovery': self.config.get('enhanced_context_discovery', True),
                'specialized_prompt_engineering': self.config.get('specialized_prompt_engineering', True),
                'intelligent_template_processing': self.config.get('intelligent_template_processing', True),
                'comprehensive_quality_validation': self.config.get('comprehensive_quality_validation', True)
            }

            logger.info("✅ TASK-126: Enhanced AI processing completed successfully")
            return context

        except Exception as e:
            logger.error(f"TASK-126 enhanced AI processing failed: {e}")
            # Fallback to original modular AI enhancement
            logger.info("🔄 TASK-126: Falling back to original modular AI enhancement")
            return await self._enhance_with_modular_ai(context, description)

    async def _task_126_phase_1_context_discovery(self, context: Dict[str, Any], description: str) -> List[ContextChunk]:
        """TASK-126 Phase 1: Enhanced Context Discovery with multi-pass semantic search."""
        try:
            # Use the enhanced context processor with TASK-126 improvements
            title = context.get('title', '')
            task_type = context.get('task_type', 'Development')
            combined_query = f"{title} {description}" if title else description

            # Enhanced context discovery using the context processor
            enhanced_chunks = self.context_processor.collect_embeddings_context(combined_query, context)

            logger.info(f"📋 TASK-126 Phase 1: Found {len(enhanced_chunks)} context chunks")
            return enhanced_chunks

        except Exception as e:
            logger.warning(f"TASK-126 Phase 1 context discovery failed: {e}")
            return []

    async def _task_126_phase_2_prompt_engineering(self, context: Dict[str, Any], description: str,
                                                 context_chunks: List[ContextChunk]) -> Dict[str, Any]:
        """TASK-126 Phase 2: Specialized Prompt Engineering with enhanced AI generation."""
        try:
            # Use the AI enhancement service with TASK-126 improvements
            title = context.get('title', '')
            task_type = context.get('task_type', 'Development')

            # Build enhanced context for AI generation
            enhanced_context_dict = context.copy()

            # Generate enhanced content using specialized prompts
            if not enhanced_context_dict.get('detailed_description'):
                enhanced_context_dict['detailed_description'] = await self.ai_enhancement.enhance_description_with_context(
                    description, context, None
                )

            # Generate requirements with enhanced prompting
            requirements_list = await self.ai_enhancement.generate_requirements_with_context(
                description, enhanced_context_dict, None
            )
            enhanced_context_dict['functional_requirements_list'] = requirements_list

            # Clear functional_requirements to force template to use list
            if requirements_list:
                enhanced_context_dict['functional_requirements'] = ""

            # Generate implementation steps with enhanced prompting
            enhanced_context_dict['implementation_steps'] = await self.ai_enhancement.generate_implementation_steps_with_context(
                description, enhanced_context_dict, None
            )

            # Generate enhanced technical considerations
            enhanced_context_dict.update(await self._generate_enhanced_technical_context(
                description, enhanced_context_dict, None
            ))

            # Generate enhanced risk assessment
            enhanced_context_dict['risks'] = await self._generate_enhanced_risks(
                description, enhanced_context_dict, None
            )

            # Generate testing strategy
            enhanced_context_dict.update(await self._generate_testing_context(
                description, enhanced_context_dict, None
            ))

            # Add Phase 2 metadata
            enhanced_context_dict['ai_enhancement_applied'] = True
            enhanced_context_dict['task_126_prompt_engineering'] = True

            logger.info("🤖 TASK-126 Phase 2: Specialized prompt engineering completed")
            return enhanced_context_dict

        except Exception as e:
            logger.warning(f"TASK-126 Phase 2 prompt engineering failed: {e}")
            return context

    async def _collect_context_with_graphiti(self, query: str, context: Dict[str, Any]) -> List[ContextChunk]:
        """Collect context using Graphiti with fallback to semantic search."""
        try:
            # Try Graphiti first if enabled and available
            if self.config['use_graphiti'] and self.graphiti_retriever.is_available():
                logger.info("Using Graphiti for context retrieval")
                graphiti_results = await self.graphiti_retriever.retrieve_context(
                    query=query,
                    max_results=self.config['max_context_items'],
                    file_types=self.context_processor._determine_relevant_file_types(query, context.get('task_type', 'Development'))
                )

                if graphiti_results:
                    logger.info(f"Graphiti returned {len(graphiti_results)} context chunks")
                    return graphiti_results

            # Fallback to semantic search
            if self.config['fallback_to_semantic']:
                logger.info("Using semantic search fallback for context retrieval")
                return self.context_processor.collect_embeddings_context(query, context)

            return []

        except Exception as e:
            logger.error(f"Context collection failed: {e}")
            return []

    async def _generate_enhanced_technical_context(self, description: str, context: Dict[str, Any],
                                                 enhanced_context) -> Dict[str, Any]:
        """Generate enhanced technical considerations using AI."""
        try:
            if not await self.ai_enhancement.initialize_provider():
                return {}

            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            prompt = f"""You are a senior technical architect providing comprehensive technical considerations for a development task.

TASK DETAILS:
- Title: {title}
- Description: {description}
- Type: {task_type}

Generate detailed technical considerations covering:

1. ARCHITECTURE & DESIGN:
   - Component architecture and design patterns
   - Integration patterns and API design
   - Data flow and state management

2. PERFORMANCE & SCALABILITY:
   - Performance requirements and benchmarks
   - Memory management and optimization
   - Loading and caching strategies

3. SECURITY & COMPATIBILITY:
   - Security considerations and requirements
   - Browser and system compatibility
   - Backward compatibility strategies

4. IMPLEMENTATION DETAILS:
   - Code organization and modularity
   - Error handling and logging
   - Testing and validation approaches

Format your response as specific, actionable technical guidance that developers can follow directly.

Provide detailed technical considerations:"""

            response = await self.ai_enhancement.ai_provider.generate_response(
                prompt,
                max_tokens=self.ai_enhancement._get_optimized_tokens('technical_tokens'),
                temperature=self.ai_enhancement._get_optimized_temperature()
            )

            # Parse response and structure it
            return {
                'technical_considerations': response.strip(),
                'component_architecture': 'AI-generated component architecture considerations',
                'performance_requirements': 'AI-generated performance requirements',
                'state_management': 'AI-generated state management strategy',
                'integration_patterns': 'AI-generated integration patterns'
            }

        except Exception as e:
            logger.warning(f"Enhanced technical context generation failed: {e}")
            return {}

    async def _generate_enhanced_risks(self, description: str, context: Dict[str, Any],
                                     enhanced_context) -> List[Dict[str, Any]]:
        """Generate enhanced risk assessment using AI."""
        try:
            if not await self.ai_enhancement.initialize_provider():
                return context.get('risks', [])

            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            prompt = f"""You are a senior project manager conducting a comprehensive risk assessment for a development task.

TASK DETAILS:
- Title: {title}
- Description: {description}
- Type: {task_type}

Generate 4-6 specific risks with detailed mitigation strategies. Consider:

TECHNICAL RISKS:
- Implementation complexity and unknowns
- Integration challenges and dependencies
- Performance and scalability concerns
- Security vulnerabilities

PROJECT RISKS:
- Timeline and resource constraints
- Stakeholder alignment and requirements changes
- External dependencies and third-party services
- Testing and quality assurance challenges

For each risk, provide:
- Specific risk description
- Impact level (High/Medium/Low)
- Probability (High/Medium/Low)
- Detailed mitigation strategy

Format as:
Risk: [Specific risk description]
Impact: [High/Medium/Low]
Probability: [High/Medium/Low]
Mitigation: [Detailed mitigation strategy]

Generate 4-6 comprehensive risks:"""

            response = await self.ai_enhancement.ai_provider.generate_response(
                prompt,
                max_tokens=self.ai_enhancement._get_optimized_tokens('risks_tokens'),
                temperature=self.ai_enhancement._get_optimized_temperature()
            )

            # Parse response into structured format
            risks = self._parse_risks_response(response)
            return risks if risks else context.get('risks', [])

        except Exception as e:
            logger.warning(f"Enhanced risk assessment generation failed: {e}")
            return context.get('risks', [])

    async def _generate_testing_context(self, description: str, context: Dict[str, Any],
                                      enhanced_context) -> Dict[str, Any]:
        """Generate enhanced testing strategy using AI."""
        try:
            if not await self.ai_enhancement.initialize_provider():
                return {}

            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            prompt = f"""You are a senior QA engineer creating a comprehensive testing strategy for a development task.

TASK DETAILS:
- Title: {title}
- Description: {description}
- Type: {task_type}

Generate a detailed testing strategy covering:

1. TESTING APPROACH:
   - Unit testing strategy and coverage goals
   - Integration testing requirements
   - End-to-end testing scenarios

2. TEST CASES:
   - Critical path testing scenarios
   - Edge cases and error conditions
   - Performance and load testing

3. VALIDATION CRITERIA:
   - Acceptance criteria and success metrics
   - Quality gates and review checkpoints
   - Automated testing requirements

Provide specific, actionable testing guidance that ensures comprehensive quality assurance.

Generate detailed testing strategy:"""

            response = await self.ai_enhancement.ai_provider.generate_response(
                prompt,
                max_tokens=self.ai_enhancement._get_optimized_tokens('testing_tokens'),
                temperature=self.ai_enhancement._get_optimized_temperature()
            )

            return {
                'testing_overview': response.strip(),
                'testing_strategy': 'Comprehensive testing approach with unit, integration, and end-to-end testing',
                'test_cases': [
                    {'name': 'Happy Path Testing', 'description': 'Test primary user workflows', 'expected': 'All features work as expected', 'status': 'Pending'},
                    {'name': 'Error Handling', 'description': 'Test error conditions and edge cases', 'expected': 'Graceful error handling', 'status': 'Pending'},
                    {'name': 'Performance Testing', 'description': 'Validate performance requirements', 'expected': 'Meets performance benchmarks', 'status': 'Pending'}
                ]
            }

        except Exception as e:
            logger.warning(f"Enhanced testing context generation failed: {e}")
            return {}

    def _parse_risks_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured risks list."""
        try:
            risks = []
            current_risk = {}

            lines = response.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('Risk:'):
                    # Save previous risk if exists
                    if current_risk and 'description' in current_risk:
                        risks.append(current_risk)

                    # Start new risk
                    current_risk = {
                        'description': line.replace('Risk:', '').strip(),
                        'impact': 'Medium',
                        'probability': 'Low',
                        'mitigation': 'Mitigation strategy to be defined'
                    }
                elif line.startswith('Impact:') and current_risk:
                    current_risk['impact'] = line.replace('Impact:', '').strip()
                elif line.startswith('Probability:') and current_risk:
                    current_risk['probability'] = line.replace('Probability:', '').strip()
                elif line.startswith('Mitigation:') and current_risk:
                    current_risk['mitigation'] = line.replace('Mitigation:', '').strip()

            # Add final risk
            if current_risk and 'description' in current_risk:
                risks.append(current_risk)

            return risks[:6]  # Limit to 6 risks

        except Exception as e:
            logger.warning(f"Failed to parse risks response: {e}")
            return []

    def _ensure_template_completeness(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all template sections have proper content WITHOUT overriding AI enhancements."""
        try:
            # CRITICAL: Do NOT override AI-enhanced content with generic templates
            # Only add minimal fallbacks if absolutely nothing is present

            # Only add basic flow diagram if completely missing AND no AI enhancement was attempted
            if not context.get('flow_diagram') and not context.get('ai_enhanced', False):
                # Generate task-specific flow diagram instead of generic search
                task_type = context.get('task_type', 'Development')
                title = context.get('title', 'Task')
                description = context.get('description', '')

                # Use template manager to generate appropriate flow diagram
                try:
                    flow_context = self.template_manager.generate_task_specific_flow_diagram(
                        task_type, description, context
                    )
                    context.update(flow_context)
                except Exception as e:
                    logger.warning(f"Flow diagram generation failed: {e}")
                    # Only use generic fallback as last resort
                    context['flow_diagram'] = f'''```mermaid
flowchart TD
    A[Start {title}] --> B[Analyze Requirements]
    B --> C[Design Solution]
    C --> D[Implement Changes]
    D --> E[Test Implementation]
    E --> F[Deploy/Complete]
```'''
                    context['flow_description'] = f'Basic workflow for {title}'
                    context['show_flow_diagram'] = True

            # CRITICAL: Do NOT add hardcoded implementation steps
            # Let AI enhancement handle this or fail transparently
            # Only add minimal fallback if absolutely nothing exists AND no AI enhancement was attempted
            if not context.get('implementation_steps') and not context.get('ai_enhanced', False):
                # Generate task-specific implementation steps based on title and description
                title = context.get('title', 'Task')
                description = context.get('description', '')

                # Create basic task-specific steps instead of hardcoded search steps
                context['implementation_steps'] = [
                    {
                        'title': f'Analysis & Planning for {title}',
                        'completed': False,
                        'in_progress': False,
                        'target_date': context.get('due_date'),
                        'substeps': [
                            {'description': f'Analyze requirements for {title.lower()}', 'completed': False},
                            {'description': f'Design architecture and approach', 'completed': False},
                            {'description': f'Create implementation plan', 'completed': False}
                        ]
                    },
                    {
                        'title': f'Implementation of {title}',
                        'completed': False,
                        'in_progress': False,
                        'target_date': context.get('due_date'),
                        'substeps': [
                            {'description': f'Implement core functionality', 'completed': False},
                            {'description': f'Add supporting features', 'completed': False},
                            {'description': f'Integrate with existing system', 'completed': False}
                        ]
                    },
                    {
                        'title': f'Testing & Validation',
                        'completed': False,
                        'in_progress': False,
                        'target_date': context.get('due_date'),
                        'substeps': [
                            {'description': f'Test {title.lower()} functionality', 'completed': False},
                            {'description': f'Validate requirements are met', 'completed': False},
                            {'description': f'Perform user acceptance testing', 'completed': False}
                        ]
                    }
                ]

            # Ensure functional requirements are properly formatted
            if context.get('functional_requirements_list'):
                # Clean up any formatting issues in requirements
                cleaned_requirements = []
                for req in context['functional_requirements_list']:
                    if isinstance(req, str) and req.strip():
                        # Clean up the requirement text
                        clean_req = req.strip()
                        if not clean_req.startswith('The system must') and not clean_req.startswith('The component must'):
                            clean_req = f"The system must {clean_req.lower()}"
                        cleaned_requirements.append(clean_req)
                context['functional_requirements_list'] = cleaned_requirements

            # CRITICAL: Do NOT add hardcoded UI design content
            # Let AI enhancement handle this or fail transparently
            # Only add minimal task-specific fallback if absolutely nothing exists AND no AI enhancement was attempted
            if not context.get('ascii_layout') and not context.get('ai_enhanced', False):
                title = context.get('title', 'Task')
                description = context.get('description', '')

                # Generate basic task-specific layout instead of hardcoded notification system
                context['ascii_layout'] = f'''┌─────────────────────────────────────────────────────────────┐
│ [{title} Layout]                                             │
│ ┌─────────────┐ ┌─────────────────────────────────────────┐ │
│ │ Navigation  │ │ Main Content Area                       │ │
│ │ - Menu      │ │ ┌─────────────────────────────────────┐ │ │
│ │ - Options   │ │ │ {title} Interface                   │ │ │
│ │ - Settings  │ │ ├─────────────────────────────────────┤ │ │
│ │             │ │ │ Content and Controls                │ │ │
│ │             │ │ │ Status: Ready                       │ │ │
│ │             │ │ └─────────────────────────────────────┘ │ │
│ └─────────────┘ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘'''

            # Only add basic template variables if missing AND no AI enhancement was attempted
            if not context.get('ai_enhanced', False):
                title = context.get('title', 'Task')
                context.setdefault('show_ui_design', True)  # Enable UI design section
                context.setdefault('ui_design_overview', f'User interface design for {title.lower()}')
                context.setdefault('ui_colors', 'Primary: #3b82f6, Secondary: #64748b, Success: #10b981, Warning: #f59e0b')
                context.setdefault('ui_typography', 'Inter font family, 14px base size, 500 weight for readability')
                context.setdefault('ui_spacing', '8px base unit, 16px component padding, 24px section margins')
                context.setdefault('ui_components', 'Standard UI components and controls')
                context.setdefault('ui_icons', 'Lucide icons: appropriate icons for functionality')

            return context

        except Exception as e:
            logger.warning(f"Template completeness check failed: {e}")
            return context

    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        existing_tasks = self.task_manager.get_all_tasks()
        max_id = 0

        for status_tasks in existing_tasks.values():
            for task in status_tasks:
                if task.task_id.startswith("TASK-"):
                    try:
                        task_num = int(task.task_id.split("-")[1])
                        max_id = max(max_id, task_num)
                    except (IndexError, ValueError):
                        continue

        return f"TASK-{max_id + 1:03d}"

    def _save_task_file(self, filename: str, content: str) -> Path:
        """Save task file to the appropriate directory."""
        tasks_dir = self.project_root / "theherotasks" / "todo"
        tasks_dir.mkdir(parents=True, exist_ok=True)

        file_path = tasks_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path

    # Backward compatibility methods - delegate to modular components
    async def index_codebase_with_graphiti(self) -> bool:
        """Index the codebase using Graphiti for enhanced context retrieval."""
        return await self.graphiti_retriever.index_codebase()

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all modular components."""
        return {
            'graphiti_available': self.graphiti_retriever.is_available(),
            'ai_enhancement_available': self.ai_enhancement.ai_available,
            'config': self.config.copy(),
            'project_root': str(self.project_root),
            'modular_components': {
                'ai_enhancement': 'loaded',
                'context_processor': 'loaded',
                'template_manager': 'loaded',
                'graphiti_retriever': 'loaded',
                'quality_validator': 'loaded'
            }
        }

    # Legacy method compatibility
    def _collect_embeddings_context(self, description: str, context: Dict[str, Any]) -> List[ContextChunk]:
        """Legacy method - delegate to context processor."""
        return self.context_processor.collect_embeddings_context(description, context)

    def _prepare_base_context(self, **kwargs) -> Dict[str, Any]:
        """Legacy method - delegate to template manager."""
        return self.template_manager.prepare_base_context(**kwargs)

    def _generate_filename(self, task_id: str, task_type: str, title: str) -> str:
        """Legacy method - delegate to template manager."""
        return self.template_manager.generate_filename(task_id, task_type, title)

    # Phase 4C Progressive Creation Methods
    async def create_task_progressive(self) -> Tuple[bool, str, str]:
        """Progressive task creation wizard with interactive context selection."""
        try:
            print("🚀 Starting Progressive Task Creation Wizard...")

            # Show AI provider information
            try:
                from ..code.indexer import _get_ai_provider_info
                ai_info = _get_ai_provider_info()
                print(f"🤖 AI Provider: {ai_info['description_full']} will enhance your task")
            except Exception as e:
                print("🤖 AI Provider info unavailable")

            # Step 1: Basic Information Collection
            success = await self._progressive_step_1_basic_info()
            if not success:
                return False, "", "User cancelled during basic information collection"

            # Step 2: Context Discovery & Selection
            success = await self._progressive_step_2_context_selection()
            if not success:
                return False, "", "User cancelled during context selection"

            # Step 3: AI Enhancement & Preview
            success = await self._progressive_step_3_ai_enhancement()
            if not success:
                return False, "", "User cancelled during AI enhancement"

            # Step 4: Final Review & Creation
            success, task_id, file_path = await self._progressive_step_4_final_creation()
            if not success:
                return False, "", "Task creation failed during final step"

            return True, task_id, file_path

        except Exception as e:
            logger.error(f"Progressive task creation failed: {e}")
            return False, "", str(e)

    async def create_task_interactive(self) -> Tuple[bool, str, str]:
        """Interactive task creation with user input prompts."""
        try:
            print("⚡ Quick Interactive Task Creation")
            print("=" * 40)

            # Collect basic information
            title = input("Task title: ").strip()
            if not title:
                return False, "", "Task title is required"

            description = input("Task description: ").strip()
            if not description:
                return False, "", "Task description is required"

            # Optional fields with defaults
            task_type = input("Task type (Development): ").strip() or "Development"
            priority = input("Priority (medium): ").strip() or "medium"
            assigned_to = input("Assigned to (Developer): ").strip() or "Developer"

            # Tags
            tags_input = input("Tags (comma-separated): ").strip()
            tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []

            # Create task using the enhanced method
            success, task_id, file_path = await self.create_enhanced_task(
                title=title,
                description=description,
                task_type=task_type,
                priority=priority,
                assigned_to=assigned_to,
                tags=tags,
                use_ai_enhancement=True
            )

            return success, task_id, file_path

        except Exception as e:
            logger.error(f"Interactive task creation failed: {e}")
            return False, "", str(e)

    # Progressive Creation Step Methods
    async def _progressive_step_1_basic_info(self) -> bool:
        """Step 1: Collect basic task information."""
        try:
            print("\n📝 Step 1/4: Basic Information")
            print("=" * 40)

            # Collect basic information
            title = input("Task title: ").strip()
            if not title:
                print("❌ Task title is required")
                return False

            description = input("Task description: ").strip()
            if not description:
                print("❌ Task description is required")
                return False

            # Optional fields
            task_type = input("Task type (Development): ").strip() or "Development"
            priority = input("Priority (medium): ").strip() or "medium"
            assigned_to = input("Assigned to (Developer): ").strip() or "Developer"

            # Tags
            tags_input = input("Tags (comma-separated): ").strip()
            tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []

            # Store in creation state
            self.creation_state['collected_data'] = {
                'title': title,
                'description': description,
                'task_type': task_type,
                'priority': priority,
                'assigned_to': assigned_to,
                'tags': tags
            }

            print("✅ Basic information collected")
            return True

        except Exception as e:
            logger.error(f"Step 1 failed: {e}")
            return False

    async def _progressive_step_2_context_selection(self) -> bool:
        """Step 2: Context discovery and selection."""
        try:
            print("\n🔍 Step 2/4: Context Discovery & Selection")
            print("=" * 40)

            data = self.creation_state['collected_data']
            query = f"{data['title']} {data['description']}"

            # Collect context using modular components
            print("🔍 Searching for relevant context...")
            context_chunks = await self._collect_context_with_graphiti(query, data)

            if not context_chunks:
                print("ℹ️  No relevant context found. Proceeding without context.")
                self.creation_state['selected_context'] = []
                return True

            # Display context options with proper deduplication for UI
            unique_files = {}
            for chunk in context_chunks:
                file_path = Path(chunk.file_path)
                file_key = str(file_path.resolve())

                # Keep the chunk with highest relevance score for each unique file
                if file_key not in unique_files or chunk.relevance_score > unique_files[file_key].relevance_score:
                    unique_files[file_key] = chunk

            unique_chunks = list(unique_files.values())

            # Enhanced sorting: prioritize foundational completed tasks, then by relevance score
            def enhanced_sort_key(chunk):
                score = chunk.relevance_score

                # Boost completed tasks that are foundational
                if '/done/' in chunk.file_path.lower():
                    if any(term in chunk.file_path.lower() for term in ['engine', 'core', 'ai', 'task']):
                        score += 0.5  # Significant boost for foundational completed tasks
                    else:
                        score += 0.2  # Moderate boost for other completed tasks

                # Boost files that match key concepts from the query
                description_lower = data.get('description', '').lower()
                title_lower = data.get('title', '').lower()
                file_path_lower = chunk.file_path.lower()

                # Extract key terms from user input
                user_terms = set()
                for text in [description_lower, title_lower]:
                    if 'kanban' in text:
                        user_terms.update(['kanban', 'board', 'visualization', 'column'])
                    if 'ai' in text or 'engine' in text:
                        user_terms.update(['ai', 'engine', 'task', 'hero'])
                    if 'git' in text:
                        user_terms.update(['git', 'integration', 'update'])
                    if 'graphiti' in text:
                        user_terms.update(['graphiti', 'context', 'retrieval'])

                # Boost files that match user's specific terms
                matching_terms = sum(1 for term in user_terms if term in file_path_lower)
                if matching_terms > 0:
                    score += 0.4 * matching_terms  # Significant boost for term matches

                # General boost for core files
                if any(term in file_path_lower for term in ['ai', 'engine', 'task', 'hero']):
                    score += 0.2

                return score

            unique_chunks.sort(key=enhanced_sort_key, reverse=True)

            # Display enhanced context selection interface
            self._display_enhanced_context_selection(unique_chunks[:5])

            # Update context_chunks to use deduplicated list for selection
            context_chunks = unique_chunks

            # Enhanced user selection with new options
            selection = input("\nSelect context (1,2,3 or 'all' or 'none' or 'auto' or 'preview X'): ").strip().lower()

            # Handle enhanced selection options
            if selection == 'none':
                self.creation_state['selected_context'] = []
            elif selection == 'all':
                self.creation_state['selected_context'] = context_chunks[:5]
            elif selection in ['auto', 'smart']:
                # Smart auto-selection
                auto_selected = self._smart_auto_select_context(context_chunks)
                print(f"🤖 Auto-selected {len(auto_selected)} files based on relevance:")
                for i, chunk in enumerate(auto_selected):
                    file_name = Path(chunk.file_path).name
                    print(f"  ✓ {file_name} (score: {chunk.relevance_score:.3f})")

                confirm = input("Use auto-selection? (Y/n): ").strip().lower()
                if confirm in ['n', 'no']:
                    print("⚠️  Auto-selection cancelled, using top 3")
                    self.creation_state['selected_context'] = context_chunks[:3]
                else:
                    self.creation_state['selected_context'] = auto_selected
            elif selection.startswith('preview '):
                # Handle preview command
                try:
                    preview_num = int(selection.split()[1]) - 1
                    if 0 <= preview_num < len(context_chunks):
                        self._show_file_preview(context_chunks[preview_num])
                        # Ask for selection again after preview
                        return await self._progressive_step_2_context_selection()
                    else:
                        print("⚠️  Invalid file number for preview")
                        self.creation_state['selected_context'] = context_chunks[:3]
                except (IndexError, ValueError):
                    print("⚠️  Invalid preview command format. Use 'preview X' where X is file number")
                    self.creation_state['selected_context'] = context_chunks[:3]
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                    selected = [context_chunks[i] for i in indices if 0 <= i < len(context_chunks)]
                    self.creation_state['selected_context'] = selected
                except:
                    print("⚠️  Invalid selection, using top 3")
                    self.creation_state['selected_context'] = context_chunks[:3]

            print(f"✅ Selected {len(self.creation_state['selected_context'])} context files")
            return True

        except Exception as e:
            logger.error(f"Step 2 failed: {e}")
            return False

    async def _progressive_step_3_ai_enhancement(self) -> bool:
        """Step 3: Comprehensive AI enhancement with detailed progress tracking."""
        try:
            print("\n🧠 Step 3/4: AI Enhancement & Preview")
            print("=" * 60)

            data = self.creation_state['collected_data']

            # Initialize progress tracker
            progress_tracker = AIEnhancementProgressTracker()

            # Step 1: AI Provider Initialization
            progress_tracker.start_step("🚀 Initializing AI provider...")
            ai_ready = await self._initialize_ai_provider()
            if not ai_ready:
                progress_tracker.fail_step("❌ AI provider initialization failed")
                print("⚠️  Continuing with basic enhancement...")
                return await self._progressive_step_3_basic_enhancement(data)

            # Show AI provider information
            try:
                from ..code.indexer import _get_ai_provider_info
                ai_info = _get_ai_provider_info()
                progress_tracker.complete_step(f"✅ AI provider ready: {ai_info['description_full']}")
            except Exception as e:
                progress_tracker.complete_step("✅ AI provider ready")

            # Step 2: Context Preparation
            progress_tracker.start_step("📋 Preparing enhancement context...")
            context = self.template_manager.prepare_base_context(**data)
            progress_tracker.complete_step("✅ Context prepared")

            # Step 3: AI Analysis
            progress_tracker.start_step("🤖 AI is analyzing your task with selected context...")
            enhanced_context = await self._comprehensive_ai_enhancement(
                context, data['description'], progress_tracker
            )

            # Store enhancements and mark as AI-enhanced
            enhanced_context['ai_enhanced'] = True
            self.creation_state['ai_enhancements'] = enhanced_context

            # Step 4: Quality Assessment
            progress_tracker.start_step("📊 Calculating quality metrics...")
            quality_score = self._calculate_enhancement_quality_score(enhanced_context)
            self.creation_state['quality_score'] = quality_score
            progress_tracker.complete_step(f"✅ Quality assessment complete")

            # Display comprehensive enhancement summary
            self._display_enhancement_summary(enhanced_context, quality_score, progress_tracker)

            # User confirmation
            proceed = input("\nProceed with this enhancement? (Y/n): ").strip().lower()
            if proceed in ['n', 'no']:
                return False

            print("✅ AI enhancement applied successfully")
            return True

        except Exception as e:
            logger.error(f"Step 3 comprehensive enhancement failed: {e}")
            print(f"❌ Enhancement failed: {e}")
            return False

    async def _comprehensive_ai_enhancement(self, context: Dict[str, Any], description: str,
                                          progress_tracker: AIEnhancementProgressTracker) -> Dict[str, Any]:
        """Perform comprehensive AI enhancement with detailed progress tracking."""
        try:
            enhanced_context = context.copy()

            # Analyze context once for all steps
            selected_context = self.creation_state.get('selected_context', [])
            context_analysis = self._analyze_context_content(selected_context, context.get('title', ''), description)

            # Step 1: Description Enhancement
            progress_tracker.start_step("🔄 Enhancing description...")
            enhanced_description = await self._enhance_description_step(context, description, progress_tracker, context_analysis)
            if enhanced_description:
                enhanced_context['detailed_description'] = enhanced_description
                progress_tracker.complete_step("✅ Description enhanced")
            else:
                progress_tracker.fail_step("⚠️  Description enhancement failed, using original")
                enhanced_context['detailed_description'] = description

            # Step 2: Requirements Generation
            progress_tracker.start_step("🔄 Generating requirements...")
            requirements = await self._generate_requirements_step(context, description, progress_tracker, context_analysis)
            if requirements:
                enhanced_context['functional_requirements_list'] = requirements
                enhanced_context['functional_requirements'] = ""  # Force template to use list
                progress_tracker.complete_step(f"✅ Generated {len(requirements)} requirements")
            else:
                progress_tracker.fail_step("⚠️  Requirements generation failed")

            # Step 3: Implementation Steps Generation
            progress_tracker.start_step("🔄 Generating implementation steps...")
            implementation_steps = await self._generate_implementation_steps_step(context, description, progress_tracker, context_analysis)
            if implementation_steps:
                enhanced_context['implementation_steps'] = implementation_steps
                progress_tracker.complete_step(f"✅ Generated {len(implementation_steps)} implementation steps")
            else:
                progress_tracker.fail_step("⚠️  Implementation steps generation failed")

            # Step 4: Risk Analysis
            progress_tracker.start_step("🔄 Analyzing risks...")
            risks = await self._analyze_risks_step(context, description, progress_tracker)
            if risks:
                enhanced_context['risks'] = risks
                progress_tracker.complete_step(f"✅ Identified {len(risks)} potential risks")
            else:
                progress_tracker.fail_step("⚠️  Risk analysis failed")

            # Step 5: Visual Elements Generation
            progress_tracker.start_step("🔄 Generating visual elements...")
            visual_elements = await self._generate_visual_elements_step(context, description, progress_tracker)
            if visual_elements:
                enhanced_context.update(visual_elements)
                progress_tracker.complete_step("✅ Generated visual elements (Mermaid diagrams, ASCII art)")
            else:
                progress_tracker.fail_step("⚠️  Visual elements generation failed")

            # Step 6: Flow Diagrams Creation
            progress_tracker.start_step("🔄 Creating flow diagrams...")
            flow_diagrams = await self._create_flow_diagrams_step(context, description, progress_tracker)
            if flow_diagrams:
                enhanced_context.update(flow_diagrams)
                progress_tracker.complete_step(f"✅ Created {len(flow_diagrams.get('flow_diagram_list', []))} flow diagrams")
            else:
                progress_tracker.fail_step("⚠️  Flow diagrams creation failed")

            # Step 7: AI Self-Validation and Iteration
            progress_tracker.start_step("🔍 AI validating content relevance...")
            validated_context = await self._ai_self_validation_step(enhanced_context, context, description, progress_tracker)
            if validated_context:
                enhanced_context = validated_context
                progress_tracker.complete_step("✅ Content validated and improved")
            else:
                progress_tracker.fail_step("⚠️  Content validation failed")

            # Step 8: Template Structure Optimization
            progress_tracker.start_step("🔄 Optimizing template structure...")
            optimized_context = self._optimize_template_structure_step(enhanced_context, context.get('task_type', 'Development'), description, progress_tracker)
            if optimized_context:
                enhanced_context = optimized_context
                progress_tracker.complete_step("✅ Template structure optimized")
            else:
                progress_tracker.fail_step("⚠️  Template optimization failed")

            return enhanced_context

        except Exception as e:
            logger.error(f"Comprehensive AI enhancement failed: {e}")
            progress_tracker.fail_step(f"❌ Enhancement failed: {e}")
            return context

    async def _progressive_step_3_basic_enhancement(self, data: Dict[str, Any]) -> bool:
        """Fallback basic enhancement when AI is not available."""
        try:
            print("🔄 Applying basic enhancement without AI...")

            # Prepare basic context
            context = self.template_manager.prepare_base_context(**data)

            # Apply template optimization only
            task_type = data.get('task_type', 'Development')
            optimized_context = self.template_manager.optimize_template_context(context, task_type, data['description'])

            # Store basic enhancements
            self.creation_state['ai_enhancements'] = optimized_context
            self.creation_state['quality_score'] = 0.6  # Basic quality score

            print("✅ Basic enhancement applied")
            return True

        except Exception as e:
            logger.error(f"Basic enhancement failed: {e}")
            return False

    def _analyze_context_content(self, selected_context: List, title: str, description: str) -> Dict[str, Any]:
        """Analyze context content type and extract relevant information for AI enhancement."""
        try:
            analysis = {
                'formatted_context': "",
                'reference_task_content': None,  # Store full content of best reference task
                'code_patterns': [],
                'template_structure_name': None,
                'best_reference_score': 0.0
            }

            if not selected_context:
                return analysis

            context_summary_for_ai = "\n\nCONTEXT-AWARE ENHANCEMENT INSTRUCTIONS:\n"

            for i, chunk in enumerate(selected_context[:3]): # Limit to top 3 for summary
                file_name = Path(chunk.file_path).name
                file_ext = Path(chunk.file_path).suffix.lower()

                # TASK FILE ANALYSIS (Markdown/Text documents)
                if file_ext == '.md' and ('task-' in file_name.lower() or 'readme' in file_name.lower() or 'doc' in file_name.lower()):
                    context_summary_for_ai += f"\n🎯 REFERENCE DOCUMENT FOUND: {file_name}\n"
                    context_summary_for_ai += "INSTRUCTION: Use this document as HIGH-CONFIDENCE reference while preserving template structure.\n"

                    doc_content = chunk.text

                    # Calculate relevance score for this reference
                    title_lower = title.lower()
                    desc_lower = description.lower()
                    combined_query = f"{title_lower} {desc_lower}"

                    # Score based on content overlap
                    query_terms = combined_query.split()
                    content_matches = sum(1 for term in query_terms if term in doc_content.lower())
                    relevance_score = content_matches / max(len(query_terms), 1)

                    # Boost for position in context list (first is most relevant)
                    position_boost = (3 - i) * 0.1
                    final_score = relevance_score + position_boost

                    # Store if this is the best reference so far
                    if final_score > analysis['best_reference_score']:
                        analysis['reference_task_content'] = doc_content # Store full content
                        analysis['template_structure_name'] = file_name
                        analysis['best_reference_score'] = final_score
                        context_summary_for_ai += f"⭐ BEST REFERENCE (Score: {final_score:.2f})\n"

                # CODE FILE ANALYSIS (Python, JS, etc.)
                elif file_ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs']:
                    context_summary_for_ai += f"\n💻 CODE REFERENCE: {file_name}\n"
                    context_summary_for_ai += "INSTRUCTION: Analyze this code to understand implementation patterns and technical requirements.\n"

                    code_content = chunk.text

                    # Look for classes and functions
                    if 'class ' in code_content:
                        classes = [line.strip() for line in code_content.split('\n') if 'class ' in line]
                        context_summary_for_ai += f"📦 KEY CLASSES: {', '.join(classes[:3])}\n"
                        analysis['code_patterns'].extend(classes[:3])

                    if 'def ' in code_content:
                        functions = [line.strip() for line in code_content.split('\n') if 'def ' in line]
                        context_summary_for_ai += f"⚙️ KEY FUNCTIONS: {', '.join(functions[:5])}\n"
                        analysis['code_patterns'].extend(functions[:5])

                    context_summary_for_ai += f"\n--- Code Context ---\n{code_content[:800]}...\n"

                # DOCUMENTATION ANALYSIS (Other text files)
                else:
                    context_summary_for_ai += f"\n📚 DOCUMENTATION: {file_name}\n"
                    context_summary_for_ai += f"--- Content ---\n{chunk.text[:600]}...\n"

            # Add confidence and intent preservation instructions
            context_summary_for_ai += f"""
🎯 ENHANCEMENT CONFIDENCE LEVEL: HIGH (Reference content found)
- Use reference content to enhance accuracy and detail
- Preserve template structure and format
- Adapt reference examples to user's specific requirements

USER INTENT PRESERVATION:
- Original Title: "{title}"
- Original Description: "{description}"
- MUST preserve user's exact goals and terminology
- MUST NOT change the core purpose or functionality requested by user
"""

            analysis['formatted_context'] = context_summary_for_ai
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing context content: {e}")
            return {
                'formatted_context': "",
                'reference_task_content': None,
                'code_patterns': [],
                'template_structure_name': None
            }

    async def _enhance_description_step(self, context: Dict[str, Any], description: str,
                                      progress_tracker: AIEnhancementProgressTracker, context_analysis: Dict[str, Any]) -> Optional[str]:
        """Enhanced description generation step with user input prioritization and reference adaptation."""
        try:
            title = context.get('title', '')
            task_type = context.get('task_type', 'Development')

            reference_content = context_analysis['reference_task_content']

            # If a high-confidence reference task is found, use it for adaptation
            if reference_content:
                enhancement_prompt = f"""You are enhancing a task description. Your primary goal is to ADAPT the provided reference content to match the user's specific task, while STRICTLY preserving the user's original intent and content.

ORIGINAL USER INPUT:
Title: {title}
Description: {description}
Task Type: {task_type}

HIGH-CONFIDENCE REFERENCE CONTENT (ADAPT THIS):
```markdown
{reference_content}
```

CRITICAL ADAPTATION STRATEGY:
1. Identify the core concepts and technical details in the REFERENCE CONTENT that are relevant to the user's task.
2. REWRITE and ADAPT sections of the REFERENCE CONTENT to fit the user's EXACT title and description.
3. Use the REFERENCE's terminology, structure, and level of detail as a guide.
4. DO NOT simply copy-paste. ADAPT and INTEGRATE.
5. Ensure the output is a cohesive, enhanced description for the user's task.
6. Focus on achieving high content similarity with the adapted reference.

ENHANCEMENT RULES:
- PRESERVE the user's exact intent and requirements.
- ADAPT the reference content to EXPAND on the user's description with specific technical details.
- DO NOT change the core functionality or purpose.
- DO NOT add unrelated features or requirements.
- Maintain the user's terminology and concepts.
- Include implementation details that support the user's vision, derived from the reference.

Enhanced description (ADAPTED from reference, preserving user intent):"""
            else:
                # Fallback to original enhancement prompt if no strong reference
                enhancement_prompt = f"""You are enhancing a task description while STRICTLY preserving the user's original intent and content.

ORIGINAL USER INPUT:
Title: {title}
Description: {description}
Task Type: {task_type}

{context_analysis['formatted_context']}

CRITICAL ENHANCEMENT STRATEGY:
When HIGH-CONFIDENCE reference content is found, you must:
1. Extract specific technical details, class names, function names, and implementation patterns from the reference
2. Adapt these details to match the user's exact title and description
3. Use the reference's terminology and approach while preserving user intent
4. Include specific code references (classes, functions, files) mentioned in the reference
5. Maintain the reference's level of technical detail and specificity

ENHANCEMENT RULES:
1. PRESERVE the user's exact intent and requirements
2. EXPAND on the user's description with specific technical details from the reference content
3. DO NOT change the core functionality or purpose
4. DO NOT add unrelated features or requirements
5. Keep the user's terminology and concepts
6. Add implementation details that support the user's vision
7. Use specific examples and patterns from the reference content
8. Include technical references (classes, functions, files) from the context

Enhanced description (preserve user intent, add specific technical depth from reference):"""

            enhanced_description = await self.ai_enhancement.ai_provider.generate_response(
                enhancement_prompt, max_tokens=800, temperature=0.3
            )

            if enhanced_description and len(enhanced_description.strip()) > len(description):
                progress_tracker.update_progress(f"Enhanced description: {len(enhanced_description)} characters")
                return enhanced_description.strip()

            progress_tracker.update_progress("Using original description (enhancement failed or no significant improvement)")
            return description

        except Exception as e:
            logger.error(f"Description enhancement step failed: {e}")
            return description

    async def _generate_requirements_step(self, context: Dict[str, Any], description: str,
                                        progress_tracker: AIEnhancementProgressTracker, context_analysis: Dict[str, Any]) -> Optional[List[str]]:
        """Requirements generation step with user input prioritization and reference adaptation."""
        try:
            title = context.get('title', '')
            task_type = context.get('task_type', 'Development')

            reference_content = context_analysis['reference_task_content']

            if reference_content:
                requirements_prompt = f"""You are a business analyst creating specific functional requirements for this exact task. Your primary goal is to ADAPT requirements found in the provided reference content to match the user's specific task.

CRITICAL REQUIREMENTS:
- MUST derive requirements from the user's EXACT description and title.
- MUST ADAPT requirements from the REFERENCE CONTENT.
- MUST NOT add generic or unrelated requirements.
- MUST focus on what the user specifically wants to achieve.

TASK DETAILS:
Title: {title}
Description: {description}
Task Type: {task_type}

HIGH-CONFIDENCE REFERENCE CONTENT (ADAPT REQUIREMENTS FROM THIS):
```markdown
{reference_content}
```

REQUIREMENTS GENERATION RULES:
1. Identify and extract functional requirements from the REFERENCE CONTENT.
2. ADAPT these requirements to align perfectly with the user's "{title}" and "{description}".
3. Use the user's terminology and concepts.
4. Make requirements testable and specific.
5. Each requirement should directly support the user's vision.
6. Focus on achieving high content similarity with the adapted reference requirements.

Generate 4-6 specific functional requirements that directly support "{title}" as described by the user.

Format as a JSON array of strings:
["Requirement 1", "Requirement 2", ...]

Requirements:"""
            else:
                # Fallback to original prompt if no strong reference
                requirements_prompt = f"""You are a business analyst creating specific functional requirements for this exact task.

CRITICAL REQUIREMENTS:
- MUST derive requirements from the user's EXACT description and title
- MUST NOT add generic or unrelated requirements
- MUST focus on what the user specifically wants to achieve
- USE the context files to understand detailed implementation requirements

TASK DETAILS:
Title: {title}
Description: {description}
Task Type: {task_type}
{context_analysis['formatted_context']}

REQUIREMENTS GENERATION RULES:
1. Extract specific functionality from the user's description
2. Use the user's terminology and concepts
3. Focus on the user's stated goals and needs
4. Make requirements testable and specific
5. DO NOT add generic software development requirements
6. Each requirement should directly support the user's vision
7. Use relevant details from the context files to create specific requirements
8. If TASK-003 is in the context, use its acceptance criteria as reference

Generate 4-6 specific functional requirements that directly support "{title}" as described by the user.

Format as a JSON array of strings:
["Requirement 1", "Requirement 2", ...]

Requirements:"""

            response = await self.ai_enhancement.ai_provider.generate_response(
                requirements_prompt, max_tokens=600, temperature=0.3
            )

            import json
            import re

            try:
                response_clean = response.strip()
                json_match = re.search(r'\[.*?\]', response_clean, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    requirements = json.loads(json_str)
                    if isinstance(requirements, list) and requirements:
                        progress_tracker.update_progress(f"Generated {len(requirements)} user-focused requirements")
                        return requirements

                requirements = json.loads(response_clean)
                if isinstance(requirements, list) and requirements:
                    progress_tracker.update_progress(f"Generated {len(requirements)} user-focused requirements")
                    return requirements

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse requirements JSON response: {e}")
                logger.debug(f"Raw response: {response[:200]}...")
                progress_tracker.fail_step(f"❌ Requirements generation failed: Invalid JSON response")
                return None

            return None

        except Exception as e:
            logger.error(f"Requirements generation step failed: {e}")
            return None

    async def _generate_implementation_steps_step(self, context: Dict[str, Any], description: str,
                                                progress_tracker: AIEnhancementProgressTracker, context_analysis: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Implementation steps generation step."""
        try:
            # Use existing AI enhancement service
            task_type = context.get('task_type', 'Development')
            enhanced_context = self.context_processor.analyze_task_context_enhanced(
                description, task_type, specific_files=None
            )

            implementation_steps = await self.ai_enhancement.generate_implementation_steps_with_context(
                description, context, enhanced_context, context_analysis['reference_task_content']
            )

            if implementation_steps:
                progress_tracker.update_progress(f"Generated {len(implementation_steps)} implementation phases")
                return implementation_steps
            return None

        except Exception as e:
            logger.error(f"Implementation steps generation step failed: {e}")
            return None

    async def _analyze_risks_step(self, context: Dict[str, Any], description: str,
                                progress_tracker: AIEnhancementProgressTracker) -> Optional[List[Dict[str, Any]]]:
        """Risk analysis step."""
        try:
            # Generate risks using AI enhancement service
            if not await self.ai_enhancement.initialize_provider():
                return None

            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            prompt = f"""You are a senior risk analyst evaluating potential risks for a development task.

TASK DETAILS:
- Title: {title}
- Description: {description}
- Type: {task_type}

RISK ANALYSIS INSTRUCTIONS:
Generate 2-4 potential risks with detailed mitigation strategies.

Each risk must include:
- Risk description
- Impact level (High/Medium/Low)
- Probability (High/Medium/Low)
- Specific mitigation strategy
- Contingency plan

Format as JSON array:
[
  {{
    "risk": "Risk description",
    "impact": "High/Medium/Low",
    "probability": "High/Medium/Low",
    "mitigation": "Specific mitigation strategy",
    "contingency": "Backup plan if mitigation fails"
  }}
]

Generate risks now:"""

            response = await self.ai_enhancement.ai_provider.generate_response(
                prompt, max_tokens=800, temperature=0.6
            )

            # Parse JSON response with better error handling
            import json
            import re

            try:
                # Clean the response to extract JSON
                response_clean = response.strip()

                # Try to extract JSON array from response
                json_match = re.search(r'\[.*?\]', response_clean, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    risks = json.loads(json_str)
                    if isinstance(risks, list) and risks:
                        progress_tracker.update_progress(f"Analyzed {len(risks)} potential risks")
                        return risks

                # Fallback: try parsing the entire response
                risks = json.loads(response_clean)
                if isinstance(risks, list) and risks:
                    progress_tracker.update_progress(f"Analyzed {len(risks)} potential risks")
                    return risks

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse risks JSON response: {e}")
                logger.debug(f"Raw response: {response[:200]}...")

                # NO FALLBACK - Let it fail transparently
                progress_tracker.fail_step(f"❌ Risk analysis failed: Invalid JSON response")
                return None

            return None

        except Exception as e:
            logger.error(f"Risk analysis step failed: {e}")
            return None

    async def _generate_visual_elements_step(self, context: Dict[str, Any], description: str,
                                           progress_tracker: AIEnhancementProgressTracker) -> Optional[Dict[str, Any]]:
        """Visual elements generation step."""
        try:
            visual_elements = {}

            # Generate Mermaid diagrams
            mermaid_diagrams = await self._generate_mermaid_diagrams(context, description)
            if mermaid_diagrams:
                visual_elements.update(mermaid_diagrams)
                progress_tracker.update_progress("Generated Mermaid diagrams")

            # Generate ASCII art
            ascii_art = await self._generate_ascii_art(context, description)
            if ascii_art:
                visual_elements.update(ascii_art)
                progress_tracker.update_progress("Generated ASCII art elements")

            return visual_elements if visual_elements else None

        except Exception as e:
            logger.error(f"Visual elements generation step failed: {e}")
            return None

    async def _create_flow_diagrams_step(self, context: Dict[str, Any], description: str,
                                       progress_tracker: AIEnhancementProgressTracker) -> Optional[Dict[str, Any]]:
        """Flow diagrams creation step."""
        try:
            # Use template manager to generate flow diagrams
            task_type = context.get('task_type', 'Development')
            flow_diagram_context = self.template_manager.generate_task_specific_flow_diagram(
                task_type, description, context
            )

            if flow_diagram_context and flow_diagram_context.get('flow_diagram'):
                # Create flow diagram list for counting
                flow_diagrams = [flow_diagram_context['flow_diagram']]
                flow_diagram_context['flow_diagram_list'] = flow_diagrams
                progress_tracker.update_progress(f"Created {len(flow_diagrams)} flow diagram(s)")
                return flow_diagram_context

            return None

        except Exception as e:
            logger.error(f"Flow diagrams creation step failed: {e}")
            return None

    def _optimize_template_structure_step(self, context: Dict[str, Any], task_type: str, description: str,
                                        progress_tracker: AIEnhancementProgressTracker) -> Optional[Dict[str, Any]]:
        """Template structure optimization step with reference task structure adaptation."""
        try:
            # Check if we have a reference task structure to follow
            selected_context = self.creation_state.get('selected_context', [])
            context_analysis = self._analyze_context_content(selected_context, context.get('title', ''), description)

            # If we have reference content, enhance template with high-confidence details
            if context_analysis.get('reference_task') and context_analysis.get('template_structure'):
                progress_tracker.update_progress(f"Enhancing template with {context_analysis['template_structure']} reference")

                # Add reference confidence marker for template processing
                context['reference_confidence'] = 'HIGH'
                context['reference_source'] = context_analysis['template_structure']

                progress_tracker.update_progress("Applied high-confidence reference enhancement")

            # Use template manager to optimize structure
            optimized_context = self.template_manager.optimize_template_context(context, task_type, description)

            if optimized_context:
                progress_tracker.update_progress("Applied template optimizations")
                return optimized_context

            return None

        except Exception as e:
            logger.error(f"Template optimization step failed: {e}")
            return None

    async def _ai_self_validation_step(self, enhanced_context: Dict[str, Any], original_context: Dict[str, Any],
                                     description: str, progress_tracker) -> Optional[Dict[str, Any]]:
        """AI self-validation step to check and improve content relevance."""
        try:
            if not await self.ai_enhancement.initialize_provider():
                return enhanced_context

            title = original_context.get('title', '')
            task_type = original_context.get('task_type', 'Development')

            # Extract generated content for validation
            implementation_steps = enhanced_context.get('implementation_steps', [])
            requirements = enhanced_context.get('functional_requirements_list', [])
            flow_diagram = enhanced_context.get('flow_diagram', '')

            # Create validation prompt
            validation_prompt = f"""You are a quality assurance expert reviewing AI-generated task content for relevance and accuracy.

ORIGINAL USER INPUT:
Title: {title}
Description: {description}
Task Type: {task_type}

GENERATED CONTENT TO VALIDATE:
Implementation Steps: {implementation_steps}
Requirements: {requirements}
Flow Diagram: {flow_diagram[:200]}...

VALIDATION CRITERIA:
1. Do the implementation steps directly relate to "{title}"?
2. Are the requirements specific to the user's description?
3. Does the flow diagram match the task purpose?
4. Is there any irrelevant content (e.g., search functionality in a kanban task)?

VALIDATION RULES:
- Flag any content that doesn't match the user's intent
- Identify generic or template-like content
- Check for wrong domain content (search in kanban, notifications in AI engine, etc.)
- Suggest specific improvements

Provide validation results as JSON:
{{
  "implementation_steps_relevant": true/false,
  "requirements_relevant": true/false,
  "flow_diagram_relevant": true/false,
  "issues_found": ["issue1", "issue2"],
  "improvement_suggestions": ["suggestion1", "suggestion2"],
  "overall_relevance_score": 0-100
}}

Validation results:"""

            response = await self.ai_enhancement.ai_provider.generate_response(
                validation_prompt, max_tokens=800, temperature=0.2
            )

            # Parse validation results
            import json
            import re

            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*?\}', response, re.DOTALL)
                if json_match:
                    validation_results = json.loads(json_match.group(0))

                    relevance_score = validation_results.get('overall_relevance_score', 0)
                    issues = validation_results.get('issues_found', [])

                    progress_tracker.update_progress(f"Relevance score: {relevance_score}%")

                    # If relevance is low, attempt to improve
                    if relevance_score < 70 or issues:
                        progress_tracker.update_progress("Low relevance detected, attempting improvements...")
                        improved_context = await self._improve_content_relevance(
                            enhanced_context, original_context, description, validation_results
                        )
                        if improved_context:
                            progress_tracker.update_progress("Content improved based on validation")
                            return improved_context

                    return enhanced_context

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse validation results: {e}")
                return enhanced_context

        except Exception as e:
            logger.error(f"AI self-validation failed: {e}")
            return enhanced_context

    async def _improve_content_relevance(self, enhanced_context: Dict[str, Any], original_context: Dict[str, Any],
                                       description: str, validation_results: dict) -> Optional[Dict[str, Any]]:
        """Improve content based on validation feedback."""
        try:
            title = original_context.get('title', '')
            issues = validation_results.get('issues_found', [])
            suggestions = validation_results.get('improvement_suggestions', [])

            # Focus on fixing implementation steps if they're irrelevant
            if not validation_results.get('implementation_steps_relevant', True):
                improvement_prompt = f"""Fix the implementation steps to be specifically relevant to "{title}".

ORIGINAL USER REQUEST:
Title: {title}
Description: {description}

CURRENT ISSUES: {', '.join(issues)}
SUGGESTIONS: {', '.join(suggestions)}

Generate 5-7 implementation steps that are SPECIFICALLY for "{title}" based on the user's description.
Use the user's exact terminology and focus on their stated requirements.

Format as JSON array:
["Step 1: ...", "Step 2: ...", ...]

Improved implementation steps:"""

                response = await self.ai_enhancement.ai_provider.generate_response(
                    improvement_prompt, max_tokens=600, temperature=0.3
                )

                # Parse improved steps
                import json
                import re

                json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                if json_match:
                    try:
                        improved_steps = json.loads(json_match.group(0))
                        if isinstance(improved_steps, list) and improved_steps:
                            enhanced_context['implementation_steps'] = improved_steps
                            logger.info("Implementation steps improved based on validation")
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse improved implementation steps")

            return enhanced_context

        except Exception as e:
            logger.error(f"Content improvement failed: {e}")
            return enhanced_context

    async def _generate_mermaid_diagrams(self, context: Dict[str, Any], description: str) -> Optional[Dict[str, Any]]:
        """Generate task-specific Mermaid diagrams based on context and task type."""
        try:
            if not await self.ai_enhancement.initialize_provider():
                return None

            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            # Get context-aware diagram type and structure
            diagram_context = self._analyze_task_for_diagram_type(title, description, task_type)

            prompt = f"""You are a technical architect creating a SPECIFIC Mermaid diagram for this exact task.

CRITICAL REQUIREMENTS:
- MUST reflect the EXACT task described by the user
- MUST use terminology from the user's title and description
- MUST NOT generate generic or unrelated content

TASK DETAILS:
- Title: {title}
- Description: {description}
- Type: {task_type}
- Diagram Focus: {diagram_context['focus']}

USER'S SPECIFIC REQUIREMENTS:
{diagram_context['analysis']}

Generate a {diagram_context['diagram_type']} Mermaid diagram that SPECIFICALLY shows the workflow for "{title}":

STRICT GUIDELINES:
1. Extract key components/processes from the user's description
2. Use the EXACT terminology from the title and description
3. Show the specific workflow for THIS task only
4. DO NOT use generic examples or unrelated processes
5. Focus on the user's stated requirements and goals

{diagram_context['example']}

Generate the SPECIFIC Mermaid diagram for "{title}" based on the user's description:"""

            response = await self.ai_enhancement.ai_provider.generate_response(
                prompt, max_tokens=800, temperature=0.4
            )

            # Extract Mermaid code
            if '```mermaid' in response:
                start = response.find('```mermaid') + 10
                end = response.find('```', start)
                if end > start:
                    mermaid_code = response[start:end].strip()
                    return {
                        'mermaid_diagram': mermaid_code,
                        'has_mermaid_diagram': True,
                        'diagram_type': diagram_context['diagram_type'],
                        'diagram_focus': diagram_context['focus']
                    }

            return None

        except Exception as e:
            logger.error(f"Mermaid diagram generation failed: {e}")
            return None

    def _analyze_task_for_diagram_type(self, title: str, description: str, task_type: str) -> Dict[str, str]:
        """Analyze task to determine the most appropriate diagram type and structure."""
        title_lower = title.lower()
        desc_lower = description.lower()

        # Integration/API tasks
        if any(keyword in title_lower or keyword in desc_lower for keyword in
               ['integration', 'api', 'graphiti', 'search', 'retrieval', 'context']):
            return {
                'diagram_type': 'flowchart TD',
                'focus': 'Integration Architecture and Data Flow',
                'analysis': 'This appears to be an integration task involving data flow and system interactions.',
                'requirements': '''1. System integration points and data flow
2. API calls and response handling
3. Error handling and fallback mechanisms
4. Performance optimization points
5. Context retrieval and processing steps''',
                'example': '''Example format:
```mermaid
flowchart TD
    A[User Query] --> B[Context Processor]
    B --> C{Graphiti Available?}
    C -->|Yes| D[Graphiti Search]
    C -->|No| E[Fallback Search]
    D --> F[Score Results]
    E --> F
    F --> G[Return Context]
```'''
            }

        # UI/Frontend tasks
        elif any(keyword in title_lower or keyword in desc_lower for keyword in
                ['ui', 'frontend', 'interface', 'component', 'react', 'vue']):
            return {
                'diagram_type': 'flowchart TD',
                'focus': 'User Interface Flow and Component Interaction',
                'analysis': 'This appears to be a UI/frontend task involving user interactions and component flow.',
                'requirements': '''1. User interaction flow
2. Component hierarchy and communication
3. State management and data flow
4. Event handling and validation
5. Error states and user feedback''',
                'example': '''Example format:
```mermaid
flowchart TD
    A[User Input] --> B[Validation]
    B -->|Valid| C[Update State]
    B -->|Invalid| D[Show Error]
    C --> E[Render Component]
    D --> A
```'''
            }

        # Database/Backend tasks
        elif any(keyword in title_lower or keyword in desc_lower for keyword in
                ['database', 'backend', 'server', 'model', 'schema', 'migration']):
            return {
                'diagram_type': 'erDiagram',
                'focus': 'Database Schema and Backend Architecture',
                'analysis': 'This appears to be a backend/database task involving data modeling and server logic.',
                'requirements': '''1. Database schema and relationships
2. API endpoints and data flow
3. Business logic and validation
4. Authentication and authorization
5. Error handling and logging''',
                'example': '''Example format:
```mermaid
erDiagram
    USER ||--o{ TASK : creates
    TASK ||--o{ COMMENT : has
    USER {
        string id
        string name
        string email
    }
```'''
            }

        # Testing tasks
        elif any(keyword in title_lower or keyword in desc_lower for keyword in
                ['test', 'testing', 'validation', 'qa', 'quality']):
            return {
                'diagram_type': 'flowchart TD',
                'focus': 'Testing Strategy and Validation Flow',
                'analysis': 'This appears to be a testing task involving validation and quality assurance.',
                'requirements': '''1. Test execution flow
2. Validation checkpoints
3. Error detection and reporting
4. Test data management
5. Coverage and quality metrics''',
                'example': '''Example format:
```mermaid
flowchart TD
    A[Test Suite] --> B[Unit Tests]
    A --> C[Integration Tests]
    B --> D[Validate Results]
    C --> D
    D --> E[Generate Report]
```'''
            }

        # Default for general development tasks
        else:
            return {
                'diagram_type': 'flowchart TD',
                'focus': 'Development Workflow and Implementation Steps',
                'analysis': 'This appears to be a general development task requiring implementation workflow.',
                'requirements': '''1. Development workflow and implementation steps
2. Key decision points and branching logic
3. Integration with existing systems
4. Error handling and validation
5. Testing and deployment considerations''',
                'example': '''Example format:
```mermaid
flowchart TD
    A[Requirements] --> B[Design]
    B --> C[Implementation]
    C --> D[Testing]
    D --> E[Deployment]
```'''
            }

    async def _generate_ascii_art(self, context: Dict[str, Any], description: str) -> Optional[Dict[str, Any]]:
        """Generate ASCII art elements for the task."""
        try:
            if not await self.ai_enhancement.initialize_provider():
                return None

            task_type = context.get('task_type', 'Development')
            title = context.get('title', 'Task')

            prompt = f"""Create simple ASCII art that represents the concept of this task.

TASK DETAILS:
- Title: {title}
- Description: {description}
- Type: {task_type}

Create a simple, clean ASCII art representation (max 10 lines, 60 characters wide).
Focus on the main concept or workflow of the task.

Generate ASCII art now:"""

            response = await self.ai_enhancement.ai_provider.generate_response(
                prompt, max_tokens=300, temperature=0.7
            )

            if response and len(response.strip()) > 10:
                return {
                    'ascii_art': response.strip(),
                    'has_ascii_art': True
                }

            return None

        except Exception as e:
            logger.error(f"ASCII art generation failed: {e}")
            return None

    def _calculate_enhancement_quality_score(self, enhanced_context: Dict[str, Any]) -> float:
        """Calculate quality score for the enhanced task."""
        try:
            score = 0.0
            max_score = 100.0

            # Base score for having enhanced content
            score += 10.0

            # Description enhancement (20 points)
            if enhanced_context.get('detailed_description'):
                desc_length = len(enhanced_context['detailed_description'])
                if desc_length > 500:
                    score += 20.0
                elif desc_length > 200:
                    score += 15.0
                else:
                    score += 10.0

            # Requirements (20 points)
            requirements = enhanced_context.get('functional_requirements_list', [])
            if requirements:
                req_count = len(requirements)
                if req_count >= 6:
                    score += 20.0
                elif req_count >= 4:
                    score += 15.0
                elif req_count >= 2:
                    score += 10.0
                else:
                    score += 5.0

            # Implementation steps (15 points)
            impl_steps = enhanced_context.get('implementation_steps', [])
            if impl_steps:
                step_count = len(impl_steps)
                if step_count >= 4:
                    score += 15.0
                elif step_count >= 2:
                    score += 10.0
                else:
                    score += 5.0

            # Risk analysis (10 points)
            risks = enhanced_context.get('risks', [])
            if risks:
                risk_count = len(risks)
                if risk_count >= 3:
                    score += 10.0
                elif risk_count >= 2:
                    score += 7.0
                else:
                    score += 5.0

            # Visual elements (15 points)
            visual_score = 0
            if enhanced_context.get('mermaid_diagram'):
                visual_score += 8.0
            if enhanced_context.get('ascii_art'):
                visual_score += 4.0
            if enhanced_context.get('flow_diagram'):
                visual_score += 3.0
            score += min(visual_score, 15.0)

            # Template optimization (10 points)
            if enhanced_context.get('ai_enhancement_applied'):
                score += 10.0

            # Context usage (10 points)
            context_used = enhanced_context.get('ai_context_used', 0)
            if context_used > 0:
                if context_used >= 5:
                    score += 10.0
                elif context_used >= 3:
                    score += 7.0
                else:
                    score += 5.0

            return min(score, max_score)

        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return 60.0  # Default score

    def _display_enhancement_summary(self, enhanced_context: Dict[str, Any], quality_score: float,
                                   progress_tracker: AIEnhancementProgressTracker) -> None:
        """Display comprehensive enhancement summary."""
        try:
            print("\n" + "="*60)
            print("📊 AI Enhancement Complete!")
            print("="*60)

            # Quality score
            print(f"   🎯 Quality Score: {quality_score:.1f}%")

            # Enhanced description
            desc = enhanced_context.get('detailed_description', '')
            if desc:
                print(f"   📝 Enhanced Description: {len(desc)} characters")

            # Requirements
            requirements = enhanced_context.get('functional_requirements_list', [])
            if requirements:
                print(f"   📋 Requirements: {len(requirements)} items")

            # Implementation steps
            impl_steps = enhanced_context.get('implementation_steps', [])
            if impl_steps:
                print(f"   🔧 Implementation Steps: {len(impl_steps)} phases")

            # Risks
            risks = enhanced_context.get('risks', [])
            if risks:
                print(f"   🚨 Risks: {len(risks)} identified")

            # Visual elements
            visual_elements = []
            if enhanced_context.get('mermaid_diagram'):
                visual_elements.append("Mermaid diagrams")
            if enhanced_context.get('ascii_art'):
                visual_elements.append("ASCII art")
            if visual_elements:
                print(f"   🎨 Visual Elements: {', '.join(visual_elements)}")
            else:
                print("   🎨 Visual Elements: None generated")

            # Flow diagrams
            flow_diagrams = enhanced_context.get('flow_diagram_list', [])
            if flow_diagrams:
                print(f"   📊 Flow Diagrams: {len(flow_diagrams)} created")
            else:
                print("   📊 Flow Diagrams: None created")

            # Context usage
            context_used = enhanced_context.get('ai_context_used', 0)
            if context_used > 0:
                print(f"   🔍 Context Files Used: {context_used}")

            # Enhancement metadata
            if enhanced_context.get('graphiti_used'):
                print("   🧠 Enhanced Context: Graphiti integration used")
            elif enhanced_context.get('modular_enhanced'):
                print("   🧠 Enhanced Context: Modular enhancement applied")

            print("="*60)

        except Exception as e:
            logger.error(f"Enhancement summary display failed: {e}")

    async def _progressive_step_4_final_creation(self) -> Tuple[bool, str, str]:
        """Step 4: Final review and task creation."""
        try:
            print("\n📄 Step 4/4: Final Review & Creation")
            print("=" * 40)

            data = self.creation_state['collected_data']
            enhancements = self.creation_state['ai_enhancements']

            # Create the task using enhanced data
            success, task_id, file_path = await self.create_enhanced_task(
                title=data['title'],
                description=data['description'],
                task_type=data['task_type'],
                priority=data['priority'],
                assigned_to=data['assigned_to'],
                tags=data['tags'],
                use_ai_enhancement=False,  # Already enhanced
                ai_enhancements=enhancements
            )

            if success:
                print(f"✅ Task {task_id} created successfully!")
                print(f"📁 File: {file_path}")
            else:
                print(f"❌ Task creation failed: {file_path}")

            return success, task_id, file_path

        except Exception as e:
            logger.error(f"Step 4 failed: {e}")
            return False, "", str(e)

    def _display_enhanced_context_selection(self, context_chunks: List[ContextChunk]) -> None:
        """Display enhanced context selection interface with previews and metadata."""
        print("\n" + "="*80)
        print("📁 ENHANCED CONTEXT SELECTION")
        print("="*80)

        for i, chunk in enumerate(context_chunks, 1):
            # File metadata
            file_path = Path(chunk.file_path)
            file_size = self._get_file_size(file_path)
            last_modified = self._get_last_modified(file_path)
            file_type_icon = self._get_file_type_icon(file_path)

            # Relevance explanation
            explanation = self._generate_relevance_explanation(chunk)

            # File preview (first 3-5 lines)
            preview = self._generate_file_preview(chunk)

            print(f"\n{i}. {file_type_icon} {chunk.file_path}")
            print(f"   📊 Relevance: {chunk.relevance_score:.3f} | 📏 {file_size} | 🕒 {last_modified}")
            print(f"   💡 Why selected: {explanation}")
            print(f"   👀 Preview:")
            for line in preview:
                print(f"      {line}")
            print("   " + "-"*60)

        print(f"\n📋 Commands:")
        print(f"   • Numbers (1,2,3): Select specific files")
        print(f"   • 'all': Select all files")
        print(f"   • 'none': Skip context")
        print(f"   • 'auto' or 'smart': Intelligent auto-selection")
        print(f"   • 'preview X': Show full content of file X")

    def _smart_auto_select_context(self, context_chunks: List[ContextChunk]) -> List[ContextChunk]:
        """Intelligently auto-select the most relevant context files."""
        if not context_chunks:
            return []

        # Calculate confidence thresholds
        scores = [chunk.relevance_score for chunk in context_chunks]
        avg_score = sum(scores) / len(scores)
        high_confidence_threshold = avg_score + (max(scores) - avg_score) * 0.5

        # Auto-select high-confidence files
        auto_selected = []
        for chunk in context_chunks:
            if chunk.relevance_score >= high_confidence_threshold:
                auto_selected.append(chunk)

            # Limit to top 5 files
            if len(auto_selected) >= 5:
                break

        # Ensure at least 3 files if available
        if len(auto_selected) < 3 and len(context_chunks) >= 3:
            auto_selected = context_chunks[:3]

        return auto_selected

    def _get_file_size(self, file_path: Path) -> str:
        """Get human-readable file size."""
        try:
            size_bytes = file_path.stat().st_size
            if size_bytes < 1024:
                return f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f}KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f}MB"
        except:
            return "Unknown"

    def _get_last_modified(self, file_path: Path) -> str:
        """Get human-readable last modified time."""
        try:
            import datetime
            mtime = file_path.stat().st_mtime
            dt = datetime.datetime.fromtimestamp(mtime)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return "Unknown"

    def _get_file_type_icon(self, file_path: Path) -> str:
        """Get file type icon based on extension."""
        FILE_TYPE_ICONS = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.md': '📝',
            '.json': '📋',
            '.yaml': '⚙️',
            '.yml': '⚙️',
            '.txt': '📄',
            '.html': '🌐',
            '.css': '🎨',
            '.bat': '⚡',
            '.ps1': '💻',
            '.sh': '🔧',
            'default': '📁'
        }

        ext = file_path.suffix.lower()
        return FILE_TYPE_ICONS.get(ext, FILE_TYPE_ICONS['default'])

    def _generate_relevance_explanation(self, chunk: ContextChunk) -> str:
        """Generate human-readable explanation for why a file was selected."""
        explanations = []

        # File type relevance
        file_path = Path(chunk.file_path)
        if file_path.suffix.lower() in ['.py', '.js', '.ts']:
            explanations.append("contains implementation code")
        elif file_path.suffix.lower() == '.md':
            explanations.append("contains documentation/task information")
        elif file_path.suffix.lower() in ['.json', '.yaml', '.yml']:
            explanations.append("contains configuration data")

        # Content-based relevance
        content_lower = chunk.text.lower()
        if 'class' in content_lower and 'def' in content_lower:
            explanations.append("defines classes and methods")
        elif 'import' in content_lower:
            explanations.append("contains relevant imports")
        elif 'config' in content_lower or 'setting' in content_lower:
            explanations.append("contains configuration")

        # Score-based explanation
        if chunk.relevance_score > 0.8:
            explanations.append("high semantic similarity")
        elif chunk.relevance_score > 0.6:
            explanations.append("moderate semantic similarity")
        elif chunk.relevance_score > 0.4:
            explanations.append("some semantic similarity")

        return "; ".join(explanations) if explanations else "general relevance to query"

    def _generate_file_preview(self, chunk: ContextChunk, max_lines: int = 3) -> List[str]:
        """Generate file preview with first few meaningful lines."""
        try:
            lines = chunk.text.split('\n')
            preview_lines = []

            for line in lines:
                cleaned_line = line.strip()
                # Skip empty lines and common non-meaningful lines
                if cleaned_line and not cleaned_line.startswith('#') and len(cleaned_line) > 5:
                    if len(cleaned_line) > 80:
                        cleaned_line = cleaned_line[:77] + "..."
                    preview_lines.append(cleaned_line)

                    if len(preview_lines) >= max_lines:
                        break

            return preview_lines if preview_lines else ["[No meaningful content preview available]"]
        except Exception:
            return ["[Preview error]"]

    def _show_file_preview(self, chunk: ContextChunk) -> None:
        """Show full file content preview."""
        print("\n" + "="*80)
        print(f"📄 FULL FILE PREVIEW: {chunk.file_path}")
        print("="*80)

        try:
            # Show file metadata
            file_path = Path(chunk.file_path)
            file_size = self._get_file_size(file_path)
            last_modified = self._get_last_modified(file_path)

            print(f"📊 Size: {file_size} | 🕒 Modified: {last_modified}")
            print(f"📈 Relevance Score: {chunk.relevance_score:.3f}")
            print(f"💡 Explanation: {self._generate_relevance_explanation(chunk)}")
            print("-" * 80)

            # Show content with line numbers
            lines = chunk.text.split('\n')
            for i, line in enumerate(lines[:50], 1):  # Limit to first 50 lines
                print(f"{i:3d}: {line}")

            if len(lines) > 50:
                print(f"\n... ({len(lines) - 50} more lines)")

        except Exception as e:
            print(f"❌ Error showing preview: {e}")

        print("="*80)
        input("Press Enter to continue...")
