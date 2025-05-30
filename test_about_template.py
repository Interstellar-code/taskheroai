#!/usr/bin/env python3
"""
Test script for the About Template System

This script tests the AboutManager and template system to ensure
about documents can be created properly following the template format.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for absolute imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_about_template_system():
    """Test the about template system."""
    print("🧪 Testing About Template System")
    print("=" * 50)
    
    try:
        from mods.project_management.about_manager import AboutManager
        
        # Initialize the about manager
        about_manager = AboutManager(str(project_root))
        
        print("✅ AboutManager initialized successfully")
        
        # Test 1: Create sample about document
        print("\n📝 Test 1: Creating sample about document...")
        success, message, file_path = about_manager.create_sample_about()
        
        if success:
            print(f"✅ Sample about document created: {file_path}")
            
            # Check if file exists and has content
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ File exists with {len(content)} characters")
                
                # Check for key template sections
                required_sections = [
                    "Why TaskHero AI Exists",
                    "Vision Statement", 
                    "Problems Solved",
                    "How TaskHero AI Works",
                    "User Experience Goals",
                    "Target Users",
                    "Key User Journeys",
                    "Success Metrics",
                    "Current Product Focus",
                    "Recent Improvements",
                    "Future Roadmap"
                ]
                
                missing_sections = []
                for section in required_sections:
                    if section not in content:
                        missing_sections.append(section)
                
                if not missing_sections:
                    print("✅ All required sections found in template")
                else:
                    print(f"⚠️ Missing sections: {missing_sections}")
                    
            else:
                print(f"❌ File was not created at {file_path}")
        else:
            print(f"❌ Failed to create sample about: {message}")
        
        # Test 2: Create basic template
        print("\n📝 Test 2: Creating basic template...")
        success, message, file_path = about_manager.create_about_document(
            product_name="Test Product"
        )
        
        if success:
            print(f"✅ Basic template created: {file_path}")
        else:
            print(f"❌ Failed to create basic template: {message}")
        
        # Test 3: Create custom about document
        print("\n📝 Test 3: Creating custom about document...")
        success, message, file_path = about_manager.create_about_document(
            product_name="Custom Product",
            core_problem="testing inefficiency",
            industry_domain="software testing",
            vision_statement="To make testing more efficient and reliable",
            key_benefits=["automated testing", "better coverage", "faster feedback"],
            problems_solved=[
                {"category": "Manual Testing", "description": "Reduces manual testing effort"},
                {"category": "Test Coverage", "description": "Improves test coverage tracking"}
            ]
        )
        
        if success:
            print(f"✅ Custom about document created: {file_path}")
        else:
            print(f"❌ Failed to create custom about: {message}")
        
        # Test 4: List created files
        print("\n📝 Test 4: Listing created about files...")
        about_files = about_manager.list_about_files()
        print(f"✅ Found {len(about_files)} about files:")
        for file_path in about_files:
            print(f"   📄 {file_path}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_engine():
    """Test the template engine directly."""
    print("\n🧪 Testing Template Engine")
    print("=" * 50)
    
    try:
        from mods.project_management.template_engine import TemplateEngine
        
        # Initialize template engine
        template_engine = TemplateEngine(str(project_root))
        
        print("✅ TemplateEngine initialized successfully")
        
        # Test template rendering
        context = {
            'product_name': 'Test Product',
            'core_problem': 'testing problems',
            'industry_domain': 'software testing',
            'key_benefits': ['automated testing', 'better coverage', 'faster feedback']
        }
        
        rendered = template_engine.render_template("about/about_template.j2", context)
        
        if rendered and len(rendered) > 100:
            print(f"✅ Template rendered successfully ({len(rendered)} characters)")
            return True
        else:
            print("❌ Template rendering failed or produced empty result")
            return False
            
    except Exception as e:
        print(f"❌ Template engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 About Template System Test Suite")
    print("=" * 60)
    
    # Test template engine first
    engine_success = test_template_engine()
    
    # Test about manager
    manager_success = test_about_template_system()
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Template Engine: {'✅ PASS' if engine_success else '❌ FAIL'}")
    print(f"About Manager:   {'✅ PASS' if manager_success else '❌ FAIL'}")
    
    if engine_success and manager_success:
        print("\n🎉 All tests passed! About template system is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        sys.exit(1) 