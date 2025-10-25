#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Heatzy Pilote Plugin - Domoticz Service
#
# Author: Mimouss56
#

"""
Domoticz service implementation.

This module provides the implementation for Domoticz-specific operations,
abstracting the Domoticz API to allow for better testing and maintenance.
"""

from typing import Optional, Dict, Any
from .models import HeatMode, HeatzyDevice
from .interfaces import IDomoticzService, ILogger, DomoticzError, DeviceNotFoundError

# Import Domoticz module (available when running in Domoticz)
try:
    import Domoticz
    DOMOTICZ_AVAILABLE = True
except ImportError:
    DOMOTICZ_AVAILABLE = False


class DomoticzService(IDomoticzService):
    """
    Domoticz service implementation.
    
    Responsible only for Domoticz operations with proper error handling
    and validation.
    """
    
    # Domoticz device configuration
    SELECTOR_SWITCH_TYPE = "Selector Switch"
    SWITCH_TYPE_ID = 18
    DEVICE_IMAGE_ID = 15
    
    def __init__(self, logger: ILogger):
        """
        Initialize Domoticz service.
        
        Args:
            logger: Logger instance
            
        Raises:
            DomoticzError: If Domoticz module is not available
        """
        if not DOMOTICZ_AVAILABLE:
            raise DomoticzError("Domoticz module not available")
        
        self.logger = logger
    
    def create_device(self, device: HeatzyDevice, unit: int) -> None:
        """
        Create a new device in Domoticz.
        
        Args:
            device: HeatzyDevice to create
            unit: Domoticz unit number
            
        Raises:
            DomoticzError: If device creation fails
        """
        if not device:
            raise ValueError("Device is required")
        if unit < 1:
            raise ValueError("Unit must be positive")
        
        try:
            # Check if unit is already used
            if self._unit_exists(unit):
                raise DomoticzError(f"Unit {unit} already exists")
            
            options = self._get_device_options()
            
            self.logger.info(f"Creating device: {device.safe_name} (Unit: {unit})")
            
            Domoticz.Device(
                Name=device.safe_name,
                Unit=unit,
                DeviceID=device.did,
                TypeName=self.SELECTOR_SWITCH_TYPE,
                Options=options,
                Switchtype=self.SWITCH_TYPE_ID,
                Image=self.DEVICE_IMAGE_ID
            ).Create()
            
            self.logger.info(f"Successfully created device: {device.safe_name}")
            
        except Exception as e:
            error_msg = f"Failed to create device {device.safe_name}: {e}"
            self.logger.error(error_msg)
            raise DomoticzError(error_msg)
    
    def update_device(self, unit: int, mode: HeatMode) -> None:
        """
        Update device status in Domoticz.
        
        Args:
            unit: Domoticz unit number
            mode: New heat mode
            
        Raises:
            DeviceNotFoundError: If unit doesn't exist
            DomoticzError: If update fails
        """
        if not self._unit_exists(unit):
            raise DeviceNotFoundError(f"Device unit {unit} not found")
        
        try:
            device = Devices[unit]
            
            # Calculate nValue and sValue based on mode
            nvalue = 1 if mode != HeatMode.OFF else 0
            svalue = str(mode.domoticz_level)
            
            # Only update if values have changed
            if (device.nValue != nvalue or 
                device.sValue != svalue or 
                device.TimedOut != 0):
                
                device.Update(
                    nValue=nvalue, 
                    sValue=svalue, 
                    TimedOut=0
                )
                
                self.logger.debug(
                    f"Updated device {unit} ({device.Name}): "
                    f"{mode.display_name} (nValue={nvalue}, sValue={svalue})"
                )
            else:
                self.logger.debug(f"Device {unit} already up to date: {mode.display_name}")
                
        except Exception as e:
            error_msg = f"Failed to update device {unit}: {e}"
            self.logger.error(error_msg)
            raise DomoticzError(error_msg)
    
    def get_next_unit(self) -> int:
        """
        Get the next available unit number.
        
        Returns:
            Available unit number
        """
        if not DOMOTICZ_AVAILABLE:
            return 1
        
        try:
            used_units = {device.ID for device in Devices.values()}
            unit = 1
            while unit in used_units:
                unit += 1
            
            self.logger.debug(f"Next available unit: {unit}")
            return unit
            
        except Exception as e:
            self.logger.error(f"Error finding next unit: {e}")
            return 1
    
    def device_exists(self, device_id: str) -> bool:
        """
        Check if a device with given ID exists in Domoticz.
        
        Args:
            device_id: Device identifier to check
            
        Returns:
            True if device exists, False otherwise
        """
        if not DOMOTICZ_AVAILABLE:
            return False
        
        try:
            for device in Devices.values():
                if device.DeviceID == device_id:
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking device existence: {e}")
            return False
    
    def get_device_unit(self, device_id: str) -> Optional[int]:
        """
        Get unit number for a device ID.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Unit number if device exists, None otherwise
        """
        if not DOMOTICZ_AVAILABLE:
            return None
        
        try:
            for device in Devices.values():
                if device.DeviceID == device_id:
                    return device.ID
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting device unit: {e}")
            return None
    
    def get_all_device_ids(self) -> Dict[str, int]:
        """
        Get mapping of all device IDs to their unit numbers.
        
        Returns:
            Dictionary mapping device IDs to unit numbers
        """
        if not DOMOTICZ_AVAILABLE:
            return {}
        
        try:
            device_map = {}
            for device in Devices.values():
                if hasattr(device, 'DeviceID') and device.DeviceID:
                    device_map[device.DeviceID] = device.ID
            
            self.logger.debug(f"Found {len(device_map)} existing devices")
            return device_map
            
        except Exception as e:
            self.logger.error(f"Error getting device mapping: {e}")
            return {}
    
    def set_device_timeout(self, unit: int, timeout: bool = True) -> None:
        """
        Set device timeout status.
        
        Args:
            unit: Domoticz unit number
            timeout: True to mark as timed out, False to clear timeout
        """
        if not self._unit_exists(unit):
            self.logger.warning(f"Cannot set timeout for non-existent unit {unit}")
            return
        
        try:
            device = Devices[unit]
            timeout_value = 1 if timeout else 0
            
            if device.TimedOut != timeout_value:
                device.Update(
                    nValue=device.nValue,
                    sValue=device.sValue,
                    TimedOut=timeout_value
                )
                
                status = "timed out" if timeout else "online"
                self.logger.debug(f"Device {unit} marked as {status}")
                
        except Exception as e:
            self.logger.error(f"Failed to set timeout for device {unit}: {e}")
    
    def _unit_exists(self, unit: int) -> bool:
        """Check if a unit exists in Domoticz."""
        if not DOMOTICZ_AVAILABLE:
            return False
        return unit in Devices
    
    def _get_device_options(self) -> Dict[str, str]:
        """Get device options for selector switch."""
        return {
            "LevelActions": "||||",
            "LevelNames": "Arrêt|Hors gel|Eco|Confort",
            "LevelOffHidden": "false",
            "SelectorStyle": "0"
        }


class MockDomoticzService(IDomoticzService):
    """
    Mock Domoticz service for testing.
    
    Provides a test implementation that doesn't require the Domoticz module.
    """
    
    def __init__(self, logger: ILogger):
        """Initialize mock service."""
        self.logger = logger
        self._devices: Dict[int, Dict[str, Any]] = {}
        self._next_unit = 1
    
    def create_device(self, device: HeatzyDevice, unit: int) -> None:
        """Mock device creation."""
        if unit in self._devices:
            raise DomoticzError(f"Unit {unit} already exists")
        
        self._devices[unit] = {
            'name': device.safe_name,
            'device_id': device.did,
            'nvalue': 0,
            'svalue': '0',
            'timeout': 0
        }
        
        self.logger.info(f"Mock: Created device {device.safe_name} at unit {unit}")
    
    def update_device(self, unit: int, mode: HeatMode) -> None:
        """Mock device update."""
        if unit not in self._devices:
            raise DeviceNotFoundError(f"Device unit {unit} not found")
        
        nvalue = 1 if mode != HeatMode.OFF else 0
        svalue = str(mode.domoticz_level)
        
        self._devices[unit]['nvalue'] = nvalue
        self._devices[unit]['svalue'] = svalue
        self._devices[unit]['timeout'] = 0
        
        self.logger.debug(f"Mock: Updated device {unit} to {mode.display_name}")
    
    def get_next_unit(self) -> int:
        """Get next available unit number."""
        while self._next_unit in self._devices:
            self._next_unit += 1
        return self._next_unit
    
    def device_exists(self, device_id: str) -> bool:
        """Check if device exists."""
        return any(
            device['device_id'] == device_id 
            for device in self._devices.values()
        )
    
    def get_device_unit(self, device_id: str) -> Optional[int]:
        """Get device unit."""
        for unit, device in self._devices.items():
            if device['device_id'] == device_id:
                return unit
        return None