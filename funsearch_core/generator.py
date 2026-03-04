"""
Candidate generator stub.

In production you would call an LLM with the prompt and prior solutions.
Here we ship a deterministic fallback so the pipeline can run offline.
"""

from __future__ import annotations

import json
import os
import pathlib
import random
import textwrap
import urllib.error
import urllib.request
from typing import List, Optional


class FunSearchGenerator:
    def __init__(
        self,
        prompt_path: pathlib.Path,
        *,
        use_ollama: bool | None = None,
        ollama_base_url: str | None = None,
        ollama_model: str | None = None,
        ollama_timeout_s: float = 90.0,
    ):
        self.prompt_path = prompt_path
        self.prompt = prompt_path.read_text(encoding="utf-8")
        self.use_ollama = use_ollama if use_ollama is not None else (os.getenv("FUNSEARCH_USE_OLLAMA", "1") == "1")
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.ollama_timeout_s = float(os.getenv("OLLAMA_TIMEOUT_S", str(ollama_timeout_s)))

    def generate_candidates(
        self, previous_solutions: Optional[List[str]] = None, n: int = 3
    ) -> List[str]:
        """Return Python code strings. Uses Ollama if available; falls back to offline stubs."""
        if self.use_ollama:
            try:
                return self._generate_with_ollama(previous_solutions=previous_solutions, n=n)
            except Exception:
                # Keep demo resilient: if Ollama is down/unreachable, still run.
                pass
        return self._generate_offline(previous_solutions=previous_solutions, n=n)

    def _generate_with_ollama(
        self, previous_solutions: Optional[List[str]] = None, n: int = 3
    ) -> List[str]:
        """
        Call Ollama local API to generate code.

        Requires an Ollama service running at OLLAMA_BASE_URL (default localhost:11434).
        """
        system = (
            "You are an expert Python developer. "
            "You generate ONLY valid Python code (no markdown fences). "
            "Return exactly one function definition color_graph(graph) using graph['edges'] (list of (u,v))."
        )
        reinject = ""
        if previous_solutions:
            reinject = "\n\nPrevious best solution(s) (for improvement, do NOT copy blindly):\n" + "\n\n".join(
                previous_solutions[:2]
            )

        user_prompt = (
            self.prompt
            + "\n\nGraph format example: graph = {'edges': [(0,1), (1,2), (2,0)]}"
            + "\nReturn a dict node->color, using as few colors as possible."
            + reinject
            + "\n\nNow output Python code only, defining color_graph(graph) and nothing else."
        )

        outputs: List[str] = []
        for i in range(n):
            payload = {
                "model": self.ollama_model,
                "prompt": user_prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": 0.2 if i == 0 else 0.6,
                    "top_p": 0.9,
                },
            }
            url = self.ollama_base_url.rstrip("/") + "/api/generate"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.ollama_timeout_s) as resp:
                    raw = resp.read().decode("utf-8")
            except urllib.error.URLError as exc:
                raise RuntimeError(f"Ollama request failed: {exc}") from exc

            data = json.loads(raw)
            text = (data.get("response") or "").strip()
            outputs.append(self._sanitize_candidate_code(text))

        # Basic contract check: ensure we have a def color_graph and references to graph["edges"].
        validated = [code for code in outputs if self._looks_valid(code)]
        if len(validated) < n:
            # Fill the rest with offline fallbacks for robustness.
            validated.extend(
                self._generate_offline(previous_solutions=previous_solutions, n=n - len(validated))
            )
        return validated[:n]

    @staticmethod
    def _sanitize_candidate_code(text: str) -> str:
        """
        Normalize common LLM responses into pure Python code.

        Handles:
        - ```python ... ``` fences
        - a leading 'python' line (seen in some UIs)
        """
        cleaned = text.strip()
        if cleaned.startswith("```"):
            # ```python\n...\n```
            parts = cleaned.split("```")
            if len(parts) >= 3:
                cleaned = parts[1]
                # drop optional language tag on first line
                cleaned_lines = cleaned.splitlines()
                if cleaned_lines and cleaned_lines[0].strip().lower() in {"python", "py"}:
                    cleaned = "\n".join(cleaned_lines[1:])
            else:
                cleaned = cleaned.replace("```", "")

        # Some models respond with a first line "python"
        lines = cleaned.splitlines()
        if lines and lines[0].strip().lower() in {"python", "py"}:
            cleaned = "\n".join(lines[1:])

        return cleaned.strip() + "\n"

    @staticmethod
    def _looks_valid(code: str) -> bool:
        """Heuristic: must define color_graph and access graph['edges']."""
        lowered = code.lower()
        return "def color_graph" in lowered and "graph[" in lowered and "edges" in lowered

    def _generate_offline(
        self, previous_solutions: Optional[List[str]] = None, n: int = 3
    ) -> List[str]:
        """Offline deterministic candidates so the pipeline works without any LLM."""
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

