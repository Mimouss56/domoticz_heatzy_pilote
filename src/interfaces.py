#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Heatzy Pilote Plugin - Interfaces
#
# Author: Mimouss56
#

"""
Abstract interfaces for the Heatzy Pilote plugin.

This module defines the contracts that different components must implement,
following the Interface Segregation and Dependency Inversion principles.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import HeatMode, HeatzyDevice, AuthToken, DeviceStatus


class ILogger(ABC):
    """
    Interface for logging operations.
    
    Provides a simple abstraction for logging that can be implemented
    by different logging backends (Domoticz, file, console, etc.).
    """
    
    @abstractmethod
    def debug(self, message: str) -> None:
        """Log a debug message."""
        pass
    
    @abstractmethod
    def info(self, message: str) -> None:
        """Log an info message."""
        pass
    
    @abstractmethod
    def warning(self, message: str) -> None:
        """Log a warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        """Log an error message."""
        pass


class IHttpClient(ABC):
    """
    Interface for HTTP client operations.
    
    Abstracts HTTP operations to allow for different implementations
    (http.client, requests, urllib, etc.).
    """
    
    @abstractmethod
    def post(self, path: str, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Make a POST request and return parsed JSON response."""
        pass
    
    @abstractmethod
    def get(self, path: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Make a GET request and return parsed JSON response."""
        pass
    
    @abstractmethod
    def set_host(self, host: str) -> None:
        """Set the target host for requests."""
        pass


class IHeatzyApiClient(ABC):
    """
    Interface for Heatzy API operations.
    
    Defines the contract for communicating with the Heatzy cloud API.
    Implementations should handle authentication, device discovery,
    status polling, and device control.
    """
    
    @abstractmethod
    def authenticate(self, username: str, password: str) -> AuthToken:
        """
        Authenticate with Heatzy API and return auth token.
        
        Args:
            username: Heatzy account username/email
            password: Heatzy account password
            
        Returns:
            AuthToken with expiration information
            
        Raises:
            AuthenticationError: If credentials are invalid
            ApiError: If API request fails
        """
        pass
    
    @abstractmethod
    def get_devices(self) -> List[HeatzyDevice]:
        """
        Get list of devices associated with the account.
        
        Returns:
            List of HeatzyDevice objects
            
        Raises:
            AuthenticationError: If not authenticated or token expired
            ApiError: If API request fails
        """
        pass
    
    @abstractmethod
    def get_device_status(self, device_id: str) -> DeviceStatus:
        """
        Get current status of a specific device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            DeviceStatus with current mode and timestamp
            
        Raises:
            DeviceNotFoundError: If device doesn't exist
            ApiError: If API request fails
        """
        pass
    
    @abstractmethod
    def control_device(self, device_id: str, mode: HeatMode) -> bool:
        """
        Control a device by setting its mode.
        
        Args:
            device_id: Device identifier
            mode: Target heat mode
            
        Returns:
            True if command was successful, False otherwise
            
        Raises:
            DeviceNotFoundError: If device doesn't exist
            ApiError: If API request fails
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if client has a valid authentication token."""
        pass


class IDomoticzService(ABC):
    """
    Interface for Domoticz operations.
    
    Abstracts Domoticz-specific operations to allow for testing
    and potential future migration to other home automation platforms.
    """
    
    @abstractmethod
    def create_device(self, device: HeatzyDevice, unit: int) -> None:
        """
        Create a new device in Domoticz.
        
        Args:
            device: HeatzyDevice to create
            unit: Domoticz unit number
            
        Raises:
            DomoticzError: If device creation fails
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_next_unit(self) -> int:
        """
        Get the next available unit number.
        
        Returns:
            Available unit number
        """
        pass
    
    @abstractmethod
    def device_exists(self, device_id: str) -> bool:
        """
        Check if a device with given ID exists in Domoticz.
        
        Args:
            device_id: Device identifier to check
            
        Returns:
            True if device exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_device_unit(self, device_id: str) -> Optional[int]:
        """
        Get unit number for a device ID.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Unit number if device exists, None otherwise
        """
        pass


class IDeviceManager(ABC):
    """
    Interface for device management operations.
    
    Defines high-level device management operations that coordinate
    between the API client and Domoticz service.
    """
    
    @abstractmethod
    def initialize_devices(self) -> None:
        """
        Initialize devices from Heatzy API into Domoticz.
        
        Discovers devices from API and creates missing ones in Domoticz.
        
        Raises:
            InitializationError: If initialization fails
        """
        pass
    
    @abstractmethod
    def sync_device_status(self) -> None:
        """
        Synchronize device status from API to Domoticz.
        
        Polls all devices and updates their status in Domoticz.
        
        Raises:
            SyncError: If synchronization fails
        """
        pass
    
    @abstractmethod
    def control_device(self, unit: int, level: int) -> bool:
        """
        Control device via API and update Domoticz.
        
        Args:
            unit: Domoticz unit number
            level: Target level (0-30)
            
        Returns:
            True if command was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_device_count(self) -> int:
        """
        Get number of managed devices.
        
        Returns:
            Number of devices currently managed
        """
        pass


# Custom exceptions for better error handling
class HeatzyPluginError(Exception):
    """Base exception for Heatzy plugin errors."""
    pass


class AuthenticationError(HeatzyPluginError):
    """Raised when authentication fails."""
    pass


class ApiError(HeatzyPluginError):
    """Raised when API requests fail."""
    pass


class DeviceNotFoundError(HeatzyPluginError):
    """Raised when a device is not found."""
    pass


class DomoticzError(HeatzyPluginError):
    """Raised when Domoticz operations fail."""
    pass


class InitializationError(HeatzyPluginError):
    """Raised when device initialization fails."""
    pass


class SyncError(HeatzyPluginError):
    """Raised when device synchronization fails."""
    pass