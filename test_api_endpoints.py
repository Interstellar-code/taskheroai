#!/usr/bin/env python3
"""
Test script for TaskHero AI HTTP API endpoints.

This script tests the new task management API endpoints to ensure they work correctly.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def test_health_check() -> bool:
    """Test the health check endpoint."""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('service', 'Unknown service')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_get_all_tasks() -> bool:
    """Test getting all tasks."""
    print("\n🔍 Testing get all tasks endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/tasks", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                tasks = data.get("tasks", {})
                total_tasks = sum(len(task_list) for task_list in tasks.values())
                print(f"✅ Get all tasks passed: Found {total_tasks} tasks across {len(tasks)} statuses")

                # Show task counts by status
                for status, task_list in tasks.items():
                    if task_list:
                        print(f"   📋 {status}: {len(task_list)} tasks")
                return True
            else:
                print(f"❌ Get all tasks failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Get all tasks failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get all tasks failed: {e}")
        return False

def test_create_task() -> str:
    """Test creating a new task. Returns task_id if successful."""
    print("\n🔍 Testing create task endpoint...")
    try:
        task_data = {
            "title": "API Test Task",
            "content": "This is a test task created via the HTTP API",
            "priority": "medium",
            "status": "todo"
        }

        response = requests.post(f"{API_BASE_URL}/api/tasks", json=task_data, timeout=10)
        if response.status_code == 201:
            data = response.json()
            if data.get("success"):
                task = data.get("task", {})
                task_id = task.get("task_id")
                print(f"✅ Create task passed: Created task {task_id}")
                return task_id
            else:
                print(f"❌ Create task failed: {data.get('error', 'Unknown error')}")
                return ""
        else:
            print(f"❌ Create task failed with status {response.status_code}")
            return ""
    except requests.exceptions.RequestException as e:
        print(f"❌ Create task failed: {e}")
        return ""

def test_get_task_details(task_id: str) -> bool:
    """Test getting task details."""
    print(f"\n🔍 Testing get task details endpoint for {task_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/tasks/{task_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                task = data.get("task", {})
                print(f"✅ Get task details passed: {task.get('title', 'Unknown title')}")
                return True
            else:
                print(f"❌ Get task details failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Get task details failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get task details failed: {e}")
        return False

def test_update_task_status(task_id: str) -> bool:
    """Test updating task status."""
    print(f"\n🔍 Testing update task status endpoint for {task_id}...")
    try:
        status_data = {"status": "inprogress"}

        response = requests.put(f"{API_BASE_URL}/api/tasks/{task_id}/status", json=status_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                task = data.get("task", {})
                new_status = task.get("status")
                print(f"✅ Update task status passed: Status changed to {new_status}")
                return True
            else:
                print(f"❌ Update task status failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Update task status failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Update task status failed: {e}")
        return False

def test_get_kanban_board() -> bool:
    """Test getting kanban board data."""
    print("\n🔍 Testing get kanban board endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/kanban", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                kanban = data.get("kanban", [])
                total_tasks = data.get("total_tasks", 0)
                print(f"✅ Get kanban board passed: {len(kanban)} columns, {total_tasks} total tasks")

                # Show column information
                for column in kanban:
                    status = column.get("status")
                    title = column.get("title")
                    task_count = column.get("task_count", 0)
                    print(f"   📋 {title}: {task_count} tasks")
                return True
            else:
                print(f"❌ Get kanban board failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Get kanban board failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get kanban board failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("🚀 TaskHero AI HTTP API Test Suite")
    print("=" * 50)

    # Check if server is running
    if not test_health_check():
        print("\n❌ API server is not running. Please start the server first:")
        print("   Option 1 (Direct): python start_http_server.py --port 8000")
        print("   Option 2 (MCP):    python start_http_server.py --port 8000 --method mcp")
        print("   Option 3 (MCP):    python mcp_server.py")
        print("\nNote: HTTP API functionality has been moved to separate modules.")
        sys.exit(1)

    # Run tests
    tests_passed = 0
    total_tests = 0

    # Test 1: Get all tasks
    total_tests += 1
    if test_get_all_tasks():
        tests_passed += 1

    # Test 2: Create a task
    total_tests += 1
    task_id = test_create_task()
    if task_id:
        tests_passed += 1

        # Test 3: Get task details (only if create succeeded)
        total_tests += 1
        if test_get_task_details(task_id):
            tests_passed += 1

        # Test 4: Update task status (only if create succeeded)
        total_tests += 1
        if test_update_task_status(task_id):
            tests_passed += 1
    else:
        total_tests += 2  # Skip dependent tests

    # Test 5: Get kanban board
    total_tests += 1
    if test_get_kanban_board():
        tests_passed += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! The HTTP API is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the API implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
