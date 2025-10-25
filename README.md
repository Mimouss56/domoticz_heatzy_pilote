# Heatzy Pilote Plugin for Domoticz - Modular Version

Domoticz plugin to control Heatzy Pilote heaters via cloud API.

[🇫🇷 Version française](README_FR.md)

## 🆕 New in Version 1.0.0

This version brings a complete refactoring with a **modular architecture** following **SOLID principles**.

### Available Versions

1. **`plugin.py`** - Original version (reference)
2. **`plugin_improved.py`** - Improved monolithic version  
3. **`plugin_modular.py`** - **Recommended modular version** ⭐

## 🏗️ Modular Architecture

```
src/
├── models.py          # Domain models (HeatMode, Device, Token)
├── interfaces.py      # Contracts and interfaces
├── api.py            # Heatzy API client with error handling
├── domoticz_service.py # Domoticz service with test mocks
├── device_manager.py  # Device orchestrator
└── logger.py         # Configurable loggers
```

### Modular Version Benefits

- ✅ **Maintainability**: Organized and documented code
- ✅ **Testability**: Unit tests for each module
- ✅ **Extensibility**: Architecture open to evolution
- ✅ **Robustness**: Complete error handling
- ✅ **Performance**: Smart caching and optimizations

## 📋 Prerequisites

- Domoticz with Python support
- Heatzy account with configured Pilote devices
- **Python 3.8+** (Python 3.9+ recommended)

> **Note**: Python 3.6-3.7 are no longer supported due to end-of-life status and GitHub Actions compatibility. See [PYTHON_COMPATIBILITY.md](PYTHON_COMPATIBILITY.md) for details.

## 🚀 Installation

### Modular version (recommended)

1. **Download the plugin**:
   ```bash
   cd domoticz/plugins/
   git clone https://github.com/Mimouss56/domoticz_heatzy_pilote.git
   ```

2. **Use the modular version**:
   ```bash
   cd domoticz_heatzy_pilote/
   cp plugin_modular.py plugin.py
   ```

3. **Restart Domoticz**

4. **Configure the plugin** in Domoticz:
   - Go to Setup → Hardware
   - Add new hardware of type "Heatzy pilote"
   - Enter your Heatzy credentials
   - Enable the plugin

## ⚙️ Configuration

| Parameter | Description | Required |
|-----------|-------------|----------|
| Username | Heatzy account email | ✅ Yes |
| Password | Heatzy password | ✅ Yes |
| Debug | Debug level (0=None, 62=Normal, -1=Full) | No |

## 🎛️ Heating Modes

| Domoticz Mode | Level | Heatzy Mode | Description |
|---------------|-------|-------------|-------------|
| Off | 0 | off | Heater off |
| Frost protection | 10 | fro | Frost protection |
| Eco | 20 | eco | Economy mode |
| Comfort | 30 | cft | Comfort mode |

## 🧪 Testing and Validation

### Test the modular architecture

```bash
cd domoticz_heatzy_pilote/
python3 test_modular.py
```

### Unit tests by module

```python
# Test models
from src.models import HeatMode
mode = HeatMode.from_domoticz_level(20)
assert mode == HeatMode.ECO

# Test with mocks
from src.logger import NullLogger
from src.domoticz_service import MockDomoticzService
logger = NullLogger()
service = MockDomoticzService(logger)
```

## 📊 Monitoring and Debug

### Available logs

- **Info**: Startup, authentication, device discovery
- **Debug**: API requests, status synchronization
- **Error**: Authentication failures, communication errors

### Useful commands

```bash
# View Domoticz logs
tail -f domoticz.log | grep HeatzyPilote

# Test plugin outside Domoticz
python3 plugin_modular.py

# Validate modules
python3 test_modular.py
```

## 🔧 Development

### SOLID principles structure

1. **Single Responsibility**: Each class has a single responsibility
2. **Open/Closed**: Extensible without modifying existing code
3. **Liskov Substitution**: Implementations respect their contracts
4. **Interface Segregation**: Specialized and targeted interfaces  
5. **Dependency Inversion**: Dependencies on abstractions

### Adding a new heating mode

```python
# In src/models.py
class HeatMode(Enum):
    # Existing modes...
    BOOST = ("boost", 4, 40)  # New mode
```

### Adding a new logger

```python
# In src/logger.py
class FileLogger(ILogger):
    def __init__(self, filename):
        self.filename = filename
    
    def info(self, message):
        with open(self.filename, 'a') as f:
            f.write(f"INFO: {message}\n")
```

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - List of improvements
- **[Source code](src/)** - Complete inline documentation

## 🐛 Troubleshooting

### Common issues

1. **"Authentication failed"**
   - Check Heatzy credentials
   - Test internet connection
   - Verify Heatzy API accessibility

2. **"No devices found"**
   - Ensure devices are configured in Heatzy app
   - Check that devices are online

3. **"Module import error"**
   - Verify all `src/*.py` files are present
   - Ensure correct permissions

### Advanced debugging

```python
# Enable full debug
Parameters["Mode6"] = "-1"

# Manual authentication test
from src.api import HeatzyApiClient, HttpClient
from src.logger import ConsoleLogger

logger = ConsoleLogger()
http_client = HttpClient(logger)
api_client = HeatzyApiClient(http_client, logger)
token = api_client.authenticate("email", "password")
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a branch for your feature
3. Add tests for your code
4. Ensure all tests pass
5. Create a Pull Request

## 📄 License

This project is under MIT license. See LICENSE file for details.

## 🙏 Acknowledgments

- Domoticz team for the plugin framework
- Heatzy for the heater control API
- Open source community for feedback and improvements

## 📈 Version History

### v1.0.0 (2025-10-25)
- ✨ Complete modular refactoring
- ✅ SOLID principles implementation
- 🧪 Comprehensive test suite
- 📚 Complete documentation
- 🚀 Performance improvements

### v0.0.1 (Original)
- 🔧 Basic Heatzy API integration
- 🏠 Domoticz device creation
- ⚡ Basic heating mode control

## 🌟 Features Comparison

| Feature | Original | Improved | Modular |
|---------|----------|----------|---------|
| Code organization | ❌ Monolithic | ✅ Better structure | ⭐ Full modules |
| Error handling | ❌ Basic | ✅ Improved | ⭐ Comprehensive |
| Testing | ❌ None | ❌ Limited | ⭐ Full suite |
| Documentation | ❌ Minimal | ✅ Good | ⭐ Complete |
| Maintainability | ❌ Hard | ✅ Better | ⭐ Excellent |
| Extensibility | ❌ Difficult | ✅ Possible | ⭐ Easy |

---

**Ready to use?** Choose the modular version for the best experience! 🚀.
* Run: ```git pull```
* Restart Domoticz.

## Configuration
Pour ajouter vos modules Heatzy rendez-vous sur la page ```Matériel``` de votre Domoticz et ajoutez un élément de type ```Heatzy pilote```.

Renseignez un nom et les identifiants de votre compte Heatzy.

## Utilisation
Ce plugin va créer (au moment du démarrage) chaque module Heaty pilote associés à votre compte.
