# AI Task Creation Automation

This directory contains automation scripts for testing AI task creation functionality across multiple AI providers and models configured in your `.env` file.

## Overview

The automation system allows you to:
- Test task creation with all configured AI providers (OpenAI, Anthropic, Ollama, OpenRouter, DeepSeek)
- Generate comprehensive reports comparing provider performance
- Create tasks using predefined test cases or custom inputs
- Store generated tasks for analysis and comparison

## Files

### Core Scripts
- **`ai_task_automation.py`** - Main automation script with comprehensive testing
- **`test_ai_task_creation_automation.py`** - Test runner with various testing options
- **`run_ai_task_automation_example.py`** - Interactive example script with menu interface

### Templates and Configuration
- **`task_input_template.md`** - Simple task input template with metadata fields

### Generated Output (Created during execution)
- **`ai_task_results/`** - Directory containing generated task files
- **`automation_reports/`** - Directory containing analysis reports
- **`*.log`** - Log files from automation runs

## Quick Start

### 1. Prerequisites

Ensure your `.env` file is configured with at least one AI provider:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and configure your AI providers
# At minimum, configure one of the following:

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Ollama (local, no API key needed)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
```

### 2. Run the Interactive Example

The easiest way to get started:

```bash
python tests/run_ai_task_automation_example.py
```

This provides a menu-driven interface with options to:
- Run quick tests
- Test specific providers
- Create custom tasks
- View results and reports

### 3. Run Automation Scripts Directly

#### Quick Test (Single task, all providers)
```bash
python tests/test_ai_task_creation_automation.py --quick
```

#### Full Test Suite (All test cases, all providers)
```bash
python tests/test_ai_task_creation_automation.py --full
```

#### Test Specific Provider
```bash
python tests/test_ai_task_creation_automation.py --provider openai
python tests/test_ai_task_creation_automation.py --provider anthropic
python tests/test_ai_task_creation_automation.py --provider ollama
```

#### Custom Task Creation
```bash
python tests/test_ai_task_creation_automation.py --custom "My Task Title" "Detailed task description here"
```

#### List Available Options
```bash
python tests/test_ai_task_creation_automation.py --list-providers
python tests/test_ai_task_creation_automation.py --list-tests
```

## Test Cases

The automation includes several predefined test cases:

1. **User Authentication System** - Complex development task with security requirements
2. **Memory Leak Bug Fix** - Critical bug fix with performance implications
3. **API Documentation** - Documentation task with specific deliverables
4. **Automated Testing Pipeline** - Test infrastructure setup
5. **User Dashboard Design** - UI/UX design task

Each test case includes:
- Title and description
- Task type (Development, Bug Fix, Documentation, etc.)
- Priority level
- Tags and dependencies
- Effort estimates
- Acceptance criteria

## Output Structure

### Generated Tasks (`ai_task_results/`)
Each generated task is saved as a Markdown file with the naming convention:
```
{TASK_ID}_{PROVIDER}_{MODEL}.md
```

Example: `TASK-001_openai_gpt-4.md`

### Reports (`automation_reports/`)

#### Summary Report
- Overall statistics (success rates, execution times)
- Provider performance comparison
- Test case results summary

#### Detailed Report
- Complete results for each test case
- Provider-specific performance metrics
- Error details for failed tests

#### Provider Comparison
- Side-by-side provider analysis
- Performance benchmarks
- Strengths and weaknesses

#### JSON Data Export
- Raw data for further analysis
- Structured format for integration with other tools

## Customization

### Adding Custom Test Cases

Edit `ai_task_automation.py` and modify the `create_test_cases()` method:

```python
def create_test_cases(self) -> List[TaskTestCase]:
    test_cases = [
        TaskTestCase(
            title="Your Custom Task",
            description="Detailed description of what needs to be done",
            task_type="Development",  # or "Bug Fix", "Documentation", etc.
            priority="high",          # low, medium, high, critical
            tags=["custom", "feature"],
            effort_estimate="Large"   # Small, Medium, Large
        ),
        # Add more test cases...
    ]
    return test_cases
```

### Using Custom Templates

Create your own task template and use it:

```bash
# Create a custom template file
echo "# My Custom Task Template
Title: {title}
Description: {description}
..." > my_template.md

# Use the template
python tests/test_ai_task_creation_automation.py --template my_template.md
```

## Troubleshooting

### Common Issues

1. **No providers configured**
   - Check your `.env` file
   - Ensure API keys are valid and not placeholder values

2. **Ollama connection failed**
   - Make sure Ollama is running: `ollama serve`
   - Check the host URL in your `.env` file

3. **API rate limits**
   - The automation includes delays between requests
   - Consider testing with fewer providers or test cases

4. **Import errors**
   - Run from the project root directory
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

### Debugging

Enable verbose logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check the generated log files in the `tests/` directory for detailed execution information.

## Integration with TaskHero AI

The automation system integrates directly with TaskHero AI's task creation functionality:

- Uses the same `AITaskCreator` class as the main application
- Leverages the same AI provider configurations
- Generates tasks in the same format as manual creation
- Stores tasks in the standard TaskHero AI directory structure

This ensures that automated tests accurately reflect real-world usage and help identify issues before they affect users.

## Performance Considerations

- **API Costs**: Be mindful of API usage, especially with commercial providers
- **Rate Limits**: The automation includes built-in delays to respect API limits
- **Execution Time**: Full test suites can take 10-30 minutes depending on providers
- **Storage**: Generated tasks and reports can accumulate over time

## Contributing

To add new features or test cases:

1. Follow the existing code structure
2. Add appropriate error handling
3. Update documentation
4. Test with multiple providers
5. Consider backward compatibility

## License

This automation system is part of the TaskHero AI project and follows the same license terms.
