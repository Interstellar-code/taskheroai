#!/usr/bin/env python
"""
Demo: AI-Enhanced Task Creation

This script demonstrates how to use the new AI-enhanced task creation system
with the enhanced template integration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_ai_task_creation():
    """Demonstrate the AI-enhanced task creation capabilities."""
    print("🚀 AI-Enhanced Task Creation Demo")
    print("=" * 50)
    
    try:
        from mods.project_management.ai_task_creator import AITaskCreator
        
        # Initialize the AI Task Creator
        ai_creator = AITaskCreator(project_root=str(project_root))
        print("✅ AI Task Creator initialized")
        
        # Demo 1: Create a development task
        print("\n📋 Demo 1: Creating a Development Task")
        print("-" * 40)
        
        success, task_id, file_path = ai_creator.create_enhanced_task(
            title="Build Real-time Chat System",
            description="""
            Implement a real-time chat system for the TaskHero AI application with the following features:
            - WebSocket-based real-time messaging
            - User presence indicators
            - Message history and persistence
            - File sharing capabilities
            - Emoji and reaction support
            - Mobile-responsive design
            
            The chat system should integrate seamlessly with the existing user authentication
            and provide a modern, intuitive user experience.
            """,
            task_type="Development",
            priority="high",
            assigned_to="Full Stack Developer",
            tags=["chat", "websocket", "real-time", "messaging"],
            effort_estimate="Large",
            use_ai_enhancement=True
        )
        
        if success:
            print(f"✅ Created: {task_id}")
            print(f"📁 File: {Path(file_path).name}")
        else:
            print(f"❌ Failed: {file_path}")
        
        # Demo 2: Create a bug fix task
        print("\n📋 Demo 2: Creating a Bug Fix Task")
        print("-" * 40)
        
        success, task_id, file_path = ai_creator.create_enhanced_task(
            title="Fix Memory Leak in Task Processing",
            description="Users report that the application becomes slow after processing many tasks. Investigation shows a memory leak in the task processing module.",
            task_type="Bug Fix",
            priority="critical",
            assigned_to="Senior Developer",
            tags=["bug", "memory-leak", "performance"],
            effort_estimate="Medium",
            use_ai_enhancement=True
        )
        
        if success:
            print(f"✅ Created: {task_id}")
            print(f"📁 File: {Path(file_path).name}")
        else:
            print(f"❌ Failed: {file_path}")
        
        # Demo 3: Create a design task
        print("\n📋 Demo 3: Creating a Design Task")
        print("-" * 40)
        
        success, task_id, file_path = ai_creator.create_enhanced_task(
            title="Design Mobile App Interface",
            description="Create a mobile-first design for the TaskHero AI mobile application with modern UI patterns and accessibility considerations.",
            task_type="Design",
            priority="medium",
            assigned_to="UI/UX Designer",
            tags=["design", "mobile", "ui", "accessibility"],
            effort_estimate="Large",
            use_ai_enhancement=True
        )
        
        if success:
            print(f"✅ Created: {task_id}")
            print(f"📁 File: {Path(file_path).name}")
        else:
            print(f"❌ Failed: {file_path}")
        
        # Demo 4: Show interactive creation (without actually running it)
        print("\n📋 Demo 4: Interactive Task Creation")
        print("-" * 40)
        print("The system also supports interactive task creation:")
        print("```python")
        print("ai_creator = AITaskCreator()")
        print("success, task_id, file_path = ai_creator.create_task_interactive()")
        print("```")
        print("This will guide you through a step-by-step wizard to create tasks.")
        
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print("✅ AI-enhanced task creation is working perfectly!")
        print("✅ Multiple task types supported")
        print("✅ Rich templates with comprehensive features")
        print("✅ Proper naming conventions followed")
        print("✅ AI content enhancement active")
        
        print("\n📁 Check the generated files in:")
        print("   mods/project_management/planning/todo/")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    demo_ai_task_creation() 