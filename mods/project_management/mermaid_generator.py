"""
TaskHero AI Mermaid Diagram Generator

This module generates task-specific Mermaid diagrams for enhanced visual
representation in task documentation.

Author: TaskHero AI Development Team
Created: 2025-05-25
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

logger = logging.getLogger("TaskHero.MermaidGenerator")

class DiagramType(Enum):
    """Types of Mermaid diagrams that can be generated."""
    FLOWCHART = "flowchart"
    USER_JOURNEY = "journey"
    SEQUENCE = "sequenceDiagram"
    GANTT = "gantt"
    STATE = "stateDiagram"
    CLASS = "classDiagram"
    GITGRAPH = "gitGraph"

class MermaidDiagramGenerator:
    """
    Generate task-specific Mermaid diagrams for TaskHero AI tasks.

    Creates appropriate diagrams based on task type, description, and context
    to enhance visual representation and user understanding.
    """

    def __init__(self):
        """Initialize the Mermaid diagram generator."""
        self.task_type_mappings = {
            'development': DiagramType.FLOWCHART,
            'bug fix': DiagramType.FLOWCHART,
            'test case': DiagramType.FLOWCHART,
            'documentation': DiagramType.FLOWCHART,
            'design': DiagramType.USER_JOURNEY,
            'research': DiagramType.FLOWCHART,
            'planning': DiagramType.GANTT
        }

        logger.info("MermaidDiagramGenerator initialized")

    def generate_task_diagram(self, task_type: str, title: str, description: str,
                            context: Dict[str, Any] = None) -> str:
        """
        Generate appropriate Mermaid diagram for a task.

        Args:
            task_type: Type of task (Development, Bug Fix, etc.)
            title: Task title
            description: Task description
            context: Additional context for diagram generation

        Returns:
            Mermaid diagram as string
        """
        try:
            # Determine diagram type based on task type and content
            diagram_type = self._determine_diagram_type(task_type, description)

            # Generate diagram based on type
            if diagram_type == DiagramType.FLOWCHART:
                return self._generate_flowchart(task_type, title, description, context)
            elif diagram_type == DiagramType.USER_JOURNEY:
                return self._generate_user_journey(task_type, title, description, context)
            elif diagram_type == DiagramType.SEQUENCE:
                return self._generate_sequence_diagram(task_type, title, description, context)
            elif diagram_type == DiagramType.GANTT:
                return self._generate_gantt_chart(task_type, title, description, context)
            else:
                return self._generate_flowchart(task_type, title, description, context)

        except Exception as e:
            logger.error(f"Error generating Mermaid diagram: {e}")
            return self._generate_fallback_diagram(task_type, title)

    def _determine_diagram_type(self, task_type: str, description: str) -> DiagramType:
        """Determine the most appropriate diagram type for the task."""
        task_type_lower = task_type.lower()
        description_lower = description.lower()

        # Priority keywords for specific diagram types - installation/setup should use FLOWCHART
        if any(keyword in description_lower for keyword in ['install', 'setup', 'configure', 'deploy']):
            return DiagramType.FLOWCHART
        elif any(keyword in description_lower for keyword in ['enhance', 'improve', 'modify', 'update']):
            return DiagramType.FLOWCHART
        elif any(keyword in description_lower for keyword in ['api', 'service', 'request', 'response', 'communication']):
            return DiagramType.SEQUENCE
        elif any(keyword in description_lower for keyword in ['user', 'journey', 'experience']) and not any(keyword in description_lower for keyword in ['install', 'setup', 'configure']):
            return DiagramType.USER_JOURNEY
        elif any(keyword in description_lower for keyword in ['timeline', 'schedule', 'phases', 'milestones']):
            return DiagramType.GANTT
        elif any(keyword in description_lower for keyword in ['state', 'status', 'transition', 'lifecycle']):
            return DiagramType.STATE
        else:
            # Default to flowchart for most task types
            return self.task_type_mappings.get(task_type_lower, DiagramType.FLOWCHART)

    def _generate_flowchart(self, task_type: str, title: str, description: str,
                          context: Dict[str, Any] = None) -> str:
        """Generate a flowchart diagram for the task."""
        # Extract key steps from description and context
        steps = self._extract_process_steps(description, context)

        # Generate flowchart based on task type
        if task_type.lower() == 'bug fix':
            return self._generate_bug_fix_flowchart(title, steps)
        elif task_type.lower() == 'test case':
            return self._generate_test_flowchart(title, steps)
        elif 'install' in title.lower() or 'setup' in title.lower():
            return self._generate_installation_flowchart(title, steps)
        elif 'enhance' in title.lower() or 'improve' in title.lower():
            return self._generate_enhancement_flowchart(title, steps)
        else:
            return self._generate_development_flowchart(title, steps)

    def _generate_development_flowchart(self, title: str, steps: List[str]) -> str:
        """Generate a development-focused flowchart."""
        diagram = [
            "```mermaid",
            "flowchart TD",
            "    A[Start Development] --> B[Analyze Requirements]",
            "    B --> C[Design Solution]",
            "    C --> D[Implement Core Features]",
            "    D --> E[Add Error Handling]",
            "    E --> F[Write Tests]",
            "    F --> G[Code Review]",
            "    G --> H{Tests Pass?}",
            "    H -->|Yes| I[Deploy to Staging]",
            "    H -->|No| J[Fix Issues]",
            "    J --> F",
            "    I --> K[User Acceptance Testing]",
            "    K --> L{UAT Approved?}",
            "    L -->|Yes| M[Deploy to Production]",
            "    L -->|No| N[Address Feedback]",
            "    N --> D",
            "    M --> O[Monitor & Maintain]",
            "",
            "    style A fill:#e1f5fe",
            "    style M fill:#c8e6c9",
            "    style O fill:#fff3e0",
            "```"
        ]

        return "\n".join(diagram)

    def _generate_bug_fix_flowchart(self, title: str, steps: List[str]) -> str:
        """Generate a bug fix-focused flowchart."""
        diagram = [
            "```mermaid",
            "flowchart TD",
            "    A[Bug Reported] --> B[Reproduce Issue]",
            "    B --> C{Can Reproduce?}",
            "    C -->|Yes| D[Analyze Root Cause]",
            "    C -->|No| E[Request More Info]",
            "    E --> B",
            "    D --> F[Design Fix]",
            "    F --> G[Implement Solution]",
            "    G --> H[Test Fix]",
            "    H --> I{Fix Works?}",
            "    I -->|Yes| J[Regression Testing]",
            "    I -->|No| K[Revise Approach]",
            "    K --> F",
            "    J --> L{No New Issues?}",
            "    L -->|Yes| M[Deploy Fix]",
            "    L -->|No| N[Address Regressions]",
            "    N --> G",
            "    M --> O[Verify in Production]",
            "    O --> P[Close Bug Report]",
            "",
            "    style A fill:#ffebee",
            "    style M fill:#c8e6c9",
            "    style P fill:#e8f5e8",
            "```"
        ]

        return "\n".join(diagram)

    def _generate_test_flowchart(self, title: str, steps: List[str]) -> str:
        """Generate a testing-focused flowchart."""
        diagram = [
            "```mermaid",
            "flowchart TD",
            "    A[Define Test Requirements] --> B[Design Test Cases]",
            "    B --> C[Set Up Test Environment]",
            "    C --> D[Prepare Test Data]",
            "    D --> E[Execute Tests]",
            "    E --> F{All Tests Pass?}",
            "    F -->|Yes| G[Generate Test Report]",
            "    F -->|No| H[Analyze Failures]",
            "    H --> I[Log Defects]",
            "    I --> J[Retest After Fixes]",
            "    J --> F",
            "    G --> K[Review Results]",
            "    K --> L[Update Test Suite]",
            "    L --> M[Archive Test Artifacts]",
            "",
            "    style A fill:#e3f2fd",
            "    style G fill:#c8e6c9",
            "    style M fill:#fff3e0",
            "```"
        ]

        return "\n".join(diagram)

    def _generate_installation_flowchart(self, title: str, steps: List[str]) -> str:
        """Generate an installation/setup-focused flowchart."""
        diagram = [
            "```mermaid",
            "flowchart TD",
            "    A[User Runs Setup Script] --> B[Check System Requirements]",
            "    B --> C{Requirements Met?}",
            "    C -->|No| D[Display Error Message]",
            "    C -->|Yes| E[Install Dependencies]",
            "    E --> F[Configure Environment]",
            "    F --> G[Collect User Preferences]",
            "    G --> H[Generate Configuration Files]",
            "    H --> I[Initialize Application]",
            "    I --> J{Setup Successful?}",
            "    J -->|Yes| K[Launch Application]",
            "    J -->|No| L[Show Error & Cleanup]",
            "    K --> M[Display Success Message]",
            "    L --> N[Provide Support Info]",
            "",
            "    style A fill:#e1f5fe",
            "    style K fill:#c8e6c9",
            "    style M fill:#e8f5e8",
            "    style D fill:#ffebee",
            "    style L fill:#ffebee",
            "```"
        ]

        return "\n".join(diagram)

    def _generate_enhancement_flowchart(self, title: str, steps: List[str]) -> str:
        """Generate an enhancement/improvement-focused flowchart."""
        diagram = [
            "```mermaid",
            "flowchart TD",
            "    A[Identify Enhancement Need] --> B[Analyze Current System]",
            "    B --> C[Define Improvement Goals]",
            "    C --> D[Research Solutions]",
            "    D --> E[Design Enhancement]",
            "    E --> F[Plan Implementation]",
            "    F --> G[Implement Changes]",
            "    G --> H[Test Improvements]",
            "    H --> I{Quality Meets Goals?}",
            "    I -->|No| J[Refine Implementation]",
            "    J --> G",
            "    I -->|Yes| K[Performance Testing]",
            "    K --> L[User Feedback Collection]",
            "    L --> M{Feedback Positive?}",
            "    M -->|Yes| N[Deploy Enhancement]",
            "    M -->|No| O[Address Concerns]",
            "    O --> G",
            "    N --> P[Monitor Impact]",
            "",
            "    style A fill:#fff3e0",
            "    style N fill:#c8e6c9",
            "    style P fill:#e8f5e8",
            "```"
        ]

        return "\n".join(diagram)

    def _generate_user_journey(self, task_type: str, title: str, description: str,
                             context: Dict[str, Any] = None) -> str:
        """Generate a user journey diagram."""
        # Extract user actions from description
        user_actions = self._extract_user_actions(description)

        diagram = [
            "```mermaid",
            "journey",
            f"    title {title} - User Journey",
            "    section User Interaction",
        ]

        # Add user actions to journey
        for i, action in enumerate(user_actions[:6], 1):  # Limit to 6 actions
            satisfaction = 5 if i <= 3 else 4  # Higher satisfaction for early steps
            diagram.append(f"      {action}: {satisfaction}: User")

        # Add default actions if none extracted
        if not user_actions:
            diagram.extend([
                "      Access System: 5: User",
                "      Navigate to Feature: 4: User",
                "      Perform Action: 5: User",
                "      Review Results: 4: User",
                "      Complete Task: 5: User"
            ])

        diagram.append("```")
        return "\n".join(diagram)

    def _generate_sequence_diagram(self, task_type: str, title: str, description: str,
                                 context: Dict[str, Any] = None) -> str:
        """Generate a sequence diagram for API/service interactions."""
        diagram = [
            "```mermaid",
            "sequenceDiagram",
            "    participant U as User",
            "    participant F as Frontend",
            "    participant A as API",
            "    participant D as Database",
            "",
            "    U->>F: Initiate Action",
            "    F->>A: Send Request",
            "    A->>A: Validate Input",
            "    A->>D: Query/Update Data",
            "    D-->>A: Return Results",
            "    A->>A: Process Response",
            "    A-->>F: Send Response",
            "    F-->>U: Display Results",
            "",
            "    Note over U,D: " + title[:40] + ("..." if len(title) > 40 else ""),
            "```"
        ]

        return "\n".join(diagram)

    def _generate_gantt_chart(self, task_type: str, title: str, description: str,
                            context: Dict[str, Any] = None) -> str:
        """Generate a Gantt chart for project timeline."""
        diagram = [
            "```mermaid",
            "gantt",
            f"    title {title} Timeline",
            "    dateFormat  YYYY-MM-DD",
            "    section Planning",
            "    Requirements Analysis    :req, 2025-05-25, 2d",
            "    Design Phase            :design, after req, 3d",
            "    section Implementation",
            "    Core Development        :dev, after design, 5d",
            "    Testing                 :test, after dev, 3d",
            "    section Deployment",
            "    Staging Deployment      :staging, after test, 1d",
            "    Production Deployment   :prod, after staging, 1d",
            "```"
        ]

        return "\n".join(diagram)

    def _extract_process_steps(self, description: str, context: Dict[str, Any] = None) -> List[str]:
        """Extract process steps from description and context."""
        steps = []

        # Look for numbered steps or bullet points
        step_patterns = [
            r'\d+\.\s+([^.]+)',  # Numbered steps
            r'[-*]\s+([^.]+)',   # Bullet points
            r'Step \d+:\s*([^.]+)',  # Step format
        ]

        for pattern in step_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            steps.extend([match.strip() for match in matches])

        # If no steps found, extract from implementation steps in context
        if not steps and context and 'implementation_steps' in context:
            impl_steps = context['implementation_steps']
            if isinstance(impl_steps, list):
                for step in impl_steps:
                    if isinstance(step, dict) and 'title' in step:
                        steps.append(step['title'])
                    elif isinstance(step, str):
                        steps.append(step)

        return steps[:8]  # Limit to 8 steps for diagram clarity

    def _extract_user_actions(self, description: str) -> List[str]:
        """Extract user actions from description for user journey."""
        actions = []
        sentences = description.split('.')

        # Better parsing logic for meaningful user actions
        for sentence in sentences:
            sentence = sentence.strip()
            if any(verb in sentence.lower() for verb in ['run', 'execute', 'configure', 'install', 'setup', 'create', 'modify', 'update', 'test', 'deploy']):
                # Extract meaningful action from sentence
                action = self._clean_action_text(sentence.strip())
                if action and len(action) > 5:
                    actions.append(action)

        # Fallback to generic actions if none found
        if not actions:
            actions = ["Start Process", "Configure Settings", "Complete Setup", "Verify Results"]

        return actions[:6]  # Limit to 6 actions

    def _clean_action_text(self, text: str) -> str:
        """Clean and format action text for user journey."""
        # Remove common prefixes and clean up text
        text = re.sub(r'^(the\s+|a\s+|an\s+)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace

        # Capitalize first letter and ensure reasonable length
        if len(text) > 50:
            text = text[:47] + "..."

        return text.strip().capitalize() if text.strip() else ""

    def _generate_fallback_diagram(self, task_type: str, title: str) -> str:
        """Generate a simple fallback diagram when generation fails."""
        diagram = [
            "```mermaid",
            "flowchart TD",
            "    A[Start Task] --> B[Analyze Requirements]",
            "    B --> C[Plan Implementation]",
            "    C --> D[Execute Work]",
            "    D --> E[Test & Validate]",
            "    E --> F[Complete Task]",
            "",
            "    style A fill:#e1f5fe",
            "    style F fill:#c8e6c9",
            "```"
        ]

        return "\n".join(diagram)

    def generate_ascii_layout(self, task_type: str, description: str) -> str:
        """Generate ASCII art layout for UI-related tasks."""
        if 'ui' in description.lower() or 'interface' in description.lower() or 'layout' in description.lower():
            return self._generate_ui_layout()
        elif 'dashboard' in description.lower():
            return self._generate_dashboard_layout()
        elif 'form' in description.lower():
            return self._generate_form_layout()
        else:
            return self._generate_generic_layout()

    def _generate_ui_layout(self) -> str:
        """Generate ASCII art for UI layout."""
        layout = [
            "```",
            "┌─────────────────────────────────────────────────────────────┐",
            "│ Header Navigation                                           │",
            "├─────────────────────────────────────────────────────────────┤",
            "│ ┌─────────────┐ ┌─────────────────────────────────────────┐ │",
            "│ │ Sidebar     │ │ Main Content Area                       │ │",
            "│ │ - Menu 1    │ │ ┌─────────────────────────────────────┐ │ │",
            "│ │ - Menu 2    │ │ │ Content Block 1                     │ │ │",
            "│ │ - Menu 3    │ │ ├─────────────────────────────────────┤ │ │",
            "│ │             │ │ │ Content Block 2                     │ │ │",
            "│ │             │ │ └─────────────────────────────────────┘ │ │",
            "│ └─────────────┘ └─────────────────────────────────────────┘ │",
            "├─────────────────────────────────────────────────────────────┤",
            "│ Footer Information                                          │",
            "└─────────────────────────────────────────────────────────────┘",
            "```"
        ]

        return "\n".join(layout)

    def _generate_dashboard_layout(self) -> str:
        """Generate ASCII art for dashboard layout."""
        layout = [
            "```",
            "┌─────────────────────────────────────────────────────────────┐",
            "│ Dashboard Title                                    [⚙️ Settings] │",
            "├─────────────────────────────────────────────────────────────┤",
            "│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │",
            "│ │ Metric 1    │ │ Metric 2    │ │ Metric 3    │ │ Status  │ │",
            "│ │ 📊 1,234    │ │ 📈 +15%     │ │ ⏱️ 2.3s     │ │ 🟢 Good │ │",
            "│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │",
            "├─────────────────────────────────────────────────────────────┤",
            "│ ┌─────────────────────────────┐ ┌─────────────────────────┐ │",
            "│ │ Chart Area                  │ │ Recent Activity         │ │",
            "│ │ ▁▂▃▅▆▇█▇▆▅▃▂▁              │ │ • Task completed        │ │",
            "│ │                             │ │ • User logged in        │ │",
            "│ │                             │ │ • Data updated          │ │",
            "│ └─────────────────────────────┘ └─────────────────────────┘ │",
            "└─────────────────────────────────────────────────────────────┘",
            "```"
        ]

        return "\n".join(layout)

    def _generate_form_layout(self) -> str:
        """Generate ASCII art for form layout."""
        layout = [
            "```",
            "┌─────────────────────────────────────────────────────────────┐",
            "│ Form Title                                                  │",
            "├─────────────────────────────────────────────────────────────┤",
            "│ Field Label 1:                                              │",
            "│ ┌─────────────────────────────────────────────────────────┐ │",
            "│ │ Input field                                             │ │",
            "│ └─────────────────────────────────────────────────────────┘ │",
            "│                                                             │",
            "│ Field Label 2:                                              │",
            "│ ┌─────────────────────────────────────────────────────────┐ │",
            "│ │ Another input field                                     │ │",
            "│ └─────────────────────────────────────────────────────────┘ │",
            "│                                                             │",
            "│ ┌─────────────┐ ┌─────────────┐                           │",
            "│ │ [Cancel]    │ │ [Submit]    │                           │",
            "│ └─────────────┘ └─────────────┘                           │",
            "└─────────────────────────────────────────────────────────────┘",
            "```"
        ]

        return "\n".join(layout)

    def _generate_generic_layout(self) -> str:
        """Generate generic ASCII art layout."""
        layout = [
            "```",
            "┌─────────────────────────────────────────────────────────────┐",
            "│ Component Layout                                            │",
            "├─────────────────────────────────────────────────────────────┤",
            "│ ┌─────────────────────────────────────────────────────────┐ │",
            "│ │ Main Component Area                                     │ │",
            "│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │ │",
            "│ │ │ Element 1   │ │ Element 2   │ │ Element 3   │       │ │",
            "│ │ └─────────────┘ └─────────────┘ └─────────────┘       │ │",
            "│ └─────────────────────────────────────────────────────────┘ │",
            "└─────────────────────────────────────────────────────────────┘",
            "```"
        ]

        return "\n".join(layout)