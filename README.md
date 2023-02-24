# wiki-corrector

## Intro

Petit outil de QA pour des wikis/documentations francophones (pour l'instant https://doc.ubuntu-fr.org/)

Cet outil s'articule autours de 3 étapes :

1. Récupération de la documentation.
Si l'arborescence des fichiers récupérés existe déjà, alors on ne récupère que le différentiel.

2. Application des passes de QA (actuellement "grammalect")

3. outil d'aide à la correction avec la possibilité d'annoter les faux-positifs.


### Récupération de la documentation.


Attention, cette étape est potentiellement longue au premier lancement (et il est délicat d'estimer le temps à l'avance donc pas de barre de progression).
Pour https://doc.ubuntu-fr.org/, cela m'a pris 7h avec une connexion fibrée.
De même, si vous interrompez manuellement la première étape, le script n'est pas en mesure de reprendre la ou il a été arrêté.
En revanche, si vous relancer après une première étape avec succès, il ne va s'attarder que sur le différentiel.

```sh
    ./recover
```

Si l'on veut forcer la récupération de zéro, il est possible de faire :

```sh
    ./recover -f
```

ou

```sh
    ./recover --full
```

### Application des passes de QA

```sh
    ./check
```

### Launch tests

```sh
python -m unittest tests
```
