@echo off
setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo                            TaskHero AI - Enhanced Setup
echo ================================================================================
echo   Welcome to the TaskHero AI Installation and Configuration Wizard!
echo   This script will guide you through the complete setup process.
echo ================================================================================
echo.

:: Skip over function definitions during main execution
goto :main

:: Function to check if a setup step was completed (using .taskhero_setup.json)
:check_setup_completed_fallback
set "step_name=%1"
:: Check .taskhero_setup.json for completion status
powershell -Command "if (Test-Path '.taskhero_setup.json') { $json = Get-Content '.taskhero_setup.json' | ConvertFrom-Json; if ($json.setup_completed.'%step_name%' -eq $true) { exit 0 } else { exit 1 } } else { exit 1 }"
exit /b %ERRORLEVEL%

:: Function to mark a setup step as completed (using .taskhero_setup.json)
:mark_setup_completed_fallback
set "step_name=%1"
:: Update .taskhero_setup.json with completion status
powershell -Command "$file = '.taskhero_setup.json'; if (Test-Path $file) { $json = Get-Content $file | ConvertFrom-Json } else { $json = @{setup_completed=@{}} }; if (-not $json.setup_completed) { $json | Add-Member -NotePropertyName 'setup_completed' -NotePropertyValue @{} }; $json.setup_completed | Add-Member -NotePropertyName '%step_name%' -NotePropertyValue $true -Force; $json.setup_completed | Add-Member -NotePropertyName 'last_updated' -NotePropertyValue (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.ffffff') -Force; $json | ConvertTo-Json -Depth 10 | Out-File $file -Encoding UTF8"
exit /b 0

:: Function to check if a file is newer than a completed step (using .taskhero_setup.json)
:check_file_newer_fallback
set "file_path=%1"
set "step_name=%2"
:: Check if step was completed and compare file timestamps
powershell -Command "if (-not (Test-Path '.taskhero_setup.json')) { exit 0 }; $json = Get-Content '.taskhero_setup.json' | ConvertFrom-Json; if (-not $json.setup_completed.'%step_name%') { exit 0 }; if (-not (Test-Path '%file_path%')) { exit 1 }; $setupTime = [DateTime]::Parse($json.setup_completed.last_updated); $fileTime = (Get-Item '%file_path%').LastWriteTime; if ($fileTime -gt $setupTime) { exit 0 } else { exit 1 }"
exit /b %ERRORLEVEL%
:: Simple check: if requirements.txt exists and marker exists, assume it may need update
:: This is a simplified check for batch-only mode
exit /b 0

:: Function to check if a setup step was completed
:check_setup_completed
set "step_name=%1"
if exist ".taskhero_setup.json" (
    findstr /c:"\"%step_name%\"" .taskhero_setup.json | findstr /c:"\"completed\": true" >nul 2>&1
    exit /b %errorlevel%
)
exit /b 1

:: Function to mark a setup step as completed
:mark_setup_completed
set "step_name=%1"
:: Create or update the setup file using Python if available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python -c "import json,os; data=json.load(open('.taskhero_setup.json')) if os.path.exists('.taskhero_setup.json') else {'setup_completed':{}}; data.setdefault('setup_completed',{})['%step_name%']={'completed':True}; json.dump(data,open('.taskhero_setup.json','w'),indent=2)" 2>nul
    if !errorlevel! equ 0 exit /b 0
)
:: Fallback: create simple marker
echo {"setup_completed":{"%step_name%":{"completed":true}}} > .taskhero_setup.json
exit /b 0

:: Function to check if a file is newer than a completed step
:check_file_newer
set "file_path=%1"
set "step_name=%2"
if not exist "%file_path%" exit /b 1
if not exist ".taskhero_setup.json" exit /b 0
:: Simple check: if file exists and setup exists, assume file might be newer
exit /b 0

:: Function to display progress bar
:show_progress
set "step=%1"
set "total=%2"
set "description=%3"
set /a "progress=(%step%*50)/%total%"
set "bar="
for /l %%i in (1,1,%progress%) do set "bar=!bar!█"
for /l %%i in (%progress%,1,49) do set "bar=!bar!░"
echo ║ %description% [!bar!] %step%/%total% ║
exit /b 0

:: Function to get user input with validation
:get_user_input
set "prompt=%1"
set "variable_name=%2"
set "validation_type=%3"
:input_loop
echo.
echo %prompt%
set /p "user_input=Enter your choice: "
if "%validation_type%"=="yn" (
    if /i "!user_input!"=="Y" (
        set "%variable_name%=Y"
        exit /b 0
    )
    if /i "!user_input!"=="N" (
        set "%variable_name%=N"
        exit /b 0
    )
    echo [ERROR] Please enter Y or N only.
    goto :input_loop
)
if "%validation_type%"=="path" (
    if "!user_input!"=="" (
        echo [ERROR] Path cannot be empty.
        goto :input_loop
    )
    set "%variable_name%=!user_input!"
    exit /b 0
)
if "%validation_type%"=="option" (
    if "!user_input!"=="1" (
        set "%variable_name%=1"
        exit /b 0
    )
    if "!user_input!"=="2" (
        set "%variable_name%=2"
        exit /b 0
    )
    if "!user_input!"=="3" (
        set "%variable_name%=3"
        exit /b 0
    )
    echo [ERROR] Please enter 1, 2, or 3 only.
    goto :input_loop
)
set "%variable_name%=!user_input!"
exit /b 0

:: Function to check if a configuration exists
:check_config_exists
set "config_key=%1"
if exist "app_settings.json" (
    findstr /c:"\"%config_key%\"" app_settings.json >nul 2>&1
    exit /b %errorlevel%
)
exit /b 1

:: Function to save configuration to .taskhero_setup.json
:save_config
set "config_key=%1"
set "config_value=%2"
:: Create or update .taskhero_setup.json using Python if available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python -c "import json,os; data=json.load(open('.taskhero_setup.json')) if os.path.exists('.taskhero_setup.json') else {'setup_completed':{}}; data['%config_key%']='%config_value%'; json.dump(data,open('.taskhero_setup.json','w'),indent=2)" 2>nul
    if !errorlevel! equ 0 exit /b 0
)
:: Fallback: create simple JSON structure
if not exist ".taskhero_setup.json" (
    echo {"setup_completed": {}, "%config_key%": "%config_value%"} > .taskhero_setup.json
) else (
    echo [WARNING] Could not update .taskhero_setup.json automatically. Please update manually.
)
exit /b 0



:: Function to add TaskHero AI folder to .gitignore
:add_to_gitignore
set "codebase_path=%1"
set "taskhero_path=%2"

echo [INFO] Configuring .gitignore to exclude TaskHero AI files...
echo [INFO] Codebase path: %codebase_path%
echo [INFO] TaskHero AI path: %taskhero_path%

:: Calculate relative path from codebase to TaskHero AI folder
set "gitignore_path=%codebase_path%\.gitignore"
set "relative_path="

:: Get the folder name of TaskHero AI installation
for %%i in ("%taskhero_path%") do set "taskhero_folder=%%~ni"

:: Try to calculate relative path (simplified approach for batch)
:: If codebase path contains taskhero path, use relative path
echo %taskhero_path% | findstr /i "%codebase_path%" >nul
if %errorlevel% equ 0 (
    :: TaskHero is inside codebase, use relative path
    call :get_relative_path "%codebase_path%" "%taskhero_path%" relative_path
) else (
    :: TaskHero is outside codebase, use folder name
    set "relative_path=./%taskhero_folder%"
)

echo [INFO] Relative path to ignore: %relative_path%

:: Check if .gitignore exists, create if not
if not exist "%gitignore_path%" (
    echo [INFO] Creating .gitignore file in codebase directory...
    echo. > "%gitignore_path%"
)

:: Check if TaskHero AI is already in .gitignore
findstr /i "taskheroai" "%gitignore_path%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] TaskHero AI folder is already in .gitignore
    exit /b 0
)

findstr /i "%relative_path%" "%gitignore_path%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] TaskHero AI folder is already in .gitignore
    exit /b 0
)

:: Add TaskHero AI to .gitignore
echo. >> "%gitignore_path%"
echo # TaskHero AI - Added by setup script >> "%gitignore_path%"
echo %relative_path% >> "%gitignore_path%"

echo [SUCCESS] Added TaskHero AI folder to .gitignore: %relative_path%
exit /b 0

:: Helper function to get relative path (simplified)
:get_relative_path
set "base_path=%~1"
set "target_path=%~2"
set "result_var=%3"

:: Simple relative path calculation
set "folder_name="
for %%i in ("%target_path%") do set "folder_name=%%~ni"
set "%result_var%=./%folder_name%"
exit /b 0

:: Function to get configuration value from .taskhero_setup.json
:get_config_value
set "config_key=%1"
set "return_var=%2"

if not exist ".taskhero_setup.json" (
    set "%return_var%="
    exit /b 1
)

:: Use PowerShell to extract the value from JSON
for /f "delims=" %%i in ('powershell -Command "try { $json = Get-Content '.taskhero_setup.json' | ConvertFrom-Json; if ($json.'%config_key%') { Write-Output $json.'%config_key%' } else { Write-Output '' } } catch { Write-Output '' }"') do (
    set "%return_var%=%%i"
)

exit /b 0

:: Function to display section header
:show_section
set "title=%1"
echo.
echo ================================================================================
echo  %title%
echo ================================================================================
exit /b 0

:: Main execution starts here
:main

:: Check for --force flag to skip setup tracking
set FORCE_SETUP=0
if "%1"=="--force" (
    set FORCE_SETUP=1
    echo   [INFO] Force setup mode enabled - all steps will be executed.
    echo ================================================================================
    echo.
) else (
    echo   [INFO] This wizard will install packages and configure your TaskHero AI setup.
    echo   [INFO] Previously completed steps will be automatically skipped.
    echo ================================================================================
    echo.
)

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Python is not installed or not in PATH.
    echo [INFO] Setup will use basic tracking without Python-based features.
    echo.
    echo Please install Python 3.11.6 or later from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    set /p CONTINUE="Do you want to continue with basic setup? (Y/N): "
    if /i "!CONTINUE!" neq "Y" exit /b 1
    set PYTHON_AVAILABLE=0
) else (
    :: Check Python version
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%V"
    echo [INFO] Detected Python version: !PYTHON_VERSION!
    set PYTHON_AVAILABLE=1

    :: Extract version components safely
    set "MAJOR=0"
    set "MINOR=0"
    set "PATCH=0"

    :: Parse version string carefully
    for /f "tokens=1,2,3 delims=." %%a in ("!PYTHON_VERSION!") do (
        set "MAJOR=%%a"
        set "MINOR=%%b"
        set "PATCH=%%c"
    )

    if !MAJOR! lss 3 (
        echo [WARNING] Python version !PYTHON_VERSION! may be too old.
        echo This application was tested with Python 3.11.6.
        echo You may encounter issues with older versions.
        echo.
        set /p CONTINUE="Do you want to continue anyway? (Y/N): "
        if /i "!CONTINUE!" neq "Y" exit /b 1
    ) else (
        if !MAJOR! equ 3 (
            if !MINOR! lss 11 (
                echo [WARNING] Python version !PYTHON_VERSION! may be too old.
                echo This application was tested with Python 3.11.6.
                echo You may encounter issues with older versions.
                echo.
                set /p CONTINUE="Do you want to continue anyway? (Y/N): "
                if /i "!CONTINUE!" neq "Y" exit /b 1
            )
        )
    )
)

:: Create virtual environment
echo.
echo [STEP 1] Creating virtual environment...

if %PYTHON_AVAILABLE% equ 0 (
    echo [ERROR] Cannot create virtual environment without Python.
    echo Please install Python first and re-run this script.
    exit /b 1
)

if %FORCE_SETUP% equ 0 (
    call :check_setup_completed "venv_created"
    if !errorlevel! equ 0 (
        echo [INFO] Virtual environment already created. Skipping creation.
        goto :skip_venv_creation
    )
)

if exist venv (
    echo [INFO] Virtual environment directory exists. Checking if it's valid...
    echo [INFO] Current directory: %CD%
    echo [INFO] Checking for: %CD%\venv\Scripts\python.exe

    if exist "venv\Scripts\python.exe" (
        call venv\Scripts\activate >nul 2>&1
        if !errorlevel! equ 0 (
            call deactivate >nul 2>&1
            echo [SUCCESS] Valid virtual environment found. Skipping creation.
            call :mark_setup_completed "venv_created"
            goto :skip_venv_creation
        ) else (
            echo [WARNING] Virtual environment directory exists but activation failed. Recreating...
            rmdir /s /q venv
        )
    ) else (
        echo [WARNING] Virtual environment directory exists but Python executable not found. Recreating...
        rmdir /s /q venv
    )
)

python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
)
echo [SUCCESS] Virtual environment created.
call :mark_setup_completed "venv_created"

:skip_venv_creation

:: Activate virtual environment
echo.
echo [STEP 2] Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    exit /b 1
)
echo [SUCCESS] Virtual environment activated.

:: Upgrade pip
echo.
echo [STEP 3] Upgrading pip...

if %FORCE_SETUP% equ 0 (
    call :check_setup_completed "pip_upgraded"
    if !errorlevel! equ 0 (
        echo [INFO] Pip already upgraded recently. Skipping upgrade.
        goto :skip_pip_upgrade
    )
)

python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip, but continuing with installation.
) else (
    call :mark_setup_completed "pip_upgraded"
)

:skip_pip_upgrade

:: Install dependencies
echo.
echo [STEP 4] Installing dependencies...

if %FORCE_SETUP% equ 0 (
    call :check_setup_completed "dependencies_installed"
    if !errorlevel! equ 0 (
        echo [INFO] Dependencies already installed. Checking if requirements.txt has changed...
        :: Check if requirements.txt is newer than the last install
        if exist requirements.txt (
            call :check_file_newer "requirements.txt" "dependencies_installed"
            if !errorlevel! equ 0 (
                echo [INFO] Requirements unchanged. Skipping dependency installation.
                goto :skip_dependency_install
            ) else (
                echo [INFO] Requirements.txt has been updated. Reinstalling dependencies...
            )
        ) else (
            echo [INFO] Requirements unchanged. Skipping dependency installation.
            goto :skip_dependency_install
        )
    )
)

echo [INFO] Installing dependencies using virtual environment Python...
echo [INFO] This may take several minutes depending on your internet connection...

:: Use the virtual environment Python and pip explicitly
venv\Scripts\python.exe -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] Pip upgrade failed, but continuing...
)

:: Install dependencies with no cache to avoid issues
venv\Scripts\python.exe -m pip install -r requirements.txt --no-cache-dir
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    echo [INFO] Please check your internet connection and try again.
    echo [INFO] You can also try running: venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo [SUCCESS] Dependencies installed successfully.

:: Verify key dependencies
echo [INFO] Verifying key dependencies...
venv\Scripts\python.exe -c "import colorama; print('colorama: OK')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] colorama verified
) else (
    echo [ERROR] colorama verification failed
    echo [INFO] Dependencies may not have installed correctly
    pause
    exit /b 1
)

venv\Scripts\python.exe -c "import requests; print('requests: OK')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] requests verified
) else (
    echo [ERROR] requests verification failed
    echo [INFO] Dependencies may not have installed correctly
    pause
    exit /b 1
)

venv\Scripts\python.exe -c "import rich; print('rich: OK')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] rich verified
) else (
    echo [ERROR] rich verification failed
    echo [INFO] Dependencies may not have installed correctly
    pause
    exit /b 1
)

echo [SUCCESS] All key dependencies verified successfully.
call :mark_setup_completed "dependencies_installed"

:skip_dependency_install

:: Check if Ollama is installed
echo.
echo [STEP 5] Checking for Ollama...

:: Check if .env file exists and has Ollama configuration
set SKIP_OLLAMA_CHECK=0
if exist .env (
    echo [INFO] Checking existing .env configuration...

    :: Check for custom OLLAMA_HOST configuration
    findstr /i "OLLAMA_HOST=" .env >nul 2>&1
    if !errorlevel! equ 0 (
        echo [INFO] Custom OLLAMA_HOST found in .env file.
        set SKIP_OLLAMA_CHECK=1
    )

    :: Check if any providers are set to non-ollama values
    findstr /i "AI_.*_PROVIDER=" .env | findstr /v /i "ollama" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [INFO] Non-Ollama providers configured in .env file.
        set SKIP_OLLAMA_CHECK=1
    )
)

if !SKIP_OLLAMA_CHECK! equ 1 (
    echo [INFO] Ollama configuration found in .env file. Skipping Ollama installation check.
    echo [INFO] Using existing configuration from .env file.
    goto :skip_ollama
)

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama is not installed or not in PATH.
    echo You will need to install Ollama to use local models.
    echo Download from: https://ollama.com/download
    echo.
    echo Would you like to open the Ollama download page? (Y/N)
    set /p OPEN_OLLAMA="Enter your choice (Y/N): "
    if /i "!OPEN_OLLAMA!"=="Y" (
        start https://ollama.com/download
    )
) else (
    echo [SUCCESS] Ollama is installed.
)

:skip_ollama

:: Create .env file if it doesn't exist
echo.
echo [STEP 6] Setting up environment variables...

if %FORCE_SETUP% equ 0 (
    call :check_setup_completed "env_file_created"
    if !errorlevel! equ 0 (
        if exist .env (
            echo [INFO] Environment file already exists and was set up previously. Skipping creation.
            goto :skip_env_creation
        )
    )
)

if not exist .env (
    echo [INFO] Creating .env file with default settings...
    (
        echo # Provider can be: ollama, google, openai, anthropic, groq, or openrouter
        echo AI_CHAT_PROVIDER=ollama
        echo AI_EMBEDDING_PROVIDER=ollama
        echo AI_DESCRIPTION_PROVIDER=ollama
        echo AI_AGENT_BUDDY_PROVIDER=ollama
        echo.
        echo # API Keys for each functionality (only needed if using that provider)
        echo # The same key will be used for the selected provider in each category
        echo AI_CHAT_API_KEY=None
        echo AI_EMBEDDING_API_KEY=None
        echo AI_DESCRIPTION_API_KEY=None
        echo AI_AGENT_BUDDY_API_KEY=None
        echo.
        echo # Model names for each provider
        echo # For ollama: llama2, codellama, mistral, etc. (embedding)
        echo # For OpenAI: gpt-4, gpt-3.5-turbo, text-embedding-ada-002 (embedding)
        echo # For OpenRouter: anthropic/claude-3-opus, openai/gpt-4-turbo, google/gemini-pro, etc.
        echo # For Google: gemini-pro, gemini-pro-vision
        echo # For Anthropic: claude-3-5-sonnet-latest, claude-3-opus-20240229, claude-3-haiku-20240307
        echo # For Groq: llama3-8b-8192, llama3-70b-8192, mixtral-8x7b-32768
        echo CHAT_MODEL=llama2
        echo EMBEDDING_MODEL=all-minilm:33m
        echo DESCRIPTION_MODEL=llama2
        echo AI_AGENT_BUDDY_MODEL=llama3.2
        echo.
        echo # Model Tempratures
        echo CHAT_MODEL_TEMPERATURE=0.7
        echo DESCRIPTION_MODEL_TEMPERATURE=0.3
        echo AI_AGENT_BUDDY_MODEL_TEMPERATURE=0.7
        echo INTENT_DETECTION_TEMPERATURE=0.1
        echo.
        echo # Model Max Tokens
        echo CHAT_MODEL_MAX_TOKENS=4096
        echo DESCRIPTION_MODEL_MAX_TOKENS=4096
        echo AI_AGENT_BUDDY_MODEL_MAX_TOKENS=4096
        echo INTENT_DETECTION_MAX_TOKENS=4096
        echo.
        echo # Other Model Settings
        echo CHAT_MODEL_TOP_P=0.95
        echo CHAT_MODEL_TOP_K=40
        echo DESCRIPTION_MODEL_TOP_P=0.95
        echo DESCRIPTION_MODEL_TOP_K=40
        echo INTENT_DETECTION_TOP_P=0.95
        echo INTENT_DETECTION_TOP_K=40
        echo.
        echo # Optional: Site information for OpenRouter rankings
        echo SITE_URL=http://localhost:3000
        echo SITE_NAME=Local Development
        echo.
        echo # Performance settings (LOW, MEDIUM, MAX)
        echo # LOW: Minimal resource usage, suitable for low-end systems
        echo # MEDIUM: Balanced resource usage, suitable for most systems
        echo # MAX: Maximum resource usage, suitable for high-end systems
        echo PERFORMANCE_MODE=MEDIUM
        echo # Maximum number of threads to use (will be calculated automatically if not set)
        echo MAX_THREADS=16
        echo # Cache size for embedding queries (higher values use more memory but improve performance)
        echo EMBEDDING_CACHE_SIZE=1000
        echo # Similarity threshold for embedding search (lower values return more results but may be less relevant)
        echo EMBEDDING_SIMILARITY_THRESHOLD=0.05
        echo.
        echo # API Rate Limiting Settings
        echo # Delay in milliseconds between embedding API calls to prevent rate limiting
        echo # Recommended: 100ms for Google, 0ms for OpenAI/Ollama (set to 0 to disable)
        echo EMBEDDING_API_DELAY_MS=100
        echo # Delay in milliseconds between description generation API calls to prevent rate limiting
        echo # Recommended: 100ms for Google, 0ms for OpenAI/Ollama (set to 0 to disable)
        echo DESCRIPTION_API_DELAY_MS=100
        echo.
        echo # Maximum number of threads to use (will be calculated automatically if not set)
        echo # MAX_THREADS=16
        echo.
        echo # UI Settings
        echo # Enable/disable markdown rendering (TRUE/FALSE)
        echo ENABLE_MARKDOWN_RENDERING=TRUE
        echo # Show thinking blocks in AI responses (TRUE/FALSE)
        echo SHOW_THINKING_BLOCKS=FALSE
        echo # Enable streaming mode for AI responses (TRUE/FALSE) # Tends to be slower for some reason # Broken for openrouter TODO: Fix this at some point !
        echo ENABLE_STREAMING_MODE=FALSE
        echo # Enable chat logging to save conversations (TRUE/FALSE)
        echo CHAT_LOGS=FALSE
        echo # Enable memory for AI conversations (TRUE/FALSE)
        echo MEMORY_ENABLED=TRUE
        echo # Maximum number of memory items to store
        echo MAX_MEMORY_ITEMS=10
        echo # Execute commands without confirmation (TRUE/FALSE)
        echo # When FALSE, the user will be prompted to confirm before executing any command
        echo # When TRUE, commands will execute automatically without confirmation
        echo COMMANDS_YOLO=FALSE
        echo.
        echo # HTTP API Server Settings
        echo # Allow connections from any IP address (TRUE/FALSE)
        echo # When FALSE, the server only accepts connections from localhost (127.0.0.1)
        echo # When TRUE, the server accepts connections from any IP address (0.0.0.0)
        echo # WARNING: Setting this to TRUE may expose your API to the internet
        echo HTTP_ALLOW_ALL_ORIGINS=FALSE
        echo.
        echo # MCP Server Settings
        echo # URL of the HTTP API server
        echo MCP_API_URL=http://localhost:8000
        echo # Port to run the HTTP API server on
        echo MCP_HTTP_PORT=8000
    ) > .env
    echo [SUCCESS] Created .env file with default settings.
    call :mark_setup_completed "env_file_created"
) else (
    echo [INFO] .env file already exists. Skipping creation.
    call :mark_setup_completed "env_file_created"
)

:skip_env_creation

:: ============================================================================
:: INTERACTIVE CONFIGURATION WIZARD
:: ============================================================================

call :show_section "STEP 7: TaskHero AI Configuration Wizard                              "

:: Check if all configurations are already completed
if %FORCE_SETUP% equ 0 (
    call :check_setup_completed "configuration_completed"
    if !errorlevel! equ 0 (
        echo   [INFO] Configuration already completed. Skipping configuration wizard.
        echo   [INFO] Use --force flag to reconfigure.
        echo ================================================================================
        goto :skip_configuration
    )
)

echo   [INFO] Starting interactive configuration wizard...
echo   [INFO] This will configure TaskHero AI for your specific needs.
echo ================================================================================

:: Configuration Step 1: Repository Type
echo.
call :show_section "Configuration 1/5: Repository Type                                      "
echo   Will this be a central repository for all different code bases,
echo   or will it reside within an existing codebase?
echo.
echo   1. Central repository (recommended for multiple projects)
echo   2. Singular repository (embedded in existing codebase)
echo ================================================================================

if %FORCE_SETUP% equ 0 (
    call :check_config_exists "repository_type"
    if !errorlevel! equ 0 (
        echo [INFO] Repository type already configured. Skipping...
        goto :config_codebase_path
    )
)

call :get_user_input "Please select repository type (1 or 2):" REPO_TYPE "option"
if "!REPO_TYPE!"=="1" (
    set REPO_TYPE_NAME=central
    echo [SUCCESS] Selected: Central repository
) else (
    set REPO_TYPE_NAME=singular
    echo [SUCCESS] Selected: Singular repository
)
call :save_config "repository_type" "!REPO_TYPE_NAME!"

:config_codebase_path
:: Configuration Step 2: Codebase Path
echo.
call :show_section "Configuration 2/5: Codebase Path                                       "
echo   Please specify the path of the codebase that TaskHero will index.
echo   Current directory: %CD%
echo.
echo   Examples:
echo   - C:\Projects\MyProject
echo   - .\MyProject (relative path)
echo   - %CD% (current directory)
echo ================================================================================

if %FORCE_SETUP% equ 0 (
    call :check_config_exists "codebase_path"
    if !errorlevel! equ 0 (
        echo [INFO] Codebase path already configured. Skipping...
        :: Still check .gitignore for existing codebase path
        call :check_setup_completed_fallback "gitignore_configured"
        if !errorlevel! equ 0 (
            echo [SUCCESS] .gitignore already configured - skipping
        ) else (
            call :get_config_value "codebase_path" EXISTING_CODEBASE_PATH
            if not "!EXISTING_CODEBASE_PATH!"=="" (
                echo [INFO] Checking .gitignore configuration for existing codebase path...
                call :add_to_gitignore "!EXISTING_CODEBASE_PATH!" "%CD%"
                if !errorlevel! equ 0 (
                    call :mark_setup_completed_fallback "gitignore_configured"
                )
            )
        )
        goto :config_task_storage
    )
)

call :get_user_input "Enter the codebase path:" CODEBASE_PATH "path"
:: Validate path exists
if not exist "!CODEBASE_PATH!" (
    echo [WARNING] Path does not exist: !CODEBASE_PATH!
    call :get_user_input "Continue anyway? (Y/N):" CONTINUE_PATH "yn"
    if /i "!CONTINUE_PATH!"=="N" goto :config_codebase_path
)
echo [SUCCESS] Codebase path set to: !CODEBASE_PATH!
call :save_config "codebase_path" "!CODEBASE_PATH!"

:: Add TaskHero AI folder to .gitignore in the codebase directory
if %FORCE_SETUP% equ 0 (
    call :check_setup_completed_fallback "gitignore_configured"
    if !errorlevel! equ 0 (
        echo [SUCCESS] .gitignore already configured - skipping
        goto :config_task_storage
    )
)
echo.
call :add_to_gitignore "!CODEBASE_PATH!" "%CD%"
if !errorlevel! equ 0 (
    call :mark_setup_completed_fallback "gitignore_configured"
)

:config_task_storage
:: Configuration Step 3: Task Files Storage
echo.
call :show_section "Configuration 3/5: Task Files Storage Location                         "
echo   Where would you like to store project task files?
echo.
echo   1. Present folder (%CD%)
echo   2. TaskHero tasks folder (/theherotasks) [RECOMMENDED]
echo   3. Custom path (you will specify)
echo ================================================================================

if %FORCE_SETUP% equ 0 (
    call :check_config_exists "task_storage_path"
    if !errorlevel! equ 0 (
        echo [INFO] Task storage location already configured. Skipping...
        goto :config_api_usage
    )
)

call :get_user_input "Please select storage location (1, 2, or 3, default 2):" STORAGE_CHOICE "option"
if "!STORAGE_CHOICE!"=="" set STORAGE_CHOICE=2
if "!STORAGE_CHOICE!"=="1" (
    set TASK_STORAGE=%CD%
    echo [SUCCESS] Selected: Present folder
) else if "!STORAGE_CHOICE!"=="2" (
    set TASK_STORAGE=%CD%\theherotasks
    echo [SUCCESS] Selected: TaskHero tasks folder (/theherotasks)
    if not exist "!TASK_STORAGE!" (
        echo [INFO] Creating TaskHero tasks directory: !TASK_STORAGE!
        mkdir "!TASK_STORAGE!" 2>nul
        :: Create task status subdirectories
        mkdir "!TASK_STORAGE!\todo" 2>nul
        mkdir "!TASK_STORAGE!\inprogress" 2>nul
        mkdir "!TASK_STORAGE!\testing" 2>nul
        mkdir "!TASK_STORAGE!\devdone" 2>nul
        mkdir "!TASK_STORAGE!\done" 2>nul
        mkdir "!TASK_STORAGE!\backlog" 2>nul
        mkdir "!TASK_STORAGE!\archive" 2>nul
        echo [SUCCESS] Created task status subdirectories
    )
) else (
    call :get_user_input "Enter custom path for task files:" TASK_STORAGE "path"
    echo [SUCCESS] Selected: Custom path
    if not exist "!TASK_STORAGE!" (
        echo [INFO] Creating directory: !TASK_STORAGE!
        mkdir "!TASK_STORAGE!" 2>nul
        :: Create task status subdirectories for custom path too
        mkdir "!TASK_STORAGE!\todo" 2>nul
        mkdir "!TASK_STORAGE!\inprogress" 2>nul
        mkdir "!TASK_STORAGE!\testing" 2>nul
        mkdir "!TASK_STORAGE!\devdone" 2>nul
        mkdir "!TASK_STORAGE!\done" 2>nul
        mkdir "!TASK_STORAGE!\backlog" 2>nul
        mkdir "!TASK_STORAGE!\archive" 2>nul
        echo [SUCCESS] Created task status subdirectories
    )
)
call :save_config "task_storage_path" "!TASK_STORAGE!"
echo [INFO] Task storage path saved to app_settings.json

:config_api_usage
:: Configuration Step 4: API and MCP Functions
echo.
call :show_section "Configuration 4/5: API and MCP Functions                               "
echo   Will TaskHero API and MCP functions be used?
echo   This enables advanced AI features and integrations.
echo.
echo   Y - Yes, enable API and MCP functions
echo   N - No, use basic functionality only
echo ================================================================================

if %FORCE_SETUP% equ 0 (
    call :check_config_exists "api_usage_enabled"
    if !errorlevel! equ 0 (
        echo [INFO] API usage preference already configured. Skipping...
        goto :config_api_details
    )
)

call :get_user_input "Enable API and MCP functions? (Y/N):" API_ENABLED "yn"
if /i "!API_ENABLED!"=="Y" (
    echo [SUCCESS] API and MCP functions will be enabled
    call :save_config "api_usage_enabled" "true"
    goto :config_api_details
) else (
    echo [SUCCESS] Using basic functionality only
    call :save_config "api_usage_enabled" "false"
    goto :config_complete
)

:config_api_details
:: Configuration Step 5: API Details (only if API is enabled)
echo.
call :show_section "Configuration 5/5: API Provider Configuration                          "
echo   Configure your preferred AI providers and API keys.
echo   You can configure multiple providers or skip for now.
echo.
echo   Available providers:
echo   - OpenAI (GPT models)
echo   - Anthropic (Claude models)
echo   - DeepSeek (DeepSeek models)
echo   - OpenRouter (Multiple models)
echo   - Ollama (Local models)
echo ================================================================================

if %FORCE_SETUP% equ 0 (
    call :check_config_exists "api_providers_configured"
    if !errorlevel! equ 0 (
        echo [INFO] API providers already configured. Skipping...
        goto :config_complete
    )
)

echo [INFO] API configuration can be done manually by editing the .env file.
echo [INFO] Default configuration uses Ollama (local models).
call :get_user_input "Would you like to configure API keys now? (Y/N):" CONFIGURE_APIS "yn"

if /i "!CONFIGURE_APIS!"=="Y" (
    echo.
    echo [INFO] Opening .env file for manual configuration...
    echo [INFO] Please edit the API keys and providers as needed.
    echo [INFO] Save and close the file when done, then press any key to continue.
    pause
    if exist "%WINDIR%\system32\notepad.exe" (
        start /wait notepad.exe .env
    ) else (
        echo [INFO] Please manually edit the .env file with your preferred text editor.
        pause
    )
) else (
    echo [INFO] Skipping API configuration. You can configure later by editing .env file.
)

call :save_config "api_providers_configured" "true"

:config_complete
echo.
call :show_section "Configuration Complete!                                                "
echo   [SUCCESS] TaskHero AI configuration has been completed successfully!
echo   [INFO] All settings have been saved and will be remembered for future runs.
echo ================================================================================

call :mark_setup_completed "configuration_completed"

:skip_configuration

echo.
echo ================================================================================
echo                        TaskHero AI Setup Complete!
echo ================================================================================
echo   Installation and configuration completed successfully!
echo.
echo   To start the application, run:
echo     venv\Scripts\activate
echo     python app.py
echo.
if %PYTHON_AVAILABLE% equ 1 (
    echo   Setup status has been saved to .taskhero_setup.json
) else (
    echo   Setup status tracking is limited without Python
)
echo   To force re-run all steps, use: setup_windows.bat --force
echo.
echo   For more information, see the README.md file.
echo ================================================================================
echo.

:: Auto-start TaskHero AI
if %PYTHON_AVAILABLE% equ 1 (
    echo.
    call :show_section "Starting TaskHero AI                                                   "
    echo   Setup complete! Starting TaskHero AI automatically...
    echo ================================================================================
    echo.

    :: Use virtual environment Python to start the app
    if exist "venv\Scripts\python.exe" (
        echo [INFO] Starting TaskHero AI with virtual environment Python...

        :: Test if dependencies are available before starting
        venv\Scripts\python.exe -c "import colorama" >nul 2>&1
        if %errorlevel% equ 0 (
            echo [SUCCESS] Dependencies verified - starting application...
            venv\Scripts\python.exe app.py
        ) else (
            echo [ERROR] Dependencies not found in virtual environment!
            echo [INFO] Please run the setup script again with --force flag.
            pause
        )
    ) else (
        echo [ERROR] Virtual environment Python not found!
        echo [INFO] Please run the setup script again with --force flag.
        pause
    )
) else (
    echo.
    echo ================================================================================
    echo   [INFO] Please install Python and re-run this script to start TaskHero AI.
    echo ================================================================================
    pause
)

endlocal
