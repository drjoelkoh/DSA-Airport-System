import heapq

class Astar:
    #a star algorithm to find cheapest flight cost path.
    def run_a_star(self,graph, start, goal):
        """
        A* algorithm to find the cheapest flight cost between two airports.
        
        Args:
        - graph: Adjacency list representation of the flight network.
        - start: Starting airport code.
        - goal: Destination airport code.
        
        Returns:
        - path: Cheapest flight path from start to goal as a list of airport codes.
        - cost: Total cost of the cheapest flight path.
        """
        # Initialize open set, closed set, and costs dictionary
        open_set = [(0, start)]
        closed_set = set()
        costs = {start: (0, None)}  # Cost is tuple (total cost so far, parent node)
        
        while open_set:
            #create a priority queue
            # Pop node with the lowest total cost
            current_cost, current_node = heapq.heappop(open_set)
            
            # Check if goal reached
            if current_node == goal:
                # Reconstruct path
                path = []
                while current_node in costs:
                    path.insert(0, current_node)
                    current_node = costs[current_node][1]
                return path, current_cost
            
            # Mark current node as visited
            closed_set.add(current_node)
            
            # Explore neighbors
            for neighbor, cost in graph[current_node].items():
                if neighbor in closed_set:
                    continue
                
                # Calculate tentative total cost
                tentative_cost = current_cost + cost
                
                # Update costs if new path is cheaper
                if neighbor not in costs or tentative_cost < costs[neighbor][0]:
                    costs[neighbor] = (tentative_cost, current_node)
                    f_value = tentative_cost  # For cheapest cost, heuristic is not needed
                    heapq.heappush(open_set, (f_value, neighbor))
        
        # No path found
        return None, float('inf')
