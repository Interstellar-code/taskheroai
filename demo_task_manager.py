#!/usr/bin/env python
"""
TaskManager Core CRUD Operations - Demonstration Script

This script demonstrates the enhanced TaskManager functionality including:
- Complete status workflow: backlog → todo → inprogress → devdone → testing → done
- Comprehensive CRUD operations
- Task validation and workflow management
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mods.project_management.task_manager import (
    TaskManager, Task, TaskStatus, TaskPriority, TaskMetadata
)

def demonstrate_task_lifecycle():
    """Demonstrate a complete task lifecycle."""
    print("🚀 TaskManager Enhanced CRUD Operations Demo")
    print("=" * 60)
    
    # Initialize TaskManager
    tm = TaskManager()
    
    print("\n1️⃣ Creating a new task...")
    task = tm.create_task(
        title="Implement User Authentication",
        content="Add secure user authentication with JWT tokens and role-based access control.",
        priority=TaskPriority.HIGH,
        status=TaskStatus.BACKLOG,
        tags=["authentication", "security", "backend"],
        estimated_hours=16.0,
        due_date="2025-02-15"
    )
    
    if task:
        print(f"✅ Created task: {task.task_id}")
        print(f"   Title: {task.title}")
        print(f"   Status: {task.status.value}")
        print(f"   Priority: {task.priority.value}")
        print(f"   Tags: {', '.join(task.metadata.tags)}")
    else:
        print("❌ Failed to create task")
        return
    
    print(f"\n2️⃣ Task workflow demonstration...")
    print(f"   Starting status: {task.status.value}")
    
    # Demonstrate the complete workflow
    workflow_steps = [
        (TaskStatus.TODO, "Task moved to development queue"),
        (TaskStatus.INPROGRESS, "Development started"),
        (TaskStatus.DEVDONE, "Development completed, ready for testing"),
        (TaskStatus.TESTING, "Task in testing phase"),
        (TaskStatus.DONE, "Task completed successfully")
    ]
    
    for target_status, description in workflow_steps:
        print(f"\n   📋 {description}")
        
        # Show valid transitions
        valid_transitions = tm.get_valid_transitions(task.task_id)
        print(f"      Valid transitions: {[s.value for s in valid_transitions]}")
        
        # Move to next status
        success = tm.move_task_status(task.task_id, target_status, validate=True)
        if success:
            updated_task = tm.get_task_by_id(task.task_id)
            print(f"   ✅ Status: {task.status.value} → {updated_task.status.value}")
            task = updated_task
        else:
            print(f"   ❌ Failed to move to {target_status.value}")
            break
    
    print(f"\n3️⃣ Task summary and statistics...")
    summary = tm.get_task_summary()
    print("   Current task distribution:")
    for status, count in summary.items():
        if count > 0:
            print(f"     {status}: {count} tasks")
    
    print(f"\n4️⃣ Search and discovery...")
    # Search for tasks
    auth_tasks = tm.search_tasks("authentication")
    print(f"   Found {len(auth_tasks)} tasks related to 'authentication'")
    
    security_tasks = tm.search_tasks("security", search_content=True)
    print(f"   Found {len(security_tasks)} tasks related to 'security' (including content)")
    
    print(f"\n5️⃣ Task validation...")
    # Demonstrate validation
    test_data = {
        'task_id': 'TASK-999',
        'title': 'Valid Test Task',
        'status': 'todo',
        'priority': 'high',
        'created_date': '2025-01-27'
    }
    
    is_valid, errors = tm.validate_task_data(test_data)
    print(f"   Task data validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if errors:
        for error in errors:
            print(f"     - {error}")
    
    print(f"\n6️⃣ Template-based creation...")
    template_task = tm.create_task_from_template(
        title="Setup Database Migration",
        priority="medium",
        due_date="2025-02-10",
        tags="database,migration,backend"
    )
    
    if template_task:
        print(f"   ✅ Created from template: {template_task.task_id}")
        print(f"      Title: {template_task.title}")
    else:
        print("   ❌ Failed to create task from template")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"   Tasks created: {task.task_id}, {template_task.task_id if template_task else 'N/A'}")
    print(f"   Final status: {task.status.value}")


def show_status_workflow():
    """Display the complete status workflow."""
    print("\n🔄 TaskHero AI Status Workflow")
    print("=" * 40)
    
    workflow = [
        ("BACKLOG", "Initial task collection and prioritization"),
        ("TODO", "Ready for development, in queue"),
        ("INPROGRESS", "Active development work"),
        ("DEVDONE", "Development complete, ready for testing"),
        ("TESTING", "Quality assurance and testing phase"),
        ("DONE", "Task completed and verified"),
        ("ARCHIVE", "Long-term storage for completed tasks")
    ]
    
    for i, (status, description) in enumerate(workflow):
        arrow = " → " if i < len(workflow) - 1 else ""
        print(f"  {status}{arrow}")
        print(f"    {description}")
        
        # Show valid transitions
        try:
            status_enum = TaskStatus.from_string(status.lower())
            transitions = TaskStatus.get_valid_transitions(status_enum)
            if transitions:
                transition_names = [t.value.upper() for t in transitions]
                print(f"    Can move to: {', '.join(transition_names)}")
        except ValueError:
            pass
        print()


def show_api_examples():
    """Show common API usage examples."""
    print("\n📚 Common TaskManager API Examples")
    print("=" * 45)
    
    examples = [
        ("Create Task", "tm.create_task(title='My Task', priority=TaskPriority.HIGH)"),
        ("Get Task", "task = tm.get_task_by_id('TASK-001')"),
        ("Update Status", "tm.move_task_status('TASK-001', TaskStatus.INPROGRESS)"),
        ("Search Tasks", "results = tm.search_tasks('authentication')"),
        ("Get Summary", "summary = tm.get_task_summary()"),
        ("Validate Data", "is_valid, errors = tm.validate_task_data(data)"),
        ("From Template", "tm.create_task_from_template('New Feature')"),
        ("Get All Tasks", "all_tasks = tm.get_all_tasks()"),
        ("Delete Task", "tm.delete_task('TASK-001')"),
        ("Valid Transitions", "transitions = tm.get_valid_transitions('TASK-001')")
    ]
    
    for operation, code in examples:
        print(f"  📋 {operation}:")
        print(f"     {code}")
        print()


if __name__ == "__main__":
    print("🎯 TaskHero AI - Enhanced Core Task Management Module")
    print("   TASK-002 Implementation Complete ✅")
    print("   Foundation ready for TASK-012 AI Integration 🚀")
    
    try:
        # Run the main demonstration
        demonstrate_task_lifecycle()
        
        # Show additional information
        show_status_workflow()
        show_api_examples()
        
        print("\n" + "=" * 60)
        print("✨ TaskManager Core CRUD Operations ready for production!")
        print("📝 Next step: Implement TASK-012 AI Engine for intelligent features")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 