"""
Evaluation module for Sudoku heuristics
"""

import time
import json
import numpy as np
from typing import Dict, List, Any, Tuple
from solver.utils import load_board_from_csv, is_valid_solution
from solver.sudoku_solver import SudokuSolver


def load_benchmark(file_path: str, max_puzzles: int = 1000) -> List[np.ndarray]:
    """
    Load Sudoku boards from a CSV file.
    
    Args:
        file_path: Path to CSV file
        max_puzzles: Maximum number of puzzles to load (for performance)
        
    Returns:
        List of Sudoku boards as numpy arrays
    """
    boards = []
    try:
        with open(file_path, 'r') as f:
            # Skip header if present
            header = f.readline().strip()
            if 'quizzes' in header.lower():
                pass  # Skip header line
            else:
                f.seek(0)  # Reset to start if no header
                
            count = 0
            for line in f:
                if count >= max_puzzles:
                    break
                    
                line = line.strip()
                if line:
                    # Handle format: quizzes,solutions or direct puzzle
                    try:
                        board = load_board_from_csv(line)
                        boards.append(board)
                        count += 1
                    except ValueError as e:
                        print(f"Skipping invalid puzzle line: {e}")
                        
    except FileNotFoundError:
        print(f"Warning: Benchmark file {file_path} not found")
        return []
    except Exception as e:
        print(f"Error loading benchmark: {e}")
        return []
    
    print(f"Loaded {len(boards)} puzzles from {file_path}")
    return boards


def evaluate_heuristic(heuristic_module, benchmark_boards: List[np.ndarray], 
                       max_time_per_board: float = 1.0) -> Dict[str, Any]:
    """
    Evaluate a single heuristic on the benchmark.
    
    Args:
        heuristic_module: Imported heuristic module
        benchmark_boards: List of Sudoku boards to test
        max_time_per_board: Maximum time allowed per board (seconds)
        
    Returns:
        Dictionary with evaluation results
    """
    results = {
        'heuristic_name': heuristic_module.get_heuristic_name(),
        'total_boards': len(benchmark_boards),
        'solved_boards': 0,
        'failed_boards': 0,
        'timeout_boards': 0,
        'total_time': 0.0,
        'average_time_per_board': 0.0,
        'board_results': []
    }
    
    solver = SudokuSolver(heuristic_module.get_next_cell)
    
    for i, board in enumerate(benchmark_boards):
        board_copy = board.copy()
        start_time = time.time()
        
        try:
            # Attempt to solve the board
            solved = solver.solve(board_copy, max_time=max_time_per_board)
            solving_time = time.time() - start_time
            
            if solved and is_valid_solution(board_copy):
                results['solved_boards'] += 1
                status = 'solved'
            else:
                results['failed_boards'] += 1
                status = 'failed'
                
        except TimeoutError:
            results['timeout_boards'] += 1
            solving_time = max_time_per_board
            status = 'timeout'
            
        except Exception as e:
            results['failed_boards'] += 1
            solving_time = time.time() - start_time
            status = f'error: {str(e)}'
        
        results['total_time'] += solving_time
        results['board_results'].append({
            'board_index': i,
            'status': status,
            'time': solving_time,
            'empty_cells': int(np.sum(board == 0))
        })
    
    if results['total_boards'] > 0:
        results['average_time_per_board'] = results['total_time'] / results['total_boards']
        results['success_rate'] = results['solved_boards'] / results['total_boards']
    else:
        results['success_rate'] = 0.0
    
    return results


def evaluate_all_heuristics(heuristic_dir: str, benchmark_file: str = None) -> List[Dict[str, Any]]:
    """
    Evaluate all heuristics in the directory against benchmark.
    
    Args:
        heuristic_dir: Directory containing heuristic files
        benchmark_file: Path to benchmark CSV file (default: sudoku.csv)
        
    Returns:
        List of evaluation results for each heuristic
    """
    import os
    import importlib.util
    
    # Use sudoku.csv by default, fallback to benchmark directory structure
    if benchmark_file is None:
        benchmark_file = "sudoku.csv"
        if not os.path.exists(benchmark_file):
            # Fallback to old structure
            benchmark_dir = "benchmark"
            benchmark_files = {
                'easy': os.path.join(benchmark_dir, 'sudoku_easy.csv'),
                'medium': os.path.join(benchmark_dir, 'sudoku_medium.csv'),
                'hard': os.path.join(benchmark_dir, 'sudoku_hard.csv')
            }
            benchmarks = {}
            for difficulty, file_path in benchmark_files.items():
                benchmarks[difficulty] = load_benchmark(file_path, max_puzzles=100)
        else:
            # Use main sudoku_50.csv file
            benchmarks = {'main': load_benchmark(benchmark_file, max_puzzles=50)}
    else:
        benchmarks = {'main': load_benchmark(benchmark_file, max_puzzles=50)}
    
    # Load heuristic modules
    heuristic_files = [f for f in os.listdir(heuristic_dir) 
                       if f.endswith('.py') and not f.startswith('__')]
    
    all_results = []
    
    for heuristic_file in heuristic_files:
        heuristic_path = os.path.join(heuristic_dir, heuristic_file)
        module_name = heuristic_file[:-3]  # Remove .py extension
        
        try:
            # Load heuristic module
            spec = importlib.util.spec_from_file_location(module_name, heuristic_path)
            heuristic_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(heuristic_module)
            
            # Evaluate against benchmark(s)
            for difficulty, boards in benchmarks.items():
                if boards:  # Only evaluate if benchmark exists
                    result = evaluate_heuristic(heuristic_module, boards)
                    result['difficulty'] = difficulty
                    result['heuristic_file'] = heuristic_file
                    result['benchmark_size'] = len(boards)
                    all_results.append(result)
                    
        except Exception as e:
            print(f"Error loading heuristic {heuristic_file}: {e}")
    
    return all_results


def save_evaluation_log(results: List[Dict[str, Any]], cycle: int, log_dir: str):
    """
    Save evaluation results to a JSON log file.
    
    Args:
        results: List of evaluation results
        cycle: Current FunSearch cycle number
        log_dir: Directory to save the log file
    """
    import os
    
    log_data = {
        'cycle': cycle,
        'timestamp': time.time(),
        'total_heuristics': len(set(r['heuristic_file'] for r in results)),
        'results': results
    }
    
    log_file = os.path.join(log_dir, f'cycle_{cycle}.json')
    
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"Evaluation log saved to {log_file}")
