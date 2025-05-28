@echo off
REM AI Task Creation Automation - Windows Batch Script
REM This script provides an easy way to run the AI task automation on Windows

echo TaskHero AI - Task Creation Automation
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "tests\ai_task_automation.py" (
    echo Error: Please run this script from the TaskHero AI root directory.
    echo Current directory: %CD%
    echo Expected files: tests\ai_task_automation.py
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Using system Python.
    echo Consider setting up a virtual environment for better isolation.
    echo.
)

REM Check if .env file exists
if not exist ".env" (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and configure your AI providers.
    echo.
    pause
    exit /b 1
)

echo Environment check complete.
echo.

REM Show menu
:menu
echo Select an option:
echo 1. Run Interactive Example (Recommended for first-time users)
echo 2. Run Quick Test (Single task, all providers)
echo 3. Run Full Test Suite (All test cases, all providers)
echo 4. List Configured Providers
echo 5. View Test Cases
echo 6. Check Results Directory
echo 0. Exit
echo.

set /p choice="Enter your choice (0-6): "

if "%choice%"=="1" goto interactive
if "%choice%"=="2" goto quick
if "%choice%"=="3" goto full
if "%choice%"=="4" goto providers
if "%choice%"=="5" goto testcases
if "%choice%"=="6" goto results
if "%choice%"=="0" goto exit
echo Invalid choice. Please try again.
echo.
goto menu

:interactive
echo.
echo Running Interactive Example...
python tests\run_ai_task_automation_example.py
goto end

:quick
echo.
echo Running Quick Test...
python tests\test_ai_task_creation_automation.py --quick
goto end

:full
echo.
echo Running Full Test Suite...
echo This may take several minutes...
python tests\test_ai_task_creation_automation.py --full
goto end

:providers
echo.
echo Listing Configured Providers...
python tests\test_ai_task_creation_automation.py --list-providers
goto end

:testcases
echo.
echo Viewing Test Cases...
python tests\test_ai_task_creation_automation.py --list-tests
goto end

:results
echo.
echo Checking Results Directory...
if exist "tests\ai_task_results" (
    echo Results directory exists: tests\ai_task_results
    dir /b tests\ai_task_results\*.md 2>nul | find /c /v "" > temp_count.txt
    set /p task_count=<temp_count.txt
    del temp_count.txt
    echo Generated tasks: %task_count%
) else (
    echo Results directory not found: tests\ai_task_results
    echo Run a test to generate results.
)

if exist "tests\automation_reports" (
    echo Reports directory exists: tests\automation_reports
    dir /b tests\automation_reports\*.* 2>nul | find /c /v "" > temp_count.txt
    set /p report_count=<temp_count.txt
    del temp_count.txt
    echo Generated reports: %report_count%
) else (
    echo Reports directory not found: tests\automation_reports
    echo Run a test to generate reports.
)
goto end

:end
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto menu

:exit
echo.
echo Thank you for using TaskHero AI Task Creation Automation!
echo Results and reports are saved in the tests directory.
echo.
pause
