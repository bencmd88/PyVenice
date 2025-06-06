#!/bin/bash
# PyVenice PyPI Publishing Script

echo "🚀 PyVenice Publishing Script"
echo "============================="

# Check if we're on main branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "❌ Error: Must be on main branch to publish (currently on $BRANCH)"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ Error: Uncommitted changes detected. Please commit or stash them."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Run tests
echo "🧪 Running tests..."
pytest -m "not integration"
if [ $? -ne 0 ]; then
    echo "❌ Error: Tests failed. Fix them before publishing."
    exit 1
fi

# Build the package
echo "📦 Building package..."
python -m build

# Check the package
echo "🔍 Checking package with twine..."
twine check dist/*

# Show what will be uploaded
echo ""
echo "📋 Files to be uploaded:"
ls -la dist/

# Confirm upload
echo ""
read -p "🤔 Upload to PyPI? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to PyPI..."
    twine upload dist/*
    echo "✅ Published successfully!"
else
    echo "❌ Upload cancelled."
fi