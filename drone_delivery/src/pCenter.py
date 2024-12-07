from geopy.distance import geodesic

class PCenter:
    def __init__(self, num_centers, points):
        self.num_centers = num_centers
        self.points = points
    

    def solve_greedy(self):
        centers=[]
        remaining_points = self.points.copy()

        centers.append(remaining_points[0])
        remaining_points.remove(remaining_points[0])

        while len(centers) < self.num_centers:
            next_center = self.find_farthest_point(centers, remaining_points)
            centers.append(next_center)
            remaining_points.remove(next_center)

        return centers
    
    def find_farthest_point(self, centers, candidates):
        max_min_distance = -1
        furthest_point = None
        for point in candidates:
         min_distance = min(self._calculate_distance(point, center) 
                         for center in centers)
         if min_distance > max_min_distance:
            max_min_distance = min_distance
            furthest_point = point


        return furthest_point
    
    def _calculate_distance(self, point1, point2):
        # Haversine distance
        from geopy.distance import geodesic
        return geodesic(point1, point2).kilometers