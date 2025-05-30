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
        """Get project analysis from the AI manager."""
        try:
            if self.ai_manager and hasattr(self.ai_manager, 'project_analyzer'):
                project_analyzer = self.ai_manager.project_analyzer
                if project_analyzer:
                    # Try to get existing project info first
                    project_info = project_analyzer.load_project_info()
                    if not project_info:
                        # Generate new project analysis
                        logger.info("Generating project analysis for about document")
                        project_info = project_analyzer.collect_project_info()
                    return project_info
        except Exception as e:
            logger.warning(f"Failed to get project analysis: {e}")
        return None

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
            
            # Generate content section by section with proper numbering
            print("📋 Section 1: Why TaskHero AI Exists & Vision Statement generation...")
            basic_info = await self._generate_basic_info(project_name, project_type, core_features, provider, model)
            
            print("🔍 Section 3: Problems Solved generation...")
            problems_solved = await self._generate_problems_solved(project_name, project_type, provider, model)
            
            print("📊 Section 4: Solution Flow Diagram generation...")
            solution_flow = await self._generate_solution_flow(project_name, core_features, provider, model)
            
            print("⚙️ Section 5: How TaskHero AI Works generation...")
            how_it_works = await self._generate_how_it_works(project_name, core_features, provider, model)
            
            print("🎨 Section 6: User Experience Goals generation...")
            ux_goals = await self._generate_ux_goals(project_name, project_type, provider, model)
            
            print("👥 Section 7: Target Users generation...")
            user_personas = await self._generate_user_personas(project_name, project_type, provider, model)
            
            print("🚶‍♂️ Section 8: Key User Journeys generation...")
            user_journeys = await self._generate_user_journeys(project_name, provider, model)
            
            print("📊 Section 9: Success Metrics generation...")
            success_metrics = await self._generate_success_metrics(project_name, provider, model)
            
            print("🎯 Section 10: Current Product Focus generation...")
            current_focus = await self._generate_current_focus(project_name, provider, model)
            
            print("🚀 Section 11: Recent Improvements generation...")
            recent_improvements = await self._generate_recent_improvements(project_name, provider, model)
            
            print("📈 Section 12: Future Roadmap generation...")
            future_roadmap = await self._generate_future_roadmap(project_name, provider, model)
            
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

    async def _generate_how_it_works(self, project_name: str, core_features: List[str], provider: str, model: str) -> List[Dict[str, str]]:
        """Generate how the software works."""
        prompt = f"""
Describe how {project_name} works by explaining its core capabilities{f" (considering these features: {', '.join(core_features[:3])})" if core_features else ""}.

Focus on the unique AI-powered capabilities that make {project_name} different from traditional project management tools.

Generate 4 core features that explain how {project_name} works. Each should:
- Have a descriptive name
- Explain the AI/technology behind it
- Show the benefit to users

Be creative and technical. Avoid generic project management features.

Return as JSON array with name and description fields.
"""
        
        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'how_it_works')

    async def _generate_ux_goals(self, project_name: str, project_type: str, provider: str, model: str) -> List[Dict[str, str]]:
        """Generate UX goals."""
        prompt = f"""
Create 4 unique user experience goals for {project_name}, a {project_type}.

Think about what would make {project_name} exceptional to use for software development teams. What UX principles would make it stand out from other project management tools?

Focus on goals that enhance developer productivity, reduce friction, and improve team collaboration through smart design.

Return as JSON array with name and description fields. Be creative and specific to AI-powered project management.
"""
        
        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'ux_goals')

    async def _generate_user_personas(self, project_name: str, project_type: str, provider: str, model: str) -> List[Dict[str, str]]:
        """Generate user personas."""
        prompt = f"""
Create 4 realistic and unique user personas for {project_name}, a {project_type}.

Think about real people who would use an AI-powered project management tool. Give each persona:
- A real name and job title
- Specific background and experience
- Unique challenges they face
- How they would specifically use {project_name}

Make each persona feel like a real person with individual needs, not generic role descriptions.

Return as JSON array with name and description fields.
"""
        
        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'user_personas')

    async def _generate_user_journeys(self, project_name: str, provider: str, model: str) -> List[Dict[str, Any]]:
        """Generate user journeys."""
        prompt = f"""
Create 3 unique user journeys for {project_name} that show how different users would interact with the platform.

Think about realistic scenarios where teams would use an AI-powered project management tool. Each journey should:
- Have a descriptive name that reflects the scenario
- Include 4-6 realistic steps that users would take
- Show how AI features enhance the experience

Focus on real workflows that software teams experience daily.

Return as JSON array:
[{{"name": "Journey Name", "steps": ["Step 1", "Step 2", "Step 3", "Step 4"]}}]

Be creative with journey names and make steps specific to AI-powered project management.
"""
        
        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'user_journeys')

    async def _generate_success_metrics(self, project_name: str, provider: str, model: str) -> List[Dict[str, str]]:
        """Generate success metrics."""
        prompt = f"""
Create 5 unique success metrics that would measure the effectiveness of {project_name} for software development teams.

Think about what outcomes matter most when AI is helping with project management. What would prove that {project_name} is actually improving team performance?

Each metric should:
- Have a descriptive name
- Explain what it measures
- Include a realistic target that teams could achieve

Focus on metrics that are specific to AI-powered project management, not generic project management KPIs.

Return as JSON array with name, description, and target fields.
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
Create 4 recent improvements that {project_name} has implemented to enhance AI-powered project management.

Think about realistic enhancements that would make {project_name} more valuable for software development teams. What features or improvements would users actually notice and appreciate?

Each improvement should:
- Have a compelling name that describes the enhancement
- Explain the technical approach or implementation
- Show the benefit to users

Focus on improvements that are specific to AI and project management, not generic software updates.

Return as JSON array with name and description fields.
"""
        
        response = await self._get_ai_response(prompt, provider, model)
        return self._parse_json_response(response, 'recent_improvements')

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