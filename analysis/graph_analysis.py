"""
Quick inspection script for runs.

Reads JSONL logs from runs/<timestamp>/scores.jsonl and prints best score plus
summary statistics. Extend this file to add clustering/visualization.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import List


def load_scores(path: pathlib.Path) -> List[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize(run_dir: pathlib.Path) -> None:
    log_path = run_dir / "scores.jsonl"
    if not log_path.exists():
        raise FileNotFoundError(f"No scores.jsonl in {run_dir}")
    rows = load_scores(log_path)
    best = max(rows, key=lambda r: r.get("score", float("-inf")))
    print(f"Total evaluations: {len(rows)}")
    print(f"Best score: {best.get('score')}")
    print(f"Best details: {best.get('result', {})}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a FunSearch run directory.")
    parser.add_argument("run_dir", type=pathlib.Path, help="Path to run directory containing scores.jsonl")
    args = parser.parse_args()
    summarize(args.run_dir)


if __name__ == "__main__":
    main()
