# Python Version Compatibility

## Supported Python Versions

This plugin is tested and compatible with the following Python versions:

- **Python 3.8** - Minimum supported version
- **Python 3.9** - Recommended version (default in CI/CD)
- **Python 3.10** - Fully supported
- **Python 3.11** - Fully supported  
- **Python 3.12** - Latest supported version

## Version History

### v1.1.0 (Current)
- **Removed support for Python 3.6 and 3.7** due to:
  - End of life status
  - Unavailability on Ubuntu 24.04 (GitHub Actions)
  - Security concerns with older versions
- **Added support for Python 3.12**
- **Set Python 3.9 as the default version** for CI/CD

### v1.0.0 (Legacy)
- Supported Python 3.6 - 3.11

## GitHub Actions Compatibility

Our CI/CD workflows are configured to run on Ubuntu Latest (currently 24.04) which supports:

- ✅ Python 3.8 - 3.12
- ❌ Python 3.6, 3.7 (deprecated, not available)

## Local Development

### Requirements
- Python 3.8 or higher
- pip (latest version recommended)

### Recommended Setup
```bash
# Check Python version
python3 --version

# Should show 3.8.x or higher
# If not, upgrade Python or use pyenv
```

### Using pyenv (recommended for development)
```bash
# Install multiple Python versions
pyenv install 3.8.18
pyenv install 3.9.18
pyenv install 3.10.12
pyenv install 3.11.6
pyenv install 3.12.0

# Set project Python version
pyenv local 3.9.18
```

## Domoticz Compatibility

### Domoticz Python Environment
- Domoticz typically uses the system Python
- Minimum requirement: Python 3.6 (but 3.8+ recommended)
- Most modern Domoticz installations support Python 3.8+

### Plugin Compatibility Matrix

| Domoticz Version | Python Version | Plugin Support |
|------------------|----------------|----------------|
| 2023.1+          | 3.8 - 3.12     | ✅ Full        |
| 2022.x           | 3.7 - 3.11     | ⚠️ Limited*    |
| 2021.x           | 3.6 - 3.10     | ❌ Not tested  |

*Limited support: Plugin will work but no CI/CD testing

## Dependencies

The plugin has minimal external dependencies to ensure broad compatibility:

### Core Dependencies (built-in)
- `http.client` - HTTP requests
- `json` - JSON parsing
- `urllib` - URL handling
- `threading` - Concurrency
- `time` - Timing operations
- `enum` - Enumerations (Python 3.4+)
- `typing` - Type hints (Python 3.5+)

### Development Dependencies
- `flake8` - Code linting
- `black` - Code formatting
- `mypy` - Type checking
- `pytest` - Testing framework
- `bandit` - Security scanning

All development dependencies support Python 3.8+.

## Migration Guide

### From Python 3.6/3.7
If you're currently using Python 3.6 or 3.7:

1. **Upgrade Python** to 3.8 or higher
2. **Test the plugin** in your environment
3. **Update your CI/CD** if using custom workflows

### Example upgrade on Ubuntu:
```bash
# Add deadsnakes PPA for newer Python versions
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.9
sudo apt install python3.9 python3.9-venv python3.9-dev

# Update alternatives
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
```

## Troubleshooting

### Common Issues

1. **"Python 3.7 not found" in GitHub Actions**
   - **Solution**: This is expected. Update your workflows to use Python 3.8+

2. **Type hints not working in Python 3.6/3.7**
   - **Solution**: Upgrade to Python 3.8+ for full type hint support

3. **Plugin works locally but fails in CI**
   - **Check**: Ensure your CI uses Python 3.8+
   - **Solution**: Update workflow files

### Version Detection
```python
import sys
print(f"Python version: {sys.version}")
print(f"Version info: {sys.version_info}")

# Check minimum version
if sys.version_info < (3, 8):
    print("⚠️ Python 3.8+ recommended")
else:
    print("✅ Python version is supported")
```

## Future Compatibility

### Planned Support
- **Python 3.13** - Will be added when stable
- **Python 3.14** - Future consideration

### Deprecation Policy
- Support for Python versions follows the [Python Release Schedule](https://www.python.org/dev/peps/pep-0602/)
- Versions are dropped 2 years after end-of-life
- Breaking changes are announced 6 months in advance

## Resources

- [Python Release Schedule](https://www.python.org/dev/peps/pep-0602/)
- [GitHub Actions Python Versions](https://github.com/actions/python-versions)
- [Domoticz Python Plugin Framework](https://www.domoticz.com/wiki/Developing_a_Python_plugin)