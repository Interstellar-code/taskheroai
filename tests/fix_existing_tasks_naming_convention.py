#!/usr/bin/env python3
"""
Script to remove naming convention sections from existing tasks.
This fixes tasks that were generated before the TASK-044 improvements.
"""

import os
import re
from pathlib import Path

def remove_naming_convention_section(file_path):
    """Remove the naming convention section from a task file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match the entire naming convention section
        pattern = r'## Task Naming Convention\n.*?(?=## \d+\. Overview|$)'
        
        # Remove the section
        cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Clean up any extra newlines
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
        
        # Write back the cleaned content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def fix_existing_tasks():
    """Fix all existing tasks by removing naming convention sections."""
    print("🔧 Fixing Existing Tasks - Removing Naming Convention Sections")
    print("=" * 60)
    
    # Find all task files
    task_dirs = [
        "mods/project_management/planning/todo",
        "mods/project_management/planning/inprogress",
        "mods/project_management/planning/testing",
        "mods/project_management/planning/done"
    ]
    
    fixed_count = 0
    total_count = 0
    
    for task_dir in task_dirs:
        task_path = Path(task_dir)
        if task_path.exists():
            for task_file in task_path.glob("TASK-*.md"):
                total_count += 1
                print(f"Processing: {task_file.name}")
                
                # Check if file contains naming convention section
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "## Task Naming Convention" in content:
                    if remove_naming_convention_section(task_file):
                        print(f"  ✅ Fixed: Removed naming convention section")
                        fixed_count += 1
                    else:
                        print(f"  ❌ Failed to fix")
                else:
                    print(f"  ℹ️  No naming convention section found")
    
    print(f"\n📊 Summary:")
    print(f"   Total tasks processed: {total_count}")
    print(f"   Tasks fixed: {fixed_count}")
    print(f"   Tasks already clean: {total_count - fixed_count}")
    
    return fixed_count

if __name__ == "__main__":
    fix_existing_tasks() 