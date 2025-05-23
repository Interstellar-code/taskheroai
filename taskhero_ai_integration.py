"""
TaskHero AI Integration Module

This module generates prompts for external AI agents to provide intelligent task management features.
Instead of calling AI services directly, it produces structured prompts that can be consumed by
external AI agents using Claude/OpenAI or other LLM providers.

Key Features:
- Codebase analysis prompts for task generation
- Code-to-task correlation prompt generation
- Task prioritization analysis prompts
- Project insights and analytics prompts
- Automated documentation prompts
- Smart task breakdown prompts
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import subprocess
import ast

# Import with error handling for optional dependencies
try:
    from mods.project_management.task_manager import TaskManager, TaskStatus, TaskPriority, Task
    TASK_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Task manager not available: {e}")
    TASK_MANAGER_AVAILABLE = False
    
    # Create mock classes for testing
    class TaskStatus:
        BACKLOG = "backlog"
        TODO = "todo" 
        INPROGRESS = "inprogress"
        DEVDONE = "devdone"
        TESTING = "testing"
        DONE = "done"
        ARCHIVE = "archive"
        
    class TaskPriority:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
        
    class Task:
        def __init__(self, task_id="", title="", content="", status=None, priority=None):
            self.task_id = task_id
            self.title = title
            self.content = content
            self.status = status or TaskStatus.TODO
            self.priority = priority or TaskPriority.MEDIUM
            self.created_date = datetime.now().strftime("%Y-%m-%d")
            self.due_date = None
            
    class TaskManager:
        def __init__(self, project_path=None):
            self.project_path = project_path or os.getcwd()
            
        def get_all_tasks(self):
            return {"todo": [], "inprogress": [], "done": []}
            
        def get_task_summary(self):
            return {"todo": 0, "inprogress": 0, "done": 0}

try:
    from mods.code.indexer import FileIndexer
    FILE_INDEXER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: File indexer not available: {e}")
    FILE_INDEXER_AVAILABLE = False
    
    class FileIndexer:
        def __init__(self, project_path):
            self.project_path = project_path

logger = logging.getLogger("TaskHero.AI.Integration")


class AIPromptGenerator:
    """Generates prompts for external AI agents to provide intelligent task management features."""
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize the AI Integration module.
        
        Args:
            project_path: Path to the project root (defaults to current directory)
        """
        self.project_path = project_path or os.getcwd()
        
        # Initialize task manager with fallback
        if TASK_MANAGER_AVAILABLE:
            self.task_manager = TaskManager(self.project_path)
        else:
            self.task_manager = TaskManager(self.project_path)  # Use mock version
            logger.warning("Using mock TaskManager - full functionality may not be available")
        
        # Initialize indexer if available
        self.indexer = None
        if FILE_INDEXER_AVAILABLE:
            try:
                self.indexer = FileIndexer(self.project_path)
            except Exception as e:
                logger.warning(f"FileIndexer initialization failed: {e}")
        else:
            logger.warning("FileIndexer not available - using basic file analysis")
        
        logger.info("AI Integration module initialized successfully")
    
    def generate_codebase_analysis_prompt(self, analysis_type: str = "task_generation") -> Dict[str, Any]:
        """
        Generate a prompt for AI agents to analyze the codebase and suggest tasks.
        
        Args:
            analysis_type: Type of analysis ('task_generation', 'code_quality', 'architecture')
            
        Returns:
            Dict containing the structured prompt for external AI consumption
        """
        try:
            # Gather codebase context
            codebase_context = self._gather_codebase_context()
            existing_tasks = self._get_existing_tasks_summary()
            project_structure = self._get_project_structure()
            
            prompt_data = {
                "task_type": "codebase_analysis",
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "project_path": self.project_path,
                    "project_structure": project_structure,
                    "codebase_summary": codebase_context,
                    "existing_tasks": existing_tasks,
                    "git_status": self._get_git_status()
                },
                "prompt": self._build_codebase_analysis_prompt(analysis_type, codebase_context, existing_tasks),
                "expected_output": {
                    "format": "structured_json",
                    "fields": [
                        "suggested_tasks",
                        "priority_recommendations", 
                        "code_quality_issues",
                        "architectural_suggestions",
                        "dependencies_analysis"
                    ]
                }
            }
            
            return prompt_data
            
        except Exception as e:
            logger.error(f"Error generating codebase analysis prompt: {str(e)}")
            return {"error": f"Failed to generate codebase analysis prompt: {str(e)}"}
    
    def generate_task_prioritization_prompt(self, tasks: Optional[List[Task]] = None) -> Dict[str, Any]:
        """
        Generate a prompt for AI agents to analyze and prioritize tasks intelligently.
        
        Args:
            tasks: List of tasks to prioritize (defaults to all active tasks)
            
        Returns:
            Dict containing the structured prompt for external AI consumption
        """
        try:
            if tasks is None:
                all_tasks = self.task_manager.get_all_tasks()
                tasks = []
                for status_tasks in all_tasks.values():
                    if status_tasks:
                        tasks.extend(status_tasks)
            
            # Filter out completed/archived tasks
            active_tasks = [t for t in tasks if t.status not in [TaskStatus.DONE, TaskStatus.ARCHIVE]]
            
            # Gather context for prioritization
            project_context = self._gather_project_context()
            dependencies = self._analyze_task_dependencies(active_tasks)
            
            prompt_data = {
                "task_type": "task_prioritization",
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "project_context": project_context,
                    "task_dependencies": dependencies,
                    "current_sprint_goals": self._get_current_sprint_goals(),
                    "team_capacity": self._estimate_team_capacity()
                },
                "tasks_to_prioritize": [self._task_to_prompt_format(task) for task in active_tasks],
                "prompt": self._build_task_prioritization_prompt(active_tasks, project_context),
                "expected_output": {
                    "format": "structured_json",
                    "fields": [
                        "prioritized_task_list",
                        "prioritization_reasoning",
                        "suggested_sprint_planning",
                        "risk_analysis",
                        "dependency_warnings"
                    ]
                }
            }
            
            return prompt_data
            
        except Exception as e:
            logger.error(f"Error generating task prioritization prompt: {str(e)}")
            return {"error": f"Failed to generate task prioritization prompt: {str(e)}"}
    
    def generate_code_to_task_correlation_prompt(self, git_diff: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a prompt for AI agents to correlate code changes with tasks.
        
        Args:
            git_diff: Git diff content (defaults to current working directory changes)
            
        Returns:
            Dict containing the structured prompt for external AI consumption
        """
        try:
            if git_diff is None:
                git_diff = self._get_current_git_diff()
            
            # Get recent tasks and code changes
            recent_tasks = self._get_recent_tasks()
            file_changes = self._analyze_file_changes(git_diff)
            
            prompt_data = {
                "task_type": "code_task_correlation",
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "git_diff": git_diff,
                    "file_changes_summary": file_changes,
                    "recent_tasks": [self._task_to_prompt_format(task) for task in recent_tasks],
                    "commit_history": self._get_recent_commit_history()
                },
                "prompt": self._build_code_correlation_prompt(git_diff, recent_tasks, file_changes),
                "expected_output": {
                    "format": "structured_json",
                    "fields": [
                        "task_correlations",
                        "progress_updates",
                        "suggested_status_changes",
                        "new_tasks_from_code",
                        "completion_estimates"
                    ]
                }
            }
            
            return prompt_data
            
        except Exception as e:
            logger.error(f"Error generating code correlation prompt: {str(e)}")
            return {"error": f"Failed to generate code correlation prompt: {str(e)}"}
    
    def generate_project_insights_prompt(self, insight_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate a prompt for AI agents to provide project insights and analytics.
        
        Args:
            insight_type: Type of insights ('comprehensive', 'velocity', 'quality', 'risks')
            
        Returns:
            Dict containing the structured prompt for external AI consumption
        """
        try:
            # Gather comprehensive project data
            project_metrics = self._gather_project_metrics()
            task_analytics = self._analyze_task_patterns()
            codebase_health = self._assess_codebase_health()
            
            prompt_data = {
                "task_type": "project_insights",
                "insight_type": insight_type,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "project_metrics": project_metrics,
                    "task_analytics": task_analytics,
                    "codebase_health": codebase_health,
                    "team_performance": self._analyze_team_performance(),
                    "timeline_analysis": self._analyze_project_timeline()
                },
                "prompt": self._build_project_insights_prompt(insight_type, project_metrics, task_analytics),
                "expected_output": {
                    "format": "structured_json",
                    "fields": [
                        "key_insights",
                        "performance_metrics",
                        "risk_assessment",
                        "recommendations",
                        "future_predictions"
                    ]
                }
            }
            
            return prompt_data
            
        except Exception as e:
            logger.error(f"Error generating project insights prompt: {str(e)}")
            return {"error": f"Failed to generate project insights prompt: {str(e)}"}
    
    def generate_task_breakdown_prompt(self, complex_task: Task) -> Dict[str, Any]:
        """
        Generate a prompt for AI agents to break down complex tasks into smaller tasks.
        
        Args:
            complex_task: The complex task to break down
            
        Returns:
            Dict containing the structured prompt for external AI consumption
        """
        try:
            # Analyze task complexity
            complexity_analysis = self._analyze_task_complexity(complex_task)
            related_code = self._find_related_code_files(complex_task)
            similar_tasks = self._find_similar_tasks(complex_task)
            
            prompt_data = {
                "task_type": "task_breakdown",
                "timestamp": datetime.now().isoformat(),
                "target_task": self._task_to_prompt_format(complex_task),
                "context": {
                    "complexity_analysis": complexity_analysis,
                    "related_code_files": related_code,
                    "similar_tasks": [self._task_to_prompt_format(task) for task in similar_tasks],
                    "project_patterns": self._get_project_patterns()
                },
                "prompt": self._build_task_breakdown_prompt(complex_task, complexity_analysis),
                "expected_output": {
                    "format": "structured_json",
                    "fields": [
                        "subtasks",
                        "task_dependencies",
                        "estimated_effort",
                        "implementation_order",
                        "success_criteria"
                    ]
                }
            }
            
            return prompt_data
            
        except Exception as e:
            logger.error(f"Error generating task breakdown prompt: {str(e)}")
            return {"error": f"Failed to generate task breakdown prompt: {str(e)}"}
    
    def generate_documentation_prompt(self, doc_type: str = "project_summary") -> Dict[str, Any]:
        """
        Generate a prompt for AI agents to create automated documentation.
        
        Args:
            doc_type: Type of documentation ('project_summary', 'api_docs', 'user_guide')
            
        Returns:
            Dict containing the structured prompt for external AI consumption
        """
        try:
            # Gather documentation context
            code_structure = self._analyze_code_structure()
            completed_tasks = self._get_completed_tasks()
            project_goals = self._extract_project_goals()
            
            prompt_data = {
                "task_type": "documentation_generation",
                "doc_type": doc_type,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "code_structure": code_structure,
                    "completed_tasks": [self._task_to_prompt_format(task) for task in completed_tasks],
                    "project_goals": project_goals,
                    "existing_docs": self._scan_existing_documentation()
                },
                "prompt": self._build_documentation_prompt(doc_type, code_structure, completed_tasks),
                "expected_output": {
                    "format": "markdown_document",
                    "fields": [
                        "document_content",
                        "table_of_contents",
                        "code_examples",
                        "diagrams_needed",
                        "update_recommendations"
                    ]
                }
            }
            
            return prompt_data
            
        except Exception as e:
            logger.error(f"Error generating documentation prompt: {str(e)}")
            return {"error": f"Failed to generate documentation prompt: {str(e)}"}
    
    # Helper methods for gathering context and building prompts
    
    def _gather_codebase_context(self) -> Dict[str, Any]:
        """Gather comprehensive codebase context for analysis."""
        context = {
            "total_files": 0,
            "programming_languages": [],
            "file_extensions": {},
            "recent_changes": [],
            "code_patterns": [],
            "dependencies": []
        }
        
        try:
            # Analyze file structure
            for root, dirs, files in os.walk(self.project_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
                
                for file in files:
                    if not file.startswith('.'):
                        context["total_files"] += 1
                        ext = Path(file).suffix.lower()
                        if ext:
                            context["file_extensions"][ext] = context["file_extensions"].get(ext, 0) + 1
            
            # Identify programming languages
            lang_mapping = {
                '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
                '.go': 'Go', '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby'
            }
            
            for ext, count in context["file_extensions"].items():
                if ext in lang_mapping:
                    context["programming_languages"].append({
                        "language": lang_mapping[ext],
                        "file_count": count,
                        "percentage": round((count / context["total_files"]) * 100, 1)
                    })
            
            # Get recent file changes
            context["recent_changes"] = self._get_recent_file_changes()
            
        except Exception as e:
            logger.warning(f"Error gathering codebase context: {e}")
        
        return context
    
    def _get_existing_tasks_summary(self) -> Dict[str, Any]:
        """Get a summary of existing tasks."""
        try:
            all_tasks = self.task_manager.get_all_tasks()
            summary = {
                "total_tasks": 0,
                "by_status": {},
                "by_priority": {},
                "recent_tasks": []
            }
            
            for status, tasks in all_tasks.items():
                summary["by_status"][status] = len(tasks)
                summary["total_tasks"] += len(tasks)
                
                # Get recent tasks (last 10)
                for task in tasks[-10:]:
                    summary["recent_tasks"].append({
                        "id": task.task_id,
                        "title": task.title,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "created": task.created_date
                    })
            
            return summary
        except Exception as e:
            logger.warning(f"Error getting tasks summary: {e}")
            return {"total_tasks": 0, "by_status": {}, "by_priority": {}, "recent_tasks": []}
    
    def _get_project_structure(self) -> Dict[str, Any]:
        """Analyze and return project structure."""
        structure = {
            "root_files": [],
            "main_directories": [],
            "config_files": [],
            "documentation_files": []
        }
        
        try:
            root_path = Path(self.project_path)
            
            # Analyze root level
            for item in root_path.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    structure["root_files"].append(item.name)
                    
                    # Categorize important files
                    if item.suffix.lower() in ['.md', '.txt', '.rst']:
                        structure["documentation_files"].append(item.name)
                    elif item.name.lower() in ['requirements.txt', 'package.json', 'Cargo.toml', 'pom.xml']:
                        structure["config_files"].append(item.name)
                        
                elif item.is_dir() and not item.name.startswith('.'):
                    structure["main_directories"].append(item.name)
            
        except Exception as e:
            logger.warning(f"Error analyzing project structure: {e}")
        
        return structure
    
    def _build_codebase_analysis_prompt(self, analysis_type: str, codebase_context: Dict, existing_tasks: Dict) -> str:
        """Build the main prompt for codebase analysis."""
        prompt = f"""
# Codebase Analysis Request for Task Generation

## Analysis Type: {analysis_type.replace('_', ' ').title()}

## Project Context
- **Total Files**: {codebase_context.get('total_files', 0)}
- **Programming Languages**: {', '.join([lang['language'] for lang in codebase_context.get('programming_languages', [])])}
- **Existing Tasks**: {existing_tasks.get('total_tasks', 0)} tasks across various statuses

## Current Project Structure
{json.dumps(codebase_context, indent=2)}

## Existing Tasks Summary
{json.dumps(existing_tasks, indent=2)}

## Request
Please analyze this codebase and provide intelligent suggestions for:

1. **New Tasks**: Identify areas that need development, improvements, or fixes
2. **Priority Assessment**: Evaluate what should be worked on first based on:
   - Technical debt
   - Security concerns
   - Performance issues
   - Feature completeness
   - Code quality

3. **Code Quality Issues**: Highlight any patterns or files that need attention

4. **Architectural Suggestions**: Recommend structural improvements

5. **Dependencies Analysis**: Identify missing or outdated dependencies

## Output Format
Please provide a structured JSON response with the following sections:
- suggested_tasks: Array of new task suggestions with titles, descriptions, priorities
- priority_recommendations: Ranking of existing and new tasks
- code_quality_issues: Identified problems and suggested fixes
- architectural_suggestions: High-level improvements
- dependencies_analysis: Dependency-related recommendations

Focus on actionable, specific suggestions that will improve the project's quality and functionality.
"""
        
        return prompt.strip()
    
    def _build_task_prioritization_prompt(self, tasks: List[Task], project_context: Dict) -> str:
        """Build the main prompt for task prioritization."""
        task_list = "\n".join([f"- **{task.task_id}**: {task.title} (Current Priority: {task.priority.value}, Status: {task.status.value})" 
                              for task in tasks])
        
        prompt = f"""
# Task Prioritization Analysis Request

## Current Active Tasks ({len(tasks)} tasks)
{task_list}

## Project Context
{json.dumps(project_context, indent=2)}

## Request
Please analyze these tasks and provide intelligent prioritization based on:

1. **Business Value**: Impact on project goals and user experience
2. **Technical Dependencies**: What tasks block others
3. **Risk Assessment**: Technical complexity and potential issues
4. **Resource Requirements**: Estimated effort and skills needed
5. **Timeline Constraints**: Deadlines and sprint planning

## Analysis Needed
1. **Prioritized Task List**: Reorder tasks by recommended priority with reasoning
2. **Dependency Mapping**: Identify which tasks depend on others
3. **Risk Analysis**: Highlight high-risk tasks that need attention
4. **Sprint Planning**: Suggest how to group tasks for development sprints
5. **Resource Allocation**: Recommend team member assignments if applicable

## Output Format
Provide a structured JSON response with prioritization logic and clear reasoning for each recommendation.
"""
        
        return prompt.strip()
    
    def _build_code_correlation_prompt(self, git_diff: str, recent_tasks: List[Task], file_changes: Dict) -> str:
        """Build the main prompt for code-to-task correlation."""
        task_summary = "\n".join([f"- **{task.task_id}**: {task.title} ({task.status.value})" 
                                 for task in recent_tasks])
        
        prompt = f"""
# Code-to-Task Correlation Analysis

## Recent Code Changes
```
{git_diff[:2000]}...  # Truncated for brevity
```

## File Changes Summary
{json.dumps(file_changes, indent=2)}

## Recent Active Tasks
{task_summary}

## Request
Please analyze the code changes and correlate them with existing tasks:

1. **Task Progress Tracking**: Which tasks have been advanced by these changes?
2. **Completion Detection**: Are any tasks now complete or ready for testing?
3. **New Task Identification**: Do the changes suggest new tasks or issues?
4. **Status Updates**: What task status changes are recommended?
5. **Quality Assessment**: Do the changes introduce any quality concerns?

## Analysis Focus
- Map specific file changes to task requirements
- Identify task completion indicators in the code
- Detect potential issues or technical debt
- Suggest follow-up tasks based on the changes

## Output Format
Provide structured JSON with task correlations, progress updates, and recommendations.
"""
        
        return prompt.strip()
    
    def _build_project_insights_prompt(self, insight_type: str, project_metrics: Dict, task_analytics: Dict) -> str:
        """Build the main prompt for project insights."""
        prompt = f"""
# Project Insights Analysis Request

## Insight Type: {insight_type.replace('_', ' ').title()}

## Project Metrics
{json.dumps(project_metrics, indent=2)}

## Task Analytics
{json.dumps(task_analytics, indent=2)}

## Request
Please provide comprehensive project insights focusing on:

1. **Performance Metrics**: Development velocity, task completion rates
2. **Quality Assessment**: Code quality trends, technical debt analysis
3. **Risk Identification**: Potential blockers, resource constraints
4. **Trend Analysis**: Progress patterns, productivity insights
5. **Future Predictions**: Timeline estimates, resource planning

## Specific Analysis Needed
- Overall project health score
- Development velocity trends
- Quality and technical debt indicators
- Resource utilization efficiency
- Risk factors and mitigation strategies
- Recommendations for improvement

## Output Format
Provide actionable insights with supporting data and clear recommendations for project improvement.
"""
        
        return prompt.strip()
    
    def _build_task_breakdown_prompt(self, complex_task: Task, complexity_analysis: Dict) -> str:
        """Build the main prompt for task breakdown."""
        prompt = f"""
# Complex Task Breakdown Request

## Target Task
- **ID**: {complex_task.task_id}
- **Title**: {complex_task.title}
- **Current Status**: {complex_task.status.value}
- **Priority**: {complex_task.priority.value}

## Task Content
{complex_task.content[:1000]}...

## Complexity Analysis
{json.dumps(complexity_analysis, indent=2)}

## Request
Please break down this complex task into smaller, manageable subtasks:

1. **Subtask Identification**: Create specific, actionable subtasks
2. **Dependency Mapping**: Identify dependencies between subtasks
3. **Effort Estimation**: Estimate time/complexity for each subtask
4. **Implementation Order**: Suggest optimal sequence for completion
5. **Success Criteria**: Define clear completion criteria for each subtask

## Breakdown Guidelines
- Each subtask should be completable in 1-2 days
- Subtasks should have clear, testable outcomes
- Consider technical dependencies and logical flow
- Include testing and documentation subtasks
- Maintain traceability to original requirements

## Output Format
Provide structured JSON with detailed subtask breakdown and implementation plan.
"""
        
        return prompt.strip()
    
    def _build_documentation_prompt(self, doc_type: str, code_structure: Dict, completed_tasks: List[Task]) -> str:
        """Build the main prompt for documentation generation."""
        prompt = f"""
# Documentation Generation Request

## Documentation Type: {doc_type.replace('_', ' ').title()}

## Code Structure Analysis
{json.dumps(code_structure, indent=2)}

## Completed Tasks ({len(completed_tasks)} tasks)
{chr(10).join([f"- {task.task_id}: {task.title}" for task in completed_tasks[:10]])}

## Request
Please generate comprehensive documentation for this project:

1. **Project Overview**: Purpose, goals, and scope
2. **Architecture**: System design and component relationships
3. **Installation**: Setup and configuration instructions
4. **Usage**: How to use the system/API
5. **Development**: Contributing guidelines and development setup

## Documentation Requirements
- Clear, concise language suitable for both technical and non-technical users
- Code examples where appropriate
- Diagrams and visual aids recommendations
- Table of contents and navigation structure
- Update and maintenance guidelines

## Output Format
Provide well-structured Markdown documentation with clear sections and professional formatting.
"""
        
        return prompt.strip()
    
    # Additional helper methods for context gathering
    
    def _get_git_status(self) -> Dict[str, Any]:
        """Get current git status information."""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                   capture_output=True, text=True, cwd=self.project_path)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return {
                    "has_changes": bool(lines[0]) if lines else False,
                    "modified_files": len([l for l in lines if l.startswith(' M')]),
                    "new_files": len([l for l in lines if l.startswith('??')]),
                    "staged_files": len([l for l in lines if l.startswith('M ')])
                }
        except Exception as e:
            logger.warning(f"Could not get git status: {e}")
        
        return {"has_changes": False, "modified_files": 0, "new_files": 0, "staged_files": 0}
    
    def _get_current_git_diff(self) -> str:
        """Get current git diff."""
        try:
            result = subprocess.run(['git', 'diff', 'HEAD'], 
                                   capture_output=True, text=True, cwd=self.project_path)
            if result.returncode == 0:
                return result.stdout
        except Exception as e:
            logger.warning(f"Could not get git diff: {e}")
        
        return ""
    
    def _get_recent_file_changes(self) -> List[Dict[str, Any]]:
        """Get recent file changes from git history."""
        changes = []
        try:
            result = subprocess.run(['git', 'log', '--name-status', '--oneline', '-10'], 
                                   capture_output=True, text=True, cwd=self.project_path)
            if result.returncode == 0:
                # Parse git log output
                for line in result.stdout.split('\n')[:20]:  # Limit to recent changes
                    if line.strip():
                        changes.append({"change": line.strip()})
        except Exception as e:
            logger.warning(f"Could not get recent file changes: {e}")
        
        return changes
    
    def _task_to_prompt_format(self, task: Task) -> Dict[str, Any]:
        """Convert a Task object to a format suitable for AI prompts."""
        return {
            "id": task.task_id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_date": task.created_date,
            "due_date": task.due_date,
            "content_preview": task.content[:200] + "..." if len(task.content) > 200 else task.content,
            "estimated_hours": getattr(task.metadata, 'estimated_hours', None),
            "actual_hours": getattr(task.metadata, 'actual_hours', None),
            "completion_percentage": getattr(task.metadata, 'completion_percentage', 0)
        }
    
    def _gather_project_context(self) -> Dict[str, Any]:
        """Gather general project context for analysis."""
        return {
            "project_path": self.project_path,
            "project_name": Path(self.project_path).name,
            "timestamp": datetime.now().isoformat(),
            "git_info": self._get_git_status(),
            "task_summary": self.task_manager.get_task_summary()
        }
    
    def _analyze_task_dependencies(self, tasks: List[Task]) -> Dict[str, List[str]]:
        """Analyze dependencies between tasks."""
        dependencies = {}
        
        for task in tasks:
            # Simple dependency analysis based on task content
            deps = []
            for other_task in tasks:
                if other_task.task_id != task.task_id:
                    # Check if task content references other task
                    if other_task.task_id in task.content or other_task.title.lower() in task.content.lower():
                        deps.append(other_task.task_id)
            
            dependencies[task.task_id] = deps
        
        return dependencies
    
    def _get_current_sprint_goals(self) -> List[str]:
        """Extract current sprint goals from tasks and project context."""
        # This is a placeholder - you might want to implement based on your sprint planning
        return ["Complete core development tasks", "Improve code quality", "Prepare for testing phase"]
    
    def _estimate_team_capacity(self) -> Dict[str, Any]:
        """Estimate team capacity for task planning."""
        # This is a placeholder - you might want to implement based on your team structure
        return {
            "total_developers": 1,
            "hours_per_week": 40,
            "current_utilization": "80%"
        }
    
    def _get_recent_tasks(self, days: int = 7) -> List[Task]:
        """Get tasks created or modified in recent days."""
        all_tasks = self.task_manager.get_all_tasks()
        recent_tasks = []
        
        for status_tasks in all_tasks.values():
            for task in status_tasks:
                # Add all active tasks for now - you might want to filter by date
                if task.status not in [TaskStatus.DONE, TaskStatus.ARCHIVE]:
                    recent_tasks.append(task)
        
        return recent_tasks[-20:]  # Return last 20 tasks
    
    def _analyze_file_changes(self, git_diff: str) -> Dict[str, Any]:
        """Analyze file changes from git diff."""
        analysis = {
            "files_modified": 0,
            "lines_added": 0,
            "lines_removed": 0,
            "file_types": {},
            "modification_patterns": []
        }
        
        if git_diff:
            # Simple diff analysis
            lines = git_diff.split('\n')
            for line in lines:
                if line.startswith('+++') or line.startswith('---'):
                    analysis["files_modified"] += 1
                elif line.startswith('+') and not line.startswith('+++'):
                    analysis["lines_added"] += 1
                elif line.startswith('-') and not line.startswith('---'):
                    analysis["lines_removed"] += 1
        
        return analysis
    
    def _get_recent_commit_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent commit history."""
        commits = []
        try:
            result = subprocess.run(['git', 'log', '--oneline', f'-{limit}'], 
                                   capture_output=True, text=True, cwd=self.project_path)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split(' ', 1)
                        if len(parts) >= 2:
                            commits.append({
                                "hash": parts[0],
                                "message": parts[1]
                            })
        except Exception as e:
            logger.warning(f"Could not get commit history: {e}")
        
        return commits
    
    def _gather_project_metrics(self) -> Dict[str, Any]:
        """Gather comprehensive project metrics."""
        metrics = {
            "task_metrics": self.task_manager.get_task_summary(),
            "codebase_metrics": self._gather_codebase_context(),
            "git_metrics": {
                "status": self._get_git_status(),
                "recent_commits": len(self._get_recent_commit_history())
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics
    
    def _analyze_task_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in task creation and completion."""
        all_tasks = self.task_manager.get_all_tasks()
        
        patterns = {
            "completion_rate": 0,
            "average_task_duration": "Unknown",
            "common_task_types": [],
            "priority_distribution": {},
            "status_distribution": {}
        }
        
        total_tasks = sum(len(tasks) for tasks in all_tasks.values())
        completed_tasks = len(all_tasks.get('done', []))
        
        if total_tasks > 0:
            patterns["completion_rate"] = round((completed_tasks / total_tasks) * 100, 1)
        
        # Analyze status distribution
        for status, tasks in all_tasks.items():
            patterns["status_distribution"][status] = len(tasks)
        
        return patterns
    
    def _assess_codebase_health(self) -> Dict[str, Any]:
        """Assess overall codebase health metrics."""
        health = {
            "total_files": 0,
            "code_quality_score": "Unknown",
            "technical_debt_indicators": [],
            "test_coverage": "Unknown",
            "documentation_coverage": "Unknown"
        }
        
        # Basic file count
        health.update(self._gather_codebase_context())
        
        # Look for common technical debt indicators
        debt_indicators = []
        
        try:
            # Check for TODO/FIXME comments
            for root, dirs, files in os.walk(self.project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if 'TODO' in content.upper():
                                    debt_indicators.append(f"TODO items found in {file}")
                                if 'FIXME' in content.upper():
                                    debt_indicators.append(f"FIXME items found in {file}")
                        except Exception:
                            continue
        except Exception as e:
            logger.warning(f"Error assessing codebase health: {e}")
        
        health["technical_debt_indicators"] = debt_indicators[:10]  # Limit to first 10
        
        return health
    
    def _analyze_team_performance(self) -> Dict[str, Any]:
        """Analyze team performance metrics."""
        return {
            "velocity": "Stable",
            "productivity_score": "Good",
            "collaboration_index": "High",
            "note": "Placeholder metrics - implement based on your team tracking"
        }
    
    def _analyze_project_timeline(self) -> Dict[str, Any]:
        """Analyze project timeline and milestones."""
        return {
            "project_start": "2025-01-27",
            "current_phase": "Development",
            "milestone_progress": "On Track",
            "estimated_completion": "TBD",
            "note": "Implement based on your project planning methodology"
        }
    
    def _analyze_task_complexity(self, task: Task) -> Dict[str, Any]:
        """Analyze complexity of a given task."""
        complexity = {
            "estimated_complexity": "Medium",
            "factors": [],
            "suggested_breakdown": True,
            "risk_level": "Low"
        }
        
        # Analyze task content for complexity indicators
        content = task.content.lower()
        
        complexity_indicators = [
            ("integration", "Requires integration work"),
            ("database", "Involves database changes"),
            ("api", "API development required"),
            ("security", "Security considerations needed"),
            ("performance", "Performance optimization required"),
            ("testing", "Comprehensive testing needed")
        ]
        
        for indicator, description in complexity_indicators:
            if indicator in content:
                complexity["factors"].append(description)
        
        # Adjust complexity based on factors
        if len(complexity["factors"]) > 3:
            complexity["estimated_complexity"] = "High"
            complexity["risk_level"] = "Medium"
        elif len(complexity["factors"]) > 1:
            complexity["estimated_complexity"] = "Medium"
        
        return complexity
    
    def _find_related_code_files(self, task: Task) -> List[str]:
        """Find code files related to a specific task."""
        related_files = []
        
        try:
            # Simple keyword matching - you might want to enhance this
            keywords = [word.lower() for word in re.findall(r'\b\w+\b', task.title + " " + task.content)]
            keywords = [k for k in keywords if len(k) > 3]  # Filter out short words
            
            for root, dirs, files in os.walk(self.project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.java')):
                        file_lower = file.lower()
                        for keyword in keywords[:5]:  # Check first 5 keywords
                            if keyword in file_lower:
                                related_files.append(os.path.join(root, file))
                                break
                        
                        if len(related_files) >= 10:  # Limit results
                            break
        except Exception as e:
            logger.warning(f"Error finding related code files: {e}")
        
        return related_files
    
    def _find_similar_tasks(self, task: Task) -> List[Task]:
        """Find tasks similar to the given task."""
        similar_tasks = []
        all_tasks = self.task_manager.get_all_tasks()
        
        # Simple similarity based on title keywords
        task_keywords = set(re.findall(r'\b\w+\b', task.title.lower()))
        
        for status_tasks in all_tasks.values():
            for other_task in status_tasks:
                if other_task.task_id != task.task_id:
                    other_keywords = set(re.findall(r'\b\w+\b', other_task.title.lower()))
                    
                    # Calculate simple similarity
                    common_keywords = task_keywords.intersection(other_keywords)
                    if len(common_keywords) >= 2:  # At least 2 common keywords
                        similar_tasks.append(other_task)
                    
                    if len(similar_tasks) >= 5:  # Limit results
                        break
        
        return similar_tasks
    
    def _get_project_patterns(self) -> Dict[str, Any]:
        """Extract common patterns from the project."""
        return {
            "naming_conventions": "snake_case for Python",
            "file_organization": "modular structure",
            "common_patterns": ["MVC", "service classes", "utility modules"],
            "note": "Enhance based on actual project analysis"
        }
    
    def _analyze_code_structure(self) -> Dict[str, Any]:
        """Analyze the overall code structure."""
        structure = {
            "main_modules": [],
            "entry_points": [],
            "configuration_files": [],
            "test_files": [],
            "documentation_files": []
        }
        
        try:
            for root, dirs, files in os.walk(self.project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                level = root.replace(self.project_path, '').count(os.sep)
                
                if level <= 2:  # Only analyze top 2 levels
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, self.project_path)
                        
                        if file.endswith('.py') and level <= 1:
                            structure["main_modules"].append(relative_path)
                        elif file in ['app.py', 'main.py', '__main__.py']:
                            structure["entry_points"].append(relative_path)
                        elif file in ['requirements.txt', 'setup.py', 'pyproject.toml']:
                            structure["configuration_files"].append(relative_path)
                        elif file.startswith('test_') or 'test' in file:
                            structure["test_files"].append(relative_path)
                        elif file.endswith(('.md', '.rst', '.txt')):
                            structure["documentation_files"].append(relative_path)
        
        except Exception as e:
            logger.warning(f"Error analyzing code structure: {e}")
        
        return structure
    
    def _get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        all_tasks = self.task_manager.get_all_tasks()
        return all_tasks.get('done', [])
    
    def _extract_project_goals(self) -> List[str]:
        """Extract project goals from various sources."""
        goals = []
        
        # Look for goals in README files
        readme_files = ['README.md', 'README.txt', 'README.rst']
        for readme in readme_files:
            readme_path = os.path.join(self.project_path, readme)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Simple extraction - look for goal-related sections
                        if 'goal' in content.lower() or 'objective' in content.lower():
                            goals.append("Goals mentioned in README")
                        break
                except Exception:
                    continue
        
        if not goals:
            goals = ["Develop comprehensive task management system", "Integrate AI capabilities"]
        
        return goals
    
    def _scan_existing_documentation(self) -> List[str]:
        """Scan for existing documentation files."""
        docs = []
        
        try:
            for root, dirs, files in os.walk(self.project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if file.endswith(('.md', '.rst', '.txt')) and 'readme' not in file.lower():
                        relative_path = os.path.relpath(os.path.join(root, file), self.project_path)
                        docs.append(relative_path)
        except Exception as e:
            logger.warning(f"Error scanning documentation: {e}")
        
        return docs


# Convenience class for external AI agent integration
class AIAgentIntegration:
    """
    Main integration class for external AI agents.
    Provides a simple interface for generating various types of AI prompts.
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """Initialize the AI Agent Integration."""
        self.prompt_generator = AIPromptGenerator(project_path)
        logger.info("AI Agent Integration initialized")
    
    async def generate_prompt(self, prompt_type: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a prompt for external AI consumption.
        
        Args:
            prompt_type: Type of prompt to generate
            **kwargs: Additional parameters for prompt generation
            
        Returns:
            Dict containing the structured prompt
        """
        try:
            if prompt_type == "codebase_analysis":
                return self.prompt_generator.generate_codebase_analysis_prompt(
                    kwargs.get('analysis_type', 'task_generation')
                )
            elif prompt_type == "task_prioritization":
                return self.prompt_generator.generate_task_prioritization_prompt(
                    kwargs.get('tasks', None)
                )
            elif prompt_type == "code_correlation":
                return self.prompt_generator.generate_code_to_task_correlation_prompt(
                    kwargs.get('git_diff', None)
                )
            elif prompt_type == "project_insights":
                return self.prompt_generator.generate_project_insights_prompt(
                    kwargs.get('insight_type', 'comprehensive')
                )
            elif prompt_type == "task_breakdown":
                return self.prompt_generator.generate_task_breakdown_prompt(
                    kwargs.get('task')
                )
            elif prompt_type == "documentation":
                return self.prompt_generator.generate_documentation_prompt(
                    kwargs.get('doc_type', 'project_summary')
                )
            else:
                return {"error": f"Unknown prompt type: {prompt_type}"}
        
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            return {"error": f"Failed to generate prompt: {str(e)}"}
    
    def get_available_prompt_types(self) -> List[str]:
        """Get list of available prompt types."""
        return [
            "codebase_analysis",
            "task_prioritization", 
            "code_correlation",
            "project_insights",
            "task_breakdown",
            "documentation"
        ] 