# Task: TASK-015 - Implement Real AI Chat Integration

## Metadata
- **Created:** 2025-01-24
- **Due:** 2025-01-31
- **Priority:** High
- **Status:** Todo
- **Assigned to:** Developer
- **Task Type:** Development
- **Sequence:** 15
- **Tags:** ai-integration, chat, openai, anthropic, ollama, real-time

## Overview
Implement actual AI chat functionality to replace placeholder responses in the chat system. This task will integrate real AI providers (OpenAI, Anthropic, Ollama) with the existing ChatHandler architecture to provide meaningful, context-aware responses about the user's codebase.

## Implementation Status
| Component | Status | Notes |
|-----------|--------|-------|
| AI Provider Integration | Pending | OpenAI, Anthropic, Ollama APIs |
| Context Injection System | Pending | Codebase context for AI responses |
| Chat Response Engine | Pending | Replace placeholder responses |
| Streaming Support | Pending | Real-time response streaming |
| Error Handling | Pending | API failures and fallbacks |
| Token Management | Pending | Cost optimization and limits |
| Conversation Memory | Pending | Maintain chat context |
| File Analysis Integration | Pending | Deep code understanding |

## Detailed Description
The current chat system shows placeholder responses: "This is a placeholder response. Full chat functionality will be implemented in the next phase." This task will implement actual AI integration to provide meaningful, intelligent responses about the user's codebase.

### Core Requirements:

**1. AI Provider Integration**
- Connect to OpenAI GPT models (gpt-4, gpt-3.5-turbo)
- Integrate Anthropic Claude models (claude-3-sonnet, claude-3-haiku)
- Support local Ollama models for offline usage
- Dynamic provider switching based on .env configuration

**2. Context-Aware Responses**
- Inject relevant codebase context based on user queries
- Use existing file indexing and embeddings from `.index/` folder
- Provide specific code examples and explanations
- Reference actual project files and structure

**3. Intelligent Query Processing**
- Understand code-related questions and provide technical answers
- Support various query types: architecture, debugging, explanations
- Provide actionable insights and suggestions
- Reference specific files, functions, and code patterns

**4. Enhanced Chat Features**
- Conversation memory to maintain context across questions
- Streaming responses for better user experience
- Token usage optimization and cost management
- Graceful fallbacks when AI services are unavailable

## Current Architecture Analysis

### Existing Components (Working):
- `AIManager.chat_with_ai()` - Interactive chat loop ✅
- `ChatHandler` class structure ✅
- Menu integration (Options 5, 6, 7) ✅
- Error handling framework ✅

### Missing Implementation (This Task):
- `ChatHandler.process_query()` - Returns only placeholder text ❌
- AI provider connections ❌
- Codebase context injection ❌
- Real AI model integration ❌

## Technical Implementation

### 1. AI Provider Classes
```python
class AIProvider:
    """Base class for AI providers"""
    async def generate_response(self, prompt: str, context: str) -> str
    
class OpenAIProvider(AIProvider):
    """OpenAI GPT integration"""
    
class AnthropicProvider(AIProvider):
    """Anthropic Claude integration"""
    
class OllamaProvider(AIProvider):
    """Local Ollama integration"""
```

### 2. Enhanced ChatHandler
```python
class ChatHandler(BaseComponent):
    def __init__(self, indexer, file_selector, project_info):
        self.ai_provider = self._get_ai_provider()
        self.context_manager = CodebaseContextManager(indexer, file_selector)
        
    async def process_query(self, query: str, max_chat_mode: bool = False) -> Tuple[str, List[str]]:
        # 1. Extract relevant codebase context
        context = await self.context_manager.get_relevant_context(query)
        
        # 2. Build AI prompt with context
        prompt = self._build_contextual_prompt(query, context, max_chat_mode)
        
        # 3. Get AI response
        response = await self.ai_provider.generate_response(prompt)
        
        # 4. Process and format response
        return self._format_response(response, context.relevant_files)
```

### 3. Context Management
```python
class CodebaseContextManager:
    """Manages codebase context for AI responses"""
    
    async def get_relevant_context(self, query: str) -> CodebaseContext:
        # Use existing indexer to find relevant files
        # Extract code snippets and documentation
        # Prepare context for AI consumption
```

## Acceptance Criteria
- [ ] **Real AI Responses**: ChatHandler returns actual AI-generated responses, not placeholders
- [ ] **Provider Support**: OpenAI, Anthropic, and Ollama integration working
- [ ] **Context Injection**: AI responses include relevant codebase context and examples
- [ ] **Query Understanding**: AI correctly interprets code-related questions
- [ ] **File References**: AI can reference specific project files and code snippets
- [ ] **Conversation Memory**: Chat maintains context across multiple questions
- [ ] **Streaming Support**: Real-time response streaming for better UX
- [ ] **Error Handling**: Graceful fallbacks when AI services fail
- [ ] **Token Management**: Cost optimization and usage tracking
- [ ] **Configuration**: Easy provider switching via .env settings
- [ ] **Max Chat Mode**: Enhanced mode with full file content injection
- [ ] **Agent Mode**: Advanced mode with tool access for deep analysis

## Implementation Steps

### Phase 1: Core AI Integration (Days 1-2)
1. **Create AI Provider Classes**
   - Implement OpenAI, Anthropic, Ollama providers
   - Add configuration loading from .env
   - Build provider factory and selection logic

2. **Update ChatHandler**
   - Replace placeholder `process_query()` method
   - Add AI provider integration
   - Implement basic response generation

### Phase 2: Context Enhancement (Days 3-4)
3. **Build Context Manager**
   - Create `CodebaseContextManager` class
   - Integrate with existing indexer and embeddings
   - Implement relevance scoring and context selection

4. **Enhanced Prompting**
   - Design effective prompts for code understanding
   - Add context injection strategies
   - Implement max chat mode with full file content

### Phase 3: Advanced Features (Days 5-6)
5. **Conversation Memory**
   - Add chat history management
   - Implement context persistence across queries
   - Optimize memory usage and relevance

6. **Streaming and UX**
   - Add streaming response support
   - Implement token usage tracking
   - Add response formatting and presentation

### Phase 4: Testing and Optimization (Day 7)
7. **Integration Testing**
   - Test with all AI providers
   - Validate context injection accuracy
   - Test error handling and fallbacks

8. **Performance Optimization**
   - Optimize context selection algorithms
   - Add caching for repeated queries
   - Monitor and optimize token usage

## Dependencies
### Required By This Task
- TASK-012 - TaskHero AI Engine Module - Complete ✅
- TASK-014 - Restore CLI Features - Complete ✅
- Existing indexer and embedding system ✅

### Dependent On This Task
- Enhanced user experience for AI chat features
- Full utilization of TaskHero AI capabilities

## Testing Strategy
- **Unit Tests**: Test each AI provider individually
- **Integration Tests**: Test ChatHandler with real AI responses
- **Context Tests**: Verify relevant codebase context injection
- **Error Tests**: Test fallbacks and error handling
- **Performance Tests**: Monitor response times and token usage
- **User Experience Tests**: Test conversation flow and memory
- **Provider Tests**: Test switching between different AI providers

## Technical Considerations
- **API Rate Limits**: Implement proper rate limiting and retries
- **Token Costs**: Monitor and optimize token usage for cost control
- **Response Quality**: Ensure AI responses are helpful and accurate
- **Security**: Protect API keys and user data
- **Performance**: Balance context richness with response speed
- **Fallbacks**: Graceful degradation when AI services unavailable
- **Scalability**: Design for multiple concurrent chat sessions

## Configuration Requirements
### .env Variables Needed:
```env
# AI Provider Selection
AI_CHAT_PROVIDER=openai  # openai, anthropic, ollama

# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000

# Anthropic Configuration
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=4000

# Ollama Configuration (for local models)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Chat Settings
CHAT_MAX_CONTEXT_FILES=10
CHAT_MAX_CONTEXT_TOKENS=8000
CHAT_STREAMING_ENABLED=true
```

## Database Changes
No database changes required - using existing file-based indexing system.

## Time Tracking
- **Estimated hours:** 20-25
- **Actual hours:** TBD

## References
- OpenAI API Documentation: https://platform.openai.com/docs
- Anthropic Claude API: https://docs.anthropic.com/
- Ollama Documentation: https://ollama.ai/
- Existing TaskHero indexer and embedding system
- TASK-012 AI Engine architecture

## Success Metrics
- **Functional**: All 3 chat options (5, 6, 7) work with real AI responses
- **Quality**: AI provides relevant, helpful answers about the codebase
- **Performance**: Response times under 5 seconds for standard queries
- **Reliability**: 99%+ uptime with proper error handling
- **User Experience**: Smooth conversation flow with context retention

## Updates
- **2025-01-24:** Task created with comprehensive AI chat integration requirements 