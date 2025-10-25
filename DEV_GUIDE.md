# Development Guide - Heatzy Pilote Plugin

## Vue d'ensemble

Ce guide explique comment utiliser les outils de développement mis en place pour le plugin Heatzy Pilote.

## Structure du projet

```
domoticz_heatzy_pilote/
├── plugin_modular.py          # Plugin principal (version modulaire)
├── src/                       # Modules source
│   ├── models.py             # Modèles de données
│   ├── interfaces.py         # Interfaces abstraites
│   ├── api.py                # Client API Heatzy
│   ├── domoticz_service.py   # Service Domoticz
│   ├── device_manager.py     # Gestionnaire d'appareils
│   └── logger.py             # Système de journalisation
├── test_modular.py           # Tests unitaires
├── version_manager.py        # Gestionnaire de versions
├── .version.toml            # Configuration des versions
├── Makefile                 # Commandes de développement
├── configure.sh             # Script de configuration
├── .github/workflows/       # CI/CD GitHub Actions
├── docs/                    # Documentation
└── dist/                    # Packages de distribution
```

## Commandes principales

### Configuration initiale

```bash
# Vérifier les prérequis système
./configure.sh --check

# Configurer l'environnement de développement
./configure.sh --setup

# Afficher l'état du système
./configure.sh --status
```

### Développement quotidien

```bash
# Vérification rapide (format + tests)
make quick

# Vérification complète de développement
make dev

# Tests seulement
make test

# Tests avec sortie détaillée
make test-verbose

# Formatage du code
make format

# Vérifications de qualité
make quality

# Vérifications de sécurité
make security
```

### Gestion des versions

```bash
# Afficher la version actuelle
make version-status

# Augmenter la version patch (1.0.0 → 1.0.1)
make version-patch

# Augmenter la version mineure (1.0.0 → 1.1.0)
make version-minor

# Augmenter la version majeure (1.0.0 → 2.0.0)
make version-major

# Détection automatique et augmentation
make version-auto
```

### Construction et installation

```bash
# Construire le package
make build

# Créer une release complète
make release

# Installer le plugin dans Domoticz
make install-plugin

# Désinstaller le plugin
make uninstall-plugin
```

### Tests et validation

```bash
# Tests continus (mode watch)
make dev-test

# Profilage des performances
make profile

# Test d'utilisation mémoire
make memory-test

# Validation de la structure du plugin
make validate
```

### Documentation

```bash
# Générer la documentation
make docs

# Afficher l'aide
make help
```

## Workflow de développement

### 1. Configuration initiale

```bash
# Cloner ou accéder au projet
cd /path/to/domoticz_heatzy_pilote

# Configurer l'environnement
./configure.sh --setup

# Vérifier que tout fonctionne
make dev
```

### 2. Développement de fonctionnalités

```bash
# Créer une branche pour votre fonctionnalité
git checkout -b feature/nouvelle-fonctionnalite

# Développer et tester régulièrement
make quick  # Tests rapides pendant le développement

# Vérifier la qualité avant commit
make quality
```

### 3. Tests et validation

```bash
# Tests complets
make test

# Validation de sécurité
make security

# Profilage si nécessaire
make profile
```

### 4. Préparation pour la production

```bash
# Nettoyage
make clean

# Construction et tests
make build

# Validation finale
make validate
```

### 5. Release

```bash
# Bump de version et release
make release

# Ou manuellement :
make version-minor  # ou patch/major selon les changements
git push origin main --tags
```

## Scripts utiles

### configure.sh

Script principal de configuration avec plusieurs options :

- `--check` : Vérifier les prérequis
- `--setup` : Configuration complète
- `--install` : Installation dans Domoticz
- `--status` : État du système

### version_manager.py

Gestionnaire de versions sémantiques :

```bash
# Utilisation directe
python3 version_manager.py status
python3 version_manager.py bump patch --commit --tag
```

## GitHub Actions

Le projet inclut 4 workflows automatisés :

1. **CI (ci.yml)** : Tests sur Python 3.6-3.11
2. **Release (release.yml)** : Releases automatiques
3. **Pull Request (pr.yml)** : Validation des PR
4. **Security (security.yml)** : Scans de sécurité

## Bonnes pratiques

### Structure du code

- Respecter les principes SOLID
- Utiliser les interfaces définies
- Maintenir la séparation des responsabilités

### Tests

- Exécuter `make test` avant chaque commit
- Maintenir la couverture de tests
- Tester les cas d'erreur

### Qualité du code

- Utiliser `make format` pour le formatage
- Respecter les règles de linting
- Vérifier la sécurité avec `make security`

### Versions

- Utiliser les versions sémantiques (semver)
- Documenter les changements dans CHANGELOG.md
- Tagger les releases

## Dépannage

### Problèmes courants

1. **Tests en échec** :
   ```bash
   make test-verbose  # Pour plus de détails
   ```

2. **Problèmes de formatage** :
   ```bash
   make format  # Correction automatique
   ```

3. **Erreurs de linting** :
   ```bash
   make lint  # Voir les erreurs
   ```

4. **Installation Domoticz échoue** :
   ```bash
   ./configure.sh --check  # Vérifier la configuration
   ```

### Variables d'environnement

- `PYTHON` : Commande Python à utiliser (défaut: python3)
- `PIP` : Commande pip à utiliser (défaut: pip3)

### Configuration locale

Créer `local_config.py` basé sur `local_config.py.template` pour la configuration locale.

## Support

- Documentation : README.md, README_FR.md
- Architecture : ARCHITECTURE.md
- Changelog : CHANGELOG.md
- Issues : GitHub Issues du projet

## Ressources additionnelles

- [Domoticz Plugin Development](https://www.domoticz.com/wiki/Developing_a_Python_plugin)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions](https://docs.github.com/en/actions)