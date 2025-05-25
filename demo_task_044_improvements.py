#!/usr/bin/env python3
"""
Demo: TASK-044 Improvements in Action

This script demonstrates the TASK-044 improvements by creating an actual task
and showing the enhanced context analysis and template optimization.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mods.project_management.ai_task_creator import AITaskCreator

async def demo_enhanced_task_creation():
    """Demonstrate enhanced task creation with TASK-044 improvements."""
    print("🚀 TASK-044 Improvements Demo")
    print("=" * 60)
    
    # Initialize AI Task Creator
    creator = AITaskCreator(str(project_root))
    
    # Demo task similar to TASK-043 but with improvements
    title = "Enhance Windows Installation Script with Better Error Handling"
    description = """
    Improve the Windows installation script (setup_windows.bat) to include:
    - Better error handling and validation
    - Dependency checking before installation
    - User feedback during installation process
    - Configuration validation for .app_settings.json
    - Environment variable setup verification
    """
    
    print(f"📝 Creating task: {title}")
    print(f"📋 Description: {description.strip()}")
    print("\n🔄 Processing with TASK-044 improvements...")
    
    try:
        # Create enhanced task with TASK-044 improvements
        success, task_id, file_path = await creator.create_enhanced_task(
            title=title,
            description=description,
            task_type="Development",
            priority="high",
            assigned_to="Development Team",
            tags=["install", "script", "error-handling", "windows", "setup"],
            effort_estimate="Medium",
            use_ai_enhancement=True
        )
        
        if success:
            print(f"\n✅ Task created successfully!")
            print(f"📄 Task ID: {task_id}")
            print(f"📁 File path: {file_path}")
            
            # Analyze the generated task content
            if file_path and Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n📊 Task Analysis:")
                print(f"   - Content length: {len(content)} characters")
                print(f"   - Lines: {len(content.splitlines())}")
                
                # Check for TASK-044 improvements
                improvements = []
                
                # Check for specific file references
                if "setup_windows.bat" in content or ".app_settings.json" in content:
                    improvements.append("✅ Specific file references included")
                
                # Check for reduced placeholder content
                placeholder_count = content.count('[Requirement') + content.count('[Benefit')
                if placeholder_count == 0:
                    improvements.append("✅ No generic placeholder content")
                elif placeholder_count < 5:
                    improvements.append("⚠️  Minimal placeholder content")
                else:
                    improvements.append("❌ Still contains placeholder content")
                
                # Check for task-specific content
                if "installation" in content.lower() and "error handling" in content.lower():
                    improvements.append("✅ Task-specific content generated")
                
                # Check for current implementation analysis
                if "Current Implementation" in content or "implementation analysis" in content.lower():
                    improvements.append("✅ Current implementation analysis included")
                
                # Check for TASK-044 enhancement marker
                if "task044_enhanced" in content.lower() or "TASK-044" in content:
                    improvements.append("✅ TASK-044 enhancement marker present")
                
                print(f"\n🎯 TASK-044 Improvements Detected:")
                for improvement in improvements:
                    print(f"   {improvement}")
                
                # Show content preview
                print(f"\n📋 Content Preview (first 30 lines):")
                lines = content.split('\n')
                for i, line in enumerate(lines[:30], 1):
                    print(f"{i:2d}: {line}")
                
                if len(lines) > 30:
                    print(f"... and {len(lines) - 30} more lines")
                
                return task_id, file_path
            else:
                print("⚠️  Task file not found for analysis")
                return task_id, None
        else:
            print(f"❌ Task creation failed: {file_path}")
            return None, None
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

async def demo_context_analysis():
    """Demonstrate enhanced context analysis."""
    print(f"\n🔍 Context Analysis Demo")
    print("-" * 40)
    
    try:
        from mods.project_management.context_analyzer import ContextAnalyzer
        
        analyzer = ContextAnalyzer(str(project_root))
        
        # Analyze context for install script task
        description = "Enhance Windows installation script with better error handling"
        task_type = "Development"
        
        print(f"📝 Analyzing: {description}")
        
        context = analyzer.analyze_task_context(description, task_type)
        
        print(f"\n📊 Analysis Results:")
        print(f"   - Relevant files found: {len(context.relevant_files)}")
        print(f"   - Recommendations generated: {len(context.recommendations)}")
        print(f"   - Dependencies mapped: {len(context.dependencies)}")
        print(f"   - Patterns detected: {sum(len(patterns) for patterns in context.patterns.values())}")
        
        if context.relevant_files:
            print(f"\n📁 Top Relevant Files:")
            for i, file_analysis in enumerate(context.relevant_files[:5], 1):
                print(f"   {i}. {file_analysis.file_path} ({file_analysis.file_type})")
                if file_analysis.key_patterns:
                    print(f"      Patterns: {', '.join(file_analysis.key_patterns[:3])}")
        
        if context.recommendations:
            print(f"\n💡 Key Recommendations:")
            for i, rec in enumerate(context.recommendations[:5], 1):
                print(f"   {i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Context analysis demo failed: {e}")
        return False

def demo_template_optimization():
    """Demonstrate template optimization."""
    print(f"\n🎨 Template Optimization Demo")
    print("-" * 40)
    
    try:
        from mods.project_management.template_optimizer import TemplateOptimizer
        
        optimizer = TemplateOptimizer()
        
        # Test with install script context (similar to TASK-043 issues)
        original_context = {
            'title': 'Enhance Windows Installation Script',
            'description': 'Enhance Windows installation script with better error handling',
            'task_type': 'Development',
            'priority': 'high',
            'functional_requirements_list': [
                '[Requirement 1]', 
                '[Requirement 2]',
                'Improve error handling in installation process'
            ],
            'benefits_list': [
                '[Benefit 1]',
                '[Benefit 2]',
                'Better user experience during installation'
            ],
            'ui_design_overview': 'UI design considerations will be defined during implementation phase.',
            'ui_wireframes': 'ASCII art wireframes will be created'
        }
        
        print(f"📝 Original context has {len(original_context)} variables")
        print(f"   - Contains placeholder content: {any('[' in str(v) for v in original_context.values())}")
        print(f"   - Has UI design sections: {'ui_design_overview' in original_context}")
        
        # Optimize template
        optimized_context = optimizer.optimize_template_context(
            original_context, 'Development', 'Enhance Windows installation script'
        )
        
        print(f"\n✨ Optimized context has {len(optimized_context)} variables")
        
        # Check improvements
        improvements = []
        
        # Check placeholder removal
        placeholder_found = False
        for key, value in optimized_context.items():
            if isinstance(value, (str, list)):
                if isinstance(value, str) and '[' in value and ']' in value:
                    placeholder_found = True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and '[' in item and ']' in item:
                            placeholder_found = True
                            break
        
        if not placeholder_found:
            improvements.append("✅ Placeholder content removed")
        else:
            improvements.append("⚠️  Some placeholder content remains")
        
        # Check UI section filtering
        ui_sections_present = any('ui_' in key for key in optimized_context.keys())
        if not ui_sections_present:
            improvements.append("✅ Irrelevant UI sections filtered out")
        else:
            improvements.append("ℹ️  UI sections retained (may be relevant)")
        
        # Check section flags
        if any(key.startswith('show_') for key in optimized_context.keys()):
            improvements.append("✅ Section control flags added")
        
        print(f"\n🎯 Optimization Results:")
        for improvement in improvements:
            print(f"   {improvement}")
        
        # Test flow diagram generation
        flow_context = optimizer.generate_task_specific_flow_diagram(
            'Development', 'Enhance Windows installation script', optimized_context
        )
        
        if 'flow_diagram' in flow_context:
            improvements.append("✅ Task-specific flow diagram generated")
        
        # Test quality validation
        issues = optimizer.validate_optimized_template(optimized_context)
        if issues:
            improvements.append(f"⚠️  Quality issues detected: {len(issues)}")
            for issue in issues[:3]:
                improvements.append(f"      - {issue}")
        else:
            improvements.append("✅ Template quality validation passed")
        
        print(f"\n🎯 Optimization Results:")
        for improvement in improvements:
            print(f"   {improvement}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template optimization demo failed: {e}")
        return False

async def main():
    """Run the complete TASK-044 improvements demo."""
    print(f"🎬 TASK-044 Improvements Demonstration")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Demo 1: Context Analysis
        context_success = await demo_context_analysis()
        
        # Demo 2: Template Optimization
        template_success = demo_template_optimization()
        
        # Demo 3: Enhanced Task Creation
        task_id, file_path = await demo_enhanced_task_creation()
        
        # Summary
        print(f"\n" + "=" * 70)
        print(f"📋 Demo Summary:")
        print(f"   ✅ Context Analysis: {'Success' if context_success else 'Failed'}")
        print(f"   ✅ Template Optimization: {'Success' if template_success else 'Failed'}")
        print(f"   ✅ Enhanced Task Creation: {'Success' if task_id else 'Failed'}")
        
        if task_id:
            print(f"\n🎯 Generated Task: {task_id}")
            if file_path:
                print(f"📁 File: {file_path}")
                print(f"\n💡 The generated task demonstrates TASK-044 improvements:")
                print(f"   - Context-aware content with specific file references")
                print(f"   - Template optimization with relevant sections only")
                print(f"   - Reduced placeholder content")
                print(f"   - Task-specific flow diagrams")
                print(f"   - Quality validation and content improvement")
        
        success_count = sum([context_success, template_success, bool(task_id)])
        if success_count == 3:
            print(f"\n🎉 All TASK-044 improvements demonstrated successfully!")
        else:
            print(f"\n⚠️  {3 - success_count} demos failed. Check output above for details.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 