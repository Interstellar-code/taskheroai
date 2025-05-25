#!/usr/bin/env python
"""
Test script to verify project management foundation works correctly.
"""

from mods.project_management.task_manager import TaskManager, TaskStatus, TaskPriority
from mods.project_management.kanban_board import KanbanBoard
from mods.project_management.project_planner import ProjectPlanner

def test_task_manager():
    """Test TaskManager functionality."""
    print("🔧 Testing TaskManager...")
    
    # Initialize TaskManager
    task_manager = TaskManager()
    
    # Create a test task
    task = task_manager.create_task(
        title="Test Enhanced CLI Integration",
        content="This is a test task to verify project management foundation works.",
        priority=TaskPriority.HIGH,
        status=TaskStatus.TODO
    )
    
    if task:
        print(f"✅ Created task: {task.task_id} - {task.title}")
        print(f"   Status: {task.status.value}")
        print(f"   Priority: {task.priority.value}")
    else:
        print("❌ Failed to create task")
        return False
    
    # Test getting all tasks
    all_tasks = task_manager.get_all_tasks()
    print(f"📊 Total tasks by status:")
    for status, tasks in all_tasks.items():
        print(f"   {status}: {len(tasks)} tasks")
    
    return True

def test_kanban_board():
    """Test KanbanBoard functionality."""
    print("\n🎯 Testing KanbanBoard...")
    
    # Initialize TaskManager and KanbanBoard
    task_manager = TaskManager()
    kanban_board = KanbanBoard(task_manager)
    
    print(f"✅ KanbanBoard initialized with {len(kanban_board.columns)} columns")
    print("📋 Available columns:")
    for col in kanban_board.columns:
        print(f"   - {col['title']} ({col['status']})")
    
    return True

def test_project_planner():
    """Test ProjectPlanner functionality."""
    print("\n📋 Testing ProjectPlanner...")
    
    try:
        project_planner = ProjectPlanner()
        print("✅ ProjectPlanner initialized successfully")
        
        # Check if it has a task manager
        if hasattr(project_planner, 'task_manager'):
            print("✅ ProjectPlanner has TaskManager integration")
        else:
            print("⚠️  ProjectPlanner missing TaskManager integration")
            
        return True
    except Exception as e:
        print(f"❌ Error initializing ProjectPlanner: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Project Management Foundation")
    print("=" * 50)
    
    results = []
    
    # Test TaskManager
    results.append(("TaskManager", test_task_manager()))
    
    # Test KanbanBoard
    results.append(("KanbanBoard", test_kanban_board()))
    
    # Test ProjectPlanner
    results.append(("ProjectPlanner", test_project_planner()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    all_passed = True
    for component, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {component}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Foundation is ready for enhanced CLI integration.")
    else:
        print("\n⚠️  Some tests failed. Need to fix foundation before proceeding.")
    
    return all_passed

if __name__ == "__main__":
    main() 