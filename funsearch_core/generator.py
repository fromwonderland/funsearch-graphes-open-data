"""
Candidate generator stub.

In production you would call an LLM with the prompt and prior solutions.
Here we ship a deterministic fallback so the pipeline can run offline.
"""

from __future__ import annotations

import pathlib
import random
import textwrap
from typing import List, Optional


class FunSearchGenerator:
    def __init__(self, prompt_path: pathlib.Path):
        self.prompt_path = prompt_path
        self.prompt = prompt_path.read_text(encoding="utf-8")

    def generate_candidates(
        self, previous_solutions: Optional[List[str]] = None, n: int = 3
    ) -> List[str]:
        """Return Python code strings. Uses small heuristics for offline runs."""
        seeds = [
            """
def color_graph(graph):
    # Simple greedy coloring.
    edges = graph["edges"]
    adj = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    colors = {}
    for node in sorted(adj):
        used = {colors[n] for n in adj[node] if n in colors}
        color = 0
        while color in used:
            color += 1
        colors[node] = color
    return colors
""",
            """
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
""",
            """
def color_graph(graph):
    # Try to reuse colors aggressively by scanning neighbors first.
    edges = graph["edges"]
    adj = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    colors = {}
    for node in sorted(adj):
        neighbor_colors = [colors[n] for n in adj[node] if n in colors]
        palette = sorted(set(neighbor_colors))
        chosen = 0
        while chosen in palette:
            chosen += 1
        colors[node] = chosen
    return colors
""",
        ]

        generated = []
        rnd = random.Random(0)
        for _ in range(n):
            template = rnd.choice(seeds)
            generated.append(textwrap.dedent(template).strip() + "\n")

        # Simple tweak: if we have previous solutions, append a comment to hint reuse.
        if previous_solutions:
            generated.append(
                textwrap.dedent(
                    """
                    def color_graph(graph):
                        # Reuse previous best but keep deterministic order.
                        edges = graph["edges"]
                        adj = {}
                        for u, v in edges:
                            adj.setdefault(u, []).append(v)
                            adj.setdefault(v, []).append(u)
                        # Prefer nodes with most neighbors first.
                        order = sorted(adj.keys(), key=lambda n: -len(adj[n]))
                        colors = {}
                        for node in order:
                            used = {colors[n] for n in adj[node] if n in colors}
                            color = 0
                            while color in used:
                                color += 1
                            colors[node] = color
                        return colors
                    """
                ).strip()
                + "\n"
            )

        return generated[:n]

