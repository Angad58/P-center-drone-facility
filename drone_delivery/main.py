from src.vis import HubVisualizer
from src.data import load_data
from src.pCenter import PCenter

def main():
    # Load random NYC points
    data = load_data(num_points=2000)  # Generate 200 points
    
    # Solve for hub locations
    num_centers = 10  # Number of hubs you want
    solver = PCenter(num_centers=num_centers, points=data['customers'])
    optimal_hubs = solver.solve_greedy()
    
    # Update data
    data['hubs'] = optimal_hubs
    
    # Visualize
    viz = HubVisualizer()
    map = viz.create_map(data)
    map.save('nyc_delivery_map.html')
    
    print(f"Generated {len(data['customers'])} customer points")
    print(f"Optimized {num_centers} hub locations")

if __name__ == "__main__":
    main()