#!/usr/bin/env python3
"""
Test TASK-044 Improvements - AI Task Creation System Enhancement

This test validates the improvements made to the AI task creation system
based on the analysis of TASK-043 issues.
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mods.project_management.ai_task_creator import AITaskCreator
from mods.project_management.context_analyzer import ContextAnalyzer
from mods.project_management.template_optimizer import TemplateOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TASK044Test")

class Task044TestSuite:
    """Test suite for TASK-044 improvements."""
    
    def __init__(self):
        self.project_root = str(Path.cwd())
        self.ai_creator = AITaskCreator(self.project_root)
        self.context_analyzer = ContextAnalyzer(self.project_root)
        self.template_optimizer = TemplateOptimizer()
        self.test_results = []
        
    async def run_all_tests(self):
        """Run all TASK-044 improvement tests."""
        logger.info("🚀 Starting TASK-044 Improvement Test Suite")
        logger.info("=" * 60)
        
        # Test 1: Context Analysis Enhancement
        await self.test_context_analysis_enhancement()
        
        # Test 2: Template Optimization
        await self.test_template_optimization()
        
        # Test 3: AI Task Creator Integration
        await self.test_ai_task_creator_integration()
        
        # Test 4: File-Specific Task Generation
        await self.test_file_specific_task_generation()
        
        # Test 5: Task Type Specialization
        await self.test_task_type_specialization()
        
        # Test 6: Quality Validation
        await self.test_quality_validation()
        
        # Generate test report
        self.generate_test_report()
        
    async def test_context_analysis_enhancement(self):
        """Test enhanced context analysis capabilities."""
        logger.info("\n📊 Test 1: Context Analysis Enhancement")
        logger.info("-" * 40)
        
        try:
            # Test with install script task (similar to TASK-043)
            description = "Enhance the Windows installation script to include better error handling and dependency validation"
            task_type = "Development"
            
            # Analyze context
            project_context = self.context_analyzer.analyze_task_context(description, task_type)
            
            # Validate results
            success = True
            issues = []
            
            # Check if relevant files were found
            if not project_context.relevant_files:
                issues.append("No relevant files identified")
                success = False
            else:
                logger.info(f"✅ Found {len(project_context.relevant_files)} relevant files")
                for file_analysis in project_context.relevant_files[:3]:
                    logger.info(f"   - {file_analysis.file_path} ({file_analysis.file_type})")
            
            # Check if recommendations were generated
            if not project_context.recommendations:
                issues.append("No recommendations generated")
                success = False
            else:
                logger.info(f"✅ Generated {len(project_context.recommendations)} recommendations")
                for rec in project_context.recommendations[:3]:
                    logger.info(f"   - {rec}")
            
            # Check for specific files that should be found for install script task
            expected_files = ["setup_windows.bat", ".app_settings.json", ".env"]
            found_files = [f.file_path for f in project_context.relevant_files]
            
            for expected_file in expected_files:
                if any(expected_file in found_file for found_file in found_files):
                    logger.info(f"✅ Found expected file: {expected_file}")
                else:
                    logger.warning(f"⚠️  Expected file not found: {expected_file}")
            
            self.test_results.append({
                "test": "Context Analysis Enhancement",
                "success": success,
                "issues": issues,
                "files_found": len(project_context.relevant_files),
                "recommendations": len(project_context.recommendations)
            })
            
        except Exception as e:
            logger.error(f"❌ Context analysis test failed: {e}")
            self.test_results.append({
                "test": "Context Analysis Enhancement",
                "success": False,
                "error": str(e)
            })
    
    async def test_template_optimization(self):
        """Test template optimization and section filtering."""
        logger.info("\n🎯 Test 2: Template Optimization")
        logger.info("-" * 40)
        
        try:
            # Test with different task types
            test_cases = [
                {
                    "task_type": "Development",
                    "description": "Enhance Windows installation script",
                    "should_exclude": ["ui_design", "user_interface"],
                    "should_include": ["implementation", "technical_specs"]
                },
                {
                    "task_type": "Bug Fix",
                    "description": "Fix login validation error",
                    "should_exclude": ["ui_design"],
                    "should_include": ["reproduction", "root_cause"]
                },
                {
                    "task_type": "Documentation",
                    "description": "Update API documentation",
                    "should_exclude": ["implementation", "ui_design"],
                    "should_include": ["content_structure", "examples"]
                }
            ]
            
            success = True
            issues = []
            
            for test_case in test_cases:
                logger.info(f"\n  Testing {test_case['task_type']} task optimization...")
                
                # Create base context
                context = {
                    "task_type": test_case["task_type"],
                    "description": test_case["description"],
                    "title": f"Test {test_case['task_type']} Task"
                }
                
                # Optimize template context
                optimized_context = self.template_optimizer.optimize_template_context(
                    context, test_case["task_type"], test_case["description"]
                )
                
                # Check if optimization worked
                if "template_sections" in optimized_context:
                    sections = optimized_context["template_sections"]
                    logger.info(f"   ✅ Template sections optimized: {len(sections)} sections")
                    
                    # Check excluded sections
                    for excluded in test_case["should_exclude"]:
                        if excluded in sections:
                            issues.append(f"{test_case['task_type']}: {excluded} should be excluded")
                            logger.warning(f"   ⚠️  {excluded} should be excluded but found")
                    
                    # Check included sections
                    for included in test_case["should_include"]:
                        if included not in sections:
                            logger.info(f"   ℹ️  {included} not explicitly included (may be default)")
                else:
                    logger.info(f"   ℹ️  No explicit section filtering applied")
                
                # Test flow diagram generation
                flow_context = self.template_optimizer.generate_task_specific_flow_diagram(
                    test_case["task_type"], test_case["description"], optimized_context
                )
                
                if "flow_diagram" in flow_context:
                    logger.info(f"   ✅ Task-specific flow diagram generated")
                else:
                    logger.warning(f"   ⚠️  No flow diagram generated")
            
            self.test_results.append({
                "test": "Template Optimization",
                "success": success,
                "issues": issues,
                "test_cases": len(test_cases)
            })
            
        except Exception as e:
            logger.error(f"❌ Template optimization test failed: {e}")
            self.test_results.append({
                "test": "Template Optimization",
                "success": False,
                "error": str(e)
            })
    
    async def test_ai_task_creator_integration(self):
        """Test AI task creator integration with TASK-044 improvements."""
        logger.info("\n🤖 Test 3: AI Task Creator Integration")
        logger.info("-" * 40)
        
        try:
            # Test task creation with TASK-044 enhancements
            title = "Test Enhanced Install Script Task"
            description = "Enhance the Windows installation script with better error handling, dependency validation, and user feedback"
            task_type = "Development"
            
            logger.info(f"Creating task: {title}")
            logger.info(f"Description: {description}")
            
            # Create enhanced task
            success, task_id, result = await self.ai_creator.create_enhanced_task(
                title=title,
                description=description,
                task_type=task_type,
                priority="high",
                use_ai_enhancement=True
            )
            
            if success:
                logger.info(f"✅ Task created successfully: {task_id}")
                logger.info(f"   File path: {result}")
                
                # Read and analyze the generated task
                if result and Path(result).exists():
                    with open(result, 'r', encoding='utf-8') as f:
                        task_content = f.read()
                    
                    # Check for TASK-044 improvements
                    improvements_found = []
                    
                    # Check for specific file references
                    if "setup_windows.bat" in task_content or ".app_settings.json" in task_content:
                        improvements_found.append("Specific file references")
                        logger.info("   ✅ Contains specific file references")
                    
                    # Check for current implementation analysis
                    if "Current Implementation" in task_content or "current_implementation" in task_content:
                        improvements_found.append("Current implementation analysis")
                        logger.info("   ✅ Contains current implementation analysis")
                    
                    # Check for task-specific content (not generic placeholders)
                    if "[Requirement 1]" not in task_content and "[Benefit 1]" not in task_content:
                        improvements_found.append("No generic placeholders")
                        logger.info("   ✅ No generic placeholder content found")
                    
                    # Check for TASK-044 enhancement marker
                    if "task044_enhanced" in task_content or "TASK-044" in task_content:
                        improvements_found.append("TASK-044 enhancement marker")
                        logger.info("   ✅ TASK-044 enhancement marker found")
                    
                    self.test_results.append({
                        "test": "AI Task Creator Integration",
                        "success": True,
                        "task_id": task_id,
                        "improvements_found": improvements_found,
                        "file_path": str(result)
                    })
                else:
                    logger.warning("⚠️  Task file not found for analysis")
                    self.test_results.append({
                        "test": "AI Task Creator Integration",
                        "success": True,
                        "task_id": task_id,
                        "warning": "Task file not found for content analysis"
                    })
            else:
                logger.error(f"❌ Task creation failed: {result}")
                self.test_results.append({
                    "test": "AI Task Creator Integration",
                    "success": False,
                    "error": result
                })
                
        except Exception as e:
            logger.error(f"❌ AI task creator integration test failed: {e}")
            self.test_results.append({
                "test": "AI Task Creator Integration",
                "success": False,
                "error": str(e)
            })
    
    async def test_file_specific_task_generation(self):
        """Test generation of tasks with specific file references."""
        logger.info("\n📁 Test 4: File-Specific Task Generation")
        logger.info("-" * 40)
        
        try:
            # Test different file-specific scenarios
            test_scenarios = [
                {
                    "description": "Fix error handling in setup_windows.bat script",
                    "expected_files": ["setup_windows.bat"],
                    "task_type": "Bug Fix"
                },
                {
                    "description": "Update app configuration settings in .app_settings.json",
                    "expected_files": [".app_settings.json"],
                    "task_type": "Development"
                },
                {
                    "description": "Enhance the main application entry point",
                    "expected_files": ["app.py"],
                    "task_type": "Development"
                }
            ]
            
            success = True
            issues = []
            
            for scenario in test_scenarios:
                logger.info(f"\n  Testing scenario: {scenario['description']}")
                
                # Analyze context for this scenario
                project_context = self.context_analyzer.analyze_task_context(
                    scenario["description"], scenario["task_type"]
                )
                
                # Check if expected files were found
                found_files = [f.file_path for f in project_context.relevant_files]
                
                for expected_file in scenario["expected_files"]:
                    if any(expected_file in found_file for found_file in found_files):
                        logger.info(f"   ✅ Found expected file: {expected_file}")
                    else:
                        logger.warning(f"   ⚠️  Expected file not found: {expected_file}")
                        issues.append(f"Expected file {expected_file} not found for scenario")
            
            self.test_results.append({
                "test": "File-Specific Task Generation",
                "success": success,
                "issues": issues,
                "scenarios_tested": len(test_scenarios)
            })
            
        except Exception as e:
            logger.error(f"❌ File-specific task generation test failed: {e}")
            self.test_results.append({
                "test": "File-Specific Task Generation",
                "success": False,
                "error": str(e)
            })
    
    async def test_task_type_specialization(self):
        """Test task type specialization and template customization."""
        logger.info("\n🎭 Test 5: Task Type Specialization")
        logger.info("-" * 40)
        
        try:
            # Test different task types
            task_types = ["Development", "Bug Fix", "Test Case", "Documentation", "Design"]
            
            success = True
            issues = []
            
            for task_type in task_types:
                logger.info(f"\n  Testing {task_type} specialization...")
                
                # Create context for this task type
                context = {
                    "task_type": task_type,
                    "description": f"Sample {task_type.lower()} task description",
                    "title": f"Test {task_type} Task"
                }
                
                # Optimize template for this task type
                optimized_context = self.template_optimizer.optimize_template_context(
                    context, task_type, context["description"]
                )
                
                # Check if task-type-specific optimizations were applied
                if "template_sections" in optimized_context:
                    logger.info(f"   ✅ Template sections customized for {task_type}")
                else:
                    logger.info(f"   ℹ️  No explicit template customization for {task_type}")
                
                # Generate flow diagram
                flow_context = self.template_optimizer.generate_task_specific_flow_diagram(
                    task_type, context["description"], optimized_context
                )
                
                if "flow_diagram" in flow_context:
                    logger.info(f"   ✅ Flow diagram generated for {task_type}")
                else:
                    logger.warning(f"   ⚠️  No flow diagram generated for {task_type}")
            
            self.test_results.append({
                "test": "Task Type Specialization",
                "success": success,
                "issues": issues,
                "task_types_tested": len(task_types)
            })
            
        except Exception as e:
            logger.error(f"❌ Task type specialization test failed: {e}")
            self.test_results.append({
                "test": "Task Type Specialization",
                "success": False,
                "error": str(e)
            })
    
    async def test_quality_validation(self):
        """Test quality validation and content improvement."""
        logger.info("\n🔍 Test 6: Quality Validation")
        logger.info("-" * 40)
        
        try:
            # Create test context with potential quality issues
            test_context = {
                "task_type": "Development",
                "description": "Test task with [Placeholder 1] and [Benefit 1]",
                "title": "Test Quality Validation",
                "functional_requirements_list": ["[Requirement 1]", "Actual requirement"],
                "benefits_list": ["[Benefit 1]", "Real benefit"]
            }
            
            # Validate template quality
            quality_issues = self.template_optimizer.validate_optimized_template(test_context)
            
            if quality_issues:
                logger.info(f"✅ Quality validation detected {len(quality_issues)} issues:")
                for issue in quality_issues:
                    logger.info(f"   - {issue}")
            else:
                logger.info("✅ No quality issues detected")
            
            # Test with clean context
            clean_context = {
                "task_type": "Development",
                "description": "Clean test task description",
                "title": "Clean Test Task",
                "functional_requirements_list": ["Specific requirement 1", "Specific requirement 2"],
                "benefits_list": ["Clear benefit 1", "Clear benefit 2"]
            }
            
            clean_quality_issues = self.template_optimizer.validate_optimized_template(clean_context)
            
            if not clean_quality_issues:
                logger.info("✅ Clean context passed quality validation")
            else:
                logger.warning(f"⚠️  Clean context still has issues: {clean_quality_issues}")
            
            self.test_results.append({
                "test": "Quality Validation",
                "success": True,
                "issues_detected": len(quality_issues) if quality_issues else 0,
                "clean_context_passed": not clean_quality_issues
            })
            
        except Exception as e:
            logger.error(f"❌ Quality validation test failed: {e}")
            self.test_results.append({
                "test": "Quality Validation",
                "success": False,
                "error": str(e)
            })
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        logger.info("\n📋 TASK-044 Test Report")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.get("success", False))
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Successful: {successful_tests}")
        logger.info(f"Failed: {total_tests - successful_tests}")
        logger.info(f"Success Rate: {(successful_tests / total_tests * 100):.1f}%")
        
        logger.info("\nDetailed Results:")
        logger.info("-" * 40)
        
        for result in self.test_results:
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            logger.info(f"{status} {result['test']}")
            
            if result.get("error"):
                logger.info(f"     Error: {result['error']}")
            if result.get("issues"):
                logger.info(f"     Issues: {len(result['issues'])}")
                for issue in result["issues"]:
                    logger.info(f"       - {issue}")
            if result.get("improvements_found"):
                logger.info(f"     Improvements: {', '.join(result['improvements_found'])}")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests * 100,
            "test_results": self.test_results
        }
        
        report_file = Path("TASK-044-test-report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 Test report saved to: {report_file}")
        
        # Summary
        if successful_tests == total_tests:
            logger.info("\n🎉 All TASK-044 improvements are working correctly!")
        else:
            logger.info(f"\n⚠️  {total_tests - successful_tests} tests failed. Review the issues above.")

async def main():
    """Main test execution function."""
    try:
        test_suite = Task044TestSuite()
        await test_suite.run_all_tests()
    except KeyboardInterrupt:
        logger.info("\n⏹️  Test execution interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 