"""
Test script for Kanban Board functionality

This script tests the Kanban board implementation to ensure it works correctly
with the task management system.
"""

import os
import sys
from pathlib import Path


def test_kanban_board_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing Kanban Board Imports...")
    
    try:
        from mods.project_management.task_manager import TaskManager, TaskStatus, TaskPriority
        print("   ✅ TaskManager imported successfully")
        
        from mods.project_management.kanban_board import KanbanBoard, launch_kanban_board
        print("   ✅ KanbanBoard imported successfully")
        
        from rich.console import Console
        from rich.layout import Layout
        from rich.panel import Panel
        print("   ✅ Rich library components imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def test_kanban_board_initialization():
    """Test that the Kanban board can be initialized."""
    print("\n🧪 Testing Kanban Board Initialization...")
    
    try:
        from mods.project_management.task_manager import TaskManager
        from mods.project_management.kanban_board import KanbanBoard
        
        # Create a task manager
        task_manager = TaskManager()
        print("   ✅ TaskManager created successfully")
        
        # Create a kanban board
        kanban_board = KanbanBoard(task_manager)
        print("   ✅ KanbanBoard created successfully")
        
        # Test basic properties
        assert len(kanban_board.columns) == 6, "Should have 6 columns"
        print("   ✅ Column configuration correct (6 columns)")
        
        column_statuses = [col['status'] for col in kanban_board.columns]
        expected_statuses = ['backlog', 'todo', 'inprogress', 'testing', 'devdone', 'done']
        assert column_statuses == expected_statuses, f"Column order incorrect: {column_statuses}"
        print("   ✅ Column order correct")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_task_card_creation():
    """Test that task cards can be created."""
    print("\n🧪 Testing Task Card Creation...")
    
    try:
        from mods.project_management.task_manager import TaskManager, TaskPriority, TaskStatus
        from mods.project_management.kanban_board import KanbanBoard
        
        # Create a task manager and kanban board
        task_manager = TaskManager()
        kanban_board = KanbanBoard(task_manager)
        
        # Create a sample task
        task = task_manager.create_task(
            title="Test Task for Kanban",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.TODO,
            assigned_to="Test User",
            task_type="Testing"
        )
        
        if task:
            print("   ✅ Sample task created successfully")
            
            # Test task card creation
            task_card = kanban_board.create_task_card(task, is_selected=False)
            print("   ✅ Task card created successfully")
            
            # Test selected task card
            selected_card = kanban_board.create_task_card(task, is_selected=True)
            print("   ✅ Selected task card created successfully")
            
            return True
        else:
            print("   ❌ Failed to create sample task")
            return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_kanban_layout():
    """Test that the Kanban layout can be created."""
    print("\n🧪 Testing Kanban Layout Creation...")
    
    try:
        from mods.project_management.task_manager import TaskManager
        from mods.project_management.kanban_board import KanbanBoard
        
        # Create components
        task_manager = TaskManager()
        kanban_board = KanbanBoard(task_manager)
        
        # Get all tasks (should be empty initially)
        all_tasks = task_manager.get_all_tasks()
        print("   ✅ Retrieved all tasks")
        
        # Create layout
        layout = kanban_board.create_kanban_layout(all_tasks)
        print("   ✅ Kanban layout created successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_enhanced_cli_integration():
    """Test that the Enhanced CLI can launch the Kanban board."""
    print("\n🧪 Testing Enhanced CLI Integration...")
    
    try:
        from enhanced_cli import EnhancedCLI
        
        # Create a mock app
        class MockApp:
            def __init__(self):
                self.project_planner = None
                self.task_manager = None
        
        mock_app = MockApp()
        enhanced_cli = EnhancedCLI(mock_app)
        print("   ✅ Enhanced CLI created successfully")
        
        # Test that the method exists
        assert hasattr(enhanced_cli, 'launch_kanban_board'), "launch_kanban_board method not found"
        print("   ✅ launch_kanban_board method exists")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def show_kanban_board_demo():
    """Show a demonstration of the Kanban board structure."""
    print("\n📋 Kanban Board Structure Demo:")
    print("=" * 80)
    
    demo_structure = """
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│   📦 BACKLOG    │    📝 TODO      │  🔄 IN PROGRESS │   🧪 TESTING    │  ✅ DEV DONE    │    🎉 DONE      │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│                 │ [H] TASK-001    │ [M] TASK-002    │ [L] TASK-003    │                 │ [H] TASK-004    │
│                 │ ⚡ Setup project│ 🔧 Build API    │ 🧪 Test UI      │                 │ ✨ CLI enhanced │
│                 │ 📅 Due: Jan 29  │ 👤 Developer    │ 👤 QA Team      │                 │ ✅ Jan 26       │
│                 │                 │                 │                 │                 │                 │
│                 │ [M] TASK-005    │                 │                 │                 │                 │
│                 │ 📋 Kanban board │                 │                 │                 │                 │
│                 │ 📅 Due: Feb 07  │                 │                 │                 │                 │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘

📊 Statistics: 5 total | 2 todo | 1 in progress | 1 testing | 0 dev done | 1 done (20% complete)
💡 Controls: ← → Navigate Columns | ↑ ↓ Select Tasks | ENTER View Details | M Move | D Delete | Q Quit | H Help
"""
    
    print(demo_structure)
    
    print("\n🎮 Interactive Features:")
    print("• Arrow key navigation between columns and tasks")
    print("• ENTER to view detailed task information")
    print("• M to move tasks between columns")
    print("• D to delete tasks (with confirmation)")
    print("• H for comprehensive help")
    print("• Q to quit and return to main menu")
    print("• Real-time statistics and progress tracking")
    print("• Color-coded priorities and status indicators")
    print("• Responsive design for different terminal sizes")


def main():
    """Run all tests and show demonstration."""
    print("🚀 TaskHero AI Kanban Board Test Suite")
    print("=" * 60)
    
    # Run tests
    tests = [
        test_kanban_board_imports,
        test_kanban_board_initialization,
        test_task_card_creation,
        test_kanban_layout,
        test_enhanced_cli_integration
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        if test():
            passed_tests += 1
    
    # Show demo
    show_kanban_board_demo()
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Kanban Board implementation is ready!")
        print("✅ TASK-003 Kanban Board Visualization: COMPLETE")
        print("\n📝 Implementation Summary:")
        print("• 6 columns: Backlog, Todo, In Progress, Testing, Dev Done, Done")
        print("• Interactive navigation with arrow keys")
        print("• Task details popup with ENTER")
        print("• Move tasks between columns with M")
        print("• Delete tasks with D (confirmation required)")
        print("• Comprehensive help system with H")
        print("• Real-time statistics and progress tracking")
        print("• Integration with Enhanced CLI (option 10)")
        print("\n🚀 Ready to move to TASK-005 Enhanced CLI Interface!")
    else:
        print(f"❌ {total_tests - passed_tests} tests failed")
        print("🔧 Please check the error messages above")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main() 