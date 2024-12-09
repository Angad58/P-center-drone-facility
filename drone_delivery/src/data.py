import json
import numpy as np
from shapely.geometry import Polygon, Point, MultiPolygon

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
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading GeoJSON: {e}")
            return None

    def create_borough_polygon(self, coordinates):
        """Create a proper polygon from GeoJSON coordinates"""
        # Handle MultiPolygon format from GeoJSON
        polygons = []
        for poly_coords in coordinates:
            # Each polygon might have multiple rings (exterior and holes)
            exterior_coords = poly_coords[0]  # First ring is exterior
            # Convert to (lon, lat) format for Shapely
            poly_points = [(coord[0], coord[1]) for coord in exterior_coords]
            polygons.append(Polygon(poly_points))
        
        # Combine all polygons into a MultiPolygon
        return MultiPolygon(polygons)

    def generate_points_in_borough(self, coordinates, num_points=100):
        """Generate random points within the borough boundary"""
        # Create proper polygon from coordinates
        borough_polygon = self.create_borough_polygon(coordinates)
        
        # Get the bounds of the polygon
        minx, miny, maxx, maxy = borough_polygon.bounds
        
        points = []
        attempts = 0
        max_attempts = num_points * 100  # Prevent infinite loop
        
        while len(points) < num_points and attempts < max_attempts:
            # Generate random point within bounds
            lon = np.random.uniform(minx, maxx)
            lat = np.random.uniform(miny, maxy)
            point = Point(lon, lat)
            
            # Check if point is within borough boundary
            if borough_polygon.contains(point):
                # Store as (lat, lon) for consistency with mapping
                points.append((lat, lon))
                
            attempts += 1
            
        if len(points) < num_points:
            print(f"Warning: Only generated {len(points)} valid points out of {num_points} requested")
            
        return points

    def get_borough_data(self, geojson_file, boro_code, num_points=100):
        """Get all data for a borough including boundary and generated points"""
        geojson_data = self.load_geojson(geojson_file)
        if not geojson_data:
            return None
        
        # Extract borough geometry
        for feature in geojson_data['features']:
            if feature['properties']['boro_code'] == boro_code:
                coordinates = feature['geometry']['coordinates']
                points = self.generate_points_in_borough(coordinates, num_points)
                
                return {
                    'borough': self.borough_codes[boro_code],
                    'boundary': coordinates,
                    'points': points,
                    'hubs': []
                }
        
        return None