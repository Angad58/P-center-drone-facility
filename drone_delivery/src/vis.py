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
        # Add borough boundaries for checking coverage
        self.borough_bounds = {
            "Manhattan": [[40.700292, -74.020438], [40.878112, -73.907001]],
            "Bronx": [[40.785743, -73.933612], [40.916617, -73.765271]],
            "Brooklyn": [[40.570927, -74.042281], [40.739446, -73.833014]],
            "Queens": [[40.541722, -73.962582], [40.810875, -73.700172]],
            "Staten Island": [[40.477399, -74.259090], [40.651800, -74.052140]]
        }

    def create_map(self, geojson_data, borough_datasets, hub_locations=None, drone_range=5.0):
        """Create interactive map with borough boundaries, points and hubs"""
        m = folium.Map(location=self.center, zoom_start=11)
        
        # Add borough boundaries
        folium.GeoJson(
            geojson_data,
            style_function=lambda feature: {
                'fillColor': self.borough_colors.get(
                    feature['properties']['boro_name'], '#ffff00'),
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.2
            }
        ).add_to(m)
        
        # Add demand points
        for boro_code, data in borough_datasets.items():
            borough_name = data['borough']
            color = self.borough_colors.get(borough_name, 'blue')
            
            for lat, lon in data['points']:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=2,
                    color=color,
                    fill=True,
                    fillOpacity=0.6,
                    popup=f"{borough_name} Point: ({lat:.4f}, {lon:.4f})"
                ).add_to(m)

        # Add hub locations and coverage
        if hub_locations:
            for i, (lat, lon) in enumerate(hub_locations):
                # Add hub marker
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color='red', icon='star', prefix='fa'),
                    popup=f'Hub {i+1}: ({lat:.4f}, {lon:.4f})'
                ).add_to(m)

                # Add coverage circle with intersection check
                folium.Circle(
                    location=[lat, lon],
                    radius=3000,
                    color='red',
                    weight=2,
                    fill=True,
                    fillColor='red',
                    fillOpacity=0.1,
                    popup=f'{drone_range}km service radius from Hub {i+1}'
                ).add_to(m)

        # Updated legend
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px;
                    border:2px solid grey; z-index:9999; background-color:white;
                    padding: 10px;
                    font-size: 14px;">
          <h4 style="margin-top:0;">NYC Drone Delivery Hubs</h4>
          <hr style="margin:5px 0;">
          <p><i class="fa fa-star" style="color:red"></i> Service Hubs</p>
          <p style="color:red">⬤ Service Coverage ({drone_range}km)</p>
          <p><b>Demand Points:</b></p>
          <p><span style="color:red">●</span> Manhattan</p>
          <p><span style="color:blue">●</span> Bronx</p>
          <p><span style="color:green">●</span> Brooklyn</p>
          <p><span style="color:purple">●</span> Queens</p>
          <p><span style="color:orange">●</span> Staten Island</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m