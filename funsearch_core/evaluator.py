"""Evaluate candidate code against a problem module."""

from __future__ import annotations

import importlib
from typing import Dict


class Evaluator:
    def __init__(self, problem_module: str):
        self.problem_module = problem_module
        self.problem = importlib.import_module(problem_module)

    def evaluate(self, candidate_code: str) -> Dict[str, object]:
        """Return a dict with score and optional details."""
        try:
            solution_fn = self.problem.load_solution_function(candidate_code)
            result = self.problem.score_function(solution_fn)
        except Exception as exc:  # pylint: disable=broad-except
            return {"score": float("-inf"), "error": str(exc)}
        return result

