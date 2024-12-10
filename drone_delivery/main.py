import os 
import pandas as pd
from src.vis import NYCVisualizer
from src.data import NYCDataProcessor
from src.pCenter import PCenter

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
    
    # Process all boroughs with demand points
    borough_datasets = data_processor.process_all_boroughs(geojson_data, total_points=200)
    
    if not borough_datasets:
        print("No data was generated.")
        return

    # Save demand points for each borough
    for boro_code, data in borough_datasets.items():
        df = pd.DataFrame(data['points'], columns=['latitude', 'longitude'])
        csv_path = os.path.join(output_path, f"{data['borough'].lower()}_points.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved points to: {csv_path}")
    
    # Initialize P-Center solver
    solver = PCenter(borough_datasets=borough_datasets)
    solver.precalculate_distances()
    # Find minimum number of centers needed for coverage
    drone_range = 3.0  # km
    max_centers = 50
    min_centers, centers = solver.binary_search_min_centers(
        drone_range=drone_range, 
        max_centers=max_centers
    )
    if centers is None:
        print("No solution found for the given parameters.")
        return
    # Get solution metrics
    # metrics = solver.evaluate_solution(centers, drone_range)
    
    # # Print solution details
    # print("\nP-Center Solution Results:")
    # print(f"Minimum number of hubs needed: {min_centers}")
    # print(f"Maximum service distance: {metrics['max_distance']:.2f} km")
    # print(f"Average service distance: {metrics['avg_distance']:.2f} km")
    # print(f"Population coverage ({drone_range}km): {metrics['coverage_percentage']:.1f}%")
    # print(f"Points covered: {metrics['covered_points']} out of {metrics['total_points']}")
    
    # Save hub locations
    hub_df = pd.DataFrame(centers, columns=['latitude', 'longitude'])
    hub_path = os.path.join(output_path, 'optimal_hubs.csv')
    hub_df.to_csv(hub_path, index=False)
    print(f"\nSaved hub locations to: {hub_path}")
    
    # Create visualization
    print(len(centers))
    print(len(borough_datasets))
    map_obj = visualizer.create_map(geojson_data, borough_datasets, centers)
    map_path = os.path.join(output_path, 'nyc_boroughs_solution.html')
    map_obj.save(map_path)
    
    print(f"\nVisualization saved to: {map_path}")
    # print(f"Total demand points: {metrics['total_points']}")
    # print(f"Number of service hubs: {len(centers)}")

if __name__ == "__main__":
    main()