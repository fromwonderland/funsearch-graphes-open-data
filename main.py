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
from pathlib import Path


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
        self.benchmark_file = "sudoku_massive.csv"  # Use massive 1000 puzzles file
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
        for directory in [self.heuristics_dir, self.log_dir, self.graph_dir, self.prompts_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def run_evolution(self):
        """Run the FunSearch evolution process with enhanced logging."""
        print("🚀 DÉMARRAGE DE L'ÉVOLUTION FUNSEARCH")
        print(f"📊 Configuration: {self.max_cycles} cycles, {self.candidates_per_cycle} candidats/cycle")
        print("=" * 60)
        
        # Check if benchmark file exists
        if not os.path.exists(self.benchmark_file):
            print(f"❌ Erreur: Fichier benchmark {self.benchmark_file} introuvable!")
            print("Veuillez vous assurer que sudoku_50.csv est dans le répertoire actuel.")
            return
        
        # Create baseline heuristic
        print("🔧 CRÉATION DE L'HEURISTIQUE DE BASE...")
        self._create_baseline_heuristic()
        print("✅ Baseline MRV créée")
        
        for cycle in range(1, self.max_cycles + 1):
            print(f"\n🔄 CYCLE {cycle}/{self.max_cycles}")
            print("-" * 40)
            
            # Evaluate current heuristics
            print("📏 ÉVALUATION DES HEURISTIQUES ACTUELLES...")
            current_results = self._evaluate_current_heuristics()
            
            # Rank heuristics
            print("🏆 CLASSEMENT DES HEURISTIQUES...")
            rankings = rank_heuristics(current_results)
            
            # Save results
            print("💾 SAUVEGARDE DES RÉSULTATS...")
            self._save_cycle_results(cycle, current_results, rankings)
            
            # Generate new heuristics
            if cycle < self.max_cycles:
                print(f"🧪 GÉNÉRATION DE {self.candidates_per_cycle} NOUVELLE(S) HEURISTIQUE(S)...")
                self._generate_new_heuristics(rankings)
            
            # Update evolution history
            best_score = rankings[0]['enhanced_score'] if rankings else 0.0
            self.evolution_history.append({
                'cycle': cycle,
                'best_score': best_score,
                'num_heuristics': len(rankings),
                'avg_score': np.mean([r['enhanced_score'] for r in rankings]) if rankings else 0.0
            })
            
            # Generate graphs every 10 cycles
            if cycle % 10 == 0:
                print("📈 GÉNÉRATION DES GRAPHIQUES TOUS LES 10 CYCLES...")
                self._generate_graphs()
                self._generate_detailed_graphs()  # Graphiques supplémentaires
            
            print(f"✅ Cycle {cycle} terminé - Meilleur score: {best_score:.3f}")
            print(f"📈 Nombre total d'heuristiques: {len(rankings)}")
        
        print("\n🎯 ÉVALUATION FINALE ET GÉNÉRATION DES GRAPHIQUES...")
        self._generate_graphs()
        self._generate_final_report()
        print("🎉 ÉVOLUTION TERMINÉE !")
        print(f"📊 Rapport final sauvegardé dans {self.log_dir}/final_report.json")
        print(f"📈 Graphiques sauvegardés dans {self.graph_dir}/evolution_summary.png")
        
    def _evaluate_current_heuristics(self) -> List[Dict[str, Any]]:
        """Evaluate all current heuristics."""
        return evaluate_all_heuristics(self.heuristics_dir, self.benchmark_file)
    
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
        """Generate new heuristics using FunSearch with enhanced logging."""
        # Get top heuristics for prompt
        top_heuristics = get_top_heuristics(rankings, top_n=3)  # Top 3 par cycle
        
        print(f"📋 Analyse des {len(top_heuristics)} meilleures heuristiques...")
        
        # Load their code for prompt
        heuristic_codes = []
        for i, heuristic_file in enumerate(top_heuristics):
            file_path = os.path.join(self.heuristics_dir, heuristic_file)
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                heuristic_codes.append(code)
                print(f"  ✅ Heuristic {i+1}: {heuristic_file}")
            except Exception as e:
                print(f"  ❌ Erreur lecture {heuristic_file}: {e}")
        
        # Create generator
        prompt_template_file = os.path.join(self.prompts_dir, "llm_prompt_final.txt")
        print("🤖 Initialisation du générateur LLM...")
        generator = FunSearchGenerator(Path(prompt_template_file))
        
        # Generate new heuristics
        print(f"🧠 Génération de {self.candidates_per_cycle} nouvelle(s) heuristique(s) via LLM...")
        new_heuristics = generator.generate_candidates(
            previous_solutions=heuristic_codes, 
            n=self.candidates_per_cycle
        )
        
        # Save new heuristics
        current_cycle = len(self.evolution_history) + 1
        print(f"💾 Sauvegarde des heuristiques du cycle {current_cycle}...")
        
        for i, heuristic_code in enumerate(new_heuristics):
            try:
                heuristic_name = generator.save_heuristic_to_collection(
                    heuristic_code, current_cycle, i+1
                )
                print(f"  ✅ Heuristic générée: {heuristic_name}")
            except Exception as e:
                print(f"  ❌ Erreur sauvegarde heuristic {i+1}: {e}")
        
        print(f"🎉 Génération terminée: {len(new_heuristics)} heuristiques créées")
        
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
    
    def _generate_detailed_graphs(self):
        """Generate additional detailed graphs every 10 cycles."""
        if not self.evolution_history:
            return
        
        # Create detailed analysis graphs
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('FunSearch Evolution Analysis - Detailed Metrics', fontsize=16)
        
        cycles = [h['cycle'] for h in self.evolution_history]
        best_scores = [h['best_score'] for h in self.evolution_history]
        num_heuristics = [h['num_heuristics'] for h in self.evolution_history]
        avg_scores = [h['avg_score'] for h in self.evolution_history]
        
        # 1. Score Evolution with Trend
        axes[0, 0].plot(cycles, best_scores, 'b-o', linewidth=2, markersize=6, label='Best Score')
        axes[0, 0].plot(cycles, avg_scores, 'r--', alpha=0.7, label='Average Score')
        if len(cycles) > 5:
            # Trend line
            z = np.polyfit(cycles, best_scores, 1)
            p = np.poly1d(z)
            axes[0, 0].plot(cycles, p(cycles), 'g:', alpha=0.5, label='Trend')
        axes[0, 0].set_xlabel('Cycle')
        axes[0, 0].set_ylabel('Enhanced Score')
        axes[0, 0].set_title('Score Evolution with Trend')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Heuristic Population Growth
        axes[0, 1].plot(cycles, num_heuristics, 'g-o', linewidth=2, markersize=6)
        axes[0, 1].fill_between(cycles, 0, num_heuristics, alpha=0.3)
        axes[0, 1].set_xlabel('Cycle')
        axes[0, 1].set_ylabel('Number of Heuristics')
        axes[0, 1].set_title('Heuristic Population Growth')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Score Variance
        if len(cycles) > 1:
            variance_data = []
            for i, cycle_data in enumerate(self.evolution_history):
                # Get variance from cycle data if available
                variance_data.append(0.1)  # Placeholder - would need actual variance calculation
            
            axes[1, 0].plot(cycles, variance_data, 'm-o', linewidth=2, markersize=6)
            axes[1, 0].set_xlabel('Cycle')
            axes[1, 0].set_ylabel('Score Variance')
            axes[1, 0].set_title('Score Variance Over Time')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Improvement Rate
        if len(best_scores) > 1:
            improvements = [best_scores[i] - best_scores[i-1] for i in range(1, len(best_scores))]
            axes[1, 1].bar(cycles[1:], improvements, alpha=0.7, color='orange')
            axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.7)
            axes[1, 1].set_xlabel('Cycle')
            axes[1, 1].set_ylabel('Score Improvement')
            axes[1, 1].set_title('Per-Cycle Improvement')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        detailed_graph_file = os.path.join(self.graph_dir, f'detailed_analysis_cycle_{cycles[-1]}.png')
        plt.savefig(detailed_graph_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Graphiques détaillés sauvegardés: {detailed_graph_file}")

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
    parser.add_argument("--cycles", type=int, default=5, help="Number of evolution cycles")
    parser.add_argument("--candidates", type=int, default=3, help="Candidates per cycle")
    
    args = parser.parse_args()
    
    # Run FunSearch
    funsearch = FunSearchSudoku(max_cycles=args.cycles, candidates_per_cycle=args.candidates)
    funsearch.run_evolution()


if __name__ == "__main__":
    main()
