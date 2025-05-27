#!/usr/bin/env python3
"""
PowerShell Syntax Validation Script
Validates basic PowerShell syntax without requiring PowerShell to be installed
"""

import re
import sys
from pathlib import Path

def validate_powershell_syntax(file_path):
    """Validate basic PowerShell syntax"""
    print(f"🔍 Validating PowerShell syntax for: {file_path}")
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    errors = []
    warnings = []
    
    # Check balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
    else:
        print(f"✅ Braces balanced: {open_braces} pairs")
    
    # Check balanced parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    if open_parens != close_parens:
        errors.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
    else:
        print(f"✅ Parentheses balanced: {open_parens} pairs")
    
    # Check balanced double quotes
    double_quotes = content.count('"')
    if double_quotes % 2 != 0:
        errors.append(f"Unbalanced double quotes: {double_quotes} total")
    else:
        print(f"✅ Double quotes balanced: {double_quotes // 2} pairs")
    
    # Check for here-strings
    here_string_pattern = r"@['\"][\s\S]*?['\"]@"
    here_strings = re.findall(here_string_pattern, content)
    print(f"📝 Found {len(here_strings)} here-string(s)")
    
    # Check for try-catch blocks
    try_blocks = len(re.findall(r'\btry\s*{', content, re.IGNORECASE))
    catch_blocks = len(re.findall(r'}\s*catch\s*{', content, re.IGNORECASE))
    if try_blocks != catch_blocks:
        errors.append(f"Unmatched try-catch blocks: {try_blocks} try, {catch_blocks} catch")
    else:
        print(f"✅ Try-catch blocks balanced: {try_blocks} pairs")
    
    # Check for function definitions
    functions = re.findall(r'function\s+([a-zA-Z-]+)', content, re.IGNORECASE)
    print(f"🔧 Found {len(functions)} function(s): {', '.join(functions[:5])}{'...' if len(functions) > 5 else ''}")
    
    # Check for param blocks
    param_blocks = len(re.findall(r'\bparam\s*\(', content, re.IGNORECASE))
    print(f"⚙️ Found {param_blocks} param block(s)")
    
    # Check for potential issues
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # Check for lines ending with backslash (potential line continuation issues)
        if line.rstrip().endswith('\\'):
            warnings.append(f"Line {i}: Potential line continuation issue")
        
        # Check for unescaped quotes in strings
        if re.search(r'"[^"]*"[^"]*"[^"]*"', line):
            warnings.append(f"Line {i}: Potential unescaped quotes in string")
    
    # Report results
    print("\n📊 Validation Results:")
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print("⚠️ WARNINGS:")
        for warning in warnings[:10]:  # Limit to first 10 warnings
            print(f"   • {warning}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more warnings")
    
    if not errors and not warnings:
        print("✅ No syntax issues detected!")
    elif not errors:
        print("✅ No critical errors found (only warnings)")
    
    return len(errors) == 0

def main():
    """Main validation function"""
    print("🔍 PowerShell Syntax Validator")
    print("=" * 50)
    
    scripts = [
        "setup_windows.ps1",
        "standalone_setup_windows.ps1"
    ]
    
    all_valid = True
    
    for script in scripts:
        print(f"\n📄 Checking {script}...")
        if not validate_powershell_syntax(script):
            all_valid = False
        print("-" * 30)
    
    print(f"\n🎯 Overall Result:")
    if all_valid:
        print("✅ All scripts passed validation!")
        return 0
    else:
        print("❌ Some scripts have issues that need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
