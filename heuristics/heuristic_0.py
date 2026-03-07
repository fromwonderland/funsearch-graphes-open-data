
import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    """
    Simple heuristic: find cell with fewest candidates (MRV).
    """
    min_candidates = 10
    best_cell = None
    
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                candidates = get_candidates(board, row, col)
                if len(candidates) < min_candidates:
                    min_candidates = len(candidates)
                    best_cell = (row, col)
                    if min_candidates == 1:  # Can't get better
                        return best_cell
    
    return best_cell

def get_heuristic_name() -> str:
    return "mrv_baseline"

def get_heuristic_description() -> str:
    return "Minimum Remaining Values - chooses cell with fewest possible candidates"
