# Installation Troubleshooting Guide

This guide helps resolve common installation issues with PyVenice, particularly on ARM64 devices and specialized environments.

## ARM64 Android/Termux Issues

### Problem: "can't find Rust compiler" Error

**Symptoms:**
- Error mentions `pydantic-core` build failure
- Message contains "error: can't find Rust compiler"
- Occurs during `pip install pyvenice` on Android/Termux

**Solution 1: Install Build Dependencies (Recommended)**

```bash
# Update Termux packages
pkg update && pkg upgrade

# Install required build tools
pkg install wget rust binutils

# Upgrade pip to latest version
pip install --upgrade pip

# Now install PyVenice
pip install pyvenice
```

**Solution 2: Use Rustup (If Solution 1 Fails)**

```bash
# Install rustup for proper Rust toolchain
pkg install rustup
rustup-init

# Restart your shell, then try:
pip install pyvenice
```

**Solution 3: Force Wheel Installation**

```bash
# Only use precompiled wheels (no source builds)
pip install --only-binary=all pyvenice
```

### Why This Happens

PyVenice depends on Pydantic v2, which includes `pydantic-core` - a Rust-compiled component. While PyPI provides ARM64 wheels for many platforms, Android/Termux combinations sometimes fall through the cracks, forcing pip to build from source.

This is a known issue tracked in [pydantic-core#1474](https://github.com/pydantic/pydantic-core/issues/1474).

## Other Platform Issues

### macOS Apple Silicon (M1/M2)

Usually works out of the box, but if you encounter issues:

```bash
# Ensure you're using the latest pip
pip install --upgrade pip

# If still failing, try:
arch -arm64 pip install pyvenice
```

### Windows ARM64

```bash
# Update pip first
python -m pip install --upgrade pip

# Install with verbose output for debugging
pip install -v pyvenice
```

### Alpine Linux / Docker Issues

Alpine's musl libc can cause wheel compatibility issues:

```bash
# Install build dependencies
apk add gcc musl-dev libffi-dev

# Then install normally
pip install pyvenice
```

## When All Else Fails

1. **Check our releases**: We're working on providing ARM64 wheels for all platforms
2. **Use a different environment**: Consider using x86_64 if ARM64 continues to fail
3. **Report the issue**: [Open an issue](https://github.com/TheLustriVA/PyVenice/issues) with your platform details

## Getting Help

When reporting installation issues, please include:

- Operating system and version
- Architecture (ARM64, x86_64, etc.)
- Python version (`python --version`)
- pip version (`pip --version`)
- Full error message

This helps us prioritize which platforms need dedicated wheel builds.