import folium
from folium import plugins
from shapely.geometry import Polygon
from shapely.ops import triangulate

class NYCVisualizer:
    def __init__(self):
        self.center = [40.7128, -74.0060]  # NYC center
        self.borough_colors = {
            "Manhattan": "red",
            "Bronx": "blue",
            "Brooklyn": "green",
            "Queens": "purple",
            "Staten Island": "orange"
        }
    
    def create_map(self, geojson_data, data):
        """Create interactive map with borough boundaries and points"""
        m = folium.Map(location=self.center, zoom_start=11)
        
        # Add GeoJSON layer
        folium.GeoJson(
            geojson_data,
            style_function=lambda feature: {
                'fillColor': self.borough_colors.get(
                    feature['properties']['boro_name'], '#ffff00'),
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.2
            },
            popup=folium.GeoJsonPopup(
                fields=['boro_name'],
                aliases=['Borough:']
            )
        ).add_to(m)
        
        # Add points if they exist
        if data and 'points' in data:
            for lat, lon in data['points']:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=3,
                    color='blue',
                    fill=True
                ).add_to(m)
        
        # Add hubs if they exist
        if data and 'hubs' in data and data['hubs']:
            for lat, lon in data['hubs']:
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color='red', icon='info-sign'),
                    popup='Hub'
                ).add_to(m)
                
                # Add coverage circle
                folium.Circle(
                    location=[lat, lon],
                    radius=1000,
                    color='red',
                    fill=True,
                    opacity=0.2
                ).add_to(m)
        
        # Add legend
        self._add_legend(m)
        
        return m
    
    def _add_legend(self, map_obj):
        """Add legend to map"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 180px;
                    border:2px solid grey; z-index:9999; background-color:white;
                    padding: 10px;
                    font-size: 14px;">
          <p><b>Legend:</b></p>
          <p><i class="fa fa-map-marker" style="color:red"></i> Hubs</p>
          <p><i class="fa fa-circle" style="color:blue"></i> Points</p>
          <p>Boroughs:</p>
          <p><span style="color:red">■</span> Manhattan</p>
          <p><span style="color:blue">■</span> Bronx</p>
          <p><span style="color:green">■</span> Brooklyn</p>
          <p><span style="color:purple">■</span> Queens</p>
          <p><span style="color:orange">■</span> Staten Island</p>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))

# Example usage:
def main():
    from data import NYCDataProcessor
    
    # Initialize processors
    data_processor = NYCDataProcessor()
    visualizer = NYCVisualizer()
    
    # Load data
    geojson_data = data_processor.load_geojson('B.geojson')
    manhattan_data = data_processor.get_borough_data('B.geojson', "1", num_points=100)
    
    # Create map
    map_obj = visualizer.create_map(geojson_data, manhattan_data)
    map_obj.save('nyc_visualization.html')

if __name__ == "__main__":
    main()