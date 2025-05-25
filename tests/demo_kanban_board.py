"""
Demo script to launch the Kanban Board directly

This script demonstrates how to use the Kanban board functionality.
"""

import os
import sys
from pathlib import Path


def create_sample_tasks():
    """Create some sample tasks for demonstration."""
    print("📝 Creating sample tasks for demonstration...")
    
    try:
        from mods.project_management.task_manager import TaskManager, TaskPriority, TaskStatus
        
        task_manager = TaskManager()
        
        # Create sample tasks
        sample_tasks = [
            {
                "title": "Set up project structure",
                "priority": TaskPriority.HIGH,
                "status": TaskStatus.DONE,
                "assigned_to": "Developer",
                "task_type": "Setup"
            },
            {
                "title": "Implement Kanban board visualization",
                "priority": TaskPriority.MEDIUM,
                "status": TaskStatus.TESTING,
                "assigned_to": "Developer",
                "task_type": "Development"
            },
            {
                "title": "Enhance CLI interface",
                "priority": TaskPriority.MEDIUM,
                "status": TaskStatus.TODO,
                "assigned_to": "Developer",
                "task_type": "Development"
            },
            {
                "title": "Write comprehensive tests",
                "priority": TaskPriority.LOW,
                "status": TaskStatus.BACKLOG,
                "assigned_to": "QA Team",
                "task_type": "Testing"
            },
            {
                "title": "Create project documentation",
                "priority": TaskPriority.LOW,
                "status": TaskStatus.BACKLOG,
                "assigned_to": "Technical Writer",
                "task_type": "Documentation"
            }
        ]
        
        for task_data in sample_tasks:
            task = task_manager.create_task(
                title=task_data["title"],
                priority=task_data["priority"],
                status=task_data["status"],
                assigned_to=task_data["assigned_to"],
                task_type=task_data["task_type"]
            )
            if task:
                print(f"   ✅ Created: {task.title}")
        
        return task_manager
        
    except Exception as e:
        print(f"   ❌ Error creating sample tasks: {e}")
        return None


def demo_kanban_board():
    """Demonstrate the Kanban board functionality."""
    print("🎯 TaskHero AI Kanban Board Demo")
    print("=" * 50)
    
    # Create sample tasks
    task_manager = create_sample_tasks()
    
    if not task_manager:
        print("❌ Failed to create sample tasks")
        return
    
    print("\n🚀 Launching Kanban Board...")
    print("=" * 50)
    print("📋 Instructions:")
    print("• Use ← → arrow keys to navigate between columns")
    print("• Use ↑ ↓ arrow keys to select tasks within a column")
    print("• Press ENTER to view detailed task information")
    print("• Press M to move tasks between columns")
    print("• Press D to delete tasks (with confirmation)")
    print("• Press H for comprehensive help")
    print("• Press Q to quit and return to this demo")
    print("=" * 50)
    
    input("Press Enter to launch the Kanban board...")
    
    try:
        from mods.project_management.kanban_board import launch_kanban_board
        launch_kanban_board(task_manager)
        
        print("\n✅ Kanban board session completed!")
        
    except Exception as e:
        print(f"❌ Error launching Kanban board: {e}")


def show_features():
    """Show the features of the Kanban board."""
    print("\n🎯 Kanban Board Features:")
    print("=" * 50)
    
    features = [
        "🎨 Rich Terminal UI - Beautiful colors and formatting",
        "📋 6 Columns - Backlog, Todo, In Progress, Testing, Dev Done, Done",
        "🎮 Interactive Navigation - Arrow key controls",
        "📝 Task Cards - Show priority, due dates, assignees, tags",
        "🔍 Task Details - Press ENTER for full information",
        "📦 Move Tasks - Press M to change status/column",
        "🗑️ Delete Tasks - Press D with confirmation",
        "❓ Help System - Press H for comprehensive help",
        "📊 Real-time Stats - Progress tracking and counts",
        "📐 Responsive Design - Adapts to terminal size",
        "🎯 Cross-platform - Works on Windows, Linux, macOS"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n🔧 Technical Details:")
    print("   • Built with Rich library for advanced terminal UI")
    print("   • Integrated with TaskManager for data persistence")
    print("   • Cross-platform keyboard input handling")
    print("   • Graceful error handling and fallbacks")
    print("   • Modular architecture for easy extension")


def main():
    """Main demo function."""
    print("🚀 TaskHero AI - Kanban Board Demo")
    print("=" * 60)
    
    while True:
        print("\n📋 Demo Options:")
        print("1. Launch Kanban Board with sample tasks")
        print("2. Show Kanban Board features")
        print("3. Exit demo")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            demo_kanban_board()
        elif choice == "2":
            show_features()
        elif choice == "3":
            print("\n👋 Thank you for trying the TaskHero AI Kanban Board!")
            print("✅ TASK-003: Kanban Board Visualization - COMPLETE")
            break
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main() 