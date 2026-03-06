"""
Template for Sudoku heuristics - to be generated/modified by LLM

This is a template that the LLM should use to create new heuristics.
Each heuristic should implement the 'get_next_cell' function.
"""

import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates, count_empty_cells


def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    """
    Heuristic to select the next cell to fill.
    
    This function should implement a strategy to choose which cell to fill next.
    Common strategies include:
    - Cell with fewest candidates (minimum remaining values)
    - Cell with most constraints
    - Sequential search
    - Random selection
    - Custom heuristics
    
    Args:
        board: 9x9 Sudoku board (0 = empty)
        
    Returns:
        Tuple (row, col) of the selected cell, or None if no empty cells
    """
    
    # TODO: Implement your heuristic here
    # Example: Simple sequential search
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                return (row, col)
    
    return None


def get_heuristic_name() -> str:
    """
    Return the name of this heuristic for logging purposes.
    
    Returns:
        String name of the heuristic
    """
    return "sequential_search"


def get_heuristic_description() -> str:
    """
    Return a description of how this heuristic works.
    
    Returns:
        String description of the heuristic strategy
    """
    return "Fills cells sequentially from top-left to bottom-right"
