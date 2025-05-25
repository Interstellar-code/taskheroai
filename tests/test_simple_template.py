#!/usr/bin/env python3
"""
Simple Test to Isolate Template Syntax Issues
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from mods.project_management.template_engine import TemplateEngine
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_template_syntax():
    """Test template syntax by loading it directly with Jinja2."""
    print("🧪 Testing Enhanced Task Template Syntax...")
    
    template_path = project_root / "mods/project_management/templates"
    
    try:
        # Create Jinja2 environment
        env = Environment(loader=FileSystemLoader(str(template_path)))
        
        # Try to load the template
        template = env.get_template("tasks/enhanced_task.j2")
        print("✅ Template loaded successfully")
        
        # Simple context
        context = {
            'task_id': 'TASK-001',
            'title': 'Test Task',
            'priority': 'High',
            'status': 'Draft',
            'assignee': 'Developer',
            'task_type': 'DEV',
            'current_date': '2025-01-28'
        }
        
        # Try to render
        rendered = template.render(context)
        print("✅ Template rendered successfully")
        print("📄 First 10 lines:")
        lines = rendered.split('\n')[:10]
        for i, line in enumerate(lines, 1):
            print(f"   {i:2}: {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template syntax error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simple syntax test."""
    print("🚀 Simple Template Syntax Test")
    print("=" * 40)
    
    if test_template_syntax():
        print("🎉 Template syntax is correct!")
    else:
        print("⚠️ Template has syntax errors")

if __name__ == "__main__":
    main() 