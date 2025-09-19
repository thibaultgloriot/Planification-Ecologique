import json 

#On utilise la réponse de la requête : https://geo.api.gouv.fr/epcis?codeRegion=53&limit=70&fields=code,nom,contour
with open("data/epcis.json", 'r') as f:
   epcis_data = json.load(f)

# Conversion en GeoJSON
geojson = {
"type": "FeatureCollection",
"features": []
}

for epci in epcis_data:
    feature = {
    "type": "Feature",
    "properties": {
        "code": epci["code"],
        "nom": epci["nom"]
    },
    "geometry": epci["contour"]}  # Utilise directement l'objet contour}
    geojson["features"].append(feature)
with open('data/epci.geojson', 'w') as f:
   json.dump(geojson, f)
   