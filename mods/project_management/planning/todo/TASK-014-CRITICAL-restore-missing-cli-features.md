# Task: TASK-014 - CRITICAL: Restore Missing CLI Features

## Metadata
- **Created:** 2025-01-28
- **Due:** 2025-01-28
- **Priority:** CRITICAL
- **Status:** Ready to Start
- **Assigned to:** Developer
- **Task Type:** Bug Fix / Feature Migration
- **Sequence:** 14
- **Tags:** critical, cli, features, migration, bug-fix, missing-functionality

## Overview
**CRITICAL ISSUE DISCOVERED**: During TASK-005 testing, discovered that essential CLI features (Options 2-7) are showing placeholder "will be implemented in next phase" messages instead of working functionality. These features **DO EXIST** in the original `temp_app.py` but were **NOT migrated** to the modular architecture.

This is a critical missing functionality issue that needs immediate resolution.

## Problem Statement
### **Missing Features (Currently Non-Functional):**
1. **Option 2**: 📁 View Indexed Files - Shows placeholder
2. **Option 3**: 📊 View Project Info - Shows placeholder  
3. **Option 4**: 🕒 Recent Projects - Shows placeholder
4. **Option 5**: 💬 Chat with AI - Says "AI Manager not available"
5. **Option 6**: 🚀 Max Chat Mode - Says "AI Manager not available"
6. **Option 7**: 🤖 Agent Mode - Says "AI Manager not available"

### **Root Cause:**
These features exist and are fully functional in `temp_app.py` but were not migrated to the modular `mods/cli/cli_manager.py` during the architectural transition.

## Investigation Results

### **Features Found in Original temp_app.py:**
| Feature | Original Method | Line Range | Status |
|---------|----------------|------------|--------|
| View Indexed Files | `view_indexed_files()` | 916-1000+ | ✅ Fully implemented |
| View Project Info | `view_project_info()` | 1004-1180+ | ✅ Fully implemented |
| Recent Projects | `view_recent_projects()` | 1237-1300+ | ✅ Fully implemented |
| Chat with AI | `chat_with_ai()` | 774-890+ | ✅ Fully implemented |
| Agent Mode | `agent_mode()` | 719-773 | ✅ Fully implemented |

### **Current Status in Modular App:**
| Feature | Current Implementation | Status |
|---------|----------------------|--------|
| View Indexed Files | Placeholder message | ❌ **MISSING** |
| View Project Info | Placeholder message | ❌ **MISSING** |
| Recent Projects | Placeholder message | ❌ **MISSING** |
| Chat with AI | "AI Manager not available" | ❌ **MISSING** |
| Max Chat Mode | "AI Manager not available" | ❌ **MISSING** |
| Agent Mode | "AI Manager not available" | ❌ **MISSING** |

## Impact Assessment

### **Severity: CRITICAL**
- **User Experience**: Major features appear broken/incomplete
- **Functionality Loss**: Core AI and project viewing features unavailable
- **Application Value**: Significantly reduced without these features
- **User Trust**: Users may think application is incomplete/buggy

### **Affected Users:**
- **All Users**: Who want to view indexed files and project information
- **AI Users**: Who want to chat with AI or use agent mode
- **Project Managers**: Who want to see recent projects

## Implementation Plan

### **Phase 1: Assessment & Dependencies (30 minutes)**
1. **Identify Missing Dependencies**: What managers/modules need to be injected
2. **Map Original Functionality**: Document what each feature does
3. **Plan Integration Strategy**: How to adapt to modular architecture

### **Phase 2: Core Feature Migration (2-3 hours)**
1. **View Indexed Files**: Migrate `view_indexed_files()` functionality
2. **View Project Info**: Migrate `view_project_info()` functionality  
3. **Recent Projects**: Migrate `view_recent_projects()` functionality
4. **Settings Integration**: Ensure proper settings manager integration

### **Phase 3: AI Features Integration (1-2 hours)**
1. **AI Manager Injection**: Ensure AI manager is properly injected
2. **Chat with AI**: Restore `chat_with_ai()` functionality
3. **Agent Mode**: Restore `agent_mode()` functionality
4. **Error Handling**: Proper fallbacks when AI not available

### **Phase 4: Testing & Validation (30 minutes)**
1. **Feature Testing**: Verify all options work correctly
2. **Integration Testing**: Ensure no regression in existing features
3. **User Experience**: Verify smooth navigation and error handling

## Technical Implementation Details

### **Files to Modify:**
1. **`mods/cli/cli_manager.py`** - Replace placeholder methods with real implementations
2. **`app.py`** - Ensure proper dependency injection for AI manager
3. **Module imports** - Add any missing imports for functionality

### **Dependencies Required:**
- **AI Manager**: For chat and agent mode functionality
- **Project Analyzer**: For project info analysis
- **File Indexer**: For viewing indexed files
- **Settings Manager**: For recent projects management

### **Key Methods to Migrate:**
```python
# From temp_app.py - need to adapt these:
def view_indexed_files(self) -> None         # Lines 916-1000+
def view_project_info(self) -> None          # Lines 1004-1180+  
def view_recent_projects(self) -> None       # Lines 1237-1300+
def chat_with_ai(self, max_chat_mode: bool)  # Lines 774-890+
async def agent_mode(self) -> None           # Lines 719-773
```

## Acceptance Criteria
- [ ] **Option 2 (View Indexed Files)**: Shows detailed index information, file structure, sample files
- [ ] **Option 3 (View Project Info)**: Shows project analysis, structure, metadata
- [ ] **Option 4 (Recent Projects)**: Shows and allows switching between recent projects
- [ ] **Option 5 (Chat with AI)**: Functional AI chat interface
- [ ] **Option 6 (Max Chat Mode)**: Enhanced AI chat with full content
- [ ] **Option 7 (Agent Mode)**: Functional AI agent mode
- [ ] **Error Handling**: Graceful degradation when dependencies unavailable
- [ ] **Integration**: All features work seamlessly in modular architecture
- [ ] **No Regression**: Existing working features (1, 8-13) remain functional

## Priority Justification
**CRITICAL Priority** because:
1. **Major functionality missing** that users expect to work
2. **Poor user experience** with placeholder messages
3. **Reduces application value** significantly
4. **Simple migration** from existing working code
5. **Should be quick to fix** with proper implementation

## Dependencies
### Required By This Task
- None (standalone critical fix)

### Dependent On This Task
- User satisfaction and application completeness
- Future feature development requiring these base features

## Testing Strategy
- **Feature Testing**: Each option works as expected
- **Integration Testing**: No conflicts with existing features
- **Error Testing**: Graceful handling when dependencies missing
- **User Flow Testing**: Smooth navigation between all menu options

## Time Estimate
- **Total**: 4-6 hours
- **Phase 1**: 30 minutes (assessment)
- **Phase 2**: 2-3 hours (core features)
- **Phase 3**: 1-2 hours (AI features)
- **Phase 4**: 30 minutes (testing)

## Notes
- **High ROI**: Significant value gain for relatively small implementation effort
- **Code Exists**: Not new development, just proper migration
- **User Impact**: Will immediately improve user experience
- **Foundation**: Required for application to be considered "complete"

## Updates
- **2025-01-28**: Task created after discovering missing functionality during TASK-005 testing 