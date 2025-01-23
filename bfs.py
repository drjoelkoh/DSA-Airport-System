from collections import deque

class BFS:
    def run_bfs(self,graph, source, destination, num_paths):
        shortest_paths = []  # List to store the shortest paths
        visited = set()  # Set to track visited nodes
        
        if source not in graph or destination not in graph:
            return shortest_paths
        
        queue = deque([(source, [source])])  # (node, path)
        
        while queue and len(shortest_paths) < num_paths:
            current_node, current_path = queue.popleft()  # Dequeue the node and its path
            
            if current_node == destination:
                shortest_paths.append(current_path)
                continue
            
            visited.add(current_node)  # Mark the current node as visited
            
            for neighbor in graph[current_node]:
                if neighbor not in visited:  # Avoid revisiting visited nodes
                    queue.append((neighbor, current_path + [neighbor]))
        
        return shortest_paths
    
    #Function to calculate the distance of the path for BFS
    def calculate_path_distance(self,graph,path):
        total_distance = 0
        for i in range(len(path) - 1):
            source = path[i]
            destination = path[i + 1]
            total_distance += graph[source][destination]
        return total_distance
