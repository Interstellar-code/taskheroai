import sys
sys.path.append('.')
from mods.project_management.template_optimizer import TemplateOptimizer

def test_template_optimizer_relevance():
    """Test template optimizer flow diagram relevance logic."""
    print("🔍 Testing Template Optimizer Flow Diagram Relevance...")
    
    optimizer = TemplateOptimizer()
    
    # Test cases
    test_cases = [
        {
            'description': 'Enhance the Windows installation script to include user configuration prompts',
            'task_type': 'DEV',
            'expected': True,
            'reason': 'Installation script should be relevant'
        },
        {
            'description': 'enhance install script for taskhero ai',
            'task_type': 'DEV', 
            'expected': True,
            'reason': 'Install script enhancement should be relevant'
        },
        {
            'description': 'Create user authentication API endpoints',
            'task_type': 'DEV',
            'expected': True,
            'reason': 'User authentication has workflow'
        },
        {
            'description': 'Update documentation for API',
            'task_type': 'DOC',
            'expected': False,
            'reason': 'Documentation task should not be relevant'
        },
        {
            'description': 'Write README file',
            'task_type': 'DEV',
            'expected': False,
            'reason': 'Documentation-only task should not be relevant'
        }
    ]
    
    print(f"\n📊 Testing {len(test_cases)} cases...")
    
    for i, case in enumerate(test_cases, 1):
        is_relevant = optimizer._is_flow_diagram_relevant(case['task_type'], case['description'])
        
        status = "✅" if is_relevant == case['expected'] else "❌"
        print(f"{status} Case {i}: {case['description'][:50]}...")
        print(f"   Expected: {case['expected']}, Got: {is_relevant}")
        print(f"   Reason: {case['reason']}")
        
        if is_relevant == case['expected']:
            # Test flow diagram generation for relevant cases
            if is_relevant:
                flow_context = optimizer.generate_task_specific_flow_diagram(
                    case['task_type'], case['description'], {}
                )
                flow_steps = flow_context.get('flow_steps', [])
                print(f"   Generated {len(flow_steps)} flow steps")
                if flow_steps:
                    print(f"   First step: {flow_steps[0].get('title', 'N/A')}")
        print()

if __name__ == "__main__":
    test_template_optimizer_relevance() 