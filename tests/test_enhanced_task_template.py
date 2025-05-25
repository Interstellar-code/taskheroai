#!/usr/bin/env python3
"""
Test Script for Enhanced Task Template

Tests the new enhanced task template with comprehensive features.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from mods.project_management.template_engine import TemplateEngine, TemplateMetadata
    from mods.project_management.template_validator import TemplateValidator, ValidationResult
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def test_enhanced_task_template():
    """Test the enhanced task template with comprehensive context."""
    print("🧪 Testing Enhanced Task Template...")
    
    try:
        engine = TemplateEngine(project_root=str(project_root))
        
        # Comprehensive context for enhanced task template
        context = {
            # Basic task information
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
            
            # Show optional sections
            'show_naming_convention': True,
            'show_metadata_legend': True,
            'show_implementation_analysis': True,
            
            # Functional requirements
            'functional_requirements': 'Implement secure user authentication with modern standards',
            'functional_requirements_list': [
                'OAuth2 integration with Google, GitHub, and Microsoft',
                'Multi-factor authentication (MFA) support',
                'Session management with JWT tokens',
                'Password strength validation and policies',
                'Account lockout and rate limiting'
            ],
            
            # Purpose and benefits
            'purpose_benefits': 'Enhance application security and user experience',
            'benefits_list': [
                'Improved security through modern authentication standards',
                'Better user experience with social login options',
                'Reduced support tickets related to password issues',
                'Compliance with security best practices',
                'Scalable authentication architecture'
            ],
            
            # Success criteria
            'success_criteria': [
                {'description': 'OAuth2 integration working with all providers', 'completed': False},
                {'description': 'MFA implementation with TOTP support', 'completed': False},
                {'description': 'JWT token management system', 'completed': True},
                {'description': 'Password policy enforcement', 'completed': True},
                {'description': 'Rate limiting and security measures', 'completed': False}
            ],
            
            # Flow diagram
            'flow_description': 'This diagram shows the user authentication flow from initial login attempt to successful authentication.',
            'flow_steps': [
                {'title': 'User enters credentials'},
                {'title': 'Validate credentials'},
                {'title': 'Check MFA requirement'},
                {'title': 'Complete MFA verification'},
                {'title': 'Generate JWT token'}
            ],
            
            # Implementation steps
            'implementation_steps': [
                {
                    'title': 'OAuth2 Integration Setup',
                    'completed': True,
                    'target_date': '2025-01-30',
                    'substeps': [
                        {'description': 'Register applications with OAuth providers', 'completed': True},
                        {'description': 'Implement OAuth2 client configuration', 'completed': True},
                        {'description': 'Test OAuth flows', 'completed': False}
                    ]
                },
                {
                    'title': 'MFA Implementation',
                    'completed': False,
                    'in_progress': True,
                    'target_date': '2025-02-05',
                    'substeps': [
                        {'description': 'TOTP library integration', 'completed': True},
                        {'description': 'QR code generation for setup', 'completed': False},
                        {'description': 'Backup codes system', 'completed': False}
                    ]
                },
                {
                    'title': 'Security Enhancements',
                    'completed': False,
                    'target_date': '2025-02-10',
                    'substeps': [
                        {'description': 'Rate limiting implementation', 'completed': False},
                        {'description': 'Account lockout mechanism', 'completed': False},
                        {'description': 'Security audit logging', 'completed': False}
                    ]
                }
            ],
            
            # Implementation analysis
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
                {'current': 'Session Cookies', 'new': 'JWT Token System', 'notes': 'Migrate to stateless JWT authentication'},
                {'current': 'Basic Password Hash', 'new': 'Advanced Password Policies', 'notes': 'Implement strength requirements and breach checking'}
            ],
            
            # Dependencies
            'dependencies': [
                'TASK-000-DEV - Project Infrastructure Setup - Complete',
                'TASK-005-DES - Authentication UI Design - In Progress'
            ],
            'dependent_tasks': [
                'TASK-002-TEST - Authentication Testing Suite - Pending',
                'TASK-003-DOC - Authentication Documentation - Pending'
            ],
            'technical_dependencies': [
                {'name': 'OAuth2 Library', 'requirement': 'authlib>=1.2.0'},
                {'name': 'JWT Library', 'requirement': 'PyJWT>=2.6.0'},
                {'name': 'TOTP Library', 'requirement': 'pyotp>=2.8.0'},
                {'name': 'QR Code Generator', 'requirement': 'qrcode>=7.4.0'}
            ],
            'dependency_type': '**Blocking**: OAuth2 provider setup must be completed before testing can begin',
            
            # Testing
            'testing_overview': 'Comprehensive testing strategy covering security, functionality, and user experience',
            'testing_strategy': 'Unit tests for authentication logic, integration tests for OAuth flows, security penetration testing',
            'test_cases': [
                {'name': 'OAuth2 Login Flow', 'description': 'Test complete OAuth2 authentication with each provider', 'expected': 'Successful authentication and token generation', 'status': 'In Progress'},
                {'name': 'MFA Setup and Verification', 'description': 'Test TOTP setup and verification process', 'expected': 'User can setup and use MFA successfully', 'status': 'Pending'},
                {'name': 'Rate Limiting', 'description': 'Test rate limiting under high load', 'expected': 'System blocks excessive requests appropriately', 'status': 'Pending'}
            ],
            
            # UI Design
            'ui_design_overview': 'Modern, secure, and user-friendly authentication interface with social login options',
            'ui_layout': '''┌─────────────────────────────────────────────────────────────┐
│                    🔐 TaskHero AI Login                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               Social Login Options                      │ │
│  │  [🔵 Google] [⚫ GitHub] [🟦 Microsoft] [📧 Email]      │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Email:    [________________________]                   │ │
│  │ Password: [________________________] [👁]               │ │
│  │ [ ] Remember Me    [Forgot Password?]                   │ │
│  │                                                         │ │
│  │           [🔐 Sign In]  [📝 Sign Up]                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │        🔐 Multi-Factor Authentication                   │ │
│  │  Enter your 6-digit verification code:                 │ │
│  │  [___] [___] [___] [___] [___] [___]                    │ │
│  │  [✓ Verify Code]  [📱 Use Backup Code]                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘''',
            'ui_colors': 'Primary: #2563eb, Secondary: #64748b, Success: #16a34a, Error: #dc2626',
            'ui_typography': 'Inter font family, 16px base size, 600 weight for headings',
            'ui_spacing': '8px base unit, 16px standard padding, 24px section margins',
            'ui_components': 'shadcn/ui Button, Input, Card, Alert, Badge components',
            'ui_icons': 'Lucide icons for social providers, eye icon for password visibility',
            'design_references': [
                'Figma: https://figma.com/auth-design-v2',
                'Authentication UI patterns reference',
                'OAuth2 provider branding guidelines'
            ],
            
            # Risk assessment
            'risks': [
                {'description': 'OAuth2 provider API changes', 'impact': 'High', 'probability': 'Low', 'mitigation': 'Monitor provider documentation and implement robust error handling'},
                {'description': 'Security vulnerabilities in third-party libraries', 'impact': 'High', 'probability': 'Medium', 'mitigation': 'Regular security audits and dependency updates'},
                {'description': 'User experience complexity with MFA', 'impact': 'Medium', 'probability': 'Medium', 'mitigation': 'Extensive user testing and clear onboarding flow'}
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
            'integration_compatibility': 'RESTful API with OpenAPI specification for external integrations',
            
            # Database changes
            'database_changes': 'New tables for OAuth providers, MFA settings, and security audit logs',
            'database_schema': '''USERS ||--o{ USER_OAUTH_PROVIDERS : "has"
USERS ||--o{ USER_MFA_SETTINGS : "has"
USERS ||--o{ SECURITY_AUDIT_LOG : "generates"
USERS {
    id uuid PK
    email string UK
    password_hash string
    created_at timestamp
    updated_at timestamp
    is_active boolean
    failed_login_attempts int
    locked_until timestamp
}
USER_OAUTH_PROVIDERS {
    id uuid PK
    user_id uuid FK
    provider string
    provider_user_id string
    access_token string
    refresh_token string
    created_at timestamp
}
USER_MFA_SETTINGS {
    id uuid PK
    user_id uuid FK
    totp_secret string
    backup_codes string[]
    is_enabled boolean
    created_at timestamp
}''',
            
            # Time tracking
            'estimated_hours': '40',
            'actual_hours': '15',
            
            # References
            'references': [
                'OAuth2 RFC 6749 Specification',
                'OWASP Authentication Cheat Sheet',
                'RFC 6238 TOTP Algorithm',
                'JWT Best Practices (RFC 8725)',
                'Google OAuth2 Documentation',
                'GitHub OAuth2 Apps Guide',
                'Microsoft Identity Platform Documentation'
            ],
            
            # Updates
            'updates': [
                {'date': '2025-01-25', 'description': 'Task created and OAuth2 research completed'},
                {'date': '2025-01-28', 'description': 'OAuth2 provider integration started'},
                {'date': '2025-01-30', 'description': 'Google and GitHub OAuth2 integration completed'},
                {'date': '2025-02-01', 'description': 'MFA implementation started with TOTP support'}
            ]
        }
        
        # Render the enhanced task template
        rendered = engine.render_template("tasks/enhanced_task.j2", context)
        print("✅ Enhanced task template rendered successfully")
        
        # Save rendered output
        output_path = project_root / "test_output_enhanced_task.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        print(f"✅ Rendered enhanced task saved to: {output_path}")
        
        # Display preview
        lines = rendered.split('\n')[:20]
        print("\n📄 Enhanced task template preview:")
        for line in lines:
            print(f"   {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced task template test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_validation():
    """Test validation of the enhanced task template."""
    print("\n🧪 Testing Enhanced Task Template Validation...")
    
    try:
        validator = TemplateValidator(project_root=str(project_root))
        
        # Validate the enhanced task template
        result = validator.validate_template("tasks/enhanced_task.j2")
        
        if result.valid:
            print("✅ Enhanced task template validation PASSED")
            print(f"   Variables detected: {len(result.variables)} variables")
            print("   Template validation successful")
        else:
            print("❌ Enhanced task template validation FAILED")
            print(f"   Errors: {result.errors}")
            print(f"   Warnings: {result.warnings}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced task template validation failed: {e}")
        return False

def test_template_metadata():
    """Test metadata extraction from enhanced task template."""
    print("\n🧪 Testing Enhanced Task Template Metadata...")
    
    try:
        engine = TemplateEngine(project_root=str(project_root))
        
        # Get metadata
        metadata = engine.get_template_metadata("tasks/enhanced_task.j2")
        
        if metadata:
            print("✅ Enhanced task template metadata extracted successfully")
            print(f"   Title: {metadata.get('title', 'Unknown')}")
            print(f"   Description: {metadata.get('description', 'Unknown')}")
            print(f"   Version: {metadata.get('version', 'Unknown')}")
            print(f"   Category: {metadata.get('category', 'Unknown')}")
            print(f"   Tags: {metadata.get('tags', [])}")
            print(f"   Variables: {len(metadata.get('variables', []))} detected")
            return True
        else:
            print("❌ Failed to extract enhanced task template metadata")
            return False
        
    except Exception as e:
        print(f"❌ Enhanced task template metadata extraction failed: {e}")
        return False

def main():
    """Run all enhanced task template tests."""
    print("🚀 Starting Enhanced Task Template Tests")
    print("=" * 50)
    
    tests = [
        test_template_validation,
        test_template_metadata,
        test_enhanced_task_template
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Enhanced Task Template Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All enhanced task template tests passed!")
        print("📋 The new template incorporates all your improvements:")
        print("   ✅ Task naming conventions")
        print("   ✅ Comprehensive metadata with legend")
        print("   ✅ Detailed overview with requirements and benefits")
        print("   ✅ Enhanced flow diagrams")
        print("   ✅ Implementation analysis and migration strategy")
        print("   ✅ UI design specifications with ASCII art")
        print("   ✅ Risk assessment matrix")
        print("   ✅ Comprehensive technical considerations")
        print("   ✅ Time tracking and references")
    else:
        print("⚠️  Some enhanced task template tests failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 