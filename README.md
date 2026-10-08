# API de couverture réseau

Cette API reçoit une adresse et dit pour chaque opérateur (Orange, SFR, Bouygues, Free) si la 2G, la 3G et la 4G sont disponibles

Une adresse est couverte s'il y a une tour assez proche :
2G -> 30 km, 3G -> 5 km, 4G -> 10 km

## Lancer l'API

Dans le terminal, Lancer:
uv sync
uv run uvicorn file:app --reload


Ouvrir ensuite http://127.0.0.1:8000/docs pour tester

## Exemple

Envoyer (POST sur `/coverage`) :

```json
{"id1": "157 boulevard Mac Donald 75019 Paris"}
```

Réponse :

```json
{
  "id1": {
    "orange":   {"2G": true,  "3G": true, "4G": true},
    "sfr":      {"2G": true,  "3G": true, "4G": true},
    "bouygues": {"2G": true,  "3G": true, "4G": true},
    "free":     {"2G": false, "3G": true, "4G": true}
  }
}
```

Si une adresse n'est pas trouvée, la réponse contient `{"erreur": "adresse introuvable"}`
pour cette adresse.

## Lancer les tests

```bash
uv run pytest test.py
```

## Comment ça marche

1. Je lis le fichier CSV des tours
2. Je demande à l'API d'adresse (`data.geopf.fr`) la position de l'adresse
3. Je convertis cette position en Lambert 93 avec pyproj
4. Je regarde si une tour de chaque opérateur est assez proche