# PowerShell Syntax Test Script
# This script tests the syntax of the setup scripts

param(
    [switch]$Verbose
)

function Test-PowerShellSyntax {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Host "❌ File not found: $FilePath" -ForegroundColor Red
        return $false
    }
    
    try {
        # Test syntax by parsing the script
        $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $FilePath -Raw), [ref]$null)
        Write-Host "✅ Syntax OK: $FilePath" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Syntax Error in $FilePath`: $_" -ForegroundColor Red
        return $false
    }
}

Write-Host "🔍 Testing PowerShell Script Syntax" -ForegroundColor Cyan
Write-Host "=" * 50

$scripts = @(
    "setup_windows.ps1",
    "standalone_setup_windows.ps1"
)

$allPassed = $true

foreach ($script in $scripts) {
    if (-not (Test-PowerShellSyntax $script)) {
        $allPassed = $false
    }
}

Write-Host ""
if ($allPassed) {
    Write-Host "🎉 All PowerShell scripts have valid syntax!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some scripts have syntax errors that need to be fixed." -ForegroundColor Yellow
}

Write-Host ""
