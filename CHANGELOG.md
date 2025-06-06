# Changelog

All notable changes to PyVenice will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-06

### Added
- Initial beta release of PyVenice
- Complete implementation of all 16 Venice.ai API endpoints
- Automatic parameter validation based on model capabilities
- Full type safety with Pydantic models
- Both synchronous and asynchronous client support
- Streaming support for chat completions and audio endpoints
- Comprehensive test suite with 82% coverage
- Support for web search in chat completions
- Image generation with multiple models and styles
- Text-to-speech with streaming audio
- Embeddings generation
- API key management endpoints
- Character-based interactions
- Billing and usage tracking

### Security
- HTTPS-only communication with certificate verification
- API key protection (never logged or exposed)
- Input validation to prevent injection attacks
- Minimal, audited dependencies

[Unreleased]: https://github.com/TheLustriVA/PyVenice/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/TheLustriVA/PyVenice/releases/tag/v0.1.0