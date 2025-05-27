# TaskHero AI Setup Script for Windows PowerShell
# This script sets up TaskHero AI with all dependencies and configuration

param(
    [switch]$Force,
    [switch]$Help
)

# Color scheme for output
$Colors = @{
    Primary = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
    Accent = "Magenta"
    Text = "Gray"
}

# Helper functions for colored output
function Write-ColoredLine {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $Colors.Success
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $Colors.Error
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor $Colors.Warning
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor $Colors.Info
}

function Write-SectionHeader {
    param([string]$Title, [string]$Icon = "")
    Write-Host ""
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-ColoredLine "  $Icon $Title" $Colors.Primary
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-Host ""
}

function Show-Progress {
    param([int]$Current, [int]$Total, [string]$Activity)
    $percent = [math]::Round(($Current / $Total) * 100)
    Write-Progress -Activity $Activity -Status "Step $Current of $Total" -PercentComplete $percent
}

# Setup completion tracking
function Test-SetupCompleted {
    param([string]$Step)
    $setupFile = ".taskhero_setup.json"
    if (Test-Path $setupFile) {
        try {
            $setupData = Get-Content $setupFile | ConvertFrom-Json
            return $setupData.setup_completed.$Step -eq $true
        } catch {
            return $false
        }
    }
    return $false
}

function Set-SetupCompleted {
    param([string]$Step)
    $setupFile = ".taskhero_setup.json"
    $setupData = @{ setup_completed = @{} }

    if (Test-Path $setupFile) {
        try {
            $jsonContent = Get-Content $setupFile | ConvertFrom-Json
            # Convert PSCustomObject to hashtable for easier manipulation
            $setupData = @{}
            $jsonContent.PSObject.Properties | ForEach-Object {
                if ($_.Name -eq "setup_completed") {
                    $setupData[$_.Name] = @{}
                    $_.Value.PSObject.Properties | ForEach-Object {
                        $setupData["setup_completed"][$_.Name] = $_.Value
                    }
                } else {
                    $setupData[$_.Name] = $_.Value
                }
            }
        } catch {
            $setupData = @{ setup_completed = @{} }
        }
    }

    if (-not $setupData.setup_completed) {
        $setupData.setup_completed = @{}
    }

    $setupData.setup_completed.$Step = $true
    $setupData.setup_completed.last_updated = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.ffffff")

    $setupData | ConvertTo-Json -Depth 10 | Out-File -FilePath $setupFile -Encoding UTF8
    return $true
}

# Function to get user input with validation (adapted from batch script)
function Get-UserInput {
    param(
        [string]$Prompt,
        [string]$ValidationType, # "yn", "path", "option"
        [string]$DefaultValue = "",
        [array]$ValidOptions = $null # New parameter for valid options
    )
    do {
        Write-Host ""
        Write-ColoredLine $Prompt $Colors.Info
        $userInput = Read-Host "Enter your choice"

        if ([string]::IsNullOrWhiteSpace($userInput) -and -not [string]::IsNullOrWhiteSpace($DefaultValue)) {
            $userInput = $DefaultValue
        }

        $isValid = $true
        switch ($ValidationType) {
            "yn" {
                if ($userInput.ToUpper() -notin @("Y", "N")) {
                    Write-Error "[ERROR] Please enter Y or N only."
                    $isValid = $false
                }
            }
            "path" {
                if ([string]::IsNullOrWhiteSpace($userInput)) {
                    Write-Error "[ERROR] Path cannot be empty."
                    $isValid = $false
                }
            }
            "option" {
                if ($ValidOptions -ne $null -and $userInput -notin $ValidOptions) {
                    Write-Error "[ERROR] Please enter one of the valid options: $($ValidOptions -join ', ')."
                    $isValid = $false
                } elseif ($ValidOptions -eq $null) {
                    # This case should ideally not be reached if "option" is used with specific ValidOptions.
                    # If it's a generic "option" without a predefined list, it might need different logic.
                    # For now, assuming ValidOptions will always be provided for "option" type.
                    Write-Error "[ERROR] Invalid option. No valid options specified for validation."
                    $isValid = $false
                }
            }
        }
    } while (-not $isValid)
    return $userInput
}

# Function to save configuration to .taskhero_setup.json (consolidated settings file)
function Save-AppConfig {
    param(
        [string]$Key,
        $Value
    )
    $setupFile = ".taskhero_setup.json"
    $setupData = @{ setup_completed = @{} }

    if (Test-Path $setupFile) {
        try {
            $jsonContent = Get-Content $setupFile | ConvertFrom-Json
            # Convert PSCustomObject to hashtable for easier manipulation
            $setupData = @{}
            $jsonContent.PSObject.Properties | ForEach-Object {
                if ($_.Name -eq "setup_completed") {
                    $setupData[$_.Name] = @{}
                    $_.Value.PSObject.Properties | ForEach-Object {
                        $setupData["setup_completed"][$_.Name] = $_.Value
                    }
                } else {
                    $setupData[$_.Name] = $_.Value
                }
            }
        } catch {
            Write-Warning "Failed to read .taskhero_setup.json, creating new one."
            $setupData = @{ setup_completed = @{} }
        }
    }

    $setupData[$Key] = $Value
    $setupData | ConvertTo-Json -Depth 10 | Out-File -FilePath $setupFile -Encoding UTF8
    Write-Success "Configuration '$Key' saved to .taskhero_setup.json"
}

# Help function
function Show-Help {
    Write-Host ""
    Write-ColoredLine "TaskHero AI Setup Script" $Colors.Primary
    Write-Host ""
    Write-Host "USAGE:"
    Write-Host "  .\setup_windows_modern.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "OPTIONS:"
    Write-Host "  -Force    Force re-run all setup steps"
    Write-Host "  -Help     Show this help message"
    Write-Host ""
    Write-Host "DESCRIPTION:"
    Write-Host "  This script sets up TaskHero AI with all required dependencies,"
    Write-Host "  creates a virtual environment, and configures the application."
    Write-Host ""
    Write-Host "EXAMPLES:"
    Write-Host "  .\setup_windows_modern.ps1           # Normal setup"
    Write-Host "  .\setup_windows_modern.ps1 -Force    # Force complete reinstall"
    Write-Host ""
    exit 0
}

if ($Help) {
    Show-Help
}

# Main setup process
Write-Host ""
Write-ColoredLine "===============================================================================" $Colors.Primary
Write-ColoredLine "                        TaskHero AI Setup for Windows                     " $Colors.Primary
Write-ColoredLine "===============================================================================" $Colors.Primary
Write-Host ""

if ($Force) {
    Write-Warning "Force mode enabled - all steps will be re-executed"
    if (Test-Path ".taskhero_setup.json") {
        Remove-Item ".taskhero_setup.json" -Force
        Write-Info "Cleared previous setup state"
    }
}

# Step 1: Check Prerequisites
Write-SectionHeader "Step 1: Checking Prerequisites" "🔍"
Show-Progress 1 7 "Verifying system requirements..."

$pythonAvailable = $false
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python found: $pythonVersion"
        $pythonAvailable = $true

        # Check Python version (should be 3.8+)
        $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
        if ($versionMatch) {
            $majorVersion = [int]$Matches[1]
            $minorVersion = [int]$Matches[2]
            if ($majorVersion -ge 3 -and $minorVersion -ge 8) { # Batch script checks for 3.11.6, but 3.8+ is more general
                Write-Success "Python version is compatible - 3.8 or higher"
            } else {
                Write-Warning "Python version $majorVersion.$minorVersion may be too old. This application was tested with Python 3.11.6."
                $continue = Get-UserInput "Do you want to continue anyway? (Y/N):" "yn" "N"
                if ($continue.ToUpper() -ne "Y") {
                    exit 1
                }
            }
        }
    } else {
        Write-Warning "Python not found in PATH"
        Write-Info "Setup will use basic tracking without Python-based features."
        Write-Info "Please install Python 3.8+ from https://python.org"
        $continue = Get-UserInput "Do you want to continue with basic setup? (Y/N):" "yn" "N"
        if ($continue.ToUpper() -ne "Y") {
            exit 1
        }
    }
} catch {
    Write-Error "Failed to check Python: $_"
    Write-Info "Please install Python 3.8+ from https://python.org"
    $continue = Get-UserInput "Do you want to continue with basic setup? (Y/N):" "yn" "N"
    if ($continue.ToUpper() -ne "Y") {
        exit 1
    }
}

# Check pip
if ($pythonAvailable) {
    try {
        $pipVersion = & python -m pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Pip found: $pipVersion"
        } else {
            Write-Error "Pip not available"
            Write-Info "Please ensure pip is installed with Python"
            Read-Host "Press Enter to exit"
            exit 1
        }
    } catch {
        Write-Error "Failed to check pip: $_"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check Git (optional but recommended)
try {
    $gitVersion = & git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Git found: $gitVersion"
    } else {
        Write-Warning "Git not found - some features may be limited"
    }
} catch {
    Write-Warning "Git not available - some features may be limited"
}

Write-Success "Prerequisites check completed"

# Step 2: Create Virtual Environment
Write-SectionHeader "Step 2: Setting up Virtual Environment" "🐍"
Show-Progress 2 7 "Creating Python virtual environment..."

if (-not $pythonAvailable) {
    Write-Error "Cannot create virtual environment without Python. Please install Python first and re-run this script."
    Read-Host "Press Enter to exit"
    exit 1
}

if ($Force -or -not (Test-SetupCompleted "venv_created")) {
    $venvNeedsCreation = $true
    if (Test-Path "venv") {
        Write-Info "Virtual environment directory exists. Checking if it's valid..."
        if (Test-Path "venv\Scripts\python.exe") {
            try {
                # Test if the virtual environment is valid by running a simple command
                & "venv\Scripts\python.exe" -c "import sys; print('Virtual environment is valid')" 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Valid virtual environment found. Skipping creation."
                    Set-SetupCompleted "venv_created" | Out-Null
                    $venvNeedsCreation = $false
                } else {
                    Write-Warning "Virtual environment directory exists but is invalid. Recreating..."
                    Remove-Item "venv" -Recurse -Force
                }
            } catch {
                Write-Warning "Virtual environment directory exists but is invalid. Recreating..."
                Remove-Item "venv" -Recurse -Force
            }
        } else {
            Write-Warning "Virtual environment directory exists but Python executable not found. Recreating..."
            Remove-Item "venv" -Recurse -Force
        }
    }

    if ($venvNeedsCreation) {
        Write-Info "Creating new virtual environment..."
        & python -m venv venv

        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment"
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Success "Virtual environment created successfully"
        Set-SetupCompleted "venv_created" | Out-Null
    }
} else {
    Write-Success "Virtual environment already exists - skipping"
}

# Step 3: Activate Virtual Environment (for current session)
Write-SectionHeader "Step 3: Activating Virtual Environment" "⚡"
Show-Progress 3 7 "Activating virtual environment..."

$activateScript = Join-Path $PWD "venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Info "Activating virtual environment..."
    try {
        # Dot-source the script to run it in the current scope
        . $activateScript
        Write-Success "Virtual environment activated"

        # Verify activation by checking Python path
        $venvPython = & python -c "import sys; print(sys.executable)" 2>&1
        if ($venvPython -like "*venv*") {
            Write-Success "Virtual environment activation verified"
        } else {
            Write-Warning "Virtual environment may not be properly activated"
            Write-Info "Python path: $venvPython"
        }
    } catch {
        Write-Warning "Failed to activate virtual environment: $_"
        Write-Info "Continuing with setup..."
    }
} else {
    Write-Error "Virtual environment activation script not found"
    Write-Error "Virtual environment setup failed. Please run with -Force to recreate."
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 4: Install Dependencies
Write-SectionHeader "Step 4: Installing Dependencies" "📦"
Show-Progress 4 7 "Installing Python packages..."

$pythonExe = Join-Path $PWD "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Error "Virtual environment Python not found at: $pythonExe"
    Write-Error "Virtual environment setup failed. Please run with -Force to recreate."
    Read-Host "Press Enter to exit"
    exit 1
}

if ($Force -or -not (Test-SetupCompleted "pip_upgraded")) {
    Write-Info "Upgrading pip..."
    try {
        & $pythonExe -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Pip upgrade failed, but continuing with installation."
        } else {
            Write-Success "Pip upgraded successfully"
            Set-SetupCompleted "pip_upgraded" | Out-Null
        }
    } catch {
        Write-Warning "Pip upgrade encountered an error: $_"
    }
} else {
    Write-Success "Pip already upgraded - skipping"
}

if ($Force -or -not (Test-SetupCompleted "dependencies_installed")) {
    Write-Info "Installing Python dependencies from requirements.txt..."
    Write-Info "This may take several minutes depending on your internet connection..."

    if (-not (Test-Path "requirements.txt")) {
        Write-Error "requirements.txt not found in current directory"
        Write-Error "Please ensure you are running this script from the TaskHero AI root directory"
        Read-Host "Press Enter to exit"
        exit 1
    }

    try {
        # Install with verbose output and no cache to avoid issues
        & $pythonExe -m pip install -r requirements.txt --no-cache-dir --verbose

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencies installed successfully"

            # Verify key dependencies
            Write-Info "Verifying key dependencies..."
            $keyDeps = @("colorama", "requests", "rich", "python-dotenv")
            $allGood = $true

            foreach ($dep in $keyDeps) {
                $testCmd = if ($dep -eq "python-dotenv") { "dotenv" } else { $dep }
                $importCmd = "import $testCmd; print(`"$testCmd imported successfully`")"
                $testResult = & $pythonExe -c $importCmd 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "✓ $dep"
                } else {
                    Write-Error "✗ $dep - $testResult"
                    $allGood = $false
                }
            }

            if ($allGood) {
                Write-Success "All key dependencies verified successfully"
                Set-SetupCompleted "dependencies_installed" | Out-Null
            } else {
                Write-Error "Some dependencies failed verification"
                Write-Info "Please check the error messages above and try running with -Force"
                Read-Host "Press Enter to exit"
                exit 1
            }
        } else {
            Write-Error "Failed to install dependencies (exit code: $LASTEXITCODE)"
            Write-Info "Please check your internet connection and try again"
            Write-Info "You can also try running: $pythonExe -m pip install -r requirements.txt"
            Read-Host "Press Enter to exit"
            exit 1
        }
    } catch {
        Write-Error "Error during dependency installation: $_"
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Success "Dependencies already installed - skipping"
}

# Step 5: Check for Ollama
Write-SectionHeader "Step 5: Checking for Ollama" "🦙"
Show-Progress 5 7 "Checking Ollama installation..."

$skipOllamaCheck = $false
if (Test-Path ".env") {
    Write-Info "Checking existing .env configuration..."
    $envContent = Get-Content ".env" | Out-String
    if ($envContent -match "OLLAMA_HOST=") {
        Write-Info "Custom OLLAMA_HOST found in .env file."
        $skipOllamaCheck = $true
    }
    if ($envContent -match "AI_.*_PROVIDER=" -and $envContent -notmatch "AI_.*_PROVIDER=ollama") {
        Write-Info "Non-Ollama providers configured in .env file."
        $skipOllamaCheck = $true
    }
}

if (-not $skipOllamaCheck) {
    Write-Info "Checking for Ollama installation..."
    $ollamaInstalled = $false
    $ollamaRunning = $false

    # Check if Ollama is installed
    try {
        $ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
        if ($ollamaPath) {
            Write-Success "Ollama found at: $($ollamaPath.Source)"
            $ollamaInstalled = $true

            # Check if Ollama is running
            try {
                $ollamaStatus = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method Get -ErrorAction SilentlyContinue
                if ($ollamaStatus) {
                    Write-Success "Ollama is running (version: $($ollamaStatus.version))"
                    $ollamaRunning = $true
                }
            } catch {
                Write-Warning "Ollama is installed but not running"
            }
        }
    } catch {
        Write-Warning "Ollama not found in PATH"
    }

    if (-not $ollamaInstalled) {
        Write-Info "Ollama is not installed. TaskHero AI can use Ollama for local AI processing."
        $installOllama = Get-UserInput "Would you like to install Ollama now? (Y/N):" "yn" "Y"

        if ($installOllama.ToUpper() -eq "Y") {
            Write-Info "Opening Ollama installation page..."
            Start-Process "https://ollama.com/download"

            Write-Info "Please follow the installation instructions on the website."
            Write-Info "After installation, please restart this setup script."
            Read-Host "Press Enter to exit"
            exit 0
        } else {
            Write-Info "Skipping Ollama installation."
            Write-Info "You can install it later from https://ollama.com/download"
        }
    } elseif (-not $ollamaRunning) {
        Write-Info "Ollama is installed but not running."
        $startOllama = Get-UserInput "Would you like to start Ollama now? (Y/N):" "yn" "Y"

        if ($startOllama.ToUpper() -eq "Y") {
            Write-Info "Starting Ollama..."
            Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden

            # Wait for Ollama to start
            Write-Info "Waiting for Ollama to start (this may take a moment)..."
            $ollamaStarted = $false
            $retryCount = 0
            $maxRetries = 10

            while (-not $ollamaStarted -and $retryCount -lt $maxRetries) {
                try {
                    $ollamaStatus = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method Get -ErrorAction SilentlyContinue
                    if ($ollamaStatus) {
                        Write-Success "Ollama started successfully (version: $($ollamaStatus.version))"
                        $ollamaStarted = $true
                    }
                } catch {
                    Write-Info "Waiting for Ollama to start... ($($retryCount + 1)/$maxRetries)"
                    Start-Sleep -Seconds 2
                    $retryCount++
                }
            }

            if (-not $ollamaStarted) {
                Write-Warning "Failed to start Ollama automatically."
                Write-Info "Please start Ollama manually and then continue with setup."
            }
        } else {
            Write-Info "Skipping Ollama startup."
            Write-Info "You can start it manually later."
        }
    }

    # Check for models if Ollama is running
    if ($ollamaRunning) {
        Write-Info "Checking for required Ollama models..."
        try {
            $ollamaModels = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -ErrorAction SilentlyContinue

            $requiredModels = @("llama3", "llama3:8b", "llama2", "mistral")
            $installedModels = $ollamaModels.models | ForEach-Object { $_.name }

            $missingModels = $requiredModels | Where-Object { $_ -notin $installedModels }

            if ($missingModels.Count -gt 0) {
                Write-Info "Some recommended models are not installed: $($missingModels -join ', ')"
                $installModels = Get-UserInput "Would you like to install the missing models now? (Y/N):" "yn" "Y"

                if ($installModels.ToUpper() -eq "Y") {
                    foreach ($model in $missingModels) {
                        Write-Info "Pulling $model... (this may take several minutes)"
                        Start-Process "ollama" -ArgumentList "pull $model" -NoNewWindow -Wait
                        Write-Success "Model $model installed successfully"
                    }
                } else {
                    Write-Info "Skipping model installation."
                    Write-Info "You can install them later using 'ollama pull [model-name]'"
                }
            } else {
                Write-Success "All recommended models are already installed"
            }
        } catch {
            Write-Warning "Failed to check Ollama models: $_"
        }
    }
}

# Step 6: Configure Application
Write-SectionHeader "Step 6: Configuring Application" "⚙️"
Show-Progress 6 7 "Setting up configuration..."

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Info "Creating default .env file..."

    # Create basic .env file with default settings
    $defaultEnv = @"
# TaskHero AI Configuration
# Created by setup script on $(Get-Date)

# AI Provider Configuration
AI_CHAT_PROVIDER=ollama
AI_CHAT_MODEL=llama3
AI_VISION_PROVIDER=ollama
AI_VISION_MODEL=llama3

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434

# Application Settings
APP_DEBUG=false
APP_LOG_LEVEL=INFO
APP_DATA_DIR=./data
"@

    $defaultEnv | Out-File -FilePath ".env" -Encoding UTF8
    Write-Success "Created default .env configuration"
} else {
    Write-Info ".env file already exists - checking for required settings..."

    $envContent = Get-Content ".env" | Out-String
    $missingSettings = @()

    # Check for essential settings
    $essentialSettings = @(
        "AI_CHAT_PROVIDER",
        "AI_CHAT_MODEL",
        "AI_VISION_PROVIDER",
        "AI_VISION_MODEL",
        "APP_DATA_DIR"
    )

    foreach ($setting in $essentialSettings) {
        if ($envContent -notmatch "$setting=") {
            $missingSettings += $setting
        }
    }

    if ($missingSettings.Count -gt 0) {
        $missingList = $missingSettings -join ', '
        Write-Warning "Some essential settings are missing from .env file: $missingList"
        $updateEnv = Get-UserInput "Would you like to add these settings with default values? (Y/N):" "yn" "Y"

        if ($updateEnv.ToUpper() -eq "Y") {
            $updatedEnv = $envContent.TrimEnd()
            $updatedEnv += "`n`n# Added by setup script on $(Get-Date)`n"

            foreach ($setting in $missingSettings) {
                switch ($setting) {
                    "AI_CHAT_PROVIDER" { $updatedEnv += "AI_CHAT_PROVIDER=ollama`n" }
                    "AI_CHAT_MODEL" { $updatedEnv += "AI_CHAT_MODEL=llama3`n" }
                    "AI_VISION_PROVIDER" { $updatedEnv += "AI_VISION_PROVIDER=ollama`n" }
                    "AI_VISION_MODEL" { $updatedEnv += "AI_VISION_MODEL=llama3`n" }
                    "APP_DATA_DIR" { $updatedEnv += "APP_DATA_DIR=./data`n" }
                }
            }

            $updatedEnv | Out-File -FilePath ".env" -Encoding UTF8
            Write-Success "Updated .env file with missing settings"
        } else {
            Write-Info "Skipping .env update. You may need to add these settings manually."
        }
    } else {
        Write-Success "All essential settings found in .env file"
    }
}

# Create data directory if it doesn't exist
$dataDir = "./data"
if (-not (Test-Path $dataDir)) {
    Write-Info "Creating data directory..."
    New-Item -Path $dataDir -ItemType Directory | Out-Null
    Write-Success "Created data directory"
} else {
    Write-Success "Data directory already exists"
}

# Step 7: Finalize Setup
Write-SectionHeader "Step 7: Finalizing Setup" "🎉"
Show-Progress 7 7 "Completing installation..."

# Create a simple test script to verify everything works
$testScriptPath = Join-Path $PWD "test_setup.py"
if (-not (Test-Path $testScriptPath) -or $Force) {
    Write-Info "Creating test script..."

    $testScript = @"
#!/usr/bin/env python
# TaskHero AI Setup Test Script
# Created by setup script on $(Get-Date)

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from dotenv import load_dotenv

console = Console()

def main():
    console.print(Panel.fit("TaskHero AI Setup Test", style="cyan"))
    console.print("")

    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"Python version: [green]{py_version}[/green]")

    # Check environment
    load_dotenv()
    env_vars = {
        "AI_CHAT_PROVIDER": os.getenv("AI_CHAT_PROVIDER", "Not set"),
        "AI_CHAT_MODEL": os.getenv("AI_CHAT_MODEL", "Not set"),
        "AI_VISION_PROVIDER": os.getenv("AI_VISION_PROVIDER", "Not set"),
        "AI_VISION_MODEL": os.getenv("AI_VISION_MODEL", "Not set"),
        "OLLAMA_HOST": os.getenv("OLLAMA_HOST", "Not set"),
        "APP_DATA_DIR": os.getenv("APP_DATA_DIR", "Not set"),
    }

    console.print("\nEnvironment Configuration:")
    for key, value in env_vars.items():
        color = "green" if value != "Not set" else "red"
        console.print(f"  {key}: [{color}]{value}[/{color}]")

    # Check data directory
    data_dir = os.getenv("APP_DATA_DIR", "./data")
    if os.path.exists(data_dir):
        console.print(f"\nData directory: [green]{os.path.abspath(data_dir)}[/green]")
    else:
        console.print(f"\nData directory: [red]Not found: {os.path.abspath(data_dir)}[/red]")

    # Check Ollama if configured
    if env_vars["AI_CHAT_PROVIDER"] == "ollama" or env_vars["AI_VISION_PROVIDER"] == "ollama":
        console.print("\nChecking Ollama connection...")
        try:
            import requests
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            response = requests.get(f"{ollama_host}/api/version", timeout=5)
            if response.status_code == 200:
                version = response.json().get("version", "unknown")
                console.print(f"  Ollama connection: [green]Success (version: {version})[/green]")
            else:
                console.print(f"  Ollama connection: [red]Failed (status code: {response.status_code})[/red]")
        except Exception as e:
            console.print(f"  Ollama connection: [red]Error: {str(e)}[/red]")
            console.print("  Make sure Ollama is running and accessible.")

    console.print("\n[cyan]Setup test completed![/cyan]")
    console.print("If you see any issues above, please check the documentation or run the setup script again.")

if __name__ == "__main__":
    main()
"@

    $testScript | Out-File -FilePath $testScriptPath -Encoding UTF8
    Write-Success "Created test script"
}

# Mark setup as completed
Set-SetupCompleted "setup_completed" | Out-Null

# Final message
Write-Host ""
Write-ColoredLine "===============================================================================" $Colors.Primary
Write-ColoredLine "                        TaskHero AI Setup Complete!                        " $Colors.Primary
Write-ColoredLine "===============================================================================" $Colors.Primary
Write-Host ""
Write-Success "TaskHero AI has been successfully set up on your system."
Write-Host ""
Write-Info "To test your installation, run:"
Write-Host "  .\venv\Scripts\python.exe test_setup.py"
Write-Host ""
Write-Info "To start using TaskHero AI, run:"
Write-Host "  .\venv\Scripts\python.exe -m taskhero"
Write-Host ""
Write-Info "For more information, see the documentation at:"
Write-Host "  https://github.com/yourusername/taskhero-ai"
Write-Host ""
Write-Host "Thank you for installing TaskHero AI!"
Write-Host ""
