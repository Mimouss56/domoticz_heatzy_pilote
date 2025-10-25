# Plugin domoticz pour Heazy Pilote

Ce plugin [Domoticz](https://www.domoticz.com) permet de controller des modules [Heatzy pilote](https://heatzy.com).

## Installation

Python version 3.8 ou supérieure est nécessaire avec Domoticz version 2021.1 ou supérieur.

Pour l'installer :
* Allez dans le repertoire de Domoticz/Plugins et.
* Le plugin exige Python library scapy ```sudo apt-get install python3-scapy```
* : ```git clone https://github.com/Mimouss56/domoticz_heatzy_pilote.git```
* Redemarrez Domoticz. ```sudo systemctl restart domoticz```

## Mise à Jour

Pour mettre à jour:
* Allez dans le repertoire de Domoticz/Plugins et ouvrez le dossier # Plugin Heatzy Pilote pour Domoticz - Version Modulaire

Plugin Domoticz pour contrôler les radiateurs Heatzy Pilote via l'API cloud.

## 🆕 Nouveautés Version 1.0.0

Cette version apporte une refactorisation complète avec une **architecture modulaire** respectant les principes **SOLID**.

### Versions disponibles

1. **`plugin.py`** - Version originale (référence)
2. **`plugin_improved.py`** - Version améliorée monolithique  
3. **`plugin_modular.py`** - **Version modulaire recommandée** ⭐

## 🏗️ Architecture Modulaire

```
src/
├── models.py          # Modèles de domaine (HeatMode, Device, Token)
├── interfaces.py      # Contrats et interfaces
├── api.py            # Client API Heatzy avec gestion d'erreurs
├── domoticz_service.py # Service Domoticz avec mocks pour tests
├── device_manager.py  # Orchestrateur de périphériques
└── logger.py         # Loggers configurables
```

### Avantages de la version modulaire

- ✅ **Maintenabilité** : Code organisé et documenté
- ✅ **Testabilité** : Tests unitaires pour chaque module
- ✅ **Extensibilité** : Architecture ouverte aux évolutions
- ✅ **Robustesse** : Gestion d'erreurs complète
- ✅ **Performance** : Cache intelligent et optimisations

## 📋 Prérequis

- Domoticz avec support Python
- Compte Heatzy avec périphériques Pilote configurés
- **Python 3.8+** (Python 3.9+ recommandé)

> **Note** : Python 3.6-3.7 ne sont plus supportés en raison de leur fin de vie et de la compatibilité GitHub Actions. Voir [PYTHON_COMPATIBILITY.md](PYTHON_COMPATIBILITY.md) pour plus de détails.

## 🚀 Installation

### Version modulaire (recommandée)

1. **Télécharger le plugin** :
   ```bash
   cd domoticz/plugins/
   git clone https://github.com/Mimouss56/domoticz_heatzy_pilote.git
   ```

2. **Utiliser la version modulaire** :
   ```bash
   cd domoticz_heatzy_pilote/
   cp plugin_modular.py plugin.py
   ```

3. **Redémarrer Domoticz**

4. **Configurer le plugin** dans Domoticz :
   - Aller dans Configuration → Matériel
   - Ajouter un nouveau matériel de type "Heatzy pilote"
   - Saisir vos identifiants Heatzy
   - Activer le plugin

## ⚙️ Configuration

| Paramètre | Description | Requis |
|-----------|-------------|--------|
| Username | Email du compte Heatzy | ✅ Oui |
| Password | Mot de passe Heatzy | ✅ Oui |
| Debug | Niveau de debug (0=Aucun, 62=Normal, -1=Complet) | Non |

## 🎛️ Modes de chauffage

| Mode Domoticz | Niveau | Mode Heatzy | Description |
|---------------|--------|-------------|-------------|
| Arrêt | 0 | off | Radiateur éteint |
| Hors gel | 10 | fro | Protection hors gel |
| Eco | 20 | eco | Mode économique |
| Confort | 30 | cft | Mode confort |

## 🧪 Tests et Validation

### Tester l'architecture modulaire

```bash
cd domoticz_heatzy_pilote/
python3 test_modular.py
```

### Tests unitaires par module

```python
# Test des modèles
from src.models import HeatMode
mode = HeatMode.from_domoticz_level(20)
assert mode == HeatMode.ECO

# Test avec mocks
from src.logger import NullLogger
from src.domoticz_service import MockDomoticzService
logger = NullLogger()
service = MockDomoticzService(logger)
```

## 📊 Monitoring et Debug

### Logs disponibles

- **Info** : Démarrage, authentification, découverte de périphériques
- **Debug** : Requêtes API, synchronisation des états
- **Error** : Échecs d'authentification, erreurs de communication

### Commandes utiles

```bash
# Voir les logs Domoticz
tail -f domoticz.log | grep HeatzyPilote

# Tester le plugin hors Domoticz
python3 plugin_modular.py

# Valider les modules
python3 test_modular.py
```

## 🔧 Développement

### Structure des principes SOLID

1. **Single Responsibility** : Chaque classe a une responsabilité unique
2. **Open/Closed** : Extensible sans modification du code existant
3. **Liskov Substitution** : Les implémentations respectent leurs contrats
4. **Interface Segregation** : Interfaces spécialisées et ciblées  
5. **Dependency Inversion** : Dépendances sur des abstractions

### Ajouter un nouveau mode de chauffage

```python
# Dans src/models.py
class HeatMode(Enum):
    # Modes existants...
    BOOST = ("boost", 4, 40)  # Nouveau mode
```

### Ajouter un nouveau logger

```python
# Dans src/logger.py
class FileLogger(ILogger):
    def __init__(self, filename):
        self.filename = filename
    
    def info(self, message):
        with open(self.filename, 'a') as f:
            f.write(f"INFO: {message}\n")
```

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture détaillée
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Liste des améliorations
- **[Code source](src/)** - Documentation inline complète

## 🐛 Dépannage

### Problèmes courants

1. **"Authentication failed"**
   - Vérifier les identifiants Heatzy
   - Tester la connexion internet
   - Vérifier que l'API Heatzy est accessible

2. **"No devices found"**
   - S'assurer que les périphériques sont configurés dans l'app Heatzy
   - Vérifier que les périphériques sont en ligne

3. **"Module import error"**
   - Vérifier que tous les fichiers `src/*.py` sont présents
   - S'assurer que les permissions sont correctes

### Debug avancé

```python
# Activer le debug complet
Parameters["Mode6"] = "-1"

# Test manuel d'authentification
from src.api import HeatzyApiClient, HttpClient
from src.logger import ConsoleLogger

logger = ConsoleLogger()
http_client = HttpClient(logger)
api_client = HeatzyApiClient(http_client, logger)
token = api_client.authenticate("email", "password")
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Merci de :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Ajouter des tests pour votre code
4. S'assurer que tous les tests passent
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- Équipe Domoticz pour le framework de plugins
- Heatzy pour l'API de contrôle des radiateurs
- Communauté open source pour les retours et améliorations.
* Run: ```git pull```
* Restart Domoticz.

## Configuration
Pour ajouter vos modules Heatzy rendez-vous sur la page ```Matériel``` de votre Domoticz et ajoutez un élément de type ```Heatzy pilote```.

Renseignez un nom et les identifiants de votre compte Heatzy.

## Utilisation
Ce plugin va créer (au moment du démarrage) chaque module Heaty pilote associés à votre compte.
