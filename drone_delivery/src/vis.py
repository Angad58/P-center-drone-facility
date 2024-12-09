import folium
from folium import plugins

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

    def create_map(self, geojson_data, borough_datasets):
        """Create interactive map with borough boundaries and points"""
        m = folium.Map(location=self.center, zoom_start=11)
        
        # Add GeoJSON layer for borough boundaries
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
        
        # Add points for each borough with corresponding colors
        for boro_code, data in borough_datasets.items():
            borough_name = data['borough']
            color = self.borough_colors.get(borough_name, 'blue')
            
            # Add demand points
            for lat, lon in data['points']:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=3,
                    color=color,
                    fill=True,
                    popup=f"{borough_name}: ({lat:.4f}, {lon:.4f})"
                ).add_to(m)
        
            # Add hubs if they exist
            if 'hubs' in data and data['hubs']:
                for lat, lon in data['hubs']:
                    folium.Marker(
                        location=[lat, lon],
                        icon=folium.Icon(color='red', icon='info-sign'),
                        popup=f'Hub in {borough_name}'
                    ).add_to(m)
                    
                    # Add coverage circle
                    folium.Circle(
                        location=[lat, lon],
                        radius=1000,  # 1km radius
                        color='red',
                        fill=True,
                        opacity=0.2
                    ).add_to(m)
        
        # Add density heatmap
        point_list = []
        for data in borough_datasets.values():
            point_list.extend([[lat, lon] for lat, lon in data['points']])
            
        plugins.HeatMap(point_list).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 180px;
                    border:2px solid grey; z-index:9999; background-color:white;
                    padding: 10px;
                    font-size: 14px;">
          <p><b>Legend:</b></p>
          <p><i class="fa fa-map-marker" style="color:red"></i> Hubs</p>
          <p>Points by Borough:</p>
          <p><span style="color:red">●</span> Manhattan</p>
          <p><span style="color:blue">●</span> Bronx</p>
          <p><span style="color:green">●</span> Brooklyn</p>
          <p><span style="color:purple">●</span> Queens</p>
          <p><span style="color:orange">●</span> Staten Island</p>
          <p>Heat Map: Population Density</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m