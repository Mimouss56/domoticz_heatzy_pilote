#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Heatzy Pilote Plugin - API Client
#
# Author: Mimouss56
#

"""
Heatzy API client implementation.

This module provides HTTP client and Heatzy API client implementations
for communicating with the Heatzy cloud service.
"""

import json
import http.client
from typing import Dict, List, Any, Optional
from .models import HeatMode, HeatzyDevice, AuthToken, DeviceStatus
from .interfaces import (
    IHttpClient, IHeatzyApiClient, ILogger,
    AuthenticationError, ApiError, DeviceNotFoundError
)


class HttpClient(IHttpClient):
    """
    HTTP client implementation using http.client.
    
    Responsible only for HTTP operations with error handling and logging.
    """
    
    def __init__(self, logger: ILogger, timeout: int = 30):
        """
        Initialize HTTP client.
        
        Args:
            logger: Logger instance
            timeout: Request timeout in seconds
        """
        self.logger = logger
        self.timeout = timeout
        self._host: Optional[str] = None
    
    def set_host(self, host: str) -> None:
        """Set the target host for requests."""
        self._host = host
        self.logger.debug(f"HTTP client host set to: {host}")
    
    def post(self, path: str, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Make POST request and return parsed JSON response.
        
        Args:
            path: Request path
            data: JSON data to send
            headers: HTTP headers
            
        Returns:
            Parsed JSON response
            
        Raises:
            ApiError: If request fails
        """
        if not self._host:
            raise ApiError("Host not configured")
        
        try:
            conn = http.client.HTTPSConnection(self._host, timeout=self.timeout)
            json_data = json.dumps(data)
            
            self.logger.debug(f"POST {path} with data: {self._safe_log_data(data)}")
            
            conn.request("POST", path, json_data, headers)
            response = conn.getresponse()
            
            if response.status != 200:
                error_msg = f"HTTP {response.status}: {response.reason}"
                self.logger.error(f"POST request failed: {error_msg}")
                raise ApiError(error_msg)
            
            response_data = response.read()
            conn.close()
            
            result = json.loads(response_data.decode("utf-8"))
            self.logger.debug(f"POST response: {self._safe_log_response(result)}")
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise ApiError(f"Invalid JSON response: {e}")
        except Exception as e:
            self.logger.error(f"POST request failed: {e}")
            raise ApiError(f"POST request failed: {e}")
    
    def get(self, path: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Make GET request and return parsed JSON response.
        
        Args:
            path: Request path
            headers: HTTP headers
            
        Returns:
            Parsed JSON response
            
        Raises:
            ApiError: If request fails
        """
        if not self._host:
            raise ApiError("Host not configured")
        
        try:
            conn = http.client.HTTPSConnection(self._host, timeout=self.timeout)
            
            self.logger.debug(f"GET {path}")
            
            conn.request("GET", path, headers=headers)
            response = conn.getresponse()
            
            if response.status != 200:
                error_msg = f"HTTP {response.status}: {response.reason}"
                self.logger.error(f"GET request failed: {error_msg}")
                raise ApiError(error_msg)
            
            response_data = response.read()
            conn.close()
            
            result = json.loads(response_data.decode("utf-8"))
            self.logger.debug(f"GET response: {self._safe_log_response(result)}")
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise ApiError(f"Invalid JSON response: {e}")
        except Exception as e:
            self.logger.error(f"GET request failed: {e}")
            raise ApiError(f"GET request failed: {e}")
    
    def _safe_log_data(self, data: Dict[str, Any]) -> str:
        """Safely log request data (hide passwords)."""
        safe_data = data.copy()
        if 'password' in safe_data:
            safe_data['password'] = '***'
        return str(safe_data)
    
    def _safe_log_response(self, response: Dict[str, Any]) -> str:
        """Safely log response data (hide tokens)."""
        safe_response = response.copy() if isinstance(response, dict) else response
        if isinstance(safe_response, dict) and 'token' in safe_response:
            safe_response['token'] = f"***{safe_response['token'][-4:]}"
        return str(safe_response)


class HeatzyApiClient(IHeatzyApiClient):
    """
    Heatzy API client implementation.
    
    Responsible only for Heatzy API communication with proper error handling,
    authentication management, and data validation.
    """
    
    # Heatzy API configuration
    API_HOST = 'euapi.gizwits.com'
    APPLICATION_ID = 'c70a66ff039d41b4a220e198b0fcc8b3'
    PILOT_PRODUCT_KEY = '9420ae048da545c88fc6274d204dd25f'
    
    def __init__(self, http_client: IHttpClient, logger: ILogger):
        """
        Initialize Heatzy API client.
        
        Args:
            http_client: HTTP client implementation
            logger: Logger instance
        """
        self.http_client = http_client
        self.logger = logger
        self._auth_token: Optional[AuthToken] = None
        
        # Configure HTTP client
        self.http_client.set_host(self.API_HOST)
    
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
        if not username or not password:
            raise AuthenticationError("Username and password are required")
        
        try:
            data = {
                'username': username,
                'password': password,
                'lang': 'en'
            }
            headers = self._get_base_headers()
            
            self.logger.info(f"Authenticating user: {username}")
            response = self.http_client.post("/app/login", data, headers)
            
            if 'token' not in response:
                raise AuthenticationError("No token in authentication response")
            
            token = AuthToken.create(response['token'])
            self._auth_token = token
            
            self.logger.info("Authentication successful")
            return token
            
        except ApiError as e:
            self.logger.error(f"Authentication API error: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def get_devices(self) -> List[HeatzyDevice]:
        """
        Get list of devices associated with the account.
        
        Returns:
            List of HeatzyDevice objects
            
        Raises:
            AuthenticationError: If not authenticated or token expired
            ApiError: If API request fails
        """
        self._ensure_authenticated()
        
        try:
            headers = self._get_authenticated_headers()
            response = self.http_client.get("/app/bindings", headers)
            
            if 'devices' not in response:
                self.logger.warning("No devices found in API response")
                return []
            
            devices = []
            for device_data in response['devices']:
                try:
                    # Validate device data
                    if 'did' not in device_data or 'dev_alias' not in device_data:
                        self.logger.warning(f"Invalid device data: {device_data}")
                        continue
                    
                    device = HeatzyDevice(
                        did=device_data['did'],
                        dev_alias=device_data['dev_alias'],
                        product_key=device_data.get('product_key', '')
                    )
                    devices.append(device)
                    
                except ValueError as e:
                    self.logger.error(f"Invalid device data: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(devices)} devices")
            return devices
            
        except ApiError as e:
            self.logger.error(f"Failed to get devices: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting devices: {e}")
            raise ApiError(f"Failed to get devices: {e}")
    
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
        if not device_id:
            raise ValueError("Device ID is required")
        
        self._ensure_authenticated()
        
        try:
            headers = self._get_authenticated_headers()
            path = f"/app/devdata/{device_id}/latest"
            response = self.http_client.get(path, headers)
            
            if 'attr' not in response or 'mode' not in response['attr']:
                raise DeviceNotFoundError(f"Invalid device response for {device_id}")
            
            api_mode = response['attr']['mode']
            mode = HeatMode.from_api_mode(api_mode)
            
            status = DeviceStatus.create(device_id, mode)
            self.logger.debug(f"Device {device_id} status: {mode.name}")
            
            return status
            
        except ValueError as e:
            raise DeviceNotFoundError(f"Invalid mode for device {device_id}: {e}")
        except ApiError as e:
            if "404" in str(e):
                raise DeviceNotFoundError(f"Device {device_id} not found")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting device status: {e}")
            raise ApiError(f"Failed to get device status: {e}")
    
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
        if not device_id:
            raise ValueError("Device ID is required")
        
        self._ensure_authenticated()
        
        try:
            data = {"attrs": {"mode": mode.api_mode}}
            headers = self._get_authenticated_headers()
            headers["Content-Type"] = "application/json"
            
            path = f"/app/control/{device_id}"
            
            self.logger.info(f"Controlling device {device_id}: {mode.name}")
            self.http_client.post(path, data, headers)
            
            self.logger.info(f"Successfully controlled device {device_id}")
            return True
            
        except ApiError as e:
            if "404" in str(e):
                raise DeviceNotFoundError(f"Device {device_id} not found")
            self.logger.error(f"Failed to control device {device_id}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error controlling device {device_id}: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if client has a valid authentication token."""
        return self._auth_token is not None and not self._auth_token.is_expired
    
    def _get_base_headers(self) -> Dict[str, str]:
        """Get base headers for API requests."""
        return {
            "Accept": "application/json",
            "X-Gizwits-Application-Id": self.APPLICATION_ID
        }
    
    def _get_authenticated_headers(self) -> Dict[str, str]:
        """
        Get headers with authentication token.
        
        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated or token expired")
        
        headers = self._get_base_headers()
        headers["X-Gizwits-User-token"] = self._auth_token.token
        return headers
    
    def _ensure_authenticated(self) -> None:
        """
        Ensure we have a valid authentication token.
        
        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.is_authenticated():
            raise AuthenticationError("Authentication required")