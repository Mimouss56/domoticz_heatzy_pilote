#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Test script for the modular Heatzy Pilote Plugin
#
# Author: Mimouss56
#

"""
Script de test pour valider l'architecture modulaire du plugin Heatzy Pilote.
Ce script teste chaque module indépendamment.
"""

import sys
import os

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_models():
    """Test des modèles de domaine."""
    print("🧪 Test des modèles...")
    
    # Test HeatMode
    from src.models import HeatMode, HeatzyDevice, AuthToken
    
    # Test conversion des modes
    mode = HeatMode.from_domoticz_level(20)
    assert mode == HeatMode.ECO, f"Expected ECO, got {mode}"
    
    mode = HeatMode.from_api_mode(0)
    assert mode == HeatMode.COMFORT, f"Expected COMFORT, got {mode}"
    
    # Test HeatzyDevice
    device = HeatzyDevice(
        did="test_device_123",
        dev_alias="Salon",
        product_key="test_key"
    )
    assert device.safe_name == "Salon"
    
    # Test AuthToken
    token = AuthToken.create("test_token", 3600)
    assert not token.is_expired
    assert token.time_until_expiry > 3500
    
    print("✅ Modèles OK")

def test_interfaces():
    """Test des interfaces."""
    print("🧪 Test des interfaces...")
    
    from src.interfaces import (
        AuthenticationError, ApiError, DeviceNotFoundError,
        DomoticzError, InitializationError, SyncError
    )
    
    # Test que les exceptions sont bien définies
    try:
        raise AuthenticationError("Test")
    except AuthenticationError:
        pass
    
    print("✅ Interfaces OK")

def test_logger():
    """Test des loggers."""
    print("🧪 Test des loggers...")
    
    from src.logger import ConsoleLogger, NullLogger
    
    # Test ConsoleLogger
    console_logger = ConsoleLogger("Test")
    console_logger.info("Message de test")
    console_logger.debug("Debug test")
    console_logger.warning("Warning test")
    console_logger.error("Error test")
    
    # Test NullLogger
    null_logger = NullLogger()
    null_logger.info("Ce message ne s'affiche pas")
    
    print("✅ Loggers OK")

def test_api_client():
    """Test du client API."""
    print("🧪 Test du client API...")
    
    from src.logger import NullLogger
    from src.api import HttpClient, HeatzyApiClient
    
    logger = NullLogger()
    
    # Test HttpClient
    http_client = HttpClient(logger)
    http_client.set_host("example.com")
    
    # Test HeatzyApiClient (sans vraies requêtes)
    api_client = HeatzyApiClient(http_client, logger)
    assert not api_client.is_authenticated()
    
    print("✅ Client API OK")

def test_domoticz_service():
    """Test du service Domoticz."""
    print("🧪 Test du service Domoticz...")
    
    from src.logger import NullLogger
    from src.domoticz_service import MockDomoticzService
    from src.models import HeatzyDevice, HeatMode
    
    logger = NullLogger()
    service = MockDomoticzService(logger)
    
    # Test création de device
    device = HeatzyDevice("test_device_123456", "Test Device")
    service.create_device(device, 1)
    
    # Test update de device
    service.update_device(1, HeatMode.ECO)
    
    # Test vérifications
    assert service.device_exists("test_device_123456")
    assert service.get_device_unit("test_device_123456") == 1
    assert service.get_next_unit() == 2
    
    print("✅ Service Domoticz OK")

def test_device_manager():
    """Test du gestionnaire de périphériques."""
    print("🧪 Test du gestionnaire de périphériques...")
    
    from src.logger import NullLogger
    from src.device_manager import MockDeviceManager
    
    logger = NullLogger()
    manager = MockDeviceManager(logger)
    
    # Test initialisation
    manager.initialize_devices()
    
    # Test contrôle
    success = manager.control_device(1, 20)  # ECO mode
    assert success
    
    # Test comptage
    assert manager.get_device_count() == 0  # Mock vide
    
    print("✅ Gestionnaire de périphériques OK")

def test_integration():
    """Test d'intégration."""
    print("🧪 Test d'intégration...")
    
    from src.logger import ConsoleLogger
    from src.api import HttpClient, HeatzyApiClient
    from src.domoticz_service import MockDomoticzService
    from src.device_manager import DeviceManager
    
    logger = ConsoleLogger("Integration")
    
    # Création des composants
    http_client = HttpClient(logger)
    api_client = HeatzyApiClient(http_client, logger)
    domoticz_service = MockDomoticzService(logger)
    device_manager = DeviceManager(api_client, domoticz_service, logger)
    
    # Test de l'assemblage
    assert device_manager.get_device_count() == 0
    
    print("✅ Intégration OK")

def main():
    """Fonction principale de test."""
    print("🚀 Démarrage des tests du plugin modulaire Heatzy Pilote")
    print("=" * 60)
    
    try:
        test_models()
        test_interfaces()
        test_logger()
        test_api_client()
        test_domoticz_service()
        test_device_manager()
        test_integration()
        
        print("=" * 60)
        print("🎉 Tous les tests sont passés avec succès !")
        print("✅ L'architecture modulaire est fonctionnelle")
        
    except Exception as e:
        print(f"❌ Erreur dans les tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)