#!/bin/bash
# Local security scanning script for PyVenice
# Run this before committing changes

set -e

echo "🔍 PyVenice Security Scanner"
echo "============================"

# Create results directory
mkdir -p results

echo ""
echo "📦 Installing security tools..."
pip install -q safety bandit semgrep pip-audit

echo ""
echo "🛡️  Running Safety check..."
safety check --short-report
safety check --json --output results/safety.json 2>/dev/null || true

echo ""
echo "🔍 Running pip-audit..."
pip-audit --desc
pip-audit --format=json --output=results/pip-audit.json 2>/dev/null || true

echo ""
echo "🔒 Running Bandit static analysis..."
bandit -r pyvenice/ -f txt
bandit -r pyvenice/ -f json -o results/bandit.json 2>/dev/null || true

echo ""
echo "⚡ Running Semgrep analysis..."
semgrep --config=auto pyvenice/ --text
semgrep --config=auto pyvenice/ --json --output=results/semgrep.json 2>/dev/null || true

echo ""
echo "🔎 Checking for hardcoded secrets..."
if grep -r -i "password\|secret\|key\|token\|api_key" pyvenice/ --exclude-dir=__pycache__ 2>/dev/null; then
    echo "⚠️  Potential secrets found - please review above"
    exit 1
else
    echo "✅ No obvious secrets detected"
fi

echo ""
echo "🎉 Security scan completed!"
echo "📁 Detailed results saved in results/ directory"
echo ""
echo "Summary:"
echo "- ✅ Dependency vulnerability scan"
echo "- ✅ Static code analysis"  
echo "- ✅ Secret detection"
echo ""
echo "Ready to commit! 🚀"