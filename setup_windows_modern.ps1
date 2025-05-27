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
                # Attempt to activate to check validity
                & "venv\Scripts\activate.ps1"
                Write-Success "Valid virtual environment found. Skipping creation."
                Set-SetupCompleted "venv_created" | Out-Null
                $venvNeedsCreation = $false # Mark as not needing creation
            } catch {
                Write-Warning "Virtual environment directory exists but activation failed. Recreating..."
                Remove-Item "venv" -Recurse -Force
            }
        } else {
            Write-Warning "Virtual environment directory exists but Python executable not found. Recreating..."
            Remove-Item "venv" -Recurse -Force
        }
    }

    if ($venvNeedsCreation) { # Only create if it doesn't exist or was removed/invalidated
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
} else { # This else corresponds to the initial 'if ($Force -or -not (Test-SetupCompleted "venv_created"))'
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

if ($skipOllamaCheck) {
    Write-Info "Ollama configuration found in .env file. Skipping Ollama installation check."
    Write-Info "Using existing configuration from .env file."
} else {
    try {
        & where.exe ollama 2>&1 | Out-Null # Use where.exe for cross-shell compatibility
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Ollama is installed."
        } else {
            Write-Warning "Ollama is not installed or not in PATH."
            Write-Info "You will need to install Ollama to use local models."
            Write-Info "Download from: https://ollama.com/download"
            $openOllama = Get-UserInput "Would you like to open the Ollama download page? (Y/N):" "yn" "N"
            if ($openOllama.ToUpper() -eq "Y") {
                Start-Process "https://ollama.com/download"
            }
        }
    } catch {
        Write-Warning "Failed to check Ollama: $_"
        Write-Info "Ollama is not installed or not in PATH."
        Write-Info "You will need to install Ollama to use local models."
        Write-Info "Download from: https://ollama.com/download"
        $openOllama = Get-UserInput "Would you like to open the Ollama download page? (Y/N):" "yn" "N"
        if ($openOllama.ToUpper() -eq "Y") {
            Start-Process "https://ollama.com/download"
        }
    }
}

# Step 6: Environment Configuration (.env file)
Write-SectionHeader "Step 6: Environment Configuration" "⚙️"
Show-Progress 6 7 "Setting up environment variables..."

if ($Force -or -not (Test-SetupCompleted "env_file_created")) {
    if (-not (Test-Path ".env")) {
        Write-Info "Creating .env file with default settings..."

        $envContent = @"
# Provider can be: ollama, google, openai, anthropic, groq, or openrouter
AI_CHAT_PROVIDER=ollama
AI_EMBEDDING_PROVIDER=ollama
AI_DESCRIPTION_PROVIDER=ollama
AI_AGENT_BUDDY_PROVIDER=ollama

# API Keys for each functionality (only needed if using that provider)
# The same key will be used for the selected provider in each category
AI_CHAT_API_KEY=None
AI_EMBEDDING_API_KEY=None
AI_DESCRIPTION_API_KEY=None
AI_AGENT_BUDDY_API_KEY=None

# Model names for each provider
# For ollama: llama2, codellama, mistral, etc. (embedding)
# For OpenAI: gpt-4, gpt-3.5-turbo, text-embedding-ada-002 (embedding)
# For OpenRouter: anthropic/claude-3-opus, openai/gpt-4-turbo, google/gemini-pro, etc.
# For Google: gemini-pro, gemini-pro-vision
# For Anthropic: claude-3-5-sonnet-latest, claude-3-opus-20240229, claude-3-haiku-20240307
# For Groq: llama3-8b-8192, llama3-70b-8192, mixtral-8x7b-32768
CHAT_MODEL=llama2
EMBEDDING_MODEL=all-minilm:33m
DESCRIPTION_MODEL=llama2
AI_AGENT_BUDDY_MODEL=llama3.2

# Model Tempratures
CHAT_MODEL_TEMPERATURE=0.7
DESCRIPTION_MODEL_TEMPERATURE=0.3
AI_AGENT_BUDDY_MODEL_TEMPERATURE=0.7
INTENT_DETECTION_TEMPERATURE=0.1

# Model Max Tokens
CHAT_MODEL_MAX_TOKENS=4096
DESCRIPTION_MODEL_MAX_TOKENS=4096
AI_AGENT_BUDDY_MODEL_MAX_TOKENS=4096
INTENT_DETECTION_MAX_TOKENS=4096

# Other Model Settings
CHAT_MODEL_TOP_P=0.95
CHAT_MODEL_TOP_K=40
DESCRIPTION_MODEL_TOP_P=0.95
DESCRIPTION_MODEL_TOP_K=40
INTENT_DETECTION_TOP_P=0.95
INTENT_DETECTION_TOP_K=40

# Optional: Site information for OpenRouter rankings
SITE_URL=http://localhost:3000
SITE_NAME=Local Development

# Performance settings (LOW, MEDIUM, MAX)
# LOW: Minimal resource usage, suitable for low-end systems
# MEDIUM: Balanced resource usage, suitable for most systems
# MAX: Maximum resource usage, suitable for high-end systems
PERFORMANCE_MODE=MEDIUM
# Maximum number of threads to use (will be calculated automatically if not set)
MAX_THREADS=16
# Cache size for embedding queries (higher values use more memory but improve performance)
EMBEDDING_CACHE_SIZE=1000
# Similarity threshold for embedding search (lower values return more results but may be less relevant)
EMBEDDING_SIMILARITY_THRESHOLD=0.05

# API Rate Limiting Settings
# Delay in milliseconds between embedding API calls to prevent rate limiting
# Recommended: 100ms for Google, 0ms for OpenAI/Ollama (set to 0 to disable)
EMBEDDING_API_DELAY_MS=100
# Delay in milliseconds between description generation API calls to prevent rate limiting
# Recommended: 100ms for Google, 0ms for OpenAI/Ollama (set to 0 to disable)
DESCRIPTION_API_DELAY_MS=100

# UI Settings
# Enable/disable markdown rendering (TRUE/FALSE)
ENABLE_MARKDOWN_RENDERING=TRUE
# Show thinking blocks in AI responses (TRUE/FALSE)
SHOW_THINKING_BLOCKS=FALSE
# Enable streaming mode for AI responses (TRUE/FALSE) # Tends to be slower for some reason # Broken for openrouter TODO: Fix this at some point !
ENABLE_STREAMING_MODE=FALSE
# Enable chat logging to save conversations (TRUE/FALSE)
CHAT_LOGS=FALSE
# Enable memory for AI conversations (TRUE/FALSE)
MEMORY_ENABLED=TRUE
# Maximum number of memory items to store
MAX_MEMORY_ITEMS=10
# Execute commands without confirmation (TRUE/FALSE)
# When FALSE, the user will be prompted to confirm before executing any command
# When TRUE, commands will execute automatically without confirmation
COMMANDS_YOLO=FALSE

# HTTP API Server Settings
# Allow connections from any IP address (TRUE/FALSE)
# When FALSE, the server only accepts connections from localhost (127.0.0.1)
# When TRUE, the server accepts connections from any IP address (0.0.0.0)
# WARNING: Setting this to TRUE may expose your API to the internet
HTTP_ALLOW_ALL_ORIGINS=FALSE

# MCP Server Settings
# URL of the HTTP API server
MCP_API_URL=http://localhost:8000
# Port to run the HTTP API server on
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

# Step 7: Interactive Configuration Wizard
Write-SectionHeader "Step 7: Interactive Configuration Wizard" "W"
Show-Progress 7 7 "Running configuration wizard..."

if ($Force -or -not (Test-SetupCompleted "configuration_completed")) {
    Write-Info "Starting interactive configuration wizard..."
    Write-Info "This will configure TaskHero AI for your specific needs."

    # Configuration Step 1: Repository Type
    Write-SectionHeader "Configuration 1/5: Repository Type"
    Write-Host "Will this be a central repository for all different code bases,"
    Write-Host "or will it reside within an existing codebase?"
    Write-Host ""
    Write-Host "1. Central repository (recommended for multiple projects)"
    Write-Host "2. Singular repository (embedded in existing codebase)"

    $repoType = ""
    if ($Force -or -not (Test-Path ".taskhero_setup.json" -and (Get-Content ".taskhero_setup.json" | Out-String) -match "repository_type")) {
        $repoChoice = Get-UserInput "Please select repository type (1 or 2):" "option" "2" -ValidOptions @("1", "2")
        if ($repoChoice -eq "1") {
            $repoType = "central"
            Write-Success "Selected: Central repository"
        } else {
            $repoType = "singular"
            Write-Success "Selected: Singular repository"
        }
        Save-AppConfig "repository_type" $repoType
    } else {
        Write-Info "Repository type already configured. Skipping..."
        $setupData = Get-Content ".taskhero_setup.json" | ConvertFrom-Json
        $repoType = $setupData.repository_type
    }

    # Configuration Step 2: Codebase Path
    Write-SectionHeader "Configuration 2/5: Codebase Path"
    Write-Host "Please specify the path of the codebase that TaskHero will index."
    Write-Host "Current directory: $PWD"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "- C:\Projects\MyProject"
    Write-Host "- .\MyProject (relative path)"
    Write-Host "- $PWD (current directory)"

    $codebasePath = ""
    if ($Force -or -not (Test-Path ".taskhero_setup.json" -and (Get-Content ".taskhero_setup.json" | Out-String) -match "codebase_path")) {
        $codebasePath = Get-UserInput "Enter the codebase path (default: $PWD):" "path" "$PWD"
        if (-not (Test-Path $codebasePath)) {
            Write-Warning "Path does not exist: $codebasePath"
            $continuePath = Get-UserInput "Continue anyway? (Y/N):" "yn" "N"
            if ($continuePath.ToUpper() -eq "N") {
                $codebasePath = Get-UserInput "Enter the codebase path (default: $PWD):" "path" "$PWD"
            }
        }
        Write-Success "Codebase path set to: $codebasePath"
        Save-AppConfig "codebase_path" $codebasePath
    } else {
        Write-Info "Codebase path already configured. Skipping..."
        $setupData = Get-Content ".taskhero_setup.json" | ConvertFrom-Json
        $codebasePath = $setupData.codebase_path
    }

    # Configuration Step 3: Task Files Storage
    Write-SectionHeader "Configuration 3/5: Task Files Storage Location"
    Write-Host "Where would you like to store project task files?"
    Write-Host ""
    Write-Host "1. Present folder ($PWD)"
    Write-Host "2. TaskHero tasks folder (/theherotasks) [RECOMMENDED]"
    Write-Host "3. Custom path (you will specify)"

    $taskStoragePath = ""
    if ($Force -or -not (Test-Path ".taskhero_setup.json" -and (Get-Content ".taskhero_setup.json" | Out-String) -match "task_storage_path")) {
        $storageChoice = Get-UserInput "Please select storage location (1, 2, or 3, default 2):" "option" "2" -ValidOptions @("1", "2", "3")
        if ($storageChoice -eq "1") {
            $taskStoragePath = $PWD.Path
            Write-Success "Selected: Present folder"
        } elseif ($storageChoice -eq "2") {
            $taskStoragePath = Join-Path $PWD.Path "theherotasks"
            Write-Success "Selected: TaskHero tasks folder (/theherotasks)"
        } else {
            $taskStoragePath = Get-UserInput "Enter custom path for task files:" "path" ""
            Write-Success "Selected: Custom path"
        }

        if (-not (Test-Path $taskStoragePath)) {
            Write-Info "Creating directory: $taskStoragePath"
            New-Item -ItemType Directory -Path $taskStoragePath -Force | Out-Null
        }
        # Create task status subdirectories
        $taskSubDirs = @("todo", "inprogress", "testing", "devdone", "done", "backlog", "archive")
        foreach ($subDir in $taskSubDirs) {
            $fullPath = Join-Path $taskStoragePath $subDir
            if (-not (Test-Path $fullPath)) {
                New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            }
        }
        Write-Success "Created task status subdirectories"
        Save-AppConfig "task_storage_path" $taskStoragePath
    } else {
        Write-Info "Task storage location already configured. Skipping..."
        $setupData = Get-Content ".taskhero_setup.json" | ConvertFrom-Json
        $taskStoragePath = $setupData.task_storage_path
    }

    # Configuration Step 4: API and MCP Functions
    Write-SectionHeader "Configuration 4/5: API and MCP Functions"
    Write-Host "Will TaskHero API and MCP functions be used?"
    Write-Host "This enables advanced AI features and integrations."
    Write-Host ""
    Write-Host "Y - Yes, enable API and MCP functions"
    Write-Host "N - No, use basic functionality only"

    $apiEnabled = $false
    if ($Force -or -not (Test-Path ".taskhero_setup.json" -and (Get-Content ".taskhero_setup.json" | Out-String) -match "api_usage_enabled")) {
        $apiChoice = Get-UserInput "Enable API and MCP functions? (Y/N):" "yn" "Y"
        if ($apiChoice.ToUpper() -eq "Y") {
            Write-Success "API and MCP functions will be enabled"
            $apiEnabled = $true
            Save-AppConfig "api_usage_enabled" $true
        } else {
            Write-Success "Using basic functionality only"
            $apiEnabled = $false
            Save-AppConfig "api_usage_enabled" $false
        }
    } else {
        Write-Info "API usage preference already configured. Skipping..."
        $setupData = Get-Content ".taskhero_setup.json" | ConvertFrom-Json
        $apiEnabled = $setupData.api_usage_enabled
    }

    # Configuration Step 5: API Details (only if API is enabled)
    if ($apiEnabled) {
        Write-SectionHeader "Configuration 5/5: API Provider Configuration"
        Write-Host "Configure your preferred AI providers and API keys."
        Write-Host "You can configure multiple providers or skip for now."
        Write-Host ""
        Write-Host "Available providers:"
        Write-Host "- OpenAI (GPT models)"
        Write-Host "- Anthropic (Claude models)"
        Write-Host "- DeepSeek (DeepSeek models)"
        Write-Host "- OpenRouter (Multiple models)"
        Write-Host "- Ollama (Local models)"

        if ($Force -or -not (Test-Path ".taskhero_setup.json" -and (Get-Content ".taskhero_setup.json" | Out-String) -match "api_providers_configured")) {
            Write-Info "API configuration can be done manually by editing the .env file."
            Write-Info "Default configuration uses Ollama (local models)."
            $configureApis = Get-UserInput "Would you like to configure API keys now? (Y/N):" "yn" "N"

            if ($configureApis.ToUpper() -eq "Y") {
                Write-Info "Opening .env file for manual configuration..."
                Write-Info "Please edit the API keys and providers as needed."
                Write-Info "Save and close the file when done, then press Enter to continue."
                try {
                    Start-Process notepad.exe -ArgumentList ".env" -Wait
                } catch {
                    Write-Info "Please manually edit the .env file with your preferred text editor."
                    Read-Host "Press Enter to continue"
                }
            } else {
                Write-Info "Skipping API configuration. You can configure later by editing .env file."
            }
            Save-AppConfig "api_providers_configured" $true
        } else {
            Write-Info "API providers already configured. Skipping..."
        }
    }

    Write-SectionHeader "Configuration Complete!"
    Write-Success "TaskHero AI configuration has been completed successfully!"
    Write-Info "All settings have been saved and will be remembered for future runs."

    Set-SetupCompleted "configuration_completed" | Out-Null
} else {
    Write-Success "Configuration wizard already completed - skipping"
}

# Final Completion Message
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
if ($pythonAvailable) {
    Write-ColoredLine "Setup status has been saved to .taskhero_setup.json" $Colors.Info
} else {
    Write-ColoredLine "Setup status tracking is limited without Python" $Colors.Info
}
Write-ColoredLine "To force re-run all steps, use: .\setup_windows_modern.ps1 -Force" $Colors.Info
Write-ColoredLine "For more information, see the README.md file" $Colors.Info
Write-Host ""

# Auto-start TaskHero AI
if ($pythonAvailable) {
    Write-Host ""
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-ColoredLine "                          Starting TaskHero AI...                        " $Colors.Primary
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-Host ""

    if (Test-Path "venv\Scripts\python.exe") {
        Write-Info "Starting TaskHero AI with virtual environment Python..."

        # Test if dependencies are available before starting
        try {
            & "venv\Scripts\python.exe" -c "import colorama" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Dependencies verified - starting application..."
                & "venv\Scripts\python.exe" app.py
            } else {
                Write-Error "Dependencies not found in virtual environment!"
                Write-Info "Please run the setup script again with -Force flag."
                Read-Host "Press Enter to exit"
            }
        } catch {
            Write-Error "Failed to verify dependencies or start app: $_"
            Write-Info "Please run the setup script again with -Force flag."
            Read-Host "Press Enter to exit"
        }
    } else {
        Write-Error "Virtual environment Python not found!"
        Write-Info "Please run the setup script again with -Force flag."
        Read-Host "Press Enter to exit"
    }
} else {
    Write-Host ""
    Write-ColoredLine "===============================================================================" $Colors.Info
    Write-ColoredLine "   Please install Python and re-run this script to start TaskHero AI.   " $Colors.Info
    Write-ColoredLine "===============================================================================" $Colors.Info
    Read-Host "Press Enter to exit"
}

Read-Host "Press Enter to exit"
