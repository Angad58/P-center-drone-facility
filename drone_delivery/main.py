import os
from src.vis import NYCVisualizer
from src.data import NYCDataProcessor

def main():
    # Set up correct file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    geojson_path = os.path.join(current_dir, 'data', 'b.geojson')
    
    # Initialize processors
    data_processor = NYCDataProcessor()
    visualizer = NYCVisualizer()
    
    # Load GeoJSON data
    geojson_data = data_processor.load_geojson(geojson_path)
    
    if geojson_data is None:
        print(f"Failed to load GeoJSON file from: {geojson_path}")
        return
    
    # Combine all points into one dataset for visualization
    combined_data = {
        'points': [],  # Will hold all generated points
        'hubs': [],    # Empty list for future hub locations
        'boundary': [] # Will hold boundary coordinates
    }
    
    # Generate and collect points for each borough
    for boro_code in data_processor.borough_codes:
        data = data_processor.get_borough_data(
            geojson_path, 
            boro_code, 
            num_points=200
        )
        if data and 'points' in data:
            combined_data['points'].extend(data['points'])
            # Add boundary if present
            if 'boundary' in data:
                combined_data['boundary'].extend(data['boundary'])
    
    if not combined_data['points']:
        print("No points were generated.")
        return
    
    # Create visualization
    map_obj = visualizer.create_map(geojson_data, combined_data)
    
    # Save to output directory
    output_path = os.path.join(current_dir, 'output')
    os.makedirs(output_path, exist_ok=True)
    map_obj.save(os.path.join(output_path, 'nyc_boroughs_points.html'))
    
    # Print summary
    print(f"\nTotal points generated: {len(combined_data['points'])}")

if __name__ == "__main__":
    main()