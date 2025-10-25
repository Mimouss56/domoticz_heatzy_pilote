#!/bin/bash
# Development configuration script for Heatzy Pilote Plugin

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="Heatzy Pilote Plugin"
PLUGIN_DIR="/opt/domoticz/plugins/heatzy_pilote"
BACKUP_DIR="$HOME/domoticz_plugin_backup"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python installation
check_python() {
    print_status "Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python3 found: $PYTHON_VERSION"
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        if [[ $PYTHON_VERSION == 3.* ]]; then
            print_success "Python found: $PYTHON_VERSION"
            PYTHON_CMD="python"
        else
            print_error "Python 2 detected. Python 3.6+ required."
            exit 1
        fi
    else
        print_error "Python not found. Please install Python 3.6+"
        exit 1
    fi
}

# Function to check Git installation
check_git() {
    print_status "Checking Git installation..."
    
    if command_exists git; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_success "Git found: $GIT_VERSION"
    else
        print_warning "Git not found. Version management will be limited."
    fi
}

# Function to install development dependencies
install_dependencies() {
    print_status "Installing development dependencies..."
    
    DEPS="flake8 black mypy pytest bandit safety"
    
    for dep in $DEPS; do
        print_status "Installing $dep..."
        if pip3 install --user "$dep" >/dev/null 2>&1; then
            print_success "$dep installed"
        else
            print_warning "Failed to install $dep"
        fi
    done
}

# Function to check Domoticz installation
check_domoticz() {
    print_status "Checking Domoticz installation..."
    
    if [ -d "/opt/domoticz" ]; then
        print_success "Domoticz found at /opt/domoticz"
        
        if [ -d "/opt/domoticz/plugins" ]; then
            print_success "Plugins directory found"
        else
            print_warning "Plugins directory not found"
            print_status "Creating plugins directory..."
            sudo mkdir -p /opt/domoticz/plugins
        fi
        
        if systemctl is-active --quiet domoticz; then
            print_success "Domoticz service is running"
        else
            print_warning "Domoticz service is not running"
        fi
    else
        print_warning "Domoticz not found at /opt/domoticz"
        print_status "Please ensure Domoticz is installed"
    fi
}

# Function to setup development environment
setup_dev_env() {
    print_status "Setting up development environment..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    print_success "Backup directory created at $BACKUP_DIR"
    
    # Setup pre-commit hook if git is available
    if command_exists git && [ -d ".git" ]; then
        if [ ! -f ".git/hooks/pre-commit" ]; then
            print_status "Setting up pre-commit hook..."
            cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running pre-commit checks..."
make quality
if [ $? -ne 0 ]; then
    echo "❌ Pre-commit checks failed"
    exit 1
fi
echo "✅ Pre-commit checks passed"
EOF
            chmod +x .git/hooks/pre-commit
            print_success "Pre-commit hook installed"
        fi
        
        # Initialize git if not already done
        if [ ! -f ".gitignore" ]; then
            print_status "Creating .gitignore..."
            cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

.pytest_cache/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/

.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

.mypy_cache/
.dmypy.json
dmypy.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Local config
local_config.py
*.local.json

# Backup files
*.bak
*.backup
EOF
            print_success ".gitignore created"
        fi
    fi
    
    # Create local configuration template
    if [ ! -f "local_config.py.template" ]; then
        print_status "Creating local configuration template..."
        cat > local_config.py.template << 'EOF'
"""
Local configuration template for development
Copy this file to local_config.py and adjust settings
"""

# Domoticz configuration
DOMOTICZ_IP = "127.0.0.1"
DOMOTICZ_PORT = "8080"

# Heatzy API configuration (for testing)
HEATZY_USERNAME = "your_username"
HEATZY_PASSWORD = "your_password"

# Development settings
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"

# Plugin installation path
PLUGIN_INSTALL_PATH = "/opt/domoticz/plugins/heatzy_pilote"
EOF
        print_success "Configuration template created"
    fi
}

# Function to run validation tests
run_validation() {
    print_status "Running validation tests..."
    
    # Check plugin structure
    if $PYTHON_CMD -c "
import re
import sys

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
        print(f'Missing required pattern: {pattern}')
        sys.exit(1)

print('Plugin structure is valid')
"; then
        print_success "Plugin structure validation passed"
    else
        print_error "Plugin structure validation failed"
        exit 1
    fi
    
    # Run tests
    if $PYTHON_CMD test_modular.py >/dev/null 2>&1; then
        print_success "Module tests passed"
    else
        print_error "Module tests failed"
        exit 1
    fi
}

# Function to backup existing plugin
backup_existing() {
    if [ -d "$PLUGIN_DIR" ]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_PATH="$BACKUP_DIR/heatzy_pilote_backup_$TIMESTAMP"
        
        print_status "Backing up existing plugin to $BACKUP_PATH"
        sudo cp -r "$PLUGIN_DIR" "$BACKUP_PATH"
        sudo chown -R $(whoami):$(whoami) "$BACKUP_PATH"
        print_success "Backup completed"
    fi
}

# Function to install plugin
install_plugin() {
    print_status "Installing plugin to Domoticz..."
    
    if [ ! -d "/opt/domoticz/plugins" ]; then
        print_error "Domoticz plugins directory not found"
        exit 1
    fi
    
    backup_existing
    
    # Create plugin directory
    sudo mkdir -p "$PLUGIN_DIR"
    
    # Copy files
    sudo cp plugin_modular.py "$PLUGIN_DIR/plugin.py"
    sudo cp -r src/ "$PLUGIN_DIR/"
    sudo cp README.md README_FR.md CHANGELOG.md "$PLUGIN_DIR/"
    
    # Set ownership
    sudo chown -R domoticz:domoticz "$PLUGIN_DIR"
    
    print_success "Plugin installed to $PLUGIN_DIR"
    print_warning "Please restart Domoticz to load the plugin"
}

# Function to show help
show_help() {
    cat << EOF
${PROJECT_NAME} Development Configuration Script

Usage: $0 [OPTION]

Options:
    --check         Check system requirements
    --setup         Setup development environment
    --install-deps  Install development dependencies
    --validate      Run validation tests
    --install       Install plugin to Domoticz
    --backup        Backup existing plugin
    --status        Show system status
    --help          Show this help message

Examples:
    $0 --check      # Check if system is ready for development
    $0 --setup      # Setup complete development environment
    $0 --install    # Install plugin to Domoticz

For more commands, use: make help
EOF
}

# Function to show system status
show_status() {
    print_status "System Status Report"
    echo "===================="
    
    # Python status
    check_python
    
    # Git status
    check_git
    
    # Domoticz status
    check_domoticz
    
    # Project status
    if [ -f "plugin_modular.py" ]; then
        print_success "Plugin source found"
    else
        print_error "Plugin source missing"
    fi
    
    if [ -d "src" ]; then
        MODULE_COUNT=$(find src -name "*.py" | wc -l)
        print_success "Source modules found: $MODULE_COUNT"
    else
        print_error "Source modules missing"
    fi
    
    # Version status
    if command_exists python3 && [ -f "version_manager.py" ]; then
        print_status "Version information:"
        $PYTHON_CMD version_manager.py status
    fi
    
    echo "===================="
}

# Main script logic
case "${1:-}" in
    --check)
        print_status "Checking system requirements..."
        check_python
        check_git
        check_domoticz
        print_success "System check completed"
        ;;
    --setup)
        print_status "Setting up development environment..."
        check_python
        setup_dev_env
        install_dependencies
        print_success "Development environment setup completed"
        ;;
    --install-deps)
        check_python
        install_dependencies
        ;;
    --validate)
        check_python
        run_validation
        ;;
    --install)
        check_python
        run_validation
        install_plugin
        ;;
    --backup)
        backup_existing
        ;;
    --status)
        show_status
        ;;
    --help|*)
        show_help
        ;;
esac