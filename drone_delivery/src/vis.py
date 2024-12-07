import folium
from folium import plugins

class HubVisualizer:
    def __init__(self):
        self.center = [40.7128, -74.0060]  # Default center (NYC)
    
    def create_map(self, data):
        m = folium.Map(location=[40.7831, -73.9712], zoom_start=12)
        
        # Draw Manhattan boundary
        folium.Polygon(
            locations=data['boundary'],
            color='red',
            weight=2,
            fill=True,
            fill_opacity=0.1
        ).add_to(m)
        
        # Plot points
        for lat, lon in data['customers']:
            folium.CircleMarker(
                location=[lat, lon],
                radius=3,
                color='blue',
                fill=True
            ).add_to(m)
        
        # Plot hubs
        for lat, lon in data['hubs']:
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color='red')
            ).add_to(m)
        
        return m