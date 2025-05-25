"""
Template Validator Module

Provides comprehensive validation for templates including JSON Schema validation,
required field checking, dependency validation, and template syntax verification.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from jsonschema import validate, ValidationError, Draft7Validator
import re

logger = logging.getLogger("TaskHeroAI.ProjectManagement.TemplateValidator")


@dataclass
class ValidationResult:
    """Template validation result structure."""
    template_name: str
    valid: bool
    errors: List[str]
    warnings: List[str]
    metadata_valid: bool
    syntax_valid: bool
    dependencies_valid: bool
    variables: List[str]
    missing_variables: List[str]
    unused_variables: List[str]


class TemplateValidator:
    """Comprehensive template validation system."""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the Template Validator.
        
        Args:
            project_root: Root directory for project management
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.schemas_dir = self.project_root / "mods" / "project_management" / "schemas"
        self.templates_dir = self.project_root / "mods" / "project_management" / "templates"
        
        # Create schemas directory if it doesn't exist
        self.schemas_dir.mkdir(parents=True, exist_ok=True)
        
        # Load validation schemas
        self.schemas = self._load_schemas()
        
        # Validation rules
        self.validation_rules = self._setup_validation_rules()
    
    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load JSON schemas for template validation."""
        schemas = {}
        
        # Default schemas if files don't exist
        default_schemas = {
            'task_template': {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "pattern": "^TASK-\\d{3}$"},
                    "title": {"type": "string", "minLength": 5, "maxLength": 100},
                    "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                    "status": {"type": "string", "enum": ["Todo", "In Progress", "Testing", "Done"]},
                    "due_date": {"type": "string", "format": "date"},
                    "assignee": {"type": "string"},
                    "description": {"type": "string", "minLength": 10},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "dependencies": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["task_id", "title", "priority", "status", "description"],
                "additionalProperties": True
            },
            'project_template': {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "minLength": 3, "maxLength": 50},
                    "description": {"type": "string", "minLength": 20},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                    "team_members": {"type": "array", "items": {"type": "string"}},
                    "technologies": {"type": "array", "items": {"type": "string"}},
                    "budget": {"type": "number", "minimum": 0}
                },
                "required": ["project_name", "description", "start_date"],
                "additionalProperties": True
            },
            'report_template': {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "minLength": 5, "maxLength": 100},
                    "author": {"type": "string", "minLength": 2},
                    "date": {"type": "string", "format": "date"},
                    "summary": {"type": "string", "minLength": 50},
                    "sections": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "author", "date", "summary"],
                "additionalProperties": True
            }
        }
        
        # Load schemas from files or use defaults
        for schema_name, default_schema in default_schemas.items():
            schema_file = self.schemas_dir / f"{schema_name}.json"
            
            if schema_file.exists():
                try:
                    with open(schema_file, 'r', encoding='utf-8') as f:
                        schemas[schema_name] = json.load(f)
                    logger.info(f"Loaded schema: {schema_name}")
                except Exception as e:
                    logger.warning(f"Failed to load schema {schema_name}: {e}, using default")
                    schemas[schema_name] = default_schema
                    self._save_schema(schema_name, default_schema)
            else:
                schemas[schema_name] = default_schema
                self._save_schema(schema_name, default_schema)
        
        return schemas
    
    def _save_schema(self, schema_name: str, schema: Dict[str, Any]):
        """Save a schema to file."""
        try:
            schema_file = self.schemas_dir / f"{schema_name}.json"
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2)
            logger.info(f"Saved schema: {schema_name}")
        except Exception as e:
            logger.error(f"Failed to save schema {schema_name}: {e}")
    
    def _setup_validation_rules(self) -> Dict[str, Any]:
        """Setup template validation rules."""
        return {
            'metadata_required_fields': ['title', 'description', 'category'],
            'metadata_optional_fields': ['tags', 'author', 'version', 'created', 'modified'],
            'variable_naming_pattern': r'^[a-zA-Z_][a-zA-Z0-9_]*$',
            'max_template_size': 1024 * 1024,  # 1MB
            'min_description_length': 10,
            'max_title_length': 100,
            'allowed_extensions': ['.j2', '.jinja', '.jinja2'],
            'forbidden_patterns': [
                r'import\s+os',
                r'import\s+sys',
                r'import\s+subprocess',
                r'exec\s*\(',
                r'eval\s*\(',
                r'__import__'
            ]
        }
    
    def validate_template(self, template_name: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Perform comprehensive template validation.
        
        Args:
            template_name: Name of the template to validate
            context: Optional context for variable validation
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(
            template_name=template_name,
            valid=False,
            errors=[],
            warnings=[],
            metadata_valid=False,
            syntax_valid=False,
            dependencies_valid=False,
            variables=[],
            missing_variables=[],
            unused_variables=[]
        )
        
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            result.errors.append(f"Template file not found: {template_name}")
            return result
        
        try:
            # Read template content
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate file size
            if len(content.encode('utf-8')) > self.validation_rules['max_template_size']:
                result.errors.append("Template file exceeds maximum size limit")
            
            # Validate extension
            if template_path.suffix not in self.validation_rules['allowed_extensions']:
                result.warnings.append(f"Template should use one of: {self.validation_rules['allowed_extensions']}")
            
            # Check for forbidden patterns
            self._check_security_patterns(content, result)
            
            # Validate metadata
            self._validate_metadata(content, result)
            
            # Validate syntax
            self._validate_syntax(content, result)
            
            # Validate variables
            self._validate_variables(content, context, result)
            
            # Validate dependencies
            self._validate_dependencies(template_name, result)
            
            # Overall validation status
            result.valid = (
                len(result.errors) == 0 and
                result.metadata_valid and
                result.syntax_valid and
                result.dependencies_valid
            )
            
            logger.info(f"Template {template_name} validation completed: {'PASSED' if result.valid else 'FAILED'}")
            
        except Exception as e:
            result.errors.append(f"Validation error: {e}")
            logger.error(f"Error validating template {template_name}: {e}")
        
        return result
    
    def _check_security_patterns(self, content: str, result: ValidationResult):
        """Check for potentially dangerous patterns in template content."""
        for pattern in self.validation_rules['forbidden_patterns']:
            if re.search(pattern, content, re.IGNORECASE):
                result.errors.append(f"Forbidden pattern detected: {pattern}")
    
    def _validate_metadata(self, content: str, result: ValidationResult):
        """Validate template metadata."""
        try:
            metadata = self._extract_metadata(content)
            
            if not metadata:
                result.warnings.append("No metadata found in template")
                return
            
            # Check required fields
            for field in self.validation_rules['metadata_required_fields']:
                if field not in metadata or not metadata[field].strip():
                    result.errors.append(f"Required metadata field missing or empty: {field}")
            
            # Validate field values
            if 'title' in metadata:
                title_len = len(metadata['title'])
                if title_len > self.validation_rules['max_title_length']:
                    result.errors.append(f"Title too long: {title_len} > {self.validation_rules['max_title_length']}")
            
            if 'description' in metadata:
                desc_len = len(metadata['description'])
                if desc_len < self.validation_rules['min_description_length']:
                    result.errors.append(f"Description too short: {desc_len} < {self.validation_rules['min_description_length']}")
            
            result.metadata_valid = len([e for e in result.errors if 'metadata' in e.lower()]) == 0
            
        except Exception as e:
            result.errors.append(f"Metadata validation error: {e}")
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from template content."""
        metadata = {}
        lines = content.split('\n')
        
        in_metadata = False
        for line in lines:
            line = line.strip()
            
            if line.startswith('{#') and 'METADATA' in line:
                in_metadata = True
                continue
            elif line == '#}' and in_metadata:
                break
            elif in_metadata and ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _validate_syntax(self, content: str, result: ValidationResult):
        """Validate Jinja2 template syntax."""
        try:
            from jinja2 import Environment, DictLoader
            
            # Create a test environment
            env = Environment(loader=DictLoader({'test': content}))
            
            # Try to parse the template
            env.get_template('test')
            
            result.syntax_valid = True
            
        except Exception as e:
            result.errors.append(f"Syntax error: {e}")
            result.syntax_valid = False
    
    def _validate_variables(self, content: str, context: Optional[Dict[str, Any]], result: ValidationResult):
        """Validate template variables."""
        try:
            from jinja2 import Environment, meta
            
            env = Environment()
            ast = env.parse(content)
            
            # Find all variables
            result.variables = list(meta.find_undeclared_variables(ast))
            
            # Validate variable names
            for var in result.variables:
                if not re.match(self.validation_rules['variable_naming_pattern'], var):
                    result.warnings.append(f"Variable name doesn't follow naming convention: {var}")
            
            # Check against context if provided
            if context:
                result.missing_variables = [var for var in result.variables if var not in context]
                result.unused_variables = [var for var in context.keys() if var not in result.variables]
                
                if result.missing_variables:
                    result.warnings.append(f"Variables missing from context: {result.missing_variables}")
                
                if result.unused_variables:
                    result.warnings.append(f"Unused context variables: {result.unused_variables}")
            
        except Exception as e:
            result.errors.append(f"Variable validation error: {e}")
    
    def _validate_dependencies(self, template_name: str, result: ValidationResult):
        """Validate template dependencies."""
        try:
            # Check if template extends another template
            template_path = self.templates_dir / template_name
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find extends statements
            extends_pattern = r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}'
            extends_matches = re.findall(extends_pattern, content)
            
            for extended_template in extends_matches:
                extended_path = self.templates_dir / extended_template
                if not extended_path.exists():
                    result.errors.append(f"Extended template not found: {extended_template}")
            
            # Find include statements
            include_pattern = r'{%\s*include\s+["\']([^"\']+)["\']\s*%}'
            include_matches = re.findall(include_pattern, content)
            
            for included_template in include_matches:
                included_path = self.templates_dir / included_template
                if not included_path.exists():
                    result.errors.append(f"Included template not found: {included_template}")
            
            result.dependencies_valid = len([e for e in result.errors if 'template not found' in e.lower()]) == 0
            
        except Exception as e:
            result.errors.append(f"Dependency validation error: {e}")
    
    def validate_context_against_schema(self, context: Dict[str, Any], schema_name: str) -> ValidationResult:
        """
        Validate context data against a JSON schema.
        
        Args:
            context: Context data to validate
            schema_name: Name of the schema to validate against
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(
            template_name=f"context_validation_{schema_name}",
            valid=False,
            errors=[],
            warnings=[],
            metadata_valid=True,
            syntax_valid=True,
            dependencies_valid=True,
            variables=list(context.keys()),
            missing_variables=[],
            unused_variables=[]
        )
        
        if schema_name not in self.schemas:
            result.errors.append(f"Schema not found: {schema_name}")
            return result
        
        try:
            schema = self.schemas[schema_name]
            validate(instance=context, schema=schema)
            result.valid = True
            
        except ValidationError as e:
            result.errors.append(f"Schema validation error: {e.message}")
        except Exception as e:
            result.errors.append(f"Validation error: {e}")
        
        return result
    
    def get_schema_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """
        Get schema suggestions based on context keys.
        
        Args:
            context: Context data to analyze
            
        Returns:
            List of suggested schema names
        """
        suggestions = []
        context_keys = set(context.keys())
        
        for schema_name, schema in self.schemas.items():
            if 'properties' in schema:
                schema_keys = set(schema['properties'].keys())
                required_keys = set(schema.get('required', []))
                
                # Calculate match score
                match_score = len(context_keys & schema_keys) / len(schema_keys | context_keys)
                required_match = len(context_keys & required_keys) / len(required_keys) if required_keys else 1.0
                
                # Suggest if good match
                if match_score > 0.5 and required_match > 0.7:
                    suggestions.append(schema_name)
        
        return suggestions
    
    def generate_validation_report(self, results: List[ValidationResult]) -> str:
        """
        Generate a comprehensive validation report.
        
        Args:
            results: List of validation results
            
        Returns:
            Formatted validation report
        """
        report_lines = [
            "# Template Validation Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Templates validated: {len(results)}",
            ""
        ]
        
        passed = [r for r in results if r.valid]
        failed = [r for r in results if not r.valid]
        
        report_lines.extend([
            f"## Summary",
            f"- ✅ Passed: {len(passed)}",
            f"- ❌ Failed: {len(failed)}",
            f"- Success rate: {len(passed)/len(results)*100:.1f}%",
            ""
        ])
        
        if failed:
            report_lines.extend([
                "## Failed Templates",
                ""
            ])
            
            for result in failed:
                report_lines.extend([
                    f"### {result.template_name}",
                    f"- Metadata valid: {'✅' if result.metadata_valid else '❌'}",
                    f"- Syntax valid: {'✅' if result.syntax_valid else '❌'}",
                    f"- Dependencies valid: {'✅' if result.dependencies_valid else '❌'}",
                    ""
                ])
                
                if result.errors:
                    report_lines.append("**Errors:**")
                    for error in result.errors:
                        report_lines.append(f"- {error}")
                    report_lines.append("")
                
                if result.warnings:
                    report_lines.append("**Warnings:**")
                    for warning in result.warnings:
                        report_lines.append(f"- {warning}")
                    report_lines.append("")
        
        return '\n'.join(report_lines)
    
    def create_schema(self, schema_name: str, schema: Dict[str, Any]) -> bool:
        """
        Create a new validation schema.
        
        Args:
            schema_name: Name for the new schema
            schema: JSON schema definition
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate the schema itself
            Draft7Validator.check_schema(schema)
            
            # Save schema
            self.schemas[schema_name] = schema
            self._save_schema(schema_name, schema)
            
            logger.info(f"Schema {schema_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating schema {schema_name}: {e}")
            return False 