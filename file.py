import csv

import httpx
from fastapi import FastAPI
from pyproj import Transformer

app = FastAPI()

CSV = "2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv"
URL = "https://data.geopf.fr/geocodage/search"

# Distance en metres
RAYONS = {"2G": 30000, "3G": 5000, "4G": 10000}

# Les codes des opérateurs dans le fichier CSV
OPERATEURS = {"20801": "orange", "20810": "sfr", "20815": "free", "20820": "bouygues"}

# Convertir GPS (longitude, latitude) en Lambert 93 (x, y en mètres)
convertisseur = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)


# Lire le fichier CSV et on obtient la liste des tours
def charger_tours():
    liste = []
    with open(CSV) as fichier:
        for ligne in csv.DictReader(fichier, delimiter=";"):
            try:
                liste.append(
                    {
                        "operateur": OPERATEURS[ligne["Operateur"]],
                        "x": float(ligne["X"]),
                        "y": float(ligne["Y"]),
                        "2G": ligne["2G"] == "1",
                        "3G": ligne["3G"] == "1",
                        "4G": ligne["4G"] == "1",
                    }
                )
            except ValueError:
                pass
    return liste


TOURS = charger_tours()


# Trouver la longitude et la latitude d'une adresse
def trouver_coordonnees(adresse):
    try:
        reponse = httpx.get(URL, params={"q": adresse, "limit": 1}, timeout=5)
    except httpx.HTTPError:
        return None, None, "service d'adresse indisponible"

    if reponse.status_code >= 500:
        return None, None, "service d'adresse indisponible"
    if reponse.status_code != 200:
        return None, None, "adresse introuvable"

    resultats = reponse.json()["features"]
    if len(resultats) == 0 or resultats[0]["properties"]["score"] < 0.4:
        return None, None, "adresse introuvable"

    longitude, latitude = resultats[0]["geometry"]["coordinates"]
    return longitude, latitude, None


# Calculer la couverture de chaque opérateur
def calculer_couverture(longitude, latitude):
    x, y = convertisseur.transform(longitude, latitude)

    couverture = {}
    for nom in OPERATEURS.values():
        couverture[nom] = {"2G": False, "3G": False, "4G": False}

    for tour in TOURS:
        distance = ((tour["x"] - x) ** 2 + (tour["y"] - y) ** 2) ** 0.5
        for techno, rayon in RAYONS.items():
            if tour[techno] and distance <= rayon:
                couverture[tour["operateur"]][techno] = True

    return couverture


# l'API
@app.post("/coverage")
def coverage(adresses: dict[str, str]):
    resultat = {}
    for identifiant, adresse in adresses.items():
        longitude, latitude, erreur = trouver_coordonnees(adresse)
        if erreur:
            resultat[identifiant] = {"erreur": erreur}
        else:
            resultat[identifiant] = calculer_couverture(longitude, latitude)
    return resultat
