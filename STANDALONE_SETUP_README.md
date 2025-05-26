# TaskHero AI Standalone Setup Scripts

These standalone setup scripts allow you to download and install TaskHero AI in any folder without manually cloning the repository first.

## 🚀 Quick Start

### Windows (PowerShell)

1. **Download the script:**
   ```powershell
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Interstellar-code/taskheroai/master/standalone_setup_windows.ps1" -OutFile "standalone_setup_windows.ps1"
   ```

2. **Run the script:**
   ```powershell
   .\standalone_setup_windows.ps1
   ```

### Linux/macOS (Bash)

1. **Download the script:**
   ```bash
   curl -O https://raw.githubusercontent.com/Interstellar-code/taskheroai/master/standalone_setup_unix.sh
   ```

2. **Make it executable and run:**
   ```bash
   chmod +x standalone_setup_unix.sh
   ./standalone_setup_unix.sh
   ```

## 📋 What These Scripts Do

1. **Check Prerequisites**: Verify Git and Python 3.8+ are installed
2. **Clone Repository**: Automatically clone the TaskHero AI repository from GitHub
3. **Run Setup**: Execute the main installation and configuration process
4. **Configure Application**: Set up virtual environment, dependencies, and settings
5. **Launch Application**: Start TaskHero AI automatically after setup

## ⚙️ Script Options

### Windows PowerShell Script

```powershell
# Basic usage
.\standalone_setup_windows.ps1

# Force reinstallation
.\standalone_setup_windows.ps1 -Force

# Install in specific directory
.\standalone_setup_windows.ps1 -TargetDir "C:\MyProjects"

# Combine options
.\standalone_setup_windows.ps1 -Force -TargetDir "C:\MyProjects"
```

### Linux/macOS Bash Script

```bash
# Basic usage
./standalone_setup_unix.sh

# Force reinstallation
./standalone_setup_unix.sh --force

# Install in specific directory
./standalone_setup_unix.sh --target-dir /home/user/projects

# Combine options
./standalone_setup_unix.sh --force --target-dir /home/user/projects

# Show help
./standalone_setup_unix.sh --help
```

## 🔧 Prerequisites

The scripts will check for and guide you to install:

- **Git**: Required for cloning the repository
- **Python 3.8+**: Required for running TaskHero AI

If these are not installed, the scripts will:
- Detect the missing prerequisites
- Provide installation instructions for your platform
- Offer to open download pages (Windows)
- Wait for you to install them before continuing

## 📁 Installation Behavior

### New Installation
- Creates a new `taskheroai` folder in your chosen directory
- Clones the repository
- Runs the complete setup process

### Existing Installation
- Detects existing TaskHero AI installation
- Asks for confirmation before proceeding
- Updates the repository with latest changes
- Re-runs setup to ensure everything is current

## 🎯 Use Cases

### 1. **Project Integration**
Run the script inside an existing project folder to integrate TaskHero AI:
```bash
cd /path/to/my/existing/project
./standalone_setup_unix.sh
# Creates: /path/to/my/existing/project/taskheroai/
```

### 2. **Central Installation**
Install TaskHero AI in a dedicated location for multiple projects:
```bash
./standalone_setup_unix.sh --target-dir /opt/tools
# Creates: /opt/tools/taskheroai/
```

### 3. **Development Setup**
Quickly set up TaskHero AI for development or testing:
```bash
./standalone_setup_unix.sh --target-dir ~/development --force
# Creates: ~/development/taskheroai/
```

## 🔄 Git Integration

After installation, TaskHero AI includes built-in Git integration:

- **Automatic Updates**: Check for updates on startup
- **Update Notifications**: See notifications in the main menu when updates are available
- **One-Click Updates**: Update through AI Settings → Git & Updates (option 14 → 15)
- **File Preservation**: Your tasks, settings, and configurations are preserved during updates

## 🆘 Troubleshooting

### Script Won't Run (Windows)
If you get execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\standalone_setup_windows.ps1
```

### Permission Denied (Linux/macOS)
Make sure the script is executable:
```bash
chmod +x standalone_setup_unix.sh
./standalone_setup_unix.sh
```

### Git/Python Not Found
The scripts will guide you through installing missing prerequisites. Follow the platform-specific instructions provided.

### Repository Clone Fails
- Check your internet connection
- Verify you can access GitHub
- Try running the script again (it will retry the clone)

## 📞 Support

If you encounter issues:

1. **Check Prerequisites**: Ensure Git and Python 3.8+ are properly installed
2. **Run with Force**: Try using the `--force` or `-Force` option
3. **Manual Fallback**: If the script fails, you can still use the manual process:
   ```bash
   git clone https://github.com/Interstellar-code/taskheroai.git
   cd taskheroai
   ./setup_linux.sh  # or setup_windows.bat on Windows
   ```

## 🔗 Links

- **Repository**: https://github.com/Interstellar-code/taskheroai
- **Issues**: https://github.com/Interstellar-code/taskheroai/issues
- **Documentation**: See README.md in the installed repository
