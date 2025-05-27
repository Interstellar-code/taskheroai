# TaskHero AI Git Integration & Auto-Update System

## Overview

The Git Integration and Auto-Update System provides TaskHero AI with the ability to automatically check for updates, notify users of new versions, and perform safe updates while preserving user data.

## Features

### ✅ Core Functionality
- **Automatic Version Checking**: Checks for updates on startup and periodically
- **Update Notifications**: Shows update availability in the main menu
- **Safe Updates**: Preserves user files during updates with automatic backup
- **Git Integration**: Works with GitHub repositories and local Git repositories
- **Settings Management**: Integrated with existing app_settings.json

### ✅ User Interface
- **Git Settings Menu**: Accessible via AI Settings → Git & Updates (option 15)
- **Update Notifications**: Prominent display in main menu when updates are available
- **Interactive Update Process**: Step-by-step update with user confirmation
- **Status Information**: Detailed version and repository status

## Usage

### Accessing Git Settings

1. Start TaskHero AI
2. Go to Main Menu → AI Settings (option 14)
3. Select Git & Updates (option 15)

### Checking for Updates

**Automatic**: Updates are checked automatically on startup (if enabled)

**Manual**:
1. Go to Git Settings → Check for Updates Now (option 4)
2. View the update status and available versions

### Performing Updates

1. Go to Git Settings → Download & Install Updates (option 5)
2. Review the update information
3. Confirm the update when prompted
4. Wait for the update to complete
5. Restart TaskHero AI to use the new version

## Configuration

Git settings are stored in `.taskhero_setup.json`:

```json
{
  "git": {
    "auto_check_enabled": true,
    "last_check_timestamp": "2025-01-27T10:00:00",
    "notifications_enabled": true,
    "repository_url": "https://github.com/Interstellar-code/taskheroai",
    "current_version": "1.0.0",
    "last_update_timestamp": "2025-01-27T09:00:00",
    "update_history": []
  }
}
```

## Technical Implementation

### Architecture

```
mods/git/
├── __init__.py           # Module initialization
├── version_manager.py    # Version checking and comparison
└── git_manager.py        # Git operations and update management

mods/ui/
└── git_settings_ui.py    # Git settings user interface
```

### Key Features
- Single version check on startup (no continuous polling)
- Update notifications in home menu
- Git update option in settings menu
- Preservation of user files during updates
- Integration with existing app_settings.json
- Windows PowerShell compatibility
- Comprehensive error handling

## File Preservation

The system automatically preserves important user files during updates:
- `theherotasks/` - All task files
- `app_settings.json` - Application settings
- `.env` - Environment variables
- User-created files and directories
- Virtual environments and IDE files

## Safety Features

- **Pre-Update Checks**: Validates Git availability and repository state
- **Automatic Backup**: Creates timestamped backups before updates
- **Rollback Capability**: Restores from backup if update fails
- **Error Recovery**: Graceful handling of all error scenarios
