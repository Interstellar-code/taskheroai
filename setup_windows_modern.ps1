# TaskHero AI Setup Script for Windows PowerShell
# This script sets up TaskHero AI with all dependencies and configuration

param(
    [switch]$Force,
    [switch]$Help,
    [switch]$Initial
)

# Set console encoding to UTF-8 to handle Unicode characters properly
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

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
    Write-Host "[+] $Message" -ForegroundColor $Colors.Success
}

function Write-Error {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor $Colors.Error
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor $Colors.Warning
}

function Write-Info {
    param([string]$Message)
    Write-Host "[i] $Message" -ForegroundColor $Colors.Info
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

# Function to remove environment folders and files for fresh installation
function Remove-EnvironmentFolders {
    Write-Host ""
    Write-ColoredLine "===============================================================================" $Colors.Warning
    Write-ColoredLine "                        INITIAL SETUP - CLEANUP WARNING                    " $Colors.Warning
    Write-ColoredLine "===============================================================================" $Colors.Warning
    Write-Host ""
    Write-Warning "The --Initial flag will DELETE the following files and folders:"
    Write-Host ""

    # Define items to be deleted
    $itemsToDelete = @(
        @{ Path = "venv"; Type = "Folder"; Description = "Virtual environment folder" },
        @{ Path = ".taskhero_setup.json"; Type = "File"; Description = "Setup tracking file" },
        @{ Path = ".env"; Type = "File"; Description = "Environment configuration file" },
        @{ Path = "app_settings.json"; Type = "File"; Description = "Application settings file" },
        @{ Path = ".index"; Type = "Folder"; Description = "Index cache folder" }
    )

    # Find all __pycache__ folders
    $pycacheFolders = Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue
    foreach ($folder in $pycacheFolders) {
        $itemsToDelete += @{ Path = $folder; Type = "Folder"; Description = "Python cache folder" }
    }

    # Find all .index folders (in case there are multiple)
    $indexFolders = Get-ChildItem -Path . -Recurse -Directory -Name ".index" -ErrorAction SilentlyContinue
    foreach ($folder in $indexFolders) {
        $itemsToDelete += @{ Path = $folder; Type = "Folder"; Description = "Index cache folder" }
    }

    # Display what will be deleted
    $existingItems = @()
    foreach ($item in $itemsToDelete) {
        if (Test-Path $item.Path) {
            $existingItems += $item
            $icon = if ($item.Type -eq "Folder") { "[DIR]" } else { "[FILE]" }
            Write-ColoredLine "  $icon $($item.Path) - $($item.Description)" $Colors.Error
        }
    }

    if ($existingItems.Count -eq 0) {
        Write-Host ""
        Write-Success "No environment files or folders found to delete."
        Write-Info "Proceeding with fresh installation..."
        return $true
    }

    Write-Host ""
    Write-ColoredLine "Total items to delete: $($existingItems.Count)" $Colors.Warning
    Write-Host ""
    Write-Warning "*** THIS ACTION CANNOT BE UNDONE! ***"
    Write-Warning "All your current environment configuration will be lost."
    Write-Host ""

    # Get user confirmation
    $confirmation = Get-UserInput "Are you sure you want to delete these items and start fresh? (y/N):" "yn" "N"

    if ($confirmation.ToUpper() -ne "Y") {
        Write-Host ""
        Write-Info "Operation cancelled by user."
        Write-Info "No files were deleted."
        return $false
    }

    # Proceed with deletion
    Write-Host ""
    Write-Info "Proceeding with cleanup..."
    Write-Host ""

    $deletedCount = 0
    $errorCount = 0

    foreach ($item in $existingItems) {
        try {
            if (Test-Path $item.Path) {
                if ($item.Type -eq "Folder") {
                    Remove-Item $item.Path -Recurse -Force -ErrorAction Stop
                    Write-Success "Deleted folder: $($item.Path)"
                } else {
                    Remove-Item $item.Path -Force -ErrorAction Stop
                    Write-Success "Deleted file: $($item.Path)"
                }
                $deletedCount++
            }
        } catch {
            Write-Error "Failed to delete $($item.Path): $($_.Exception.Message)"
            $errorCount++
        }
    }

    Write-Host ""
    if ($errorCount -eq 0) {
        Write-Success "Cleanup completed successfully!"
        Write-Success "Deleted $deletedCount items."
        Write-Info "Environment has been reset for fresh installation."
    } else {
        Write-Warning "Cleanup completed with $errorCount errors."
        Write-Info "Successfully deleted $deletedCount items."
        Write-Warning "Some items could not be deleted. Please check the errors above."

        $continueAnyway = Get-UserInput "Do you want to continue with setup anyway? (Y/N):" "yn" "Y"
        if ($continueAnyway.ToUpper() -ne "Y") {
            Write-Info "Setup cancelled."
            return $false
        }
    }

    Write-Host ""
    return $true
}

# Setup completion tracking
function Test-SetupCompleted {
    param([string]$Step)
    $setupFile = Join-Path $PSScriptRoot ".taskhero_setup.json"
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
    $setupFile = Join-Path $PSScriptRoot ".taskhero_setup.json"
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

# Function to get configuration value from .taskhero_setup.json
function Get-ConfigValue {
    param(
        [string]$Key
    )

    $setupFile = Join-Path $PSScriptRoot ".taskhero_setup.json"
    if (-not (Test-Path $setupFile)) {
        return $null
    }

    try {
        $setupData = Get-Content $setupFile | ConvertFrom-Json
        if ($setupData.PSObject.Properties.Name -contains $Key) {
            return $setupData.$Key
        }
        return $null
    } catch {
        Write-Warning "Failed to read configuration value for '$Key': $_"
        return $null
    }
}

# Function to add TaskHero AI folder to .gitignore
function Add-ToGitIgnore {
    param(
        [string]$CodebasePath,
        [string]$TaskHeroPath
    )

    try {
        # Resolve absolute paths
        $codebaseAbsolute = Resolve-Path $CodebasePath -ErrorAction SilentlyContinue
        $taskHeroAbsolute = Resolve-Path $TaskHeroPath -ErrorAction SilentlyContinue

        if (-not $codebaseAbsolute) {
            Write-Warning "Could not resolve codebase path: $CodebasePath"
            return $false
        }

        if (-not $taskHeroAbsolute) {
            Write-Warning "Could not resolve TaskHero AI path: $TaskHeroPath"
            return $false
        }

        # Find .gitignore file in codebase directory
        $gitIgnorePath = Join-Path $codebaseAbsolute.Path ".gitignore"

        # Calculate relative path from codebase to TaskHero AI folder
        $relativePath = ""
        try {
            # Try to get relative path
            $relativePath = [System.IO.Path]::GetRelativePath($codebaseAbsolute.Path, $taskHeroAbsolute.Path)
            # Normalize path separators for git (use forward slashes)
            $relativePath = $relativePath -replace '\\', '/'
        } catch {
            # Fallback: use folder name if paths are not related
            $relativePath = Split-Path $taskHeroAbsolute.Path -Leaf
        }

        # Ensure the path starts with / for absolute ignore or is relative
        if (-not $relativePath.StartsWith('/') -and -not $relativePath.StartsWith('./')) {
            if ($relativePath -eq (Split-Path $taskHeroAbsolute.Path -Leaf)) {
                # If it's just the folder name, make it relative
                $relativePath = "./$relativePath"
            }
        }

        Write-Info "Adding TaskHero AI folder to .gitignore..."
        Write-Info "Codebase path: $($codebaseAbsolute.Path)"
        Write-Info "TaskHero AI path: $($taskHeroAbsolute.Path)"
        Write-Info "Relative path to ignore: $relativePath"

        # Read existing .gitignore content or create empty array
        $gitIgnoreContent = @()
        if (Test-Path $gitIgnorePath) {
            $gitIgnoreContent = Get-Content $gitIgnorePath -ErrorAction SilentlyContinue
            if (-not $gitIgnoreContent) {
                $gitIgnoreContent = @()
            }
        }

        # Check if the path is already in .gitignore
        $pathExists = $false
        foreach ($line in $gitIgnoreContent) {
            $trimmedLine = $line.Trim()
            if ($trimmedLine -eq $relativePath -or
                $trimmedLine -eq "/$relativePath" -or
                $trimmedLine -eq $relativePath.TrimStart('./') -or
                $trimmedLine -eq "taskheroai" -or
                $trimmedLine -eq "/taskheroai" -or
                $trimmedLine -eq "./taskheroai") {
                $pathExists = $true
                break
            }
        }

        if ($pathExists) {
            Write-Success "TaskHero AI folder is already in .gitignore"
            return $true
        }

        # Add the path to .gitignore
        $newContent = $gitIgnoreContent + @("", "# TaskHero AI - Added by setup script", $relativePath)

        # Write to .gitignore file
        $newContent | Out-File -FilePath $gitIgnorePath -Encoding UTF8
        Write-Success "Added TaskHero AI folder to .gitignore: $relativePath"

        return $true
    } catch {
        Write-Warning "Failed to update .gitignore: $_"
        return $false
    }
}

# Function to set configuration value in .taskhero_setup.json
function Set-ConfigValue {
    param(
        [string]$Key,
        [string]$Value
    )

    $setupFile = Join-Path $PSScriptRoot ".taskhero_setup.json"

    try {
        # Load existing data or create new structure
        if (Test-Path $setupFile) {
            $setupData = Get-Content $setupFile | ConvertFrom-Json
        } else {
            $setupData = [PSCustomObject]@{
                setup_completed = [PSCustomObject]@{}
            }
        }

        # Add or update the key
        $setupData | Add-Member -MemberType NoteProperty -Name $Key -Value $Value -Force

        # Update timestamp
        if (-not $setupData.setup_completed) {
            $setupData.setup_completed = [PSCustomObject]@{}
        }
        $setupData.setup_completed | Add-Member -MemberType NoteProperty -Name "last_updated" -Value (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.ffffff") -Force

        # Save back to file
        $setupData | ConvertTo-Json -Depth 10 | Out-File -FilePath $setupFile -Encoding UTF8
        return $true
    } catch {
        Write-Warning "Failed to save configuration value for '$Key': $_"
        return $false
    }
}

# Function to save configuration to .taskhero_setup.json (consolidated settings file)
function Save-AppConfig {
    param(
        [string]$Key,
        $Value
    )
    $setupFile = Join-Path $PSScriptRoot ".taskhero_setup.json"
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
    Write-Host "  -Force     Force re-run all setup steps"
    Write-Host "  -Initial   Delete all environment files and start completely fresh"
    Write-Host "  -Help      Show this help message"
    Write-Host ""
    Write-Host "DESCRIPTION:"
    Write-Host "  This script sets up TaskHero AI with all required dependencies,"
    Write-Host "  creates a virtual environment, and configures the application."
    Write-Host ""
    Write-Host "PARAMETER DETAILS:"
    Write-Host "  -Force:    Skips existing setup checks and re-runs all installation steps."
    Write-Host "             Useful when you want to update dependencies or fix issues."
    Write-Host ""
    Write-Host "  -Initial:  *** DESTRUCTIVE OPERATION ***"
    Write-Host "             Deletes ALL environment files and folders before setup:"
    Write-Host "             - Virtual environment folder (venv)"
    Write-Host "             - Setup tracking file (.taskhero_setup.json)"
    Write-Host "             - Environment configuration (.env)"
    Write-Host "             - Application settings (app_settings.json)"
    Write-Host "             - Index cache folders (.index)"
    Write-Host "             - Python cache folders (__pycache__)"
    Write-Host "             Automatically enables Force mode after cleanup."
    Write-Host "             Requires user confirmation before deletion."
    Write-Host ""
    Write-Host "EXAMPLES:"
    Write-Host "  .\setup_windows_modern.ps1              # Normal setup"
    Write-Host "  .\setup_windows_modern.ps1 -Force       # Force complete reinstall"
    Write-Host "  .\setup_windows_modern.ps1 -Initial     # Delete everything and start fresh"
    Write-Host ""
    Write-Host "SAFETY NOTES:"
    Write-Host "  - The -Initial flag will ask for confirmation before deleting files"
    Write-Host "  - Confirmation defaults to 'No' for safety"
    Write-Host "  - You can cancel the operation at any time during confirmation"
    Write-Host "  - Use -Initial when you want to completely reset your installation"
    Write-Host ""
    exit 0
}

if ($Help) {
    Show-Help
}

# Handle Initial flag - cleanup environment before setup
if ($Initial) {
    Write-Host ""
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-ColoredLine "                        TaskHero AI Initial Setup Mode                    " $Colors.Primary
    Write-ColoredLine "===============================================================================" $Colors.Primary
    Write-Host ""
    Write-Info "Initial setup mode detected - preparing for complete environment reset..."

    # Call cleanup function
    $cleanupSuccess = Remove-EnvironmentFolders

    if (-not $cleanupSuccess) {
        Write-Host ""
        Write-Error "Initial setup cancelled or failed during cleanup."
        Write-Info "No changes were made to your environment."
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Automatically enable Force mode after successful cleanup
    Write-Host ""
    Write-Success "Environment cleanup completed successfully!"
    Write-Info "Automatically enabling Force mode for complete fresh installation..."
    $Force = $true

    Write-Host ""
    Write-ColoredLine "===============================================================================" $Colors.Success
    Write-ColoredLine "                    Proceeding with Fresh Installation                     " $Colors.Success
    Write-ColoredLine "===============================================================================" $Colors.Success
    Write-Host ""
}

# Main setup process
Write-Host ""
Write-ColoredLine "===============================================================================" $Colors.Primary
Write-ColoredLine "                        TaskHero AI Setup for Windows                     " $Colors.Primary
Write-ColoredLine "===============================================================================" $Colors.Primary
Write-Host ""

if ($Force) {
    Write-Warning "Force mode enabled - all steps will be re-executed"
    $setupFile = Join-Path $PSScriptRoot ".taskhero_setup.json"
    if (Test-Path $setupFile) {
        Remove-Item $setupFile -Force
        Write-Info "Cleared previous setup state"
    }
}

# Check if setup is already complete and can skip to app launch
if (-not $Force) {
    $setupFile = Join-Path $PSScriptRoot ".taskhero_setup.json"
    if (Test-Path $setupFile) {
        try {
            $setupData = Get-Content $setupFile | ConvertFrom-Json
            $requiredSteps = @("venv_created", "dependencies_installed", "pip_upgraded", "setup_completed")
            $allStepsComplete = $true

            foreach ($step in $requiredSteps) {
                if (-not $setupData.setup_completed.$step) {
                    $allStepsComplete = $false
                    break
                }
            }

            # Also verify that key files/directories exist
            $pythonExe = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
            $appFile = Join-Path $PSScriptRoot "app.py"

            if ($allStepsComplete -and (Test-Path $pythonExe) -and (Test-Path $appFile)) {
                Write-Host ""
                Write-ColoredLine "===============================================================================" $Colors.Success
                Write-ColoredLine "                    TaskHero AI Already Set Up - Quick Start!                " $Colors.Success
                Write-ColoredLine "===============================================================================" $Colors.Success
                Write-Host ""
                Write-Success "Setup already completed on $($setupData.setup_completed.last_updated)"
                Write-Info "All required components are installed and configured."
                Write-Host ""

                # Quick verification of dependencies
                Write-Info "Performing quick dependency check..."
                try {
                    & $pythonExe -c "import colorama, rich, dotenv" 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) {
                        Write-Success "Dependencies verified successfully"

                        # Skip directly to app launch
                        Write-Host ""
                        Write-ColoredLine "===============================================================================" $Colors.Primary
                        Write-ColoredLine "                          Starting TaskHero AI...                        " $Colors.Primary
                        Write-ColoredLine "===============================================================================" $Colors.Primary
                        Write-Host ""

                        Write-Info "Launching TaskHero AI main application..."
                        & $pythonExe $appFile
                        exit 0
                    }
                    else {
                        Write-Warning "Dependencies verification failed. Running full setup..."
                    }
                }
                catch {
                    Write-Warning "Dependencies check failed: $_. Running full setup..."
                }
            }
            else {
                Write-Info "Setup incomplete or files missing. Running full setup..."
            }
        }
        catch {
            Write-Info "Could not read setup file. Running full setup..."
        }
    }
    else {
        Write-Info "No previous setup found. Running full setup..."
    }
}

# Step 1: Check Prerequisites
Write-SectionHeader "Step 1: Checking Prerequisites" "[CHECK]"
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
Write-SectionHeader "Step 2: Setting up Virtual Environment" "[PYTHON]"
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
Write-SectionHeader "Step 3: Activating Virtual Environment" "[ACTIVATE]"
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
Write-SectionHeader "Step 4: Installing Dependencies" "[PACKAGES]"
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
                $importCmd = "import $testCmd; print('$testCmd imported successfully')"
                $testResult = & $pythonExe -c $importCmd 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "$dep"
                } else {
                    Write-Error "$dep - $testResult"
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
Write-SectionHeader "Step 5: Checking for Ollama" "[OLLAMA]"
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

# Step 6: Interactive Configuration Wizard
Write-SectionHeader "Step 6: Interactive Configuration Wizard" "[CONFIG]"
Show-Progress 6 8 "Starting configuration wizard..."

Write-Info "Starting interactive configuration wizard..."
Write-Info "This will configure TaskHero AI for your specific needs."
Write-ColoredLine "===============================================================================" $Colors.Primary

# Configuration Step 1: Repository Type
Write-Host ""
Write-SectionHeader "Configuration 1/5: Repository Type" "[CONFIG]"
Write-Info "Will this be a central repository for all different code bases,"
Write-Info "or will it reside within an existing codebase?"
Write-Host ""
Write-Info "1. Central repository (recommended for multiple projects)"
Write-Info "2. Singular repository (embedded in existing codebase)"
Write-ColoredLine "===============================================================================" $Colors.Primary

# Configuration Step 1: Repository Type
$skipRepoType = $false
if (-not $Force) {
    $existingRepoType = Get-ConfigValue "repository_type"
    if ($existingRepoType) {
        Write-Info "Repository type already configured as: $existingRepoType. Skipping..."
        $skipRepoType = $true
    }
}

if (-not $skipRepoType) {
    $repoTypeChoice = Get-UserInput "Please select repository type (1 or 2):" "option" "1" @("1", "2")
    if ($repoTypeChoice -eq "1") {
        $repoTypeName = "central"
        Write-Success "Selected: Central repository"
    } else {
        $repoTypeName = "singular"
        Write-Success "Selected: Singular repository"
    }
    Set-ConfigValue "repository_type" $repoTypeName
}

# Configuration Step 2: Codebase Path
Write-Host ""
Write-SectionHeader "Configuration 2/5: Codebase Path" "[CONFIG]"
Write-Info "Please specify the path of the codebase that TaskHero will index."
Write-Info "Current directory: $PWD"
Write-Host ""
Write-Info "Examples:"
Write-Info "- C:\Projects\MyProject"
Write-Info "- .\MyProject (relative path)"
Write-Info "- $PWD (current directory)"
Write-ColoredLine "===============================================================================" $Colors.Primary

$skipCodebasePath = $false
if (-not $Force) {
    $existingCodebasePath = Get-ConfigValue "codebase_path"
    if ($existingCodebasePath) {
        Write-Info "Codebase path already configured as: $existingCodebasePath. Skipping..."
        $skipCodebasePath = $true
    }
}

if (-not $skipCodebasePath) {
    $codebasePath = Get-UserInput "Enter the codebase path to index:" "path" $PWD
    Write-Success "Codebase path set to: $codebasePath"
    Set-ConfigValue "codebase_path" $codebasePath

    # Add TaskHero AI folder to .gitignore in the codebase directory
    if (-not $Force -and (Test-SetupCompleted "gitignore_configured")) {
        Write-Success ".gitignore already configured - skipping"
    } else {
        Write-Host ""
        Write-Info "Configuring .gitignore to exclude TaskHero AI files..."
        $gitIgnoreResult = Add-ToGitIgnore -CodebasePath $codebasePath -TaskHeroPath $PSScriptRoot
        if ($gitIgnoreResult) {
            Set-SetupCompleted "gitignore_configured" | Out-Null
        } else {
            Write-Warning "Could not automatically update .gitignore. You may want to manually add the TaskHero AI folder to your .gitignore file."
        }
    }
} else {
    # Even if skipping codebase path configuration, try to update .gitignore if we have the path
    $existingCodebasePath = Get-ConfigValue "codebase_path"
    if ($existingCodebasePath) {
        if (-not $Force -and (Test-SetupCompleted "gitignore_configured")) {
            Write-Success ".gitignore already configured - skipping"
        } else {
            Write-Host ""
            Write-Info "Checking .gitignore configuration for existing codebase path..."
            $gitIgnoreResult = Add-ToGitIgnore -CodebasePath $existingCodebasePath -TaskHeroPath $PSScriptRoot
            if ($gitIgnoreResult) {
                Set-SetupCompleted "gitignore_configured" | Out-Null
            } else {
                Write-Info "Note: You may want to manually add the TaskHero AI folder to your .gitignore file."
            }
        }
    }
}

# Configuration Step 3: Task Files Storage
Write-Host ""
Write-SectionHeader "Configuration 3/5: Task Files Storage Location" "[CONFIG]"
Write-Info "Where would you like to store project task files?"
Write-Host ""
Write-Info "1. Present folder ($PWD)"
Write-Info "2. TaskHero tasks folder (/theherotasks) [RECOMMENDED]"
Write-Info "3. Custom path (you will specify)"
Write-ColoredLine "===============================================================================" $Colors.Primary

$skipTaskStorage = $false
if (-not $Force) {
    $existingTaskPath = Get-ConfigValue "task_storage_path"
    if ($existingTaskPath) {
        Write-Info "Task storage location already configured as: $existingTaskPath. Skipping..."
        $skipTaskStorage = $true
    }
}

if (-not $skipTaskStorage) {
    $taskStorageChoice = Get-UserInput "Please select task storage option (1, 2, or 3):" "option" "2" @("1", "2", "3")
    switch ($taskStorageChoice) {
        "1" {
            $taskStoragePath = $PWD
            Write-Success "Task storage set to: Present folder"
        }
        "2" {
            $taskStoragePath = Join-Path $PWD "theherotasks"
            Write-Success "Task storage set to: TaskHero tasks folder"
            # Create the directory if it doesn't exist
            if (-not (Test-Path $taskStoragePath)) {
                New-Item -Path $taskStoragePath -ItemType Directory -Force | Out-Null
                Write-Info "Created theherotasks directory"
            }
        }
        "3" {
            $taskStoragePath = Get-UserInput "Enter custom path for task storage:" "path"
            Write-Success "Task storage set to: Custom path ($taskStoragePath)"
            # Create the directory if it doesn't exist
            if (-not (Test-Path $taskStoragePath)) {
                try {
                    New-Item -Path $taskStoragePath -ItemType Directory -Force | Out-Null
                    Write-Info "Created custom task storage directory"
                } catch {
                    Write-Warning "Could not create custom directory. Using current directory instead."
                    $taskStoragePath = $PWD
                }
            }
        }
    }
    Set-ConfigValue "task_storage_path" $taskStoragePath
}
# Configuration Step 4: API Usage
Write-Host ""
Write-SectionHeader "Configuration 4/5: API Configuration" "[CONFIG]"
Write-Info "TaskHero AI can work with various AI providers."
Write-Info "Default configuration uses Ollama (local models)."
Write-Host ""
Write-Info "Available providers:"
Write-Info "- Ollama (local, free, requires installation)"
Write-Info "- OpenAI (cloud, requires API key)"
Write-Info "- Anthropic (cloud, requires API key)"
Write-Info "- OpenRouter (cloud, requires API key)"
Write-Info "- Google (cloud, requires API key)"
Write-Info "- Groq (cloud, requires API key)"
Write-ColoredLine "===============================================================================" $Colors.Primary

# Check for .env file and create with comprehensive settings
if (-not (Test-Path ".env")) {
    Write-Info "Creating comprehensive .env file..."

    # Create comprehensive .env file with all provider options
    $comprehensiveEnv = @'
# TaskHero AI Configuration
# Created by setup script

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

# Model Temperatures
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

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434

# Application Settings
APP_DEBUG=false
APP_LOG_LEVEL=INFO
APP_DATA_DIR=./data
'@

    $comprehensiveEnv | Out-File -FilePath ".env" -Encoding UTF8
    Write-Success "Created comprehensive .env configuration"
} else {
    Write-Info ".env file already exists - checking for required settings..."
    Write-Success "Using existing .env configuration"
}

Write-Info "API configuration can be done manually by editing the .env file."
Write-Info "Default configuration uses Ollama (local models)."
$configureApis = Get-UserInput "Would you like to configure API keys now? (Y/N):" "yn" "N"

if ($configureApis.ToUpper() -eq "Y") {
    Write-Host ""
    Write-Info "Opening .env file for manual configuration..."
    Write-Info "Please edit the API keys and providers as needed."
    Write-Info "Save and close the file when done, then press any key to continue."
    Write-Host "Press any key to continue..." -NoNewline
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""

    if (Get-Command "notepad.exe" -ErrorAction SilentlyContinue) {
        Start-Process -FilePath "notepad.exe" -ArgumentList ".env" -Wait
    } else {
        Write-Info "Please manually edit the .env file with your preferred text editor."
        Write-Host "Press any key to continue..." -NoNewline
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Write-Host ""
    }
} else {
    Write-Info "Skipping API configuration. You can configure later by editing .env file."
}

# Configuration Step 5: Model Settings
Write-Host ""
Write-SectionHeader "Configuration 5/5: Model Settings" "[CONFIG]"
Write-Info "TaskHero AI uses different models for different tasks."
Write-Info "Default models are configured for Ollama."
Write-Host ""
Write-Info "Model categories:"
Write-Info "- Chat Model: For conversations and general AI assistance"
Write-Info "- Embedding Model: For code indexing and similarity search"
Write-Info "- Description Model: For generating task descriptions"
Write-Info "- Agent Buddy Model: For AI agent interactions"
Write-ColoredLine "===============================================================================" $Colors.Primary

$configureModels = Get-UserInput "Would you like to review/modify model settings? (Y/N):" "yn" "N"

if ($configureModels.ToUpper() -eq "Y") {
    Write-Host ""
    Write-Info "Opening .env file for model configuration..."
    Write-Info "Look for the model settings section and modify as needed."
    Write-Info "Save and close the file when done, then press any key to continue."
    Write-Host "Press any key to continue..." -NoNewline
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""

    if (Get-Command "notepad.exe" -ErrorAction SilentlyContinue) {
        Start-Process -FilePath "notepad.exe" -ArgumentList ".env" -Wait
    } else {
        Write-Info "Please manually edit the .env file with your preferred text editor."
        Write-Host "Press any key to continue..." -NoNewline
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Write-Host ""
    }
} else {
    Write-Info "Using default model settings. You can modify later by editing .env file."
}

Write-Host ""
Write-Success "Configuration wizard completed!"
Write-ColoredLine "===============================================================================" $Colors.Primary

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
Write-SectionHeader "Step 7: Finalizing Setup" "[COMPLETE]"
Show-Progress 7 8 "Completing installation..."

# Quick setup verification
Write-Info "Performing quick setup verification..."
try {
    $pythonExe = Join-Path $PWD "venv\Scripts\python.exe"
    if (Test-Path $pythonExe) {
        & $pythonExe -c "import colorama, rich, dotenv; print('All key dependencies are available')" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Setup verification completed successfully"
        } else {
            Write-Warning "Some dependencies may not be properly installed"
        }
    } else {
        Write-Warning "Virtual environment Python not found"
    }
} catch {
    Write-Warning "Setup verification encountered an issue: $_"
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

# Step 8: Auto-start TaskHero AI
Write-SectionHeader "Step 8: Starting TaskHero AI" "[LAUNCH]"
Show-Progress 8 8 "Launching application..."
Write-Host ""

$pythonExe = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (Test-Path $pythonExe) {
    Write-Info "Starting TaskHero AI with virtual environment Python..."

    # Test if dependencies are available before starting
    try {
        & $pythonExe -c "import colorama, rich, dotenv" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencies verified, starting application..."

            # Launch TaskHero AI main application
            $appPath = Join-Path $PSScriptRoot "app.py"

            if (Test-Path $appPath) {
                Write-Info "Launching TaskHero AI main application..."
                & $pythonExe $appPath
            }
            else {
                Write-Error "app.py not found in the TaskHero AI directory!"
                Write-Info "Please ensure you are running this script from the TaskHero AI root directory."
                Read-Host "Press Enter to exit"
            }
        }
        else {
            Write-Error "Dependencies not found in virtual environment!"
            Write-Info "Please run the setup script again with -Force flag."
            Write-Host ""
            Write-Info "To manually start TaskHero AI later, run:"
            Write-Host "  .\venv\Scripts\python.exe app.py"
            Write-Host ""
            Read-Host "Press Enter to exit"
        }
    }
    catch {
        Write-Error "Failed to verify dependencies or start app: $_"
        Write-Info "Please run the setup script again with -Force flag."
        Write-Host ""
        Write-Info "To manually start TaskHero AI later, run:"
        Write-Host "  .\venv\Scripts\python.exe app.py"
        Write-Host ""
        Read-Host "Press Enter to exit"
    }
}
else {
    Write-Error "Virtual environment Python not found!"
    Write-Info "Please run the setup script again with -Force flag."
    Write-Host ""
    Write-Info "For more information, see the documentation at:"
    Write-Host "  https://github.com/Interstellar-code/taskheroai"
    Write-Host ""
    Read-Host "Press Enter to exit"
}