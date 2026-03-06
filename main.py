"""
Main FunSearch script for Sudoku heuristics evolution
"""

import os
import sys
import json
import time
import shutil
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import numpy as np

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluation.evaluate import evaluate_all_heuristics, save_evaluation_log
from evaluation.scoring import rank_heuristics, get_top_heuristics
from funsearch_core.generator import FunSearchGenerator


class FunSearchSudoku:
    """
    Main class for FunSearch Sudoku evolution
    """
    
    def __init__(self, max_cycles: int = 100, candidates_per_cycle: int = 3):
        """
        Initialize FunSearch for Sudoku.
        
        Args:
            max_cycles: Maximum number of evolution cycles
            candidates_per_cycle: Number of new heuristics to generate per cycle
        """
        self.max_cycles = max_cycles
        self.candidates_per_cycle = candidates_per_cycle
        
        # Directory structure
        self.benchmark_dir = "benchmark"
        self.heuristics_dir = "heuristics"
        self.log_dir = "logs"
        self.graph_dir = "graphs"
        self.prompts_dir = "prompts"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Evolution history
        self.evolution_history = []
        
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for directory in [self.benchmark_dir, self.heuristics_dir, self.log_dir, self.graph_dir, self.prompts_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def run_evolution(self):
        """
        Run the complete FunSearch evolution process.
        """
        print("Starting FunSearch Sudoku Evolution")
        print(f"Max cycles: {self.max_cycles}")
        print(f"Candidates per cycle: {self.candidates_per_cycle}")
        print("=" * 50)
        
        # Initial evaluation
        print("Evaluating initial heuristics...")
        initial_results = self._evaluate_current_heuristics()
        
        if not initial_results:
            print("No initial heuristics found. Creating baseline heuristic...")
            self._create_baseline_heuristic()
            initial_results = self._evaluate_current_heuristics()
        
        # Evolution loop
        for cycle in range(1, self.max_cycles + 1):
            print(f"\n--- Cycle {cycle}/{self.max_cycles} ---")
            
            # Evaluate current heuristics
            current_results = self._evaluate_current_heuristics()
            
            # Rank heuristics
            rankings = rank_heuristics(current_results)
            
            # Save results
            self._save_cycle_results(cycle, current_results, rankings)
            
            # Generate new heuristics
            if cycle < self.max_cycles:  # Don't generate on last cycle
                self._generate_new_heuristics(rankings)
            
            # Update evolution history
            best_score = rankings[0]['overall'] if rankings else 0.0
            self.evolution_history.append({
                'cycle': cycle,
                'best_score': best_score,
                'num_heuristics': len(rankings),
                'avg_score': np.mean([r['overall'] for r in rankings]) if rankings else 0.0
            })
            
            # Generate graphs every 10 cycles
            if cycle % 10 == 0:
                self._generate_graphs()
            
            print(f"Best score: {best_score:.3f}")
            print(f"Number of heuristics: {len(rankings)}")
        
        # Final evaluation and graphs
        print("\nEvolution complete!")
        self._generate_final_report()
        self._generate_graphs()
        
    def _evaluate_current_heuristics(self) -> List[Dict[str, Any]]:
        """Evaluate all current heuristics."""
        return evaluate_all_heuristics(self.heuristics_dir, self.benchmark_dir)
    
    def _create_baseline_heuristic(self):
        """Create a simple baseline heuristic."""
        baseline_code = '''
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
'''
        
        baseline_file = os.path.join(self.heuristics_dir, "heuristic_0.py")
        with open(baseline_file, 'w') as f:
            f.write(baseline_code)
        
        print(f"Created baseline heuristic: {baseline_file}")
    
    def _generate_new_heuristics(self, rankings: List[Dict[str, Any]]):
        """Generate new heuristics using FunSearch."""
        # Get top heuristics for prompt
        top_heuristics = get_top_heuristics(rankings, top_n=3)
        
        # Load their code for prompt
        heuristic_codes = []
        for heuristic_file in top_heuristics:
            file_path = os.path.join(self.heuristics_dir, heuristic_file)
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                heuristic_codes.append(f"// {heuristic_file}\n{code}")
            except Exception as e:
                print(f"Error reading {heuristic_file}: {e}")
        
        # Create prompt
        prompt_template_file = os.path.join(self.prompts_dir, "llm_prompt.txt")
        try:
            with open(prompt_template_file, 'r') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            print("Warning: llm_prompt.txt not found, using default prompt")
            prompt_template = "Create a new Sudoku heuristic based on the best performing ones."
        
        prompt = prompt_template.format(best_heuristics="\n\n".join(heuristic_codes))
        
        # Generate new heuristics
        generator = FunSearchGenerator(None)  # We'll implement this properly
        new_heuristics = generator.generate_candidates(
            previous_solutions=heuristic_codes, 
            n=self.candidates_per_cycle
        )
        
        # Save new heuristics
        for i, heuristic_code in enumerate(new_heuristics):
            heuristic_file = f"heuristic_generated_{int(time.time())}_{i}.py"
            file_path = os.path.join(self.heuristics_dir, heuristic_file)
            
            with open(file_path, 'w') as f:
                f.write(heuristic_code)
            
            print(f"Generated new heuristic: {heuristic_file}")
    
    def _save_cycle_results(self, cycle: int, results: List[Dict[str, Any]], rankings: List[Dict[str, Any]]):
        """Save results for current cycle."""
        cycle_data = {
            'cycle': cycle,
            'timestamp': time.time(),
            'results': results,
            'rankings': rankings,
            'evolution_summary': self.evolution_history[-1] if self.evolution_history else None
        }
        
        log_file = os.path.join(self.log_dir, f"cycle_{cycle}.json")
        with open(log_file, 'w') as f:
            json.dump(cycle_data, f, indent=2)
    
    def _generate_graphs(self):
        """Generate evolution graphs."""
        if not self.evolution_history:
            return
        
        cycles = [h['cycle'] for h in self.evolution_history]
        best_scores = [h['best_score'] for h in self.evolution_history]
        avg_scores = [h['avg_score'] for h in self.evolution_history]
        num_heuristics = [h['num_heuristics'] for h in self.evolution_history]
        
        # Score evolution graph
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.plot(cycles, best_scores, 'b-', label='Best Score', linewidth=2)
        plt.plot(cycles, avg_scores, 'r--', label='Average Score', linewidth=1)
        plt.xlabel('Cycle')
        plt.ylabel('Score')
        plt.title('Score Evolution')
        plt.legend()
        plt.grid(True)
        
        # Number of heuristics
        plt.subplot(2, 2, 2)
        plt.plot(cycles, num_heuristics, 'g-', linewidth=2)
        plt.xlabel('Cycle')
        plt.ylabel('Number of Heuristics')
        plt.title('Heuristic Population')
        plt.grid(True)
        
        # Score distribution
        plt.subplot(2, 2, 3)
        if self.evolution_history:
            latest_cycle = max(cycles)
            latest_log_file = os.path.join(self.log_dir, f"cycle_{latest_cycle}.json")
            try:
                with open(latest_log_file, 'r') as f:
                    latest_data = json.load(f)
                
                scores = [r['overall'] for r in latest_data['rankings']]
                plt.hist(scores, bins=20, alpha=0.7, edgecolor='black')
                plt.xlabel('Score')
                plt.ylabel('Frequency')
                plt.title('Score Distribution (Latest Cycle)')
                plt.grid(True)
            except:
                pass
        
        # Progress rate
        plt.subplot(2, 2, 4)
        if len(best_scores) > 1:
            progress_rate = np.diff(best_scores)
            plt.plot(cycles[1:], progress_rate, 'm-', linewidth=1)
            plt.xlabel('Cycle')
            plt.ylabel('Score Improvement')
            plt.title('Evolution Rate')
            plt.grid(True)
        
        plt.tight_layout()
        graph_file = os.path.join(self.graph_dir, "evolution_summary.png")
        plt.savefig(graph_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Graphs saved to {graph_file}")
    
    def _generate_final_report(self):
        """Generate final evolution report."""
        if not self.evolution_history:
            return
        
        report = {
            'experiment_summary': {
                'total_cycles': len(self.evolution_history),
                'max_cycles': self.max_cycles,
                'candidates_per_cycle': self.candidates_per_cycle,
                'start_time': self.evolution_history[0]['cycle'] if self.evolution_history else None,
                'end_time': self.evolution_history[-1]['cycle'] if self.evolution_history else None
            },
            'evolution_history': self.evolution_history,
            'final_best_score': max(h['best_score'] for h in self.evolution_history),
            'improvement': (self.evolution_history[-1]['best_score'] - 
                          self.evolution_history[0]['best_score']) if len(self.evolution_history) > 1 else 0
        }
        
        report_file = os.path.join(self.log_dir, "final_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Final report saved to {report_file}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FunSearch Sudoku Evolution")
    parser.add_argument("--cycles", type=int, default=50, help="Number of evolution cycles")
    parser.add_argument("--candidates", type=int, default=3, help="Candidates per cycle")
    
    args = parser.parse_args()
    
    # Run FunSearch
    funsearch = FunSearchSudoku(max_cycles=args.cycles, candidates_per_cycle=args.candidates)
    funsearch.run_evolution()


if __name__ == "__main__":
    main()
