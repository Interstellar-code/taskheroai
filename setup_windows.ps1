# TaskHero AI Setup Script - PowerShell Version
# Enhanced setup wizard with configuration management

param(
    [switch]$Force,
    [switch]$Help
)

# Color scheme for enhanced UI
$Colors = @{
    Primary   = "Cyan"
    Secondary = "Yellow"
    Success   = "Green"
    Warning   = "Yellow"
    Error     = "Red"
    Info      = "Blue"
    Text      = "White"
    Accent    = "Magenta"
}

function Write-ColoredLine {
    param(
        [string]$Text,
        [string]$Color = "White",
        [switch]$NoNewline
    )

    if ($NoNewline) {
        Write-Host $Text -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $Text -ForegroundColor $Color
    }
}

function Write-Header {
    param([string]$Title)

    Clear-Host
    Write-Host ""
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-ColoredLine "                    TaskHero AI - Enhanced Setup Wizard                    " $Colors.Primary
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-ColoredLine "  Welcome to the TaskHero AI Installation and Configuration Wizard!        " $Colors.Text
    Write-ColoredLine "  This script will guide you through the complete setup process.           " $Colors.Text
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-Host ""

    if ($Title) {
        Write-ColoredLine "Current Step: $Title" $Colors.Secondary
        Write-Host ""
    }
}

function Write-SectionHeader {
    param([string]$Title, [string]$Icon = "Package")

    Write-Host ""
    Write-ColoredLine "-------------------------------------------------------------------------------" $Colors.Secondary
    Write-ColoredLine " $Icon $Title" $Colors.Secondary
    Write-ColoredLine "-------------------------------------------------------------------------------" $Colors.Secondary
}

function Write-Success {
    param([string]$Message)
    Write-ColoredLine "[SUCCESS] $Message" $Colors.Success
}

function Write-Info {
    param([string]$Message)
    Write-ColoredLine "[INFO] $Message" $Colors.Info
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredLine "[WARNING] $Message" $Colors.Warning
}

function Write-Error {
    param([string]$Message)
    Write-ColoredLine "[ERROR] $Message" $Colors.Error
}

function Show-Progress {
    param(
        [int]$Step,
        [int]$Total,
        [string]$Description
    )

    $percentage = [math]::Round(($Step / $Total) * 100)
    $barLength = 50
    $filledLength = [math]::Round(($percentage / 100) * $barLength)

    $bar = "#" * $filledLength + "-" * ($barLength - $filledLength)

    Write-ColoredLine "Progress: " $Colors.Info -NoNewline
    Write-ColoredLine "[$bar] " $Colors.Primary -NoNewline
    Write-ColoredLine "$percentage% " $Colors.Success -NoNewline
    Write-ColoredLine "($Step/$Total)" $Colors.Text
    Write-ColoredLine "   $Description" $Colors.Text
}

function Get-UserChoice {
    param(
        [string]$Prompt,
        [string[]]$ValidChoices,
        [string]$DefaultChoice = ""
    )

    do {
        Write-Host ""
        Write-ColoredLine "$Prompt" $Colors.Accent
        if ($DefaultChoice) {
            Write-ColoredLine "   (Default: $DefaultChoice)" $Colors.Info
        }
        Write-ColoredLine "Your choice: " $Colors.Text -NoNewline

        $choice = Read-Host

        if ([string]::IsNullOrWhiteSpace($choice) -and $DefaultChoice) {
            $choice = $DefaultChoice
        }

        if ($ValidChoices -contains $choice) {
            return $choice
        } else {
            Write-Error "Invalid choice. Please select from: $($ValidChoices -join ', ')"
        }
    } while ($true)
}

function Get-UserInput {
    param(
        [string]$Prompt,
        [string]$DefaultValue = "",
        [switch]$Required
    )

    do {
        Write-Host ""
        Write-ColoredLine "$Prompt" $Colors.Accent
        if ($DefaultValue) {
            Write-ColoredLine "   (Default: $DefaultValue)" $Colors.Info
        }
        Write-ColoredLine "Enter value: " $Colors.Text -NoNewline

        $userInput = Read-Host

        if ([string]::IsNullOrWhiteSpace($userInput)) {
            if ($DefaultValue) {
                return $DefaultValue
            } elseif ($Required) {
                Write-Error "This field is required. Please enter a value."
                continue
            } else {
                return ""
            }
        }

        return $userInput
    } while ($true)
}

function Test-PythonInstallation {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python detected: $pythonVersion"
            return $true
        }
    } catch {
        Write-Warning "Python not found in PATH"
        return $false
    }
    return $false
}

function Test-VirtualEnvironment {
    # Check for the actual Python executable, not just the activation script
    if (Test-Path "venv\Scripts\python.exe") {
        return $true
    } else {
        return $false
    }
}

function Test-SetupCompleted {
    param([string]$StepName)

    if (-not (Test-Path ".taskhero_setup.json")) {
        return $false
    }

    try {
        $setupData = Get-Content ".taskhero_setup.json" | ConvertFrom-Json
        $stepData = $setupData.setup_completed.$StepName
        return $stepData.completed -eq $true
    } catch {
        return $false
    }
}

function Set-SetupCompleted {
    param([string]$StepName)

    try {
        $setupFile = ".taskhero_setup.json"

        if (Test-Path $setupFile) {
            $setupData = Get-Content $setupFile | ConvertFrom-Json
        } else {
            $setupData = @{
                setup_completed = @{}
            }
        }

        $setupData.setup_completed.$StepName = @{
            completed = $true
            timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.ffffff")
        }

        $setupData | ConvertTo-Json -Depth 10 | Out-File -FilePath $setupFile -Encoding UTF8
        return $true
    } catch {
        return $false
    }
}

# Install-Dependencies function removed - dependency installation is now inline in Step 4

function Show-ConfigurationWizard {
    Write-Header "Configuration Wizard"

    $config = @{}

    # Step 1: Repository Type
    Write-SectionHeader "Step 1/5: Repository Type" "Config"
    Write-Info "Will this be a central repository for all different code bases,"
    Write-Info "or will it reside within an existing codebase?"
    Write-Host ""
    Write-ColoredLine "1  Central repository (recommended for multiple projects)" $Colors.Text
    Write-ColoredLine "2  Singular repository (embedded in existing codebase)" $Colors.Text

    $repoChoice = Get-UserChoice "Please select repository type" @("1", "2")
    $config.RepositoryType = if ($repoChoice -eq "1") { "central" } else { "singular" }
    Write-Success "Selected: $(if ($repoChoice -eq '1') { 'Central repository' } else { 'Singular repository' })"

    # Step 2: Codebase Path
    Write-SectionHeader "Step 2/5: Codebase Path" "Folder"
    Write-Info "Please specify the path of the codebase that TaskHero will index."
    Write-Info "Current directory: $PWD"
    Write-Host ""
    Write-ColoredLine "Examples:" $Colors.Info
    Write-ColoredLine "  C:\Projects\MyProject" $Colors.Text
    Write-ColoredLine "  .\MyProject (relative path)" $Colors.Text
    Write-ColoredLine "  $PWD (current directory)" $Colors.Text

    $codebasePath = Get-UserInput "Enter the codebase path" $PWD.Path -Required

    if (-not (Test-Path $codebasePath)) {
        Write-Warning "Path does not exist: $codebasePath"
        $continue = Get-UserChoice "Continue anyway?" @("Y", "N") "N"
        if ($continue -eq "N") {
            return Show-ConfigurationWizard
        }
    }

    $config.CodebasePath = $codebasePath
    Write-Success "Codebase path set to: $codebasePath"

    # Step 3: Task Files Storage
    Write-SectionHeader "Step 3/5: Task Files Storage Location" "Storage"
    Write-Info "Where would you like to store project task files?"
    Write-Host ""
    Write-ColoredLine "1  Present folder ($PWD)" $Colors.Text
    Write-ColoredLine "2  TaskHero tasks folder (/theherotasks) [RECOMMENDED]" $Colors.Text
    Write-ColoredLine "3  Custom path (you will specify)" $Colors.Text

    $storageChoice = Get-UserChoice "Please select storage location" @("1", "2", "3") "2"

    switch ($storageChoice) {
        "1" {
            $config.TaskStorage = $PWD.Path
            Write-Success "Selected: Present folder"
        }
        "2" {
            $config.TaskStorage = Join-Path $PWD.Path "theherotasks"
            if (-not (Test-Path $config.TaskStorage)) {
                Write-Info "Creating TaskHero tasks directory: $($config.TaskStorage)"
                New-Item -ItemType Directory -Path $config.TaskStorage -Force | Out-Null

                # Create task status subdirectories
                $statusDirs = @("todo", "inprogress", "testing", "devdone", "done", "backlog", "archive")
                foreach ($dir in $statusDirs) {
                    $statusPath = Join-Path $config.TaskStorage $dir
                    New-Item -ItemType Directory -Path $statusPath -Force | Out-Null
                }
                Write-Success "Created task status subdirectories"
            }
            Write-Success "Selected: TaskHero tasks folder (/theherotasks)"
        }
        "3" {
            $customPath = Get-UserInput "Enter custom path for task files" -Required
            $config.TaskStorage = $customPath
            if (-not (Test-Path $config.TaskStorage)) {
                Write-Info "Creating directory: $config.TaskStorage"
                New-Item -ItemType Directory -Path $config.TaskStorage -Force | Out-Null

                # Create task status subdirectories for custom path too
                $statusDirs = @("todo", "inprogress", "testing", "devdone", "done", "backlog", "archive")
                foreach ($dir in $statusDirs) {
                    $statusPath = Join-Path $config.TaskStorage $dir
                    New-Item -ItemType Directory -Path $statusPath -Force | Out-Null
                }
                Write-Success "Created task status subdirectories"
            }
            Write-Success "Selected: Custom path"
        }
    }

    # Step 4: API and MCP Functions
    Write-SectionHeader "Step 4/5: API and MCP Functions" "API"
    Write-Info "Will TaskHero API and MCP functions be used?"
    Write-Info "This enables advanced AI features and integrations."
    Write-Host ""
    Write-ColoredLine "Y  Yes, enable API and MCP functions" $Colors.Text
    Write-ColoredLine "N  No, use basic functionality only" $Colors.Text

    $apiEnabled = Get-UserChoice "Enable API and MCP functions?" @("Y", "N")
    $config.ApiEnabled = ($apiEnabled -eq "Y")

    if ($apiEnabled -eq "Y") {
        Write-Success "API and MCP functions will be enabled"

        # Step 5: API Provider Configuration
        Write-SectionHeader "Step 5/5: API Provider Configuration" "Key"
        Write-Info "Configure your preferred AI providers and API keys."
        Write-Info "You can configure multiple providers or skip for now."
        Write-Host ""
        Write-ColoredLine "Available providers:" $Colors.Info
        Write-ColoredLine "  OpenAI (GPT models)" $Colors.Text
        Write-ColoredLine "  Anthropic (Claude models)" $Colors.Text
        Write-ColoredLine "  DeepSeek (DeepSeek models)" $Colors.Text
        Write-ColoredLine "  OpenRouter (Multiple models)" $Colors.Text
        Write-ColoredLine "  Ollama (Local models)" $Colors.Text

        Write-Host ""
        Write-Info "API configuration can be done manually by editing the .env file."
        Write-Info "Default configuration uses Ollama (local models)."

        $configureApis = Get-UserChoice "Would you like to configure API keys now?" @("Y", "N") "N"

        if ($configureApis -eq "Y") {
            Write-Info "Opening .env file for manual configuration..."
            Write-Info "Please edit the API keys and providers as needed."
            Write-Info "Save and close the file when done, then press any key to continue."

            if (Get-Command notepad -ErrorAction SilentlyContinue) {
                Start-Process notepad ".env" -Wait
            } else {
                Write-Info "Please manually edit the .env file with your preferred text editor."
                Read-Host "Press Enter when done editing"
            }
        } else {
            Write-Info "Skipping API configuration. You can configure later by editing .env file."
        }

        $config.ApiProvidersConfigured = $true
    } else {
        Write-Success "Using basic functionality only"
        $config.ApiProvidersConfigured = $false
    }

    return $config
}

# Main execution
if ($Help) {
    Write-Header "Help Information"
    Write-Info "TaskHero AI Setup Script - PowerShell Version"
    Write-Host ""
    Write-ColoredLine "Usage:" $Colors.Secondary
    Write-ColoredLine "  .\setup_windows_fixed.ps1           # Normal setup" $Colors.Text
    Write-ColoredLine "  .\setup_windows_fixed.ps1 -Force    # Force reinstall everything" $Colors.Text
    Write-ColoredLine "  .\setup_windows_fixed.ps1 -Help     # Show this help" $Colors.Text
    Write-Host ""
    exit 0
}

# Start main setup process
Write-Header

if ($Force) {
    Write-Info "Force setup mode enabled - all steps will be executed."
} else {
    Write-Info "This wizard will install packages and configure your TaskHero AI setup."
    Write-Info "Previously completed steps will be automatically skipped."
}

Write-Host ""

# Step 1: Check Python
Write-SectionHeader "Step 1: Python Installation Check" "Python"
Show-Progress 1 7 "Checking Python installation..."

if (-not (Test-PythonInstallation)) {
    Write-Error "Python is not installed or not in PATH."
    Write-Info "Please install Python 3.8+ from https://python.org"
    Write-Info "Make sure to check 'Add Python to PATH' during installation."
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Virtual Environment
Write-SectionHeader "Step 2: Virtual Environment Setup" "VEnv"
Show-Progress 2 7 "Setting up virtual environment..."

# Always check if virtual environment actually exists in current directory
$venvExists = Test-VirtualEnvironment
$setupCompleted = Test-SetupCompleted "venv_created"

# Debug information for troubleshooting
Write-Info "Virtual environment exists in current directory: $venvExists"
Write-Info "Setup completion status: $setupCompleted"
Write-Info "Current directory: $PWD"

if ($Force -or -not $venvExists) {
    if (-not $venvExists) {
        Write-Info "Creating virtual environment..."
        & python -m venv venv

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Virtual environment created successfully"
            Set-SetupCompleted "venv_created" | Out-Null
        } else {
            Write-Error "Failed to create virtual environment"
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Success "Virtual environment already exists"
        Set-SetupCompleted "venv_created" | Out-Null
    }
} else {
    if ($setupCompleted -and $venvExists) {
        Write-Success "Virtual environment setup already completed - skipping"
    } else {
        # Setup was marked complete but venv doesn't exist - recreate it
        Write-Warning "Virtual environment marked as complete but not found in current directory"
        Write-Info "This can happen when running setup in different repository directories"
        Write-Info "Recreating virtual environment for this repository..."
        & python -m venv venv

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Virtual environment created successfully"
            Set-SetupCompleted "venv_created" | Out-Null
        } else {
            Write-Error "Failed to create virtual environment"
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
}

# Step 3: Activate Virtual Environment
Write-SectionHeader "Step 3: Activating Virtual Environment" "Activate"
Show-Progress 3 7 "Activating virtual environment..."

# Check if virtual environment exists
$venvPython = "venv\Scripts\python.exe"
Write-Info "Checking for virtual environment Python at: $venvPython"

if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment Python not found at: $venvPython"
    Write-Info "This indicates the virtual environment was not created properly"
    Write-Info "Please run the script with -Force to recreate the virtual environment"
    Read-Host "Press Enter to exit"
    exit 1
} else {
    Write-Success "Virtual environment Python found"
}

# Set environment variables to use the virtual environment
$env:VIRTUAL_ENV = Join-Path $PWD "venv"
$env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"

# Verify activation by checking Python path
try {
    $pythonPath = & python -c "import sys; print(sys.executable)" 2>&1
    if ($pythonPath -like "*venv*") {
        Write-Success "Virtual environment activated successfully"
        Write-Info "Using Python: $pythonPath"
    } else {
        Write-Warning "Virtual environment may not be properly activated"
        Write-Info "Python path: $pythonPath"
    }
} catch {
    Write-Error "Failed to verify virtual environment activation: $_"
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 4: Install Dependencies
Write-SectionHeader "Step 4: Installing Dependencies" "Install"
Show-Progress 4 7 "Installing Python packages..."

if ($Force -or -not (Test-SetupCompleted "dependencies_installed")) {
    Write-Info "Installing Python dependencies..."

    # Use the virtual environment Python directly
    $pythonExe = Join-Path $PWD "venv\Scripts\python.exe"
    Write-Info "Using Python: $pythonExe"

    if (-not (Test-Path $pythonExe)) {
        Write-Error "Virtual environment Python not found at: $pythonExe"
        Write-Error "Virtual environment setup failed. Please run with -Force to recreate."
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Verify we have requirements.txt
    if (-not (Test-Path "requirements.txt")) {
        Write-Error "requirements.txt not found in current directory"
        Write-Error "Please ensure you're running this script from the TaskHero AI root directory"
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Info "Upgrading pip..."
    try {
        & $pythonExe -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Pip upgrade failed, but continuing..."
        } else {
            Write-Success "Pip upgraded successfully"
        }
    } catch {
        Write-Warning "Pip upgrade encountered an error: $_"
    }

    Write-Info "Installing dependencies from requirements.txt..."
    Write-Info "This may take several minutes depending on your internet connection..."

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
                $testResult = & $pythonExe -c "import $testCmd; print('$dep' + ': OK')" 2>&1
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

    # Still verify they're actually there
    $pythonExe = Join-Path $PWD "venv\Scripts\python.exe"
    if (Test-Path $pythonExe) {
        $coloramaTest = & $pythonExe -c "import colorama; print('verified')" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Dependencies marked as installed but verification failed"
            Write-Info "Re-installing dependencies..."
            & $pythonExe -m pip install -r requirements.txt --no-cache-dir
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Dependencies re-installed successfully"
            } else {
                Write-Error "Failed to re-install dependencies"
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
    }
}

# Step 5: Environment Configuration
Write-SectionHeader "Step 5: Environment Configuration" "Config"
Show-Progress 5 7 "Setting up environment variables..."

if ($Force -or -not (Test-SetupCompleted "env_file_created")) {
    if (-not (Test-Path ".env")) {
        Write-Info "Creating .env file with default settings..."

        $envContent = @"
# TaskHero AI Configuration
# Generated by PowerShell setup script

# AI Models Configuration
CHAT_MODEL=llama2
EMBEDDING_MODEL=all-minilm:33m
DESCRIPTION_MODEL=llama2
AI_AGENT_BUDDY_MODEL=llama3.2

# Model Parameters
CHAT_MODEL_TEMPERATURE=0.7
DESCRIPTION_MODEL_TEMPERATURE=0.3
AI_AGENT_BUDDY_MODEL_TEMPERATURE=0.7
INTENT_DETECTION_TEMPERATURE=0.1

# Model Max Tokens
CHAT_MODEL_MAX_TOKENS=4096
DESCRIPTION_MODEL_MAX_TOKENS=4096
AI_AGENT_BUDDY_MODEL_MAX_TOKENS=4096
INTENT_DETECTION_MAX_TOKENS=4096

# Performance Settings
PERFORMANCE_MODE=MEDIUM
MAX_THREADS=16
EMBEDDING_CACHE_SIZE=1000
EMBEDDING_SIMILARITY_THRESHOLD=0.05

# UI Settings
ENABLE_MARKDOWN_RENDERING=TRUE
SHOW_THINKING_BLOCKS=FALSE
ENABLE_STREAMING_MODE=FALSE
CHAT_LOGS=FALSE

# HTTP API Server Settings
HTTP_ALLOW_ALL_ORIGINS=FALSE
MCP_API_URL=http://localhost:8000
MCP_HTTP_PORT=8000
"@

        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "Environment file created successfully"
        Set-SetupCompleted "env_file_created" | Out-Null
    } else {
        Write-Success "Environment file already exists"
        Set-SetupCompleted "env_file_created" | Out-Null
    }
} else {
    Write-Success "Environment configuration already completed - skipping"
}

# Step 6: Configuration Wizard
Write-SectionHeader "Step 6: Interactive Configuration Wizard" "Wizard"
Show-Progress 6 7 "Running configuration wizard..."

if ($Force -or -not (Test-SetupCompleted "configuration_completed")) {
    $config = Show-ConfigurationWizard

    # Save configuration to both setup file and app_settings.json
    try {
        # Save to .taskhero_setup.json for setup tracking
        $setupFile = ".taskhero_setup.json"
        if (Test-Path $setupFile) {
            $setupData = Get-Content $setupFile | ConvertFrom-Json
        } else {
            $setupData = @{ setup_completed = @{}; configuration = @{} }
        }

        if (-not $setupData.configuration) {
            $setupData | Add-Member -NotePropertyName "configuration" -NotePropertyValue @{} -Force
        }

        foreach ($key in $config.Keys) {
            $setupData.configuration.$key = @{
                value = $config[$key]
                timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.ffffff")
            }
        }

        $setupData | ConvertTo-Json -Depth 10 | Out-File -FilePath $setupFile -Encoding UTF8

        # Save to app_settings.json for application use
        $appSettingsFile = "app_settings.json"
        if (Test-Path $appSettingsFile) {
            $appSettings = Get-Content $appSettingsFile | ConvertFrom-Json
        } else {
            $appSettings = @{}
        }

        # Map configuration keys to app settings
        if ($config.RepositoryType) { $appSettings.repository_type = $config.RepositoryType }
        if ($config.CodebasePath) { $appSettings.codebase_path = $config.CodebasePath }
        if ($config.TaskStorage) { $appSettings.task_storage_path = $config.TaskStorage }
        if ($config.ApiEnabled) { $appSettings.api_usage_enabled = $config.ApiEnabled }
        if ($config.ApiProvidersConfigured) { $appSettings.api_providers_configured = $config.ApiProvidersConfigured }

        $appSettings | ConvertTo-Json -Depth 10 | Out-File -FilePath $appSettingsFile -Encoding UTF8
        Write-Success "Configuration saved to both .taskhero_setup.json and app_settings.json"
    } catch {
        Write-Warning "Failed to save configuration: $_"
    }

    Set-SetupCompleted "configuration_completed" | Out-Null
    Write-Success "Configuration saved to .taskhero_setup.json"
} else {
    Write-Success "Configuration wizard already completed - skipping"
}

# Step 7: Completion
Write-SectionHeader "Step 7: Setup Complete!" "Complete"
Show-Progress 7 7 "Finalizing setup..."

Write-Host ""
Write-ColoredLine "===============================================================================" $Colors.Success
Write-ColoredLine "                        TaskHero AI Setup Complete!                       " $Colors.Success
Write-ColoredLine "===============================================================================" $Colors.Success
Write-Host ""
Write-Success "Installation and configuration completed successfully!"
Write-Host ""
Write-ColoredLine "To start the application, run:" $Colors.Info
Write-ColoredLine "   venv\Scripts\Activate.ps1" $Colors.Text
Write-ColoredLine "   python app.py" $Colors.Text
Write-Host ""
Write-ColoredLine "Setup status has been saved to .taskhero_setup.json" $Colors.Info
Write-ColoredLine "To force re-run all steps, use: .\setup_windows_fixed.ps1 -Force" $Colors.Info
Write-ColoredLine "For more information, see the README.md file" $Colors.Info
Write-Host ""

# Auto-start TaskHero AI
Write-Host ""
Write-ColoredLine "===============================================================================" $Colors.Primary
Write-ColoredLine "                          Starting TaskHero AI...                        " $Colors.Primary
Write-ColoredLine "===============================================================================" $Colors.Primary
Write-Host ""

try {
    # Use the virtual environment Python to start the app
    $pythonExe = Join-Path $PWD "venv\Scripts\python.exe"
    Write-Info "Current directory: $PWD"
    Write-Info "Looking for Python at: $pythonExe"

    if (Test-Path $pythonExe) {
        Write-Success "Virtual environment Python found!"

        # Set environment variables to ensure virtual environment is used
        $env:VIRTUAL_ENV = Join-Path $PWD "venv"
        $env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"

        # Verify the Python path before starting
        $actualPython = & $pythonExe -c "import sys; print(sys.executable)" 2>&1
        Write-Info "Using Python: $actualPython"

        # Test if colorama is available
        $coloramaTest = & $pythonExe -c "import colorama; print('colorama available')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencies verified - colorama is available"
            Write-Info "Starting TaskHero AI with virtual environment Python..."
            & $pythonExe app.py
        } else {
            Write-Error "Dependencies not found in virtual environment!"
            Write-Info "Colorama test result: $coloramaTest"
            Write-Info "This suggests the virtual environment wasn't activated during dependency installation."
            Write-Info "Please run the setup script again with -Force flag."
            Read-Host "Press Enter to exit"
        }
    } else {
        Write-Error "Virtual environment Python not found at: $pythonExe"
        Write-Info "This suggests the virtual environment wasn't created properly."
        Write-Info "Please run the setup script again with -Force flag."
        Read-Host "Press Enter to exit"
    }
} catch {
    Write-Error "Failed to start TaskHero AI: $_"
    Read-Host "Press Enter to exit"
}

Write-Host ""
Write-ColoredLine "===============================================================================" $Colors.Accent
Write-ColoredLine "                     Thank you for using TaskHero AI!                     " $Colors.Accent
Write-ColoredLine "                        Setup completed successfully.                         " $Colors.Accent
Write-ColoredLine "===============================================================================" $Colors.Accent

Read-Host "Press Enter to exit"
