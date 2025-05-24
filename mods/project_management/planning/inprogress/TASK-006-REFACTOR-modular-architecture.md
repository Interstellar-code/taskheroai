# Task: TASK-006 - Refactor Monolithic App into Modular Architecture

## Metadata
- **Created:** 2025-01-27
- **Due:** 2025-02-10
- **Priority:** High
- **Status:** Phase 3 Complete - Ready for TASK-005 Integration
- **Assigned to:** Developer
- **Task Type:** Architecture Refactoring
- **Sequence:** 6
- **Tags:** refactoring, architecture, modular, maintainability, scalability, code-organization

## Overview
Refactor the monolithic `app.py` file (2,373 lines) into a modular architecture with focused, maintainable components. This will improve code maintainability, testability, and enable better collaboration while reducing file editing conflicts and complexity.

## Current Status & Context
- **Current Problem**: `app.py` is 2,373 lines and becoming unmanageable
- **TaskHeroAI Class**: Has too many responsibilities (20+ methods)
- **Editing Challenges**: Large file size causes conflicts and is difficult to navigate
- **Testing Issues**: Hard to test individual components in isolation
- **TASK-005**: ⏸️ **PAUSED** - Enhanced CLI Integration (resume after refactoring)

## Implementation Status| Phase | Status | Notes ||-------|--------|-------|| **Phase 1: Architecture Design** | ✅ **COMPLETE** | Modular structure designed || **Phase 1: Module Structure Planning** | ✅ **COMPLETE** | Directory structure defined || **Phase 1: Create Base Module Structure** | ✅ **COMPLETE** | Core modules, interfaces, base classes created || **Phase 2: Extract Settings Management** | ✅ **COMPLETE** | SettingsManager fully extracted (278 lines) || **Phase 2: Extract AI Features Interface** | ✅ **COMPLETE** | AIManager, ChatHandler, AgentMode created || **Phase 2: Extract Menu System** | ✅ **COMPLETE** | MenuManager and DisplayManager created || **Phase 2: Application Controller** | ✅ **COMPLETE** | Full module orchestration implemented || **Phase 3: Extract Project Management CLI** | 🔄 **IN PROGRESS** | Ready to integrate TASK-005 features || **Phase 3: Simplify Main App** | 📋 **TODO** | Move functionality from app.py to modules || **Phase 3: Integration Testing** | 📋 **TODO** | Final integration and testing |

## Proposed Modular Architecture

### **1. Main Application** (`app.py` - SIMPLIFIED ~200-300 lines)
```python
# Minimal orchestration only
class TaskHeroApp:
    def __init__(self):
        self.cli_manager = CLIManager()
        self.settings_manager = SettingsManager()
    
    def run(self):
        self.cli_manager.run()
```

### **2. CLI Management** (`mods/terminal_ui/cli_manager.py`)
```python
class CLIManager:
    def __init__(self):
        self.menu_manager = MainMenuManager()
        self.ai_interface = AICliInterface()
        self.pm_interface = ProjectManagementCLI()
        self.file_interface = FileOperationsCLI()
        
    def run(self):
        # Main application loop
        # Handle menu navigation
        # Delegate to appropriate interfaces
```

### **3. Menu System** (`mods/terminal_ui/main_menu.py`)
```python
class MainMenuManager:
    def display_menu(self):
        # Display main menu (options 1-20)
    
    def handle_menu_choice(self, choice):
        # Route to appropriate handler
```

### **4. AI Features Interface** (`mods/ai/cli_interface.py`)
```python
class AICliInterface:
    def chat_with_ai(self, max_chat_mode=False):
        # Extract from current app.py
    
    def agent_mode(self):
        # Extract from current app.py
    
    def index_directory(self, force_reindex=False):
        # Extract from current app.py
```

### **5. Enhanced Project Management CLI** (`mods/project_management/cli_interface.py`)
```python
class ProjectManagementCLI:
    def launch_kanban_board(self):
        # Enhanced CLI method from TASK-005
    
    def quick_create_task(self):
        # Enhanced CLI method from TASK-005
    
    def quick_view_tasks(self):
        # Enhanced CLI method from TASK-005
    
    def show_project_overview(self):
        # Enhanced CLI method from TASK-005
```

### **6. File Operations Interface** (`mods/code/cli_interface.py`)
```python
class FileOperationsCLI:
    def view_indexed_files(self):
        # Extract from current app.py
    
    def view_project_info(self):
        # Extract from current app.py
    
    def view_recent_projects(self):
        # Extract from current app.py
```

### **7. Settings Management** (`mods/settings/manager.py`)
```python
class SettingsManager:
    def toggle_markdown_rendering(self):
        # Extract from current app.py
    
    def toggle_thinking_blocks(self):
        # Extract from current app.py
    
    def load_settings(self):
        # Extract from current app.py
```

## Detailed Implementation Steps

### **Phase 1: Create Module Structure**
1. Create new directories (`mods/ai/`, `mods/settings/`)
2. Create base interface files with proper imports
3. Set up module `__init__.py` files
4. Define common base classes and interfaces

### **Phase 2: Extract Project Management CLI**
1. Create `mods/project_management/cli_interface.py`
2. Move enhanced CLI methods from TASK-005 implementation
3. Integrate with existing project management components
4. Test PM functionality independently

### **Phase 3: Extract AI Features Interface**
1. Create `mods/ai/cli_interface.py`
2. Move `chat_with_ai()`, `agent_mode()`, `index_directory()` methods
3. Ensure proper state management and initialization
4. Test AI functionality independently

### **Phase 4: Extract Menu System**
1. Create `mods/terminal_ui/main_menu.py`
2. Move `display_menu()` and menu routing logic
3. Create centralized menu option management
4. Test menu navigation and routing

### **Phase 5: Extract Settings & File Operations**
1. Create `mods/settings/manager.py`
2. Move settings toggle methods and configuration management
3. Create `mods/code/cli_interface.py` for file operations
4. Move file viewing and project management methods

### **Phase 6: Create CLI Manager**
1. Create `mods/terminal_ui/cli_manager.py`
2. Implement centralized coordination between all interfaces
3. Handle shared state and dependency injection
4. Manage application lifecycle

### **Phase 7: Simplify Main App**
1. Reduce `app.py` to minimal orchestration (200-300 lines)
2. Remove extracted methods and classes
3. Wire up all modules through CLIManager
4. Maintain command-line argument handling

### **Phase 8: Integration Testing**
1. Test all individual modules independently
2. Test module integration through CLIManager
3. Verify all existing functionality preserved
4. Test on Windows PowerShell environment

## Acceptance Criteria
- [ ] **`app.py` reduced to 200-300 lines** (orchestration only)
- [ ] **All functionality preserved** - no feature regressions
- [ ] **Modular structure implemented** - focused single-responsibility modules
- [ ] **Independent testability** - each module can be tested separately
- [ ] **Clean imports and dependencies** - proper module organization
- [ ] **Enhanced CLI methods integrated** - TASK-005 features included
- [ ] **Performance maintained** - no significant performance degradation
- [ ] **Documentation updated** - module documentation and imports
- [ ] **Error handling preserved** - consistent error handling patterns
- [ ] **Cross-platform compatibility** - Windows PowerShell compatibility maintained

## Technical Implementation Notes

### **File Size Targets:**
- `app.py`: ~200-300 lines (orchestration only)
- Each interface module: ~300-500 lines max
- Menu manager: ~200-300 lines
- Settings manager: ~150-200 lines
- CLI manager: ~400-500 lines

### **Key Extraction Points:**
1. **Menu Display & Routing** - Lines ~250-320 in current app.py
2. **AI Features** - Lines ~800-1500 (chat, agent, indexing methods)
3. **File Operations** - Lines ~1500-1800 (view methods)
4. **Settings Management** - Lines ~2200-2373 (toggle methods)
5. **Enhanced PM Features** - From TASK-005 implementation

### **Dependencies to Maintain:**
- ✅ **Existing mods structure** - Build on current organization
- ✅ **Project management components** - Integrate with existing modules
- ✅ **Terminal UI utilities** - Leverage existing display functions
- ✅ **Code analysis components** - Maintain indexer/analyzer integration

## Benefits
- **Maintainability**: Smaller, focused modules easier to understand and modify
- **Testability**: Each component can be tested independently
- **Collaboration**: Multiple developers can work on different modules simultaneously
- **Debugging**: Easier to locate and fix issues in specific modules
- **Extension**: Easier to add new features without affecting existing code
- **File Management**: Avoid large file editing conflicts and limitations

## Risk Mitigation Strategies- **Incremental Approach**: Extract one module at a time, test before proceeding- **Backup Safety**: Keep `app_backup.py` as rollback option- **Feature Parity**: Verify all functionality works after each extraction---## 🎉 LATEST UPDATE: Phase 2 Complete!**Date**: May 24, 2025### Phase 2 Achievements:✅ **AI Module Architecture**: AIManager, ChatHandler, AgentMode fully implemented  ✅ **UI Module Architecture**: MenuManager, DisplayManager with complete functionality  ✅ **Integration Testing**: All modules working together seamlessly  ✅ **Dependency Injection**: Clean module communication established  ✅ **Settings Integration**: Centralized configuration management working  ### Test Results:```🧪 Testing TaskHero AI Modular Architecture...✅ All modular architecture tests passed!✅ Settings Manager: Initialized✅ AI Manager: Initialized  ✅ UI Manager: Initialized```### Next: Phase 3 - Actual Code ExtractionReady to extract ~1800+ lines from monolithic app.py into modules and complete the refactoring.
- **State Management**: Carefully handle shared state between modules
- **Import Management**: Avoid circular dependencies and maintain clean imports

## Dependencies
### Required By This Task
- ✅ **TASK-005 Methods**: Enhanced CLI methods already implemented
- ✅ **Existing Architecture**: Current modular structure in `mods/`
- ✅ **Working App**: Current app.py as extraction source

### Dependent On This Task
- 🔄 **TASK-005**: Enhanced CLI Integration (resume after refactoring)
- 📋 **Future Tasks**: All future development will benefit from modular structure

## Testing Strategy
- **Unit Testing**: Test each extracted module independently
- **Integration Testing**: Test module interactions through CLIManager
- **Regression Testing**: Verify all existing features work unchanged
- **Performance Testing**: Ensure no significant performance impact
- **Cross-platform Testing**: Verify Windows PowerShell compatibility

## Time Tracking
- **Estimated hours:** 12-16 hours
  - Phase 1: 2 hours (Module structure)
  - Phase 2: 2 hours (PM CLI extraction)
  - Phase 3: 3 hours (AI features extraction)
  - Phase 4: 2 hours (Menu system)
  - Phase 5: 2 hours (Settings & file ops)
  - Phase 6: 2 hours (CLI manager)
  - Phase 7: 1 hour (Simplify main app)
  - Phase 8: 2-4 hours (Integration testing)
- **Actual hours:** TBD

## Next Session Goals
1. **Create Module Structure** (Phase 1): Set up directories and base files
2. **Extract PM CLI** (Phase 2): Create project management CLI interface
3. **Test PM Integration**: Verify project management features work independently
4. **Plan AI Extraction**: Analyze AI feature dependencies for next phase

**Estimated Time for Next Session: 3-4 hours**

## Updates
- **2025-01-27:** Task created based on refactoring plan analysis
- **2025-01-27:** Status set to "In Progress" - prioritizing modular architecture
- **2025-01-27:** TASK-005 paused to address architectural concerns first 