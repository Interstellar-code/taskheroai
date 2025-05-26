#!/usr/bin/env pwsh
<#
.SYNOPSIS
    TaskHero AI Standalone Setup Script for Windows

.DESCRIPTION
    This script can be downloaded and run independently to:
    1. Clone the TaskHero AI repository from GitHub
    2. Run the complete installation and configuration process
    3. Set up the application ready to use

.PARAMETER Force
    Force re-installation even if TaskHero AI is already present

.PARAMETER TargetDir
    Directory where TaskHero AI should be installed (default: current directory)

.EXAMPLE
    .\standalone_setup_windows.ps1

.EXAMPLE
    .\standalone_setup_windows.ps1 -Force -TargetDir "C:\MyProjects"
#>

param(
    [switch]$Force,
    [string]$TargetDir = (Get-Location).Path
)

# Script configuration
$RepoUrl = "https://github.com/Interstellar-code/taskheroai.git"
$ProjectName = "taskheroai"
$ProjectPath = Join-Path $TargetDir $ProjectName

# Color configuration for output
$Colors = @{
    Primary = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Blue"
    Text = "White"
}

function Write-ColoredLine {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-SectionHeader {
    param([string]$Title, [string]$Icon = "🔧")
    Write-Host ""
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-ColoredLine "$Icon $Title" $Colors.Primary
    Write-ColoredLine "===============================================================================" $Colors.Primary
}

function Test-GitInstalled {
    try {
        $null = Get-Command git -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Test-PythonInstalled {
    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            return ($major -eq 3 -and $minor -ge 8) -or ($major -gt 3)
        }
        return $false
    } catch {
        return $false
    }
}

function Install-Git {
    Write-ColoredLine "Git is required but not installed." $Colors.Warning
    Write-ColoredLine "Please install Git from: https://git-scm.com/download/win" $Colors.Info

    $choice = Read-Host "Would you like to open the Git download page? (y/n)"
    if ($choice -eq 'y' -or $choice -eq 'Y') {
        Start-Process "https://git-scm.com/download/win"
    }

    Write-ColoredLine "Please install Git and run this script again." $Colors.Error
    Read-Host "Press Enter to exit"
    exit 1
}

function Install-Python {
    Write-ColoredLine "Python 3.8+ is required but not installed or not the correct version." $Colors.Warning
    Write-ColoredLine "Please install Python from: https://www.python.org/downloads/" $Colors.Info

    $choice = Read-Host "Would you like to open the Python download page? (y/n)"
    if ($choice -eq 'y' -or $choice -eq 'Y') {
        Start-Process "https://www.python.org/downloads/"
    }

    Write-ColoredLine "Please install Python 3.8+ and run this script again." $Colors.Error
    Read-Host "Press Enter to exit"
    exit 1
}

# Main script execution
Clear-Host

Write-SectionHeader "TaskHero AI Standalone Setup" "🚀"
Write-ColoredLine "This script will download and set up TaskHero AI automatically." $Colors.Info
Write-ColoredLine "Repository: $RepoUrl" $Colors.Text
Write-ColoredLine "Target Directory: $TargetDir" $Colors.Text
Write-ColoredLine "Project Path: $ProjectPath" $Colors.Text
Write-Host ""

# Check if project already exists
if (Test-Path $ProjectPath) {
    if (-not $Force) {
        Write-ColoredLine "TaskHero AI already exists at: $ProjectPath" $Colors.Warning
        $choice = Read-Host "Do you want to continue anyway? This will update the existing installation. (y/n)"
        if ($choice -ne 'y' -and $choice -ne 'Y') {
            Write-ColoredLine "Setup cancelled by user." $Colors.Info
            exit 0
        }
    }
    Write-ColoredLine "Proceeding with existing installation..." $Colors.Info
}

# Step 1: Check prerequisites
Write-SectionHeader "Step 1: Checking Prerequisites" "🔍"

Write-ColoredLine "Checking Git installation..." $Colors.Info
if (-not (Test-GitInstalled)) {
    Install-Git
}
Write-ColoredLine "✓ Git is installed" $Colors.Success

Write-ColoredLine "Checking Python installation..." $Colors.Info
if (-not (Test-PythonInstalled)) {
    Install-Python
}
Write-ColoredLine "✓ Python 3.8+ is installed" $Colors.Success

# Step 2: Clone or update repository
Write-SectionHeader "Step 2: Repository Setup" "📥"

if (Test-Path $ProjectPath) {
    Write-ColoredLine "Updating existing repository..." $Colors.Info
    try {
        Set-Location $ProjectPath
        & git fetch origin
        & git pull origin master
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredLine "✓ Repository updated successfully" $Colors.Success
        } else {
            Write-ColoredLine "⚠ Repository update had issues, but continuing..." $Colors.Warning
        }
    } catch {
        Write-ColoredLine "⚠ Could not update repository, but continuing with existing files..." $Colors.Warning
    }
} else {
    Write-ColoredLine "Cloning TaskHero AI repository..." $Colors.Info
    try {
        Set-Location $TargetDir
        & git clone $RepoUrl
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredLine "✓ Repository cloned successfully" $Colors.Success
            Set-Location $ProjectPath
        } else {
            Write-ColoredLine "✗ Failed to clone repository" $Colors.Error
            Read-Host "Press Enter to exit"
            exit 1
        }
    } catch {
        Write-ColoredLine "✗ Error during repository cloning: $_" $Colors.Error
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Step 3: Run the main setup script
Write-SectionHeader "Step 3: Running TaskHero AI Setup" "⚙️"

$setupScript = "setup_windows.ps1"
if (Test-Path $setupScript) {
    Write-ColoredLine "Running main setup script..." $Colors.Info
    try {
        # Set execution policy for this session to allow the setup script to run
        $currentPolicy = Get-ExecutionPolicy -Scope Process
        if ($currentPolicy -eq "Restricted") {
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
        }

        if ($Force) {
            & powershell.exe -ExecutionPolicy RemoteSigned -File ".\$setupScript" -Force
        } else {
            & powershell.exe -ExecutionPolicy RemoteSigned -File ".\$setupScript"
        }

        if ($LASTEXITCODE -eq 0) {
            Write-ColoredLine "✓ TaskHero AI setup completed successfully!" $Colors.Success
        } else {
            Write-ColoredLine "⚠ Setup completed with some warnings" $Colors.Warning
        }
    } catch {
        Write-ColoredLine "✗ Error during setup: $_" $Colors.Error
        Write-ColoredLine "You can try running the setup manually:" $Colors.Info
        Write-ColoredLine "  cd $ProjectPath" $Colors.Text
        Write-ColoredLine "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process" $Colors.Text
        Write-ColoredLine "  .\setup_windows.ps1" $Colors.Text
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-ColoredLine "⚠ Main setup script not found, trying batch version..." $Colors.Warning
    $setupBatch = "setup_windows.bat"
    if (Test-Path $setupBatch) {
        Write-ColoredLine "Running batch setup script..." $Colors.Info
        & cmd.exe /c ".\$setupBatch"
    } else {
        Write-ColoredLine "✗ No setup script found in the repository" $Colors.Error
        Write-ColoredLine "Please check the repository contents and run setup manually." $Colors.Info
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Final message
Write-Host ""
Write-SectionHeader "Setup Complete!" "🎉"
Write-ColoredLine "TaskHero AI has been successfully installed!" $Colors.Success
Write-ColoredLine "Location: $ProjectPath" $Colors.Info
Write-Host ""
Write-ColoredLine "To start TaskHero AI in the future:" $Colors.Info
Write-ColoredLine "  cd $ProjectPath" $Colors.Text
Write-ColoredLine "  venv\Scripts\Activate.ps1" $Colors.Text
Write-ColoredLine "  python app.py" $Colors.Text
Write-Host ""
Write-ColoredLine "The application should start automatically now..." $Colors.Info

Read-Host "Press Enter to continue"
