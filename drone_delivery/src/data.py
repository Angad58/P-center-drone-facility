# src/data.py
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
import os

class NYCDataProcessor:
    def __init__(self):
        self.borough_codes = {
            "1": {"name": "Manhattan", 
                  "high_density": [(40.7128, -73.9947), (40.7589, -73.9851), (40.7831, -73.9712)],
                  "weight": 3.0},
            "2": {"name": "Bronx", 
                  "high_density": [(40.8448, -73.8648), (40.8501, -73.8662)],
                  "weight": 2.0},
            "3": {"name": "Brooklyn", 
                  "high_density": [(40.6782, -73.9442), (40.6872, -73.9418)],
                  "weight": 2.5},
            "4": {"name": "Queens", 
                  "high_density": [(40.7282, -73.7949), (40.7464, -73.8213)],
                  "weight": 2.0},
            "5": {"name": "Staten Island", 
                  "high_density": [(40.6295, -74.0776)],
                  "weight": 1.5}
        }
        
        self.density_multipliers = {
            'very_high': 3.0,
            'high': 2.0,
            'medium': 1.5,
            'low': 1.0
        }

    def load_geojson(self, file_path):
        try:
            return gpd.read_file(file_path)
        except Exception as e:
            print(f"Error loading GeoJSON: {e}")
            return gpd.GeoDataFrame()

    def create_borough_polygon(self, geometry):
        if geometry.geom_type == 'MultiPolygon':
            return geometry
        return MultiPolygon([geometry])

    def get_density_weight(self, point, boro_code):
        lat, lon = point.y, point.x
        borough_data = self.borough_codes[boro_code]
        base_weight = borough_data['weight']
        
        min_distance = float('inf')
        for center_lat, center_lon in borough_data['high_density']:
            dist = np.sqrt((lat - center_lat)**2 + (lon - center_lon)**2)
            min_distance = min(min_distance, dist)
        
        if min_distance < 0.01:
            return base_weight * self.density_multipliers['very_high']
        elif min_distance < 0.02:
            return base_weight * self.density_multipliers['high']
        elif min_distance < 0.03:
            return base_weight * self.density_multipliers['medium']
        else:
            return base_weight * self.density_multipliers['low']

    def generate_points_in_borough(self, geometry, boro_code, num_points=100):
        borough_polygon = self.create_borough_polygon(geometry)
        minx, miny, maxx, maxy = borough_polygon.bounds
        
        points = []
        attempts = 0
        max_attempts = num_points * 100
        
        while len(points) < num_points and attempts < max_attempts:
            lon = np.random.uniform(minx, maxx)
            lat = np.random.uniform(miny, maxy)
            point = Point(lon, lat)
            
            if borough_polygon.contains(point):
                density_weight = self.get_density_weight(point, boro_code)
                acceptance_prob = density_weight / self.density_multipliers['very_high']
                
                if np.random.random() < acceptance_prob:
                    points.append((lat, lon))
            
            attempts += 1
        
        if len(points) < num_points:
            print(f"Warning: Generated {len(points)} out of {num_points} requested points for {self.borough_codes[boro_code]['name']}")
        
        return points

    def get_borough_data(self, geojson_data, boro_code, num_points=100):
        if geojson_data.empty:
            return None
        
        borough_data = geojson_data[geojson_data['boro_code'] == boro_code]
        
        if borough_data.empty:
            return None
            
        try:
            geometry = borough_data.iloc[0].geometry
            points = self.generate_points_in_borough(geometry, boro_code, num_points)
            
            return {
                'borough': self.borough_codes[boro_code]['name'],
                'geometry': geometry,
                'points': points,
                'hubs': []
            }
        except Exception as e:
            print(f"Error processing borough {boro_code}: {e}")
            return None