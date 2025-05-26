#!/usr/bin/env python3
"""
Simple API test that starts the server and tests it.
"""

import asyncio
import threading
import time
import requests
import uvicorn
from mods.http_api import create_app

def run_server():
    """Run the HTTP server in a separate thread."""
    app = create_app(allow_all_origins=False)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def test_api():
    """Test the API endpoints."""
    print("🚀 Testing TaskHero AI HTTP API")
    print("=" * 40)
    
    # Start server in background thread
    print("🔧 Starting HTTP server...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test health endpoint
        print("\n🔍 Testing health endpoint...")
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('service', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test get all tasks
        print("\n🔍 Testing get all tasks...")
        response = requests.get("http://localhost:8000/api/tasks", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                tasks = data.get("tasks", {})
                total_tasks = sum(len(task_list) for task_list in tasks.values())
                print(f"✅ Get all tasks passed: {total_tasks} tasks found")
            else:
                print(f"❌ Get all tasks failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Get all tasks failed: {response.status_code}")
        
        # Test create task
        print("\n🔍 Testing create task...")
        task_data = {
            "title": "API Test Task",
            "content": "This is a test task created via HTTP API",
            "priority": "medium",
            "status": "todo"
        }
        response = requests.post("http://localhost:8000/api/tasks", json=task_data, timeout=10)
        if response.status_code == 201:
            data = response.json()
            if data.get("success"):
                task = data.get("task", {})
                task_id = task.get("task_id")
                print(f"✅ Create task passed: {task_id}")
                
                # Test get task details
                print(f"\n🔍 Testing get task details for {task_id}...")
                response = requests.get(f"http://localhost:8000/api/tasks/{task_id}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        task = data.get("task", {})
                        print(f"✅ Get task details passed: {task.get('title', 'Unknown')}")
                    else:
                        print(f"❌ Get task details failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ Get task details failed: {response.status_code}")
                
                # Test update task status
                print(f"\n🔍 Testing update task status for {task_id}...")
                status_data = {"status": "inprogress"}
                response = requests.put(f"http://localhost:8000/api/tasks/{task_id}/status", json=status_data, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        task = data.get("task", {})
                        print(f"✅ Update task status passed: {task.get('status', 'Unknown')}")
                    else:
                        print(f"❌ Update task status failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ Update task status failed: {response.status_code}")
            else:
                print(f"❌ Create task failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Create task failed: {response.status_code}")
        
        # Test kanban board
        print("\n🔍 Testing kanban board...")
        response = requests.get("http://localhost:8000/api/kanban", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                kanban = data.get("kanban", [])
                total_tasks = data.get("total_tasks", 0)
                print(f"✅ Kanban board passed: {len(kanban)} columns, {total_tasks} tasks")
            else:
                print(f"❌ Kanban board failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Kanban board failed: {response.status_code}")
        
        print("\n🎉 API testing completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    test_api()
