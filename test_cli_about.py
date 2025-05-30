#!/usr/bin/env python3
"""
Test script for CLI about generation functionality
"""

import sys
import os
from pathlib import Path
import traceback

# Add the current directory to Python path for absolute imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_cli_about_generation():
    """Test the CLI about generation functionality."""
    print("🧪 Testing CLI About Generation")
    print("=" * 40)
    
    try:
        from mods.project_management.about_manager import AboutManager
        from mods.settings import SettingsManager
        from mods.ai.ai_manager import AIManager
        
        # Initialize components like the CLI would
        settings_manager = SettingsManager()
        ai_manager = AIManager()
        
        about_manager = AboutManager(
            project_root=str(project_root),
            ai_manager=ai_manager,
            settings_manager=settings_manager
        )
        
        print("✅ All managers initialized successfully")
        
        # Test the same method used by CLI
        print("\n📝 Testing CLI about generation method...")
        success, message, file_path = about_manager.create_dynamic_about()
        
        if success:
            print(f"✅ {message}")
            print(f"📁 File saved to: {file_path}")
            
            # Verify file exists and has good content
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for key TaskHero AI specific content
                quality_checks = [
                    'TaskHero AI' in content,
                    'AI-powered' in content or 'AI-Powered' in content,
                    'project management' in content,
                    'development teams' in content,
                    'intelligent' in content,
                    'automation' in content
                ]
                
                passed_checks = sum(quality_checks)
                
                print(f"✅ File content quality: {passed_checks}/{len(quality_checks)} checks passed")
                
                if passed_checks >= 5:
                    print("🎉 CLI about generation works correctly!")
                    return True
                else:
                    print("⚠️ Content quality could be improved")
                    return False
            else:
                print(f"❌ File was not created at {file_path}")
                return False
        else:
            print(f"❌ Failed: {message}")
            return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 CLI About Generation Test")
    print("=" * 35)
    
    success = test_cli_about_generation()
    
    print(f"\n📊 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\n🎉 CLI about generation is working correctly!")
        print("You can now use the main menu option to generate about documents.")
    else:
        print("\n💥 There are issues with CLI about generation.")
    
    sys.exit(0 if success else 1) 