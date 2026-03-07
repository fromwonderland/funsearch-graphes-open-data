"""
Utils for Sudoku solver - utility functions for board manipulation
"""

import numpy as np
from typing import List, Tuple, Set, Optional


def load_board_from_csv(csv_line: str) -> np.ndarray:
    """
    Load a Sudoku board from a CSV line string.
    Empty cells should be represented by 0.
    
    Args:
        csv_line: String with 81 comma-separated values (0-9) or 81-digit string
        
    Returns:
        9x9 numpy array representing the Sudoku board
    """
    line = csv_line.strip()
    
    # Handle format: "004300209..." (81 digits)
    if len(line) == 81 and ',' not in line:
        values = [int(x) for x in line]
    # Handle format: "quiz,solution" where quiz is 81 digits
    elif ',' in line:
        parts = line.split(',')
        if len(parts) >= 2 and len(parts[0]) == 81:
            # Format: "004300209005009001...,864371259325849761..."
            quiz_str = parts[0]
            values = [int(x) for x in quiz_str]
        else:
            # Format: "0,0,4,3,0,0,2,0,9..." (comma-separated)
            values = [int(x) for x in line.split(',') if x.strip()]
    else:
        raise ValueError(f"Invalid Sudoku line format: {line[:50]}...")
    
    if len(values) != 81:
        raise ValueError(f"Expected 81 values, got {len(values)}: {line[:50]}...")
    
    return np.array(values).reshape(9, 9)


def board_to_csv(board: np.ndarray) -> str:
    """
    Convert a Sudoku board to CSV string format.
    
    Args:
        board: 9x9 numpy array
        
    Returns:
        CSV string representation
    """
    return ','.join(str(board.flatten()[i]) for i in range(81))


def get_candidates(board: np.ndarray, row: int, col: int) -> Set[int]:
    """
    Get valid candidates for a cell.
    
    Args:
        board: 9x9 Sudoku board
        row: Row index (0-8)
        col: Column index (0-8)
        
    Returns:
        Set of valid candidate values (1-9)
    """
    if board[row, col] != 0:
        return set()
    
    candidates = set(range(1, 10))
    
    # Check row
    candidates -= set(board[row, :])
    
    # Check column
    candidates -= set(board[:, col])
    
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    candidates -= set(board[box_row:box_row+3, box_col:box_col+3].flatten())
    
    return candidates


def is_valid(board: np.ndarray, row: int, col: int, value: int) -> bool:
    """
    Check if placing a value in a cell is valid.
    
    Args:
        board: 9x9 Sudoku board
        row: Row index (0-8)
        col: Column index (0-8)
        value: Value to place (1-9)
        
    Returns:
        True if the placement is valid
    """
    # Check if cell is empty
    if board[row, col] != 0:
        return False
    
    # Check row
    if value in board[row, :]:
        return False
    
    # Check column
    if value in board[:, col]:
        return False
    
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    if value in board[box_row:box_row+3, box_col:box_col+3]:
        return False
    
    return True


def is_complete(board: np.ndarray) -> bool:
    """
    Check if the board is completely filled.
    
    Args:
        board: 9x9 Sudoku board
        
    Returns:
        True if board is complete (no empty cells)
    """
    return not np.any(board == 0)


def is_valid_solution(board: np.ndarray) -> bool:
    """
    Check if a completed board is a valid solution.
    
    Args:
        board: 9x9 Sudoku board
        
    Returns:
        True if the solution is valid
    """
    if not is_complete(board):
        return False
    
    # Check each row
    for row in range(9):
        if len(set(board[row, :])) != 9:
            return False
    
    # Check each column
    for col in range(9):
        if len(set(board[:, col])) != 9:
            return False
    
    # Check each 3x3 box
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box = board[box_row:box_row+3, box_col:box_col+3]
            if len(set(box.flatten())) != 9:
                return False
    
    return True


def display_board(board: np.ndarray) -> str:
    """
    Create a string representation of the Sudoku board.
    
    Args:
        board: 9x9 Sudoku board
        
    Returns:
        Formatted string representation
    """
    result = []
    for i in range(9):
        if i % 3 == 0 and i != 0:
            result.append("-" * 21)
        
        row_str = ""
        for j in range(9):
            if j % 3 == 0 and j != 0:
                row_str += "| "
            
            cell_val = board[i, j] if board[i, j] != 0 else "."
            row_str += f"{cell_val} "
        
        result.append(row_str.strip())
    
    return "\n".join(result)


def count_empty_cells(board: np.ndarray) -> int:
    """
    Count the number of empty cells in the board.
    
    Args:
        board: 9x9 Sudoku board
        
    Returns:
        Number of empty cells
    """
    return np.sum(board == 0)


def get_empty_cells(board: np.ndarray) -> List[Tuple[int, int]]:
    """
    Get list of all empty cells.
    
    Args:
        board: 9x9 Sudoku board
        
    Returns:
        List of (row, col) tuples for empty cells
    """
    return [(i, j) for i in range(9) for j in range(9) if board[i, j] == 0]
