def color_graph(graph):
    def dfs(node, color_id, colors, graph):
        if node in colors:
            return True
        colors[node] = color_id
        for neighbor in graph[node]:
            if neighbor in colors and colors[neighbor] == color_id:
                return False
            if neighbor not in colors and not dfs(neighbor, (color_id + 1) % len(colors), colors, graph):
                return False
        return True

    colors = {}
    for node in graph:
        if node not in colors and not dfs(node, 0, colors, graph):
            return None
    return colors
