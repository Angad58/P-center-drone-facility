import numpy as np
from shapely.geometry import Polygon, Point

def load_data(num_points=100):
    # More detailed Manhattan boundary (counterclockwise from bottom)
    manhattan_coords = [
        (40.7019, -74.0097),  # Battery Park
        (40.7052, -74.0030),  # South Street Seaport
        (40.7134, -73.9903),  # Lower East Side
        (40.7262, -73.9796),  # East Village
        (40.7347, -73.9737),  # Stuyvesant Town
        (40.7580, -73.9738),  # Midtown East
        (40.7685, -73.9666),  # Upper East Side
        (40.7831, -73.9593),  # Upper East Side North
        (40.7940, -73.9366),  # East Harlem
        (40.8051, -73.9308),  # Harlem River
        (40.8185, -73.9473),  # Hamilton Heights
        (40.8075, -73.9609),  # Morning Side Heights
        (40.7937, -73.9712),  # Upper West Side
        (40.7870, -73.9782),  # Upper West Side South
        (40.7720, -73.9856),  # Midtown West
        (40.7551, -73.9989),  # Chelsea
        (40.7421, -74.0080),  # Greenwich Village
        (40.7219, -74.0134),  # Tribeca
        (40.7019, -74.0097),  # Back to start
    ]
    
    manhattan = Polygon([(lon, lat) for lat, lon in manhattan_coords])  # Note the swap for shapely
    
    # Updated density zones based on real population density
    density_zones = {
        'midtown': {
            'bounds': (40.7480, 40.7630, -73.9900, -73.9700),
            'weight': 0.25  # Very high density
        },
        'upper_east': {
            'bounds': (40.7700, 40.7850, -73.9700, -73.9500),
            'weight': 0.20
        },
        'financial': {
            'bounds': (40.7050, 40.7150, -74.0150, -74.0000),
            'weight': 0.15
        },
        'chelsea': {
            'bounds': (40.7400, 40.7550, -74.0050, -73.9900),
            'weight': 0.15
        },
        'rest': {
            'weight': 0.25
        }
    }

    def generate_points():
        points = []
        points_needed = 0
        
        for zone, info in density_zones.items():
            zone_points = int(num_points * info['weight'])
            points_needed += zone_points
            
            if zone != 'rest':
                min_lat, max_lat, min_lon, max_lon = info['bounds']
                attempts = 0
                while len(points) < points_needed and attempts < 1000:
                    lat = np.random.uniform(min_lat, max_lat)
                    lon = np.random.uniform(min_lon, max_lon)
                    if manhattan.contains(Point(lon, lat)):  # Note the swap
                        points.append((lat, lon))
                    attempts += 1
            else:
                while len(points) < num_points:
                    lat = np.random.uniform(40.7019, 40.8185)
                    lon = np.random.uniform(-74.0134, -73.9308)
                    if manhattan.contains(Point(lon, lat)):  # Note the swap
                        points.append((lat, lon))

        return points

    return {
        'customers': generate_points(),
        'hubs': [],
        'boundary': manhattan_coords
    }