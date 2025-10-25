#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Heatzy Pilote Plugin - Logger Implementation
#
# Author: Mimouss56
#

"""
Logger implementation for the Heatzy Pilote plugin.

This module provides logger implementations that integrate with Domoticz
logging system and provide fallbacks for testing.
"""

from .interfaces import ILogger

# Import Domoticz module (available when running in Domoticz)
try:
    import Domoticz
    DOMOTICZ_AVAILABLE = True
except ImportError:
    DOMOTICZ_AVAILABLE = False


class DomoticzLogger(ILogger):
    """
    Domoticz logger implementation.
    
    Uses the Domoticz logging system when available.
    """
    
    def __init__(self, prefix: str = "HeatzyPilote"):
        """
        Initialize Domoticz logger.
        
        Args:
            prefix: Prefix for log messages
        """
        self.prefix = prefix
    
    def debug(self, message: str) -> None:
        """Log a debug message."""
        if DOMOTICZ_AVAILABLE:
            Domoticz.Debug(f"[{self.prefix}] {message}")
        else:
            print(f"DEBUG [{self.prefix}] {message}")
    
    def info(self, message: str) -> None:
        """Log an info message."""
        if DOMOTICZ_AVAILABLE:
            Domoticz.Log(f"[{self.prefix}] {message}")
        else:
            print(f"INFO [{self.prefix}] {message}")
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        if DOMOTICZ_AVAILABLE:
            Domoticz.Log(f"[{self.prefix}] WARNING: {message}")
        else:
            print(f"WARNING [{self.prefix}] {message}")
    
    def error(self, message: str) -> None:
        """Log an error message."""
        if DOMOTICZ_AVAILABLE:
            Domoticz.Error(f"[{self.prefix}] {message}")
        else:
            print(f"ERROR [{self.prefix}] {message}")


class ConsoleLogger(ILogger):
    """
    Console logger implementation for testing.
    
    Provides basic console logging when Domoticz is not available.
    """
    
    def __init__(self, prefix: str = "HeatzyPilote"):
        """
        Initialize console logger.
        
        Args:
            prefix: Prefix for log messages
        """
        self.prefix = prefix
    
    def debug(self, message: str) -> None:
        """Log a debug message."""
        print(f"DEBUG [{self.prefix}] {message}")
    
    def info(self, message: str) -> None:
        """Log an info message."""
        print(f"INFO [{self.prefix}] {message}")
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        print(f"WARNING [{self.prefix}] {message}")
    
    def error(self, message: str) -> None:
        """Log an error message."""
        print(f"ERROR [{self.prefix}] {message}")


class NullLogger(ILogger):
    """
    Null logger implementation.
    
    Discards all log messages - useful for testing when you don't want output.
    """
    
    def debug(self, message: str) -> None:
        """Discard debug message."""
        pass
    
    def info(self, message: str) -> None:
        """Discard info message."""
        pass
    
    def warning(self, message: str) -> None:
        """Discard warning message."""
        pass
    
    def error(self, message: str) -> None:
        """Discard error message."""
        pass