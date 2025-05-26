#!/bin/bash

#
# TaskHero AI Standalone Setup Script for Linux/macOS
#
# This script can be downloaded and run independently to:
# 1. Clone the TaskHero AI repository from GitHub
# 2. Run the complete installation and configuration process
# 3. Set up the application ready to use
#
# Usage:
#   chmod +x standalone_setup_unix.sh
#   ./standalone_setup_unix.sh [options]
#
# Options:
#   --force         Force re-installation even if TaskHero AI is already present
#   --target-dir    Directory where TaskHero AI should be installed (default: current directory)
#   --help          Show this help message
#

# Script configuration
REPO_URL="https://github.com/Interstellar-code/taskheroai.git"
PROJECT_NAME="taskheroai"
FORCE_INSTALL=false
TARGET_DIR="$(pwd)"

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
print_section_header() {
    local title=$1
    local icon=${2:-"🔧"}
    echo ""
    print_colored $CYAN "==============================================================================="
    print_colored $CYAN "$icon $title"
    print_colored $CYAN "==============================================================================="
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Git installation
check_git() {
    if command_exists git; then
        return 0
    else
        return 1
    fi
}

# Function to check Python installation
check_python() {
    if command_exists python3; then
        local version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; then
            return 0
        elif [ "$major" -gt 3 ]; then
            return 0
        fi
    fi
    return 1
}

# Function to install Git
install_git() {
    print_colored $YELLOW "Git is required but not installed."
    echo ""
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_colored $BLUE "On macOS, you can install Git using:"
        print_colored $WHITE "  brew install git"
        print_colored $WHITE "  or download from: https://git-scm.com/download/mac"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_colored $BLUE "On Linux, you can install Git using:"
        print_colored $WHITE "  Ubuntu/Debian: sudo apt install git"
        print_colored $WHITE "  CentOS/RHEL: sudo yum install git"
        print_colored $WHITE "  Fedora: sudo dnf install git"
    fi
    
    echo ""
    read -p "Press Enter after installing Git to continue, or Ctrl+C to exit..."
    
    if ! check_git; then
        print_colored $RED "Git is still not available. Please install Git and run this script again."
        exit 1
    fi
}

# Function to install Python
install_python() {
    print_colored $YELLOW "Python 3.8+ is required but not installed or not the correct version."
    echo ""
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_colored $BLUE "On macOS, you can install Python using:"
        print_colored $WHITE "  brew install python3"
        print_colored $WHITE "  or download from: https://www.python.org/downloads/"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_colored $BLUE "On Linux, you can install Python using:"
        print_colored $WHITE "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        print_colored $WHITE "  CentOS/RHEL: sudo yum install python3 python3-pip"
        print_colored $WHITE "  Fedora: sudo dnf install python3 python3-pip"
    fi
    
    echo ""
    read -p "Press Enter after installing Python 3.8+ to continue, or Ctrl+C to exit..."
    
    if ! check_python; then
        print_colored $RED "Python 3.8+ is still not available. Please install Python and run this script again."
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "TaskHero AI Standalone Setup Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --force         Force re-installation even if TaskHero AI is already present"
    echo "  --target-dir    Directory where TaskHero AI should be installed (default: current directory)"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 --force --target-dir /home/user/projects"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_INSTALL=true
            shift
            ;;
        --target-dir)
            TARGET_DIR="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_colored $RED "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set project path
PROJECT_PATH="$TARGET_DIR/$PROJECT_NAME"

# Main script execution
clear

print_section_header "TaskHero AI Standalone Setup" "🚀"
print_colored $BLUE "This script will download and set up TaskHero AI automatically."
print_colored $WHITE "Repository: $REPO_URL"
print_colored $WHITE "Target Directory: $TARGET_DIR"
print_colored $WHITE "Project Path: $PROJECT_PATH"
echo ""

# Check if project already exists
if [ -d "$PROJECT_PATH" ]; then
    if [ "$FORCE_INSTALL" = false ]; then
        print_colored $YELLOW "TaskHero AI already exists at: $PROJECT_PATH"
        read -p "Do you want to continue anyway? This will update the existing installation. (y/n): " choice
        if [[ ! "$choice" =~ ^[Yy]$ ]]; then
            print_colored $BLUE "Setup cancelled by user."
            exit 0
        fi
    fi
    print_colored $BLUE "Proceeding with existing installation..."
fi

# Step 1: Check prerequisites
print_section_header "Step 1: Checking Prerequisites" "🔍"

print_colored $BLUE "Checking Git installation..."
if ! check_git; then
    install_git
fi
print_colored $GREEN "✓ Git is installed"

print_colored $BLUE "Checking Python installation..."
if ! check_python; then
    install_python
fi
print_colored $GREEN "✓ Python 3.8+ is installed"

# Step 2: Clone or update repository
print_section_header "Step 2: Repository Setup" "📥"

if [ -d "$PROJECT_PATH" ]; then
    print_colored $BLUE "Updating existing repository..."
    cd "$PROJECT_PATH" || exit 1
    
    if git fetch origin && git pull origin master; then
        print_colored $GREEN "✓ Repository updated successfully"
    else
        print_colored $YELLOW "⚠ Repository update had issues, but continuing..."
    fi
else
    print_colored $BLUE "Cloning TaskHero AI repository..."
    cd "$TARGET_DIR" || exit 1
    
    if git clone "$REPO_URL"; then
        print_colored $GREEN "✓ Repository cloned successfully"
        cd "$PROJECT_PATH" || exit 1
    else
        print_colored $RED "✗ Failed to clone repository"
        exit 1
    fi
fi

# Step 3: Run the main setup script
print_section_header "Step 3: Running TaskHero AI Setup" "⚙️"

SETUP_SCRIPT="setup_linux.sh"
if [ -f "$SETUP_SCRIPT" ]; then
    print_colored $BLUE "Running main setup script..."
    chmod +x "$SETUP_SCRIPT"
    
    if ./"$SETUP_SCRIPT"; then
        print_colored $GREEN "✓ TaskHero AI setup completed successfully!"
    else
        print_colored $YELLOW "⚠ Setup completed with some warnings"
    fi
else
    print_colored $RED "✗ Setup script not found in the repository"
    print_colored $BLUE "Please check the repository contents and run setup manually."
    exit 1
fi

# Final message
echo ""
print_section_header "Setup Complete!" "🎉"
print_colored $GREEN "TaskHero AI has been successfully installed!"
print_colored $BLUE "Location: $PROJECT_PATH"
echo ""
print_colored $BLUE "To start TaskHero AI in the future:"
print_colored $WHITE "  cd $PROJECT_PATH"
print_colored $WHITE "  source venv/bin/activate"
print_colored $WHITE "  python app.py"
echo ""
print_colored $BLUE "The application should have started automatically..."

echo ""
read -p "Press Enter to continue..."
