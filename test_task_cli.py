#!/usr/bin/env python
"""
Test script for TaskCLI module functionality.
"""

from mods.cli.task_cli import TaskCLI


def test_task_cli():
    """Test TaskCLI basic functionality."""
    print("🧪 Testing TaskCLI Module")
    print("=" * 40)
    
    # Initialize TaskCLI
    task_cli = TaskCLI()
    print("✅ TaskCLI initialized successfully")
    
    # Test quick create (non-interactive)
    print("\n🚀 Testing quick task creation...")
    task = task_cli.quick_create(
        title="Test TASK-005 Enhanced CLI Integration --priority high #testing #cli",
        description="Testing the new TaskCLI functionality"
    )
    
    if task:
        print(f"✅ Task created: {task.task_id} - {task.title}")
        print(f"   Priority: {task.priority.value}")
        print(f"   Status: {task.status.value}")
    else:
        print("❌ Failed to create task")
        return False
    
    # Test task summary
    print("\n📊 Testing task summary...")
    all_tasks = task_cli.task_manager.get_all_tasks()
    task_cli._show_task_summary(all_tasks)
    
    print("\n🎉 TaskCLI basic functionality test complete!")
    return True


if __name__ == "__main__":
    test_task_cli() 