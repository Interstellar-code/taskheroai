"""
Project Templates Module

Handles template management functionality for creating standardized documents
and project structures from TaskHeroMD templates.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("TaskHeroAI.ProjectManagement.ProjectTemplates")


class ProjectTemplates:
    """Manages project templates and document generation."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize ProjectTemplates.
        
        Args:
            project_root: Root directory for project management. Defaults to current working directory.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.templates_dir = self.project_root / "mods" / "project_management" / "templates"
        
    def get_available_templates(self) -> List[str]:
        """Get list of available template files.
        
        Returns:
            List of template filenames
        """
        if not self.templates_dir.exists():
            return []
        
        templates = []
        for file_path in self.templates_dir.glob("*.md"):
            templates.append(file_path.name)
        
        return sorted(templates)
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, str]]:
        """Get information about a specific template.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Dictionary with template information or None if not found
        """
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract basic info from template
            lines = content.split('\n')
            title = ""
            description = ""
            
            # Get title from first line
            if lines and lines[0].startswith('# '):
                title = lines[0][2:].strip()
            
            # Look for description in early lines
            for line in lines[:10]:
                if line.strip() and not line.startswith('#') and not line.startswith('##'):
                    description = line.strip()
                    break
            
            return {
                'name': template_name,
                'title': title,
                'description': description,
                'size': len(content),
                'modified': datetime.fromtimestamp(template_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            }
            
        except Exception as e:
            logger.error(f"Error reading template {template_name}: {e}")
            return None
    
    def create_document_from_template(self, 
                                    template_name: str, 
                                    output_path: str, 
                                    replacements: Optional[Dict[str, str]] = None) -> bool:
        """Create a new document from a template.
        
        Args:
            template_name: Name of the template file to use
            output_path: Path where the new document should be created
            replacements: Dictionary of placeholder replacements
            
        Returns:
            True if successful, False otherwise
        """
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            logger.error(f"Template not found: {template_name}")
            return False
        
        try:
            # Read template content
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply replacements if provided
            if replacements:
                for placeholder, value in replacements.items():
                    content = content.replace(f"[{placeholder}]", value)
            
            # Apply default replacements
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            content = content.replace("[DATE]", current_date)
            content = content.replace("[DATETIME]", current_datetime)
            content = content.replace("[YEAR]", str(datetime.now().year))
            
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write new document
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created document from template {template_name}: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating document from template {template_name}: {e}")
            return False
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """Validate a template file and return validation results.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Dictionary with validation results
        """
        template_path = self.templates_dir / template_name
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'placeholders': []
        }
        
        if not template_path.exists():
            result['errors'].append(f"Template file not found: {template_name}")
            return result
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for basic structure
            lines = content.split('\n')
            
            # Check if it has a title
            if not lines or not lines[0].startswith('# '):
                result['warnings'].append("Template should start with a title (# Title)")
            
            # Find placeholders
            import re
            placeholders = re.findall(r'\[([A-Z_]+)\]', content)
            result['placeholders'] = list(set(placeholders))
            
            # Basic validation passed
            result['valid'] = True
            
        except Exception as e:
            result['errors'].append(f"Error reading template: {e}")
        
        return result
    
    def copy_template(self, source_template: str, new_name: str) -> bool:
        """Create a copy of an existing template.
        
        Args:
            source_template: Name of the template to copy
            new_name: Name for the new template
            
        Returns:
            True if successful, False otherwise
        """
        source_path = self.templates_dir / source_template
        target_path = self.templates_dir / new_name
        
        if not source_path.exists():
            logger.error(f"Source template not found: {source_template}")
            return False
        
        if target_path.exists():
            logger.error(f"Target template already exists: {new_name}")
            return False
        
        try:
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied template {source_template} to {new_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error copying template: {e}")
            return False
    
    def get_template_content(self, template_name: str) -> Optional[str]:
        """Get the raw content of a template.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Template content as string or None if not found
        """
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading template {template_name}: {e}")
            return None
    
    def create_custom_template(self, 
                             template_name: str, 
                             title: str, 
                             content_sections: List[str]) -> bool:
        """Create a new custom template.
        
        Args:
            template_name: Name for the new template file
            title: Title for the template document
            content_sections: List of section names to include
            
        Returns:
            True if successful, False otherwise
        """
        template_path = self.templates_dir / template_name
        
        if template_path.exists():
            logger.error(f"Template already exists: {template_name}")
            return False
        
        try:
            # Build template content
            content = f"# {title}\n\n"
            
            # Add metadata section
            content += "## Metadata\n"
            content += "- **Created:** [DATE]\n"
            content += "- **Author:** [AUTHOR]\n"
            content += "- **Version:** [VERSION]\n"
            content += "- **Status:** [STATUS]\n\n"
            
            # Add custom sections
            for section in content_sections:
                content += f"## {section}\n"
                content += "[CONTENT]\n\n"
            
            # Write template file
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created custom template: {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom template: {e}")
            return False 