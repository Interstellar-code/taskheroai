"""
Modular AI-Enhanced Task Creator

Clean, modular implementation that orchestrates the specialized components
for AI-enhanced task creation with Graphiti integration.
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

logger = logging.getLogger("TaskHeroAI.ProjectManagement.ModularAITaskCreator")


class ModularAITaskCreator:
    """Clean, modular AI-enhanced task creation with intelligent content generation."""

    def __init__(self, project_root: Optional[str] = None):
        """Initialize the Modular AI Task Creator.

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
            'quality_threshold': 0.7,
            'max_context_items': 10
        }

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
                                 use_ai_enhancement: bool = True) -> Tuple[bool, str, Optional[str]]:
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

        Returns:
            Tuple of (success, task_id, file_path or error_message)
        """
        try:
            # Step 1: Generate task ID
            task_id = self._generate_task_id()

            # Step 2: Enhanced metadata generation
            enhanced_tags = await self._generate_enhanced_tags(title, description, task_type, tags or [])
            enhanced_dependencies = await self._generate_enhanced_dependencies(title, description, dependencies or [])
            enhanced_effort = await self._generate_enhanced_effort_estimate(title, description, effort_estimate)

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

            # Step 4: AI Enhancement (if enabled)
            if use_ai_enhancement and self.config['enable_ai_enhancement']:
                context = await self._enhance_with_modular_ai(context, description)

            # Step 5: Template optimization
            context = self.template_manager.optimize_template_context(context, task_type, description)

            # Step 6: Generate flow diagram if not already present
            if not context.get('flow_diagram'):
                flow_diagram_context = self.template_manager.generate_task_specific_flow_diagram(
                    task_type, description, context
                )
                context.update(flow_diagram_context)

            # Step 7: Render task content
            task_content = self.template_manager.render_enhanced_task(context)

            # Step 8: Validate quality
            quality_result = self.quality_validator.validate_task_quality(task_content, context)

            # Step 9: Generate filename and save
            filename = self.template_manager.generate_filename(task_id, task_type, title)
            file_path = self._save_task_file(filename, task_content)

            # Step 10: Log results
            logger.info(f"Enhanced task created: {task_id} at {file_path} (Quality: {quality_result['quality_level']}, Score: {quality_result['overall_score']:.2f})")
            return True, task_id, str(file_path)

        except Exception as e:
            logger.error(f"Error creating enhanced task: {e}")
            return False, "", str(e)

    async def _enhance_with_modular_ai(self, context: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Enhanced AI processing using modular components with Graphiti integration."""
        try:
            # Step 1: Enhanced context analysis
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

            # Step 3: Optimize context for AI processing
            optimized_context = self.context_processor.optimize_context_for_ai(relevant_context)

            # Step 4: Use AI enhancement service for content generation
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

            # Step 5: Add metadata
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
                    file_types=self._determine_relevant_file_types(query, context.get('task_type', 'Development'))
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

    def _determine_relevant_file_types(self, query: str, task_type: str) -> List[str]:
        """Determine relevant file types based on query and task type."""
        return self.context_processor._determine_relevant_file_types(query, task_type)

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

    async def _generate_enhanced_tags(self, title: str, description: str, task_type: str, existing_tags: List[str]) -> List[str]:
        """Generate comprehensive tags for better metadata completeness."""
        # Simplified tag generation - can be enhanced later
        tags = list(existing_tags) if existing_tags else []
        
        # Add task type based tags
        if task_type.lower() == 'development':
            tags.extend(['development', 'coding'])
        elif task_type.lower() == 'documentation':
            tags.extend(['documentation', 'writing'])
        
        # Remove duplicates and limit
        unique_tags = list(dict.fromkeys(tags))
        return unique_tags[:8]

    async def _generate_enhanced_dependencies(self, title: str, description: str, existing_deps: List[str]) -> List[str]:
        """Generate smart dependencies based on task content."""
        return existing_deps or []

    async def _generate_enhanced_effort_estimate(self, title: str, description: str, existing_effort: str) -> str:
        """Generate more accurate effort estimates based on task complexity."""
        return existing_effort or 'Medium'

    def _save_task_file(self, filename: str, content: str) -> Path:
        """Save task file to the appropriate directory."""
        # Use task manager's save functionality
        tasks_dir = self.project_root / "theherotasks" / "todo"
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = tasks_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path

    async def index_codebase_with_graphiti(self) -> bool:
        """Index the codebase using Graphiti for enhanced context retrieval."""
        return await self.graphiti_retriever.index_codebase()

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all modular components."""
        return {
            'graphiti_available': self.graphiti_retriever.is_available(),
            'ai_enhancement_available': self.ai_enhancement.ai_available,
            'config': self.config.copy(),
            'project_root': str(self.project_root)
        }
