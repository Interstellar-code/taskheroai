# Task: TASK-017 - Restore Project Cleanup Manager

## Metadata
- **Created:** 2025-01-24
- **Due:** 2025-01-30
- **Priority:** Medium
- **Status:** Todo
- **Assigned to:** Developer
- **Task Type:** Development
- **Sequence:** 17
- **Tags:** cleanup, indices, reset, maintenance, restoration

## Overview
Restore the Project Cleanup Manager functionality (option 13) that allows users to delete indices, reset projects, and perform maintenance operations. The functionality was lost during CLI fixes, leaving only a placeholder implementation.

## Current Problem Analysis
CLI menu option 13 currently shows a placeholder response:
```
13. 🗑️ Project Cleanup Manager → "Project cleanup features are available but need integration."
```

**Root Cause**: During CLI fixes, the comprehensive cleanup functionality was replaced with a placeholder method that doesn't provide actual cleanup capabilities.

## Implementation Status
| Component | Status | Notes |
|-----------|--------|-------|
| Menu Display | ✅ Working | Shows Option 13 correctly |
| Cleanup Implementation | ❌ Missing | Only placeholder method exists |
| Index Cleanup | ⚠️ Partial | `FileIndexer.cleanup_index_files()` exists |
| Settings Reset | ❌ Missing | No settings cleanup implementation |
| Batch Operations | ❌ Missing | No multi-project cleanup |

## Available Cleanup Foundation

### 1. FileIndexer Cleanup (`mods/code/indexer.py`)
- **`cleanup_index_files()`** - Removes index files from index directory
- **Index directory management** - Can identify and clean `.index` directories
- **Metadata cleanup** - Removes associated metadata, embeddings, descriptions

### 2. Settings Manager
- **Directory tracking** - Knows about indexed projects
- **Configuration management** - Can reset settings

### 3. File System Operations
- **Directory deletion** - Standard file operations available
- **Path management** - Cross-platform path handling

## Detailed Description
This task will implement a comprehensive Project Cleanup Manager that provides:

1. **Individual Project Cleanup** - Delete specific project indices
2. **Batch Project Cleanup** - Delete multiple projects at once
3. **Complete Reset** - Delete all indices and reset to clean state
4. **Selective Cleanup** - Clean logs, settings, or specific components
5. **Safety Features** - Confirmations and backup options

### Core Requirements:

**1. Individual Project Cleanup**
- List all indexed projects
- Select specific project to clean
- Remove all associated index data
- Update settings to remove project reference

**2. Batch Operations**
- Select multiple projects for cleanup
- Confirm batch operation
- Process all selected projects
- Report completion status

**3. Complete System Reset**
- Delete all `.index` directories
- Clear all settings
- Reset application to initial state
- Provide strong confirmation prompts

**4. Selective Cleanup**
- Clean only logs
- Reset only settings
- Clear only specific project indices
- Granular control over cleanup scope

**5. Safety and Usability**
- Multiple confirmation prompts for destructive operations
- Clear explanations of what will be deleted
- Dry-run mode to preview operations
- Progress feedback for long operations

## Technical Implementation

### 1. ProjectCleanupManager Class
```python
class ProjectCleanupManager:
    """Manages project cleanup and reset operations."""
    
    def __init__(self, settings_manager, logger):
        self.settings_manager = settings_manager
        self.logger = logger
        
    def list_indexed_projects(self) -> List[Dict[str, Any]]:
        """List all projects with index directories."""
        
    def cleanup_project(self, project_path: str) -> bool:
        """Clean up a specific project's index data."""
        
    def cleanup_multiple_projects(self, project_paths: List[str]) -> Dict[str, bool]:
        """Clean up multiple projects."""
        
    def reset_all_projects(self) -> bool:
        """Reset everything to clean state."""
        
    def cleanup_logs_only(self) -> bool:
        """Clean up only log files."""
        
    def cleanup_settings_only(self) -> bool:
        """Reset only settings."""
```

### 2. CLI Integration
```python
def _handle_project_cleanup(self) -> None:
    """Handle project cleanup option - Enhanced implementation."""
    print(f"\n{Fore.CYAN}🗑️ Project Cleanup Manager{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    cleanup_manager = ProjectCleanupManager(self.settings_manager, self.logger)
    
    while True:
        self._show_cleanup_menu()
        choice = input(f"{Fore.GREEN}Choose cleanup option: {Style.RESET_ALL}").strip()
        
        if choice == "1":
            self._cleanup_specific_project(cleanup_manager)
        elif choice == "2":
            self._cleanup_multiple_projects(cleanup_manager)
        elif choice == "3":
            self._reset_all_projects(cleanup_manager)
        elif choice == "4":
            self._selective_cleanup(cleanup_manager)
        elif choice == "0":
            break
        else:
            print(f"{Fore.RED}Invalid option{Style.RESET_ALL}")
```

### 3. Interactive Cleanup Interface
```python
def _show_cleanup_menu(self):
    """Display cleanup options menu."""
    print(f"\n{Fore.YELLOW}Select cleanup operation:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}1.{Style.RESET_ALL} Clean specific project")
    print(f"  {Fore.CYAN}2.{Style.RESET_ALL} Clean multiple projects")
    print(f"  {Fore.RED}3.{Style.RESET_ALL} Reset ALL projects (clean slate)")
    print(f"  {Fore.CYAN}4.{Style.RESET_ALL} Selective cleanup (logs, settings)")
    print(f"  {Fore.GREEN}0.{Style.RESET_ALL} Return to main menu")
```

## Acceptance Criteria
- [ ] **Individual Project Cleanup**: Can select and clean specific project indices
- [ ] **Batch Cleanup**: Can select and clean multiple projects at once
- [ ] **Complete Reset**: Can reset entire system to clean state
- [ ] **Selective Cleanup**: Can clean logs, settings, or specific components
- [ ] **Project Discovery**: Automatically finds and lists all indexed projects
- [ ] **Safety Features**: Multiple confirmations for destructive operations
- [ ] **Progress Feedback**: Shows progress for long-running operations
- [ ] **Error Handling**: Graceful handling of permission errors and failures
- [ ] **Cross-Platform**: Works on Windows, Linux, macOS
- [ ] **Settings Update**: Updates settings after cleanup operations

## Implementation Steps

### Phase 1: Core Infrastructure (Day 1)
1. **Create ProjectCleanupManager Class**
   - Basic class structure
   - Project discovery functionality
   - Single project cleanup

2. **Integrate with CLI Manager**
   - Replace placeholder `_handle_project_cleanup()` method
   - Add cleanup menu system
   - Basic user interface

### Phase 2: Enhanced Features (Day 2)
3. **Batch Operations**
   - Multiple project selection
   - Batch cleanup processing
   - Progress tracking

4. **Complete Reset Functionality**
   - System-wide reset capability
   - Strong confirmation prompts
   - Settings and logs cleanup

### Phase 3: Advanced Features (Day 3)
5. **Selective Cleanup**
   - Granular cleanup options
   - Component-specific cleaning
   - Dry-run mode

6. **Safety and UX Enhancements**
   - Multiple confirmation levels
   - Clear operation descriptions
   - Better error messages

### Phase 4: Testing and Polish (Day 4)
7. **Cross-Platform Testing**
   - Test on Windows, Linux, macOS
   - Handle permission issues
   - Path handling verification

8. **Integration Testing**
   - Test with existing projects
   - Verify settings integration
   - Test error scenarios

## Dependencies
### Required By This Task
- Current CLI manager structure ✅
- Settings manager functionality ✅
- FileIndexer cleanup methods ✅

### Dependent On This Task
- Complete maintenance capabilities
- User ability to reset/clean projects

## Testing Strategy
- **Project Discovery Tests**: Test finding projects in various locations
- **Cleanup Tests**: Test cleaning individual and multiple projects
- **Reset Tests**: Test complete system reset functionality
- **Permission Tests**: Test handling of permission errors
- **Cross-Platform Tests**: Test on different operating systems
- **Settings Tests**: Verify settings are properly updated after cleanup

## Technical Considerations
- **File Permissions**: Handle cases where files can't be deleted
- **Concurrent Access**: Handle cases where files are in use
- **Path Handling**: Cross-platform path operations
- **Atomic Operations**: Ensure partial failures don't leave system in bad state
- **Backup Options**: Consider adding backup before cleanup
- **Performance**: Efficient handling of large directory structures

## Files to Modify
1. **`mods/cli/cli_manager.py`**
   - Replace `_handle_project_cleanup()` method
   - Add cleanup menu and user interface

2. **Create New File: `mods/core/cleanup_manager.py`**
   - ProjectCleanupManager class
   - Core cleanup functionality
   - Cross-platform operations

3. **Potentially Update**:
   - Settings manager for cleanup integration
   - File indexer for enhanced cleanup methods

## Expected Outcome
After implementation, option 13 will provide comprehensive cleanup functionality:

```
13. 🗑️ Project Cleanup Manager → Interactive cleanup interface

Cleanup Options:
1. Clean specific project     - Select and clean individual projects
2. Clean multiple projects    - Batch cleanup operations  
3. Reset ALL projects        - Complete system reset
4. Selective cleanup         - Clean logs, settings, components
0. Return to main menu       - Back to main interface
```

**Example User Flow:**
```
🗑️ Project Cleanup Manager
================================
Found 3 indexed projects:
  1. ProjectA (/path/to/projectA) - 156 files indexed
  2. ProjectB (/path/to/projectB) - 89 files indexed  
  3. ProjectC (/path/to/projectC) - 234 files indexed

Select cleanup operation:
  1. Clean specific project
  2. Clean multiple projects
  3. Reset ALL projects (clean slate)
  4. Selective cleanup (logs, settings)
  0. Return to main menu

Choose cleanup option: 1

Select project to clean:
  1. ProjectA (/path/to/projectA)
  2. ProjectB (/path/to/projectB)
  3. ProjectC (/path/to/projectC)

Choose project: 2

⚠️  WARNING: This will permanently delete all index data for ProjectB
   - .index directory will be removed
   - All embeddings and metadata will be lost
   - Project will be removed from settings

Are you sure? (y/N): y

🗑️  Cleaning ProjectB...
   ✅ Removed index directory
   ✅ Updated settings
   ✅ Cleanup completed successfully

Project ProjectB has been cleaned.
```

## Time Tracking
- **Estimated hours:** 10-12
- **Actual hours:** TBD

## References
- Existing FileIndexer cleanup methods
- Settings manager functionality
- Cross-platform file operations best practices

## Updates
- **2025-01-24:** Task created to restore Project Cleanup Manager functionality 