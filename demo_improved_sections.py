#!/usr/bin/env python3
"""
Demo script to show improved section reporting
"""

import sys
from pathlib import Path

# Add the current directory to Python path for absolute imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_section_reporting():
    """Demonstrate the improved section reporting."""
    print("🚀 TaskHero AI About Generation - Improved Section Reporting Demo")
    print("=" * 70)
    
    try:
        from mods.project_management.about_manager import AboutManager
        
        print("📝 Creating AboutManager instance...")
        about_manager = AboutManager(str(project_root))
        
        print("✅ AboutManager initialized successfully")
        print("\n🎯 Starting dynamic about generation with improved section reporting...")
        print("=" * 70)
        
        # Generate about document
        success, message, file_path = about_manager.create_dynamic_about()
        
        if success:
            print(f"\n✅ {message}")
            print(f"📁 File saved to: {file_path}")
            
            # Check the generated file
            if file_path and Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n📊 Generated Content Summary:")
                print(f"   Content Length: {len(content):,} characters")
                print(f"   Section Count: {content.count('## ')}")
                print(f"   Contains TaskHero AI: {'✅ Yes' if 'TaskHero AI' in content else '❌ No'}")
                print(f"   Contains AI-powered: {'✅ Yes' if 'AI-powered' in content or 'AI-Powered' in content else '❌ No'}")
                
                # Show first few lines
                lines = content.split('\n')[:10]
                print(f"\n📋 Content Preview (first 10 lines):")
                for i, line in enumerate(lines, 1):
                    print(f"   {i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
            else:
                print(f"⚠️ Generated file not found at {file_path}")
        else:
            print(f"❌ Generation failed: {message}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_section_reporting()
    
    print(f"\n📊 Demo Result: {'✅ SUCCESS' if success else '❌ FAILURE'}")
    
    if success:
        print("\n🎉 The improved section reporting is working!")
        print("Notice how each section is now clearly labeled with its number and purpose.")
    else:
        print("\n💥 Demo failed. Please check the error messages above.")
    
    sys.exit(0 if success else 1) 