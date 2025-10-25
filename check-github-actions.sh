#!/bin/bash
# Quick GitHub Actions readiness check

set -e

echo "🔍 GitHub Actions Readiness Check"
echo "================================="

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
echo "Python version: $PYTHON_VERSION"

# Check if version is supported
if [[ "$PYTHON_VERSION" == "3.8" ]] || [[ "$PYTHON_VERSION" == "3.9" ]] || [[ "$PYTHON_VERSION" == "3.10" ]] || [[ "$PYTHON_VERSION" == "3.11" ]] || [[ "$PYTHON_VERSION" == "3.12" ]]; then
    echo "✅ Python version is supported in CI matrix"
else
    echo "⚠️  Python version may not be in CI matrix (but plugin should work)"
fi

# Check imports
echo "📋 Checking imports..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from src import (
    HeatMode, HeatzyDevice, AuthToken,
    HttpClient, HeatzyApiClient,
    DomoticzService, DeviceManager,
    DomoticzLogger,
    AuthenticationError, ApiError, InitializationError, SyncError
)
from plugin_modular import create_test_plugin
print('✅ All imports successful')
"

# Run tests
echo "📋 Running tests..."
python3 test_modular.py > /dev/null 2>&1
echo "✅ Tests passed"

# Check workflow files
echo "📋 Checking workflow files..."
for workflow in .github/workflows/*.yml; do
    if [[ -f "$workflow" ]]; then
        if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
            echo "✅ $(basename $workflow) is valid"
        else
            echo "❌ $(basename $workflow) has YAML errors"
            exit 1
        fi
    fi
done

# Check for deprecated Python versions in workflows
echo "📋 Checking for deprecated Python versions..."
if grep -r "python-version.*3\.[67]" .github/workflows/ >/dev/null 2>&1; then
    echo "⚠️  Found deprecated Python 3.6/3.7 in workflows"
else
    echo "✅ No deprecated Python versions found"
fi

# Check branch configuration
echo "📋 Checking branch configuration..."
if grep -r "branches.*master" .github/workflows/ >/dev/null 2>&1; then
    echo "✅ Workflows configured for master branch"
else
    echo "⚠️  Check branch configuration in workflows"
fi

echo "================================="
echo "🎉 Readiness check completed!"
echo "✅ Project should work with GitHub Actions"
echo ""
echo "💡 To test locally:"
echo "   ./configure.sh --check"
echo "   make test"
echo "   make quality"