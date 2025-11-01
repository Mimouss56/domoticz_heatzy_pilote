#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Improved Heatzy Pilote Plugin
#
# Author: Mimouss56
#
"""
<plugin key="heatzy_pilote" name="Heatzy pilote" author="Mimouss" version="1.0.0">
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

import Domoticz
import json
import http.client
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# DOMAIN MODELS (Single Responsibility + Value Objects)
# =============================================================================

class HeatMode(Enum):
    """Enum for heat modes - ensures type safety and extensibility"""
    OFF = ("off", 0, 0)
    FREEZE = ("fro", 2, 10)
    ECO = ("eco", 1, 20)
    COMFORT = ("cft", 0, 30)
    
    def __init__(self, api_value: str, api_mode: int, domoticz_level: int):
        self.api_value = api_value
        self.api_mode = api_mode
        self.domoticz_level = domoticz_level
    
    @classmethod
    def from_api_mode(cls, mode: int) -> 'HeatMode':
        for heat_mode in cls:
            if heat_mode.api_mode == mode:
                return heat_mode
        raise ValueError(f"Unknown mode: {mode}")
    
    @classmethod
    def from_api_value(cls, value: str) -> 'HeatMode':
        for heat_mode in cls:
            if heat_mode.api_value == value:
                return heat_mode
        raise ValueError(f"Unknown mode: {value}")
    
    @classmethod
    def from_domoticz_level(cls, level: int) -> 'HeatMode':
        for heat_mode in cls:
            if heat_mode.domoticz_level == level:
                return heat_mode
        raise ValueError(f"Unknown level: {level}")


@dataclass
class HeatzyDevice:
    """Value object representing a Heatzy device"""
    did: str
    dev_alias: str
    product_key: str
    
    def __post_init__(self):
        if not self.did or not self.dev_alias:
            raise ValueError("Device ID and alias are required")


@dataclass
class AuthToken:
    """Value object for authentication token with expiration logic"""
    token: str
    expires_at: float
    
    @classmethod
    def create(cls, token: str, ttl_seconds: int = 3600) -> 'AuthToken':
        return cls(token, time.time() + ttl_seconds)
    
    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at - 100  # 100s buffer


# =============================================================================
# INTERFACES (Interface Segregation Principle)
# =============================================================================

class IHeatzyApiClient(ABC):
    """Interface for Heatzy API operations"""
    
    @abstractmethod
    def authenticate(self, username: str, password: str) -> AuthToken:
        pass
    
    @abstractmethod
    def get_devices(self) -> List[HeatzyDevice]:
        pass
    
    @abstractmethod
    def get_device_status(self, device_id: str) -> HeatMode:
        pass
    
    @abstractmethod
    def control_device(self, device_id: str, mode: HeatMode) -> bool:
        pass


class IDomoticzService(ABC):
    """Interface for Domoticz operations"""
    
    @abstractmethod
    def create_device(self, device: HeatzyDevice, unit: int) -> None:
        pass
    
    @abstractmethod
    def update_device(self, unit: int, mode: HeatMode) -> None:
        pass
    
    @abstractmethod
    def get_next_unit(self) -> int:
        pass


class ILogger(ABC):
    """Interface for logging operations"""
    
    @abstractmethod
    def debug(self, message: str) -> None:
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        pass


# =============================================================================
# HTTP CLIENT (Single Responsibility)
# =============================================================================

class HttpClient:
    """Responsible only for HTTP operations"""
    
    def __init__(self, host: str, logger: ILogger):
        self.host = host
        self.logger = logger
    
    def post(self, path: str, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Make POST request and return parsed JSON response"""
        try:
            conn = http.client.HTTPSConnection(self.host)
            json_data = json.dumps(data)
            conn.request("POST", path, json_data, headers)
            response = conn.getresponse()
            
            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {response.reason}")
            
            data = response.read()
            conn.close()
            return json.loads(data.decode("utf-8"))
            
        except Exception as e:
            self.logger.error(f"POST request failed: {e}")
            raise
    
    def get(self, path: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Make GET request and return parsed JSON response"""
        try:
            conn = http.client.HTTPSConnection(self.host)
            conn.request("GET", path, headers=headers)
            response = conn.getresponse()
            
            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {response.reason}")
            
            data = response.read()
            conn.close()
            return json.loads(data.decode("utf-8"))
            
        except Exception as e:
            self.logger.error(f"GET request failed: {e}")
            raise


# =============================================================================
# API CLIENT (Single Responsibility + Dependency Inversion)
# =============================================================================

class HeatzyApiClient(IHeatzyApiClient):
    """Responsible only for Heatzy API communication"""
    
    API_HOST = 'euapi.gizwits.com'
    APPLICATION_ID = 'c70a66ff039d41b4a220e198b0fcc8b3'
    
    def __init__(self, http_client: HttpClient, logger: ILogger):
        self.http_client = http_client
        self.logger = logger
        self._auth_token: Optional[AuthToken] = None
    
    def authenticate(self, username: str, password: str) -> AuthToken:
        """Authenticate and return token"""
        data = {
            'username': username,
            'password': password,
            'lang': 'en'
        }
        headers = self._get_base_headers()
        
        response = self.http_client.post("/app/login", data, headers)
        token = AuthToken.create(response['token'])
        self._auth_token = token
        return token
    
    def get_devices(self) -> List[HeatzyDevice]:
        """Get list of devices"""
        headers = self._get_authenticated_headers()
        response = self.http_client.get("/app/bindings", headers)
        
        devices = []
        for device_data in response.get("devices", []):
            try:
                device = HeatzyDevice(
                    did=device_data['did'],
                    dev_alias=device_data['dev_alias'],
                    product_key=device_data.get('product_key', '')
                )
                devices.append(device)
            except ValueError as e:
                self.logger.error(f"Invalid device data: {e}")
        
        return devices
    
    def get_device_status(self, device_id: str) -> HeatMode:
        """Get device status"""
        headers = self._get_authenticated_headers()
        response = self.http_client.get(f"/app/devdata/{device_id}/latest", headers)
        
        mode = response["attr"]["mode"]
        return HeatMode.from_api_value(mode)
    
    def control_device(self, device_id: str, mode: HeatMode) -> bool:
        """Control device mode"""
        data = {"attrs": {"mode": mode.api_mode}}
        headers = self._get_authenticated_headers()
        headers["Content-Type"] = "application/json"
        
        try:
            self.http_client.post(f"/app/control/{device_id}", data, headers)
            return True
        except Exception as e:
            self.logger.error(f"Failed to control device {device_id}: {e}")
            return False
    
    def _get_base_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "X-Gizwits-Application-Id": self.APPLICATION_ID
        }
    
    def _get_authenticated_headers(self) -> Dict[str, str]:
        if not self._auth_token or self._auth_token.is_expired:
            raise Exception("No valid authentication token")
        
        headers = self._get_base_headers()
        headers["X-Gizwits-User-token"] = self._auth_token.token
        return headers
    
    def _ensure_authenticated(self, username: str, password: str) -> None:
        """Ensure we have a valid token"""
        if not self._auth_token or self._auth_token.is_expired:
            self.authenticate(username, password)


# =============================================================================
# DOMOTICZ SERVICE (Single Responsibility + Dependency Inversion)
# =============================================================================

class DomoticzService(IDomoticzService):
    """Responsible only for Domoticz operations"""
    
    def __init__(self, logger: ILogger):
        self.logger = logger
    
    def create_device(self, device: HeatzyDevice, unit: int) -> None:
        """Create a new device in Domoticz"""
        options = {
            "LevelActions": "||||",
            "LevelNames": "Off|Hors gel|Eco|Confort",
            "LevelOffHidden": "false",
            "SelectorStyle": "0"
        }
        
        Domoticz.Device(
            Name=device.dev_alias,
            Unit=unit,
            DeviceID=device.did,
            TypeName="Selector Switch",
            Options=options,
            Switchtype=18,
            Image=15
        ).Create()
        
        self.logger.debug(f"Created device: {device.dev_alias} (Unit: {unit})")
    
    def update_device(self, unit: int, mode: HeatMode) -> None:
        """Update device status"""
        if unit not in Devices:
            self.logger.error(f"Device unit {unit} not found")
            return
        
        nvalue = 1 if mode != HeatMode.OFF else 0
        svalue = str(mode.domoticz_level)
        
        if (Devices[unit].nValue != nvalue or 
            Devices[unit].sValue != svalue):
            Devices[unit].Update(nValue=nvalue, sValue=svalue)
            self.logger.debug(f"Updated device {unit}: {mode.name}")
    
    def get_next_unit(self) -> int:
        """Get next available unit number"""
        used_units = [device.ID for device in Devices.values()]
        unit = 1
        while unit in used_units:
            unit += 1
        return unit


# =============================================================================
# LOGGER IMPLEMENTATION
# =============================================================================

class DomoticzLogger(ILogger):
    """Domoticz logger implementation"""
    
    def debug(self, message: str) -> None:
        Domoticz.Debug(message)
    
    def error(self, message: str) -> None:
        Domoticz.Error(message)


# =============================================================================
# DEVICE MANAGER (Single Responsibility)
# =============================================================================

class DeviceManager:
    """Manages device operations and synchronization"""
    
    def __init__(self, api_client: IHeatzyApiClient, domoticz_service: IDomoticzService, logger: ILogger):
        self.api_client = api_client
        self.domoticz_service = domoticz_service
        self.logger = logger
    
    def initialize_devices(self) -> None:
        """Initialize devices from Heatzy API"""
        try:
            devices = self.api_client.get_devices()
            existing_device_ids = {device.DeviceID for device in Devices.values()}
            
            for device in devices:
                if device.did not in existing_device_ids:
                    unit = self.domoticz_service.get_next_unit()
                    self.domoticz_service.create_device(device, unit)
                    
        except Exception as e:
            self.logger.error(f"Failed to initialize devices: {e}")
    
    def sync_device_status(self) -> None:
        """Synchronize device status from API"""
        try:
            for device in Devices.values():
                try:
                    mode = self.api_client.get_device_status(device.DeviceID)
                    self.domoticz_service.update_device(device.ID, mode)
                except Exception as e:
                    self.logger.error(f"Failed to sync device {device.DeviceID}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to sync devices: {e}")
    
    def control_device(self, unit: int, level: int) -> bool:
        """Control device via API"""
        if unit not in Devices:
            self.logger.error(f"Device unit {unit} not found")
            return False
        
        try:
            mode = HeatMode.from_domoticz_level(level)
            device_id = Devices[unit].DeviceID
            success = self.api_client.control_device(device_id, mode)
            
            if success:
                self.domoticz_service.update_device(unit, mode)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to control device {unit}: {e}")
            return False


# =============================================================================
# MAIN PLUGIN CLASS (Orchestrator - Open/Closed Principle)
# =============================================================================

class BasePlugin:
    """Main plugin class - orchestrates components"""
    
    HEARTBEAT_INTERVAL = 3  # minutes
    
    def __init__(self):
        # Dependency injection setup
        self.logger = DomoticzLogger()
        self.http_client = HttpClient(HeatzyApiClient.API_HOST, self.logger)
        self.api_client = HeatzyApiClient(self.http_client, self.logger)
        self.domoticz_service = DomoticzService(self.logger)
        self.device_manager = DeviceManager(self.api_client, self.domoticz_service, self.logger)
        
        self.__runAgain = 0
    
    def onStart(self):
        """Plugin startup"""
        self.logger.debug("Plugin starting...")
        
        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
        
        try:
            # Authenticate
            self.api_client.authenticate(
                Parameters["Username"], 
                Parameters["Password"]
            )
            
            # Initialize devices
            self.device_manager.initialize_devices()
            
        except Exception as e:
            self.logger.error(f"Plugin startup failed: {e}")
    
    def onCommand(self, Unit, Command, Level, Hue):
        """Handle device commands"""
        self.logger.debug(f"Command for Unit {Unit}: {Command}, Level: {Level}")
        
        if Command == 'Set Level':
            success = self.device_manager.control_device(Unit, Level)
            if not success:
                self.logger.error(f"Failed to execute command for unit {Unit}")
    
    def onHeartbeat(self):
        """Periodic sync"""
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            self.__runAgain = self.HEARTBEAT_INTERVAL
            
            try:
                # Re-authenticate if needed
                self.api_client._ensure_authenticated(
                    Parameters["Username"], 
                    Parameters["Password"]
                )
                
                # Sync device status
                self.device_manager.sync_device_status()
                
            except Exception as e:
                self.logger.error(f"Heartbeat failed: {e}")
        else:
            self.logger.debug(f"Next heartbeat in {self.__runAgain} cycles")
    
    # Minimal implementations for required methods
    def onStop(self): pass
    def onConnect(self, Connection, Status, Description): pass
    def onMessage(self, Connection, Data): pass
    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile): pass
    def onDisconnect(self, Connection): pass


# =============================================================================
# GLOBAL PLUGIN INSTANCE AND CALLBACKS
# =============================================================================

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()