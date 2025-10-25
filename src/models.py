#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Heatzy Pilote Plugin - Domain Models
#
# Author: Mimouss56
#

"""
Domain models and value objects for the Heatzy Pilote plugin.

This module contains the core domain models that represent the business logic
and data structures used throughout the application.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class HeatMode(Enum):
    """
    Enum for heat modes - ensures type safety and extensibility.
    
    Each mode contains:
    - api_value: String value used by Heatzy API
    - api_mode: Integer mode used by Heatzy API  
    - domoticz_level: Level used by Domoticz selector switch
    """
    OFF = ("off", 3, 0)
    FREEZE = ("fro", 2, 10)
    ECO = ("eco", 1, 20)
    COMFORT = ("cft", 0, 30)
    
    def __init__(self, api_value: str, api_mode: int, domoticz_level: int):
        self.api_value = api_value
        self.api_mode = api_mode
        self.domoticz_level = domoticz_level
    
    @classmethod
    def from_api_mode(cls, mode: int) -> 'HeatMode':
        """Create HeatMode from API mode integer."""
        for heat_mode in cls:
            if heat_mode.api_mode == mode:
                return heat_mode
        raise ValueError(f"Unknown API mode: {mode}")
    
    @classmethod
    def from_domoticz_level(cls, level: int) -> 'HeatMode':
        """Create HeatMode from Domoticz level."""
        for heat_mode in cls:
            if heat_mode.domoticz_level == level:
                return heat_mode
        raise ValueError(f"Unknown Domoticz level: {level}")
    
    @property
    def display_name(self) -> str:
        """Get user-friendly display name."""
        names = {
            HeatMode.OFF: "Arrêt",
            HeatMode.FREEZE: "Hors gel", 
            HeatMode.ECO: "Eco",
            HeatMode.COMFORT: "Confort"
        }
        return names[self]


@dataclass(frozen=True)
class HeatzyDevice:
    """
    Value object representing a Heatzy device.
    
    Immutable representation of a device with validation.
    """
    did: str
    dev_alias: str
    product_key: str = ""
    
    def __post_init__(self):
        """Validate device data after initialization."""
        if not self.did:
            raise ValueError("Device ID (did) is required")
        if not self.dev_alias:
            raise ValueError("Device alias (dev_alias) is required")
        if len(self.did) < 10:  # Basic validation
            raise ValueError("Device ID seems invalid (too short)")
    
    @property
    def safe_name(self) -> str:
        """Get a safe name for Domoticz (no special characters)."""
        import re
        # Remove or replace special characters
        safe = re.sub(r'[^\w\s-]', '', self.dev_alias)
        return safe.strip() or f"Device_{self.did[:8]}"


@dataclass(frozen=True)
class AuthToken:
    """
    Value object for authentication token with expiration logic.
    
    Immutable token representation with automatic expiration handling.
    """
    token: str
    expires_at: float
    
    # Default TTL for tokens (1 hour)
    DEFAULT_TTL: ClassVar[int] = 3600
    # Safety buffer before expiration (100 seconds)
    EXPIRY_BUFFER: ClassVar[int] = 100
    
    @classmethod
    def create(cls, token: str, ttl_seconds: int = None) -> 'AuthToken':
        """
        Create a new AuthToken with expiration time.
        
        Args:
            token: The authentication token string
            ttl_seconds: Time to live in seconds (default: 1 hour)
        """
        if not token:
            raise ValueError("Token cannot be empty")
        
        ttl = ttl_seconds or cls.DEFAULT_TTL
        expires_at = time.time() + ttl
        return cls(token, expires_at)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired or about to expire."""
        return time.time() >= (self.expires_at - self.EXPIRY_BUFFER)
    
    @property
    def time_until_expiry(self) -> float:
        """Get seconds until token expires."""
        return max(0, self.expires_at - time.time())
    
    def __str__(self) -> str:
        """String representation (hides token value for security)."""
        return f"AuthToken(expires_in={self.time_until_expiry:.0f}s)"


@dataclass(frozen=True)
class DeviceStatus:
    """
    Value object representing the current status of a device.
    
    Used for status synchronization between API and Domoticz.
    """
    device_id: str
    mode: HeatMode
    last_updated: float
    online: bool = True
    
    @classmethod
    def create(cls, device_id: str, mode: HeatMode) -> 'DeviceStatus':
        """Create a new device status with current timestamp."""
        return cls(
            device_id=device_id,
            mode=mode,
            last_updated=time.time(),
            online=True
        )
    
    @property
    def age_seconds(self) -> float:
        """Get age of this status in seconds."""
        return time.time() - self.last_updated
    
    @property
    def is_stale(self, max_age_seconds: int = 300) -> bool:
        """Check if status is stale (older than max_age_seconds)."""
        return self.age_seconds > max_age_seconds