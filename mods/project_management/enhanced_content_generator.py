"""
TaskHero AI Enhanced Content Generator

This module provides enhanced content generation capabilities that address
the quality gaps identified in TASK-057 vs TASK-008 analysis, focusing on
specificity, testability, and technical depth.

Key Features:
- Context-aware functional requirements generation
- Detailed implementation step generation with sub-tasks
- Technical depth enhancement for architecture considerations
- Specific, testable content instead of generic templates

Author: TaskHero AI Development Team
Created: 2025-05-25 (TASK-058 Step 3)
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

# Import existing LLM infrastructure
try:
    from mods.llms import generate_response, generate_description
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger("TaskHero.EnhancedContentGenerator")

@dataclass
class ContentGenerationContext:
    """Context for enhanced content generation."""
    task_type: str
    title: str
    description: str
    domain: str  # e.g., 'web-development', 'data-processing', 'ui-design'
    complexity: str  # 'simple', 'medium', 'complex'
    technology_stack: List[str]
    user_personas: List[str]
    business_context: str
    existing_systems: List[str]

class EnhancedContentGenerator:
    """
    Enhanced content generator that produces specific, testable, and
    technically detailed content for TaskHero AI tasks.
    
    Addresses quality gaps by:
    - Generating specific, testable functional requirements
    - Creating detailed implementation steps with clear sub-tasks
    - Providing context-aware content based on task domain
    - Including comprehensive technical depth and architecture considerations
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize the enhanced content generator.
        
        Args:
            project_path: Path to the project root
        """
        self.project_path = project_path or "."
        
        # Content generation templates and patterns
        self.requirement_patterns = self._initialize_requirement_patterns()
        self.implementation_patterns = self._initialize_implementation_patterns()
        self.technical_patterns = self._initialize_technical_patterns()
        
        logger.info("Enhanced Content Generator initialized successfully")
    
    def _initialize_requirement_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for generating specific functional requirements."""
        return {
            "authentication": [
                "The system must validate user credentials against {auth_provider} with {security_level} security",
                "The system must implement {mfa_type} multi-factor authentication for {user_roles}",
                "The system must enforce password policies with minimum {min_length} characters and {complexity_rules}",
                "The system must provide secure password reset functionality via {reset_method}",
                "The system must maintain user session security with {session_timeout} timeout"
            ],
            "data_processing": [
                "The system must process {data_volume} records per {time_unit} with {accuracy_level} accuracy",
                "The system must validate input data against {validation_schema} before processing",
                "The system must handle {error_scenarios} gracefully with appropriate error messages",
                "The system must provide data transformation from {source_format} to {target_format}",
                "The system must ensure data integrity through {integrity_mechanisms}"
            ],
            "ui_interface": [
                "The interface must be responsive across {device_types} with {breakpoint_specifications}",
                "The interface must meet {accessibility_standards} accessibility requirements",
                "The interface must provide {interaction_patterns} for {user_actions}",
                "The interface must display {data_elements} with {performance_requirements}",
                "The interface must support {localization_requirements} for {target_markets}"
            ],
            "api_integration": [
                "The API must handle {request_volume} requests per second with {response_time} response time",
                "The API must implement {authentication_method} authentication and {authorization_model}",
                "The API must provide {data_formats} data exchange with {validation_rules}",
                "The API must include comprehensive error handling for {error_scenarios}",
                "The API must maintain {uptime_requirement} uptime with {monitoring_capabilities}"
            ],
            "testing": [
                "The test suite must achieve {coverage_percentage} code coverage across {test_types}",
                "The tests must validate {functional_scenarios} with {assertion_criteria}",
                "The tests must include {performance_benchmarks} performance validation",
                "The tests must cover {edge_cases} and {error_conditions}",
                "The tests must provide {reporting_format} test reports with {metrics}"
            ]
        }
    
    def _initialize_implementation_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize patterns for generating detailed implementation steps."""
        return {
            "development": [
                {
                    "phase": "Analysis and Design",
                    "steps": [
                        "Analyze existing {system_components} and identify integration points",
                        "Design {architecture_pattern} architecture with {scalability_considerations}",
                        "Create detailed technical specifications for {feature_components}",
                        "Define data models and database schema for {data_entities}",
                        "Establish coding standards and development guidelines"
                    ]
                },
                {
                    "phase": "Core Implementation",
                    "steps": [
                        "Implement {core_functionality} with {technology_stack}",
                        "Develop {data_layer} with {database_technology} integration",
                        "Create {business_logic} layer with {design_patterns}",
                        "Implement {api_endpoints} with {security_measures}",
                        "Add comprehensive error handling and logging"
                    ]
                },
                {
                    "phase": "Testing and Validation",
                    "steps": [
                        "Write unit tests for {component_types} with {testing_framework}",
                        "Implement integration tests for {integration_points}",
                        "Perform {performance_testing} with {load_scenarios}",
                        "Conduct security testing for {security_aspects}",
                        "Execute user acceptance testing with {user_scenarios}"
                    ]
                },
                {
                    "phase": "Deployment and Monitoring",
                    "steps": [
                        "Set up {deployment_environment} with {infrastructure_requirements}",
                        "Configure {monitoring_tools} for {monitoring_metrics}",
                        "Implement {backup_strategy} and disaster recovery procedures",
                        "Deploy to {staging_environment} for final validation",
                        "Execute production deployment with {rollback_strategy}"
                    ]
                }
            ],
            "bug_fix": [
                {
                    "phase": "Investigation and Analysis",
                    "steps": [
                        "Reproduce the issue in {test_environment} with {reproduction_steps}",
                        "Analyze {log_files} and {error_traces} for root cause identification",
                        "Review {code_sections} related to {affected_functionality}",
                        "Identify {contributing_factors} and {system_dependencies}",
                        "Document findings and proposed solution approach"
                    ]
                },
                {
                    "phase": "Solution Development",
                    "steps": [
                        "Implement fix for {root_cause} in {affected_components}",
                        "Add {validation_logic} to prevent similar issues",
                        "Update {error_handling} for better user experience",
                        "Modify {test_cases} to cover the fixed scenario",
                        "Review code changes with {review_criteria}"
                    ]
                },
                {
                    "phase": "Testing and Verification",
                    "steps": [
                        "Test fix with {original_reproduction_steps}",
                        "Perform regression testing on {related_functionality}",
                        "Validate fix in {multiple_environments}",
                        "Confirm {performance_impact} is within acceptable limits",
                        "Obtain approval from {stakeholders} before deployment"
                    ]
                }
            ]
        }
    
    def _initialize_technical_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize patterns for technical depth enhancement."""
        return {
            "architecture": {
                "patterns": [
                    "Implement {architectural_pattern} pattern for {scalability_benefits}",
                    "Use {design_pattern} for {component_interaction} management",
                    "Apply {data_pattern} for efficient {data_operations}",
                    "Utilize {integration_pattern} for {external_system} integration"
                ],
                "considerations": [
                    "Ensure {performance_metrics} meet {business_requirements}",
                    "Design for {scalability_targets} with {growth_projections}",
                    "Implement {security_measures} for {threat_scenarios}",
                    "Plan for {maintenance_requirements} and {upgrade_paths}"
                ]
            },
            "performance": {
                "optimization": [
                    "Implement {caching_strategy} for {data_access_patterns}",
                    "Optimize {database_queries} with {indexing_strategy}",
                    "Use {async_processing} for {long_running_operations}",
                    "Apply {load_balancing} for {traffic_distribution}"
                ],
                "monitoring": [
                    "Monitor {performance_metrics} with {monitoring_tools}",
                    "Set up alerts for {threshold_violations}",
                    "Track {user_experience_metrics} across {user_journeys}",
                    "Implement {performance_profiling} for {optimization_opportunities}"
                ]
            },
            "security": {
                "measures": [
                    "Implement {authentication_mechanism} with {security_standards}",
                    "Apply {authorization_model} for {resource_access}",
                    "Use {encryption_methods} for {data_protection}",
                    "Implement {input_validation} against {security_threats}"
                ],
                "compliance": [
                    "Ensure compliance with {regulatory_requirements}",
                    "Implement {audit_logging} for {compliance_tracking}",
                    "Apply {data_privacy} measures for {sensitive_data}",
                    "Conduct {security_assessments} with {assessment_criteria}"
                ]
            }
        }
    
    def generate_enhanced_functional_requirements(self, context: ContentGenerationContext) -> List[str]:
        """
        Generate specific, testable functional requirements based on context.
        
        Args:
            context: Content generation context
            
        Returns:
            List of specific functional requirements
        """
        try:
            # Determine domain-specific patterns
            domain_patterns = self._get_domain_patterns(context.domain)
            
            # Generate context-aware requirements
            requirements = []
            
            # Use AI to generate specific requirements if available
            if LLM_AVAILABLE:
                requirements.extend(self._generate_ai_requirements(context))
            
            # Add pattern-based requirements
            requirements.extend(self._generate_pattern_requirements(context, domain_patterns))
            
            # Ensure requirements are specific and testable
            requirements = self._enhance_requirement_specificity(requirements, context)
            
            logger.info(f"Generated {len(requirements)} enhanced functional requirements")
            return requirements
            
        except Exception as e:
            logger.error(f"Error generating enhanced functional requirements: {e}")
            return self._generate_fallback_requirements(context)
    
    def generate_enhanced_implementation_steps(self, context: ContentGenerationContext) -> List[Dict[str, Any]]:
        """
        Generate detailed implementation steps with sub-tasks and timelines.
        
        Args:
            context: Content generation context
            
        Returns:
            List of implementation phases with detailed steps
        """
        try:
            # Get base implementation pattern
            base_pattern = self.implementation_patterns.get(
                self._map_task_type_to_pattern(context.task_type), 
                self.implementation_patterns["development"]
            )
            
            # Enhance with context-specific details
            enhanced_steps = []
            
            for phase in base_pattern:
                enhanced_phase = {
                    "phase": phase["phase"],
                    "steps": [],
                    "estimated_duration": self._estimate_phase_duration(phase, context),
                    "dependencies": self._identify_phase_dependencies(phase, context),
                    "deliverables": self._identify_phase_deliverables(phase, context)
                }
                
                # Enhance each step with context
                for step_template in phase["steps"]:
                    enhanced_step = self._contextualize_step(step_template, context)
                    enhanced_phase["steps"].append(enhanced_step)
                
                enhanced_steps.append(enhanced_phase)
            
            logger.info(f"Generated {len(enhanced_steps)} implementation phases")
            return enhanced_steps
            
        except Exception as e:
            logger.error(f"Error generating enhanced implementation steps: {e}")
            return self._generate_fallback_implementation_steps(context)
    
    def generate_enhanced_technical_considerations(self, context: ContentGenerationContext) -> Dict[str, Any]:
        """
        Generate comprehensive technical considerations with architecture details.
        
        Args:
            context: Content generation context
            
        Returns:
            Dict containing technical considerations by category
        """
        try:
            considerations = {
                "architecture": self._generate_architecture_considerations(context),
                "performance": self._generate_performance_considerations(context),
                "security": self._generate_security_considerations(context),
                "scalability": self._generate_scalability_considerations(context),
                "maintainability": self._generate_maintainability_considerations(context),
                "integration": self._generate_integration_considerations(context)
            }
            
            logger.info("Generated comprehensive technical considerations")
            return considerations
            
        except Exception as e:
            logger.error(f"Error generating technical considerations: {e}")
            return self._generate_fallback_technical_considerations(context)
    
    def _get_domain_patterns(self, domain: str) -> List[str]:
        """Get domain-specific requirement patterns."""
        domain_mapping = {
            "authentication": "authentication",
            "data": "data_processing",
            "ui": "ui_interface",
            "api": "api_integration",
            "test": "testing"
        }
        
        for key, pattern_key in domain_mapping.items():
            if key in domain.lower():
                return self.requirement_patterns.get(pattern_key, [])
        
        return self.requirement_patterns.get("data_processing", [])
    
    def _generate_ai_requirements(self, context: ContentGenerationContext) -> List[str]:
        """Generate requirements using AI if available."""
        if not LLM_AVAILABLE:
            return []
        
        try:
            prompt = f"""
Generate 5 specific, testable functional requirements for a {context.task_type} task:

Title: {context.title}
Description: {context.description}
Domain: {context.domain}
Technology Stack: {', '.join(context.technology_stack)}

Requirements should be:
- Specific and measurable
- Testable with clear acceptance criteria
- Technically detailed
- Context-appropriate for the domain

Format each requirement as a bullet point starting with "The system must..."
"""
            
            response = generate_response(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a technical requirements analyst creating specific, testable requirements.",
                temperature=0.3,
                max_tokens=1000
            )
            
            # Extract requirements from response
            requirements = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    requirements.append(line[2:].strip())
                elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    requirements.append(line[3:].strip())
            
            return requirements[:5]  # Limit to 5 requirements
            
        except Exception as e:
            logger.warning(f"AI requirement generation failed: {e}")
            return []
    
    def _generate_pattern_requirements(self, context: ContentGenerationContext, patterns: List[str]) -> List[str]:
        """Generate requirements using patterns."""
        requirements = []
        
        # Context variables for pattern substitution
        variables = {
            "auth_provider": "OAuth 2.0",
            "security_level": "enterprise-grade",
            "mfa_type": "TOTP-based",
            "user_roles": "administrative users",
            "min_length": "12",
            "complexity_rules": "uppercase, lowercase, numbers, and special characters",
            "reset_method": "email verification",
            "session_timeout": "30-minute",
            "data_volume": "10,000",
            "time_unit": "minute",
            "accuracy_level": "99.9%",
            "validation_schema": "JSON Schema v7",
            "error_scenarios": "invalid input, network failures, and timeout conditions",
            "source_format": "CSV",
            "target_format": "JSON",
            "integrity_mechanisms": "checksums and transaction logging"
        }
        
        # Apply context-specific variables
        if context.technology_stack:
            variables.update({
                "technology_stack": ", ".join(context.technology_stack),
                "database_technology": context.technology_stack[0] if context.technology_stack else "PostgreSQL"
            })
        
        # Generate requirements from patterns
        for pattern in patterns[:3]:  # Limit to 3 pattern-based requirements
            try:
                requirement = pattern.format(**variables)
                requirements.append(requirement)
            except KeyError as e:
                # Handle missing variables gracefully
                requirement = pattern.replace(f"{{{e.args[0]}}}", "[to be specified]")
                requirements.append(requirement)
        
        return requirements
    
    def _enhance_requirement_specificity(self, requirements: List[str], context: ContentGenerationContext) -> List[str]:
        """Enhance requirements to be more specific and testable."""
        enhanced = []
        
        for req in requirements:
            # Add specific metrics and criteria
            if "must" in req and not any(metric in req.lower() for metric in ["seconds", "minutes", "hours", "%", "mb", "gb"]):
                # Add performance criteria if missing
                if "performance" in req.lower() or "speed" in req.lower():
                    req += " within 2 seconds under normal load conditions"
                elif "accuracy" in req.lower():
                    req += " with 99.5% accuracy"
                elif "availability" in req.lower():
                    req += " with 99.9% uptime"
            
            # Ensure testability
            if not any(test_word in req.lower() for test_word in ["validate", "verify", "test", "measure", "check"]):
                req += " (verifiable through automated testing)"
            
            enhanced.append(req)
        
        return enhanced
    
    def _map_task_type_to_pattern(self, task_type: str) -> str:
        """Map task type to implementation pattern."""
        if "bug" in task_type.lower() or "fix" in task_type.lower():
            return "bug_fix"
        else:
            return "development"
    
    def _estimate_phase_duration(self, phase: Dict[str, Any], context: ContentGenerationContext) -> str:
        """Estimate duration for implementation phase."""
        complexity_multipliers = {
            "simple": 1.0,
            "medium": 1.5,
            "complex": 2.5
        }
        
        base_durations = {
            "Analysis and Design": 3,
            "Core Implementation": 7,
            "Testing and Validation": 4,
            "Deployment and Monitoring": 2,
            "Investigation and Analysis": 2,
            "Solution Development": 3,
            "Testing and Verification": 2
        }
        
        base_days = base_durations.get(phase["phase"], 3)
        multiplier = complexity_multipliers.get(context.complexity, 1.5)
        estimated_days = int(base_days * multiplier)
        
        return f"{estimated_days} days"
    
    def _identify_phase_dependencies(self, phase: Dict[str, Any], context: ContentGenerationContext) -> List[str]:
        """Identify dependencies for implementation phase."""
        dependencies = {
            "Analysis and Design": ["Requirements approval", "Technical architecture review"],
            "Core Implementation": ["Design completion", "Development environment setup"],
            "Testing and Validation": ["Core implementation completion", "Test environment setup"],
            "Deployment and Monitoring": ["Testing completion", "Production environment preparation"]
        }
        
        return dependencies.get(phase["phase"], [])
    
    def _identify_phase_deliverables(self, phase: Dict[str, Any], context: ContentGenerationContext) -> List[str]:
        """Identify deliverables for implementation phase."""
        deliverables = {
            "Analysis and Design": ["Technical specification", "Architecture diagrams", "Database schema"],
            "Core Implementation": ["Working software", "Unit tests", "Code documentation"],
            "Testing and Validation": ["Test reports", "Performance benchmarks", "Bug fixes"],
            "Deployment and Monitoring": ["Production deployment", "Monitoring setup", "Documentation"]
        }
        
        return deliverables.get(phase["phase"], [])
    
    def _contextualize_step(self, step_template: str, context: ContentGenerationContext) -> str:
        """Contextualize implementation step with specific details."""
        # Context variables for step substitution
        variables = {
            "system_components": "authentication module, data processing engine, and user interface",
            "architecture_pattern": "microservices",
            "scalability_considerations": "horizontal scaling and load distribution",
            "feature_components": "user management, data validation, and reporting",
            "data_entities": "users, transactions, and audit logs",
            "core_functionality": "business logic and data processing",
            "technology_stack": ", ".join(context.technology_stack) if context.technology_stack else "modern web technologies",
            "data_layer": "repository pattern implementation",
            "database_technology": context.technology_stack[0] if context.technology_stack else "PostgreSQL",
            "business_logic": "service layer",
            "design_patterns": "dependency injection and factory patterns",
            "api_endpoints": "RESTful API endpoints",
            "security_measures": "authentication, authorization, and input validation",
            "component_types": "controllers, services, and repositories",
            "testing_framework": "Jest and Supertest",
            "integration_points": "external APIs and database connections",
            "performance_testing": "load testing",
            "load_scenarios": "peak usage conditions",
            "security_aspects": "authentication, authorization, and data protection",
            "user_scenarios": "typical user workflows",
            "deployment_environment": "containerized production environment",
            "infrastructure_requirements": "Docker containers and Kubernetes orchestration",
            "monitoring_tools": "application performance monitoring and logging",
            "monitoring_metrics": "response times, error rates, and resource utilization",
            "backup_strategy": "automated daily backups",
            "staging_environment": "pre-production staging",
            "rollback_strategy": "blue-green deployment"
        }
        
        try:
            return step_template.format(**variables)
        except KeyError as e:
            # Handle missing variables gracefully
            return step_template.replace(f"{{{e.args[0]}}}", "[to be specified]")
    
    def _generate_architecture_considerations(self, context: ContentGenerationContext) -> List[str]:
        """Generate architecture-specific considerations."""
        return [
            f"Implement microservices architecture for {context.domain} functionality",
            f"Design API-first approach for {', '.join(context.technology_stack)} integration",
            "Apply domain-driven design principles for business logic organization",
            "Implement event-driven architecture for asynchronous processing",
            "Use containerization for deployment consistency and scalability"
        ]
    
    def _generate_performance_considerations(self, context: ContentGenerationContext) -> List[str]:
        """Generate performance-specific considerations."""
        return [
            "Implement caching strategy for frequently accessed data",
            "Optimize database queries with proper indexing and query optimization",
            "Use connection pooling for database and external service connections",
            "Implement lazy loading for large datasets and complex objects",
            "Monitor and optimize memory usage and garbage collection"
        ]
    
    def _generate_security_considerations(self, context: ContentGenerationContext) -> List[str]:
        """Generate security-specific considerations."""
        return [
            "Implement OAuth 2.0 with PKCE for secure authentication",
            "Apply principle of least privilege for user authorization",
            "Use HTTPS/TLS for all data transmission",
            "Implement input validation and sanitization against injection attacks",
            "Apply security headers and CORS policies for web applications"
        ]
    
    def _generate_scalability_considerations(self, context: ContentGenerationContext) -> List[str]:
        """Generate scalability-specific considerations."""
        return [
            "Design for horizontal scaling with stateless application architecture",
            "Implement load balancing for traffic distribution",
            "Use database sharding or read replicas for data scaling",
            "Apply caching layers for performance optimization",
            "Design for auto-scaling based on demand metrics"
        ]
    
    def _generate_maintainability_considerations(self, context: ContentGenerationContext) -> List[str]:
        """Generate maintainability-specific considerations."""
        return [
            "Follow SOLID principles for clean, maintainable code",
            "Implement comprehensive logging and monitoring",
            "Use dependency injection for loose coupling",
            "Apply consistent coding standards and documentation",
            "Implement automated testing for regression prevention"
        ]
    
    def _generate_integration_considerations(self, context: ContentGenerationContext) -> List[str]:
        """Generate integration-specific considerations."""
        return [
            "Design robust API contracts with versioning strategy",
            "Implement circuit breaker pattern for external service calls",
            "Use message queues for asynchronous integration",
            "Apply retry mechanisms with exponential backoff",
            "Implement comprehensive error handling and logging for integrations"
        ]
    
    def _generate_fallback_requirements(self, context: ContentGenerationContext) -> List[str]:
        """Generate fallback requirements when AI is not available."""
        return [
            f"The system must implement {context.title} functionality according to specifications",
            "The system must provide comprehensive error handling and validation",
            "The system must maintain backward compatibility with existing systems",
            "The system must include appropriate logging and monitoring capabilities",
            "The system must follow established coding standards and best practices"
        ]
    
    def _generate_fallback_implementation_steps(self, context: ContentGenerationContext) -> List[Dict[str, Any]]:
        """Generate fallback implementation steps when enhancement fails."""
        return [
            {
                "phase": "Analysis and Planning",
                "steps": [
                    "Analyze current system and requirements",
                    "Design solution architecture and approach",
                    "Create detailed implementation plan",
                    "Set up development environment and tools"
                ],
                "estimated_duration": "3 days",
                "dependencies": ["Requirements approval"],
                "deliverables": ["Technical specification"]
            },
            {
                "phase": "Implementation",
                "steps": [
                    "Implement core functionality and features",
                    "Add comprehensive error handling",
                    "Implement logging and monitoring",
                    "Add configuration and customization options"
                ],
                "estimated_duration": "7 days",
                "dependencies": ["Design completion"],
                "deliverables": ["Working software"]
            }
        ]
    
    def _generate_fallback_technical_considerations(self, context: ContentGenerationContext) -> Dict[str, Any]:
        """Generate fallback technical considerations when enhancement fails."""
        return {
            "architecture": ["Component design and interaction patterns"],
            "performance": ["Response time and throughput optimization"],
            "security": ["Authentication and authorization implementation"],
            "scalability": ["Horizontal scaling capabilities"],
            "maintainability": ["Code organization and documentation"],
            "integration": ["External system integration patterns"]
        } 