# Git Stash Update Refactor

## Overview

This refactor replaces the complex backup/download/restore update mechanism with a clean, simple Git stash-based approach. The new system uses Git's built-in stash functionality to handle uncommitted changes during updates.

## Problem Solved

**Before (Old System):**
```
✗ Update failed
Error: Core TaskHero files have uncommitted changes: mods/git/git_manager.py, mods/git/version_manager.py, mods/project_management/feedback/quality_feedback.json, mods/project_management/metrics/quality_metrics.json, mods/settings/settings_manager.py (and 38 more). Please commit or stash these changes first.
Stage: pre_check
```

**After (New System):**
```
✓ Update completed successfully using git stash
Method: git_stash
Stash used: TaskHero-auto-update-20250127-143022
Stash restored: true
```

## Key Changes

### 1. New Primary Update Method: `perform_stash_update()`

**Simple 5-step process:**
1. **`git stash push`** - Save all uncommitted changes with a timestamped name
2. **`git fetch`** - Get latest changes from remote
3. **`git pull`** - Update local repository
4. **`git stash pop`** - Restore all uncommitted changes
5. **Handle conflicts** - Graceful conflict resolution if needed

### 2. Simplified Pre-Update Checks: `_pre_update_checks_stash()`

**Removed complex file categorization:**
- ❌ No more blocking on "core file" changes
- ❌ No more complex user/core file categorization
- ✅ Simple Git availability and connectivity checks
- ✅ Informational logging of uncommitted changes

### 3. Enhanced Stash Management

**New methods:**
- `_perform_stash_update()` - Main stash-based update logic
- `_restore_stash_by_name()` - Restore specific named stashes
- Improved error handling and recovery

### 4. Backward Compatibility

**Legacy methods preserved:**
- `perform_legacy_update()` - Old backup/restore method
- `_perform_git_update()` - Legacy git update logic
- `_pre_update_checks()` - Original pre-update checks

## Code Structure

```python
# New recommended approach
git_manager.perform_update(use_stash=True)  # Default
git_manager.perform_stash_update()          # Direct call

# Legacy approach (still available)
git_manager.perform_update(use_stash=False)
git_manager.perform_legacy_update()
```

## Benefits

### 🚀 **Reliability**
- Uses Git's proven stash mechanism
- No complex file copying/restoration
- Better error recovery

### 🎯 **Simplicity**
- 5 clear steps vs complex backup logic
- Fewer failure points
- Easier to debug and maintain

### 🔧 **Flexibility**
- Handles ALL file types (core, user, config)
- No more blocking on core file changes
- Graceful conflict handling

### 📊 **Better User Experience**
- Clear progress logging with ✓ indicators
- Informative error messages
- Conflict resolution guidance

## Usage Examples

### Basic Update
```python
from mods.git.git_manager import GitManager

git_manager = GitManager(settings_manager)
git_manager.initialize()

# Use new stash-based update (recommended)
result = git_manager.perform_stash_update()

if result["success"]:
    print(f"✓ Update completed: {result['message']}")
    if result["git_result"]["has_conflicts"]:
        print("⚠ Manual conflict resolution needed")
else:
    print(f"✗ Update failed: {result['error']}")
```

### Check Update Status
```python
# Check for available updates
update_check = git_manager.check_for_updates()
if update_check["update_available"]:
    print("Updates available!")
    
    # Perform update
    result = git_manager.perform_stash_update()
```

## Migration Guide

### For Existing Code

**Old way:**
```python
# This will now use git stash by default
result = git_manager.perform_update()
```

**New way (explicit):**
```python
# Explicitly use the new method
result = git_manager.perform_stash_update()
```

**Legacy fallback:**
```python
# Use old method if needed
result = git_manager.perform_legacy_update()
```

### For UI/Menu Integration

Update any UI code that calls the update functionality:

```python
# Replace complex error handling for "core file changes"
# with simple stash-based updates

try:
    result = git_manager.perform_stash_update()
    if result["success"]:
        show_success_message(result["message"])
        if result["git_result"].get("has_conflicts"):
            show_conflict_warning()
    else:
        show_error_message(result["error"])
except Exception as e:
    show_error_message(f"Update failed: {e}")
```

## Testing

Run the test script to verify functionality:

```bash
python test_git_stash_update.py
```

This will:
1. Initialize the Git manager
2. Check for updates
3. Demonstrate the new stash-based update
4. Show comparison between old and new methods

## Configuration

The new system respects existing Git settings:

```json
{
  "git": {
    "auto_check_enabled": true,
    "repository_url": "https://github.com/Interstellar-code/taskheroai",
    "notifications_enabled": true
  }
}
```

## Error Handling

### Common Scenarios

1. **No uncommitted changes**: Update proceeds normally
2. **Uncommitted changes**: Automatically stashed and restored
3. **Network issues**: Clear error messages with retry suggestions
4. **Merge conflicts**: Graceful handling with user guidance
5. **Git not available**: Clear installation instructions

### Recovery

If something goes wrong:
```bash
# Check stash list
git stash list

# Restore manually if needed
git stash pop stash@{0}

# Or apply without removing from stash
git stash apply stash@{0}
```

## Performance

**Improvements:**
- ⚡ Faster updates (no file copying)
- 💾 Less disk usage (no backup directories)
- 🔄 Atomic operations (Git handles consistency)

## Future Enhancements

Potential improvements:
1. **Interactive conflict resolution** - Guide users through conflicts
2. **Stash management UI** - View and manage stashes
3. **Update rollback** - Easy rollback to previous versions
4. **Batch updates** - Handle multiple repositories

## Conclusion

This refactor significantly improves the update experience by:
- ✅ Eliminating the "core files have uncommitted changes" error
- ✅ Simplifying the update process
- ✅ Using Git's reliable stash mechanism
- ✅ Providing better error handling and user feedback

The new `git stash` → `git pull` → `git stash pop` approach is the industry standard for handling updates with uncommitted changes, making TaskHero AI's update system more reliable and user-friendly.
