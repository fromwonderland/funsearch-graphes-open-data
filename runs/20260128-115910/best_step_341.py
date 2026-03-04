def color_graph(graph):
    # Degree-sorted greedy (tends to reduce palette).
    edges = graph["edges"]
    adj = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    order = sorted(adj.keys(), key=lambda n: -len(adj[n]))
    colors = {}
    for node in order:
        used = {colors[n] for n in adj[node] if n in colors}
        color = 0
        while color in used:
            color += 1
        colors[node] = color
    return colors
