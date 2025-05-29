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

        # Configuration
        self.config = {
            'use_graphiti': True,
            'fallback_to_semantic': True,
            'enable_ai_enhancement': True,
            'enable_progressive_creation': True,
            'quality_threshold': 0.7,
            'max_context_items': 10
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
                # Step 5: AI Enhancement using modular components
                context = await self._enhance_with_modular_ai(context, description)

            # Step 6: Template optimization using template manager
            ai_flow_diagram = context.get('flow_diagram')
            context = self.template_manager.optimize_template_context(context, task_type, description)

            # Step 7: Generate flow diagram if not already present
            if not ai_flow_diagram:
                flow_diagram_context = self.template_manager.generate_task_specific_flow_diagram(
                    task_type, description, context
                )
                context.update(flow_diagram_context)

            # Step 8: Render task content using template manager
            task_content = self.template_manager.render_enhanced_task(context)

            # Step 9: Validate quality
            quality_result = self.quality_validator.validate_task_quality(task_content, context)

            # Step 10: Generate filename and save
            filename = self.template_manager.generate_filename(task_id, task_type, title)
            file_path = self._save_task_file(filename, task_content)

            # Step 11: Log results
            logger.info(f"Enhanced task created: {task_id} at {file_path} (Quality: {quality_result['quality_level']}, Score: {quality_result['overall_score']:.2f})")
            return True, task_id, str(file_path)

        except Exception as e:
            logger.error(f"Error creating enhanced task: {e}")
            return False, "", str(e)

    def _apply_ai_enhancements(self, context: Dict[str, Any], ai_enhancements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply pre-generated AI enhancements to context (Phase 4C compatibility)."""
        if ai_enhancements.get('description'):
            context['description'] = ai_enhancements['description']
        if ai_enhancements.get('requirements'):
            context['functional_requirements'] = ai_enhancements['requirements']
        if ai_enhancements.get('implementation_steps'):
            context['implementation_steps'] = ai_enhancements['implementation_steps']
        if ai_enhancements.get('risks'):
            context['risks'] = ai_enhancements['risks']

        # Handle visual elements and flow diagrams
        if ai_enhancements.get('visual_elements'):
            visual_elements = ai_enhancements['visual_elements']
            if visual_elements.get('mermaid_diagram'):
                mermaid_diagram = visual_elements['mermaid_diagram']
                context['flow_diagram'] = f"```mermaid\n{mermaid_diagram.get('content', '')}\n```"
                context['flow_description'] = mermaid_diagram.get('description', 'Task flow diagram')

        if ai_enhancements.get('flow_diagrams'):
            flow_diagrams = ai_enhancements['flow_diagrams']
            if flow_diagrams:
                main_diagram = flow_diagrams[0]
                if main_diagram.get('content'):
                    content = main_diagram['content']
                    if not content.startswith('```mermaid'):
                        content = f"```mermaid\n{content}\n```"
                    context['flow_diagram'] = content
                    context['flow_description'] = main_diagram.get('title', 'Task flow diagram')

        # Add Phase 4C metadata
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

            # Display context options
            print(f"\n📁 Found {len(context_chunks)} relevant files:")
            for i, chunk in enumerate(context_chunks[:5]):  # Show top 5
                file_name = chunk.file_path.name if hasattr(chunk.file_path, 'name') else str(chunk.file_path)
                print(f"  {i+1}. {file_name} (relevance: {chunk.relevance_score:.2f})")

            # User selection
            selection = input("\nSelect context (1,2,3 or 'all' or 'none'): ").strip().lower()

            if selection == 'none':
                self.creation_state['selected_context'] = []
            elif selection == 'all':
                self.creation_state['selected_context'] = context_chunks[:5]
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
        """Step 3: AI enhancement and preview."""
        try:
            print("\n🧠 Step 3/4: AI Enhancement & Preview")
            print("=" * 40)

            data = self.creation_state['collected_data']

            # Prepare context for AI enhancement
            context = self.template_manager.prepare_base_context(**data)

            # Apply AI enhancement
            print("🤖 Applying AI enhancement...")
            enhanced_context = await self._enhance_with_modular_ai(context, data['description'])

            # Store enhancements
            self.creation_state['ai_enhancements'] = enhanced_context

            # Show preview
            print("\n📋 Enhanced Task Preview:")
            print(f"Title: {enhanced_context.get('title', 'N/A')}")
            print(f"Type: {enhanced_context.get('task_type', 'N/A')}")

            if enhanced_context.get('detailed_description'):
                print(f"Enhanced Description: {enhanced_context['detailed_description'][:200]}...")

            if enhanced_context.get('functional_requirements_list'):
                print(f"Requirements: {len(enhanced_context['functional_requirements_list'])} generated")

            # User confirmation
            proceed = input("\nProceed with this enhancement? (Y/n): ").strip().lower()
            if proceed in ['n', 'no']:
                return False

            print("✅ AI enhancement applied")
            return True

        except Exception as e:
            logger.error(f"Step 3 failed: {e}")
            return False

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
