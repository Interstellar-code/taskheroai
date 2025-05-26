# TASK-080-DEV: Git Integration and Auto-Update System

## Task Information
- **Task ID**: TASK-080-DEV
- **Title**: Git Integration and Auto-Update System
- **Status**: inprogress
- **Priority**: medium
- **Created Date**: 2025-01-27
- **Due Date**: 2025-02-03
- **Assignee**: Developer
- **Task Type**: Development
- **Tags**: [git, integration, auto-update, version-control]

## Overview
Implement a Git integration and auto-update system for TaskHero AI that allows users to:
- Check for updates from the master branch of https://github.com/Interstellar-code/taskheroai
- Receive notifications when new versions are available
- Update the application while preserving user files and settings
- Manage Git integration settings through the application interface

## Requirements

### Core Functionality
1. **Version Checking**
   - Check current local version against remote master branch
   - Single version check on application startup (no continuous polling)
   - Display update notifications in home menu when available
   - Cache version check results to avoid excessive API calls

2. **Update Notifications**
   - Show update available indicator in main menu
   - Display version information (current vs. available)
   - Provide clear call-to-action for updating

3. **Git Update Process**
   - Pull latest changes from master branch
   - Preserve user files during updates:
     - Task files (theherotasks directory)
     - Settings files (app_settings.json, .env)
     - User-created content
   - Handle merge conflicts gracefully
   - Provide rollback option if update fails

4. **Settings Integration**
   - Add Git settings to existing app_settings.json (no separate git_settings.json)
   - Settings include:
     - Auto-check enabled/disabled
     - Last check timestamp
     - Update notifications enabled/disabled
     - Repository URL (default: https://github.com/Interstellar-code/taskheroai)

### User Interface Integration
1. **Home Menu Integration**
   - Add update notification banner when updates available
   - Show current version information
   - Quick access to update process

2. **Settings Menu Integration**
   - Add "Git & Updates" option to AI Settings menu (option 15)
   - Configure auto-update preferences
   - Manual version check option
   - View update history

### Technical Implementation
1. **Git Integration Manager**
   - Handle Git operations (fetch, pull, status)
   - Version comparison logic
   - File preservation during updates
   - Error handling and recovery

2. **Version Management**
   - Semantic version comparison
   - Git commit hash tracking
   - Update history logging

3. **Windows PowerShell Compatibility**
   - Ensure all Git commands work in Windows PowerShell environment
   - Handle Windows-specific path issues
   - Proper error handling for Windows Git installations

## Simplified Approach (Based on Previous Discussions)
- **Single version check on startup** (no continuous polling)
- **No rollback functionality** (keep it simple)
- **Selective updates** that preserve user files
- **Integration with existing app_settings.json** (no new config files)

## Implementation Plan

### Phase 1: Core Git Integration
1. Create GitManager class in `mods/git/git_manager.py`
2. Implement version checking functionality
3. Add Git settings to app_settings.json structure
4. Create basic update mechanism

### Phase 2: UI Integration
1. Modify MenuManager to show update notifications
2. Add Git settings to AI Settings menu
3. Create update confirmation dialogs
4. Implement progress indicators

### Phase 3: File Preservation
1. Implement user file detection and backup
2. Create selective update process
3. Add error handling and recovery
4. Test with various update scenarios

### Phase 4: Testing and Polish
1. Test in Windows PowerShell environment
2. Verify file preservation works correctly
3. Test error scenarios and recovery
4. Update documentation

## Files to Modify/Create

### New Files
- `mods/git/__init__.py`
- `mods/git/git_manager.py`
- `mods/git/version_manager.py`
- `mods/ui/git_settings_ui.py`

### Modified Files
- `app_settings.json` (add git settings structure)
- `mods/ui/menu_manager.py` (add update notifications)
- `mods/ui/ai_settings_ui.py` (add Git settings option)
- `mods/cli/cli_manager.py` (add Git settings handler)
- `mods/core/app_controller.py` (integrate Git manager)

## Settings Structure
Add to app_settings.json:
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

## Success Criteria
- [ ] Version checking works on application startup
- [ ] Update notifications appear in main menu when updates available
- [ ] Git settings accessible through AI Settings menu
- [ ] Update process preserves user files (tasks, settings, env)
- [ ] System works correctly in Windows PowerShell environment
- [ ] Error handling prevents data loss during updates
- [ ] Integration with existing app_settings.json works seamlessly

## Testing Checklist
- [ ] Test version checking with various Git states
- [ ] Verify update notifications display correctly
- [ ] Test update process with user files present
- [ ] Verify settings persistence across updates
- [ ] Test error scenarios (no Git, network issues, conflicts)
- [ ] Confirm Windows PowerShell compatibility
- [ ] Test with different repository states (ahead, behind, diverged)

## Notes
- Focus on simplicity and reliability over advanced features
- Preserve user data at all costs during updates
- Provide clear feedback during all operations
- Ensure graceful degradation when Git is not available
- Follow existing TaskHero AI architectural patterns
