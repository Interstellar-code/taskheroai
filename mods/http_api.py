"""HTTP API module for TaskHero AI.

This module provides a lightweight HTTP API for TaskHero AI functionality,
allowing remote access to core features like indexing, agent queries, and status checks.
"""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from mods.code.agent_mode import AgentMode
from mods.code.indexer import FileIndexer
from mods.code.memory import MemoryManager
from mods.project_management.task_manager import TaskManager, TaskStatus, TaskPriority
from mods.project_management.kanban_board import KanbanBoard

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)
logger = logging.getLogger("TaskHeroAI.HTTP")

indexer: Optional[FileIndexer] = None
agent_mode: Optional[AgentMode] = None
memory_manager: Optional[MemoryManager] = None
task_manager: Optional[TaskManager] = None
kanban_board: Optional[KanbanBoard] = None
indexing_status: Dict[str, Any] = {
    "in_progress": False,
    "directory": None,
    "start_time": None,
    "complete": False,
    "error": None,
    "progress": 0,
}

background_tasks = set()


def _initialize_task_management() -> bool:
    """Initialize task management components.

    Returns:
        bool: True if successful, False otherwise
    """
    global task_manager, kanban_board

    try:
        if not task_manager:
            task_manager = TaskManager()
            logger.info("TaskManager initialized successfully")

        if not kanban_board:
            kanban_board = KanbanBoard(task_manager)
            logger.info("KanbanBoard initialized successfully")

        return True
    except Exception as e:
        logger.error(f"Error initializing task management: {e}")
        return False


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Get a boolean value from environment variables.

    Args:
        key (str): The environment variable key.
        default (bool): The default value if the key is not found.

    Returns:
        bool: The boolean value.
    """
    value: str = os.getenv(key, str(default)).upper()
    return value in ("TRUE", "YES", "1", "Y", "T")


async def initialize_directory(request: Request) -> JSONResponse:
    """Initialize a directory for use with VerbalCodeAI.

    Args:
        request (Request): HTTP request with directory_path in JSON body

    Returns:
        JSONResponse: Result of initialization
    """
    global indexer, agent_mode, memory_manager, indexing_status

    try:
        data = await request.json()
        directory_path = data.get("directory_path")

        if not directory_path:
            return JSONResponse({"success": False, "error": "Missing directory_path parameter"}, status_code=400)

        if not os.path.isdir(directory_path):
            return JSONResponse({
                "success": False,
                "error": f"Directory not found: {directory_path}"
            }, status_code=404)

        indexer = FileIndexer(directory_path)
        agent_mode = AgentMode(indexer)
        memory_manager = MemoryManager(root_path=directory_path, indexer=indexer)

        # Get index status using the improved indexer method
        index_status = indexer.is_index_complete()
        index_status["directory"] = directory_path

        # Update global indexing_status
        indexing_status.update(index_status)
        indexing_status["directory"] = directory_path

        return JSONResponse({
            "success": True,
            "directory": directory_path,
            "index_status": index_status
        })
    except Exception as e:
        logger.error(f"Error initializing directory: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


async def ask_agent(request: Request) -> JSONResponse:
    """Ask the agent a question about the codebase.

    Args:
        request (Request): HTTP request with question in JSON body

    Returns:
        JSONResponse: Agent's response
    """
    global agent_mode, indexer

    try:
        data = await request.json()
        question = data.get("question")

        if not question:
            return JSONResponse({"success": False, "error": "Missing question parameter"}, status_code=400)

        if not agent_mode or not indexer:
            return JSONResponse({
                "success": False,
                "error": "No directory initialized. Call initialize_directory first."
            }, status_code=400)

        response = await agent_mode.process_query(question)

        return JSONResponse({
            "success": True,
            "question": question,
            "response": response
        })
    except Exception as e:
        logger.error(f"Error processing agent question: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


async def run_indexing() -> None:
    """Run the indexing process in the background."""
    global indexer, indexing_status

    try:
        if not indexer:
            logger.error("Indexer not initialized")
            indexing_status["error"] = "Indexer not initialized"
            indexing_status["in_progress"] = False
            return

        logger.info(f"Starting indexing for directory: {indexer.root_path}")
        indexed_files = indexer.index_directory()

        # Get updated status from indexer
        index_status = indexer.is_index_complete()
        indexing_status.update(index_status)
        indexing_status["in_progress"] = False
        indexing_status["files_indexed"] = len(indexed_files) if indexed_files else 0

        logger.info(f"Indexing completed for directory: {indexer.root_path}, indexed {len(indexed_files) if indexed_files else 0} files")
    except Exception as e:
        logger.error(f"Error during indexing: {e}", exc_info=True)
        indexing_status["error"] = str(e)
        indexing_status["in_progress"] = False


async def start_indexing(request: Request) -> JSONResponse:
    """Start indexing a directory.

    Args:
        request (Request): HTTP request with directory_path in JSON body

    Returns:
        JSONResponse: Result of starting indexing
    """
    global indexer, indexing_status

    try:
        data = await request.json()
        directory_path = data.get("directory_path")

        if not directory_path:
            return JSONResponse({"success": False, "error": "Missing directory_path parameter"}, status_code=400)

        if not os.path.isdir(directory_path):
            return JSONResponse({
                "success": False,
                "error": f"Directory not found: {directory_path}"
            }, status_code=404)

        if indexing_status.get("in_progress", False):
            return JSONResponse({
                "success": False,
                "error": "Indexing already in progress",
                "status": indexing_status
            }, status_code=409)

        if not indexer or indexer.root_path != directory_path:
            indexer = FileIndexer(directory_path)

        indexing_status = {
            "in_progress": True,
            "directory": directory_path,
            "start_time": time.time(),
            "complete": False,
            "error": None,
            "progress": 0,
        }

        task = asyncio.create_task(run_indexing())
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

        return JSONResponse({
            "success": True,
            "status": indexing_status
        })
    except Exception as e:
        logger.error(f"Error starting indexing: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


async def get_indexing_status(request: Request) -> JSONResponse:
    """Get the status of the indexing process.

    Args:
        request (Request): The HTTP request.

    Returns:
        JSONResponse: Current indexing status
    """
    global indexer, indexing_status

    try:
        if indexer:
            # Get current status from indexer
            current_status = indexer.is_index_complete()
            current_status["in_progress"] = indexing_status.get("in_progress", False)
            current_status["directory"] = indexer.root_path
            current_status["files_indexed"] = indexing_status.get("files_indexed", 0)

            # Update global status
            indexing_status.update(current_status)

        return JSONResponse({
            "success": True,
            "status": indexing_status
        })
    except Exception as e:
        logger.error(f"Error getting indexing status: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


async def health_check(request: Request) -> JSONResponse:
    """Simple health check endpoint.

    Args:
        request (Request): The HTTP request.

    Returns:
        JSONResponse: Health status
    """
    return JSONResponse({
        "status": "ok",
        "version": "1.0.0",
        "service": "TaskHero AI HTTP API"
    })


# Task Management Endpoints

async def get_all_tasks(request: Request) -> JSONResponse:
    """Get all tasks organized by status.

    Args:
        request (Request): The HTTP request.

    Returns:
        JSONResponse: All tasks organized by status
    """
    try:
        if not _initialize_task_management():
            return JSONResponse({
                "success": False,
                "error": "Failed to initialize task management"
            }, status_code=500)

        all_tasks = task_manager.get_all_tasks()

        # Convert tasks to dictionaries for JSON serialization
        tasks_dict = {}
        for status, tasks in all_tasks.items():
            tasks_dict[status] = []
            for task in tasks:
                task_dict = {
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "created_date": task.metadata.created_date,
                    "due_date": getattr(task.metadata, 'due_date', None),
                    "assignee": getattr(task.metadata, 'assignee', None),
                    "task_type": getattr(task.metadata, 'task_type', None),
                    "tags": getattr(task.metadata, 'tags', []),
                    "file_path": task.file_path
                }
                tasks_dict[status].append(task_dict)

        return JSONResponse({
            "success": True,
            "tasks": tasks_dict
        })
    except Exception as e:
        logger.error(f"Error getting all tasks: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


async def get_task_by_id(request: Request) -> JSONResponse:
    """Get a specific task by ID.

    Args:
        request (Request): The HTTP request with task_id in path

    Returns:
        JSONResponse: Task details or error
    """
    try:
        if not _initialize_task_management():
            return JSONResponse({
                "success": False,
                "error": "Failed to initialize task management"
            }, status_code=500)

        task_id = request.path_params.get("task_id")
        if not task_id:
            return JSONResponse({
                "success": False,
                "error": "Missing task_id parameter"
            }, status_code=400)

        task = task_manager.get_task_by_id(task_id)
        if not task:
            return JSONResponse({
                "success": False,
                "error": f"Task not found: {task_id}"
            }, status_code=404)

        task_dict = {
            "task_id": task.task_id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_date": task.metadata.created_date,
            "due_date": getattr(task.metadata, 'due_date', None),
            "assignee": getattr(task.metadata, 'assignee', None),
            "task_type": getattr(task.metadata, 'task_type', None),
            "tags": getattr(task.metadata, 'tags', []),
            "content": task.content,
            "file_path": task.file_path
        }

        return JSONResponse({
            "success": True,
            "task": task_dict
        })
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


async def create_task(request: Request) -> JSONResponse:
    """Create a new task.

    Args:
        request (Request): The HTTP request with task data in JSON body

    Returns:
        JSONResponse: Created task details or error
    """
    try:
        if not _initialize_task_management():
            return JSONResponse({
                "success": False,
                "error": "Failed to initialize task management"
            }, status_code=500)

        data = await request.json()
        title = data.get("title")
        if not title:
            return JSONResponse({
                "success": False,
                "error": "Missing title parameter"
            }, status_code=400)

        # Parse optional parameters
        content = data.get("content", "")
        priority_str = data.get("priority", "medium")
        status_str = data.get("status", "todo")

        try:
            priority = TaskPriority(priority_str.lower())
        except ValueError:
            return JSONResponse({
                "success": False,
                "error": f"Invalid priority: {priority_str}. Valid values: {[p.value for p in TaskPriority]}"
            }, status_code=400)

        try:
            status = TaskStatus(status_str.lower())
        except ValueError:
            return JSONResponse({
                "success": False,
                "error": f"Invalid status: {status_str}. Valid values: {[s.value for s in TaskStatus]}"
            }, status_code=400)

        # Create task
        task = task_manager.create_task(
            title=title,
            content=content,
            priority=priority,
            status=status,
            **{k: v for k, v in data.items() if k not in ["title", "content", "priority", "status"]}
        )

        if not task:
            return JSONResponse({
                "success": False,
                "error": "Failed to create task"
            }, status_code=500)

        task_dict = {
            "task_id": task.task_id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_date": task.metadata.created_date,
            "due_date": getattr(task.metadata, 'due_date', None),
            "assignee": getattr(task.metadata, 'assignee', None),
            "task_type": getattr(task.metadata, 'task_type', None),
            "tags": getattr(task.metadata, 'tags', []),
            "content": task.content,
            "file_path": task.file_path
        }

        return JSONResponse({
            "success": True,
            "task": task_dict
        }, status_code=201)
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


async def update_task_status(request: Request) -> JSONResponse:
    """Update task status.

    Args:
        request (Request): The HTTP request with task_id in path and new_status in JSON body

    Returns:
        JSONResponse: Updated task details or error
    """
    try:
        if not _initialize_task_management():
            return JSONResponse({
                "success": False,
                "error": "Failed to initialize task management"
            }, status_code=500)

        task_id = request.path_params.get("task_id")
        if not task_id:
            return JSONResponse({
                "success": False,
                "error": "Missing task_id parameter"
            }, status_code=400)

        data = await request.json()
        new_status_str = data.get("status")
        if not new_status_str:
            return JSONResponse({
                "success": False,
                "error": "Missing status parameter"
            }, status_code=400)

        try:
            new_status = TaskStatus(new_status_str.lower())
        except ValueError:
            return JSONResponse({
                "success": False,
                "error": f"Invalid status: {new_status_str}. Valid values: {[s.value for s in TaskStatus]}"
            }, status_code=400)

        success = task_manager.move_task_status(task_id, new_status)
        if not success:
            return JSONResponse({
                "success": False,
                "error": f"Failed to update task status. Task may not exist or transition may be invalid."
            }, status_code=400)

        # Get updated task
        task = task_manager.get_task_by_id(task_id)
        if not task:
            return JSONResponse({
                "success": False,
                "error": f"Task not found after update: {task_id}"
            }, status_code=500)

        task_dict = {
            "task_id": task.task_id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_date": task.metadata.created_date,
            "due_date": getattr(task.metadata, 'due_date', None),
            "assignee": getattr(task.metadata, 'assignee', None),
            "task_type": getattr(task.metadata, 'task_type', None),
            "tags": getattr(task.metadata, 'tags', []),
            "file_path": task.file_path
        }

        return JSONResponse({
            "success": True,
            "task": task_dict,
            "message": f"Task {task_id} status updated to {new_status.value}"
        })
    except Exception as e:
        logger.error(f"Error updating task status: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


async def get_kanban_board(request: Request) -> JSONResponse:
    """Get kanban board data.

    Args:
        request (Request): The HTTP request

    Returns:
        JSONResponse: Kanban board data organized by columns
    """
    try:
        if not _initialize_task_management():
            return JSONResponse({
                "success": False,
                "error": "Failed to initialize task management"
            }, status_code=500)

        all_tasks = task_manager.get_all_tasks()

        # Get kanban columns configuration
        columns = [
            {"status": "backlog", "title": "📦 BACKLOG", "color": "bright_black"},
            {"status": "todo", "title": "📝 TODO", "color": "yellow"},
            {"status": "inprogress", "title": "🔄 IN PROGRESS", "color": "blue"},
            {"status": "testing", "title": "🧪 TESTING", "color": "magenta"},
            {"status": "devdone", "title": "✅ DEV DONE", "color": "cyan"},
            {"status": "done", "title": "🎉 DONE", "color": "green"}
        ]

        # Organize tasks by columns
        kanban_data = []
        for column in columns:
            status = column["status"]
            tasks = all_tasks.get(status, [])

            column_data = {
                "status": status,
                "title": column["title"],
                "color": column["color"],
                "task_count": len(tasks),
                "tasks": []
            }

            for task in tasks:
                task_dict = {
                    "task_id": task.task_id,
                    "title": task.title,
                    "priority": task.priority.value,
                    "created_date": task.metadata.created_date,
                    "due_date": getattr(task.metadata, 'due_date', None),
                    "assignee": getattr(task.metadata, 'assignee', None),
                    "task_type": getattr(task.metadata, 'task_type', None),
                    "tags": getattr(task.metadata, 'tags', [])
                }
                column_data["tasks"].append(task_dict)

            kanban_data.append(column_data)

        return JSONResponse({
            "success": True,
            "kanban": kanban_data,
            "total_tasks": sum(len(tasks) for tasks in all_tasks.values())
        })
    except Exception as e:
        logger.error(f"Error getting kanban board: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


routes = [
    # Health and core endpoints
    Route("/api/health", health_check, methods=["GET"]),
    Route("/api/initialize", initialize_directory, methods=["POST"]),
    Route("/api/ask", ask_agent, methods=["POST"]),

    # Indexing endpoints
    Route("/api/index/start", start_indexing, methods=["POST"]),
    Route("/api/index/status", get_indexing_status, methods=["GET"]),

    # Task management endpoints
    Route("/api/tasks", get_all_tasks, methods=["GET"]),
    Route("/api/tasks", create_task, methods=["POST"]),
    Route("/api/tasks/{task_id}", get_task_by_id, methods=["GET"]),
    Route("/api/tasks/{task_id}/status", update_task_status, methods=["PUT"]),

    # Kanban board endpoints
    Route("/api/kanban", get_kanban_board, methods=["GET"]),
]


def create_app(allow_all_origins: bool = None) -> Starlette:
    """Create and configure the Starlette application.

    Args:
        allow_all_origins (bool, optional): Whether to allow all origins or only localhost.
                                             If None, reads from environment variable. Defaults to None.

    Returns:
        Starlette: Configured application
    """
    if allow_all_origins is None:
        allow_all_origins = _get_env_bool("HTTP_ALLOW_ALL_ORIGINS", False)

    if allow_all_origins:
        logger.warning("HTTP API server configured to allow connections from any IP address")
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["GET", "POST", "PUT", "DELETE"],
                allow_headers=["*"],
            )
        ]
    else:
        logger.info("HTTP API server configured to allow connections from localhost only")
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=["http://localhost", "http://127.0.0.1"],
                allow_methods=["GET", "POST", "PUT", "DELETE"],
                allow_headers=["*"],
            )
        ]

    app = Starlette(
        debug=True,
        routes=routes,
        middleware=middleware,
    )

    return app
