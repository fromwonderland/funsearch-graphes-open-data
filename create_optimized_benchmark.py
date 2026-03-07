#!/usr/bin/env python3
"""
Create optimized Sudoku benchmark with 200 varied difficulty puzzles
"""

import random
from pathlib import Path

def create_optimized_benchmark():
    """Create a balanced benchmark with 200 puzzles of varying difficulty."""
    
    # Read the original file to get puzzles
    input_file = Path("sudoku.csv")
    output_file = Path("sudoku_200.csv")
    
    if not input_file.exists():
        print(f"Error: {input_file} not found!")
        return
    
    puzzles = []
    
    with open(input_file, 'r') as f:
        # Skip header
        header = f.readline().strip()
        
        # Read puzzles and sample strategically
        all_puzzles = []
        for line in f:
            line = line.strip()
            if ',' in line:
                puzzle = line.split(',')[0]  # Take quiz part
                if len(puzzle) == 81:
                    all_puzzles.append(puzzle)
        
        # Strategic sampling: ensure variety
        total_puzzles = len(all_puzzles)
        print(f"Found {total_puzzles} total puzzles")
        
        if total_puzzles >= 200:
            # Sample evenly from the dataset
            step = total_puzzles // 200
            for i in range(200):
                idx = min(i * step + random.randint(0, step-1), total_puzzles-1)
                puzzles.append(all_puzzles[idx])
        else:
            # If less than 200, take all and duplicate some if needed
            puzzles = all_puzzles.copy()
            while len(puzzles) < 200:
                puzzles.append(random.choice(all_puzzles))
    
    # Write the optimized benchmark
    with open(output_file, 'w') as f:
        f.write("quizzes,solutions\n")
        for puzzle in puzzles[:200]:
            # Add dummy solution (we don't need it for evaluation)
            dummy_solution = "0" * 81
            f.write(f"{puzzle},{dummy_solution}\n")
    
    print(f"Created {output_file} with {len(puzzles)} puzzles")
    
    # Analyze difficulty distribution
    empty_counts = [puzzle.count('0') for puzzle in puzzles]
    avg_empty = sum(empty_counts) / len(empty_counts)
    
    print(f"Average empty cells per puzzle: {avg_empty:.1f}")
    print(f"Empty cells range: {min(empty_counts)} - {max(empty_counts)}")
    
    # Difficulty estimation based on empty cells
    easy = sum(1 for count in empty_counts if count < 40)
    medium = sum(1 for count in empty_counts if 40 <= count < 50)
    hard = sum(1 for count in empty_counts if count >= 50)
    
    print(f"Difficulty distribution:")
    print(f"  Easy (<40 empty): {easy}")
    print(f"  Medium (40-49 empty): {medium}")
    print(f"  Hard (50+ empty): {hard}")

if __name__ == "__main__":
    create_optimized_benchmark()
