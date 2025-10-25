#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Heatzy Pilote Plugin - Module initialization
#
# Author: Mimouss56
#

"""
Heatzy Pilote Plugin for Domoticz

This module provides a clean, SOLID-compliant implementation for controlling
Heatzy Pilote heating devices through Domoticz.

The module is organized as follows:
- models: Domain models and value objects
- interfaces: Abstract interfaces for dependency inversion
- api: Heatzy API client implementation
- domoticz_service: Domoticz-specific operations
- device_manager: Device management and synchronization
- logger: Logging utilities
"""

__version__ = "1.2.0"
__author__ = "Mimouss56"

# Make main classes available at package level
from .models import HeatMode, HeatzyDevice, AuthToken
from .interfaces import (
    IHeatzyApiClient, IDomoticzService, ILogger,
    AuthenticationError, ApiError, InitializationError, SyncError
)
from .api import HttpClient, HeatzyApiClient
from .domoticz_service import DomoticzService
from .device_manager import DeviceManager
from .logger import DomoticzLogger

__all__ = [
    'HeatMode',
    'HeatzyDevice', 
    'AuthToken',
    'IHeatzyApiClient',
    'IDomoticzService',
    'ILogger',
    'AuthenticationError',
    'ApiError',
    'InitializationError',
    'SyncError',
    'HttpClient',
    'HeatzyApiClient',
    'DomoticzService',
    'DeviceManager',
    'DomoticzLogger'
]