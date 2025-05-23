# Task: TASK-011 - Update Branding from VerbalCodeAI to TaskHero AI

## Metadata
- **Created:** 2025-05-23
- **Due:** 2025-05-30
- **Priority:** High
- **Status:** Todo
- **Assigned to:** Developer
- **Task Type:** Documentation
- **Sequence:** 11
- **Tags:** branding, documentation, ui, interface, naming, consistency

## Overview
Update all references from "VerbalCodeAI" to "TaskHero AI" throughout the codebase, user interface, documentation, and file headers. This comprehensive branding update ensures consistent branding presentation when the application is run and removes all references to the old "VerbalCodeAI" brand.

## Implementation Status
| Step | Status | Notes |
|------|--------|-------|
| Audit existing references | ✅ Complete | Found all VerbalCodeAI references across codebase |
| Update main application file | ✅ Complete | Updated app.py with new branding |
| Update setup scripts | ✅ Complete | Updated Windows and Linux setup scripts |
| Update documentation files | 🔄 In Progress | Module docstrings updated, README files pending |
| Update file headers and comments | ✅ Complete | Updated Python module docstrings |
| Update logging and output messages | ✅ Complete | Updated user-facing messages |
| Update configuration files | Pending | Need to check other config files |
| Test branding consistency | Pending | Ready for user testing |

## Detailed Description
Perform a comprehensive branding update to replace all instances of "VerbalCodeAI" with "TaskHero AI" across the entire codebase. This includes:

### Files Requiring Updates:
1. **Main Application (app.py)**:
   - Class name `VerbalCodeAI` → `TaskHeroAI`
   - Log file names and logging references
   - Application title and descriptions
   - Terminal output and user interface text

2. **Setup Scripts**:
   - `setup_windows.bat` - Update echo messages and application name
   - `setup_linux.sh` - Update echo messages and application name

3. **Documentation Files**:
   - `README_verbalai.md` - Complete rebranding or consider renaming/removing
   - Update any references in `README.md`
   - Update documentation in `mods/` directory

4. **Python Module Files**:
   - `mods/__init__.py` - Update package docstring
   - `mods/terminal_utils.py` - Update module docstring
   - `mods/terminal_ui.py` - Update module docstring
   - Other module files with VerbalCodeAI references

5. **Configuration and Logging**:
   - Log file naming conventions
   - Logger names and identifiers
   - Error messages and user prompts

6. **User Interface Elements**:
   - Menu titles and descriptions
   - Progress messages
   - Status indicators
   - Help text and instructions

### Branding Guidelines:
- **Application Name**: "TaskHero AI" (with space and proper capitalization)
- **Class Names**: `TaskHeroAI` (CamelCase, no spaces)
- **File Names**: Keep existing file structure, update content only
- **Log Files**: Update to `taskheroai_` prefix instead of `verbalcodeai_`
- **URLs and Links**: Update any references to old repository or website URLs

## Acceptance Criteria
- [ ] All instances of "VerbalCodeAI" replaced with "TaskHero AI" in user-facing text
- [ ] Application class renamed from `VerbalCodeAI` to `TaskHeroAI`
- [ ] Setup scripts updated with new branding messages
- [ ] All module docstrings updated with new branding
- [ ] Log file naming updated to reflect new branding
- [ ] No references to "VerbalCodeAI" remain in user interface
- [ ] All documentation files updated with consistent branding
- [ ] Terminal output and messages use new branding consistently
- [ ] Configuration files and settings reflect new branding
- [ ] Application runs without any old branding references visible to users

## Implementation Steps
1. **Audit Phase**:
   - Search entire codebase for "VerbalCodeAI", "verbalcode", "verbal code" variations
   - Document all files and locations requiring updates
   - Create checklist of specific changes needed

2. **Core Application Updates**:
   - Update main `app.py` file class name and references
   - Update application title and description strings
   - Update logging configuration and log file names

3. **Setup Script Updates**:
   - Update `setup_windows.bat` echo messages and prompts
   - Update `setup_linux.sh` echo messages and prompts
   - Test setup scripts with new branding

4. **Module and Documentation Updates**:
   - Update all Python module docstrings
   - Update README files and documentation
   - Review and update any configuration files

5. **User Interface Updates**:
   - Update all menu text and user prompts
   - Update progress messages and status indicators
   - Update help text and error messages

6. **Testing and Validation**:
   - Run application and verify no old branding appears
   - Test all user interface flows
   - Verify logs use new naming convention
   - Check setup scripts work correctly

## Dependencies
### Required By This Task
- TASK-008 - Comprehensive Documentation - Todo
- TASK-010 - Create Deployment and Packaging System - Todo

### Dependent On This Task
- None (independent branding update)

## Testing Strategy
- **Visual Testing**: Run application and verify all displayed text uses "TaskHero AI"
- **Log File Testing**: Verify log files are created with new naming convention
- **Setup Testing**: Test setup scripts on clean systems with new branding
- **Documentation Review**: Verify all documentation reflects new branding
- **User Flow Testing**: Test all menu options and features for branding consistency
- **Configuration Testing**: Verify settings and configuration files work with new branding

## Technical Considerations
- **Class Renaming**: Update `VerbalCodeAI` class name while maintaining functionality
- **Import Statements**: Ensure all imports continue to work after class renaming
- **Logging Names**: Update logger names consistently throughout the application
- **File Naming**: Consider updating log file prefixes and naming conventions
- **Backward Compatibility**: Consider impact on existing user configurations
- **Case Sensitivity**: Maintain consistent capitalization throughout
- **URL References**: Update any hardcoded URLs or repository references

## Database Changes
No database changes required - this is a branding/documentation update only.

## Time Tracking
- **Estimated hours:** 6
- **Actual hours:** TBD

## References
- Current codebase structure and file organization
- Python naming conventions and best practices
- Brand identity guidelines for TaskHero AI
- User interface consistency standards

## Updates
- **2025-05-23:** Task created with comprehensive branding update requirements 