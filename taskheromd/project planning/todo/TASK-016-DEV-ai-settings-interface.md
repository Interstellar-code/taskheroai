# TASK-016-DEV: AI Settings Interface

## Task Information
- **Task ID**: TASK-016-DEV
- **Task Type**: Development 
- **Priority**: High
- **Status**: Todo
- **Assigned To**: Development Team
- **Created Date**: 2025-01-24
- **Due Date**: TBD
- **Estimated Hours**: 10-14 hours

## Task Title
AI Settings Interface - Environment Configuration Management

## Task Description
Implement a comprehensive AI Settings interface under the "Settings and Tools" main menu that allows users to configure AI provider settings (OpenAI, Anthropic, Ollama, OpenRouter) and manage environment variables through the application interface.

## Context and Background
Currently, TaskHero AI supports multiple AI providers (OpenAI, Anthropic, Ollama, OpenRouter) but requires manual editing of environment variables. The AI chat functionality uses these ENV settings, and the indexing feature already utilizes environment configuration. This task will create a user-friendly interface for managing these settings without manual file editing.

## Current State Analysis
**Existing Infrastructure:**
- ✅ AI Provider Factory supports ENV variables (OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_HOST, etc.)
- ✅ Environment Manager base structure exists (`mods/settings/environment_manager.py`)
- ✅ Settings Manager framework in place (`mods/settings/settings_manager.py`)
- ✅ AI Chat feature reads from environment variables
- ✅ Indexing feature uses environment settings

**Missing Components:**
- ❌ AI Settings UI interface
- ❌ Environment file read/write functionality
- ❌ Settings validation and testing interface
- ❌ Integration with main menu system
- ❌ OpenRouter provider implementation

## Objectives
1. **Primary Goals:**
   - Create AI Settings submenu under "Settings and Tools"
   - Implement OpenAI settings configuration interface
   - Implement Anthropic settings configuration interface
   - Implement Ollama settings configuration interface  
   - Implement OpenRouter settings configuration interface
   - Environment file read/write functionality
   - Settings validation and API key testing

2. **Secondary Goals:**
   - Provider availability detection
   - Settings backup and restore
   - Configuration templates
   - Settings export/import functionality

## Technical Requirements

### Environment Variables to Manage
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# Anthropic Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=4000
ANTHROPIC_TEMPERATURE=0.7

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_MAX_TOKENS=4000
OLLAMA_TEMPERATURE=0.7

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4
OPENROUTER_MAX_TOKENS=4000
OPENROUTER_TEMPERATURE=0.7
OPENROUTER_HTTP_REFERER=https://your-app-name.com
OPENROUTER_X_TITLE=TaskHeroAI

# AI Chat General Settings
AI_CHAT_PROVIDER=auto
CHAT_STREAMING_ENABLED=true
```

### Menu Structure
```
Settings and Tools
├── General Settings
├── AI Settings                    ← NEW
│   ├── OpenAI Configuration      ← NEW
│   ├── Anthropic Configuration   ← NEW
│   ├── Ollama Configuration      ← NEW
│   ├── OpenRouter Configuration  ← NEW
│   ├── Test AI Connections       ← NEW
│   └── Reset to Defaults         ← NEW
├── Project Settings
└── Advanced Settings
```

## Implementation Plan

### Phase 1: Core Infrastructure (5-6 hours)
1. **Environment Manager Enhancement**
   - Implement `.env` file reading/writing
   - Add environment variable validation
   - Create backup/restore functionality

2. **AI Settings Manager**
   - Create `AISettingsManager` class
   - Implement provider configuration management
   - Add settings validation methods

3. **OpenRouter Provider Implementation**
   - Create `OpenRouterProvider` class
   - Implement OpenRouter API integration
   - Add to provider factory

### Phase 2: User Interface (4-5 hours)
1. **Menu Integration**
   - Add "AI Settings" to Settings and Tools menu
   - Create submenu navigation structure

2. **Configuration Interfaces**
   - OpenAI settings form (API key, model, parameters)
   - Anthropic settings form (API key, model, parameters)  
   - Ollama settings form (host, model, parameters)
   - OpenRouter settings form (API key, model, parameters, referer, title)

### Phase 3: Validation and Testing (3-4 hours)
1. **Connection Testing**
   - API key validation for all providers
   - Provider availability testing
   - Health check functionality

2. **Integration Testing**
   - Ensure AI chat uses updated settings
   - Verify environment file persistence
   - Test settings reload functionality

## File Structure
```
mods/
├── ai/
│   └── providers/
│       ├── openrouter_provider.py ← NEW
│       ├── provider_factory.py    ← UPDATE
│       └── __init__.py            ← UPDATE
├── settings/
│   ├── ai_settings_manager.py     ← NEW
│   ├── environment_manager.py     ← ENHANCE
│   └── __init__.py                ← UPDATE
├── ui/
│   ├── ai_settings_ui.py          ← NEW
│   └── __init__.py                ← UPDATE
└── cli/
    ├── settings_commands.py       ← ENHANCE
    └── __init__.py                ← UPDATE
```

## Key Features to Implement

### 1. AI Settings Manager (`mods/settings/ai_settings_manager.py`)
```python
class AISettingsManager:
    def get_openai_settings(self) -> Dict[str, Any]
    def set_openai_settings(self, settings: Dict[str, Any]) -> bool
    def get_anthropic_settings(self) -> Dict[str, Any]
    def set_anthropic_settings(self, settings: Dict[str, Any]) -> bool
    def get_ollama_settings(self) -> Dict[str, Any]
    def set_ollama_settings(self, settings: Dict[str, Any]) -> bool
    def get_openrouter_settings(self) -> Dict[str, Any]
    def set_openrouter_settings(self, settings: Dict[str, Any]) -> bool
    def test_provider_connection(self, provider: str) -> bool
    def get_available_providers(self) -> List[str]
    def reset_to_defaults(self, provider: str) -> bool
```

### 2. OpenRouter Provider (`mods/ai/providers/openrouter_provider.py`)
```python
class OpenRouterProvider(AIProvider):
    def __init__(self, config: Dict[str, Any])
    async def generate_response(self, prompt: str, **kwargs) -> str
    async def stream_response(self, prompt: str, **kwargs) -> AsyncIterator[str]
    async def check_health(self) -> bool
    def get_available_models(self) -> List[str]
```

### 3. Enhanced Environment Manager
```python
def read_env_file(self) -> Dict[str, str]
def write_env_file(self, variables: Dict[str, str]) -> bool
def backup_env_file(self) -> str
def restore_env_file(self, backup_path: str) -> bool
def validate_env_var(self, key: str, value: str) -> bool
```

### 4. AI Settings UI Interface
- Interactive forms for each provider (OpenAI, Anthropic, Ollama, OpenRouter)
- Real-time validation feedback
- Connection testing buttons
- Save/Cancel/Reset options
- Clear success/error messaging
- OpenRouter-specific fields (HTTP Referer, X-Title)

## OpenRouter Integration Details

### API Configuration
OpenRouter provides access to multiple AI models through a unified API:
- **API Key**: Required for authentication
- **Model Selection**: Choose from various providers (OpenAI, Anthropic, Meta, etc.)
- **HTTP Referer**: Optional for analytics
- **X-Title**: Optional app identification

### Supported Models (Examples)
```
openai/gpt-4
openai/gpt-3.5-turbo
anthropic/claude-3-sonnet
anthropic/claude-3-haiku
meta-llama/llama-2-70b-chat
google/gemini-pro
```

### Benefits
- Access to multiple AI providers through single API
- Competitive pricing
- No need for separate API keys for each provider
- Model comparison capabilities

## Acceptance Criteria
1. ✅ "AI Settings" appears in Settings and Tools menu
2. ✅ Can configure OpenAI API key and model settings
3. ✅ Can configure Anthropic API key and model settings  
4. ✅ Can configure Ollama host and model settings
5. ✅ Can configure OpenRouter API key, model, and metadata settings
6. ✅ Settings are persisted to .env file
7. ✅ AI chat feature uses updated settings immediately
8. ✅ Can test API connections from interface for all providers
9. ✅ Input validation prevents invalid configurations
10. ✅ Clear error messages for invalid settings
11. ✅ Settings can be reset to defaults for each provider
12. ✅ OpenRouter provider integrates seamlessly with existing architecture

## Testing Strategy
1. **Unit Tests**
   - Environment file read/write operations
   - Settings validation logic
   - Provider configuration management
   - OpenRouter provider functionality

2. **Integration Tests**
   - Menu navigation functionality
   - Settings persistence across sessions
   - AI chat integration with new settings
   - All four providers working correctly

3. **User Acceptance Tests**
   - Complete settings configuration workflow for all providers
   - Error handling for invalid inputs
   - Settings backup/restore functionality
   - OpenRouter model selection and testing

## Dependencies
- **Blocked By**: None
- **Blocks**: None  
- **Related To**: TASK-015 (AI Chat Integration - uses these settings)
- **Requires**: Environment file structure, AI Provider Factory, OpenRouter API integration

## Risks and Mitigation
1. **Risk**: Environment file corruption
   - **Mitigation**: Automatic backup before changes

2. **Risk**: Invalid API keys breaking functionality
   - **Mitigation**: Connection testing and validation for all providers

3. **Risk**: Settings changes not taking effect
   - **Mitigation**: Hot-reload functionality for settings

4. **Risk**: OpenRouter API rate limits or availability
   - **Mitigation**: Proper error handling and fallback mechanisms

## Success Metrics
- Users can configure AI settings for all providers without manual file editing
- 100% of AI provider settings are manageable through the interface
- Zero data loss during settings configuration
- Intuitive user experience with clear feedback
- OpenRouter integration provides seamless access to multiple models

## Notes
- Ensure backward compatibility with existing .env file structure
- Consider implementing settings encryption for API keys
- Provide clear documentation for each setting and provider
- Include helpful tooltips and examples in the interface
- OpenRouter requires HTTP Referer and X-Title for proper attribution
- Consider implementing model discovery for OpenRouter's dynamic model list

---

**Task Created**: 2025-01-24  
**Last Updated**: 2025-01-24 (Added OpenRouter support)  
**Estimated Completion**: Phase-based implementation over 10-14 hours 