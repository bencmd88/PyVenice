# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"pyvenice" - A comprehensive Python client library for the Venice.ai API, providing a wrapper for all API endpoints with type safety, automatic validation, and convenience features.

## Key Architecture

The library implements a **decorator-based validation pattern** that requires understanding across multiple files:

1. **validators.py** defines `@validate_model_params` decorator that intercepts API calls
2. **models.py** provides model capability checking via `get_model_traits()`
3. **Endpoint modules** (chat.py, image.py, etc.) use the decorator to automatically filter unsupported parameters before API calls
4. This prevents API errors when users pass parameters like `parallel_tool_calls` to models that don't support them

## Essential Commands

```bash
# Development setup
source .venv/bin/activate      # Activate uv virtual environment
pip install -e .[dev]         # Include test dependencies

# Code quality
ruff check .                   # Run linting checks
ruff check --fix .            # Fix auto-fixable linting issues
pytest tests/ -m "not integration" --cov=pyvenice --cov-report=term-missing  # Unit tests with coverage

# Testing
pytest tests/test_chat.py -v  # Run specific test module
pytest --cov=pyvenice --cov-report=html  # Generate HTML coverage report

# Manual testing
export VENICE_API_KEY='your-api-key'
python src/simple_example.py  # Basic functionality test
python src/example_usage.py   # Comprehensive API demonstration
```

## Development Workflow

1. **Before modifying endpoints**: Check if the parameter needs validation in `validators.py`
2. **When adding new endpoints**: Follow the pattern in existing modules (e.g., chat.py) - create a class with sync/async methods
3. **For streaming endpoints**: See `chat.py` and `audio.py` for the streaming response handling pattern
4. **Testing changes**: Always run the test suite - the project maintains 82% coverage minimum

## Critical Implementation Details

### Known Issues & Workarounds

1. **Brotli Compression**: Venice.ai supports `br` encoding but httpx has decoding issues. The client only requests `gzip` compression in `client.py:59`

2. **Parameter Defaults**: Avoid default values for optional parameters (e.g., `parallel_tool_calls`) as they'll always be sent. Use `None` defaults in `chat.py:176`

3. **Compatibility Mapping**: The `/models/compatibility_mapping` endpoint returns a dict, not a list. See `models.py:170` for correct handling

### Cross-Module Dependencies

- **All endpoint modules** depend on the `@validate_model_params` decorator from `validators.py`
- **validators.py** depends on `models.py` for capability checking
- **models.py** caches are shared across all endpoint instances via the client
- **Streaming responses** in chat/audio require special handling of SSE format and chunk processing

### User soft-disabled CodeCov

- **CodeCov failing** due to lack of token no longer causes the CI/CD to fail. The user changed the setting in test.conf.
- **Investigate token** requirements before when next debugging the CI/CD pipeline.

## Robust File Modification methodology

**ALWAYS follow this 5-phase process when adding code to files to avoid loops and conflicts:**

### Phase 1: Planning & Reconnaissance
1. **Read target area** - Use `Read` tool ±10 lines around intended location
2. **Use Grep** to check if targeting strings appear multiple times  
3. **Choose insertion strategy** - End of file, before/after specific method, etc.
4. **Identify exact target location** with line numbers

### Phase 2: Tool Selection & Targeting  
1. **Select appropriate tool**:
   - `Edit` - Only when target string is unique
   - `Write` - For complete file replacement (with backup)
   - `Bash` append (`>>`) - For end-of-file additions
2. **Plan targeting string** - Must be unique with enough context
3. **Use `grep -n` to verify target string uniqueness**

### Phase 3: Pre-execution Safety
1. **Create backup**: `git stash push -m "backup before changes"`
2. **Define success criteria** - Exact line numbers, syntax check, etc.
3. **Define failure detection** - Duplicates, syntax errors, wrong location
4. **Plan one-command rollback** - `git checkout -- file` or `git stash pop`

### Phase 4: Execution & Immediate Verification
1. **Execute the change** using planned tool/targeting
2. **Immediate syntax check** - `python -c "import module"` 
3. **Immediate location check** - `grep -n "new_code_marker"` to confirm placement
4. **Check for duplicates** - `grep -c "function_name"` should be 1
5. **If ANY failure detected** - Immediately revert and restart from Phase 1

### Phase 5: Final Validation
1. **Test function import** - `from module import function`
2. **Run relevant tests** if available
3. **Commit only if all checks pass**

**Key principles:**
- ✅ Never proceed without unique targeting string
- ✅ Always verify immediately after each change  
- ✅ Always have one-command rollback ready
- ✅ Use `Read` extensively before `Edit`
- ✅ Stop and restart from Phase 1 if any verification fails
