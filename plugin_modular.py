#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Heatzy Pilote Plugin for Domoticz - Modular Version
#
# Author: Mimouss56
# Version: 1.0.0
#
"""
<plugin key="heatzy_pilote" name="Heatzy pilote" author="Mimouss" version="1.4.0">
    <params>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Python" value="18"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
        <param field="Username" label="Heatzy user / email" width="200px" required="true" default=""/>
        <param field="Password" label="Heatzy password" width="200px" required="true" default=""/>
    </params>
</plugin>
"""

# Standard library imports
import sys
import os

# Add the src directory to the Python path for imports
plugin_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(plugin_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import Domoticz module (available when running in Domoticz)
try:
    import Domoticz
    DOMOTICZ_AVAILABLE = True
except ImportError:
    DOMOTICZ_AVAILABLE = False
    # Create mock Domoticz for testing
    class MockDomoticz:
        @staticmethod
        def Debug(msg): print(f"DEBUG: {msg}")
        @staticmethod
        def Log(msg): print(f"LOG: {msg}")
        @staticmethod
        def Error(msg): print(f"ERROR: {msg}")
        @staticmethod
        def Debugging(level): pass
    
    Domoticz = MockDomoticz()

# Import our modules
try:
    from src import (
        HeatMode, HeatzyDevice, AuthToken,
        HttpClient, HeatzyApiClient,
        DomoticzService, DeviceManager,
        DomoticzLogger,
        AuthenticationError, ApiError, InitializationError, SyncError
    )
except ImportError as e:
    Domoticz.Error(f"Failed to import plugin modules: {e}")
    raise


class BasePlugin:
    """
    Main plugin class - orchestrates all components.
    
    This class follows the Single Responsibility Principle by acting as a
    coordinator that delegates specific tasks to specialized components.
    """
    
    # Plugin configuration
    HEARTBEAT_INTERVAL_MINUTES = 3
    VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize the plugin with dependency injection."""
        self.logger = None
        self.http_client = None
        self.api_client = None
        self.domoticz_service = None
        self.device_manager = None
        
        # Plugin state
        self._heartbeat_counter = 0
        self._initialized = False
        self._credentials = {'username': '', 'password': ''}
    
    def onStart(self):
        """
        Plugin startup - initialize all components and authenticate.
        
        This method sets up the dependency injection container and
        initializes the device discovery process.
        """
        try:
            self.logger = DomoticzLogger("HeatzyPilote")
            self.logger.info(f"Starting Heatzy Pilote Plugin v{self.VERSION}")
            
            # Enable debugging if requested
            if Parameters.get("Mode6", "0") != "0":
                debug_level = int(Parameters["Mode6"])
                if DOMOTICZ_AVAILABLE:
                    Domoticz.Debugging(debug_level)
                self.logger.debug(f"Debug mode enabled (level: {debug_level})")
            
            # Store credentials
            self._credentials['username'] = Parameters.get("Username", "")
            self._credentials['password'] = Parameters.get("Password", "")
            
            # Validate credentials
            if not self._credentials['username'] or not self._credentials['password']:
                self.logger.error("Username and password are required")
                return
            
            # Initialize components (Dependency Injection)
            self._initialize_components()
            
            # Authenticate with Heatzy API
            self._authenticate()
            
            # Initialize devices
            self._initialize_devices()
            
            self._initialized = True
            self.logger.info("Plugin startup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Plugin startup failed: {e}")
            self._initialized = False
    
    def onStop(self):
        """Plugin shutdown."""
        self.logger.info("Stopping Heatzy Pilote Plugin")
    
    def onCommand(self, Unit, Command, Level, Hue):
        """
        Handle device commands from Domoticz.
        
        Args:
            Unit: Domoticz device unit number
            Command: Command type (e.g., 'Set Level')
            Level: Command level (0-30 for heat modes)
            Hue: Color hue (not used for this plugin)
        """
        if not self._initialized:
            self.logger.error("Plugin not initialized, ignoring command")
            return
        
        try:
            self.logger.debug(
                f"Command received - Unit: {Unit}, Command: {Command}, Level: {Level}"
            )
            
            if Command == 'Set Level':
                success = self.device_manager.control_device(Unit, Level)
                if not success:
                    self.logger.error(f"Failed to execute command for unit {Unit}")
            else:
                self.logger.warning(f"Unknown command: {Command}")
                
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")
    
    def onHeartbeat(self):
        """
        Periodic sync - synchronize device status with Heatzy API.
        
        This method is called regularly by Domoticz to maintain
        synchronization between the cloud API and local devices.
        """
        if not self._initialized:
            return
        
        self._heartbeat_counter -= 1
        
        if self._heartbeat_counter <= 0:
            self._heartbeat_counter = self.HEARTBEAT_INTERVAL_MINUTES
            
            try:
                self.logger.debug("Starting periodic device synchronization")
                
                # Re-authenticate if needed
                if not self.api_client.is_authenticated():
                    self.logger.info("Re-authenticating with Heatzy API")
                    self._authenticate()
                
                # Sync device status
                self.device_manager.sync_device_status()
                
                self.logger.debug("Periodic synchronization completed")
                
            except Exception as e:
                self.logger.error(f"Heartbeat synchronization failed: {e}")
        else:
            self.logger.debug(f"Next heartbeat in {self._heartbeat_counter} cycles")
    
    # Minimal implementations for required Domoticz callbacks
    def onConnect(self, Connection, Status, Description):
        """Handle connection events (not used by this plugin)."""
        pass
    
    def onMessage(self, Connection, Data):
        """Handle messages (not used by this plugin)."""
        pass
    
    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        """Handle notifications (not used by this plugin)."""
        pass
    
    def onDisconnect(self, Connection):
        """Handle disconnection events (not used by this plugin)."""
        pass
    
    # Private helper methods
    
    def _initialize_components(self):
        """Initialize all plugin components with dependency injection."""
        self.logger.debug("Initializing plugin components...")
        
        # Create HTTP client
        self.http_client = HttpClient(self.logger)
        
        # Create API client
        self.api_client = HeatzyApiClient(self.http_client, self.logger)
        
        # Create Domoticz service
        if DOMOTICZ_AVAILABLE:
            self.domoticz_service = DomoticzService(self.logger)
        else:
            # Use mock service for testing
            from src.domoticz_service import MockDomoticzService
            self.domoticz_service = MockDomoticzService(self.logger)
        
        # Create device manager
        self.device_manager = DeviceManager(
            self.api_client,
            self.domoticz_service,
            self.logger
        )
        
        self.logger.debug("All components initialized successfully")
    
    def _authenticate(self):
        """Authenticate with Heatzy API."""
        try:
            self.logger.info("Authenticating with Heatzy API...")
            
            token = self.api_client.authenticate(
                self._credentials['username'],
                self._credentials['password']
            )
            
            self.logger.info(f"Authentication successful, token expires in {token.time_until_expiry:.0f}s")
            
        except AuthenticationError as e:
            self.logger.error(f"Authentication failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected authentication error: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def _initialize_devices(self):
        """Initialize devices from Heatzy API."""
        try:
            self.logger.info("Initializing devices...")
            
            self.device_manager.initialize_devices()
            
            device_count = self.device_manager.get_device_count()
            self.logger.info(f"Device initialization completed: {device_count} devices")
            
        except InitializationError as e:
            self.logger.error(f"Device initialization failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected initialization error: {e}")
            raise InitializationError(f"Device initialization failed: {e}")


# =============================================================================
# DOMOTICZ PLUGIN INTERFACE
# =============================================================================

# Global plugin instance
global _plugin
_plugin = BasePlugin()

def onStart():
    """Domoticz callback: Plugin start."""
    global _plugin
    _plugin.onStart()

def onStop():
    """Domoticz callback: Plugin stop."""
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    """Domoticz callback: Connection established."""
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    """Domoticz callback: Message received."""
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    """Domoticz callback: Device command."""
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    """Domoticz callback: Notification received."""
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    """Domoticz callback: Connection lost."""
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    """Domoticz callback: Periodic heartbeat."""
    global _plugin
    _plugin.onHeartbeat()


# =============================================================================
# UTILITY FUNCTIONS FOR BACKWARD COMPATIBILITY
# =============================================================================

def DumpConfigToLog():
    """Dump configuration to log (backward compatibility)."""
    if not DOMOTICZ_AVAILABLE:
        return
    
    logger = DomoticzLogger("Config")
    
    # Show parameters
    logger.debug(f"Parameters count: {len(Parameters)}")
    for key, value in Parameters.items():
        if value and key != "Password":  # Don't log password
            logger.debug(f"Parameter '{key}': '{value}'")
        elif key == "Password":
            logger.debug(f"Parameter '{key}': '***'")
    
    # Show settings
    logger.debug(f"Settings count: {len(Settings)}")
    for key, value in Settings.items():
        logger.debug(f"Setting '{key}': '{value}'")
    
    # Show devices
    logger.debug(f"Device count: {len(Devices)}")
    for unit, device in Devices.items():
        logger.debug(f"Device {unit}: {device.Name} (ID: {device.DeviceID})")


# =============================================================================
# TESTING SUPPORT
# =============================================================================

def create_test_plugin():
    """Create a plugin instance for testing."""
    # Mock Parameters for testing
    global Parameters, Settings, Devices, Images
    
    Parameters = {
        "Username": "test@example.com",
        "Password": "testpass",
        "Mode6": "62"
    }
    
    Settings = {}
    Devices = {}
    Images = {}
    
    return BasePlugin()


if __name__ == "__main__":
    # Basic testing when run directly
    print("Heatzy Pilote Plugin - Testing Mode")
    
    # Create test plugin
    test_plugin = create_test_plugin()
    
    # Test initialization
    try:
        test_plugin.onStart()
        print("Plugin initialized successfully")
    except Exception as e:
        print(f"Plugin initialization failed: {e}")
    
    print("Testing completed")