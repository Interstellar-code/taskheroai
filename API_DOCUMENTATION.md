# TaskHero AI HTTP API Documentation

## Overview

The TaskHero AI HTTP API provides RESTful endpoints for managing tasks, accessing kanban board data, code analysis, and integrating with external tools. The API is built using Starlette and supports CORS for web applications.

**Key Features:**
- 📊 Task management and kanban board operations
- 🤖 AI-powered code analysis and chat
- 📁 Project indexing and file management
- 🔗 MCP (Model Context Protocol) integration
- 🌐 RESTful design with JSON responses

## Base URL

```
http://localhost:8000
```

## Quick Start

1. **Start the HTTP API Server:**
   ```bash
   python start_http_server.py --port 8000
   ```

2. **Test the connection:**
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Initialize a project:**
   ```bash
   curl -X POST http://localhost:8000/api/initialize \
     -H "Content-Type: application/json" \
     -d '{"directory_path": "/path/to/your/project"}'
   ```

## Authentication

Currently, the API does not require authentication. This may be added in future versions.

> **Security Note:** By default, the server only accepts connections from localhost (127.0.0.1). To allow connections from other hosts, set `HTTP_ALLOW_ALL_ORIGINS=TRUE` in your `.env` file.

## Response Format

All API responses follow this format:

```json
{
  "success": true|false,
  "data": {...},
  "error": "error message (if success is false)"
}
```

## Endpoints

### Health Check

#### GET /api/health

Check if the API server is running.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "service": "TaskHero AI HTTP API"
}
```

### Directory Management

#### POST /api/initialize

Initialize a directory for code analysis.

**Request Body:**
```json
{
  "directory_path": "/path/to/directory"
}
```

**Response:**
```json
{
  "success": true,
  "directory": "/path/to/directory",
  "index_status": {
    "complete": true|false,
    "reason": "status description",
    "outdated_count": 0,
    "missing_count": 0,
    "ignored_count": 0
  }
}
```

### AI Agent

#### POST /api/ask

Ask the AI agent a question about the codebase.

**Request Body:**
```json
{
  "question": "What does this function do?"
}
```

**Response:**
```json
{
  "success": true,
  "question": "What does this function do?",
  "response": "AI agent response..."
}
```

### Indexing

#### POST /api/index/start

Start indexing a directory.

**Request Body:**
```json
{
  "directory_path": "/path/to/directory"
}
```

**Response:**
```json
{
  "success": true,
  "status": {
    "in_progress": true,
    "directory": "/path/to/directory",
    "start_time": 1234567890,
    "complete": false,
    "error": null,
    "progress": 0
  }
}
```

#### GET /api/index/status

Get the current indexing status.

**Response:**
```json
{
  "success": true,
  "status": {
    "in_progress": false,
    "directory": "/path/to/directory",
    "complete": true,
    "files_indexed": 150,
    "outdated_count": 0,
    "missing_count": 0,
    "ignored_count": 25
  }
}
```

### Task Management

#### GET /api/tasks

Get all tasks organized by status.

**Response:**
```json
{
  "success": true,
  "tasks": {
    "todo": [
      {
        "task_id": "TASK-001",
        "title": "Implement feature X",
        "status": "todo",
        "priority": "high",
        "created_date": "2025-01-27",
        "due_date": "2025-02-01",
        "assignee": "Developer",
        "task_type": "Development",
        "tags": ["feature", "api"],
        "file_path": "/path/to/task/file.md"
      }
    ],
    "inprogress": [...],
    "done": [...]
  }
}
```

#### POST /api/tasks

Create a new task.

**Request Body:**
```json
{
  "title": "Task title",
  "content": "Task description and details",
  "priority": "medium",
  "status": "todo",
  "due_date": "2025-02-01",
  "assignee": "Developer",
  "task_type": "Development",
  "tags": ["tag1", "tag2"]
}
```

**Response:**
```json
{
  "success": true,
  "task": {
    "task_id": "TASK-002",
    "title": "Task title",
    "status": "todo",
    "priority": "medium",
    "created_date": "2025-01-27",
    "content": "Task description and details",
    "file_path": "/path/to/task/file.md"
  }
}
```

#### GET /api/tasks/{task_id}

Get details for a specific task.

**Response:**
```json
{
  "success": true,
  "task": {
    "task_id": "TASK-001",
    "title": "Implement feature X",
    "status": "todo",
    "priority": "high",
    "created_date": "2025-01-27",
    "content": "Full task content in markdown format...",
    "file_path": "/path/to/task/file.md"
  }
}
```

#### PUT /api/tasks/{task_id}/status

Update the status of a task.

**Request Body:**
```json
{
  "status": "inprogress"
}
```

**Response:**
```json
{
  "success": true,
  "task": {
    "task_id": "TASK-001",
    "title": "Implement feature X",
    "status": "inprogress",
    "priority": "high",
    "created_date": "2025-01-27",
    "file_path": "/path/to/task/file.md"
  },
  "message": "Task TASK-001 status updated to inprogress"
}
```

### Kanban Board

#### GET /api/kanban

Get kanban board data with tasks organized by columns.

**Response:**
```json
{
  "success": true,
  "kanban": [
    {
      "status": "todo",
      "title": "📝 TODO",
      "color": "yellow",
      "task_count": 3,
      "tasks": [
        {
          "task_id": "TASK-001",
          "title": "Implement feature X",
          "priority": "high",
          "created_date": "2025-01-27",
          "due_date": "2025-02-01",
          "assignee": "Developer",
          "task_type": "Development",
          "tags": ["feature", "api"]
        }
      ]
    }
  ],
  "total_tasks": 15
}
```

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., indexing already in progress)
- `500 Internal Server Error` - Server error

## Task Status Values

- `backlog` - Task is in the backlog
- `todo` - Task is ready to be worked on
- `inprogress` - Task is currently being worked on
- `testing` - Task is being tested
- `devdone` - Development is complete
- `done` - Task is fully completed

## Task Priority Values

- `low` - Low priority
- `medium` - Medium priority
- `high` - High priority
- `critical` - Critical priority

## Error Handling

All endpoints return appropriate HTTP status codes and error messages in the response body when errors occur.

Example error response:
```json
{
  "success": false,
  "error": "Task not found: TASK-999"
}
```

## CORS Support

The API supports Cross-Origin Resource Sharing (CORS) for web applications. By default, it allows requests from localhost only. Set the `HTTP_ALLOW_ALL_ORIGINS` environment variable to `true` to allow requests from any origin.

## MCP Integration

The API is integrated with Model Context Protocol (MCP) servers that provide tools for Claude and other AI assistants to interact with TaskHero AI functionality.

### Starting the MCP Server

```bash
# Start the HTTP API server first
python start_http_server.py --port 8000

# Start the MCP server (in a new terminal)
python mcp_server.py
```

### Available MCP Tools

#### Code Analysis Tools
- `initialize_directory(directory_path)` - Initialize a directory for code analysis
- `ask_agent(question)` - Ask the AI agent questions about the codebase
- `start_indexing(directory_path)` - Start indexing a directory
- `get_indexing_status()` - Get the status of the indexing process
- `health_check()` - Check if the HTTP API server is running

#### Task Management Tools
- `get_all_tasks()` - Get all tasks organized by status
- `create_task(title, content, priority, status)` - Create a new task
- `get_task_details(task_id)` - Get detailed information about a specific task
- `update_task_status(task_id, new_status)` - Update the status of a task
- `get_kanban_board()` - Get kanban board data with visual organization

#### Utility Tools
- `start_http_server_tool(port)` - Start the HTTP API server if not running
- `set_api_url(url)` - Configure the API URL for the MCP server

### Claude Desktop Integration

To use with Claude Desktop, add this configuration to your `mcp_servers.json`:

```json
{
  "mcpServers": {
    "TaskHeroAI": {
      "command": "YOUR_VENV_PATH\\Scripts\\python.exe",
      "args": ["PATH_TO_TASKHEROAI\\mcp_server.py"]
    }
  }
}
```

### Example MCP Usage

```
User: Can you help me analyze my Python project?

Claude: I'll help you analyze your Python project using TaskHero AI. Let me start by checking if the server is running and then initialize your project.

[Tool: health_check]
Result: {"status": "ok", "message": "HTTP API server is running"}

Great! The server is running. Now let me initialize your project directory.

[Tool: initialize_directory]
Input: {"directory_path": "/path/to/your/project"}
Result: {"status": "ok", "message": "Directory initialized successfully"}

Now I'll start indexing your project to analyze the codebase.

[Tool: start_indexing]
Input: {"directory_path": "/path/to/your/project"}
Result: {"status": "ok", "message": "Indexing started"}

The indexing has started. Once it's complete, I can help you with code analysis, task management, and answer questions about your project structure.
```
