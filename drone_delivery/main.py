# main.py
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
    
    # Generate points for each borough
    borough_datasets = {}
    total_points = 0
    
    for boro_code in data_processor.borough_codes:
        data = data_processor.get_borough_data(
            geojson_data,
            boro_code, 
            num_points=200  # Points per borough
        )
        
        if data and 'points' in data:
            borough_datasets[boro_code] = data
            num_points = len(data['points'])
            total_points += num_points
            print(f"Generated {num_points} points for {data['borough']}")
            
            # Save borough points to CSV
            df = pd.DataFrame(data['points'], columns=['latitude', 'longitude'])
            csv_path = os.path.join(output_path, f"{data['borough'].lower()}_points.csv")
            df.to_csv(csv_path, index=False)
            print(f"Saved points to: {csv_path}")
    
    if total_points == 0:
        print("No points were generated.")
        return
    
    # Create visualization
   # Inside main()
    # Create visualization
    map_obj = visualizer.create_map(geojson_data, borough_datasets)  # Pass borough_datasets, not combined_data
    map_path = os.path.join(output_path, 'nyc_boroughs_points.html')
    map_obj.save(map_path)
    print(f"\nVisualization saved to: {map_path}")
    print(f"Total points generated: {total_points}")
    print(f"Average points per borough: {total_points/len(borough_datasets):.1f}")

if __name__ == "__main__":
    main()