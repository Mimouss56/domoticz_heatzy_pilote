# Development Configuration

Configuration and setup for Heatzy Pilote Plugin development.

## Development Environment Setup

### Prerequisites
- Python 3.6+
- Git
- Text editor or IDE with Python support

### Recommended IDE Configuration

#### VS Code
```json
{
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.unittestEnabled": true,
    "files.associations": {
        "*.py": "python"
    }
}
```

#### PyCharm
- Enable type checking
- Configure code style to PEP 8
- Set up pytest as test runner

### Code Quality Tools

#### Install development dependencies
```bash
pip3 install --user flake8 black mypy pytest
```

#### Pre-commit hooks (optional)
```bash
# Install pre-commit
pip3 install --user pre-commit

# Setup hooks
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
EOF

# Install hooks
pre-commit install
```

## Testing

### Run all tests
```bash
python3 test_modular.py
```

### Run specific module tests
```bash
# Test models only
python3 -c "
import sys; sys.path.insert(0, 'src')
from test_modular import test_models
test_models()
print('Models test passed')
"
```

### Test with different Python versions
```bash
# Test with Python 3.6 (minimum supported)
python3.6 test_modular.py

# Test with Python 3.9+
python3.9 test_modular.py
```

## Code Style

### Formatting
Use Black for consistent formatting:
```bash
black src/ *.py
```

### Linting
Use flake8 for style checking:
```bash
flake8 src/ *.py --max-line-length=88 --extend-ignore=E203,W503
```

### Type Checking
Use mypy for type validation:
```bash
mypy src/ --ignore-missing-imports
```

## Performance Testing

### Memory Usage
```python
import tracemalloc
tracemalloc.start()

# Run plugin code
from plugin_modular import create_test_plugin
plugin = create_test_plugin()

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

### Performance Profiling
```python
import cProfile
import pstats

# Profile the plugin startup
pr = cProfile.Profile()
pr.enable()

from plugin_modular import create_test_plugin
plugin = create_test_plugin()
plugin.onStart()

pr.disable()
stats = pstats.Stats(pr)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Debugging

### Enable Debug Logging
```python
# In plugin code
Parameters["Mode6"] = "-1"  # Full debug
```

### Debug API Calls
```python
from src.logger import ConsoleLogger
from src.api import HttpClient, HeatzyApiClient

logger = ConsoleLogger()
http_client = HttpClient(logger)
api_client = HeatzyApiClient(http_client, logger)

# Test authentication
try:
    token = api_client.authenticate("test@example.com", "password")
    print(f"Token: {token}")
except Exception as e:
    print(f"Auth failed: {e}")
```

### Mock API Responses
```python
# Create mock HTTP client for testing
class MockHttpClient:
    def __init__(self):
        self.responses = {}
    
    def set_response(self, path, response):
        self.responses[path] = response
    
    def post(self, path, data, headers):
        return self.responses.get(path, {})
    
    def get(self, path, headers):
        return self.responses.get(path, {})

# Use in tests
mock_client = MockHttpClient()
mock_client.set_response("/app/login", {"token": "test_token"})
```

## Building and Packaging

### Create Release Package
```bash
#!/bin/bash
# create_release.sh

VERSION="1.0.0"
PACKAGE_NAME="heatzy_pilote_v${VERSION}"

# Create package directory
mkdir -p "dist/${PACKAGE_NAME}"

# Copy necessary files
cp plugin_modular.py "dist/${PACKAGE_NAME}/plugin.py"
cp -r src/ "dist/${PACKAGE_NAME}/"
cp README.md "dist/${PACKAGE_NAME}/"
cp CHANGELOG.md "dist/${PACKAGE_NAME}/"

# Create archive
cd dist
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}/"
zip -r "${PACKAGE_NAME}.zip" "${PACKAGE_NAME}/"

echo "Release packages created in dist/"
```

### Validate Package
```bash
# Test the packaged version
cd dist/heatzy_pilote_v1.0.0/
python3 -c "
import sys
sys.path.insert(0, 'src')
from plugin_modular import create_test_plugin
plugin = create_test_plugin()
print('Package validation successful')
"
```

## Documentation

### Generate API Documentation
```bash
# Install pydoc
pip3 install --user pdoc3

# Generate documentation
pdoc --html --output-dir docs src/
```

### Update Documentation
When adding new features:
1. Update docstrings in code
2. Update README.md
3. Update ARCHITECTURE.md
4. Add entry to CHANGELOG.md

## Continuous Integration

### GitHub Actions (example)
```yaml
# .github/workflows/test.yml
name: Test Plugin

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.6, 3.7, 3.8, 3.9]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Run tests
      run: python3 test_modular.py
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 src/ --max-line-length=88
```

## Contributing Guidelines

### Before submitting a PR:
1. Run all tests: `python3 test_modular.py`
2. Check code style: `flake8 src/`
3. Update documentation if needed
4. Add tests for new features
5. Update CHANGELOG.md

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] All existing tests pass
- [ ] New tests added (if applicable)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```