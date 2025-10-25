# Makefile for Heatzy Pilote Plugin Development

.PHONY: help install test lint format clean build release version

# Variables
PYTHON := python3
PIP := pip3
PROJECT_NAME := heatzy_pilote
VERSION := $(shell $(PYTHON) version_manager.py current)

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Heatzy Pilote Plugin Development Commands"
	@echo "========================================"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	$(PIP) install --user flake8 black mypy pytest bandit safety
	@echo "✅ Dependencies installed"

test: ## Run all tests
	@echo "🧪 Running tests..."
	$(PYTHON) test_modular.py
	@echo "✅ All tests passed"

test-verbose: ## Run tests with verbose output
	@echo "🧪 Running tests (verbose)..."
	$(PYTHON) test_modular.py -v
	@echo "✅ All tests passed"

lint: ## Run linting checks
	@echo "🔍 Running linting checks..."
	flake8 src/ *.py --max-line-length=88 --extend-ignore=E203,W503
	@echo "✅ Linting passed"

format: ## Format code with Black
	@echo "🎨 Formatting code..."
	black src/ *.py
	@echo "✅ Code formatted"

format-check: ## Check code formatting without making changes
	@echo "🎨 Checking code formatting..."
	black --check --diff src/ *.py
	@echo "✅ Code formatting is correct"

type-check: ## Run type checking with mypy
	@echo "🔍 Running type checks..."
	mypy src/ --ignore-missing-imports --no-strict-optional
	@echo "✅ Type checking passed"

security: ## Run security checks
	@echo "🛡️ Running security checks..."
	bandit -r src/ -f txt
	@echo "✅ Security checks passed"

quality: lint format-check type-check security ## Run all quality checks

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/
	@echo "✅ Cleanup complete"

build: clean test quality ## Build release package
	@echo "📦 Building release package..."
	$(PYTHON) version_manager.py status
	mkdir -p dist/$(PROJECT_NAME)_v$(VERSION)
	cp plugin_modular.py dist/$(PROJECT_NAME)_v$(VERSION)/plugin.py
	cp -r src/ dist/$(PROJECT_NAME)_v$(VERSION)/
	cp README.md README_FR.md CHANGELOG.md ARCHITECTURE.md dist/$(PROJECT_NAME)_v$(VERSION)/
	cd dist && tar -czf $(PROJECT_NAME)_v$(VERSION).tar.gz $(PROJECT_NAME)_v$(VERSION)/
	cd dist && zip -r $(PROJECT_NAME)_v$(VERSION).zip $(PROJECT_NAME)_v$(VERSION)/
	@echo "✅ Package built: dist/$(PROJECT_NAME)_v$(VERSION).tar.gz"

version-status: ## Show current version status
	@$(PYTHON) version_manager.py status

version-patch: ## Bump patch version
	@$(PYTHON) version_manager.py bump patch --commit --tag
	@echo "🎉 Patch version bumped"

version-minor: ## Bump minor version
	@$(PYTHON) version_manager.py bump minor --commit --tag
	@echo "🎉 Minor version bumped"

version-major: ## Bump major version
	@$(PYTHON) version_manager.py bump major --commit --tag
	@echo "🎉 Major version bumped"

version-auto: ## Auto-detect and bump version
	@$(PYTHON) version_manager.py bump --commit --tag
	@echo "🎉 Version auto-bumped"

release: build ## Create a full release
	@echo "🚀 Creating release..."
	$(PYTHON) version_manager.py bump --commit --tag
	git push origin main --tags
	@echo "✅ Release created and pushed"

install-plugin: build ## Install plugin to local Domoticz
	@echo "🔧 Installing plugin to Domoticz..."
	@if [ -d "/opt/domoticz/plugins" ]; then \
		sudo cp -r dist/$(PROJECT_NAME)_v$(VERSION)/* /opt/domoticz/plugins/heatzy_pilote/; \
		sudo chown -R domoticz:domoticz /opt/domoticz/plugins/heatzy_pilote/; \
		echo "✅ Plugin installed to /opt/domoticz/plugins/heatzy_pilote/"; \
		echo "📋 Please restart Domoticz to load the plugin"; \
	else \
		echo "❌ Domoticz plugins directory not found at /opt/domoticz/plugins"; \
		echo "📋 Manual installation required"; \
	fi

uninstall-plugin: ## Uninstall plugin from local Domoticz
	@echo "🗑️ Uninstalling plugin from Domoticz..."
	@if [ -d "/opt/domoticz/plugins/heatzy_pilote" ]; then \
		sudo rm -rf /opt/domoticz/plugins/heatzy_pilote/; \
		echo "✅ Plugin uninstalled"; \
		echo "📋 Please restart Domoticz"; \
	else \
		echo "ℹ️ Plugin not found in /opt/domoticz/plugins/heatzy_pilote"; \
	fi

dev-setup: install ## Set up development environment
	@echo "⚙️ Setting up development environment..."
	@if [ ! -f ".git/hooks/pre-commit" ]; then \
		echo "Setting up pre-commit hook..."; \
		cat > .git/hooks/pre-commit << 'EOF'; \
#!/bin/bash; \
echo "Running pre-commit checks..."; \
make quality; \
if [ $$? -ne 0 ]; then; \
	echo "❌ Pre-commit checks failed"; \
	exit 1; \
fi; \
echo "✅ Pre-commit checks passed"; \
EOF; \
		chmod +x .git/hooks/pre-commit; \
		echo "✅ Pre-commit hook installed"; \
	fi
	@echo "✅ Development environment ready"

dev-test: ## Run development tests continuously
	@echo "🔄 Running continuous tests..."
	@while true; do \
		$(PYTHON) test_modular.py; \
		echo "Waiting for file changes... (Ctrl+C to stop)"; \
		sleep 5; \
	done

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@if command -v pdoc3 >/dev/null 2>&1; then \
		pdoc3 --html --output-dir docs src/; \
		echo "✅ Documentation generated in docs/"; \
	else \
		echo "📦 Installing pdoc3..."; \
		$(PIP) install --user pdoc3; \
		pdoc3 --html --output-dir docs src/; \
		echo "✅ Documentation generated in docs/"; \
	fi

profile: ## Profile plugin performance
	@echo "📊 Profiling plugin performance..."
	$(PYTHON) -c "
import cProfile
import pstats
import sys
sys.path.insert(0, 'src')

pr = cProfile.Profile()
pr.enable()

from plugin_modular import create_test_plugin
plugin = create_test_plugin()
plugin.onStart()

pr.disable()
stats = pstats.Stats(pr)
stats.sort_stats('cumulative')
stats.print_stats(20)
"

memory-test: ## Test memory usage
	@echo "💾 Testing memory usage..."
	$(PYTHON) -c "
import tracemalloc
import sys
sys.path.insert(0, 'src')

tracemalloc.start()

from plugin_modular import create_test_plugin
plugin = create_test_plugin()

current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f'Current memory usage: {current / 1024 / 1024:.2f} MB')
print(f'Peak memory usage: {peak / 1024 / 1024:.2f} MB')
"

validate: ## Validate plugin structure
	@echo "✅ Validating plugin structure..."
	@$(PYTHON) -c "
import re
import sys

# Check plugin structure
with open('plugin_modular.py', 'r') as f:
    content = f.read()

required_patterns = [
    r'<plugin.*key=.*name=.*author=.*version=.*>',
    r'def onStart\(\):',
    r'def onStop\(\):',  
    r'def onCommand\(',
    r'def onHeartbeat\(\):',
    r'global _plugin'
]

for pattern in required_patterns:
    if not re.search(pattern, content):
        print(f'❌ Missing required pattern: {pattern}')
        sys.exit(1)

print('✅ Plugin structure is valid')
"

git-status: ## Show git status with version info
	@echo "📋 Git Status:"
	@git status --short
	@echo ""
	@echo "📋 Version Info:"
	@$(PYTHON) version_manager.py status
	@echo ""
	@echo "📋 Recent Commits:"
	@git log --oneline -5

# Development workflow shortcuts
dev: dev-setup quality test ## Complete development check
ci: quality test build ## Run CI checks locally
quick: format test ## Quick development check