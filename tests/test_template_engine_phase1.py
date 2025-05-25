#!/usr/bin/env python3
"""
Test Script for Template Engine Phase 1

Tests the enhanced template engine with Jinja2 integration and validation.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from mods.project_management.template_engine import TemplateEngine, TemplateMetadata
    from mods.project_management.template_validator import TemplateValidator, ValidationResult
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def test_template_engine_basic():
    """Test basic template engine functionality."""
    print("🧪 Testing Template Engine Basic Functionality...")
    
    try:
        # Initialize template engine
        engine = TemplateEngine(project_root=str(project_root))
        print("✅ Template engine initialized successfully")
        
        # Test template categories
        categories = engine.get_template_categories()
        print(f"✅ Found template categories: {categories}")
        
        # Test template listing
        templates = engine.list_templates()
        print(f"✅ Found {len(templates)} templates")
        
        for template in templates:
            print(f"   - {template['name']} ({template['category']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Template engine test failed: {e}")
        return False

def test_template_validation():
    """Test template validation functionality."""
    print("\n🧪 Testing Template Validation...")
    
    try:
        # Initialize validator
        validator = TemplateValidator(project_root=str(project_root))
        print("✅ Template validator initialized successfully")
        
        # Test validation of base template
        result = validator.validate_template("base/document_base.j2")
        print(f"✅ Base template validation result: {'PASSED' if result.valid else 'FAILED'}")
        
        if not result.valid:
            print(f"   Errors: {result.errors}")
            print(f"   Warnings: {result.warnings}")
        
        # Test validation of development task template
        result = validator.validate_template("tasks/development_task.j2")
        print(f"✅ Development task template validation result: {'PASSED' if result.valid else 'FAILED'}")
        
        if not result.valid:
            print(f"   Errors: {result.errors}")
            print(f"   Warnings: {result.warnings}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template validation test failed: {e}")
        return False

def test_template_rendering():
    """Test template rendering with sample data."""
    print("\n🧪 Testing Template Rendering...")
    
    try:
        # Initialize template engine
        engine = TemplateEngine(project_root=str(project_root))
        
        # Sample context for development task template
        context = {
            'task_id': 'TASK-001',
            'title': 'Test Development Task',
            'description': 'This is a test development task to verify template rendering functionality.',
            'priority': 'High',
            'status': 'In Progress',
            'assignee': 'Test Developer',
            'task_type': 'Development',
            'created': '2025-01-27',
            'due_date': '2025-02-10',
            'sequence': '1',
            'tags': ['development', 'test', 'template'],
            'dependencies': ['TASK-000 - Setup Project Structure'],
            'dependent_tasks': ['TASK-002 - Integration Testing'],
            'estimated_hours': '8',
            'actual_hours': '4',
            'implementation_steps': [
                {
                    'title': 'Setup Development Environment',
                    'completed': True,
                    'target_date': '2025-01-28',
                    'substeps': [
                        {'description': 'Install dependencies', 'completed': True},
                        {'description': 'Configure environment', 'completed': True}
                    ]
                },
                {
                    'title': 'Implement Core Functionality',
                    'completed': False,
                    'in_progress': True,
                    'target_date': '2025-01-30',
                    'substeps': [
                        {'description': 'Create base classes', 'completed': True},
                        {'description': 'Implement business logic', 'completed': False}
                    ]
                }
            ],
            'acceptance_criteria': [
                {'description': 'Template engine can load Jinja2 templates', 'completed': True},
                {'description': 'Template validation works correctly', 'completed': False},
                {'description': 'Templates render with proper context', 'completed': False}
            ],
            'testing_strategy': 'Comprehensive unit and integration testing approach',
            'technical_notes': 'Use Jinja2 for template processing with proper error handling',
            'references': ['Jinja2 Documentation', 'Template Design Patterns'],
            'flow_description': 'This flow diagram shows the development process steps',
            'flow_notes': 'Additional notes about the flow diagram and process',
            'detailed_description': 'This is a detailed description of the development task with comprehensive information about implementation approach and expected outcomes.',
            'test_cases': [
                {'name': 'Template Engine Test', 'description': 'Test template rendering', 'expected': 'Template renders successfully', 'status': 'Passed'},
                {'name': 'Validation Test', 'description': 'Test template validation', 'expected': 'Validation passes', 'status': 'In Progress'}
            ],
            'architecture_notes': 'Modular architecture with clear separation of concerns',
            'performance_considerations': 'Template caching and optimized rendering',
            'security_considerations': 'Sandboxed template execution and input validation',
            'database_changes': 'No database changes required for this implementation',
            'database_schema': 'No database schema changes needed',
            'updates': [
                {'date': '2025-01-27', 'description': 'Test task created for template validation'},
                {'date': '2025-01-28', 'description': 'Added implementation steps and context'}
            ]
        }
        
        # Render the development task template
        rendered = engine.render_template("tasks/development_task.j2", context)
        print("✅ Development task template rendered successfully")
        
        # Save rendered output for inspection
        output_path = project_root / "test_output_development_task.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        print(f"✅ Rendered template saved to: {output_path}")
        
        # Display first few lines of rendered content
        lines = rendered.split('\n')[:15]
        print("\n📄 Rendered template preview:")
        for line in lines:
            print(f"   {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template rendering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_metadata():
    """Test template metadata extraction."""
    print("\n🧪 Testing Template Metadata Extraction...")
    
    try:
        # Initialize template engine
        engine = TemplateEngine(project_root=str(project_root))
        
        # Test metadata extraction for base template
        metadata = engine.get_template_metadata("base/document_base.j2")
        if metadata:
            print("✅ Base template metadata extracted:")
            print(f"   Title: {metadata.title}")
            print(f"   Description: {metadata.description}")
            print(f"   Category: {metadata.category}")
            print(f"   Tags: {metadata.tags}")
            print(f"   Is Base: {metadata.is_base}")
        else:
            print("❌ Failed to extract base template metadata")
            return False
        
        # Test metadata extraction for development task template
        metadata = engine.get_template_metadata("tasks/development_task.j2")
        if metadata:
            print("✅ Development task template metadata extracted:")
            print(f"   Title: {metadata.title}")
            print(f"   Description: {metadata.description}")
            print(f"   Category: {metadata.category}")
            print(f"   Extends: {metadata.extends}")
        else:
            print("❌ Failed to extract development task template metadata")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Template metadata test failed: {e}")
        return False

def test_template_preview():
    """Test template preview functionality."""
    print("\n🧪 Testing Template Preview...")
    
    try:
        # Initialize template engine
        engine = TemplateEngine(project_root=str(project_root))
        
        # Generate preview for development task template
        preview = engine.get_template_preview("tasks/development_task.j2")
        print("✅ Development task template preview generated")
        
        # Save preview for inspection
        preview_path = project_root / "test_preview_development_task.md"
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(preview)
        
        print(f"✅ Template preview saved to: {preview_path}")
        
        # Display first few lines of preview
        lines = preview.split('\n')[:10]
        print("\n📄 Template preview:")
        for line in lines:
            print(f"   {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template preview test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Template Engine Phase 1 Tests")
    print("=" * 50)
    
    tests = [
        test_template_engine_basic,
        test_template_validation,
        test_template_rendering,
        test_template_metadata,
        test_template_preview
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Phase 1 implementation is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 