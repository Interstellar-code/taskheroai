#!/usr/bin/env python3
"""
Test Script for Template Engine Phase 2

Tests the enhanced templates created during Phase 2 migration.
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

def test_project_plan_template():
    """Test the project plan template."""
    print("🧪 Testing Project Plan Template...")
    
    try:
        engine = TemplateEngine(project_root=str(project_root))
        
        # Sample context for project plan
        context = {
            'project_name': 'TaskHero AI Development',
            'total_tasks': 25,
            'done_count': 8,
            'testing_count': 3,
            'devdone_count': 4,
            'inprogress_count': 5,
            'todo_count': 3,
            'backlog_count': 2,
            'completion_rate': 60,
            'total_estimated_hours': 120,
            'total_actual_hours': 75,
            'progress_percentage': 65,
            'tasks': [
                {'id': 'TASK-001', 'status': 'Done', 'title': 'Setup Project Structure', 'type': 'Setup', 'priority': 'High', 'due_date': '2025-01-20', 'assignee': 'Dev Team', 'progress': 100},
                {'id': 'TASK-006', 'status': 'In Progress', 'title': 'Template System', 'type': 'Development', 'priority': 'Medium', 'due_date': '2025-02-10', 'assignee': 'Dev Team', 'progress': 75}
            ],
            'kanban_backlog': [{'id': 'TASK-020', 'title': 'Future Enhancement'}],
            'kanban_todo': [{'id': 'TASK-015', 'title': 'AI Integration'}],
            'kanban_inprogress': [{'id': 'TASK-006', 'title': 'Template System'}],
            'kanban_devdone': [{'id': 'TASK-005', 'title': 'Core Module'}],
            'kanban_testing': [{'id': 'TASK-003', 'title': 'CLI Interface'}],
            'kanban_done': [{'id': 'TASK-001', 'title': 'Project Setup'}],
            'dependencies': [
                {'task_id': 'TASK-006', 'task_name': 'Template System', 'depends_on': ['TASK-001'], 'required_by': ['TASK-015']}
            ],
            'recent_updates': [
                {'date': '2025-01-27', 'description': 'Phase 1 template engine completed'},
                {'date': '2025-01-28', 'description': 'Phase 2 template migration started'}
            ],
            'timeline_entries': [
                {'date': '2025-01-20', 'title': 'Project Started', 'description': 'Initial setup completed'},
                {'date': '2025-01-27', 'title': 'Phase 1 Complete', 'description': 'Template engine implemented'},
                {'date': '2025-01-30', 'title': 'Phase 2 Target', 'description': 'Template migration completion'}
            ],
            'task_categories': [
                {'name': 'Development', 'completed': 5, 'total': 8, 'percentage': 63},
                {'name': 'Testing', 'completed': 2, 'total': 4, 'percentage': 50},
                {'name': 'Documentation', 'completed': 1, 'total': 2, 'percentage': 50}
            ],
            'team_performance': [
                {'name': 'Dev Team', 'completed_tasks': 8, 'hours_logged': 75}
            ],
            'current_sprint': {
                'name': 'Sprint 2',
                'start_date': '2025-01-20',
                'end_date': '2025-02-03',
                'goal': 'Complete template system implementation',
                'tasks': ['TASK-006', 'TASK-007'],
                'progress': 65
            },
            'blockers': [
                {'severity': 'Low', 'description': 'Minor dependency on external library', 'impact': 'Minimal delay possible', 'mitigation': 'Alternative approach identified'}
            ],
            'milestones': [
                {'name': 'Phase 1 Complete', 'date': '2025-01-27', 'status': 'Complete', 'dependencies': ['TASK-001']},
                {'name': 'Phase 2 Complete', 'date': '2025-01-30', 'status': 'In Progress', 'dependencies': ['TASK-006']}
            ]
        }
        
        # Render the project plan template
        rendered = engine.render_template("projects/project_plan.j2", context)
        print("✅ Project plan template rendered successfully")
        
        # Save rendered output
        output_path = project_root / "test_output_project_plan.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        print(f"✅ Rendered project plan saved to: {output_path}")
        
        # Display preview
        lines = rendered.split('\n')[:15]
        print("\n📄 Project plan preview:")
        for line in lines:
            print(f"   {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Project plan template test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_status_report_template():
    """Test the status report template."""
    print("\n🧪 Testing Status Report Template...")
    
    try:
        engine = TemplateEngine(project_root=str(project_root))
        
        # Sample context for status report
        context = {
            'project_name': 'TaskHero AI',
            'report_date': '2025-01-28',
            'total_tasks': 25,
            'completed_tasks': 8,
            'completion_percentage': 32,
            'inprogress_tasks': 5,
            'inprogress_percentage': 20,
            'todo_tasks': 12,
            'todo_percentage': 48,
            'overdue_tasks': 0,
            'health_score': 85,
            'executive_summary': 'Project is progressing well with Phase 1 template engine completed and Phase 2 migration underway.',
            'accomplishments': [
                {'title': 'Template Engine Implementation', 'date': '2025-01-27', 'description': 'Completed Jinja2-based template engine with validation', 'impact': 'Foundation for all future template work'},
                {'title': 'Base Template Creation', 'date': '2025-01-28', 'description': 'Created comprehensive base template with inheritance', 'impact': 'Standardized document structure'}
            ],
            'current_work': [
                {'title': 'Template Migration', 'assignee': 'Dev Team', 'status': 'In Progress', 'progress': 60, 'due_date': '2025-01-30', 'blockers': 'None'},
                {'title': 'Enhanced Templates', 'assignee': 'Dev Team', 'status': 'In Progress', 'progress': 40, 'due_date': '2025-02-01', 'blockers': 'None'}
            ],
            'upcoming_deadlines': [
                {'id': 'TASK-006', 'title': 'Template System Completion', 'due_date': '2025-02-10', 'assignee': 'Dev Team', 'status': 'In Progress', 'risk': 'Low'}
            ],
            'team_updates': [
                {'name': 'Development Team', 'focus_areas': ['Template System', 'Migration'], 'completed': 'Phase 1 template engine', 'current_work': 'Phase 2 template migration', 'blockers': 'None', 'availability': '100%', 'achievements': ['Completed template engine', 'Enhanced validation system']}
            ],
            'blockers': [
                {'severity': 'Low', 'title': 'Minor Integration Issue', 'description': 'Small compatibility issue with legacy templates', 'impact': 'Minimal delay', 'mitigation': 'Workaround implemented', 'owner': 'Dev Team', 'target_date': '2025-01-30'}
            ],
            'sprint_name': 'Template Migration Sprint'
        }
        
        # Render the status report template
        rendered = engine.render_template("reports/status_report.j2", context)
        print("✅ Status report template rendered successfully")
        
        # Save rendered output
        output_path = project_root / "test_output_status_report.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        print(f"✅ Rendered status report saved to: {output_path}")
        
        # Display preview
        lines = rendered.split('\n')[:15]
        print("\n📄 Status report preview:")
        for line in lines:
            print(f"   {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Status report template test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_general_task_template():
    """Test the general task template."""
    print("\n🧪 Testing General Task Template...")
    
    try:
        engine = TemplateEngine(project_root=str(project_root))
        
        # Sample context for general task
        context = {
            'task_id': 'TASK-TEST',
            'title': 'Test General Task Template',
            'description': 'This is a test of the general task template functionality.',
            'priority': 'Medium',
            'status': 'In Progress',
            'assignee': 'Test User',
            'task_type': 'Testing',
            'created': '2025-01-28',
            'due_date': '2025-02-05',
            'sequence': '1',
            'tags': ['testing', 'template', 'general'],
            'flow_description': 'This flow shows the general task processing workflow',
            'flow_steps': [
                {'title': 'Initial Setup'},
                {'title': 'Content Development'}
            ],
            'show_flow_diagram': True,
            'flow_notes': 'Additional notes about the task workflow and process',
            'detailed_description': 'This is a comprehensive test of the general task template functionality, including all major sections and features.',
            'implementation_steps': [
                {
                    'title': 'Template Setup',
                    'completed': True,
                    'target_date': '2025-01-28',
                    'substeps': [
                        {'description': 'Create template structure', 'completed': True},
                        {'description': 'Add metadata', 'completed': True}
                    ]
                },
                {
                    'title': 'Content Development',
                    'completed': False,
                    'in_progress': True,
                    'target_date': '2025-01-30',
                    'substeps': [
                        {'description': 'Add main content blocks', 'completed': True},
                        {'description': 'Test template rendering', 'completed': False}
                    ]
                }
            ],
            'acceptance_criteria': [
                {'description': 'Template renders without errors', 'completed': True},
                {'description': 'All sections display correctly', 'completed': False}
            ],
            'success_metrics': [
                {'name': 'Template Rendering Success Rate', 'target': '100%', 'current': '95%'},
                {'name': 'Validation Pass Rate', 'target': '100%', 'current': '100%'}
            ],
            'dependencies': ['TASK-001 - Project Setup'],
            'dependent_tasks': ['TASK-007 - Next Phase'],
            'dependency_type': 'Blocking - This task cannot start until dependencies are completed',
            'testing_strategy': 'Comprehensive testing with various data inputs',
            'test_plan': [
                {'name': 'Template Engine Test', 'description': 'Test template rendering', 'completed': True},
                {'name': 'Validation Test', 'description': 'Test template validation', 'completed': False}
            ],
            'technical_notes': 'Uses Jinja2 template inheritance for consistency',
            'references': ['Template Design Guide', 'Jinja2 Documentation'],
            'updates': [
                {'date': '2025-01-28', 'description': 'Task created for testing purposes'}
            ]
        }
        
        # Render the general task template
        rendered = engine.render_template("tasks/general_task.j2", context)
        print("✅ General task template rendered successfully")
        
        # Save rendered output
        output_path = project_root / "test_output_general_task.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        print(f"✅ Rendered general task saved to: {output_path}")
        
        # Display preview
        lines = rendered.split('\n')[:15]
        print("\n📄 General task preview:")
        for line in lines:
            print(f"   {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ General task template test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_validation_phase2():
    """Test validation of all Phase 2 templates."""
    print("\n🧪 Testing Phase 2 Template Validation...")
    
    try:
        validator = TemplateValidator(project_root=str(project_root))
        
        templates_to_test = [
            "projects/project_plan.j2",
            "reports/status_report.j2", 
            "tasks/general_task.j2"
        ]
        
        all_valid = True
        
        for template in templates_to_test:
            result = validator.validate_template(template)
            status = "✅ PASSED" if result.valid else "❌ FAILED"
            print(f"   {template}: {status}")
            
            if not result.valid:
                all_valid = False
                print(f"     Errors: {result.errors}")
                print(f"     Warnings: {result.warnings}")
        
        if all_valid:
            print("✅ All Phase 2 templates passed validation")
        else:
            print("❌ Some Phase 2 templates failed validation")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Phase 2 template validation failed: {e}")
        return False

def test_template_discovery():
    """Test template discovery and listing."""
    print("\n🧪 Testing Template Discovery...")
    
    try:
        engine = TemplateEngine(project_root=str(project_root))
        
        # List all templates
        templates = engine.list_templates()
        print(f"✅ Found {len(templates)} templates total")
        
        # Group by category
        by_category = {}
        for template in templates:
            category = template['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(template['name'])
        
        for category, template_list in by_category.items():
            print(f"   📁 {category}: {len(template_list)} templates")
            for template in template_list:
                print(f"      - {template}")
        
        # Check that we have the expected Phase 2 templates
        expected_templates = [
            'projects\\project_plan.j2',
            'reports\\status_report.j2',
            'tasks\\general_task.j2'
        ]
        
        found_templates = [t['name'] for t in templates]
        missing = [t for t in expected_templates if t not in found_templates]
        
        if missing:
            print(f"❌ Missing expected templates: {missing}")
            return False
        else:
            print("✅ All expected Phase 2 templates found")
            return True
        
    except Exception as e:
        print(f"❌ Template discovery test failed: {e}")
        return False

def main():
    """Run all Phase 2 tests."""
    print("🚀 Starting Template Engine Phase 2 Tests")
    print("=" * 50)
    
    tests = [
        test_template_discovery,
        test_template_validation_phase2,
        test_project_plan_template,
        test_status_report_template,
        test_general_task_template
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
    print(f"📊 Phase 2 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All Phase 2 tests passed! Template migration is successful.")
    else:
        print("⚠️  Some Phase 2 tests failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 