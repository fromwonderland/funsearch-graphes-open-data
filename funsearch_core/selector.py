"""Select top-performing candidates."""

from __future__ import annotations

from typing import Dict, List, Tuple


class Selector:
    def __init__(self, keep: int = 2):
        self.keep = keep

    def select(self, evaluations: List[Tuple[str, Dict[str, object]]]) -> List[str]:
        """
        evaluations: list of (candidate_code, result_dict) tuples.
        Returns a list of candidate_code strings to keep.
        """
        ranked = sorted(evaluations, key=lambda item: item[1].get("score", float("-inf")), reverse=True)
        return [code for code, _ in ranked[: self.keep]]

