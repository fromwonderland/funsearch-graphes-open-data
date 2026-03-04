python
def color_graph(graph):
    def dsatur(node, colors):
        saturation = {n: 0 for n in graph}
        degree = {n: len(graph[n]) for n in graph}
        
        # Initialize the first node with color 0
        current_node = next(iter(graph))
        coloring = {current_node: 0}
        del graph[current_node]
        
        while graph:
            # Find the most saturated and least colored neighbor
            max_saturation = -1
            chosen_node = None
            for node in graph:
                if degree[node] > max_saturation or (degree[node] == max_saturation and len(set(coloring[n] for n in graph[node])) < len(set(coloring.values()))):
                    max_saturation = degree[node]
                    chosen_node = node
            
            # Assign the smallest available color
            used_colors = {coloring[n] for n in graph[chosen_node]}
            for color in range(len(graph)):
                if color not in used_colors:
                    coloring[chosen_node] = color
                    break
            
            # Update saturation and degree
            for neighbor in graph[chosen_node]:
                saturation[neighbor] += 1
                degree[neighbor] -= 1
            
            del graph[chosen_node]
        
        return coloring

    return dsatur(graph, {})
