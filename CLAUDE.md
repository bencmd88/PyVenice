# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Setup Checklist

**ALWAYS verify when starting work on a new project:**
- [ ] GRIMOIRE.md symlinked: `ls -la GRIMOIRE.md` (should show symlink to ~/code/central_projections/GRIMOIRE.md)
- [ ] If missing: `ln -s ~/code/central_projections/GRIMOIRE.md ./GRIMOIRE.md`
- [ ] Remind user if symlink is missing or broken

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

## File Modification Best Practices

**Follow these 3 rules to avoid edit loops and file corruption:**

### Rule 1: Read First, Edit Second
- **Always use `Read` tool** to understand context before any `Edit`
- **Check ±10 lines** around target location for conflicts
- **Understand the structure** before making changes

### Rule 2: Verify Target Uniqueness  
- **Use `grep -n "target_string" file`** to check uniqueness before Edit
- **If multiple matches**: Use more context or different strategy
- **Tool selection**:
  - `Edit` - Only for unique targeting strings
  - `Bash` append (`>>`) - For end-of-file additions
  - `Write` - For complete file rewrites (rare)

### Rule 3: Verify Immediately After Changes
- **Syntax check**: `python -c "import module"` right after edit
- **Placement check**: `grep -n "new_code"` to confirm location  
- **Duplicate check**: `grep -c "function_name"` should equal 1
- **If ANY check fails**: `git checkout -- file` and restart

### Emergency Recovery
- **Before risky edits**: `git stash push -m "backup"`
- **If stuck in loop**: `git checkout -- file` to reset
- **Nuclear option**: `git stash pop` to restore backup

**Core insight**: 2x ceremony prevents 4x rework = 2x faster overall

**For process improvements**: Document in PROCEDURES.md immediately while solution is fresh
