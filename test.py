with open("data/a-epci2025.geojson", 'r') as f:
            import json
            geojson_data = json.load(f)
            first_feature = geojson_data['features'][0]