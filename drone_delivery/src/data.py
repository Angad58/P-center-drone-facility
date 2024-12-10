# src/data.py
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
import os

class NYCDataProcessor:
    def __init__(self):
        # Borough data from 2020 census
        self.borough_codes = {
            "1": {
                "name": "Manhattan",
                "population": 1694251,
                "density": 74781,
                "centers": [(40.7128, -73.9947), (40.7589, -73.9851)],  # Midtown, Downtown
            },
            "2": {
                "name": "Bronx",
                "population": 1472654,
                "density": 34920,
                "centers": [(40.8448, -73.8648)]  # South Bronx
            },
            "3": {
                "name": "Brooklyn",
                "population": 2736074,
                "density": 39438,
                "centers": [(40.6782, -73.9442)]  # Downtown Brooklyn
            },
            "4": {
                "name": "Queens",
                "population": 2405464,
                "density": 22125,
                "centers": [(40.7282, -73.7949)]  # Long Island City
            },
            "5": {
                "name": "Staten Island",
                "population": 495747,
                "density": 8618,
                "centers": [(40.6295, -74.0776)]  # St. George
            }
        }
        
        self.total_population = sum(b["population"] for b in self.borough_codes.values())
        self.max_density = max(b["density"] for b in self.borough_codes.values())

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
        """Calculate weight based on actual density and distance to centers"""
        lat, lon = point.y, point.x
        borough_data = self.borough_codes[boro_code]
        base_weight = borough_data['density'] / self.max_density
        
        # Calculate distance to nearest center
        min_distance = float('inf')
        for center_lat, center_lon in borough_data['centers']:
            dist = np.sqrt((lat - center_lat)**2 + (lon - center_lon)**2)
            min_distance = min(min_distance, dist)
        
        # Adjust weight based on distance
        distance_factor = np.exp(-min_distance * 100)  # Exponential decay
        return base_weight * (1 + distance_factor)

    def calculate_points_per_borough(self, total_points):
        """Calculate points per borough based on population"""
        points = {}
        for code, data in self.borough_codes.items():
            points[code] = int((data["population"] / self.total_population) * total_points)
        return points

    def generate_points_in_borough(self, geometry, boro_code, num_points):
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
                if np.random.random() < density_weight:
                    points.append((lat, lon))
            
            attempts += 1
        
        return points

    def process_all_boroughs(self, geojson_data, total_points=1000):
        """Process all boroughs with population-based point distribution"""
        points_per_borough = self.calculate_points_per_borough(total_points)
        borough_datasets = {}
        
        for boro_code, num_points in points_per_borough.items():
            borough_data = geojson_data[geojson_data['boro_code'] == boro_code]
            if not borough_data.empty:
                try:
                    geometry = borough_data.iloc[0].geometry
                    points = self.generate_points_in_borough(geometry, boro_code, num_points)
                    
                    borough_datasets[boro_code] = {
                        'borough': self.borough_codes[boro_code]['name'],
                        'geometry': geometry,
                        'points': points,
                        'population': self.borough_codes[boro_code]['population'],
                        'density': self.borough_codes[boro_code]['density'],
                        'hubs': []
                    }
                    
                    print(f"Generated {len(points)} points for {self.borough_codes[boro_code]['name']}")
                    print(f"Population: {self.borough_codes[boro_code]['population']:,}")
                    print(f"Density: {self.borough_codes[boro_code]['density']:,}/sq mile\n")
                    
                except Exception as e:
                    print(f"Error processing borough {boro_code}: {e}")
        
        return borough_datasets