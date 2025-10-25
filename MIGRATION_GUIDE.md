# Migration Guide: Python Version Update

## 🚨 Important Notice

Starting with version 1.4.0, this plugin requires **Python 3.8 or higher**.

Python 3.6 and 3.7 are no longer supported due to:
- End-of-life status
- Security vulnerabilities  
- GitHub Actions/Ubuntu 24.04 incompatibility
- Modern Python features used in the codebase

## 🔍 Check Your Current Python Version

```bash
python3 --version
```

## ✅ If You Have Python 3.8+

No action needed! Your system is already compatible.

## ⚠️ If You Have Python 3.6 or 3.7

You need to upgrade Python. Choose one of the options below:

### Option 1: System Upgrade (Recommended)

#### Ubuntu/Debian:
```bash
# Update package list
sudo apt update

# Install Python 3.9 (recommended)
sudo apt install python3.9 python3.9-venv python3.9-dev

# Update default python3 link
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Verify
python3 --version
```

#### CentOS/RHEL/Fedora:
```bash
# CentOS/RHEL 8+
sudo dnf install python39 python39-devel

# Fedora
sudo dnf install python3.9 python3.9-devel

# Update alternatives
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
```

#### Alpine Linux:
```bash
# Install Python 3.9
sudo apk add python3 py3-pip

# Verify
python3 --version
```

### Option 2: Using pyenv (Advanced Users)

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to shell configuration
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.9
pyenv install 3.9.18
pyenv global 3.9.18

# Verify
python --version
```

### Option 3: Using conda/miniconda

```bash
# Install miniconda if not present
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create environment with Python 3.9
conda create -n domoticz python=3.9
conda activate domoticz

# Install in Domoticz context
# (Note: You'll need to configure Domoticz to use this Python)
```

## 🏠 Domoticz-Specific Considerations

### Check Domoticz Python Version

1. **Via Domoticz UI**: Go to Setup → Log → check for Python version in startup logs
2. **Via Command Line**: 
   ```bash
   # If Domoticz is running as service
   sudo systemctl status domoticz
   
   # Check which Python Domoticz uses
   ps aux | grep domoticz
   ```

### Update Domoticz Python (if needed)

#### Method 1: Recompile Domoticz
```bash
# Backup your Domoticz
sudo systemctl stop domoticz
cp -r /opt/domoticz /opt/domoticz.backup

# Download and compile with new Python
cd /tmp
git clone https://github.com/domoticz/domoticz.git
cd domoticz
make clean
make

# Install
sudo make install
sudo systemctl start domoticz
```

#### Method 2: Use Updated Package
```bash
# Ubuntu: Add Domoticz repository with updated packages
# (Check Domoticz documentation for latest packages)
```

## 🔧 Plugin Installation After Upgrade

1. **Verify Python version**:
   ```bash
   python3 --version  # Should show 3.8+
   ```

2. **Test plugin import**:
   ```bash
   cd /opt/domoticz/plugins/domoticz_heatzy_pilote
   python3 -c "
   import sys
   sys.path.insert(0, 'src')
   from plugin_modular import create_test_plugin
   print('✅ Plugin import successful')
   "
   ```

3. **Restart Domoticz**:
   ```bash
   sudo systemctl restart domoticz
   ```

## 🐛 Troubleshooting

### Error: "Module not found"
```bash
# Check Python path
python3 -c "import sys; print(sys.path)"

# Reinstall plugin
cd /opt/domoticz/plugins
rm -rf domoticz_heatzy_pilote
git clone https://github.com/Mimouss56/domoticz_heatzy_pilote.git
sudo systemctl restart domoticz
```

### Error: "Permission denied"
```bash
# Fix permissions
sudo chown -R domoticz:domoticz /opt/domoticz/plugins/domoticz_heatzy_pilote
sudo chmod +x /opt/domoticz/plugins/domoticz_heatzy_pilote/*.py
```

### Plugin Not Loading
1. Check Domoticz logs: `/var/log/domoticz.log`
2. Verify Python version compatibility
3. Check plugin permissions
4. Restart Domoticz service

### Performance Issues
```bash
# Check if multiple Python versions are conflicting
which python3
python3 --version

# Clean Python cache
find /opt/domoticz/plugins -name "__pycache__" -type d -exec rm -rf {} +
```

## 📊 Migration Checklist

- [ ] Check current Python version
- [ ] Backup Domoticz configuration
- [ ] Backup current plugin
- [ ] Upgrade Python to 3.8+
- [ ] Verify Domoticz recognizes new Python
- [ ] Update plugin to latest version
- [ ] Test plugin functionality
- [ ] Check Domoticz logs for errors
- [ ] Verify device communication

## 🆘 Need Help?

### Community Support
- **GitHub Issues**: [Report problems](https://github.com/Mimouss56/domoticz_heatzy_pilote/issues)
- **Domoticz Forum**: General Domoticz support
- **Python.org**: Python installation guides

### Compatibility Testing
```bash
# Test script to verify compatibility
cd /opt/domoticz/plugins/domoticz_heatzy_pilote
./configure.sh --check
```

### Emergency Rollback
If you encounter issues:

1. **Restore backup**:
   ```bash
   sudo systemctl stop domoticz
   cp -r /opt/domoticz.backup/* /opt/domoticz/
   sudo systemctl start domoticz
   ```

2. **Use previous plugin version**:
   ```bash
   cd /opt/domoticz/plugins/domoticz_heatzy_pilote
   git checkout v1.3.0  # Last version supporting Python 3.6/3.7
   sudo systemctl restart domoticz
   ```

## 🔮 Future Considerations

- **Python 3.13**: Will be supported when stable
- **Domoticz Evolution**: Keep both Python and Domoticz updated
- **Security**: Regular updates recommended for security patches

---

💡 **Remember**: This upgrade improves security, performance, and future compatibility. The short-term effort pays off in long-term stability!