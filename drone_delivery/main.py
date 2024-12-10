import os
import pandas as pd
from src.vis import NYCVisualizer
from src.data import NYCDataProcessor

def main():
    # Initialize paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    geojson_path = os.path.join(current_dir, 'data', 'b.geojson')
    output_path = os.path.join(current_dir, 'output')
    os.makedirs(output_path, exist_ok=True)
    
    # Initialize processors
    data_processor = NYCDataProcessor()
    visualizer = NYCVisualizer()
    
    # Load GeoJSON data
    geojson_data = data_processor.load_geojson(geojson_path)
    
    if geojson_data.empty:
        print(f"Failed to load GeoJSON file from: {geojson_path}")
        return
    
    # Process all boroughs with 1000 total points
    borough_datasets = data_processor.process_all_boroughs(geojson_data, total_points=10000)
    
    if not borough_datasets:
        print("No data was generated.")
        return
    
    # Save point data for each borough
    for boro_code, data in borough_datasets.items():
        df = pd.DataFrame(data['points'], columns=['latitude', 'longitude'])
        csv_path = os.path.join(output_path, f"{data['borough'].lower()}_points.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved points to: {csv_path}")
    
    # Create visualization
    map_obj = visualizer.create_map(geojson_data, borough_datasets)
    map_path = os.path.join(output_path, 'nyc_boroughs_points.html')
    map_obj.save(map_path)
    
    # Print summary
    total_points = sum(len(data['points']) for data in borough_datasets.values())
    print(f"\nVisualization saved to: {map_path}")
    print(f"Total points generated: {total_points}")

if __name__ == "__main__":
    main()