"""
Minimal FunSearch loop to orchestrate generation -> evaluation -> selection.

This script intentionally avoids external dependencies so a demo run works
out-of-the-box. Replace FunSearchGenerator with a real LLM-backed generator
for production workflows.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import time
from typing import List, Tuple

try:
    # When executed as a module: python -m funsearch_core.loop
    from .evaluator import Evaluator
    from .generator import FunSearchGenerator
    from .selector import Selector
except ImportError:  # pragma: no cover
    # When executed as a script: python funsearch_core/loop.py
    import sys
    _repo_root = pathlib.Path(__file__).resolve().parents[1]
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))
    from funsearch_core.evaluator import Evaluator
    from funsearch_core.generator import FunSearchGenerator
    from funsearch_core.selector import Selector


def run_loop(
    problem: str,
    prompt: pathlib.Path,
    iterations: int = 1,
    candidates: int = 3,
    run_dir: pathlib.Path | None = None,
) -> pathlib.Path:
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    base_run_dir = run_dir or pathlib.Path(__file__).parent.parent / "runs" / timestamp
    base_run_dir.mkdir(parents=True, exist_ok=True)

    evaluator = Evaluator(problem_module=problem)
    generator = FunSearchGenerator(prompt_path=prompt)
    selector = Selector()

    kept: List[str] = []
    log_path = base_run_dir / "scores.jsonl"
    with log_path.open("w", encoding="utf-8") as log_file:
        for step in range(iterations):
            candidates_code = generator.generate_candidates(previous_solutions=kept, n=candidates)
            evaluations: List[Tuple[str, dict]] = []
            for code in candidates_code:
                result = evaluator.evaluate(code)
                evaluations.append((code, result))
                log_file.write(json.dumps({"step": step, "score": result.get("score"), "result": result}) + "\n")
            kept = selector.select(evaluations)

            # Persist the best code for inspection.
            if kept:
                best_path = base_run_dir / f"best_step_{step}.py"
                best_path.write_text(kept[0], encoding="utf-8")

    return base_run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a minimal FunSearch loop.")
    parser.add_argument("--problem", required=True, help="Problem module, e.g. problems.min_palette")
    parser.add_argument("--prompt", required=True, type=pathlib.Path, help="Prompt text file")
    parser.add_argument("--iterations", type=int, default=1, help="Number of generate/evaluate iterations")
    parser.add_argument("--candidates", type=int, default=3, help="Candidates per iteration")
    parser.add_argument("--run-dir", type=pathlib.Path, default=None, help="Optional output directory")
    args = parser.parse_args()

    run_path = run_loop(
        problem=args.problem,
        prompt=args.prompt,
        iterations=args.iterations,
        candidates=args.candidates,
        run_dir=args.run_dir,
    )
    print(f"Run finished. Outputs in: {run_path}")


if __name__ == "__main__":
    main()
