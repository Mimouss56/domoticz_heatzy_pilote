# Plugin domoticz pour Heazy Pilote

Ce plugin [Domoticz](https://www.domoticz.com) permet de controller des modules [Heatzy pilote](https://heatzy.com).

## Installation
Clonez simplement ce dépôt dans le dossier ```plugins``` de votre Domoticz.

## Configuration
Pour ajouter vos modules Heatzy rendez-vous sur la page ```Matériel``` de votre Domoticz et ajoutez un élément de type ```Heatzy pilote```.

Renseignez un nom et les identifiants de votre compte Heatzy.

## Utilisation
Ce plugin va créer (au moment du démarrage) deux dispositifs par module Heaty pilote associés à votre compte.

- Le premier est un sélecteur permettant de choisir entre les modes Off, Hors gel, Eco, et Confort.
- Le deuxième est un interrupteur On/Off (mode confort) permettant une compatibilité avec le plugin [Smart Virtual Thermostat](https://www.domoticz.com/wiki/Plugins/Smart_Virtual_Thermostat.html)
