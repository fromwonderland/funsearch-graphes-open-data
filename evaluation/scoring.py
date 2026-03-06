"""
Scoring module for evaluating heuristic performance
"""

import time
import ast
import numpy as np
from typing import Dict, List, Any


def calculate_complexity_score(heuristic_file: str) -> float:
    """
    Calculate code complexity score (lower is better).
    
    Args:
        heuristic_file: Path to heuristic file
        
    Returns:
        Complexity score (0-1, where 0 is simplest)
    """
    try:
        with open(heuristic_file, 'r') as f:
            code = f.read()
        
        # Parse the code to analyze complexity
        tree = ast.parse(code)
        
        # Simple complexity metrics
        num_lines = len(code.split('\n'))
        num_statements = len(list(ast.walk(tree)))
        num_functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        num_loops = len([node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))])
        num_conditions = len([node for node in ast.walk(tree) if isinstance(node, ast.If)])
        
        # Normalize to 0-1 scale (lower is better)
        complexity = (num_lines / 100 + num_statements / 50 + num_loops / 10 + num_conditions / 20) / 4
        return min(1.0, complexity)
        
    except Exception:
        return 0.5  # Default complexity if parsing fails


def calculate_performance_score(evaluation_result: Dict[str, Any]) -> float:
    """
    Calculate performance score based on solving capability.
    
    Args:
        evaluation_result: Result from evaluate_heuristic
        
    Returns:
        Performance score (0-1, where 1 is best)
    """
    success_rate = evaluation_result.get('success_rate', 0.0)
    avg_time = evaluation_result.get('average_time_per_board', 30.0)
    
    # Success rate is primary factor
    performance = success_rate
    
    # Time penalty (faster is better, up to 30 seconds max)
    time_penalty = min(avg_time / 30.0, 1.0)
    performance *= (1.0 - time_penalty * 0.3)  # Time is 30% of score
    
    return performance


def calculate_robustness_score(results: List[Dict[str, Any]]) -> float:
    """
    Calculate robustness score across different difficulties.
    
    Args:
        results: List of evaluation results for same heuristic across difficulties
        
    Returns:
        Robustness score (0-1, where 1 is most robust)
    """
    if not results:
        return 0.0
    
    # Group by difficulty
    difficulties = {}
    for result in results:
        diff = result.get('difficulty', 'unknown')
        difficulties[diff] = result
    
    # Calculate consistency across difficulties
    performances = [calculate_performance_score(result) for result in difficulties.values()]
    
    if not performances:
        return 0.0
    
    # Robustness is high if performance is consistent across difficulties
    mean_perf = np.mean(performances)
    std_perf = np.std(performances)
    
    # Lower standard deviation = higher robustness
    robustness = mean_perf * (1.0 - std_perf)
    return max(0.0, min(1.0, robustness))


def calculate_overall_score(evaluation_results: List[Dict[str, Any]], 
                          heuristic_file: str) -> Dict[str, float]:
    """
    Calculate overall score for a heuristic combining multiple factors.
    
    Args:
        evaluation_results: List of evaluation results for the heuristic
        heuristic_file: Path to heuristic file
        
    Returns:
        Dictionary with different score components
    """
    # Group results by heuristic file
    heuristic_results = [r for r in evaluation_results if r.get('heuristic_file') == heuristic_file]
    
    if not heuristic_results:
        return {'overall': 0.0, 'performance': 0.0, 'complexity': 0.5, 'robustness': 0.0}
    
    # Performance score (average across all difficulties)
    performance_scores = [calculate_performance_score(result) for result in heuristic_results]
    avg_performance = np.mean(performance_scores)
    
    # Complexity score (lower is better, so we invert)
    complexity = calculate_complexity_score(heuristic_file)
    complexity_score = 1.0 - complexity
    
    # Robustness score
    robustness = calculate_robustness_score(heuristic_results)
    
    # Overall weighted score
    weights = {'performance': 0.5, 'complexity': 0.2, 'robustness': 0.3}
    overall = (weights['performance'] * avg_performance + 
              weights['complexity'] * complexity_score + 
              weights['robustness'] * robustness)
    
    return {
        'overall': overall,
        'performance': avg_performance,
        'complexity': complexity_score,
        'robustness': robustness,
        'num_evaluations': len(heuristic_results)
    }


def rank_heuristics(evaluation_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank all heuristics by their overall score.
    
    Args:
        evaluation_results: List of all evaluation results
        
    Returns:
        List of heuristic rankings with scores
    """
    # Get unique heuristic files
    heuristic_files = list(set(r.get('heuristic_file') for r in evaluation_results))
    
    rankings = []
    for heuristic_file in heuristic_files:
        scores = calculate_overall_score(evaluation_results, heuristic_file)
        rankings.append({
            'heuristic_file': heuristic_file,
            **scores
        })
    
    # Sort by overall score (descending)
    rankings.sort(key=lambda x: x['overall'], reverse=True)
    
    # Add rank
    for i, ranking in enumerate(rankings):
        ranking['rank'] = i + 1
    
    return rankings


def get_top_heuristics(rankings: List[Dict[str, Any]], top_n: int = 3) -> List[str]:
    """
    Get the top N heuristics by rank.
    
    Args:
        rankings: List of heuristic rankings
        top_n: Number of top heuristics to return
        
    Returns:
        List of top heuristic file names
    """
    return [r['heuristic_file'] for r in rankings[:top_n]]
