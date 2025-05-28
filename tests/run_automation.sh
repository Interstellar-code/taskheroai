#!/bin/bash

# AI Task Creation Automation - Unix/Linux Shell Script
# This script provides an easy way to run the AI task automation on Unix/Linux systems

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to print colored output
print_colored() {
    local color=$1
    local message=$2
    printf "${color}${message}${NC}\n"
}

# Function to print section headers
print_header() {
    local title=$1
    echo ""
    print_colored $CYAN "========================================"
    print_colored $CYAN "$title"
    print_colored $CYAN "========================================"
}

# Check if we're in the right directory
check_directory() {
    if [ ! -f "tests/ai_task_automation.py" ]; then
        print_colored $RED "Error: Please run this script from the TaskHero AI root directory."
        print_colored $WHITE "Current directory: $(pwd)"
        print_colored $WHITE "Expected files: tests/ai_task_automation.py"
        exit 1
    fi
}

# Check and activate virtual environment
check_venv() {
    if [ -f "venv/bin/activate" ]; then
        print_colored $GREEN "Activating virtual environment..."
        source venv/bin/activate
    else
        print_colored $YELLOW "Warning: Virtual environment not found. Using system Python."
        print_colored $YELLOW "Consider setting up a virtual environment for better isolation."
    fi
}

# Check for .env file
check_env() {
    if [ ! -f ".env" ]; then
        print_colored $RED "Error: .env file not found!"
        print_colored $WHITE "Please copy .env.example to .env and configure your AI providers."
        exit 1
    fi
}

# Show menu
show_menu() {
    echo ""
    print_colored $CYAN "Select an option:"
    print_colored $WHITE "1. Run Interactive Example (Recommended for first-time users)"
    print_colored $WHITE "2. Run Quick Test (Single task, all providers)"
    print_colored $WHITE "3. Run Full Test Suite (All test cases, all providers)"
    print_colored $WHITE "4. List Configured Providers"
    print_colored $WHITE "5. View Test Cases"
    print_colored $WHITE "6. Check Results Directory"
    print_colored $WHITE "0. Exit"
    echo ""
}

# Run interactive example
run_interactive() {
    echo ""
    print_colored $GREEN "Running Interactive Example..."
    python tests/run_ai_task_automation_example.py
}

# Run quick test
run_quick() {
    echo ""
    print_colored $GREEN "Running Quick Test..."
    python tests/test_ai_task_creation_automation.py --quick
}

# Run full test suite
run_full() {
    echo ""
    print_colored $GREEN "Running Full Test Suite..."
    print_colored $YELLOW "This may take several minutes..."
    python tests/test_ai_task_creation_automation.py --full
}

# List providers
list_providers() {
    echo ""
    print_colored $GREEN "Listing Configured Providers..."
    python tests/test_ai_task_creation_automation.py --list-providers
}

# View test cases
view_testcases() {
    echo ""
    print_colored $GREEN "Viewing Test Cases..."
    python tests/test_ai_task_creation_automation.py --list-tests
}

# Check results
check_results() {
    echo ""
    print_colored $GREEN "Checking Results Directory..."
    
    if [ -d "tests/ai_task_results" ]; then
        task_count=$(find tests/ai_task_results -name "*.md" 2>/dev/null | wc -l)
        print_colored $GREEN "✓ Results directory exists: tests/ai_task_results"
        print_colored $WHITE "  Generated tasks: $task_count"
        
        if [ $task_count -gt 0 ]; then
            print_colored $WHITE "  Recent tasks:"
            ls -t tests/ai_task_results/*.md 2>/dev/null | head -5 | while read file; do
                print_colored $WHITE "  - $(basename "$file")"
            done
        fi
    else
        print_colored $RED "✗ Results directory not found: tests/ai_task_results"
        print_colored $WHITE "  Run a test to generate results."
    fi
    
    if [ -d "tests/automation_reports" ]; then
        report_count=$(find tests/automation_reports -type f 2>/dev/null | wc -l)
        print_colored $GREEN "✓ Reports directory exists: tests/automation_reports"
        print_colored $WHITE "  Generated reports: $report_count"
        
        if [ $report_count -gt 0 ]; then
            print_colored $WHITE "  Recent reports:"
            ls -t tests/automation_reports/* 2>/dev/null | head -3 | while read file; do
                print_colored $WHITE "  - $(basename "$file")"
            done
        fi
    else
        print_colored $RED "✗ Reports directory not found: tests/automation_reports"
        print_colored $WHITE "  Run a test to generate reports."
    fi
}

# Main function
main() {
    print_header "TaskHero AI - Task Creation Automation"
    
    # Perform checks
    check_directory
    check_venv
    check_env
    
    print_colored $GREEN "Environment check complete."
    
    # Main menu loop
    while true; do
        show_menu
        read -p "Enter your choice (0-6): " choice
        
        case $choice in
            1)
                run_interactive
                ;;
            2)
                run_quick
                ;;
            3)
                run_full
                ;;
            4)
                list_providers
                ;;
            5)
                view_testcases
                ;;
            6)
                check_results
                ;;
            0)
                echo ""
                print_colored $GREEN "Thank you for using TaskHero AI Task Creation Automation!"
                print_colored $WHITE "Results and reports are saved in the tests directory."
                echo ""
                exit 0
                ;;
            *)
                print_colored $RED "Invalid choice. Please try again."
                ;;
        esac
        
        echo ""
        print_colored $CYAN "Press Enter to return to menu..."
        read
    done
}

# Run main function
main
