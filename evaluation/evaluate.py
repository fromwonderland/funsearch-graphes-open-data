"""
Evaluation module for Sudoku heuristics
"""

import time
import json
import numpy as np
import importlib.util
from typing import Dict, List, Any, Tuple
from solver.utils import load_board_from_csv, is_valid_solution
from solver.sudoku_solver import SudokuSolver


def evaluate_collection_module(heuristic_module, benchmark_boards: List[np.ndarray], 
                              max_time_per_board: float = 0.1) -> Dict[str, Any]:
    """
    Evaluate the collection module by finding and evaluating the best heuristic in it.
    
    Args:
        heuristic_module: The imported heuristic_collection module
        benchmark_boards: List of Sudoku boards to test
        max_time_per_board: Maximum time allowed per board (seconds)
        
    Returns:
        Dictionary with evaluation results for the best heuristic
    """
    # Find all heuristic functions in the collection
    heuristic_functions = []
    
    # Get all attributes that start with "get_next_cell_"
    for attr_name in dir(heuristic_module):
        if attr_name.startswith('get_next_cell_') and callable(getattr(heuristic_module, attr_name)):
            # Get the corresponding name and description functions
            name_attr = attr_name.replace('get_next_cell_', 'get_heuristic_name_')
            desc_attr = attr_name.replace('get_next_cell_', 'get_heuristic_description_')
            
            heuristic_func = getattr(heuristic_module, attr_name)
            heuristic_name = getattr(heuristic_module, name_attr, lambda: "unknown")()
            heuristic_desc = getattr(heuristic_module, desc_attr, lambda: "No description")()
            
            heuristic_functions.append({
                'func': heuristic_func,
                'name': heuristic_name,
                'description': heuristic_desc,
                'attr_name': attr_name
            })
    
    if not heuristic_functions:
        return {
            'heuristic_name': 'collection_empty',
            'total_boards': len(benchmark_boards),
            'solved_boards': 0,
            'failed_boards': len(benchmark_boards),
            'timeout_boards': 0,
            'total_time': 0.0,
            'average_time_per_board': 0.0,
            'total_backtracks': 0,
            'total_nodes': 0,
            'enhanced_score': -10000.0,
            'error': 'No heuristic functions found in collection'
        }
    
    # Evaluate each heuristic and return the best one
    best_result = None
    best_score = float('-inf')
    
    for heuristic_info in heuristic_functions:
        try:
            # Create a simple module-like object for evaluation
            class SimpleModule:
                def __init__(self, func, name, desc):
                    self.get_next_cell = func
                    self.get_heuristic_name = lambda: name
                    self.get_heuristic_description = lambda: desc
            
            simple_module = SimpleModule(
                heuristic_info['func'], 
                heuristic_info['name'], 
                heuristic_info['description']
            )
            
            # Evaluate this heuristic
            result = evaluate_single_heuristic(simple_module, benchmark_boards, max_time_per_board)
            result['collection_function'] = heuristic_info['attr_name']
            
            # Check if this is the best so far
            if result['enhanced_score'] > best_score:
                best_score = result['enhanced_score']
                best_result = result
                
        except Exception as e:
            print(f"Error evaluating {heuristic_info['attr_name']}: {e}")
            continue
    
    return best_result or {'error': 'All heuristics failed to evaluate'}


def evaluate_single_heuristic(heuristic_module, benchmark_boards: List[np.ndarray], 
                              max_time_per_board: float = 0.1) -> Dict[str, Any]:
    """
    Evaluate a single heuristic on the benchmark with enhanced scoring.
    
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
        'total_backtracks': 0,
        'total_nodes': 0,
        'enhanced_score': 0.0
    }
    
    for board_idx, board in enumerate(benchmark_boards):
        solver = SudokuSolver(heuristic_module.get_next_cell)
        
        start_time = time.time()
        solved = solver.solve(board, max_time=max_time_per_board)
        elapsed = time.time() - start_time
        
        if solved is not None:
            results['solved_boards'] += 1
        elif elapsed >= max_time_per_board:
            results['timeout_boards'] += 1
        else:
            results['failed_boards'] += 1
        
        results['total_time'] += elapsed
        results['total_backtracks'] += solver.backtrack_count
        results['total_nodes'] += solver.nodes_explored
    
    results['average_time_per_board'] = results['total_time'] / len(benchmark_boards)
    results['enhanced_score'] = (
        1000 * (results['solved_boards'] / len(benchmark_boards)) 
        - 0.1 * results['total_backtracks'] 
        - 0.01 * results['total_nodes'] 
        - results['total_time'] * 1000
    )
    
    return results


def evaluate_heuristic(heuristic_module, benchmark_boards: List[np.ndarray], 
                       max_time_per_board: float = 0.1) -> Dict[str, Any]:
    """
    Evaluate a single heuristic on the benchmark with enhanced scoring.
    
    Args:
        heuristic_module: Imported heuristic module
        benchmark_boards: List of Sudoku boards to test
        max_time_per_board: Maximum time allowed per board (seconds)
        
    Returns:
        Dictionary with evaluation results
    """
    # Handle collection module differently
    if hasattr(heuristic_module, '__name__') and heuristic_module.__name__ == 'heuristic_collection':
        # For collection module, we need to evaluate each heuristic separately
        return evaluate_collection_module(heuristic_module, benchmark_boards, max_time_per_board)
    
    # For regular modules, use the single heuristic evaluation
    return evaluate_single_heuristic(heuristic_module, benchmark_boards, max_time_per_board)


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
            benchmarks = {'main': load_benchmark(benchmark_file, max_puzzles=100)}
    else:
        benchmarks = {'main': load_benchmark(benchmark_file, max_puzzles=100)}
    
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
