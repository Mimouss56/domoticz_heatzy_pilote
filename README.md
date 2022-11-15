# Plugin domoticz pour Heazy Pilote

Ce plugin [Domoticz](https://www.domoticz.com) permet de controller des modules [Heatzy pilote](https://heatzy.com).

## Installation

Python version 3.4 or higher est nécessaire avec Domoticz version 2021.1 ou supérieur .

Pour l'installer :
* Allez dans le repertoire de Domoticz/Plugins et.
* Le plugin exige Python library scapy ```sudo apt-get install python3-scapy```
* : ```git clone https://github.com/mimouss/Domoticz-WiZ-connected-plugin.git```
* Redemarrez Domoticz. ```sudo systemctl restart domoticz```

## Mise à Jour

Pour mettre à jour:
* Allez dans le repertoire de Domoticz/Plugins et ouvrez le dossier domoticz_heatzy_pilote.
* Run: ```git pull```
* Restart Domoticz.

## Configuration
Pour ajouter vos modules Heatzy rendez-vous sur la page ```Matériel``` de votre Domoticz et ajoutez un élément de type ```Heatzy pilote```.

Renseignez un nom et les identifiants de votre compte Heatzy.

## Utilisation
Ce plugin va créer (au moment du démarrage) chaque module Heaty pilote associés à votre compte.
