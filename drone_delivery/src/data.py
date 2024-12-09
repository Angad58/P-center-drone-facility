import json
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.ops import triangulate

class NYCDataProcessor:
    def __init__(self):
        self.borough_codes = {
            "1": "Manhattan",
            "2": "Bronx",
            "3": "Brooklyn", 
            "4": "Queens",
            "5": "Staten Island"
        }
    
    def load_geojson(self, file_path):
        """Load GeoJSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading GeoJSON: {e}")
            return None
    
    def extract_borough_coordinates(self, geojson_data, boro_code):
        """Extract coordinates for a specific borough"""
        for feature in geojson_data['features']:
            if feature['properties']['boro_code'] == boro_code:
                return feature['geometry']['coordinates']
        return None
    
    def generate_points_in_borough(self, coordinates, num_points=100):
        """Generate random points within a borough boundary"""
        # Convert coordinates to polygon
        polygon_coords = []
        for poly in coordinates:
            for ring in poly:
                polygon_coords.extend([(lon, lat) for lon, lat in ring])
        
        polygon = Polygon(polygon_coords)
        
        # Triangulate the polygon
        triangles = triangulate(polygon)
        areas = [t.area for t in triangles]
        weights = np.array(areas) / sum(areas)
        
        points = []
        while len(points) < num_points:
            # Select random triangle based on area
            triangle = np.random.choice(triangles, p=weights)
            
            # Generate point in triangle
            a, b, c = triangle.exterior.coords[:-1]
            r1, r2 = np.random.random(2)
            s = np.sqrt(r1)
            point = (
                (1 - s) * np.array(a) + 
                (s * (1 - r2)) * np.array(b) + 
                (s * r2) * np.array(c)
            )
            
            points.append((point[1], point[0]))  # Convert to lat, lon
            
        return points
    
    def apply_density_weights(self, points, density_zones):
        """Apply density weights to points"""
        weighted_points = []
        for lat, lon in points:
            weight = 1.0
            for zone, (minlat, maxlat, minlon, maxlon, w) in density_zones.items():
                if minlat <= lat <= maxlat and minlon <= lon <= maxlon:
                    weight = w * 2
            if np.random.random() < weight:
                weighted_points.append((lat, lon))
        return weighted_points
    
    def get_borough_data(self, geojson_file, boro_code, num_points=100):
        """Get all data for a borough including boundary and generated points"""
        geojson_data = self.load_geojson(geojson_file)
        if not geojson_data:
            return None
        
        coordinates = self.extract_borough_coordinates(geojson_data, boro_code)
        if not coordinates:
            return None
        
        points = self.generate_points_in_borough(coordinates, num_points)
        
        return {
            'borough': self.borough_codes[boro_code],
            'boundary': coordinates,
            'points': points,
            'hubs': []  # Empty list for hubs to be added later
        }

# Example density zones (can be modified as needed)
DENSITY_ZONES = {
    'manhattan_midtown': (40.7480, 40.7630, -73.9900, -73.9700, 0.25),
    'manhattan_downtown': (40.7050, 40.7150, -74.0150, -74.0000, 0.15),
    'brooklyn_downtown': (40.6900, 40.7000, -73.9900, -73.9700, 0.20),
    'queens_central': (40.7400, 40.7550, -73.8900, -73.8700, 0.15)
}