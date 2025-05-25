@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================================
echo               TaskHero AI - Setup Script
echo ========================================================
echo Windows Setup Script for TaskHero AI
echo ========================================================
echo.

:: Skip over function definitions during main execution
goto :main

:: Function to check if a setup step was completed (batch-only fallback)
:check_setup_completed_fallback
set "step_name=%1"
set "setup_marker_file=.setup_%step_name%.done"
if exist "%setup_marker_file%" (
    exit /b 0
) else (
    exit /b 1
)

:: Function to mark a setup step as completed (batch-only fallback)
:mark_setup_completed_fallback
set "step_name=%1"
set "setup_marker_file=.setup_%step_name%.done"
echo %date% %time% > "%setup_marker_file%"
exit /b 0

:: Function to check if a file is newer than a completed step (batch-only fallback)
:check_file_newer_fallback
set "file_path=%1"
set "step_name=%2"
set "setup_marker_file=.setup_%step_name%.done"
if not exist "%setup_marker_file%" (
    exit /b 0
)
if not exist "%file_path%" (
    exit /b 1
)
:: Simple check: if requirements.txt exists and marker exists, assume it may need update
:: This is a simplified check for batch-only mode
exit /b 0

:: Function to check if a setup step was completed (with Python fallback)
:check_setup_completed
set "step_name=%1"
:: Try Python-based tracking first if available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    if exist setup_tracker.py (
        python setup_tracker.py check %step_name% >nul 2>&1
        exit /b %errorlevel%
    )
)
:: Fall back to batch-only tracking
call :check_setup_completed_fallback %step_name%
exit /b %errorlevel%

:: Function to mark a setup step as completed (with Python fallback)
:mark_setup_completed
set "step_name=%1"
:: Try Python-based tracking first if available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    if exist setup_tracker.py (
        python setup_tracker.py mark %step_name% >nul 2>&1
        exit /b 0
    )
)
:: Fall back to batch-only tracking
call :mark_setup_completed_fallback %step_name%
exit /b 0

:: Function to check if a file is newer than a completed step (with Python fallback)
:check_file_newer
set "file_path=%1"
set "step_name=%2"
:: Try Python-based tracking first if available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    if exist setup_tracker.py (
        python setup_tracker.py file_newer %file_path% %step_name% >nul 2>&1
        exit /b %errorlevel%
    )
)
:: Fall back to batch-only tracking
call :check_file_newer_fallback %file_path% %step_name%
exit /b %errorlevel%

:: Main execution starts here
:main

:: Check for --force flag to skip setup tracking
set FORCE_SETUP=0
if "%1"=="--force" (
    set FORCE_SETUP=1
    echo [INFO] Force setup mode enabled - all steps will be executed.
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
    call venv\Scripts\activate >nul 2>&1
    if !errorlevel! equ 0 (
        call deactivate >nul 2>&1
        echo [INFO] Valid virtual environment found. Skipping creation.
        call :mark_setup_completed "venv_created"
        goto :skip_venv_creation
    ) else (
        echo [WARNING] Invalid virtual environment found. Recreating...
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

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    exit /b 1
)
echo [SUCCESS] Dependencies installed.
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

echo.
echo ========================================================
echo TaskHero AI setup completed successfully!
echo.
echo To start the application, run:
echo   venv\Scripts\activate
echo   python app.py
echo.
if %PYTHON_AVAILABLE% equ 1 (
    echo Setup status has been saved to .app_settings.json
) else (
    echo Setup status has been saved to .setup_*.done files
)
echo To force re-run all steps, use: setup_windows.bat --force
echo.
echo For more information, see the README.md file.
echo ========================================================
echo.

:: Offer to run the application
if %PYTHON_AVAILABLE% equ 1 (
    echo Would you like to run TaskHero AI now? (Y/N)
    set /p RUN_APP="Enter your choice (Y/N): "
    if /i "!RUN_APP!"=="Y" (
        echo.
        echo Starting TaskHero AI...
        python app.py
    )
) else (
    echo.
    echo [INFO] Please install Python and re-run this script to start TaskHero AI.
)

endlocal
