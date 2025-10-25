# Architecture Modulaire du Plugin Heatzy Pilote

## Vue d'ensemble

Le plugin a été complètement refactorisé en une architecture modulaire respectant les principes SOLID. Cette nouvelle organisation améliore la maintenabilité, la testabilité et l'extensibilité du code.

## Structure des fichiers

```
domoticz_heatzy_pilote/
├── plugin.py              # Plugin original (pour comparaison)
├── plugin_improved.py     # Version améliorée monolithique
├── plugin_modular.py      # Nouvelle version modulaire
├── src/                   # Modules du plugin
│   ├── __init__.py        # Configuration du package
│   ├── models.py          # Modèles de domaine
│   ├── interfaces.py      # Interfaces et contrats
│   ├── api.py            # Client API Heatzy
│   ├── domoticz_service.py # Service Domoticz
│   ├── device_manager.py  # Gestionnaire de périphériques
│   └── logger.py          # Services de logging
├── IMPROVEMENTS.md        # Documentation des améliorations
└── ARCHITECTURE.md        # Ce fichier
```

## Description des modules

### 📦 `src/models.py` - Modèles de domaine
**Responsabilité** : Définir les structures de données métier

- **`HeatMode`** : Énumération des modes de chauffage avec conversion automatique
- **`HeatzyDevice`** : Représentation immutable d'un périphérique Heatzy
- **`AuthToken`** : Token d'authentification avec gestion automatique de l'expiration
- **`DeviceStatus`** : État d'un périphérique avec horodatage

**Avantages** :
- Validation automatique des données
- Immutabilité des objets (thread-safe)
- Conversion transparente entre API et Domoticz
- Gestion intelligente de l'expiration des tokens

### 🔌 `src/interfaces.py` - Interfaces et contrats
**Responsabilité** : Définir les contrats que doivent respecter les implémentations

- **`ILogger`** : Interface de logging
- **`IHttpClient`** : Interface pour les requêtes HTTP
- **`IHeatzyApiClient`** : Interface pour l'API Heatzy
- **`IDomoticzService`** : Interface pour les opérations Domoticz
- **`IDeviceManager`** : Interface pour la gestion des périphériques
- **Exceptions personnalisées** : Gestion d'erreurs typée

**Avantages** :
- Inversion de dépendances (testabilité)
- Contrats clairs et documentés
- Facilite les tests unitaires
- Permet l'extensibilité future

### 🌐 `src/api.py` - Client API Heatzy
**Responsabilité** : Communication avec l'API Heatzy

- **`HttpClient`** : Client HTTP générique avec gestion d'erreurs
- **`HeatzyApiClient`** : Client spécialisé pour l'API Heatzy

**Fonctionnalités** :
- Gestion automatique de l'authentification
- Retry et gestion d'erreurs robuste
- Logging sécurisé (masquage des mots de passe/tokens)
- Validation des réponses API
- Cache intelligent des tokens

### 🏠 `src/domoticz_service.py` - Service Domoticz
**Responsabilité** : Interaction avec Domoticz

- **`DomoticzService`** : Implémentation pour Domoticz réel
- **`MockDomoticzService`** : Implémentation pour les tests

**Fonctionnalités** :
- Création et mise à jour de périphériques
- Gestion des unités Domoticz
- Gestion des timeouts de périphériques
- Validation des paramètres
- Support des tests sans Domoticz

### 🔧 `src/device_manager.py` - Gestionnaire de périphériques
**Responsabilité** : Orchestration des opérations sur les périphériques

**Fonctionnalités** :
- Découverte automatique des périphériques
- Synchronisation bidirectionnelle API ↔ Domoticz
- Cache intelligent des états
- Gestion des erreurs par périphérique
- Commandes de contrôle avec validation

### 📝 `src/logger.py` - Services de logging
**Responsabilité** : Logging abstrait et configurable

- **`DomoticzLogger`** : Logger intégré à Domoticz
- **`ConsoleLogger`** : Logger console pour tests
- **`NullLogger`** : Logger silencieux pour tests

## Principes SOLID appliqués

### 🎯 Single Responsibility Principle (SRP)
Chaque classe a une responsabilité unique :
- `HttpClient` : uniquement les requêtes HTTP
- `HeatzyApiClient` : uniquement l'API Heatzy
- `DomoticzService` : uniquement les opérations Domoticz
- `DeviceManager` : uniquement la gestion des périphériques

### 🔓 Open/Closed Principle (OCP)
- Extensions possibles sans modification du code existant
- Nouveaux modes de chauffage via l'enum `HeatMode`
- Nouveaux loggers via l'interface `ILogger`
- Nouveaux clients API via l'interface `IHttpClient`

### 🔄 Liskov Substitution Principle (LSP)
- Toutes les implémentations respectent leurs interfaces
- `MockDomoticzService` peut remplacer `DomoticzService`
- `ConsoleLogger` peut remplacer `DomoticzLogger`

### ⚡ Interface Segregation Principle (ISP)
- Interfaces spécialisées et ciblées
- Pas de méthodes inutiles forcées
- Contrats adaptés aux besoins réels

### 🔀 Dependency Inversion Principle (DIP)
- Le plugin principal dépend d'abstractions
- Injection de dépendances dans les constructeurs
- Facilite les tests et la modularité

## Migration et utilisation

### Pour utiliser la version modulaire :

1. **Remplacer le plugin** :
   ```bash
   cp plugin_modular.py plugin.py
   ```

2. **Redémarrer Domoticz** pour charger la nouvelle version

3. **Vérifier les logs** pour confirmer le bon fonctionnement

### Rétrocompatibilité
- ✅ Même interface Domoticz
- ✅ Mêmes paramètres de configuration
- ✅ Préservation des périphériques existants
- ✅ Aucune migration de données nécessaire

## Avantages de la nouvelle architecture

### 🧪 Testabilité
- Tests unitaires pour chaque module
- Mocks intégrés pour les tests
- Isolation des dépendances externes

### 📈 Maintenabilité  
- Code auto-documenté
- Responsabilités claires
- Facilité de débogage

### 🔧 Extensibilité
- Ajout facile de nouvelles fonctionnalités
- Support de nouveaux protocoles
- Intégration d'autres services

### 🛡️ Robustesse
- Gestion d'erreurs complète
- Validation stricte des données
- Récupération gracieuse des pannes

### ⚡ Performance
- Cache intelligent
- Authentification optimisée
- Requêtes HTTP optimisées

## Tests et validation

Le code modulaire peut être testé indépendamment :

```python
# Test d'un module spécifique
from src.models import HeatMode
mode = HeatMode.from_domoticz_level(20)
assert mode == HeatMode.ECO

# Test avec mocks
from src.logger import NullLogger
from src.device_manager import MockDeviceManager

logger = NullLogger()
manager = MockDeviceManager(logger)
```

## Conclusion

Cette architecture modulaire transforme le plugin en une application maintenable et extensible tout en conservant toutes les fonctionnalités existantes. Elle constitue une base solide pour les évolutions futures du plugin.