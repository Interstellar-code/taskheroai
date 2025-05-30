#!/usr/bin/env python3
"""Test the project analysis functionality."""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_project_analysis():
    """Test the project analysis functionality."""
    try:
        from mods.cli.cli_manager import CLIManager
        from mods.core import ApplicationController
        
        print("🧪 Testing Project Analysis Functionality")
        print("=" * 50)
        
        # Create application controller and initialize it
        app_controller = ApplicationController()
        app_controller.initialize()
        
        if not app_controller.cli_manager:
            print("❌ CLI Manager not initialized")
            return
        
        cli_manager = app_controller.cli_manager
        
        # Check if indexer is available
        if not cli_manager.indexer:
            print("❌ No indexer available - need to index first")
            return
        
        print(f"✅ Indexer available for: {cli_manager.indexer.root_path}")
        
        # Test getting kanban folder path
        kanban_path = cli_manager._get_kanban_folder_path()
        if kanban_path:
            print(f"✅ Kanban folder path: {kanban_path}")
        else:
            print("❌ Could not determine kanban folder path")
            return
        
        # Test functional analysis
        print("\n🔍 Running functional analysis...")
        functional_analysis = cli_manager._analyze_project_functionality()
        
        print(f"✅ Analysis completed!")
        print(f"   - User capabilities: {len(functional_analysis['user_capabilities'])}")
        print(f"   - Core features: {len(functional_analysis['core_features'])}")
        print(f"   - Functional modules: {len(functional_analysis['functional_modules'])}")
        print(f"   - Interfaces: {len(functional_analysis['interfaces'])}")
        print(f"   - Data handling: {len(functional_analysis['data_handling'])}")
        print(f"   - Automation features: {len(functional_analysis['automation_features'])}")
        print(f"   - Integration points: {len(functional_analysis['integration_points'])}")
        
        # Test creating about.md content
        print("\n📝 Generating about.md content...")
        about_content = cli_manager._create_about_md_content(functional_analysis)
        print(f"✅ About.md content generated ({len(about_content)} characters)")
        
        # Test saving the file
        print("\n💾 Testing file save...")
        analysis_dir = os.path.join(kanban_path, "project-analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        
        about_file_path = os.path.join(analysis_dir, "about.md")
        with open(about_file_path, 'w', encoding='utf-8') as f:
            f.write(about_content)
        
        print(f"✅ File saved to: {about_file_path}")
        
        # Show preview of the generated content
        print("\n📖 Preview of generated content:")
        print("-" * 40)
        lines = about_content.split('\n')
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            print(line)
        if len(lines) > 20:
            print(f"... and {len(lines) - 20} more lines")
        
        print("\n🎉 Project analysis test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_project_analysis() 