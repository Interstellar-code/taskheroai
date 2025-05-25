#!/usr/bin/env python3
"""
Focused Test for Enhanced Task Template
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from mods.project_management.template_engine import TemplateEngine
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_enhanced_task():
    """Test the working enhanced task template."""
    print("🧪 Testing Enhanced Task Template...")
    
    try:
        engine = TemplateEngine(project_root=str(project_root))
        
        # Simple context for testing
        context = {
            'task_id': 'TASK-001-DEV',
            'title': 'Enhanced User Authentication System',
            'brief_description': 'Implement a comprehensive user authentication system with OAuth2, MFA, and advanced security features.',
            'priority': 'High',
            'status': 'In Progress',
            'assignee': 'Development Team',
            'task_type': 'DEV',
            'due_date': '2025-02-15',
            'sequence': '1',
            'estimated_effort': 'Large',
            'related_epic': 'User Management Epic',
            'tags': ['authentication', 'security', 'oauth2', 'mfa'],
            'current_date': '2025-01-28',
            'functional_requirements': 'Implement secure user authentication with modern standards',
            'functional_requirements_list': [
                'OAuth2 integration with Google, GitHub, and Microsoft',
                'Multi-factor authentication (MFA) support',
                'Session management with JWT tokens'
            ],
            'purpose_benefits': 'Enhance application security and user experience',
            'benefits_list': [
                'Improved security through modern authentication standards',
                'Better user experience with social login options',
                'Reduced support tickets related to password issues'
            ],
            'success_criteria': [
                {'description': 'OAuth2 integration working with all providers', 'completed': False},
                {'description': 'MFA implementation with TOTP support', 'completed': False},
                {'description': 'JWT token management system', 'completed': True}
            ],
            'detailed_description': 'This task involves implementing a comprehensive authentication system with OAuth2 integration, multi-factor authentication, and advanced security measures.',
            'testing_overview': 'Comprehensive testing strategy covering security, functionality, and user experience',
            'estimated_hours': '40',
            'actual_hours': '15',
            # Implementation analysis variables
            'current_implementation': 'Basic username/password authentication with session cookies',
            'current_components': 'Simple login form, password hashing, session management',
            'current_limitations': 'No social login, weak password policies, limited security features',
            'new_features': 'OAuth2 social login with Google, GitHub, Microsoft support',
            'new_features_2': 'Multi-factor authentication with TOTP and backup codes',
            'new_features_3': 'Advanced security with rate limiting and audit logging',
            'migration_approach': 'Gradual migration with backward compatibility for existing users',
            'backward_compatibility': 'Existing users can continue using passwords while new features are optional',
            'risk_mitigation': 'Feature flags, extensive testing, rollback procedures',
            # Component mapping
            'component_mapping': [
                {'current': 'Simple Login Form', 'new': 'Enhanced Login with OAuth Options', 'notes': 'Add social login buttons and MFA fields'},
                {'current': 'Session Cookies', 'new': 'JWT Token System', 'notes': 'Migrate to stateless JWT authentication'}
            ],
            # UI Design
            'ui_design_overview': 'Modern, secure, and user-friendly authentication interface with social login options',
            'ui_colors': 'Primary: #2563eb, Secondary: #64748b, Success: #16a34a, Error: #dc2626',
            'ui_typography': 'Inter font family, 16px base size, 600 weight for headings',
            'ui_spacing': '8px base unit, 16px standard padding, 24px section margins',
            'ui_components': 'shadcn/ui Button, Input, Card, Alert, Badge components',
            'ui_icons': 'Lucide icons for social providers, eye icon for password visibility',
            # Risk assessment
            'risks': [
                {'description': 'OAuth2 provider API changes', 'impact': 'High', 'probability': 'Low', 'mitigation': 'Monitor provider documentation and implement robust error handling'},
                {'description': 'Security vulnerabilities in third-party libraries', 'impact': 'High', 'probability': 'Medium', 'mitigation': 'Regular security audits and dependency updates'}
            ],
            # Technical considerations
            'technical_considerations': 'Security-first approach with defense in depth, scalable architecture for high user loads',
            'state_management': 'Stateless JWT tokens with refresh token rotation for security',
            'data_persistence': 'Encrypted user credentials, OAuth tokens, and MFA secrets in secure database',
            'state_sync': 'Real-time session validation across multiple devices and browser tabs',
            'component_architecture': 'Modular authentication system with pluggable providers',
            'reusability': 'Generic OAuth2 adapter pattern for easy addition of new providers',
            'integration_patterns': 'Middleware-based authentication with clean API integration',
            'performance_requirements': 'Sub-200ms authentication response time, 10,000 concurrent users',
            'memory_management': 'Efficient token caching with TTL and memory-safe operations',
            'loading_optimizations': 'Lazy loading of OAuth2 providers and progressive enhancement',
            'browser_compatibility': 'Modern browsers (Chrome 90+, Firefox 88+, Safari 14+)',
            'backward_compatibility_notes': 'Graceful degradation for users without JavaScript',
            'integration_compatibility': 'RESTful API with OpenAPI specification for external integrations'
        }
        
        # Render the enhanced task template
        rendered = engine.render_template("tasks/enhanced_task.j2", context)
        print("✅ Enhanced task template rendered successfully")
        
        # Save rendered output
        output_path = project_root / "test_output_enhanced_task_working.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        print(f"✅ Rendered enhanced task saved to: {output_path}")
        
        # Show some stats
        lines = rendered.split('\n')
        print(f"📊 Template stats:")
        print(f"   Lines: {len(lines)}")
        print(f"   Size: {len(rendered)} characters")
        
        # Display first 15 lines
        print("\n📄 Enhanced task template preview:")
        for i, line in enumerate(lines[:15], 1):
            print(f"   {i:2}: {line}")
        
        print(f"\n🎉 Enhanced task template is working!")
        print(f"📁 Output saved to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced task template test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the focused test."""
    print("🚀 Enhanced Task Template Working Test")
    print("=" * 50)
    
    if test_enhanced_task():
        print("\n✨ SUCCESS: Enhanced task template is fully functional!")
    else:
        print("\n❌ FAILED: Enhanced task template has issues")

if __name__ == "__main__":
    main() 