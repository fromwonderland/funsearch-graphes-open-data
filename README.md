FunSearch project scaffold
==========================

This repository is a minimal scaffold for running FunSearch-style loops to generate, evaluate, select, and reinject candidate solutions to programming problems.

- `data/` — example data assets (graphs, csv, images).
- `problems/` — problem definitions exposing `load_solution_function` and `score_function`.
- `prompts/` — text prompts to steer candidate generation.
- `funsearch_core/` — generator / evaluator / selector / loop orchestrator.
- `runs/` — per-experiment outputs (candidates, scores, logs).
- `analysis/` — quick scripts to inspect runs and graphs.
- `notebooks/` — space for interactive exploration.

To try a miniature run, execute:

```
python funsearch_core/loop.py --problem problems.min_palette --prompt prompts/min_palette.txt --iterations 1 --candidates 3
```
