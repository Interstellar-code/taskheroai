"""
AI-Enhanced Task Creator Module

Integrates the enhanced task template with AI capabilities to provide intelligent,
comprehensive task creation with context-aware content generation.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio

from .template_engine import TemplateEngine
from .task_manager import TaskManager, TaskPriority, TaskStatus
from ..ai.ai_manager import AIManager

logger = logging.getLogger("TaskHeroAI.ProjectManagement.AITaskCreator")


class AITaskCreator:
    """AI-enhanced task creation with intelligent content generation."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the AI Task Creator.
        
        Args:
            project_root: Root directory for project management
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.template_engine = TemplateEngine(project_root)
        self.task_manager = TaskManager(project_root)
        self.ai_manager = None  # Will be initialized when needed
        
        # Enhanced task template path
        self.enhanced_template = "tasks/enhanced_task.j2"
        
        # Task type mappings for filename generation
        self.task_type_mappings = {
            "Development": "DEV",
            "Bug Fix": "BUG", 
            "Test Case": "TEST",
            "Documentation": "DOC",
            "Design": "DES",
            "Research": "RES",
            "Planning": "PLAN"
        }
        
    def _initialize_ai_manager(self) -> bool:
        """Initialize AI manager if available."""
        try:
            if self.ai_manager is None:
                self.ai_manager = AIManager()
                # Check if AI dependencies are available
                if hasattr(self.ai_manager, 'is_ready') and not self.ai_manager.is_ready():
                    logger.warning("AI Manager not ready - AI features will be limited")
                    return False
            return True
        except Exception as e:
            logger.warning(f"AI Manager initialization failed: {e}")
            return False
    
    def create_enhanced_task(self, 
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
        """
        Create an enhanced task using the enhanced_task.j2 template with AI assistance.
        
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
            # Generate task ID
            task_id = self._generate_task_id()
            
            # Prepare basic context
            context = self._prepare_base_context(
                task_id=task_id,
                title=title,
                description=description,
                task_type=task_type,
                priority=priority,
                assigned_to=assigned_to,
                due_date=due_date,
                tags=tags or [],
                dependencies=dependencies or [],
                effort_estimate=effort_estimate
            )
            
            # Enhance with AI if requested and available
            if use_ai_enhancement:
                context = self._enhance_with_ai(context, description)
            
            # Generate task content using enhanced template
            task_content = self.template_engine.render_template(
                self.enhanced_template, 
                context
            )
            
            # Generate filename following naming convention
            filename = self._generate_filename(task_id, task_type, title)
            
            # Save the task file
            file_path = self._save_task_file(filename, task_content)
            
            logger.info(f"Enhanced task created: {task_id} at {file_path}")
            return True, task_id, str(file_path)
            
        except Exception as e:
            logger.error(f"Error creating enhanced task: {e}")
            return False, "", str(e)
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        # Get existing task IDs to find the next number
        existing_tasks = self.task_manager.get_all_tasks()
        max_id = 0
        
        for status_tasks in existing_tasks.values():
            for task in status_tasks:
                # Extract number from task ID (e.g., TASK-015 -> 15)
                if task.task_id.startswith("TASK-"):
                    try:
                        task_num = int(task.task_id.split("-")[1])
                        max_id = max(max_id, task_num)
                    except (IndexError, ValueError):
                        continue
        
        return f"TASK-{max_id + 1:03d}"
    
    def _prepare_base_context(self, **kwargs) -> Dict[str, Any]:
        """Prepare the base context for template rendering."""
        # Convert tags and dependencies to proper format
        tags = kwargs.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        dependencies = kwargs.get('dependencies', [])
        if isinstance(dependencies, str):
            dependencies = [dep.strip() for dep in dependencies.split(',') if dep.strip()]
        
        # Calculate due date if not provided
        due_date = kwargs.get('due_date')
        if not due_date:
            # Default to 1 week from now for medium effort, adjust based on effort
            effort = kwargs.get('effort_estimate', 'Medium').lower()
            days_map = {'small': 3, 'medium': 7, 'large': 14}
            days = days_map.get(effort, 7)
            due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get task type abbreviation
        task_type = kwargs.get('task_type', 'Development')
        task_prefix = self.task_type_mappings.get(task_type, 'DEV')
        
        return {
            'task_id': kwargs.get('task_id'),
            'title': kwargs.get('title'),
            'description': kwargs.get('description', ''),
            'brief_description': kwargs.get('description', '')[:200] + '...' if len(kwargs.get('description', '')) > 200 else kwargs.get('description', ''),
            'priority': kwargs.get('priority', 'medium').title(),
            'status': 'Todo',
            'assignee': kwargs.get('assigned_to', 'Developer'),
            'task_type': task_type,
            'task_prefix': task_prefix,
            'due_date': due_date,
            'created': datetime.now().strftime('%Y-%m-%d'),
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'tags': tags,
            'dependencies': dependencies,
            'estimated_effort': kwargs.get('effort_estimate', 'Medium'),
            'sequence': int(kwargs.get('task_id', 'TASK-001').split('-')[1]) if kwargs.get('task_id') else 1,
            'related_epic': kwargs.get('related_epic', 'TaskHero AI Project'),
            
            # Enhanced template specific fields
            'show_naming_convention': True,
            'show_metadata_legend': True,
            'show_implementation_analysis': True,
            
            # Default implementation steps
            'implementation_steps': [
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
            ],
            
            # Default success criteria
            'success_criteria': [
                {'description': 'All functional requirements are implemented', 'completed': False},
                {'description': 'Code passes all tests and quality checks', 'completed': False},
                {'description': 'Documentation is complete and accurate', 'completed': False}
            ],
            
            # Flow diagram steps
            'flow_steps': [
                {'title': 'User initiates action'},
                {'title': 'System validates input'},
                {'title': 'Process request'},
                {'title': 'Return result'}
            ],
            
            # Default technical considerations
            'technical_considerations': 'Consider performance, security, maintainability, and scalability requirements.',
            'state_management': 'Define how application state will be managed and synchronized.',
            'component_architecture': 'Plan component structure for reusability and maintainability.',
            'performance_requirements': 'Identify performance benchmarks and optimization strategies.',
            
            # Default risk assessment
            'risks': [
                {
                    'description': 'Technical complexity higher than estimated',
                    'impact': 'Medium',
                    'probability': 'Low',
                    'mitigation': 'Break down into smaller tasks, seek technical review'
                },
                {
                    'description': 'Dependencies not available on time',
                    'impact': 'High',
                    'probability': 'Medium',
                    'mitigation': 'Identify alternative approaches, communicate early with dependencies'
                }
            ],
            
            # Additional template variables
            'functional_requirements': f'Implement {kwargs.get("title", "functionality").lower()} according to specifications',
            'functional_requirements_list': None,
            'benefits_list': None,
            'flow_description': f'User workflow for {kwargs.get("title", "task")} implementation',
            'detailed_description': kwargs.get('description', ''),
            'purpose_benefits': f'This task enhances the TaskHero AI system by implementing {kwargs.get("title", "functionality").lower()}.',
            
            # UI Design variables
            'ui_design_overview': 'UI design considerations will be defined during implementation phase.',
            'ui_layout': None,
            'ui_colors': 'Follow TaskHero AI design system color palette',
            'ui_typography': 'Use system default typography standards',
            'ui_spacing': 'Follow 8px grid system for consistent spacing',
            'ui_components': 'Utilize existing component library where applicable',
            'ui_icons': 'Use consistent icon set from design system',
            'design_references': None,
            
            # Technical considerations variables
            'data_persistence': 'Data persistence requirements will be defined based on functionality needs',
            'state_sync': 'State synchronization will follow established patterns',
            'reusability': 'Components will be designed for maximum reusability',
            'integration_patterns': 'Integration will follow existing architectural patterns',
            'memory_management': 'Memory usage will be optimized for performance',
            'loading_optimizations': 'Loading performance will be optimized where applicable',
            'browser_compatibility': 'Cross-browser compatibility will be ensured',
            'backward_compatibility_notes': 'Backward compatibility will be maintained where possible',
            'integration_compatibility': 'Integration compatibility with existing systems will be verified',
            
            # Implementation analysis variables
            'current_implementation': 'Current implementation will be analyzed during planning phase',
            'current_components': 'Existing components will be mapped and evaluated',
            'current_limitations': 'Current limitations will be identified and addressed',
            'new_features': 'New features will be implemented according to requirements',
            'new_features_2': 'Additional enhancements will be considered',
            'new_features_3': 'Future extensibility will be planned',
            'migration_approach': 'Migration strategy will be developed if needed',
            'backward_compatibility': 'Backward compatibility strategy will be defined',
            'risk_mitigation': 'Risk mitigation strategies will be implemented',
            'component_mapping': None,
            
            # Database and schema variables
            'database_changes': None,
            'database_schema': None,
            
            # Time and reference variables
            'estimated_hours': None,
            'actual_hours': None,
            'references': None,
            'updates': None,
            'dependent_tasks': None,
            'technical_dependencies': None,
            'dependency_type': 'Related tasks and technical dependencies will be identified during planning phase.',
            'testing_overview': 'Testing strategy will be developed based on implementation requirements.',
            'testing_strategy': None,
            'test_cases': None
        }
    
    def _enhance_with_ai(self, context: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Enhance the context using AI capabilities."""
        try:
            if not self._initialize_ai_manager():
                logger.info("AI enhancement not available, using default context")
                return context
            
            # AI enhancement logic would go here
            # For now, we'll enhance the description and add intelligent suggestions
            enhanced_context = context.copy()
            
            # Step 1: Collect relevant context from embeddings
            relevant_context = self._collect_embeddings_context(description, context)
            
            # Step 2: Enhance the description with context
            if description:
                enhanced_context['detailed_description'] = self._ai_enhance_description(description, context, relevant_context)
                enhanced_context['functional_requirements'] = self._ai_generate_requirements(description, context, relevant_context)
                enhanced_context['purpose_benefits'] = self._ai_generate_benefits(description, context, relevant_context)
            
            # Step 3: Add AI-generated implementation analysis with context
            enhanced_context.update(self._ai_generate_implementation_analysis(description, context, relevant_context))
            
            # Step 4: Add context metadata
            enhanced_context['ai_context_used'] = len(relevant_context)
            enhanced_context['ai_enhancement_applied'] = True
            
            return enhanced_context
            
        except Exception as e:
            logger.warning(f"AI enhancement failed, using default context: {e}")
            return context
    
    def _collect_embeddings_context(self, description: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect relevant context from existing embeddings."""
        try:
            embeddings_dir = self.project_root / ".index" / "embeddings"
            if not embeddings_dir.exists():
                logger.info("No embeddings directory found")
                return []
            
            # Get task type for targeted search
            task_type = context.get('task_type', 'Development').lower()
            
            # Search terms based on description and task type
            search_terms = self._extract_search_terms(description, task_type)
            
            relevant_files = []
            embedding_files = list(embeddings_dir.glob("*.json"))
            
            logger.info(f"Searching {len(embedding_files)} embedding files for context")
            
            for embedding_file in embedding_files:
                try:
                    with open(embedding_file, 'r', encoding='utf-8') as f:
                        embedding_data = json.load(f)
                    
                    # Calculate relevance score
                    relevance_score = self._calculate_relevance(embedding_data, search_terms, task_type)
                    
                    if relevance_score > 0.3:  # Threshold for relevance
                        file_context = {
                            'file_path': embedding_data.get('path', str(embedding_file)),
                            'file_name': embedding_file.stem,
                            'relevance_score': relevance_score,
                            'content_preview': self._extract_content_preview(embedding_data),
                            'file_type': self._determine_file_type(embedding_file.stem),
                            'chunks_count': len(embedding_data.get('chunks', []))
                        }
                        relevant_files.append(file_context)
                        
                except Exception as e:
                    logger.warning(f"Error processing embedding file {embedding_file}: {e}")
                    continue
            
            # Sort by relevance and return top results
            relevant_files.sort(key=lambda x: x['relevance_score'], reverse=True)
            top_results = relevant_files[:5]  # Top 5 most relevant
            
            logger.info(f"Found {len(top_results)} relevant context files")
            return top_results
            
        except Exception as e:
            logger.error(f"Error collecting embeddings context: {e}")
            return []
    
    def _extract_search_terms(self, description: str, task_type: str) -> List[str]:
        """Extract search terms from description and task type."""
        # Basic keyword extraction (could be enhanced with NLP)
        import re
        
        # Clean and tokenize description
        words = re.findall(r'\b\w+\b', description.lower())
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract meaningful terms
        meaningful_words = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Add task type specific terms
        task_terms = {
            'development': ['implement', 'create', 'build', 'develop', 'code', 'function', 'class', 'method'],
            'bug': ['fix', 'error', 'bug', 'issue', 'problem', 'debug', 'resolve'],
            'test': ['test', 'testing', 'unit', 'integration', 'coverage', 'assert', 'verify'],
            'documentation': ['document', 'docs', 'readme', 'guide', 'manual', 'api', 'reference'],
            'design': ['design', 'ui', 'ux', 'interface', 'layout', 'component', 'style'],
            'research': ['research', 'analyze', 'investigate', 'study', 'explore', 'evaluate']
        }
        
        if task_type in task_terms:
            meaningful_words.extend(task_terms[task_type])
        
        # Return unique terms, prioritizing longer ones
        unique_terms = list(set(meaningful_words))
        unique_terms.sort(key=len, reverse=True)
        
        return unique_terms[:10]  # Top 10 search terms
    
    def _calculate_relevance(self, embedding_data: Dict[str, Any], search_terms: List[str], task_type: str) -> float:
        """Calculate relevance score for an embedding file."""
        try:
            score = 0.0
            
            # Get file path and content
            file_path = embedding_data.get('path', '').lower()
            chunks = embedding_data.get('chunks', [])
            
            # File path relevance
            for term in search_terms:
                if term in file_path:
                    score += 0.2
            
            # Task type relevance
            if task_type in file_path:
                score += 0.3
            
            # Content relevance
            content_text = ""
            for chunk in chunks:
                if isinstance(chunk, dict):
                    content_text += chunk.get('text', '') + " "
                elif isinstance(chunk, str):
                    content_text += chunk + " "
            
            content_text = content_text.lower()
            
            # Search term matches in content
            for term in search_terms:
                if term in content_text:
                    score += 0.1
            
            # Bonus for task-related files
            if any(keyword in file_path for keyword in ['task', 'project', 'management', 'planning']):
                score += 0.2
            
            # Bonus for code files if development task
            if task_type == 'development' and any(ext in file_path for ext in ['.py', '.js', '.ts', '.java', '.cpp']):
                score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.warning(f"Error calculating relevance: {e}")
            return 0.0
    
    def _extract_content_preview(self, embedding_data: Dict[str, Any]) -> str:
        """Extract a preview of the content from embedding data."""
        try:
            chunks = embedding_data.get('chunks', [])
            if not chunks:
                return "No content preview available"
            
            # Get first chunk text
            first_chunk = chunks[0]
            if isinstance(first_chunk, dict):
                text = first_chunk.get('text', '')
            elif isinstance(first_chunk, str):
                text = first_chunk
            else:
                text = str(first_chunk)
            
            # Return first 200 characters
            return text[:200] + "..." if len(text) > 200 else text
            
        except Exception as e:
            logger.warning(f"Error extracting content preview: {e}")
            return "Content preview unavailable"
    
    def _determine_file_type(self, filename: str) -> str:
        """Determine file type from filename."""
        filename = filename.lower()
        
        if any(ext in filename for ext in ['.py', '.pyx']):
            return 'python'
        elif any(ext in filename for ext in ['.js', '.jsx', '.ts', '.tsx']):
            return 'javascript'
        elif any(ext in filename for ext in ['.md', '.markdown']):
            return 'markdown'
        elif any(ext in filename for ext in ['.json', '.yaml', '.yml']):
            return 'config'
        elif any(ext in filename for ext in ['.html', '.css', '.scss']):
            return 'web'
        elif 'task' in filename:
            return 'task'
        elif 'test' in filename:
            return 'test'
        elif 'doc' in filename:
            return 'documentation'
        else:
            return 'other'
    
    def _ai_enhance_description(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> str:
        """Use AI to enhance the task description."""
        # This would integrate with the actual AI system
        # For now, provide a structured enhancement
        task_type = context.get('task_type', 'Development')
        
        enhanced = f"""
## Task Overview
{description}

## Context and Background
This {task_type.lower()} task is part of the TaskHero AI project management system. The implementation should follow established patterns and maintain consistency with the existing codebase.

## Key Considerations
- Ensure compatibility with existing system architecture
- Follow established coding standards and best practices
- Consider performance and scalability implications
- Implement proper error handling and logging
- Include comprehensive testing coverage

## Expected Deliverables
- Functional implementation meeting all requirements
- Unit tests with appropriate coverage
- Documentation updates as needed
- Code review and quality assurance completion

## Context from Embeddings
"""
        for file_context in relevant_context:
            enhanced += f"- {file_context['file_name']} ({file_context['file_type']}): {file_context['content_preview']}\n"
        
        enhanced += """
## Additional Considerations
- Ensure that the implementation aligns with the existing codebase and architectural patterns.
- Consider the impact of the task on the existing system and its dependencies.
- Ensure that the task is well-documented and that all stakeholders are aware of its requirements and deliverables.
"""
        return enhanced.strip()
    
    def _ai_generate_requirements(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> List[str]:
        """Generate functional requirements based on description."""
        # This would use AI to analyze the description and generate requirements
        base_requirements = [
            "System must handle the described functionality correctly",
            "Implementation must be robust and handle edge cases",
            "User interface (if applicable) must be intuitive and responsive",
            "Performance must meet established benchmarks",
            "Security considerations must be addressed appropriately"
        ]
        
        # Add task-type specific requirements
        task_type = context.get('task_type', 'Development')
        if task_type == 'Development':
            base_requirements.extend([
                "Code must follow established architectural patterns",
                "Integration with existing systems must be seamless"
            ])
        elif task_type == 'Bug Fix':
            base_requirements.extend([
                "Root cause must be identified and addressed",
                "Fix must not introduce new issues or regressions"
            ])
        elif task_type == 'Test Case':
            base_requirements.extend([
                "Test coverage must be comprehensive",
                "Tests must be maintainable and reliable"
            ])
        
        # Add context-based requirements
        for file_context in relevant_context:
            base_requirements.append(f"Use {file_context['file_name']} for {file_context['file_type']} implementation")
        
        return base_requirements
    
    def _ai_generate_benefits(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> List[str]:
        """Generate benefits and value proposition."""
        benefits = [
            "Improves overall system functionality and user experience",
            "Enhances code quality and maintainability",
            "Reduces technical debt and future maintenance costs",
            "Supports project goals and business objectives",
            "Provides foundation for future enhancements"
        ]
        
        # Add context-based benefits
        if relevant_context:
            benefits.append(f"Leverages existing codebase patterns from {len(relevant_context)} relevant files")
        
        return benefits
    
    def _ai_generate_implementation_analysis(self, description: str, context: Dict[str, Any], relevant_context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate implementation analysis using AI insights."""
        return {
            'current_implementation': 'Analyze existing codebase and identify current state of related functionality.',
            'current_components': 'Map existing components and their relationships to the new requirements.',
            'current_limitations': 'Identify limitations in current implementation that this task addresses.',
            'new_features': 'Define new features and capabilities being added.',
            'new_features_2': 'Outline secondary features and improvements.',
            'new_features_3': 'Describe additional enhancements and optimizations.',
            'migration_approach': 'Plan migration strategy from current to new implementation.',
            'backward_compatibility': 'Ensure backward compatibility where required.',
            'risk_mitigation': 'Implement strategies to mitigate identified risks.',
            'context_based_analysis': f'Use context from {", ".join(file_context["file_name"] for file_context in relevant_context)}'
        }
    
    def _generate_filename(self, task_id: str, task_type: str, title: str) -> str:
        """Generate filename following TaskHero naming convention."""
        # Get task type abbreviation
        task_prefix = self.task_type_mappings.get(task_type, 'DEV')
        
        # Clean title for filename
        clean_title = title.lower()
        clean_title = ''.join(c if c.isalnum() or c in ' -_' else '' for c in clean_title)
        clean_title = '-'.join(clean_title.split())
        clean_title = clean_title[:50]  # Limit length
        
        return f"{task_id}-{task_prefix}-{clean_title}.md"
    
    def _save_task_file(self, filename: str, content: str) -> Path:
        """Save the task file to the appropriate directory."""
        # Save to todo directory by default
        todo_dir = self.project_root / "mods" / "project_management" / "planning" / "todo"
        todo_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = todo_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def create_task_interactive(self) -> Tuple[bool, str, Optional[str]]:
        """Create a task through interactive prompts."""
        try:
            print("\n🚀 Enhanced Task Creation Wizard")
            print("=" * 50)
            
            # Collect basic information
            title = input("📝 Task Title: ").strip()
            if not title:
                return False, "", "Task title is required"
            
            print("\n📋 Task Type:")
            for i, task_type in enumerate(self.task_type_mappings.keys(), 1):
                print(f"  {i}. {task_type}")
            
            task_type_choice = input("Select task type (1-7, default 1): ").strip()
            task_types = list(self.task_type_mappings.keys())
            try:
                task_type = task_types[int(task_type_choice) - 1] if task_type_choice else task_types[0]
            except (ValueError, IndexError):
                task_type = task_types[0]
            
            print(f"\n⚡ Priority:")
            priorities = ["Low", "Medium", "High", "Critical"]
            for i, priority in enumerate(priorities, 1):
                print(f"  {i}. {priority}")
            
            priority_choice = input("Select priority (1-4, default 2): ").strip()
            try:
                priority = priorities[int(priority_choice) - 1] if priority_choice else "Medium"
            except (ValueError, IndexError):
                priority = "Medium"
            
            assigned_to = input("\n👤 Assigned to (default: Developer): ").strip() or "Developer"
            
            due_date = input("\n📅 Due date (YYYY-MM-DD, optional): ").strip()
            if due_date and not self._validate_date(due_date):
                print("⚠️  Invalid date format, using auto-calculated due date")
                due_date = None
            
            tags_input = input("\n🏷️  Tags (comma-separated, optional): ").strip()
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []
            
            dependencies_input = input("\n🔗 Dependencies (comma-separated task IDs, optional): ").strip()
            dependencies = [dep.strip() for dep in dependencies_input.split(',') if dep.strip()] if dependencies_input else []
            
            print(f"\n💪 Effort Estimate:")
            efforts = ["Small (1-8h)", "Medium (1-3d)", "Large (1w+)"]
            for i, effort in enumerate(efforts, 1):
                print(f"  {i}. {effort}")
            
            effort_choice = input("Select effort (1-3, default 2): ").strip()
            effort_map = {"1": "Small", "2": "Medium", "3": "Large"}
            effort_estimate = effort_map.get(effort_choice, "Medium")
            
            print(f"\n📝 Task Description:")
            print("Enter a detailed description (press Enter twice to finish):")
            description_lines = []
            while True:
                line = input()
                if line == "" and description_lines and description_lines[-1] == "":
                    break
                description_lines.append(line)
            
            description = '\n'.join(description_lines).strip()
            
            use_ai = input(f"\n🤖 Use AI enhancement? (y/n, default y): ").strip().lower() != 'n'
            
            print(f"\n📊 Task Summary:")
            print(f"  Title: {title}")
            print(f"  Type: {task_type}")
            print(f"  Priority: {priority}")
            print(f"  Assigned to: {assigned_to}")
            print(f"  Due date: {due_date or 'Auto-calculated'}")
            print(f"  Tags: {', '.join(tags) if tags else 'None'}")
            print(f"  Dependencies: {', '.join(dependencies) if dependencies else 'None'}")
            print(f"  Effort: {effort_estimate}")
            print(f"  AI Enhancement: {'Yes' if use_ai else 'No'}")
            print(f"  Description: {len(description)} characters")
            
            confirm = input(f"\n✅ Create this task? (y/n, default y): ").strip().lower()
            if confirm == 'n':
                return False, "", "Task creation cancelled by user"
            
            # Create the task
            return self.create_enhanced_task(
                title=title,
                description=description,
                task_type=task_type,
                priority=priority.lower(),
                assigned_to=assigned_to,
                due_date=due_date,
                tags=tags,
                dependencies=dependencies,
                effort_estimate=effort_estimate,
                use_ai_enhancement=use_ai
            )
            
        except KeyboardInterrupt:
            return False, "", "Task creation cancelled by user"
        except Exception as e:
            logger.error(f"Error in interactive task creation: {e}")
            return False, "", str(e)
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date format."""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False 