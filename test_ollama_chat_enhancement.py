#!/usr/bin/env python3
"""
Test script for TASK-125: Ollama Chat Performance Enhancement

This script tests the enhanced context discovery, prompt engineering,
and response processing improvements implemented for Ollama chat.
"""

import asyncio
import os
import sys
import time
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mods.ai.chat_handler import ChatHandler
from mods.ai.context_manager import CodebaseContextManager
from mods.code.indexer import FileIndexer
from mods.settings.environment_manager import EnvironmentManager


class OllamaChatTester:
    """Test class for Ollama chat performance enhancements."""
    
    def __init__(self):
        """Initialize the tester with required components."""
        self.environment_manager = EnvironmentManager()
        self.indexer = None
        self.chat_handler = None
        self.context_manager = None
        
        # Test queries for different scenarios
        self.test_queries = [
            {
                'query': 'What can you tell me about the codebase from a functional user perspective?',
                'type': 'functional_analysis',
                'expected_files': 15
            },
            {
                'query': 'What are the main features users can access?',
                'type': 'functional_analysis', 
                'expected_files': 12
            },
            {
                'query': 'How do users typically interact with this system?',
                'type': 'workflow_analysis',
                'expected_files': 10
            },
            {
                'query': 'How does the AI chat system work technically?',
                'type': 'technical_analysis',
                'expected_files': 8
            },
            {
                'query': 'Explain the task management capabilities',
                'type': 'component_analysis',
                'expected_files': 10
            }
        ]
    
    async def setup(self) -> bool:
        """Set up the test environment."""
        try:
            print("🔧 Setting up test environment...")
            
            # Initialize indexer
            self.indexer = FileIndexer()
            if not self.indexer.is_indexed():
                print("⚠️  Project not indexed. Please run indexing first.")
                return False
            
            # Initialize context manager
            self.context_manager = CodebaseContextManager(self.indexer)
            
            # Initialize chat handler
            self.chat_handler = ChatHandler(
                indexer=self.indexer,
                environment_manager=self.environment_manager
            )
            
            # Initialize AI provider
            if not await self.chat_handler.initialize_ai_provider():
                print("❌ Failed to initialize AI provider")
                return False
            
            print("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    async def test_context_discovery(self) -> Dict[str, Any]:
        """Test the enhanced context discovery system."""
        print("\n📁 Testing Context Discovery Enhancement...")
        
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'details': []
        }
        
        for test_case in self.test_queries:
            results['total_tests'] += 1
            
            try:
                # Test context discovery
                context = await self.context_manager.get_relevant_context(
                    test_case['query'], 
                    max_files=20
                )
                
                files_found = len(context.relevant_files)
                expected_files = test_case['expected_files']
                
                # Check if we found enough files
                if files_found >= expected_files:
                    results['passed_tests'] += 1
                    status = "✅ PASS"
                else:
                    results['failed_tests'] += 1
                    status = "❌ FAIL"
                
                test_result = {
                    'query': test_case['query'][:50] + "...",
                    'type': test_case['type'],
                    'files_found': files_found,
                    'expected_files': expected_files,
                    'status': status
                }
                
                results['details'].append(test_result)
                print(f"  {status} {test_case['type']}: {files_found}/{expected_files} files")
                
            except Exception as e:
                results['failed_tests'] += 1
                results['details'].append({
                    'query': test_case['query'][:50] + "...",
                    'error': str(e),
                    'status': "❌ ERROR"
                })
                print(f"  ❌ ERROR {test_case['type']}: {e}")
        
        return results
    
    async def test_prompt_engineering(self) -> Dict[str, Any]:
        """Test the enhanced prompt engineering system."""
        print("\n🎯 Testing Prompt Engineering Enhancement...")
        
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'details': []
        }
        
        # Test query classification
        from mods.ai.providers.ollama_provider import OllamaProvider
        
        provider = OllamaProvider()
        
        for test_case in self.test_queries:
            results['total_tests'] += 1
            
            try:
                # Test query classification
                classified_type = provider._classify_query_type(test_case['query'])
                expected_type = test_case['type']
                
                if classified_type == expected_type:
                    results['passed_tests'] += 1
                    status = "✅ PASS"
                else:
                    results['failed_tests'] += 1
                    status = "❌ FAIL"
                
                test_result = {
                    'query': test_case['query'][:50] + "...",
                    'classified_as': classified_type,
                    'expected_type': expected_type,
                    'status': status
                }
                
                results['details'].append(test_result)
                print(f"  {status} Query classified as: {classified_type}")
                
            except Exception as e:
                results['failed_tests'] += 1
                results['details'].append({
                    'query': test_case['query'][:50] + "...",
                    'error': str(e),
                    'status': "❌ ERROR"
                })
                print(f"  ❌ ERROR: {e}")
        
        return results
    
    async def test_end_to_end_chat(self) -> Dict[str, Any]:
        """Test end-to-end chat functionality with enhancements."""
        print("\n💬 Testing End-to-End Chat Enhancement...")
        
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'details': [],
            'response_times': []
        }
        
        # Test one representative query
        test_query = "What can you tell me about the codebase from a functional user perspective?"
        
        try:
            results['total_tests'] += 1
            
            start_time = time.time()
            
            # Process query with enhanced system
            response, relevant_files = await self.chat_handler.process_query(
                test_query, 
                max_chat_mode=True
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            results['response_times'].append(response_time)
            
            # Validate response quality
            if response and len(response) > 100:
                # Check for structured content
                has_structure = any(marker in response for marker in ['##', '###', '**', '•', '-'])
                
                # Check for project-specific content
                has_project_content = any(term in response.lower() for term in ['taskhero', 'task', 'ai', 'chat'])
                
                # Check for follow-up suggestions
                has_follow_up = '💡 Related Questions' in response
                
                if has_structure and has_project_content:
                    results['passed_tests'] += 1
                    status = "✅ PASS"
                else:
                    results['failed_tests'] += 1
                    status = "❌ FAIL"
                
                test_result = {
                    'query': test_query[:50] + "...",
                    'response_length': len(response),
                    'files_used': len(relevant_files),
                    'response_time': f"{response_time:.2f}s",
                    'has_structure': has_structure,
                    'has_project_content': has_project_content,
                    'has_follow_up': has_follow_up,
                    'status': status
                }
                
                results['details'].append(test_result)
                print(f"  {status} Response: {len(response)} chars, {len(relevant_files)} files, {response_time:.2f}s")
                print(f"    Structure: {has_structure}, Project Content: {has_project_content}, Follow-up: {has_follow_up}")
                
            else:
                results['failed_tests'] += 1
                results['details'].append({
                    'query': test_query[:50] + "...",
                    'error': "Response too short or empty",
                    'status': "❌ FAIL"
                })
                print(f"  ❌ FAIL: Response too short or empty")
                
        except Exception as e:
            results['failed_tests'] += 1
            results['details'].append({
                'query': test_query[:50] + "...",
                'error': str(e),
                'status': "❌ ERROR"
            })
            print(f"  ❌ ERROR: {e}")
        
        return results
    
    async def run_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        print("🚀 Starting Ollama Chat Performance Enhancement Tests")
        print("=" * 60)
        
        # Setup
        if not await self.setup():
            return {'error': 'Setup failed'}
        
        # Run individual test suites
        context_results = await self.test_context_discovery()
        prompt_results = await self.test_prompt_engineering()
        e2e_results = await self.test_end_to_end_chat()
        
        # Compile overall results
        overall_results = {
            'context_discovery': context_results,
            'prompt_engineering': prompt_results,
            'end_to_end_chat': e2e_results,
            'summary': {
                'total_tests': (context_results['total_tests'] + 
                              prompt_results['total_tests'] + 
                              e2e_results['total_tests']),
                'total_passed': (context_results['passed_tests'] + 
                               prompt_results['passed_tests'] + 
                               e2e_results['passed_tests']),
                'total_failed': (context_results['failed_tests'] + 
                               prompt_results['failed_tests'] + 
                               e2e_results['failed_tests'])
            }
        }
        
        # Calculate success rate
        total_tests = overall_results['summary']['total_tests']
        total_passed = overall_results['summary']['total_passed']
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        overall_results['summary']['success_rate'] = success_rate
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {overall_results['summary']['total_failed']}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT: Enhancement implementation successful!")
        elif success_rate >= 60:
            print("✅ GOOD: Enhancement mostly working, minor issues to address")
        else:
            print("⚠️  NEEDS WORK: Enhancement needs significant improvements")
        
        return overall_results
    
    async def cleanup(self):
        """Clean up resources."""
        if self.chat_handler:
            await self.chat_handler.close()


async def main():
    """Main test function."""
    tester = OllamaChatTester()
    
    try:
        results = await tester.run_tests()
        
        # Save results to file
        import json
        with open('ollama_chat_enhancement_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: ollama_chat_enhancement_test_results.json")
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
