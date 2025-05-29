#!/usr/bin/env python3
"""
Automated test script to validate kanban task generation quality.
Compares generated task against TASK-003 reference with 90% similarity target.
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from difflib import SequenceMatcher

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mods.project_management.ai_task_creator import AITaskCreator
from mods.project_management.task_manager import TaskManager

class KanbanTaskQualityTester:
    def __init__(self):
        self.reference_file = Path("theherotasks/done/TASK-003-DEV-kanban-visualization.md")
        self.test_data = {
            "title": "Implement Kanban Board Visualization",
            "description": "Create a visual Kanban board system that displays tasks in Todo, InProgress, and Done columns with proper formatting and status indicators. This will provide users with an intuitive visual interface for managing their project tasks within the terminal environment.",
            "task_type": "Development",
            "priority": "Medium",
            "assigned_to": "Developer",
            "tags": "visualization, kanban, ui, terminal, rich"
        }
        self.similarity_target = 90.0

    def load_reference_task(self) -> dict:
        """Load and parse the reference TASK-003 file."""
        try:
            with open(self.reference_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract key sections for comparison
            reference = {
                'content': content,
                'has_kanban_terms': self._count_kanban_terms(content),
                'has_proper_flow': self._check_kanban_flow(content),
                'implementation_steps': self._extract_implementation_steps(content),
                'requirements': self._extract_requirements(content),
                'technical_considerations': self._extract_technical_considerations(content)
            }

            print(f"✅ Reference task loaded: {len(content)} characters")
            print(f"   📊 Kanban terms found: {reference['has_kanban_terms']}")
            print(f"   🔄 Proper kanban flow: {reference['has_proper_flow']}")

            return reference

        except Exception as e:
            print(f"❌ Failed to load reference task: {e}")
            return None

    def _count_kanban_terms(self, content: str) -> int:
        """Count kanban-related terms in content."""
        kanban_terms = [
            'kanban', 'board', 'column', 'todo', 'inprogress', 'done',
            'drag', 'drop', 'move', 'status', 'card', 'visual', 'terminal',
            'rich', 'formatting', 'display', 'interface'
        ]
        content_lower = content.lower()
        return sum(1 for term in kanban_terms if term in content_lower)

    def _check_kanban_flow(self, content: str) -> bool:
        """Check if content has proper kanban workflow."""
        kanban_flow_indicators = [
            'todo', 'inprogress', 'done', 'column', 'move', 'status'
        ]
        content_lower = content.lower()
        return sum(1 for indicator in kanban_flow_indicators if indicator in content_lower) >= 4

    def _extract_implementation_steps(self, content: str) -> list:
        """Extract implementation steps from content."""
        steps = []
        lines = content.split('\n')
        in_implementation = False

        for line in lines:
            if 'implementation steps' in line.lower():
                in_implementation = True
                continue
            elif in_implementation and line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '*')):
                steps.append(line.strip())
            elif in_implementation and line.strip() and not line.startswith(' '):
                break

        return steps

    def _extract_requirements(self, content: str) -> list:
        """Extract requirements from content."""
        requirements = []
        lines = content.split('\n')
        in_requirements = False

        for line in lines:
            if 'acceptance criteria' in line.lower() or 'requirements' in line.lower():
                in_requirements = True
                continue
            elif in_requirements and ('- [ ]' in line or '- [x]' in line or line.strip().startswith('-')):
                requirements.append(line.strip())
            elif in_requirements and line.strip() and line.startswith('#'):
                break

        return requirements

    def _extract_technical_considerations(self, content: str) -> str:
        """Extract technical considerations section."""
        lines = content.split('\n')
        in_tech = False
        tech_content = []

        for line in lines:
            if 'technical considerations' in line.lower():
                in_tech = True
                continue
            elif in_tech and line.startswith('#') and line.strip() != '':
                break
            elif in_tech:
                tech_content.append(line)

        return '\n'.join(tech_content).strip()

    async def generate_test_task(self) -> tuple:
        """Generate a new kanban task using the progressive wizard (simulating menu option 10)."""
        try:
            print("\n🚀 Simulating Progressive Task Creation Wizard (Menu Option 10)...")

            # Initialize task creator
            project_root = os.path.abspath(".")
            ai_task_creator = AITaskCreator(project_root)

            # Simulate the progressive wizard steps
            print("📝 Step 1/4: Basic Information")
            print("=" * 40)

            # Step 1: Set up the basic information (simulating user input)
            ai_task_creator.creation_state['collected_data'] = {
                'title': self.test_data["title"],
                'description': self.test_data["description"],
                'task_type': self.test_data["task_type"],
                'priority': self.test_data["priority"],
                'assigned_to': self.test_data["assigned_to"],
                'tags': [tag.strip() for tag in self.test_data["tags"].split(",")]
            }
            print(f"✅ Title: {self.test_data['title']}")
            print(f"✅ Description: {self.test_data['description'][:100]}...")
            print(f"✅ Type: {self.test_data['task_type']}")
            print(f"✅ Priority: {self.test_data['priority']}")
            print(f"✅ Tags: {self.test_data['tags']}")

            # Step 2: Context Discovery & Selection (automated for testing)
            print("\n🔍 Step 2/4: Context Discovery & Selection")
            print("=" * 40)
            print("🔍 Searching for relevant context...")

            # Simulate context selection step
            success = await self._simulate_context_selection_step(ai_task_creator)
            if not success:
                print("❌ Context selection failed")
                return None, None

            # Step 3: AI Enhancement & Preview (automated for testing)
            print("\n🧠 Step 3/4: AI Enhancement & Preview")
            print("=" * 60)

            # Simulate AI enhancement step
            success = await self._simulate_ai_enhancement_step(ai_task_creator)
            if not success:
                print("❌ AI enhancement failed")
                return None, None

            # Step 4: Final Review & Creation
            print("\n📄 Step 4/4: Final Review & Creation")
            print("=" * 40)

            # Simulate final creation step
            success, task_id, file_path = await self._simulate_final_creation_step(ai_task_creator)
            if not success:
                print(f"❌ Task creation failed: {file_path}")
                return None, None

            # Read the generated file
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                with open(file_path_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ Test task generated: {file_path}")
                return file_path_obj, content
            else:
                print(f"❌ Generated file not found: {file_path}")
                return None, None

        except Exception as e:
            print(f"❌ Task generation error: {e}")
            return None, None

    async def _simulate_context_selection_step(self, ai_task_creator) -> bool:
        """Simulate the context selection step of the progressive wizard."""
        try:
            data = ai_task_creator.creation_state['collected_data']

            # Collect context using the same method as the progressive wizard
            combined_text = f"{data['title']} {data['description']}"
            if data.get('tags'):
                tags_text = ' '.join(data['tags'])
                combined_text = f"{combined_text} {tags_text}"

            # Use the enhanced Graphiti context collection (same as progressive wizard)
            context_chunks = await ai_task_creator._collect_context_with_graphiti(
                combined_text, data
            )

            if context_chunks:
                print(f"📁 Found {len(context_chunks)} relevant context files")

                # Display top 5 context files (simulating the enhanced context selection)
                for i, chunk in enumerate(context_chunks[:5], 1):
                    file_name = os.path.basename(chunk.file_path)
                    print(f"{i:2d}. {file_name:<50} | Score: {chunk.relevance_score:.3f}")
                    if "TASK-003" in chunk.file_path:
                        print(f"    ⭐ FOUND TASK-003! (Reference task)")

                # Auto-select top 3 files for testing (simulating 'auto' selection)
                selected_context = context_chunks[:3]
                ai_task_creator.creation_state['selected_context'] = selected_context
                print(f"✅ Auto-selected top {len(selected_context)} context files")
                return True
            else:
                print("⚠️  No relevant context found, proceeding without context")
                ai_task_creator.creation_state['selected_context'] = []
                return True

        except Exception as e:
            print(f"❌ Context selection error: {e}")
            return False

    async def _simulate_ai_enhancement_step(self, ai_task_creator) -> bool:
        """Simulate the AI enhancement step of the progressive wizard."""
        try:
            data = ai_task_creator.creation_state['collected_data']

            # Use the same comprehensive AI enhancement as the progressive wizard
            from mods.project_management.ai_task_creator import AIEnhancementProgressTracker
            progress_tracker = AIEnhancementProgressTracker()

            # Initialize AI provider
            progress_tracker.start_step("🚀 Initializing AI provider...")
            ai_ready = await ai_task_creator._initialize_ai_provider()
            if not ai_ready:
                progress_tracker.fail_step("❌ AI provider initialization failed")
                print("⚠️  Continuing with basic enhancement...")
                return True  # Continue without AI enhancement
            progress_tracker.complete_step("✅ AI provider ready")

            # Prepare enhancement context
            progress_tracker.start_step("📋 Preparing enhancement context...")
            context = {
                'title': data['title'],
                'description': data['description'],
                'task_type': data['task_type'],
                'priority': data['priority'],
                'assigned_to': data['assigned_to'],
                'tags': data['tags']
            }
            progress_tracker.complete_step("✅ Context prepared")

            # Run comprehensive AI enhancement
            progress_tracker.start_step("🤖 AI is analyzing your task with selected context...")
            enhanced_context = await ai_task_creator._comprehensive_ai_enhancement(
                context, data['description'], progress_tracker
            )

            if enhanced_context:
                # Calculate quality score
                progress_tracker.start_step("📊 Calculating quality metrics...")
                quality_score = ai_task_creator._calculate_enhancement_quality_score(enhanced_context)
                ai_task_creator.creation_state['quality_score'] = quality_score
                progress_tracker.complete_step("✅ Quality assessment complete")

                # Store enhancements
                ai_task_creator.creation_state['ai_enhancements'] = enhanced_context

                # Display enhancement summary
                ai_task_creator._display_enhancement_summary(enhanced_context, quality_score, progress_tracker)

                # Auto-proceed for testing (simulating user pressing 'Y')
                print("\n✅ AI enhancement applied successfully (auto-proceeding for test)")
                return True
            else:
                print("❌ AI enhancement failed")
                return False

        except Exception as e:
            print(f"❌ AI enhancement error: {e}")
            return False

    async def _simulate_final_creation_step(self, ai_task_creator) -> tuple:
        """Simulate the final creation step of the progressive wizard."""
        try:
            data = ai_task_creator.creation_state['collected_data']
            enhancements = ai_task_creator.creation_state['ai_enhancements']

            # Create the task using enhanced data (same as progressive wizard)
            success, task_id, file_path = await ai_task_creator.create_enhanced_task(
                title=data['title'],
                description=data['description'],
                task_type=data['task_type'],
                priority=data['priority'],
                assigned_to=data['assigned_to'],
                tags=data['tags'],
                use_ai_enhancement=False,  # Already enhanced
                ai_enhancements=enhancements
            )

            if success:
                print(f"✅ Task {task_id} created successfully!")
                print(f"📁 File: {file_path}")
            else:
                print(f"❌ Task creation failed: {file_path}")

            return success, task_id, file_path

        except Exception as e:
            print(f"❌ Final creation error: {e}")
            return False, "", str(e)

    def analyze_generated_task(self, generated_content: str, reference: dict) -> dict:
        """Analyze the generated task against the reference."""
        analysis = {
            'kanban_terms': self._count_kanban_terms(generated_content),
            'has_proper_flow': self._check_kanban_flow(generated_content),
            'implementation_steps': self._extract_implementation_steps(generated_content),
            'requirements': self._extract_requirements(generated_content),
            'technical_considerations': self._extract_technical_considerations(generated_content),
            'content_similarity': 0.0,
            'structure_similarity': 0.0,
            'kanban_relevance': 0.0,
            'full_content': generated_content  # Store for contamination analysis
        }

        # Calculate content similarity
        matcher = SequenceMatcher(None, reference['content'], generated_content)
        analysis['content_similarity'] = matcher.ratio() * 100

        # Calculate structure similarity (sections present)
        ref_sections = len([s for s in [reference['implementation_steps'], reference['requirements']] if s])
        gen_sections = len([s for s in [analysis['implementation_steps'], analysis['requirements']] if s])
        analysis['structure_similarity'] = (gen_sections / max(ref_sections, 1)) * 100

        # Calculate kanban relevance
        kanban_score = 0
        if analysis['kanban_terms'] >= reference['has_kanban_terms'] * 0.7:
            kanban_score += 40
        if analysis['has_proper_flow']:
            kanban_score += 30
        if any('kanban' in step.lower() for step in analysis['implementation_steps']):
            kanban_score += 30
        analysis['kanban_relevance'] = kanban_score

        return analysis

    def calculate_overall_quality(self, analysis: dict) -> float:
        """Calculate overall quality score."""
        weights = {
            'kanban_relevance': 0.4,      # 40% - Most important
            'structure_similarity': 0.3,   # 30% - Structure matters
            'content_similarity': 0.3      # 30% - Content quality
        }

        score = (
            analysis['kanban_relevance'] * weights['kanban_relevance'] +
            analysis['structure_similarity'] * weights['structure_similarity'] +
            analysis['content_similarity'] * weights['content_similarity']
        )

        return score

    def display_results(self, analysis: dict, quality_score: float):
        """Display detailed test results."""
        print("\n" + "="*80)
        print("📊 KANBAN TASK QUALITY ANALYSIS RESULTS")
        print("="*80)

        print(f"\n🎯 Overall Quality Score: {quality_score:.1f}% (Target: {self.similarity_target}%)")

        status = "✅ PASS" if quality_score >= self.similarity_target else "❌ FAIL"
        print(f"🏆 Test Result: {status}")

        print(f"\n📋 Detailed Metrics:")
        print(f"   🔤 Kanban Relevance: {analysis['kanban_relevance']:.1f}%")
        print(f"   📐 Structure Similarity: {analysis['structure_similarity']:.1f}%")
        print(f"   📝 Content Similarity: {analysis['content_similarity']:.1f}%")

        print(f"\n🔍 Content Analysis:")
        print(f"   📊 Kanban terms found: {analysis['kanban_terms']}")
        print(f"   🔄 Proper kanban flow: {analysis['has_proper_flow']}")
        print(f"   📋 Implementation steps: {len(analysis['implementation_steps'])}")
        print(f"   ✅ Requirements found: {len(analysis['requirements'])}")

        # Check for specific issues
        print(f"\n⚠️  Issues Detected:")
        issues = []

        if analysis['kanban_terms'] < 10:
            issues.append("Low kanban terminology usage")
        if not analysis['has_proper_flow']:
            issues.append("Missing proper kanban workflow")
        if len(analysis['implementation_steps']) < 5:
            issues.append("Insufficient implementation steps")
        if any('search' in step.lower() for step in analysis['implementation_steps']):
            issues.append("❌ CRITICAL: Search-related content in kanban task!")

        if issues:
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("   ✅ No major issues detected")

    async def run_test(self):
        """Run the complete kanban task quality test with two approaches."""
        print("🧪 Starting Kanban Task Quality Test")
        print("="*50)

        # Load reference task
        reference = self.load_reference_task()
        if not reference:
            return False

        print("\n" + "=" * 80)
        print("🎯 TEST 1: CONTEXT-AWARE GENERATION (With TASK-003 Reference)")
        print("=" * 80)

        # Generate test task using context discovery (original test)
        file_path_1, generated_content_1 = await self.generate_test_task()
        if not generated_content_1:
            return False

        # Analyze generated task 1
        analysis_1 = self.analyze_generated_task(generated_content_1, reference)
        quality_score_1 = self.calculate_overall_quality(analysis_1)

        # Display results for test 1
        self.display_results(analysis_1, quality_score_1)

        print("\n" + "=" * 80)
        print("🎯 TEST 2: PROJECT-CONTEXT GENERATION (With TaskHero AI Overview)")
        print("=" * 80)

        # Generate test task using project context only
        file_path_2, generated_content_2 = await self.generate_test_task_with_project_context()
        if not generated_content_2:
            return False

        # Analyze generated task 2
        analysis_2 = self.analyze_generated_task(generated_content_2, reference)
        quality_score_2 = self.calculate_overall_quality(analysis_2)

        # Display results for test 2
        self.display_results(analysis_2, quality_score_2)

        # Compare results
        self._compare_results(analysis_1, quality_score_1, analysis_2, quality_score_2)

        # Save comparative results
        test_results = {
            'timestamp': str(Path().cwd()),
            'test_1_context_aware': {
                'quality_score': quality_score_1,
                'analysis': analysis_1,
                'generated_file': str(file_path_1) if file_path_1 else None
            },
            'test_2_project_context': {
                'quality_score': quality_score_2,
                'analysis': analysis_2,
                'generated_file': str(file_path_2) if file_path_2 else None
            },
            'target_score': self.similarity_target,
            'best_score': max(quality_score_1, quality_score_2),
            'winner': 'Context-Aware' if quality_score_1 > quality_score_2 else 'Project-Context'
        }

        with open('kanban_test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2, default=str)

        print(f"\n💾 Test results saved to: kanban_test_results.json")

        return max(quality_score_1, quality_score_2) >= self.similarity_target

    async def generate_test_task_with_project_context(self) -> tuple:
        """Generate a kanban task using only basic inputs and TaskHero AI project context."""
        try:
            print("\n🚀 Generating Task with Project Context Only...")

            # Initialize task creator
            project_root = os.path.abspath(".")
            ai_task_creator = AITaskCreator(project_root)

            # Prepare TaskHero AI project context
            project_context = """★ TaskHero AI: Overview & User Interaction

TaskHero AI is a project management tool designed to streamline task organization, collaboration, and intelligent task generation. It's built around an AI engine that helps users manage their projects more efficiently. Here's a breakdown of its key components and how users interact with them:

★ 1. Core Functionality - The AI Engine

★ Smart Content Generation: This is the heart of TaskHero AI. The AI engine analyzes task descriptions and generates complete, well-structured task content. It leverages existing templates and, crucially, follows a strict template structure to ensure consistency. Think of it as an AI assistant that writes your tasks for you.
★ Semantic Task Search: Users can search for tasks based on their meaning rather than just keywords. The AI engine uses semantic understanding to find relevant tasks, even if the exact wording isn't present.
★ Template Intelligence: The AI engine analyzes existing tasks and suggests new task templates based on patterns. It can even generate new templates when needed, based on task descriptions.
★ Historical Learning: The system analyzes completed tasks to identify trends and best practices, continuously improving its ability to generate and suggest tasks.
★ AI Agent Optimization: The AI engine optimizes prompts for the AI coding agent, ensuring it receives the most effective input for generating code snippets.

★ 2. User Interaction Components & Features

★ Task Dashboard: A central view of all tasks, providing an overview of project status and priorities.
★ Kanban Board: A visual project management tool that allows users to drag and drop tasks across different stages (e.g., To Do, In Progress, Testing, DevDone, Done). It's an interactive tool for managing workflow.
★ Quick Create Task: A streamlined interface for quickly adding new tasks, with the AI engine assisting in generating the task content.
★ Quick View Tasks: Allows users to quickly examine the details of a selected task.
★ Search Tasks: A powerful search function that leverages the AI engine's semantic understanding to find relevant tasks.
★ Project Planner: A component that helps users plan projects by breaking them down into smaller, manageable tasks.

★ 3. How Users Interact – A Typical Workflow

1. Receive a Task Request: A user receives a general description of a task they need to complete.
2. Create Task: The user uses the "Quick Create Task" feature.
3. AI Assistance: The AI engine analyzes the task description and automatically generates a complete task, following the established template.
4. Review & Adjust: The user reviews the generated task and can make adjustments if needed.
5. Move to Kanban: The user moves the task to the appropriate stage on the Kanban board.
6. Search & Refine: If needed, the user can search for the task or refine its details."""

            # Set up basic data with project context
            ai_task_creator.creation_state['collected_data'] = {
                'title': self.test_data["title"],
                'description': self.test_data["description"],
                'task_type': self.test_data["task_type"],
                'priority': self.test_data["priority"],
                'assigned_to': self.test_data["assigned_to"],
                'tags': [tag.strip() for tag in self.test_data["tags"].split(",")]
            }

            print(f"✅ Title: {self.test_data['title']}")
            print(f"✅ Description: {self.test_data['description'][:100]}...")
            print(f"✅ Type: {self.test_data['task_type']}")
            print(f"✅ Priority: {self.test_data['priority']}")
            print(f"✅ Tags: {self.test_data['tags']}")
            print("✅ Using TaskHero AI project context instead of specific task references")

            # Create a mock context chunk with project overview
            from mods.project_management.semantic_search import ContextChunk
            project_context_chunk = ContextChunk(
                text=project_context,
                file_path="project_overview.md",
                chunk_type="documentation",
                start_line=1,
                end_line=50,
                confidence=1.0,
                relevance_score=1.0
            )

            # Set project context as selected context
            ai_task_creator.creation_state['selected_context'] = [project_context_chunk]
            print("📁 Using TaskHero AI project overview as context")

            # Run AI enhancement with project context
            from mods.project_management.ai_task_creator import AIEnhancementProgressTracker
            progress_tracker = AIEnhancementProgressTracker()

            # Initialize AI provider
            progress_tracker.start_step("🚀 Initializing AI provider...")
            ai_ready = await ai_task_creator._initialize_ai_provider()
            if not ai_ready:
                progress_tracker.fail_step("❌ AI provider initialization failed")
                return None, None
            progress_tracker.complete_step("✅ AI provider ready")

            # Prepare enhancement context
            progress_tracker.start_step("📋 Preparing enhancement context...")
            context = {
                'title': self.test_data['title'],
                'description': self.test_data['description'],
                'task_type': self.test_data['task_type'],
                'priority': self.test_data['priority'],
                'assigned_to': self.test_data['assigned_to'],
                'tags': [tag.strip() for tag in self.test_data["tags"].split(",")]
            }
            progress_tracker.complete_step("✅ Context prepared")

            # Run comprehensive AI enhancement with project context
            progress_tracker.start_step("🤖 AI is analyzing your task with project context...")
            enhanced_context = await ai_task_creator._comprehensive_ai_enhancement(
                context, self.test_data['description'], progress_tracker
            )

            if enhanced_context:
                # Calculate quality score
                progress_tracker.start_step("📊 Calculating quality metrics...")
                quality_score = ai_task_creator._calculate_enhancement_quality_score(enhanced_context)
                ai_task_creator.creation_state['quality_score'] = quality_score
                progress_tracker.complete_step("✅ Quality assessment complete")

                # Store enhancements
                ai_task_creator.creation_state['ai_enhancements'] = enhanced_context

                # Display enhancement summary
                ai_task_creator._display_enhancement_summary(enhanced_context, quality_score, progress_tracker)

                print("\n✅ AI enhancement applied successfully (auto-proceeding for test)")

                # Create the task
                success, task_id, file_path = await ai_task_creator.create_enhanced_task(
                    title=self.test_data['title'],
                    description=self.test_data['description'],
                    task_type=self.test_data['task_type'],
                    priority=self.test_data['priority'],
                    assigned_to=self.test_data['assigned_to'],
                    tags=[tag.strip() for tag in self.test_data["tags"].split(",")],
                    use_ai_enhancement=False,  # Already enhanced
                    ai_enhancements=enhanced_context
                )

                if success:
                    print(f"✅ Task {task_id} created successfully!")
                    print(f"📁 File: {file_path}")

                    # Read the generated file
                    file_path_obj = Path(file_path)
                    if file_path_obj.exists():
                        with open(file_path_obj, 'r', encoding='utf-8') as f:
                            content = f.read()
                        print(f"✅ Test task generated: {file_path}")
                        return file_path_obj, content
                    else:
                        print(f"❌ Generated file not found: {file_path}")
                        return None, None
                else:
                    print(f"❌ Task creation failed: {file_path}")
                    return None, None
            else:
                print("❌ AI enhancement failed")
                return None, None

        except Exception as e:
            print(f"❌ Project context task generation error: {e}")
            return None, None

    def _compare_results(self, analysis_1: dict, score_1: float, analysis_2: dict, score_2: float):
        """Compare results between the two test approaches."""
        print("\n" + "=" * 80)
        print("🔍 COMPARATIVE ANALYSIS")
        print("=" * 80)

        print(f"\n📊 Quality Scores:")
        print(f"   🎯 Context-Aware (TASK-003):     {score_1:.1f}%")
        print(f"   🎯 Project-Context (Overview):   {score_2:.1f}%")

        winner = "Context-Aware" if score_1 > score_2 else "Project-Context"
        diff = abs(score_1 - score_2)
        print(f"   🏆 Winner: {winner} (+{diff:.1f}%)")

        print(f"\n📋 Content Similarity:")
        print(f"   📝 Context-Aware:    {analysis_1['content_similarity']:.1f}%")
        print(f"   📝 Project-Context:  {analysis_2['content_similarity']:.1f}%")

        print(f"\n🔤 Kanban Terms Found:")
        print(f"   📊 Context-Aware:    {analysis_1['kanban_terms']} terms")
        print(f"   📊 Project-Context:  {analysis_2['kanban_terms']} terms")

        print(f"\n📋 Implementation Steps:")
        print(f"   🔧 Context-Aware:    {len(analysis_1['implementation_steps'])} steps")
        print(f"   🔧 Project-Context:  {len(analysis_2['implementation_steps'])} steps")

        # Check for contamination issues
        print(f"\n⚠️  Contamination Analysis:")

        # Check for TASK-080 references in context-aware
        context_aware_content = str(analysis_1.get('full_content', ''))
        if 'task-080' in context_aware_content.lower() or 'git integration' in context_aware_content.lower():
            print("   ❌ Context-Aware: Contains TASK-080/Git integration contamination")
        else:
            print("   ✅ Context-Aware: No contamination detected")

        # Check for project-specific contamination in project-context
        project_content = str(analysis_2.get('full_content', ''))
        if 'task-003' in project_content.lower():
            print("   ❌ Project-Context: Contains specific task references")
        else:
            print("   ✅ Project-Context: Clean project-level context")

async def main():
    """Main test function."""
    tester = KanbanTaskQualityTester()
    success = await tester.run_test()

    if success:
        print("\n🎉 Test PASSED! Task generation quality meets requirements.")
        sys.exit(0)
    else:
        print("\n💥 Test FAILED! Task generation needs improvement.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
