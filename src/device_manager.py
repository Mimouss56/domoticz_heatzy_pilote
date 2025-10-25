#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Heatzy Pilote Plugin - Device Manager
#
# Author: Mimouss56
#

"""
Device manager implementation.

This module provides high-level device management operations that coordinate
between the Heatzy API client and Domoticz service.
"""

from typing import Dict, Set, Optional
from .models import HeatMode, HeatzyDevice, DeviceStatus
from .interfaces import (
    IDeviceManager, IHeatzyApiClient, IDomoticzService, ILogger,
    InitializationError, SyncError, DeviceNotFoundError
)


class DeviceManager(IDeviceManager):
    """
    Device manager implementation.
    
    Coordinates between API client and Domoticz service to manage devices,
    handle synchronization, and execute commands.
    """
    
    def __init__(
        self, 
        api_client: IHeatzyApiClient, 
        domoticz_service: IDomoticzService, 
        logger: ILogger
    ):
        """
        Initialize device manager.
        
        Args:
            api_client: Heatzy API client
            domoticz_service: Domoticz service
            logger: Logger instance
        """
        self.api_client = api_client
        self.domoticz_service = domoticz_service
        self.logger = logger
        
        # Cache for device mapping and status
        self._device_cache: Dict[str, HeatzyDevice] = {}
        self._status_cache: Dict[str, DeviceStatus] = {}
        self._unit_mapping: Dict[str, int] = {}
    
    def initialize_devices(self) -> None:
        """
        Initialize devices from Heatzy API into Domoticz.
        
        Discovers devices from API and creates missing ones in Domoticz.
        
        Raises:
            InitializationError: If initialization fails
        """
        try:
            self.logger.info("Starting device initialization...")
            
            # Get devices from API
            api_devices = self.api_client.get_devices()
            if not api_devices:
                self.logger.warning("No devices found in Heatzy API")
                return
            
            # Get existing devices from Domoticz
            existing_device_ids = set(self.domoticz_service.get_all_device_ids().keys())
            
            # Create missing devices
            created_count = 0
            for device in api_devices:
                try:
                    # Cache the device
                    self._device_cache[device.did] = device
                    
                    if device.did not in existing_device_ids:
                        # Device doesn't exist in Domoticz, create it
                        unit = self.domoticz_service.get_next_unit()
                        self.domoticz_service.create_device(device, unit)
                        self._unit_mapping[device.did] = unit
                        created_count += 1
                        
                        self.logger.info(f"Created device: {device.safe_name} (Unit: {unit})")
                    else:
                        # Device exists, update mapping
                        unit = self.domoticz_service.get_device_unit(device.did)
                        if unit:
                            self._unit_mapping[device.did] = unit
                        
                except Exception as e:
                    self.logger.error(f"Failed to initialize device {device.safe_name}: {e}")
                    continue
            
            self.logger.info(
                f"Device initialization complete. "
                f"Found {len(api_devices)} devices, created {created_count} new devices"
            )
            
        except Exception as e:
            error_msg = f"Device initialization failed: {e}"
            self.logger.error(error_msg)
            raise InitializationError(error_msg)
    
    def sync_device_status(self) -> None:
        """
        Synchronize device status from API to Domoticz.
        
        Polls all devices and updates their status in Domoticz.
        
        Raises:
            SyncError: If synchronization fails
        """
        if not self._unit_mapping:
            self.logger.warning("No devices to sync (run initialize_devices first)")
            return
        
        try:
            self.logger.debug("Starting device status synchronization...")
            
            sync_count = 0
            error_count = 0
            
            for device_id, unit in self._unit_mapping.items():
                try:
                    # Get current status from API
                    status = self.api_client.get_device_status(device_id)
                    
                    # Cache the status
                    self._status_cache[device_id] = status
                    
                    # Update device in Domoticz
                    self.domoticz_service.update_device(unit, status.mode)
                    
                    # Clear timeout if device is online
                    if status.online:
                        self.domoticz_service.set_device_timeout(unit, False)
                    
                    sync_count += 1
                    self.logger.debug(
                        f"Synced device {device_id} (Unit: {unit}): {status.mode.display_name}"
                    )
                    
                except DeviceNotFoundError:
                    self.logger.warning(f"Device {device_id} not found in API, marking as offline")
                    self.domoticz_service.set_device_timeout(unit, True)
                    error_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to sync device {device_id}: {e}")
                    self.domoticz_service.set_device_timeout(unit, True)
                    error_count += 1
            
            self.logger.debug(
                f"Status synchronization complete. "
                f"Synced {sync_count} devices, {error_count} errors"
            )
            
        except Exception as e:
            error_msg = f"Device synchronization failed: {e}"
            self.logger.error(error_msg)
            raise SyncError(error_msg)
    
    def control_device(self, unit: int, level: int) -> bool:
        """
        Control device via API and update Domoticz.
        
        Args:
            unit: Domoticz unit number
            level: Target level (0-30)
            
        Returns:
            True if command was successful, False otherwise
        """
        try:
            # Find device ID for this unit
            device_id = self._find_device_id_by_unit(unit)
            if not device_id:
                self.logger.error(f"No device found for unit {unit}")
                return False
            
            # Convert level to heat mode
            try:
                mode = HeatMode.from_domoticz_level(level)
            except ValueError as e:
                self.logger.error(f"Invalid level {level} for unit {unit}: {e}")
                return False
            
            self.logger.info(f"Controlling device {device_id} (Unit: {unit}): {mode.display_name}")
            
            # Send command to API
            success = self.api_client.control_device(device_id, mode)
            
            if success:
                # Update device in Domoticz to reflect new state
                self.domoticz_service.update_device(unit, mode)
                
                # Update status cache
                status = DeviceStatus.create(device_id, mode)
                self._status_cache[device_id] = status
                
                self.logger.info(f"Successfully controlled device {device_id}")
                return True
            else:
                self.logger.error(f"Failed to control device {device_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error controlling device unit {unit}: {e}")
            return False
    
    def get_device_count(self) -> int:
        """
        Get number of managed devices.
        
        Returns:
            Number of devices currently managed
        """
        return len(self._unit_mapping)
    
    def get_device_info(self, unit: int) -> Optional[Dict[str, str]]:
        """
        Get device information for a unit.
        
        Args:
            unit: Domoticz unit number
            
        Returns:
            Device information dict or None if not found
        """
        device_id = self._find_device_id_by_unit(unit)
        if not device_id:
            return None
        
        device = self._device_cache.get(device_id)
        status = self._status_cache.get(device_id)
        
        info = {
            'device_id': device_id,
            'unit': str(unit)
        }
        
        if device:
            info.update({
                'name': device.safe_name,
                'alias': device.dev_alias
            })
        
        if status:
            info.update({
                'mode': status.mode.display_name,
                'last_updated': str(status.last_updated),
                'online': str(status.online)
            })
        
        return info
    
    def refresh_device_cache(self) -> None:
        """Refresh device cache from API."""
        try:
            self.logger.debug("Refreshing device cache...")
            
            devices = self.api_client.get_devices()
            self._device_cache.clear()
            
            for device in devices:
                self._device_cache[device.did] = device
            
            self.logger.debug(f"Refreshed cache with {len(devices)} devices")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh device cache: {e}")
    
    def clear_status_cache(self) -> None:
        """Clear status cache to force fresh polling."""
        self._status_cache.clear()
        self.logger.debug("Status cache cleared")
    
    def get_cached_status(self, device_id: str) -> Optional[DeviceStatus]:
        """
        Get cached status for a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Cached status or None if not found
        """
        return self._status_cache.get(device_id)
    
    def _find_device_id_by_unit(self, unit: int) -> Optional[str]:
        """Find device ID by Domoticz unit number."""
        for device_id, mapped_unit in self._unit_mapping.items():
            if mapped_unit == unit:
                return device_id
        
        # Fallback: check Domoticz service directly
        try:
            for device_id in self._device_cache.keys():
                mapped_unit = self.domoticz_service.get_device_unit(device_id)
                if mapped_unit == unit:
                    self._unit_mapping[device_id] = unit  # Update cache
                    return device_id
        except Exception as e:
            self.logger.debug(f"Error in fallback device lookup: {e}")
        
        return None
    
    def _rebuild_unit_mapping(self) -> None:
        """Rebuild unit mapping from Domoticz service."""
        try:
            self._unit_mapping.clear()
            device_map = self.domoticz_service.get_all_device_ids()
            
            for device_id, unit in device_map.items():
                if device_id in self._device_cache:
                    self._unit_mapping[device_id] = unit
            
            self.logger.debug(f"Rebuilt unit mapping: {len(self._unit_mapping)} devices")
            
        except Exception as e:
            self.logger.error(f"Failed to rebuild unit mapping: {e}")


class MockDeviceManager(IDeviceManager):
    """
    Mock device manager for testing.
    
    Provides a test implementation that simulates device management
    without requiring real API or Domoticz connections.
    """
    
    def __init__(self, logger: ILogger):
        """Initialize mock device manager."""
        self.logger = logger
        self._devices: Dict[str, HeatzyDevice] = {}
        self._statuses: Dict[str, DeviceStatus] = {}
        self._initialized = False
    
    def initialize_devices(self) -> None:
        """Mock device initialization."""
        self.logger.info("Mock: Initializing devices...")
        self._initialized = True
    
    def sync_device_status(self) -> None:
        """Mock status synchronization."""
        if not self._initialized:
            raise SyncError("Devices not initialized")
        self.logger.debug("Mock: Syncing device status...")
    
    def control_device(self, unit: int, level: int) -> bool:
        """Mock device control."""
        try:
            mode = HeatMode.from_domoticz_level(level)
            self.logger.info(f"Mock: Controlling unit {unit} to {mode.display_name}")
            return True
        except ValueError:
            return False
    
    def get_device_count(self) -> int:
        """Get mock device count."""
        return len(self._devices)