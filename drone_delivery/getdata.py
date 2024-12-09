import json

def extract_borough_boundaries(file_path, step=20):
    """Extract coordinates for each borough from GeoJSON file"""
    try:
        # Read the GeoJSON file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Borough code to name mapping
        borough_names = {
            "1": "manhattan",
            "2": "bronx",
            "3": "brooklyn",
            "4": "queens",
            "5": "staten_island"
        }
        
        # Process each borough
        for feature in data['features']:
            boro_code = feature['properties']['boro_code']
            if boro_code in borough_names:
                borough_name = borough_names[boro_code]
                output_file = f'{borough_name}_coords.txt'
                
                # Get coordinates from MultiPolygon
                coordinates = []
                for polygon in feature['geometry']['coordinates']:
                    for ring in polygon:
                        for coord in ring:
                            coordinates.append((coord[1], coord[0]))  # Swap to lat, lon
                
                # Take every nth coordinate
                simplified = coordinates[::step]
                
                # Add first coordinate at end if needed
                if simplified[-1] != simplified[0]:
                    simplified.append(simplified[0])
                
                # Save to file
                with open(output_file, 'w') as f:
                    for lat, lon in simplified:
                        f.write(f"({lat:.6f}, {lon:.6f}),\n")
    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    geojson_file = 'B.geojson'  # Your input GeoJSON file
    extract_borough_boundaries(geojson_file, step=20)

if __name__ == "__main__":
    main()