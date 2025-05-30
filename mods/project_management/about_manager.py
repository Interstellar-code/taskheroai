"""
About Template Management Module

Handles dynamic about document creation using AI analysis of the codebase.
Provides truly intelligent about document generation with real-time project analysis.
"""

import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .template_engine import TemplateEngine

logger = logging.getLogger("TaskHeroAI.ProjectManagement.AboutManager")


class AboutManager:
    """Service for managing dynamic about document creation with AI enhancement."""

    def __init__(self, project_root: str, ai_manager=None, settings_manager=None):
        """Initialize the About Manager.

        Args:
            project_root: Root directory for project management
            ai_manager: AI manager for intelligent content generation
            settings_manager: Settings manager for AI configuration
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.template_engine = TemplateEngine(project_root)
        self.ai_manager = ai_manager
        self.settings_manager = settings_manager

        # About template path
        self.about_template = "about/about_template.j2"

        # Output directory for about files - use task folder from settings
        self.output_dir = self._get_task_analysis_folder()

    def _get_task_analysis_folder(self) -> Path:
        """Get the task analysis folder from settings or use default."""
        try:
            # Try to get kanban folder from settings
            if self.settings_manager:
                kanban_path = self.settings_manager.get_task_kanban_folder()
                if kanban_path and Path(kanban_path).exists():
                    analysis_dir = Path(kanban_path) / "project-analysis"
                    analysis_dir.mkdir(parents=True, exist_ok=True)
                    return analysis_dir

            # Fallback: use default structure
            default_tasks = self.project_root / "theherotasks"
            if default_tasks.exists():
                analysis_dir = default_tasks / "project-analysis"
                analysis_dir.mkdir(parents=True, exist_ok=True)
                return analysis_dir

            # Final fallback: create theherotasks structure
            analysis_dir = self.project_root / "theherotasks" / "project-analysis"
            analysis_dir.mkdir(parents=True, exist_ok=True)
            return analysis_dir

        except Exception as e:
            logger.warning(f"Could not determine task folder, using default: {e}")
            # Absolute fallback
            analysis_dir = self.project_root / "theherotasks" / "project-analysis"
            analysis_dir.mkdir(parents=True, exist_ok=True)
            return analysis_dir

    def create_dynamic_about(self) -> tuple[bool, str, Optional[str]]:
        """Create a truly dynamic about document by analyzing the codebase with AI."""
        try:
            print(f"🔍 Analyzing codebase structure...")

            # Get comprehensive project analysis
            project_info = self._get_project_analysis()
            if not project_info:
                print(f"⚠️  No project analysis available, generating from basic codebase scan...")
                project_info = self._perform_basic_codebase_analysis()

            print(f"🤖 Generating AI-powered content for all sections...")

            # Generate all content dynamically using AI
            dynamic_context = asyncio.run(self._generate_full_dynamic_content(project_info))

            # Create the about document
            return self.create_about_document(use_ai=False, **dynamic_context)

        except Exception as e:
            logger.error(f"Error creating dynamic about: {e}")
            return False, f"Error creating dynamic about: {e}", None

    def create_about_document(self, use_ai: bool = True, **kwargs) -> tuple[bool, str, Optional[str]]:
        """Create an about document using the template."""
        try:
            # Prepare context (AI enhancement was already done in dynamic creation)
            context = self.prepare_about_context(**kwargs)

            # Render the template
            content = self.render_about_template(context)

            # Generate filename
            filename = self.generate_about_filename(
                context.get('product_name', 'Product')
            )

            # Save the file
            file_path = self._save_about_file(filename, content)

            logger.info(f"About document created: {file_path}")
            return True, f"About document created successfully", str(file_path)

        except Exception as e:
            logger.error(f"Error creating about document: {e}")
            return False, f"Error creating about document: {e}", None

    def _get_project_analysis(self) -> Optional[Dict[str, Any]]:
        """Get enhanced project analysis using ContextProcessor for better context discovery."""
        try:
            # Try to get existing project info from AI manager first
            if self.ai_manager and hasattr(self.ai_manager, 'project_analyzer'):
                project_analyzer = self.ai_manager.project_analyzer
                if project_analyzer:
                    project_info = project_analyzer.load_project_info()
                    if project_info:
                        # Enhance existing project info with ContextProcessor
                        return self._enhance_project_analysis_with_context(project_info)

            # Generate enhanced project analysis using ContextProcessor
            logger.info("Generating enhanced project analysis for about document using ContextProcessor")
            return self._generate_enhanced_project_analysis()

        except Exception as e:
            logger.warning(f"Failed to get enhanced project analysis: {e}")
        return None

    def _enhance_project_analysis_with_context(self, base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance existing project analysis with ContextProcessor insights."""
        try:
            from .context_processor import ContextProcessor

            context_processor = ContextProcessor(str(self.project_root))

            # Use multi-source context discovery for TaskHero AI overview
            enhanced_context = context_processor.collect_embeddings_context(
                "TaskHero AI project overview features capabilities architecture",
                {"task_type": "Documentation", "title": "About Document", "description": "Project overview"}
            )

            # Extract enhanced insights from context
            enhanced_insights = self._extract_context_insights(enhanced_context)

            # Merge with base analysis
            enhanced_analysis = {**base_analysis}
            enhanced_analysis.update({
                'enhanced_features': enhanced_insights.get('features', []),
                'context_files': [chunk.file_path for chunk in enhanced_context],
                'project_capabilities': enhanced_insights.get('capabilities', []),
                'architecture_details': enhanced_insights.get('architecture', {}),
                'context_quality_score': len(enhanced_context)
            })

            logger.info(f"Enhanced project analysis with {len(enhanced_context)} context sources")
            return enhanced_analysis

        except Exception as e:
            logger.warning(f"Failed to enhance project analysis with context: {e}")
            return base_analysis

    def _generate_enhanced_project_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive project analysis using ContextProcessor."""
        try:
            from .context_processor import ContextProcessor

            context_processor = ContextProcessor(str(self.project_root))

            # Multi-pass context discovery for comprehensive analysis
            project_context = context_processor.collect_embeddings_context(
                "TaskHero AI complete project analysis features architecture capabilities",
                {"task_type": "Documentation", "title": "Project Analysis", "description": "Complete project overview"}
            )

            # Extract comprehensive insights
            insights = self._extract_context_insights(project_context)

            # Combine with basic analysis
            basic_analysis = self._perform_basic_codebase_analysis()

            enhanced_analysis = {
                **basic_analysis,
                'enhanced_features': insights.get('features', basic_analysis.get('core_features', [])),
                'context_files': [chunk.file_path for chunk in project_context],
                'project_capabilities': insights.get('capabilities', []),
                'architecture_details': insights.get('architecture', {'type': basic_analysis.get('architecture', 'modular')}),
                'context_quality_score': len(project_context),
                'task_management_context': self._get_task_management_insights(project_context),
                'ai_integration_details': self._get_ai_integration_insights(project_context)
            }

            logger.info(f"Generated enhanced project analysis with {len(project_context)} context sources")
            return enhanced_analysis

        except Exception as e:
            logger.error(f"Failed to generate enhanced project analysis: {e}")
            return self._perform_basic_codebase_analysis()

    def _perform_basic_codebase_analysis(self) -> Dict[str, Any]:
        """Perform basic codebase analysis when project analyzer is not available."""
        try:
            analysis = {
                'project_name': self._detect_project_name(),
                'project_type': self._detect_project_type(),
                'core_features': self._extract_core_features(),
                'file_structure': self._analyze_file_structure(),
                'dependencies': self._extract_dependencies(),
                'complexity_level': 'intermediate',
                'architecture': self._detect_architecture_pattern()
            }
            return analysis
        except Exception as e:
            logger.warning(f"Basic codebase analysis failed: {e}")
            return {
                'project_name': 'Project',
                'project_type': 'software application',
                'core_features': [],
                'file_structure': {},
                'dependencies': [],
                'complexity_level': 'intermediate',
                'architecture': 'modular'
            }

    def _detect_project_name(self) -> str:
        """Detect project name from various sources."""
        try:
            # Try setup.json first
            setup_file = self.project_root / '.taskhero_setup.json'
            if setup_file.exists():
                import json
                with open(setup_file, 'r') as f:
                    setup_data = json.load(f)
                    if 'project_name' in setup_data:
                        return setup_data['project_name']

            # Try package.json
            package_file = self.project_root / 'package.json'
            if package_file.exists():
                import json
                with open(package_file, 'r') as f:
                    package_data = json.load(f)
                    return package_data.get('name', 'TaskHero AI')

            # For TaskHero AI project, always return the proper name
            if self.project_root.name in ['taskheroai', 'tasktheroai', 'task-hero-ai']:
                return 'TaskHero AI'

            # Try requirements.txt or setup.py for Python projects
            if (self.project_root / 'requirements.txt').exists() or (self.project_root / 'setup.py').exists():
                # Check if this looks like TaskHero AI based on directory structure
                if (self.project_root / 'mods').exists() and (self.project_root / 'theherotasks').exists():
                    return 'TaskHero AI'
                return self.project_root.name

            # Fallback to TaskHero AI for this project
            return 'TaskHero AI'

        except Exception:
            return 'TaskHero AI'

    def _detect_project_type(self) -> str:
        """Detect project type from file extensions and structure."""
        try:
            python_files = list(self.project_root.rglob("*.py"))
            js_files = list(self.project_root.rglob("*.js"))
            ts_files = list(self.project_root.rglob("*.ts"))
            java_files = list(self.project_root.rglob("*.java"))

            if len(python_files) > 10:
                return "Python application"
            elif len(js_files) > 10 or len(ts_files) > 10:
                return "JavaScript/TypeScript application"
            elif len(java_files) > 5:
                return "Java application"
            else:
                return "software application"

        except Exception:
            return "software application"

    def _extract_core_features(self) -> List[str]:
        """Extract core features by analyzing file names and directory structure."""
        try:
            features = set()

            # Analyze directory names for features
            for item in self.project_root.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    name = item.name.lower()
                    if any(keyword in name for keyword in ['api', 'service', 'manager', 'handler', 'mods']):
                        features.add(f"{item.name.replace('_', ' ').title()} Module")

            # Analyze Python files for class/function patterns
            for py_file in self.project_root.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Look for manager/handler classes
                        import re
                        classes = re.findall(r'class\s+(\w*(?:Manager|Handler|Service|API|Engine))', content)
                        for cls in classes:
                            clean_name = cls.replace('Manager', '').replace('Handler', '').replace('Service', '').replace('API', '').replace('Engine', '')
                            if clean_name:
                                features.add(f"{clean_name} Management")
                except Exception:
                    continue

            return list(features)[:7]  # Limit to 7 features

        except Exception:
            return ["Core Functionality", "User Management", "Data Processing"]

    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze file structure to understand project organization."""
        try:
            structure = {
                'total_files': 0,
                'main_directories': [],
                'file_types': {}
            }

            for item in self.project_root.rglob("*"):
                if item.is_file() and not any(ignore in str(item) for ignore in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                    structure['total_files'] += 1
                    ext = item.suffix.lower()
                    structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1

            for item in self.project_root.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    structure['main_directories'].append(item.name)

            return structure

        except Exception:
            return {'total_files': 0, 'main_directories': [], 'file_types': {}}

    def _extract_dependencies(self) -> List[str]:
        """Extract project dependencies from various files."""
        try:
            dependencies = []

            # Python requirements
            req_file = self.project_root / 'requirements.txt'
            if req_file.exists():
                with open(req_file, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            dep = line.strip().split('==')[0].split('>=')[0].split('<=')[0]
                            dependencies.append(dep)

            # Package.json dependencies
            package_file = self.project_root / 'package.json'
            if package_file.exists():
                import json
                with open(package_file, 'r') as f:
                    package_data = json.load(f)
                    deps = package_data.get('dependencies', {})
                    dependencies.extend(list(deps.keys())[:10])  # Limit to 10

            return dependencies[:15]  # Limit to 15 dependencies

        except Exception:
            return []

    def _detect_architecture_pattern(self) -> str:
        """Detect architecture pattern from project structure."""
        try:
            directories = [item.name.lower() for item in self.project_root.iterdir() if item.is_dir()]

            if 'mods' in directories or 'modules' in directories:
                return "modular architecture"
            elif 'api' in directories and 'ui' in directories:
                return "API-driven architecture"
            elif 'src' in directories and 'tests' in directories:
                return "standard project structure"
            elif 'app' in directories:
                return "application-based architecture"
            else:
                return "custom architecture"

        except Exception:
            return "modular architecture"

    def _extract_context_insights(self, context_chunks) -> Dict[str, Any]:
        """Extract insights from context chunks for enhanced project analysis."""
        try:
            insights = {
                'features': [],
                'capabilities': [],
                'architecture': {}
            }

            # Analyze context chunks for features and capabilities
            for chunk in context_chunks:
                file_path = str(chunk.file_path).lower()
                content = chunk.text.lower()

                # Extract features based on file names and content
                if 'task' in file_path or 'task' in content:
                    insights['features'].append('Task Management System')
                if 'ai' in file_path or 'chat' in file_path or 'ai' in content:
                    insights['features'].append('AI-Powered Chat Integration')
                if 'index' in file_path or 'search' in content:
                    insights['features'].append('Intelligent File Indexing')
                if 'dashboard' in file_path or 'menu' in content:
                    insights['features'].append('Interactive Dashboard')
                if 'kanban' in file_path or 'kanban' in content:
                    insights['features'].append('Kanban Board Visualization')

                # Extract capabilities
                if 'context' in file_path or 'context' in content:
                    insights['capabilities'].append('Context-Aware Analysis')
                if 'provider' in file_path or 'ollama' in content or 'openai' in content:
                    insights['capabilities'].append('Multi-Provider AI Integration')
                if 'semantic' in content or 'embedding' in content:
                    insights['capabilities'].append('Semantic Search')
                if 'template' in file_path or 'template' in content:
                    insights['capabilities'].append('Template-Based Generation')

            # Remove duplicates and limit
            insights['features'] = list(set(insights['features']))[:7]
            insights['capabilities'] = list(set(insights['capabilities']))[:5]

            # Determine architecture type
            if any('modular' in str(chunk.file_path).lower() for chunk in context_chunks):
                insights['architecture'] = {'type': 'modular', 'pattern': 'component-based'}
            else:
                insights['architecture'] = {'type': 'layered', 'pattern': 'service-oriented'}

            return insights

        except Exception as e:
            logger.warning(f"Failed to extract context insights: {e}")
            return {'features': [], 'capabilities': [], 'architecture': {}}

    def _get_task_management_insights(self, context_chunks) -> Dict[str, Any]:
        """Extract task management specific insights from context."""
        try:
            task_insights = {
                'workflow_types': [],
                'management_features': [],
                'integration_points': []
            }

            for chunk in context_chunks:
                content = chunk.text.lower()
                file_path = str(chunk.file_path).lower()

                # Workflow types
                if 'kanban' in content or 'kanban' in file_path:
                    task_insights['workflow_types'].append('Kanban Board Management')
                if 'dashboard' in content or 'dashboard' in file_path:
                    task_insights['workflow_types'].append('Dashboard-Based Workflow')
                if 'ai' in content and 'task' in content:
                    task_insights['workflow_types'].append('AI-Assisted Task Creation')

                # Management features
                if 'metadata' in content:
                    task_insights['management_features'].append('Enhanced Metadata Management')
                if 'template' in content:
                    task_insights['management_features'].append('Template-Based Task Generation')
                if 'context' in content:
                    task_insights['management_features'].append('Context-Aware Task Discovery')

                # Integration points
                if 'git' in content:
                    task_insights['integration_points'].append('Git Integration')
                if 'ai' in content or 'provider' in content:
                    task_insights['integration_points'].append('AI Provider Integration')

            # Remove duplicates
            for key in task_insights:
                task_insights[key] = list(set(task_insights[key]))

            return task_insights

        except Exception as e:
            logger.warning(f"Failed to extract task management insights: {e}")
            return {'workflow_types': [], 'management_features': [], 'integration_points': []}

    def _get_ai_integration_insights(self, context_chunks) -> Dict[str, Any]:
        """Extract AI integration specific insights from context."""
        try:
            ai_insights = {
                'providers': [],
                'capabilities': [],
                'features': []
            }

            for chunk in context_chunks:
                content = chunk.text.lower()
                file_path = str(chunk.file_path).lower()

                # AI Providers
                if 'ollama' in content or 'ollama' in file_path:
                    ai_insights['providers'].append('Ollama (Local AI)')
                if 'openai' in content or 'openai' in file_path:
                    ai_insights['providers'].append('OpenAI (GPT Models)')
                if 'anthropic' in content or 'claude' in content:
                    ai_insights['providers'].append('Anthropic (Claude)')
                if 'deepseek' in content:
                    ai_insights['providers'].append('DeepSeek')

                # AI Capabilities
                if 'chat' in content and 'ai' in content:
                    ai_insights['capabilities'].append('Interactive AI Chat')
                if 'context' in content and 'ai' in content:
                    ai_insights['capabilities'].append('Context-Aware AI Responses')
                if 'embedding' in content or 'semantic' in content:
                    ai_insights['capabilities'].append('Semantic Understanding')
                if 'prompt' in content:
                    ai_insights['capabilities'].append('Advanced Prompt Engineering')

                # AI Features
                if 'task' in content and 'ai' in content:
                    ai_insights['features'].append('AI-Powered Task Creation')
                if 'about' in content and 'ai' in content:
                    ai_insights['features'].append('Dynamic About Generation')
                if 'analysis' in content and 'ai' in content:
                    ai_insights['features'].append('Intelligent Code Analysis')

            # Remove duplicates
            for key in ai_insights:
                ai_insights[key] = list(set(ai_insights[key]))

            return ai_insights

        except Exception as e:
            logger.warning(f"Failed to extract AI integration insights: {e}")
            return {'providers': [], 'capabilities': [], 'features': []}

    async def _generate_full_dynamic_content(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all about document content dynamically using AI."""
        try:
            # Get AI settings
            from ..settings import AISettingsManager
            ai_settings = AISettingsManager()
            ai_settings.initialize()

            assignments = ai_settings.get_ai_function_assignments()
            description_assignment = assignments.get('description', {})
            provider = description_assignment.get('provider', 'ollama')
            model = description_assignment.get('model', 'llama3.2:latest')

            print(f"🤖 Using AI: {provider} ({model}) for dynamic content generation")

            project_name = project_info.get('project_name', 'Project')
            project_type = project_info.get('project_type', 'software application')
            core_features = project_info.get('core_features', [])
            dependencies = project_info.get('dependencies', [])
            architecture = project_info.get('architecture', 'modular')

            # Enhanced context from ContextProcessor
            enhanced_features = project_info.get('enhanced_features', core_features)
            project_capabilities = project_info.get('project_capabilities', [])
            task_management_context = project_info.get('task_management_context', {})
            ai_integration_details = project_info.get('ai_integration_details', {})
            context_quality_score = project_info.get('context_quality_score', 0)

            print(f"📊 Enhanced context quality: {context_quality_score} sources discovered")

            # Enhanced context for all sections
            enhanced_context = {
                'project_name': project_name,
                'project_type': project_type,
                'enhanced_features': enhanced_features,
                'project_capabilities': project_capabilities,
                'task_management_context': task_management_context,
                'ai_integration_details': ai_integration_details,
                'architecture': architecture,
                'dependencies': dependencies,
                'context_quality_score': context_quality_score
            }

            # Generate content section by section with enhanced context and provider-specific prompts
            print("📋 Section 1: Why TaskHero AI Exists & Vision Statement generation...")
            basic_info = await self._generate_basic_info_enhanced(enhanced_context, provider, model)

            print("🔍 Section 3: Problems Solved generation...")
            problems_solved = await self._generate_problems_solved_enhanced(enhanced_context, provider, model)

            print("📊 Section 4: Solution Flow Diagram generation...")
            solution_flow = await self._generate_solution_flow_enhanced(enhanced_context, provider, model)

            print("⚙️ Section 5: How TaskHero AI Works generation...")
            how_it_works = await self._generate_how_it_works_enhanced(enhanced_context, provider, model)

            print("🎨 Section 6: User Experience Goals generation...")
            ux_goals = await self._generate_ux_goals_enhanced(enhanced_context, provider, model)

            print("👥 Section 7: Target Users generation...")
            user_personas = await self._generate_user_personas_enhanced(enhanced_context, provider, model)

            print("🚶‍♂️ Section 8: Key User Journeys generation...")
            user_journeys = await self._generate_user_journeys_enhanced(enhanced_context, provider, model)

            print("📊 Section 9: Success Metrics generation...")
            success_metrics = await self._generate_success_metrics_enhanced(enhanced_context, provider, model)

            print("🎯 Section 10: Current Product Focus generation...")
            current_focus = await self._generate_current_focus_enhanced(enhanced_context, provider, model)

            print("🚀 Section 11: Recent Improvements generation...")
            recent_improvements = await self._generate_recent_improvements_enhanced(enhanced_context, provider, model)

            print("📈 Section 12: Future Roadmap generation...")
            future_roadmap = await self._generate_future_roadmap_enhanced(enhanced_context, provider, model)

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
            logger.error(f"Failed to generate dynamic content: {e}")
            raise

    def _get_provider_prompt_config(self, provider: str, model: str) -> Dict[str, Any]:
        """Get provider-specific prompt configuration for optimized responses."""
        provider_configs = {
            'ollama': {
                'instruction_style': 'detailed_structured',
                'context_emphasis': 'high',
                'example_preference': 'concrete',
                'response_format': 'json_with_explanation'
            },
            'openai': {
                'instruction_style': 'concise_precise',
                'context_emphasis': 'medium',
                'example_preference': 'varied',
                'response_format': 'structured_json'
            },
            'anthropic': {
                'instruction_style': 'analytical_thorough',
                'context_emphasis': 'high',
                'example_preference': 'detailed',
                'response_format': 'comprehensive_json'
            },
            'deepseek': {
                'instruction_style': 'technical_focused',
                'context_emphasis': 'medium',
                'example_preference': 'practical',
                'response_format': 'efficient_json'
            }
        }

        return provider_configs.get(provider, provider_configs['ollama'])

    def _build_enhanced_section_prompt(self, section_type: str, context: Dict[str, Any],
                                     provider: str, model: str) -> str:
        """Build enhanced prompts optimized for specific AI providers and sections."""

        # Get provider-specific configuration
        prompt_config = self._get_provider_prompt_config(provider, model)

        # Extract context information
        project_name = context.get('project_name', 'TaskHero AI')
        enhanced_features = context.get('enhanced_features', [])
        project_capabilities = context.get('project_capabilities', [])
        task_management_context = context.get('task_management_context', {})
        ai_integration_details = context.get('ai_integration_details', {})

        # Build context-aware prompt based on section type
        if section_type == 'basic_info':
            return self._build_basic_info_prompt(context, prompt_config)
        elif section_type == 'problems_solved':
            return self._build_problems_solved_prompt(context, prompt_config)
        elif section_type == 'how_it_works':
            return self._build_how_it_works_prompt(context, prompt_config)
        elif section_type == 'solution_flow':
            return self._build_solution_flow_prompt(context, prompt_config)
        else:
            return self._build_generic_section_prompt(section_type, context, prompt_config)

    def _build_basic_info_prompt(self, context: Dict[str, Any], prompt_config: Dict[str, Any]) -> str:
        """Build enhanced prompt for basic info generation."""
        project_name = context.get('project_name', 'TaskHero AI')
        enhanced_features = context.get('enhanced_features', [])
        project_capabilities = context.get('project_capabilities', [])
        ai_integration_details = context.get('ai_integration_details', {})

        features_text = f" with features like: {', '.join(enhanced_features[:3])}" if enhanced_features else ""
        capabilities_text = f" and capabilities including: {', '.join(project_capabilities[:2])}" if project_capabilities else ""

        return f"""
You are creating a product context document for {project_name}, an AI-powered project management and task automation platform{features_text}{capabilities_text}.

Generate CONCISE and SPECIFIC product information for {project_name}. Keep all descriptions SHORT and CLEAR.

IMPORTANT: Follow the reference format exactly. Each field should be:
- core_problem: One clear sentence (max 15 words)
- pain_points: List 4 specific pain points, separated by commas (max 80 words total)
- challenge: One clear sentence about team struggles (max 20 words)
- core_solution: One clear sentence about the AI solution (max 15 words)
- key_benefits: Exactly 3 short, specific benefits (max 10 words each)
- vision_statement: One inspiring sentence (max 25 words)

Generate basic product information for {project_name} in JSON format:
{{
    "product_name": "{project_name}",
    "core_problem": "inefficient project management and task tracking in software development",
    "industry_domain": "software development and project management",
    "target_users": "development teams, project managers, and software engineers",
    "pain_points": "scattered task information, manual status updates, lack of intelligent automation, and poor project visibility",
    "challenge": "teams struggle to maintain visibility and efficiency in complex projects while managing multiple priorities",
    "core_solution": "an AI-powered task management and project analysis platform",
    "product_type": "intelligent project management system",
    "key_benefits": ["automate task creation and tracking with AI", "provide intelligent insights and project analytics", "streamline team collaboration and workflow optimization"],
    "vision_statement": "To revolutionize project management by making AI-powered automation accessible to every development team, enabling them to focus on creating great products rather than managing processes."
}}

CRITICAL: Keep all content CONCISE and SPECIFIC. Avoid long, complex sentences. Match the reference format exactly.
"""

    async def _generate_basic_info_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> Dict[str, Any]:
        """Generate enhanced basic product information with provider-specific prompts."""
        try:
            prompt = self._build_enhanced_section_prompt('basic_info', context, provider, model)
            response = await self._get_ai_response(prompt, provider, model)

            # Parse the response
            result = self._parse_json_response_dict(response, 'basic_info')

            # Apply strict content filtering to ensure concise output
            filtered_result = self._filter_verbose_content(result, 'basic_info')

            return filtered_result

        except Exception as e:
            logger.error(f"Failed to generate enhanced basic info: {e}")
            return self._get_fallback_basic_info(context)

    def _filter_verbose_content(self, content: Any, section_type: str) -> Any:
        """Filter out verbose content and ensure concise format."""
        try:
            if section_type == 'basic_info' and isinstance(content, dict):
                # Apply strict word limits to each field
                filtered = {}
                for key, value in content.items():
                    if isinstance(value, str):
                        # Apply word limits based on field type
                        if key in ['core_problem', 'core_solution']:
                            # Max 15 words
                            words = value.split()[:15]
                            filtered[key] = ' '.join(words)
                        elif key in ['pain_points', 'challenge']:
                            # Max 25 words
                            words = value.split()[:25]
                            filtered[key] = ' '.join(words)
                        elif key == 'vision_statement':
                            # Max 30 words
                            words = value.split()[:30]
                            filtered[key] = ' '.join(words)
                        else:
                            filtered[key] = value
                    elif isinstance(value, list):
                        # For lists, limit each item to 10 words
                        filtered[key] = [' '.join(str(item).split()[:10]) for item in value[:3]]
                    else:
                        filtered[key] = value
                return filtered
            elif isinstance(content, list):
                # For list content, limit descriptions
                filtered = []
                for item in content:
                    if isinstance(item, dict):
                        filtered_item = {}
                        for key, value in item.items():
                            if key == 'description' and isinstance(value, str):
                                # Max 25 words for descriptions
                                words = value.split()[:25]
                                filtered_item[key] = ' '.join(words)
                            else:
                                filtered_item[key] = value
                        filtered.append(filtered_item)
                    else:
                        filtered.append(item)
                return filtered
            else:
                return content
        except Exception as e:
            logger.warning(f"Failed to filter verbose content: {e}")
            return content

    async def _validate_and_enhance_content(self, content: Any, section_type: str,
                                          context: Dict[str, Any], provider: str, model: str) -> Any:
        """Validate content quality and enhance if needed."""
        try:
            # Quality scoring for different content types
            if isinstance(content, dict):
                quality_score = self._score_dict_content_quality(content, section_type, context)
            elif isinstance(content, list):
                quality_score = self._score_list_content_quality(content, section_type, context)
            else:
                quality_score = 0.5  # Default for unknown types

            logger.info(f"Content quality score for {section_type}: {quality_score:.2f}")

            # Enhancement if quality is below threshold
            if quality_score < 0.75:
                logger.info(f"Enhancing {section_type} content due to low quality score")
                enhanced_content = await self._enhance_content_quality(content, section_type, context, provider, model)
                return enhanced_content

            return content

        except Exception as e:
            logger.warning(f"Content validation failed for {section_type}: {e}")
            return content

    def _score_dict_content_quality(self, content: Dict[str, Any], section_type: str, context: Dict[str, Any]) -> float:
        """Score quality of dictionary content."""
        try:
            score = 0.0
            total_checks = 0

            project_name = context.get('project_name', 'TaskHero AI')

            # Check for specific content vs generic placeholders
            for key, value in content.items():
                total_checks += 1
                if isinstance(value, str):
                    # Check for TaskHero AI specific content
                    if any(term in value.lower() for term in ['taskhero', 'ai-powered', 'intelligent', 'automated']):
                        score += 0.3
                    # Check for specific vs generic content
                    if not any(generic in value.lower() for generic in ['[', 'generic', 'placeholder', 'example']):
                        score += 0.2
                    # Check for meaningful length
                    if len(value) > 20:
                        score += 0.1
                elif isinstance(value, list) and len(value) > 0:
                    score += 0.2

            # Normalize score
            return min(1.0, score / max(1, total_checks)) if total_checks > 0 else 0.5

        except Exception as e:
            logger.warning(f"Failed to score dict content quality: {e}")
            return 0.5

    def _score_list_content_quality(self, content: List[Any], section_type: str, context: Dict[str, Any]) -> float:
        """Score quality of list content."""
        try:
            if not content:
                return 0.0

            score = 0.0
            project_name = context.get('project_name', 'TaskHero AI')

            for item in content:
                if isinstance(item, dict):
                    # Check for specific vs generic content in dict items
                    for key, value in item.items():
                        if isinstance(value, str):
                            if any(term in value.lower() for term in ['taskhero', 'ai-powered', 'intelligent']):
                                score += 0.3
                            if len(value) > 15 and '[' not in value:
                                score += 0.2
                elif isinstance(item, str):
                    if any(term in item.lower() for term in ['taskhero', 'ai-powered', 'intelligent']):
                        score += 0.3
                    if len(item) > 15 and '[' not in item:
                        score += 0.2

            # Normalize score
            return min(1.0, score / len(content))

        except Exception as e:
            logger.warning(f"Failed to score list content quality: {e}")
            return 0.5

    async def _enhance_content_quality(self, content: Any, section_type: str,
                                     context: Dict[str, Any], provider: str, model: str) -> Any:
        """Enhance content quality for low-scoring content."""
        try:
            project_name = context.get('project_name', 'TaskHero AI')
            enhanced_features = context.get('enhanced_features', [])

            enhancement_prompt = f"""
The following {section_type} content for {project_name} needs enhancement to be more specific and relevant:

Current content: {content}

Please enhance this content to:
1. Be more specific to {project_name} (AI-powered project management platform)
2. Include relevant features: {', '.join(enhanced_features[:3])}
3. Remove any generic or placeholder text
4. Make it more compelling and detailed
5. Ensure it reflects TaskHero AI's unique capabilities

Return the enhanced content in the same JSON format as the input.
"""

            response = await self._get_ai_response(enhancement_prompt, provider, model)

            if isinstance(content, dict):
                enhanced = self._parse_json_response_dict(response, section_type)
                return enhanced if enhanced else content
            elif isinstance(content, list):
                enhanced = self._parse_json_response(response, section_type)
                return enhanced if enhanced else content
            else:
                return content

        except Exception as e:
            logger.warning(f"Failed to enhance content quality: {e}")
            return content

    def _get_fallback_basic_info(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback basic info when AI generation fails."""
        project_name = context.get('project_name', 'TaskHero AI')

        return {
            'product_name': project_name,
            'core_problem': 'inefficient project management and task tracking in software development',
            'industry_domain': 'software development and project management',
            'target_users': 'development teams, project managers, and software engineers',
            'pain_points': 'scattered task information, manual status updates, lack of intelligent automation, and poor project visibility',
            'challenge': 'teams struggle to maintain visibility and efficiency in complex projects while managing multiple priorities',
            'core_solution': 'an AI-powered task management and project analysis platform',
            'product_type': 'intelligent project management system',
            'key_benefits': [
                'automate task creation and tracking with AI',
                'provide intelligent insights and project analytics',
                'streamline team collaboration and workflow optimization'
            ],
            'vision_statement': 'To revolutionize project management by making AI-powered automation accessible to every development team, enabling them to focus on creating great products rather than managing processes.'
        }

    async def _generate_basic_info(self, project_name: str, project_type: str, core_features: List[str], provider: str, model: str) -> Dict[str, Any]:
        """Generate basic product information."""
        features_text = f" with features like: {', '.join(core_features)}" if core_features else ""

        prompt = f"""
You are creating a product context document for TaskHero AI, an AI-powered project management and task automation platform. TaskHero AI helps software development teams and project managers automate task creation, track project progress, and optimize workflows using intelligent analysis.

Generate basic product information for TaskHero AI in JSON format:
{{
    "product_name": "TaskHero AI",
    "core_problem": "inefficient project management and task tracking in software development",
    "industry_domain": "software development and project management",
    "target_users": "development teams, project managers, and software engineers",
    "pain_points": "scattered task information, manual status updates, lack of intelligent automation, and poor project visibility",
    "challenge": "teams struggle to maintain visibility and efficiency in complex projects while managing multiple priorities",
    "core_solution": "an AI-powered task management and project analysis platform",
    "product_type": "intelligent project management system",
    "key_benefits": ["automate task creation and tracking with AI", "provide intelligent insights and project analytics", "streamline team collaboration and workflow optimization"],
    "vision_statement": "To revolutionize project management by making AI-powered automation accessible to every development team, enabling them to focus on creating great products rather than managing processes."
}}

Focus on TaskHero AI's core mission: using AI to make project management intelligent and automated for software development teams.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response_dict(response, 'basic_info')

    def _build_problems_solved_prompt(self, context: Dict[str, Any], prompt_config: Dict[str, Any]) -> str:
        """Build enhanced prompt for problems solved generation."""
        project_name = context.get('project_name', 'TaskHero AI')

        return f"""
Generate 5 CONCISE problems that {project_name} solves for software development teams.

IMPORTANT: Follow the reference format exactly:
- Each category should be 2-4 words (e.g., "Task Management Inefficiency")
- Each description should be ONE clear sentence (max 25 words)
- Focus on specific, unique problems that AI solves
- Avoid generic project management descriptions

Return as JSON array with category and description fields only:

[
    {{"category": "Task Management Inefficiency", "description": "Manual task creation and tracking leads to inconsistencies, missed deadlines, and lost productivity"}},
    {{"category": "Poor Project Visibility", "description": "Teams lack real-time insights into project progress, bottlenecks, and resource allocation"}},
    {{"category": "Context Switching Overhead", "description": "Developers lose focus and productivity when switching between different tools and interfaces"}},
    {{"category": "Inconsistent Documentation", "description": "Project documentation becomes outdated and fragmented across multiple platforms"}},
    {{"category": "Knowledge Silos", "description": "Important project knowledge gets trapped with individual team members"}}
]

CRITICAL: Keep descriptions SHORT and SPECIFIC. Each description must be exactly ONE sentence.
"""

    async def _generate_problems_solved_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> List[Dict[str, str]]:
        """Generate enhanced problems solved with provider-specific prompts."""
        try:
            prompt = self._build_enhanced_section_prompt('problems_solved', context, provider, model)
            response = await self._get_ai_response(prompt, provider, model)

            # Parse and filter response
            result = self._parse_json_response(response, 'problems_solved')
            filtered_result = self._filter_verbose_content(result, 'problems_solved')

            return filtered_result

        except Exception as e:
            logger.error(f"Failed to generate enhanced problems solved: {e}")
            return self._get_fallback_problems_solved(context)

    def _get_fallback_problems_solved(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get fallback problems solved when AI generation fails."""
        return [
            {
                "category": "Manual Task Management Inefficiency",
                "description": "TaskHero AI eliminates time-consuming manual task creation by using AI to analyze project requirements and automatically generate comprehensive, context-aware tasks with proper metadata and implementation steps."
            },
            {
                "category": "Context Discovery Challenges",
                "description": "TaskHero AI solves the problem of finding relevant code and documentation in large projects by using intelligent semantic search and multi-pass context discovery to surface the most relevant files and information."
            },
            {
                "category": "Inconsistent Project Documentation",
                "description": "TaskHero AI addresses poor project documentation by automatically generating comprehensive about documents, task descriptions, and project analysis using AI-powered content generation."
            },
            {
                "category": "Workflow Automation Gaps",
                "description": "TaskHero AI bridges workflow automation gaps by providing AI-assisted task management, intelligent kanban boards, and automated project tracking that adapts to team needs."
            },
            {
                "category": "Multi-Provider AI Integration Complexity",
                "description": "TaskHero AI simplifies AI integration by providing a unified interface for multiple AI providers (Ollama, OpenAI, Anthropic) with intelligent fallback mechanisms and optimized prompt engineering."
            }
        ]

    async def _generate_problems_solved(self, project_name: str, project_type: str, provider: str, model: str) -> List[Dict[str, str]]:
        """Generate problems solved by the software."""
        prompt = f"""
Think deeply about the real problems that {project_name} solves for software development teams.

{project_name} is a {project_type} that uses AI to help with project management. What specific pain points does it address? Be creative and think about unique challenges that AI can solve in project management.

Generate 5 unique problems that {project_name} solves. Make each one specific and different. Avoid generic descriptions.

Return as JSON array with category and description fields only. Be creative with problem categories.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'problems_solved')

    # Placeholder enhanced methods for remaining sections
    async def _generate_solution_flow_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> Dict[str, str]:
        """Generate enhanced solution flow with provider-specific prompts."""
        try:
            # Use existing method with enhanced context
            project_name = context.get('project_name', 'TaskHero AI')
            enhanced_features = context.get('enhanced_features', [])
            return await self._generate_solution_flow(project_name, enhanced_features, provider, model)
        except Exception as e:
            logger.error(f"Failed to generate enhanced solution flow: {e}")
            return await self._generate_solution_flow(project_name, [], provider, model)

    async def _generate_how_it_works_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> List[Dict[str, str]]:
        """Generate enhanced how it works with provider-specific prompts."""
        try:
            project_name = context.get('project_name', 'TaskHero AI')
            enhanced_features = context.get('enhanced_features', [])
            return await self._generate_how_it_works(project_name, enhanced_features, provider, model)
        except Exception as e:
            logger.error(f"Failed to generate enhanced how it works: {e}")
            return await self._generate_how_it_works(project_name, [], provider, model)

    async def _generate_ux_goals_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> List[Dict[str, str]]:
        """Generate enhanced UX goals with provider-specific prompts."""
        try:
            project_name = context.get('project_name', 'TaskHero AI')
            project_type = context.get('project_type', 'software application')
            return await self._generate_ux_goals(project_name, project_type, provider, model)
        except Exception as e:
            logger.error(f"Failed to generate enhanced UX goals: {e}")
            return await self._generate_ux_goals(project_name, 'software application', provider, model)

    async def _generate_user_personas_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> List[Dict[str, str]]:
        """Generate enhanced user personas with provider-specific prompts."""
        try:
            project_name = context.get('project_name', 'TaskHero AI')
            project_type = context.get('project_type', 'software application')
            return await self._generate_user_personas(project_name, project_type, provider, model)
        except Exception as e:
            logger.error(f"Failed to generate enhanced user personas: {e}")
            return await self._generate_user_personas(project_name, 'software application', provider, model)

    async def _generate_user_journeys_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> List[Dict[str, Any]]:
        """Generate enhanced user journeys with provider-specific prompts."""
        try:
            project_name = context.get('project_name', 'TaskHero AI')
            return await self._generate_user_journeys(project_name, provider, model)
        except Exception as e:
            logger.error(f"Failed to generate enhanced user journeys: {e}")
            return await self._generate_user_journeys(project_name, provider, model)

    async def _generate_success_metrics_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> List[Dict[str, str]]:
        """Generate enhanced success metrics with provider-specific prompts."""
        try:
            project_name = context.get('project_name', 'TaskHero AI')
            return await self._generate_success_metrics(project_name, provider, model)
        except Exception as e:
            logger.error(f"Failed to generate enhanced success metrics: {e}")
            return await self._generate_success_metrics(project_name, provider, model)

    async def _generate_current_focus_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> Dict[str, Any]:
        """Generate enhanced current focus with provider-specific prompts."""
        try:
            project_name = context.get('project_name', 'TaskHero AI')
            return await self._generate_current_focus(project_name, provider, model)
        except Exception as e:
            logger.error(f"Failed to generate enhanced current focus: {e}")
            return await self._generate_current_focus(project_name, provider, model)

    async def _generate_recent_improvements_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> List[Dict[str, str]]:
        """Generate enhanced recent improvements with provider-specific prompts."""
        try:
            project_name = context.get('project_name', 'TaskHero AI')
            return await self._generate_recent_improvements(project_name, provider, model)
        except Exception as e:
            logger.error(f"Failed to generate enhanced recent improvements: {e}")
            return await self._generate_recent_improvements(project_name, provider, model)

    async def _generate_future_roadmap_enhanced(self, context: Dict[str, Any], provider: str, model: str) -> List[Dict[str, str]]:
        """Generate enhanced future roadmap with provider-specific prompts."""
        try:
            project_name = context.get('project_name', 'TaskHero AI')
            return await self._generate_future_roadmap(project_name, provider, model)
        except Exception as e:
            logger.error(f"Failed to generate enhanced future roadmap: {e}")
            return await self._generate_future_roadmap(project_name, provider, model)

    async def _generate_how_it_works(self, project_name: str, core_features: List[str], provider: str, model: str) -> List[Dict[str, str]]:
        """Generate how the software works."""
        prompt = f"""
Generate 4 CONCISE features that explain how {project_name} works.

IMPORTANT: Follow the reference format exactly:
- Each name should be 3-6 words (e.g., "AI-Powered Task Creation")
- Each description should be ONE clear sentence (max 30 words)
- Focus on specific AI capabilities
- Avoid generic project management features

Return as JSON array with name and description fields:

[
    {{"name": "AI-Powered Task Creation", "description": "Automatically generate detailed, actionable tasks from high-level requirements using advanced AI analysis"}},
    {{"name": "Intelligent Project Analysis", "description": "Analyze codebase structure and project patterns to provide contextual insights and recommendations"}},
    {{"name": "Automated Workflow Integration", "description": "Seamlessly integrate with existing development tools and Git workflows for minimal disruption"}},
    {{"name": "Real-time Progress Tracking", "description": "Monitor project progress with intelligent metrics and automated status updates"}}
]

CRITICAL: Keep descriptions SHORT and SPECIFIC. Each description must be exactly ONE sentence.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'how_it_works')

    async def _generate_ux_goals(self, project_name: str, project_type: str, provider: str, model: str) -> List[Dict[str, str]]:
        """Generate UX goals."""
        prompt = f"""
Generate 4 CONCISE user experience goals for {project_name}.

IMPORTANT: Follow the reference format exactly:
- Each name should be 3-5 words (e.g., "Minimal Learning Curve")
- Each description should be ONE clear sentence (max 25 words)
- Focus on developer productivity and ease of use
- Avoid generic UX descriptions

Return as JSON array with name and description fields:

[
    {{"name": "Minimal Learning Curve", "description": "Developers can start using the system immediately without extensive training"}},
    {{"name": "Context-Aware Interface", "description": "UI adapts to current project context and user workflow patterns"}},
    {{"name": "Intelligent Automation", "description": "System handles routine tasks automatically while keeping users informed"}},
    {{"name": "Unified Workspace", "description": "Single interface for all project management and development activities"}}
]

CRITICAL: Keep descriptions SHORT and SPECIFIC. Each description must be exactly ONE sentence.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'ux_goals')

    async def _generate_user_personas(self, project_name: str, project_type: str, provider: str, model: str) -> List[Dict[str, str]]:
        """Generate user personas."""
        prompt = f"""
Generate 4 CONCISE user personas for {project_name}.

IMPORTANT: Follow the reference format exactly:
- Each name should be a job title (e.g., "Senior Developer/Tech Lead")
- Each description should be ONE clear sentence (max 30 words)
- Focus on their role and needs
- Avoid long biographical details

Return as JSON array with name and description fields:

[
    {{"name": "Senior Developer/Tech Lead", "description": "Experienced developers who need to manage complex projects and coordinate team efforts while maintaining code quality"}},
    {{"name": "Project Manager", "description": "Non-technical project managers who need clear visibility into development progress and team productivity"}},
    {{"name": "Solo Developer/Freelancer", "description": "Independent developers working on multiple projects who need efficient task management and project organization"}},
    {{"name": "Development Team Lead", "description": "Team leaders who balance hands-on coding with team management and project coordination responsibilities"}}
]

CRITICAL: Keep descriptions SHORT and SPECIFIC. Each description must be exactly ONE sentence.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'user_personas')

    async def _generate_user_journeys(self, project_name: str, provider: str, model: str) -> List[Dict[str, Any]]:
        """Generate user journeys."""
        prompt = f"""
Generate 3 CONCISE user journeys for {project_name}.

IMPORTANT: Follow the reference format exactly:
- Each name should be 3-5 words (e.g., "New Project Setup")
- Each journey should have exactly 5 steps
- Each step should be ONE clear action (max 15 words)
- Focus on realistic development workflows

Return as JSON array:

[
    {{"name": "New Project Setup", "steps": ["Clone or create new project repository", "Run TaskHero AI initialization to analyze codebase", "Review AI-generated project insights and recommendations", "Set up initial task board and project goals", "Configure team access and collaboration settings"]}},
    {{"name": "Daily Development Workflow", "steps": ["Check task dashboard for daily priorities", "Use AI task creator for new feature requirements", "Track progress automatically as code changes", "Review AI-generated insights and suggestions", "Update project status with minimal manual effort"]}},
    {{"name": "Project Analysis and Optimization", "steps": ["Generate comprehensive project analysis report", "Review codebase metrics and complexity insights", "Identify potential bottlenecks and optimization opportunities", "Plan future development phases based on AI recommendations", "Share insights with stakeholders and team members"]}}
]

CRITICAL: Keep steps SHORT and SPECIFIC. Each step must be exactly ONE action.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'user_journeys')

    async def _generate_success_metrics(self, project_name: str, provider: str, model: str) -> List[Dict[str, str]]:
        """Generate success metrics."""
        prompt = f"""
Generate 5 CONCISE success metrics for {project_name}.

IMPORTANT: Follow the reference format exactly:
- Each name should be 3-6 words (e.g., "Task Creation Efficiency")
- Each description should be ONE clear sentence (max 20 words)
- Each target should be specific and measurable
- Focus on productivity improvements

Return as JSON array with name, description, and target fields:

[
    {{"name": "Task Creation Efficiency", "description": "Time reduction in creating detailed, actionable tasks", "target": "70% reduction in task creation time"}},
    {{"name": "Project Visibility Score", "description": "Team understanding of project status and priorities", "target": "90% team alignment on project goals"}},
    {{"name": "Development Velocity", "description": "Increase in feature delivery speed", "target": "40% improvement in sprint completion rates"}},
    {{"name": "Context Switch Reduction", "description": "Decrease in time spent switching between tools", "target": "50% reduction in tool-switching overhead"}},
    {{"name": "Documentation Quality", "description": "Consistency and completeness of project documentation", "target": "85% of tasks have complete, up-to-date documentation"}}
]

CRITICAL: Keep descriptions SHORT and SPECIFIC. Each description must be exactly ONE sentence.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'success_metrics')

    async def _generate_current_focus(self, project_name: str, provider: str, model: str) -> Dict[str, Any]:
        """Generate current product focus."""
        prompt = f"""
Describe the current product focus for {project_name}, an AI-powered project management platform.

Think about what {project_name} should be prioritizing right now to best serve software development teams. What area of development would have the biggest impact?

Generate a JSON response with:
{{
    "area": "current focus area name",
    "approach": "how you'll achieve this focus",
    "benefits": [
        {{"name": "Benefit Name", "description": "What this benefit provides", "target": "specific measurable target or empty string"}},
        {{"name": "Benefit Name", "description": "What this benefit provides", "target": "specific measurable target or empty string"}}
    ],
    "next_steps": "what happens after current focus is completed"
}}

Be creative and think about what would truly move the needle for AI-powered project management.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response_dict(response, 'current_focus')

    async def _generate_recent_improvements(self, project_name: str, provider: str, model: str) -> List[Dict[str, str]]:
        """Generate recent improvements."""
        prompt = f"""
Generate 4 CONCISE recent improvements for {project_name}.

IMPORTANT: Follow the reference format exactly:
- Each name should be 3-6 words (e.g., "Enhanced Template System")
- Each description should be ONE clear sentence (max 30 words)
- Focus on specific AI improvements
- Avoid technical jargon and long explanations

Return as JSON array with name and description fields:

[
    {{"name": "Enhanced Template System", "description": "Implemented comprehensive Jinja2-based templating for all document types with AI-powered content generation"}},
    {{"name": "AI-Powered Task Creation", "description": "Added intelligent task generation with context awareness, quality validation, and automated requirements analysis"}},
    {{"name": "Advanced Project Analysis", "description": "Integrated deep codebase analysis with architectural insights and optimization recommendations"}},
    {{"name": "Improved User Experience", "description": "Streamlined workflows with better navigation, context-aware interfaces, and reduced cognitive load"}}
]

CRITICAL: Keep descriptions SHORT and SPECIFIC. Each description must be exactly ONE sentence.
"""

        response = await self._get_ai_response(prompt, provider, model)
        result = self._parse_json_response(response, 'recent_improvements')
        return self._filter_verbose_content(result, 'recent_improvements')

    async def _generate_future_roadmap(self, project_name: str, provider: str, model: str) -> List[Dict[str, str]]:
        """Generate future roadmap."""
        prompt = f"""
Create a 5-phase future roadmap for {project_name} that shows the evolution of AI-powered project management.

Think about how {project_name} should grow and evolve to better serve software development teams. What features and capabilities would create the most value over time?

Each phase should:
- Have a realistic time period (quarters or years)
- Focus on a major theme or capability area
- Build logically on previous phases
- Be specific to AI and project management innovation

Return as JSON array:
[{{"time_period": "Q1 2025", "focus": "description of what this phase accomplishes"}}]

Be creative and think about the future of AI in project management.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'future_roadmap')

    async def _generate_solution_flow(self, project_name: str, core_features: List[str], provider: str, model: str) -> Dict[str, str]:
        """Generate solution flow diagram content."""
        features_text = f" including features like: {', '.join(core_features[:3])}" if core_features else ""

        prompt = f"""
Create a unique solution flow for {project_name}, an AI-powered project management platform{features_text}.

Think creatively about how {project_name} specifically transforms user problems into solutions. Consider the unique aspects of AI-powered project management.

Generate a JSON response with:
{{
    "flow_description": "Your unique description of how {project_name} works",
    "flow_steps": [
        {{"step": "Step Name", "description": "Step description"}},
        {{"step": "Step Name", "description": "Step description"}}
    ],
    "mermaid_diagram": "Your unique mermaid flowchart or graph"
}}

Make this truly unique to {project_name}. Be creative with step names and the mermaid diagram structure.
Focus on what makes {project_name} special and innovative in the AI space.

Return ONLY valid JSON.
"""

        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response_dict(response, 'solution_flow')

    async def _get_ai_response(self, prompt: str, provider: str, model: str) -> str:
        """Get AI response using the configured provider."""
        try:
            # Import the AI response generation function from the correct module
            from ..llms import generate_response

            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: generate_response(messages, provider=provider, model=model, temperature=0.7, parse_thinking=True)
            )

            # Handle tuple response (full_response, think_tokens, clean_response)
            if isinstance(response, tuple) and len(response) >= 3:
                return response[2]  # Return the clean response (thinking tokens removed)
            elif isinstance(response, tuple) and len(response) >= 1:
                return response[0]  # Return the first element if tuple is shorter
            else:
                return str(response)  # Convert to string if not a tuple

        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            raise

    def _parse_json_response(self, response: str, content_type: str) -> List[Dict[str, Any]]:
        """Parse JSON response from AI, with fallback to default values."""
        try:
            import json
            import re

            # Extract JSON from response
            json_pattern = r'\[[\s\S]*\]'
            match = re.search(json_pattern, response)

            if match:
                json_data = json.loads(match.group(0))
                if isinstance(json_data, list) and len(json_data) > 0:
                    # Ensure required fields exist for specific content types
                    if content_type == 'success_metrics':
                        for item in json_data:
                            if 'target' not in item:
                                item['target'] = 'TBD'
                    return json_data

        except Exception as e:
            logger.warning(f"Failed to parse AI JSON response for {content_type}: {e}")

        # Return default fallback
        return []

    def _parse_json_response_dict(self, response: str, content_type: str) -> Dict[str, Any]:
        """Parse JSON response that should return a dictionary."""
        try:
            import json
            import re

            # Extract JSON from response
            json_pattern = r'\{[\s\S]*\}'
            match = re.search(json_pattern, response)

            if match:
                json_data = json.loads(match.group(0))
                if isinstance(json_data, dict):
                    # Ensure required fields exist for specific content types
                    if content_type == 'current_focus':
                        if 'benefits' in json_data and isinstance(json_data['benefits'], list):
                            for benefit in json_data['benefits']:
                                if 'target' not in benefit:
                                    benefit['target'] = ''
                    return json_data

        except Exception as e:
            logger.warning(f"Failed to parse AI JSON response for {content_type}: {e}")

        # Return content-specific fallbacks
        if content_type == 'current_focus':
            return {
                'area': 'core functionality improvement',
                'approach': 'iterative development and user feedback integration',
                'benefits': [
                    {'name': 'Enhanced User Experience', 'description': 'Improved interface and functionality', 'target': 'Increase user satisfaction'},
                    {'name': 'Better Performance', 'description': 'Optimized core features', 'target': 'Reduce load times'},
                    {'name': 'Expanded Capabilities', 'description': 'New features and integrations', 'target': 'Meet user needs'}
                ],
                'next_steps': 'Continue gathering user feedback and implementing improvements based on usage patterns'
            }
        elif content_type == 'basic_info':
            return {
                'product_name': 'TaskHero AI',
                'core_problem': 'inefficient project management and task tracking in software development',
                'industry_domain': 'software development and project management',
                'target_users': 'development teams, project managers, and software engineers',
                'pain_points': 'scattered task information, manual status updates, lack of intelligent automation, and poor project visibility',
                'challenge': 'teams struggle to maintain visibility and efficiency in complex projects while managing multiple priorities',
                'core_solution': 'an AI-powered task management and project analysis platform',
                'product_type': 'intelligent project management system',
                'key_benefits': ['automate task creation and tracking with AI', 'provide intelligent insights and project analytics', 'streamline team collaboration and workflow optimization'],
                'vision_statement': 'To revolutionize project management by making AI-powered automation accessible to every development team, enabling them to focus on creating great products rather than managing processes.'
            }
        elif content_type == 'solution_flow':
            return {
                'flow_description': 'TaskHero AI transforms project management challenges into automated solutions through intelligent analysis and AI-powered workflows',
                'flow_steps': [
                    {'step': 'User Problem/Need', 'description': 'Software teams face challenges with manual task management and lack of project visibility'},
                    {'step': 'Problem Analysis', 'description': 'TaskHero AI analyzes project requirements and team workflows to understand specific needs'},
                    {'step': 'AI Solution Components', 'description': 'Three core components: AI-Powered Automation, Intelligent Analysis, and Streamlined Workflow'},
                    {'step': 'Feature Implementation', 'description': 'These components deliver specific features like automated task creation, real-time insights, and team collaboration'},
                    {'step': 'User Success', 'description': 'Teams achieve improved productivity, better project visibility, and reduced manual effort'},
                    {'step': 'Continuous Improvement', 'description': 'User feedback and AI learning drive ongoing platform enhancements'}
                ],
                'mermaid_diagram': 'graph TD\n    A[User Problem/Need] --> B{Problem Analysis}\n    B --> C[TaskHero AI Solution]\n    C --> D[Core Features]\n    D --> E[AI-Powered Automation]\n    D --> F[Intelligent Analysis]\n    D --> G[Streamlined Workflow]\n    E --> H[Task Generation]\n    F --> I[Project Insights]\n    G --> J[Team Collaboration]\n    H --> K[User Success]\n    I --> K\n    J --> K\n    K --> L{Continuous Improvement}\n    L --> C'
            }

        # Return default fallback for other content types
        return {}

    def prepare_about_context(self, **kwargs) -> Dict[str, Any]:
        """Prepare the context for about template rendering."""
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Base context with provided data (from AI generation)
        context = {
            'current_date': current_date,
            **kwargs  # Use all provided AI-generated data
        }

        return context

    def render_about_template(self, context: Dict[str, Any]) -> str:
        """Render the about template with the provided context."""
        try:
            return self.template_engine.render_template(self.about_template, context)
        except Exception as e:
            logger.error(f"About template rendering failed: {e}")
            raise

    def generate_about_filename(self, product_name: str) -> str:
        """Generate filename for the about document."""
        try:
            # Always use "about.md" for the project analysis folder
            filename = "about.md"
            return filename
        except Exception as e:
            logger.error(f"Filename generation failed: {e}")
            return "about.md"

    def _save_about_file(self, filename: str, content: str) -> Path:
        """Save the about document to file."""
        try:
            file_path = self.output_dir / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return file_path

        except Exception as e:
            logger.error(f"Error saving about file: {e}")
            raise

    def list_about_files(self) -> List[Path]:
        """List all about files in the output directory."""
        try:
            return list(self.output_dir.glob("about*.md"))
        except Exception as e:
            logger.error(f"Error listing about files: {e}")
            return []