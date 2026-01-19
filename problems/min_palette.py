"""
Minimal palette graph coloring example problem.

The goal: given an undirected graph (as edge list), output a color assignment
that uses as few distinct colors as possible while keeping adjacent nodes with
different colors.
"""

from __future__ import annotations

import json
import pathlib
from typing import Callable, Dict, List, Tuple

Graph = Dict[str, List[Tuple[int, int]]]
Coloring = Dict[int, int]


def _load_graphs() -> List[Graph]:
    """Load small graphs from data/sample_graph.json."""
    data_path = pathlib.Path(__file__).parent.parent / "data" / "sample_graph.json"
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    graphs: List[Graph] = []
    for g in raw["graphs"]:
        graphs.append({"name": g["name"], "edges": [tuple(e) for e in g["edges"]]})
    return graphs


def _build_adjacency(graph: Graph) -> Dict[int, List[int]]:
    """Convert edge list into adjacency for quick checks."""
    adj: Dict[int, List[int]] = {}
    for u, v in graph["edges"]:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    return adj


def load_solution_function(candidate_code: str) -> Callable[[Graph], Coloring]:
    """
    Execute candidate code in a small namespace and return its color_graph() function.
    The candidate must define:

    def color_graph(graph):
        # graph["edges"] is a list of (u, v) pairs
        return {node: color_id, ...}
    """
    local_vars: Dict[str, object] = {}
    safe_globals = {"__builtins__": {"range": range, "len": len}}
    exec(candidate_code, safe_globals, local_vars)  # nosec: controlled demo code
    if "color_graph" not in local_vars:
        raise ValueError("Candidate code must define color_graph(graph).")
    return local_vars["color_graph"]


def _is_valid_coloring(adj: Dict[int, List[int]], coloring: Coloring) -> bool:
    for node, neighbors in adj.items():
        for nb in neighbors:
            if coloring.get(node) == coloring.get(nb):
                return False
    return True


def _color_count(coloring: Coloring) -> int:
    return len(set(coloring.values()))


def score_function(solution_fn: Callable[[Graph], Coloring]) -> Dict[str, float]:
    """
    Evaluate a candidate coloring function on toy graphs.

    Score is negative total colors used (fewer colors => higher score),
    with a heavy penalty for invalid colorings.
    """
    graphs = _load_graphs()
    total_colors = 0
    penalties = 0
    details = []

    for graph in graphs:
        adj = _build_adjacency(graph)
        coloring = solution_fn(graph)
        valid = _is_valid_coloring(adj, coloring)
        colors_used = _color_count(coloring)
        if not valid:
            penalties += 5.0
        total_colors += colors_used
        details.append(
            {
                "graph": graph["name"],
                "valid": valid,
                "colors_used": colors_used,
            }
        )

    score = -float(total_colors + penalties)
    return {"score": score, "details": details}
