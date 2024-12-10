from geopy.distance import geodesic
import numpy as np

class PCenter:
    def __init__(self, borough_datasets):
        """
        Initialize P-Center solver with borough datasets
        
        Parameters:
        - borough_datasets: dictionary containing borough data with population-weighted points
        """
        self.borough_datasets = borough_datasets
        # Combine all points from all boroughs
        self.points = []
        self.point_weights = []
        self.distance_matrix = None
        for boro_code, data in borough_datasets.items():
            borough_points = data['points']
            # Get borough population density for weighting
            density = data['density']
            self.points.extend(borough_points)
            # Add weights based on borough density
            self.point_weights.extend([density] * len(borough_points))
    
    def precalculate_distances(self):
        """
        Precompute pairwise distances between all points for faster access.
        Stores distances in a dictionary with point indices as keys.
        """
        num_points = len(self.points)
        self.distance_matrix = np.zeros((num_points, num_points))
        
        for i in range(num_points):
            for j in range(i + 1, num_points):
                dist = self._calculate_distance(self.points[i], self.points[j])
                self.distance_matrix[i][j] = dist
                self.distance_matrix[j][i] = dist

    def _get_distance(self, point_idx1, point_idx2):
        """
        Retrieve the precalculated distance between two points.
        
        Parameters:
        - point_idx1: Index of the first point
        - point_idx2: Index of the second point
        
        Returns:
        - Distance between the two points
        """
        return self.distance_matrix[point_idx1][point_idx2]


    def binary_search_min_centers(self, drone_range=3.0, max_centers=20):
        """
        Find minimum number of centers needed for coverage using binary search
        
        Parameters:
        - drone_range: maximum coverage radius in km
        - max_centers: maximum number of centers to consider
        
        Returns:
        - min_required: minimum number of centers needed
        - best_centers: locations of centers for the minimum solution
        """
        left = 1
        right = max_centers
        min_required = max_centers
        best_centers = None
        
        while left <= right:
            mid = (left + right) // 2
            centers = self.solve_greedy(mid)
            
            if self.test_feasibility(centers, drone_range):
                # This many centers works, try fewer
                min_required = mid
                best_centers = centers
                right = mid - 1
            else:
                # Need more centers
                left = mid + 1
        
        return min_required, best_centers

    def test_feasibility(self, centers, drone_range):
      """Test if given centers can cover all points within drone_range"""
      for point_idx, point in enumerate(self.points):
          min_distance = min(self._get_distance(point_idx, self.points.index(center)) 
                           for center in centers)
          if min_distance > drone_range:
              return False
      return True

    def solve_greedy(self, num_centers):
        """
        Solve the p-center problem using a weighted greedy approach
        
        Parameters:
        - num_centers: number of centers to place
        """
        centers = []
        remaining_points = self.points.copy()
        remaining_weights = self.point_weights.copy()
        
        # Choose first center as point in highest density area
        max_weight_idx = np.argmax(remaining_weights)
        centers.append(remaining_points[max_weight_idx])
        remaining_points.pop(max_weight_idx)
        remaining_weights.pop(max_weight_idx)
        
        while len(centers) < num_centers:
            next_center = self.find_farthest_point(centers, remaining_points, remaining_weights)
            if next_center is None:
                break
            centers.append(next_center)
            idx = remaining_points.index(next_center)
            remaining_points.pop(idx)
            remaining_weights.pop(idx)
        
        return centers
    
    def find_farthest_point(self, centers, candidates, weights):
      """Find the farthest point considering population density weights"""
      max_weighted_distance = -1
      furthest_point = None
      
      for candidate_idx, point in enumerate(candidates):
          min_distance = min(self._get_distance(candidate_idx, self.points.index(center)) 
                           for center in centers)
          # Weight the distance by population density
          weighted_distance = min_distance * weights[candidate_idx]
          
          if weighted_distance > max_weighted_distance:
              max_weighted_distance = weighted_distance
              furthest_point = point
      
      return furthest_point
    
    def _calculate_distance(self, point1, point2):
        """Calculate distance between two points using Haversine formula"""
        return geodesic(point1, point2).kilometers
    
    def evaluate_solution(self, centers, drone_range=3.0):
        """
        Evaluate the solution quality
        
        Parameters:
        - centers: list of center locations
        - drone_range: maximum coverage radius in km
        """
        max_distance = -1
        total_distance = 0
        covered_points = 0
        
        for center_idx, center in enumerate(centers):
            center_idx = self.points.index(center)
            for point_idx, point in enumerate(self.points):
                min_distance = self._get_distance(point_idx, center_idx)
                max_distance = max(max_distance, min_distance)
                total_distance += min_distance
                
                if min_distance <= drone_range:
                    covered_points += 1
        
        coverage_percentage = (covered_points / len(self.points)) * 100
        avg_distance = total_distance / len(self.points)
        
        return {
            'max_distance': max_distance,
            'avg_distance': avg_distance,
            'coverage_percentage': coverage_percentage,
            'covered_points': covered_points,
            'total_points': len(self.points)
        }