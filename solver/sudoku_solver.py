"""
Sudoku solver with pluggable heuristics
"""

import time
import numpy as np
from typing import Callable, Optional, Tuple
from solver.utils import get_candidates, is_valid, is_complete, is_valid_solution


class SudokuSolver:
    """
    Sudoku solver that uses a heuristic to select the next cell to fill.
    """
    
    def __init__(self, heuristic_func: Callable[[np.ndarray], Optional[Tuple[int, int]]]):
        """
        Initialize the solver with a heuristic function.
        
        Args:
            heuristic_func: Function that takes a board and returns (row, col) of next cell
        """
        self.heuristic_func = heuristic_func
        self.nodes_explored = 0
        self.backtracks = 0
    
    def solve(self, board: np.ndarray, max_time: float = 30.0) -> bool:
        """
        Solve the Sudoku puzzle using the heuristic.
        
        Args:
            board: 9x9 Sudoku board (0 = empty)
            max_time: Maximum time allowed for solving (seconds)
            
        Returns:
            True if solved successfully, False otherwise
            
        Raises:
            TimeoutError: If solving exceeds max_time
        """
        start_time = time.time()
        self.nodes_explored = 0
        self.backtracks = 0
        
        result = self._solve_recursive(board, start_time, max_time)
        
        if not result:
            raise TimeoutError(f"Solving exceeded {max_time} seconds")
        
        return result
    
    def _solve_recursive(self, board: np.ndarray, start_time: float, max_time: float) -> bool:
        """
        Recursive backtracking solver with heuristic cell selection.
        
        Args:
            board: Current board state
            start_time: Start time for timeout checking
            max_time: Maximum allowed time
            
        Returns:
            True if solution found, False otherwise
        """
        # Check timeout
        if time.time() - start_time > max_time:
            return False
        
        # Check if board is complete
        if is_complete(board):
            return is_valid_solution(board)
        
        # Use heuristic to select next cell
        next_cell = self.heuristic_func(board)
        
        if next_cell is None:
            return False  # No valid cell found
        
        row, col = next_cell
        self.nodes_explored += 1
        
        # Try all possible values for this cell
        candidates = get_candidates(board, row, col)
        
        if not candidates:
            self.backtracks += 1
            return False
        
        # Try candidates in order (could be optimized)
        for value in sorted(candidates):
            if is_valid(board, row, col, value):
                board[row, col] = value
                
                if self._solve_recursive(board, start_time, max_time):
                    return True
                
                # Backtrack
                board[row, col] = 0
                self.backtracks += 1
        
        return False
    
    def get_stats(self) -> dict:
        """
        Get solving statistics.
        
        Returns:
            Dictionary with solving statistics
        """
        return {
            'nodes_explored': self.nodes_explored,
            'backtracks': self.backtracks,
            'efficiency': 1.0 - (self.backtracks / max(1, self.nodes_explored))
        }


class AdvancedSudokuSolver(SudokuSolver):
    """
    Advanced Sudoku solver with additional optimizations.
    """
    
    def __init__(self, heuristic_func: Callable[[np.ndarray], Optional[Tuple[int, int]]]):
        super().__init__(heuristic_func)
        self.candidate_cache = {}
    
    def solve(self, board: np.ndarray, max_time: float = 30.0) -> bool:
        """
        Advanced solve with caching and optimizations.
        """
        start_time = time.time()
        self.candidate_cache.clear()
        
        return self._solve_recursive(board, start_time, max_time)
    
    def _solve_recursive(self, board: np.ndarray, start_time: float, max_time: float) -> bool:
        """
        Recursive solver with candidate caching.
        """
        # Check timeout
        if time.time() - start_time > max_time:
            return False
        
        # Check if board is complete
        if is_complete(board):
            return is_valid_solution(board)
        
        # Use heuristic to select next cell
        next_cell = self.heuristic_func(board)
        
        if next_cell is None:
            return False
        
        row, col = next_cell
        self.nodes_explored += 1
        
        # Get candidates (with caching)
        board_key = tuple(board.flatten())
        cache_key = (board_key, row, col)
        
        if cache_key in self.candidate_cache:
            candidates = self.candidate_cache[cache_key]
        else:
            candidates = get_candidates(board, row, col)
            self.candidate_cache[cache_key] = candidates
        
        if not candidates:
            self.backtracks += 1
            return False
        
        # Order candidates by constraint (fewest possibilities first)
        # This is already handled by the heuristic selection
        
        for value in sorted(candidates):
            if is_valid(board, row, col, value):
                board[row, col] = value
                
                if self._solve_recursive(board, start_time, max_time):
                    return True
                
                # Backtrack
                board[row, col] = 0
                self.backtracks += 1
        
        return False
