#!/usr/bin/env python3
"""
Multi-Provider About Generation Test Script
Tests about document generation with all configured AI providers and models
"""

import sys
import os
import json
import time
from pathlib import Path
import traceback
import re
import asyncio
from typing import Dict, List, Tuple, Any

# Add the current directory to Python path for absolute imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def load_ai_configurations() -> Dict[str, Dict[str, Any]]:
    """Load AI provider configurations from setup file."""
    try:
        setup_file = project_root / '.taskhero_setup.json'
        if setup_file.exists():
            with open(setup_file, 'r', encoding='utf-8') as f:
                setup_data = json.load(f)
                
            ai_config = setup_data.get('ai_enhancement_config', {})
            model_optimizations = ai_config.get('model_optimizations', {})
            
            # Organize by provider
            providers = {}
            for model, config in model_optimizations.items():
                provider = config.get('provider')
                if provider not in providers:
                    providers[provider] = []
                providers[provider].append({
                    'model': model,
                    'config': config
                })
            
            return providers
        else:
            print("⚠️ Setup file not found, using default configurations")
            return {
                'ollama': [{'model': 'llama3.2:latest', 'config': {'quality_tier': 'local_general'}}]
            }
    except Exception as e:
        print(f"⚠️ Error loading configurations: {e}")
        return {'ollama': [{'model': 'llama3.2:latest', 'config': {'quality_tier': 'default'}}]}

def check_provider_availability(provider: str) -> bool:
    """Check if a provider is properly configured and available."""
    try:
        from mods.settings import AISettingsManager
        ai_settings = AISettingsManager()
        ai_settings.initialize()
        
        provider_status = ai_settings.get_provider_status(provider)
        return provider_status.get('configured', False)
    except Exception as e:
        print(f"⚠️ Could not check {provider} availability: {e}")
        # For ollama, assume it's available as it's local
        return provider == 'ollama'

def filter_available_providers(providers_config: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """Filter providers to only include those that are properly configured."""
    available_providers = {}
    
    for provider, models in providers_config.items():
        if check_provider_availability(provider):
            available_providers[provider] = models
            print(f"✅ {provider.upper()} is available")
        else:
            print(f"❌ {provider.upper()} is not properly configured - skipping")
    
    return available_providers

def analyze_content_quality(content: str) -> dict:
    """Analyze the quality of generated content."""
    
    # Count actual placeholders/unfilled content (more refined patterns)
    placeholder_patterns = [
        r'\[.*?\]',  # [placeholder text] - but exclude footnotes and reference-style links
        r'Product was created to solve general',  # Generic project descriptions
        r'software developers and teams experience',  # Generic user descriptions
        r'\[Description.*?\]',  # Template descriptions
        r'\[Brief description.*?\]',  # Template brief descriptions
        r'\[Core Feature.*?\]',  # Template feature names
        r'\[UX Goal.*?\]',  # Template UX goals
        r'\[User Persona.*?\]',  # Template personas
        r'\[Journey.*?\]',  # Template journeys
        r'\[Step.*?\]',  # Template steps
        r'\[Metric.*?\]',  # Template metrics
        r'\[Improvement.*?\]',  # Template improvements
        r'\[Time Period.*?\]',  # Template time periods
        r'\[describe.*?\]',  # Template describe prompts
        r'\[what.*?\]',  # Template what prompts
        r'\[who.*?\]',  # Template who prompts
        r'\[how.*?\]',  # Template how prompts
        r'\[when.*?\]',  # Template when prompts
        r'\[Major focus.*?\]',  # Template roadmap items
    ]
    
    placeholder_count = 0
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        # Filter out legitimate numbered items like "1. **TaskHero AI** specific content"
        filtered_matches = []
        for match in matches:
            # Skip if it's part of numbered formatting or contains actual content
            if not (re.match(r'\d+\.', match) or 'taskhero' in match.lower() or 'ai' in match.lower()):
                filtered_matches.append(match)
        placeholder_count += len(filtered_matches)
    
    # Count specific content sections
    sections = {
        'problems_solved': len(re.findall(r'\*\*.*?\*\*:', content.split('## 3. Problems Solved')[1].split('## 4.')[0])) if '## 3. Problems Solved' in content else 0,
        'how_it_works': len(re.findall(r'\d+\.\s+\*\*.*?\*\*:', content.split('## 5. How')[1].split('## 6.')[0])) if '## 5. How' in content else 0,
        'ux_goals': len(re.findall(r'\d+\.\s+\*\*.*?\*\*:', content.split('## 6. User Experience Goals')[1].split('## 7.')[0])) if '## 6. User Experience Goals' in content else 0,
        'user_personas': len(re.findall(r'\d+\.\s+\*\*.*?\*\*:', content.split('## 7. Target Users')[1].split('## 8.')[0])) if '## 7. Target Users' in content else 0,
        'user_journeys': len(re.findall(r'\d+\.\s+\*\*.*?\*\*:', content.split('## 8. Key User Journeys')[1].split('## 9.')[0])) if '## 8. Key User Journeys' in content else 0,
        'success_metrics': len(re.findall(r'\d+\.\s+\*\*.*?\*\*:', content.split('## 9. Success Metrics')[1].split('## 10.')[0])) if '## 9. Success Metrics' in content else 0,
        'recent_improvements': len(re.findall(r'\d+\.\s+\*\*.*?\*\*:', content.split('## 11. Recent Improvements')[1].split('## 12.')[0])) if '## 11. Recent Improvements' in content else 0,
    }
    
    # Calculate content richness
    total_chars = len(content)
    meaningful_chars = total_chars - (placeholder_count * 20)  # Estimate placeholder character impact
    
    # Check for specific TaskHero AI content and quality indicators
    taskhero_specific = any(term in content.lower() for term in [
        'taskhero', 'task hero', 'ai-powered task', 'project management', 
        'intelligent task', 'automated task', 'codebase analysis'
    ])
    
    # Check for quality indicators (detailed descriptions, specific features, etc.)
    quality_indicators = [
        len(re.findall(r'leverag[ei]', content, re.IGNORECASE)),  # "leverage", "leveraging"
        len(re.findall(r'automat[ei]', content, re.IGNORECASE)),  # "automate", "automated", "automatic"
        len(re.findall(r'intelligen[tc]', content, re.IGNORECASE)),  # "intelligent", "intelligence"
        len(re.findall(r'analyz[ei]|analy[sz]is', content, re.IGNORECASE)),  # analysis-related words
        len(re.findall(r'optimi[sz]', content, re.IGNORECASE)),  # optimization words
        len(re.findall(r'real-time', content, re.IGNORECASE)),  # real-time features
        len(re.findall(r'machine learning|ml|ai|artificial intelligence', content, re.IGNORECASE)),  # AI/ML terms
    ]
    
    total_quality_indicators = sum(quality_indicators)
    
    # Improved quality score calculation
    base_quality = (meaningful_chars / total_chars * 100) if total_chars > 0 else 0
    placeholder_penalty = placeholder_count * 3  # Reduced penalty for placeholders
    quality_bonus = min(30, total_quality_indicators)  # Increased bonus for quality content
    
    quality_score = max(0, min(100, base_quality - placeholder_penalty + quality_bonus))
    
    return {
        'total_characters': total_chars,
        'placeholder_count': placeholder_count,
        'sections': sections,
        'meaningful_content_ratio': meaningful_chars / total_chars if total_chars > 0 else 0,
        'taskhero_specific_content': taskhero_specific,
        'quality_indicators': total_quality_indicators,
        'quality_score': quality_score
    }

def compare_with_reference(generated_content: str, reference_path: str) -> dict:
    """Compare generated content with reference about page."""
    
    if not os.path.exists(reference_path):
        return {'error': f'Reference file not found: {reference_path}'}
    
    with open(reference_path, 'r', encoding='utf-8') as f:
        reference_content = f.read()
    
    # Analyze both contents
    generated_analysis = analyze_content_quality(generated_content)
    reference_analysis = analyze_content_quality(reference_content)
    
    # Compare sections completeness
    section_completeness = {}
    for section, ref_count in reference_analysis['sections'].items():
        gen_count = generated_analysis['sections'][section]
        if ref_count > 0:
            completeness = min(100, (gen_count / ref_count) * 100)
        else:
            completeness = 100 if gen_count == 0 else 0
        section_completeness[section] = {
            'reference_count': ref_count,
            'generated_count': gen_count,
            'completeness_percent': completeness
        }
    
    # Overall similarity assessment
    similarity_score = 0
    
    # Content length comparison (weight: 15%)
    length_ratio = min(1.0, generated_analysis['total_characters'] / reference_analysis['total_characters'])
    similarity_score += length_ratio * 15
    
    # Quality score (weight: 35%)
    quality_score = generated_analysis['quality_score'] / 100
    similarity_score += quality_score * 35
    
    # Section completeness (weight: 35%)
    avg_completeness = sum(s['completeness_percent'] for s in section_completeness.values()) / len(section_completeness)
    similarity_score += (avg_completeness / 100) * 35
    
    # TaskHero specific content (weight: 15%)
    specific_content_score = 100 if generated_analysis['taskhero_specific_content'] else 0
    similarity_score += (specific_content_score / 100) * 15
    
    return {
        'generated_analysis': generated_analysis,
        'reference_analysis': reference_analysis,
        'section_completeness': section_completeness,
        'similarity_score': similarity_score
    }

def test_about_generation_with_provider(provider: str, model: str, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Test about generation with a specific AI provider and model."""
    
    try:
        from mods.project_management.about_manager import AboutManager
        
        # Create a unique about manager for this test
        about_manager = AboutManager(str(project_root))
        
        # Override the AI settings for this specific test
        # We'll modify the _generate_full_dynamic_content method to use our provider/model
        original_method = about_manager._generate_full_dynamic_content
        
        async def custom_content_generation(project_info):
            """Custom content generation with specific provider/model."""
            try:
                print(f"🤖 Using AI: {provider} ({model}) for dynamic content generation")
                
                project_name = project_info.get('project_name', 'TaskHero AI')
                project_type = project_info.get('project_type', 'software application')
                core_features = project_info.get('core_features', [])
                dependencies = project_info.get('dependencies', [])
                architecture = project_info.get('architecture', 'modular')
                
                # Generate content section by section with proper numbering
                print("📋 Section 1: Why TaskHero AI Exists & Vision Statement generation...")
                basic_info = await about_manager._generate_basic_info(project_name, project_type, core_features, provider, model)
                
                print("🔍 Section 3: Problems Solved generation...")
                problems_solved = await about_manager._generate_problems_solved(project_name, project_type, provider, model)
                
                print("📊 Section 4: Solution Flow Diagram generation...")
                solution_flow = await about_manager._generate_solution_flow(project_name, core_features, provider, model)
                
                print("⚙️ Section 5: How TaskHero AI Works generation...")
                how_it_works = await about_manager._generate_how_it_works(project_name, core_features, provider, model)
                
                print("🎨 Section 6: User Experience Goals generation...")
                ux_goals = await about_manager._generate_ux_goals(project_name, project_type, provider, model)
                
                print("👥 Section 7: Target Users generation...")
                user_personas = await about_manager._generate_user_personas(project_name, project_type, provider, model)
                
                print("🚶‍♂️ Section 8: Key User Journeys generation...")
                user_journeys = await about_manager._generate_user_journeys(project_name, provider, model)
                
                print("📊 Section 9: Success Metrics generation...")
                success_metrics = await about_manager._generate_success_metrics(project_name, provider, model)
                
                print("🎯 Section 10: Current Product Focus generation...")
                current_focus = await about_manager._generate_current_focus(project_name, provider, model)
                
                print("🚀 Section 11: Recent Improvements generation...")
                recent_improvements = await about_manager._generate_recent_improvements(project_name, provider, model)
                
                print("📈 Section 12: Future Roadmap generation...")
                future_roadmap = await about_manager._generate_future_roadmap(project_name, provider, model)
                
                # Combine all generated content
                dynamic_context = {
                    **basic_info,
                    'problems_solved': problems_solved,
                    'solution_flow': solution_flow,
                    'how_it_works': how_it_works,
                    'ux_goals': ux_goals,
                    'user_personas': user_personas,
                    'user_journeys': user_journeys,
                    'success_metrics': success_metrics,
                    'current_focus': current_focus,
                    'recent_improvements': recent_improvements,
                    'future_roadmap': future_roadmap,
                    'additional_context': f"Built with {architecture}. Dependencies include: {', '.join(dependencies[:5])}. Total project files: {project_info.get('file_structure', {}).get('total_files', 'unknown')}.",
                    'improvements_summary': 'These AI-generated improvements reflect the current state and capabilities of the codebase analysis.'
                }
                
                print("✅ All about document sections generated successfully!")
                return dynamic_context
                
            except Exception as e:
                print(f"❌ Error in custom content generation: {e}")
                raise
        
        # Temporarily replace the method
        about_manager._generate_full_dynamic_content = custom_content_generation
        
        # Measure generation time
        start_time = time.time()
        
        # Generate about document
        success, message, file_path = about_manager.create_dynamic_about()
        
        generation_time = time.time() - start_time
        
        if not success:
            return False, {
                'error': message,
                'generation_time': generation_time,
                'provider': provider,
                'model': model,
                'config': config
            }
        
        # Read generated content
        if not os.path.exists(file_path):
            return False, {
                'error': f'Generated file not found: {file_path}',
                'generation_time': generation_time,
                'provider': provider,
                'model': model,
                'config': config
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            generated_content = f.read()
        
        # Compare with reference
        reference_path = project_root / "theherotasks" / "project-analysis" / "about-reference.md"
        comparison = compare_with_reference(generated_content, str(reference_path))
        
        if 'error' in comparison:
            return False, {
                'error': comparison['error'],
                'generation_time': generation_time,
                'provider': provider,
                'model': model,
                'config': config
            }
        
        # Create unique filename for this provider/model combination
        output_filename = f"about_{provider}_{model.replace(':', '_').replace('/', '_')}.md"
        output_path = project_root / "theherotasks" / "project-analysis" / output_filename
        
        # Save provider-specific version
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_content)
        
        result = {
            'success': True,
            'provider': provider,
            'model': model,
            'config': config,
            'generation_time': generation_time,
            'file_path': str(output_path),
            'content_length': len(generated_content),
            'quality_analysis': comparison['generated_analysis'],
            'similarity_score': comparison['similarity_score'],
            'section_completeness': comparison['section_completeness']
        }
        
        return True, result
        
    except Exception as e:
        return False, {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'provider': provider,
            'model': model,
            'config': config
        }

def test_all_providers():
    """Test about generation with all configured AI providers and models."""
    print("🚀 Multi-Provider About Generation Test")
    print("=" * 60)
    
    # Load AI configurations
    providers_config = load_ai_configurations()
    
    print(f"🔍 Found {len(providers_config)} providers with {sum(len(models) for models in providers_config.values())} total models")
    
    # Filter to only available providers
    print(f"\n🔍 Checking provider availability...")
    available_providers = filter_available_providers(providers_config)
    
    if not available_providers:
        print("❌ No AI providers are properly configured. Please check your setup.")
        return False
    
    print(f"\n✅ Testing {len(available_providers)} available providers with {sum(len(models) for models in available_providers.values())} models")
    
    # Results storage
    successful_tests = []
    failed_tests = []
    
    total_tests = sum(len(models) for models in available_providers.values())
    current_test = 0
    
    # Test each provider and model
    for provider, models in available_providers.items():
        print(f"\n🔧 Testing Provider: {provider.upper()}")
        print("=" * 40)
        
        for model_info in models:
            current_test += 1
            model = model_info['model']
            config = model_info['config']
            quality_tier = config.get('quality_tier', 'unknown')
            
            print(f"\n[{current_test}/{total_tests}] 🧪 Testing {provider} - {model} ({quality_tier})")
            print("-" * 50)
            
            try:
                success, result = test_about_generation_with_provider(provider, model, config)
                
                if success:
                    successful_tests.append(result)
                    print(f"✅ SUCCESS: Generated in {result['generation_time']:.2f}s")
                    print(f"   Quality Score: {result['quality_analysis']['quality_score']:.1f}%")
                    print(f"   Similarity: {result['similarity_score']:.1f}%")
                    print(f"   File: {result['file_path']}")
                else:
                    failed_tests.append(result)
                    error_msg = result.get('error', 'Unknown error')
                    if len(error_msg) > 100:
                        error_msg = error_msg[:100] + "..."
                    print(f"❌ FAILED: {error_msg}")
            except Exception as e:
                failed_tests.append({
                    'provider': provider,
                    'model': model,
                    'config': config,
                    'error': str(e)
                })
                print(f"❌ FAILED: {str(e)}")
    
    # Generate comprehensive comparison report
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE COMPARISON REPORT")
    print("=" * 60)
    
    print(f"\n📈 Test Summary:")
    print(f"   Successful: {len(successful_tests)}/{total_tests}")
    print(f"   Failed: {len(failed_tests)}/{total_tests}")
    if total_tests > 0:
        print(f"   Success Rate: {len(successful_tests)/total_tests*100:.1f}%")
    
    if successful_tests:
        # Sort by similarity score
        successful_tests.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        print(f"\n🏆 Top Performers (by Similarity Score):")
        print("-" * 60)
        for i, result in enumerate(successful_tests[:5], 1):
            quality_tier = result['config'].get('quality_tier', 'unknown')
            print(f"{i}. {result['provider'].upper()} - {result['model']}")
            print(f"   Similarity: {result['similarity_score']:.1f}% | Quality: {result['quality_analysis']['quality_score']:.1f}%")
            print(f"   Generation Time: {result['generation_time']:.2f}s | Tier: {quality_tier}")
            print(f"   Placeholders: {result['quality_analysis']['placeholder_count']} | Characters: {result['content_length']:,}")
            print()
        
        # Performance analysis
        print(f"\n⚡ Performance Analysis:")
        print("-" * 40)
        avg_similarity = sum(r['similarity_score'] for r in successful_tests) / len(successful_tests)
        avg_quality = sum(r['quality_analysis']['quality_score'] for r in successful_tests) / len(successful_tests)
        avg_time = sum(r['generation_time'] for r in successful_tests) / len(successful_tests)
        
        print(f"Average Similarity Score: {avg_similarity:.1f}%")
        print(f"Average Quality Score: {avg_quality:.1f}%")
        print(f"Average Generation Time: {avg_time:.2f}s")
        
        # Best by category
        best_similarity = max(successful_tests, key=lambda x: x['similarity_score'])
        best_quality = max(successful_tests, key=lambda x: x['quality_analysis']['quality_score'])
        fastest = min(successful_tests, key=lambda x: x['generation_time'])
        
        print(f"\n🎯 Category Winners:")
        print(f"Best Similarity: {best_similarity['provider']}/{best_similarity['model']} ({best_similarity['similarity_score']:.1f}%)")
        print(f"Best Quality: {best_quality['provider']}/{best_quality['model']} ({best_quality['quality_analysis']['quality_score']:.1f}%)")
        print(f"Fastest: {fastest['provider']}/{fastest['model']} ({fastest['generation_time']:.2f}s)")
        
        # Detailed comparison matrix
        print(f"\n📋 Detailed Comparison Matrix:")
        print("-" * 100)
        print(f"{'Provider/Model':<30} {'Similarity':<12} {'Quality':<10} {'Time':<8} {'Chars':<8} {'Placeholders':<12}")
        print("-" * 100)
        
        for result in successful_tests:
            provider_model = f"{result['provider']}/{result['model']}"[:29]
            similarity = f"{result['similarity_score']:.1f}%"
            quality = f"{result['quality_analysis']['quality_score']:.1f}%"
            time_str = f"{result['generation_time']:.1f}s"
            chars = f"{result['content_length']:,}"[:7]
            placeholders = str(result['quality_analysis']['placeholder_count'])
            
            print(f"{provider_model:<30} {similarity:<12} {quality:<10} {time_str:<8} {chars:<8} {placeholders:<12}")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        print("-" * 40)
        for result in failed_tests:
            error_msg = result.get('error', 'Unknown error')
            if len(error_msg) > 80:
                error_msg = error_msg[:80] + "..."
            print(f"• {result['provider']}/{result['model']}: {error_msg}")
    
    if successful_tests:
        print(f"\n📁 Generated Files:")
        print("-" * 30)
        for result in successful_tests:
            print(f"• {result['file_path']}")
    
        # Final recommendation
        best_overall = max(successful_tests, key=lambda x: (x['similarity_score'] + x['quality_analysis']['quality_score']) / 2)
        print(f"\n🌟 RECOMMENDED MODEL:")
        print(f"   {best_overall['provider'].upper()} - {best_overall['model']}")
        print(f"   Combined Score: {(best_overall['similarity_score'] + best_overall['quality_analysis']['quality_score']) / 2:.1f}%")
        print(f"   Quality Tier: {best_overall['config'].get('quality_tier', 'unknown')}")
    
    return len(successful_tests) > 0

if __name__ == "__main__":
    print("🤖 TaskHero AI - Multi-Provider About Generation Test")
    print("=" * 65)
    
    success = test_all_providers()
    
    print(f"\n📊 Final Result: {'✅ SUCCESS' if success else '❌ FAILURE'}")
    
    if success:
        print("\n🎉 Multi-provider testing completed successfully!")
        print("Check the generated files in theherotasks/project-analysis/ for comparison.")
    else:
        print("\n💥 All tests failed. Please check your AI provider configurations.")
    
    sys.exit(0 if success else 1) 