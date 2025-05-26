# Task: TASK-080 - Git Integration and Auto-Update System

## Metadata
- **Created:** 2025-05-26
- **Due:** 2025-06-15
- **Priority:** High
- **Status:** Todo
- **Assigned to:** Developer
- **Task Type:** Development
- **Sequence:** 80
- **Tags:** git, integration, auto-update, version-control, notifications, setup, repository

## Overview
Implement comprehensive Git integration functionality for TaskHero AI that allows users to directly clone the repository, receive update notifications, and seamlessly update their local installation when new versions are available.

## Implementation Status
| Step | Status | Notes |
|------|--------|-------|
| Git repository cloning in setup | Pending | Integrate with setup scripts |
| Version checking on app start | Pending | Check once per app launch |
| Main menu notifications | Pending | Display update availability |
| Settings menu update option | Pending | Manual update trigger |
| Selective file update system | Pending | Update code files only |

## Detailed Description
Develop a simplified Git integration system that enhances the TaskHero AI user experience by providing:

### Core Features:
1. **Repository Cloning Integration**
   - Modify setup scripts (setup_windows.ps1, setup_windows.bat, setup_linux.sh) to clone repository directly
   - Use HTTPS cloning (no authentication needed for public repo)
   - Automatic dependency installation after cloning
   - Integration with existing setup workflow

2. **Version Update Detection**
   - Check against GitHub repository on app startup only (https://github.com/Interstellar-code/taskheroai)
   - Compare local version with latest commit/release
   - Simple once-per-launch check (no periodic scheduling)
   - Graceful handling when network unavailable

3. **Main Menu Notifications**
   - Display update availability status in main menu header
   - Simple notification: "New version available" or "Up to date"
   - Non-intrusive notification system
   - Quick access to update functionality

4. **Settings Menu Integration**
   - Add "Update TaskHero AI" option in settings menu
   - View current version and latest available version
   - Manual update trigger option
   - Simple enable/disable update notifications

5. **Selective Update Mechanism**
   - Update only code-related files (.py, .md documentation, requirements.txt)
   - Preserve user files: tasks folder, app_settings.json, .env files
   - No backup/rollback needed (user data preserved)
   - Progress indication during update process

## Acceptance Criteria
- [ ] Setup scripts clone Git repository directly and continue with installation
- [ ] Version checking works on app startup (once per launch)
- [ ] Main menu displays simple update notifications
- [ ] Settings menu includes "Update TaskHero AI" option
- [ ] Update process preserves user files (tasks, settings, .env)
- [ ] Selective update only touches code files (.py, .md, requirements.txt)
- [ ] Network connectivity issues handled gracefully
- [ ] Update process includes progress indicators
- [ ] Users can download and run setup scripts directly from GitHub

## Implementation Steps

### Phase 1: Setup Script Integration (Days 1-2)
1. Modify `setup_windows.ps1` to clone repository first, then continue setup
2. Update `setup_windows.bat` with Git cloning integration
3. Enhance `setup_linux.sh` for repository cloning
4. Add Git availability checks (install if missing)
5. Test setup scripts with direct repository cloning

### Phase 2: Version Management System (Days 3-4)
1. Create `mods/git/version_manager.py` module
2. Implement simple GitHub API check for latest commit/release
3. Add local version tracking in app_settings.json
4. Check version once on app startup only
5. Handle offline mode gracefully

### Phase 3: UI Integration (Days 5-6)
1. Modify main menu to display simple update notifications
2. Add "Update TaskHero AI" option in settings menu
3. Store update preferences in app_settings.json
4. Add manual update trigger functionality

### Phase 4: Selective Update Mechanism (Days 7-8)
1. Create `mods/git/update_manager.py` module
2. Implement selective file update (code files only)
3. Preserve user files (tasks, app_settings.json, .env)
4. Implement progress tracking and user feedback

### Phase 5: Testing and Documentation (Days 9-10)
1. Test setup scripts with Git cloning on clean systems
2. Test update scenarios (successful, failed, network issues)
3. Verify user files are preserved during updates
4. Update documentation for new Git integration workflow

## Dependencies
### Required By This Task
- Git installation on user system (auto-install if missing)
- Network connectivity for version checking
- GitHub public repository access

### Dependent On This Task
- Enhanced user experience with simple updates
- Easier installation process
- Improved adoption through direct repository access

## Testing Strategy
- Test Git cloning on systems with and without Git installed
- Verify version checking with various network conditions
- Test selective update preserves user files correctly
- Cross-platform testing (Windows, Linux, macOS)
- Test setup scripts with direct repository cloning
- Simulate network failures during update process

## Technical Considerations

### Security
- Use HTTPS cloning only (no authentication needed)
- Validate repository URL matches expected GitHub repo
- Verify file integrity after updates

### Performance
- Efficient version checking without blocking UI
- Minimal network usage for version checks
- Fast selective file updates

### Compatibility
- Support for different Git versions
- Cross-platform path handling
- Handle existing installations gracefully

## Database Changes
No database changes required - uses existing file-based configuration system.

## Configuration Files
- `app_settings.json`: Add Git integration settings (version tracking, update preferences)

## Time Tracking
- **Estimated hours:** 20
- **Actual hours:** TBD

## References
- GitHub API Documentation: https://docs.github.com/en/rest
- Git Documentation: https://git-scm.com/docs
- TaskHero AI Repository: https://github.com/Interstellar-code/taskheroai

## Updates
- **2025-05-26:** Task created with simplified Git integration and auto-update specifications
- **2025-05-26:** Simplified features - removed periodic checks, rollback, authentication, separate config files
