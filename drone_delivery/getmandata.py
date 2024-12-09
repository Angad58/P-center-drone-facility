import shapely.geometry as geom

def clean_manhattan_boundary(input_file, output_file):
    """Create a cleaner Manhattan boundary, excluding surrounding islands."""
    
    # Define the main Manhattan polygon boundary
    manhattan_polygon_coords = [
        (-74.018200, 40.699800),  # Bottom-left
        (-73.925000, 40.699800),  # Bottom-right
        (-73.925000, 40.878500),  # Top-right
        (-74.018200, 40.878500),  # Top-left
        (-74.018200, 40.699800),  # Close the loop
    ]
    manhattan_polygon = geom.Polygon(manhattan_polygon_coords)
    
    # Exclusion zones for islands
    exclusion_zones = [
        geom.Polygon([  # Randalls Island
            (-73.932030, 40.785500), 
            (-73.920000, 40.785500), 
            (-73.920000, 40.805000), 
            (-73.932030, 40.805000), 
            (-73.932030, 40.785500),
        ]),
        geom.Polygon([  # Roosevelt Island
            (-73.949000, 40.750000), 
            (-73.940000, 40.750000), 
            (-73.940000, 40.770000), 
            (-73.949000, 40.770000), 
            (-73.949000, 40.750000),
        ]),
    ]
    
    def is_valid_manhattan_point(lat, lon):
        """Check if a point is within Manhattan and not in exclusion zones."""
        point = geom.Point(lon, lat)
        if not manhattan_polygon.contains(point):
            return False
        for exclusion_zone in exclusion_zones:
            if exclusion_zone.contains(point):
                return False
        return True
    
    # Filter coordinates
    manhattan_coords = []
    seen_coords = set()
    
    with open(input_file, 'r') as f:
        for line in f:
            try:
                # Parse coordinates
                coords = line.strip()[1:-2].split(', ')
                lat, lon = map(float, coords)
                
                # Validate point
                if is_valid_manhattan_point(lat, lon):
                    coord = (lat, lon)
                    if coord not in seen_coords:
                        manhattan_coords.append(coord)
                        seen_coords.add(coord)
            except ValueError:
                continue  # Skip invalid lines
    
    # Ensure the polygon is closed
    if manhattan_coords and manhattan_coords[0] != manhattan_coords[-1]:
        manhattan_coords.append(manhattan_coords[0])
    
    # Write cleaned coordinates
    with open(output_file, 'w') as f:
        for lat, lon in manhattan_coords:
            f.write(f"({lat:.6f}, {lon:.6f}),\n")
    
    print(f"Cleaned coordinates: {len(manhattan_coords)}")
    print(f"Saved to: {output_file}")

# Usage
input_file = 'manhattan_coords.txt'
output_file = 'manhattan_clean.txt'

clean_manhattan_boundary(input_file, output_file)
