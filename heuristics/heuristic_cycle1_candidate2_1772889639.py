import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    # Degree heuristic - choose cell affecting most constrained cells
    max_degree = -1
    best_cell = None

    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                # Count empty cells in same row, column, and box
                degree = 0
                # Row and column
                for i in range(9):
                    if board[row, i] == 0 and i != col:
                        degree += 1
                    if board[i, col] == 0 and i != row:
                        degree += 1
                # Box
                box_row, box_col = 3 * (row // 3), 3 * (col // 3)
                for i in range(box_row, box_row + 3):
                    for j in range(box_col, box_col + 3):
                        if board[i, j] == 0 and (i != row or j != col):
                            degree += 1

                if degree > max_degree:
                    max_degree = degree
                    best_cell = (row, col)

    return best_cell

def get_heuristic_name() -> str:
    return "degree_heuristic"

def get_heuristic_description() -> str:
    return "Degree heuristic - chooses cell affecting most other empty cells"
