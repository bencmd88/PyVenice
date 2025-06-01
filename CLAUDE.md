# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"menace" - A comprehensive Python client library for the Venice.ai API, providing a wrapper for all API endpoints with type safety, automatic validation, and convenience features.

## Project Structure

```
multiprompt/
├── menace/              # Main package directory
│   ├── __init__.py      # Package exports
│   ├── client.py        # Base client with auth and common functionality
│   ├── exceptions.py    # Custom exception classes
│   ├── validators.py    # Model capability validation
│   ├── models.py        # Models endpoint wrapper
│   ├── chat.py          # Chat completions endpoint
│   ├── image.py         # Image generation/upscaling endpoints
│   ├── embeddings.py    # Text embeddings endpoint
│   ├── audio.py         # Text-to-speech endpoint
│   ├── api_keys.py      # API key management endpoints
│   ├── characters.py    # Characters endpoint
│   └── billing.py       # Billing/usage endpoint
├── src/                 # User scripts directory
├── docs/
│   └── swagger.yaml     # Venice.ai API specification
└── main.py              # Entry point (to be updated)
```

## Key Features

1. **Automatic Model Capability Validation**: The library automatically checks model capabilities and removes unsupported parameters to prevent errors.

2. **Type Safety**: All request/response models use Pydantic for validation and type hints.

3. **Multiple Import Styles**:
   ```python
   # Full import
   import menace
   client = menace.VeniceClient(api_key="...")
   
   # Specific imports
   from menace import ChatCompletion, ImageGeneration
   ```

4. **Sync and Async Support**: All endpoints support both synchronous and asynchronous operations.

## Common Development Tasks

### Running the Project
```bash
python main.py  # Currently just prints hello
```

### Installing Dependencies
```bash
pip install -e .  # Install in development mode
```

### Using the Library
```python
from menace import VeniceClient, ChatCompletion

# Initialize client
client = VeniceClient(api_key="your-api-key")

# Create chat completion
chat = ChatCompletion(client)
response = chat.create(
    model="venice-uncensored",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## API Implementation Details

- **Authentication**: Uses Bearer token authentication via API key
- **Error Handling**: Custom exceptions for different error types (401, 402, 429, etc.)
- **Model Validation**: Automatic parameter filtering based on model capabilities
- **Compression**: Supports gzip/br compression for responses
- **Streaming**: Chat completions and audio support streaming responses

## Venice.ai Specific Features

- Web search integration in chat completions
- Character-based conversations
- Safe mode for image generation
- Venice system prompts
- VCU (Venice Credit Units) billing support

## Implementation Summary

This library was created as a comprehensive Python wrapper for the Venice.ai API, implementing all 16 endpoints found in the swagger specification:

### Core Modules Implemented

1. **Base Infrastructure**
   - `client.py`: HTTP client with authentication, retries, compression, error handling
   - `exceptions.py`: Custom exceptions for all API error codes (400, 401, 402, 415, 429, 500, 503, 504)
   - `validators.py`: Model capability validation with automatic parameter filtering

2. **API Endpoints**
   - `models.py`: `/models`, `/models/traits`, `/models/compatibility_mapping`
   - `chat.py`: `/chat/completions` with streaming and web search
   - `image.py`: `/image/generate`, `/images/generations`, `/image/styles`, `/image/upscale`
   - `embeddings.py`: `/embeddings`
   - `audio.py`: `/audio/speech` with streaming
   - `api_keys.py`: `/api_keys`, `/api_keys/rate_limits`, `/api_keys/rate_limits/log`, `/api_keys/generate_web3_key`
   - `characters.py`: `/characters`
   - `billing.py`: `/billing/usage` with pagination

### Key Design Decisions

1. **Automatic Parameter Validation**: The library checks model capabilities and automatically removes unsupported parameters (e.g., `parallel_tool_calls` for models that don't support it), preventing runtime errors.

2. **Dual Import Pattern**: Supports both `import menace` and `from menace import ChatCompletion` for flexibility.

3. **Type Safety**: All requests/responses use Pydantic models with full type hints.

4. **Caching**: Model lists and capabilities are cached to reduce API calls.

5. **Streaming Support**: Chat completions and audio endpoints support real-time streaming.

6. **Sync/Async**: Every endpoint has both synchronous and asynchronous implementations.

### Usage Example

```python
from menace import VeniceClient, ChatCompletion

client = VeniceClient()  # Uses VENICE_API_KEY env var
chat = ChatCompletion(client)

# Automatically removes unsupported params
response = chat.create(
    model="venice-uncensored",
    messages=[{"role": "user", "content": "Hello!"}],
    parallel_tool_calls=True  # Removed if model doesn't support it
)
```

## Session 2 Updates (Debugging & Fixes)

### Issues Encountered and Fixed

1. **Installation Issue**: The package wasn't importable after `pip install -e .`
   - **Fix**: Added build system configuration to `pyproject.toml`:
   ```toml
   [build-system]
   requires = ["setuptools", "wheel"]
   build-backend = "setuptools.build_meta"
   
   [tool.setuptools]
   packages = ["menace"]
   ```

2. **Encoding Error**: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc6`
   - **Cause**: Venice.ai API supports brotli compression (`br`), but httpx had issues decoding it
   - **Fix**: Limited `Accept-Encoding` header to only request `gzip` compression in `client.py`:
   ```python
   headers["Accept-Encoding"] = "gzip"  # Changed from "gzip, br"
   ```

3. **Compatibility Mapping Error**: `TypeError: string indices must be integers`
   - **Cause**: The `/models/compatibility_mapping` endpoint returns `data` as a dict, not a list
   - **Fix**: Updated `models.py` to handle dict response:
   ```python
   self._compatibility_cache = response.get("data", {})  # Was iterating as list
   ```

4. **Parameter Validation Issue**: `parallel_tool_calls is not supported by this model`
   - **Cause**: `parallel_tool_calls` had a default value of `True`, so it was always sent
   - **Fix**: Changed default to `None` in `chat.py`:
   ```python
   parallel_tool_calls: Optional[bool] = None  # Was = True
   ```

5. **Streaming Issues**: 
   - Context manager error and bytes vs string issues
   - **Fix**: Removed unnecessary context manager and fixed string handling in streaming

### Current Status

✅ All endpoints implemented and working:
- Chat completions (with automatic parameter filtering)
- Models listing and capability checking
- Image generation and upscaling
- Embeddings
- Audio/TTS
- API key management
- Characters
- Billing

✅ Key features working:
- Automatic removal of unsupported parameters based on model capabilities
- Both sync and async support
- Streaming responses
- Web search integration
- Compression handling (gzip only)

### Testing the Library

```bash
# Set your API key
export VENICE_API_KEY='your-actual-api-key'

# Test with simple example
python src/simple_example.py

# Test all features
python src/example_usage.py
```

### Important Notes

- The library requires a valid Venice.ai API key to work
- Models endpoint works without auth for listing, but chat/image generation requires valid API key
- The library automatically handles the edge case of removing parameters like `parallel_tool_calls` for models that don't support them
- Only gzip compression is used (not brotli) to avoid encoding issues