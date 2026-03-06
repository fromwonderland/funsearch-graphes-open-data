"""
FunSearch Generator - LLM-based heuristic generation for Sudoku
"""

from __future__ import annotations

import json
import os
import pathlib
import random
import textwrap
import urllib.error
import urllib.request
from typing import List, Optional, Dict, Any

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class FunSearchGenerator:
    """
    Generates new Sudoku heuristics using LLM (CodeT5) or templates
    """
    
    def __init__(
        self,
        prompt_path: Optional[pathlib.Path] = None,
        *,
        use_llm: bool = True,
        model_name: str = "Salesforce/codet5-small"
    ):
        """
        Initialize LLM generator.
        
        Args:
            prompt_path: Path to prompt file (optional)
            use_llm: Whether to use LLM or template-based generation
            model_name: HuggingFace model name for LLM
        """
        self.prompt_path = prompt_path
        self.use_llm = use_llm and TRANSFORMERS_AVAILABLE
        self.model_name = model_name
        
        if self.use_llm:
            print(f"Loading LLM: {self.model_name}")
            try:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.model.to(self.device)
                
                # Add padding token if needed
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    
                print(f"LLM loaded successfully on {self.device}")
            except Exception as e:
                print(f"Error loading model {self.model_name}: {e}")
                print("Falling back to template-based generation")
                self.use_llm = False
                self.model = None
                self.tokenizer = None
        else:
            print("Using template-based generation (no LLM)")
            self.model = None
            self.tokenizer = None
    
    def generate_candidates(
        self,
        previous_solutions: List[str],
        n: int = 3,
        temperature: float = 0.7,
        stop: str | None = None,
    ) -> List[str]:
        """
        Generate new heuristic candidates based on previous best solutions.
        
        Args:
            previous_solutions: List of best heuristic codes
            n: Number of new candidates to generate
            temperature: Sampling temperature for LLM
            stop: Stop sequence for generation
            
        Returns:
            List of new heuristic code strings
        """
        if self.model is None or self.tokenizer is None:
            return self._generate_template_candidates(previous_solutions, n)
        
        new_candidates = []
        
        for i in range(n):
            try:
                candidate = self._generate_single_candidate(previous_solutions, i)
                if candidate and self._validate_candidate(candidate):
                    new_candidates.append(candidate)
                else:
                    # Fallback to template if LLM fails
                    fallback = self._generate_template_candidates(previous_solutions, 1)
                    if fallback:
                        new_candidates.extend(fallback)
                        
            except Exception as e:
                print(f"Error generating candidate {i}: {e}")
                # Use template fallback
                fallback = self._generate_template_candidates(previous_solutions, 1)
                if fallback:
                    new_candidates.extend(fallback)
        
        return new_candidates[:n]
    
    def _generate_single_candidate(self, previous_solutions: List[str], candidate_id: int) -> str:
        """Generate a single candidate using LLM."""
        
        # Create prompt from best solutions
        best_solution = previous_solutions[0] if previous_solutions else ""
        
        prompt = f"""You are an expert Sudoku solver. Create a new heuristic function for solving Sudoku puzzles.

The current best heuristic is:
```python
{best_solution}
```

Create a NEW, IMPROVED heuristic that:
1. Uses a different strategy (e.g., degree heuristic, constraint propagation, pattern recognition)
2. Is efficient and well-commented
3. Maintains the same function signature
4. Includes get_heuristic_name() and get_heuristic_description() functions

Return only the complete Python code:

```python
import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    # Your new heuristic implementation here
    pass

def get_heuristic_name() -> str:
    return "your_heuristic_name"

def get_heuristic_description() -> str:
    return "Description of your heuristic strategy"
```"""

        # Tokenize input
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=1024,
            padding=True
        ).to(self.device)
        
        # Generate with appropriate parameters for code
        outputs = self.model.generate(
            **inputs,
            max_length=512,
            temperature=0.7,
            do_sample=True,
            top_p=0.95,
            num_return_sequences=1,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Decode and clean output
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract Python code from response
        candidate_code = self._extract_python_code(generated_text)
        
        return candidate_code
    
    def _extract_python_code(self, text: str) -> str:
        """Extract Python code from generated text."""
        # Look for code blocks
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            if end != -1:
                return text[start:end].strip()
        
        # Look for any code block
        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end != -1:
                code = text[start:end].strip()
                if not code.startswith("python"):
                    return code
        
        # Return the whole text if no code blocks found
        return text.strip()
    
    def _validate_candidate(self, candidate_code: str) -> bool:
        """Validate that the candidate code is syntactically correct and has required functions."""
        try:
            # Check syntax
            compile(candidate_code, '<string>', 'exec')
            
            # Check for required functions
            required_functions = ['get_next_cell', 'get_heuristic_name', 'get_heuristic_description']
            for func_name in required_functions:
                if f'def {func_name}(' not in candidate_code:
                    return False
            
            return True
            
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def _generate_template_candidates(self, previous_solutions: List[str], n: int) -> List[str]:
        """Generate candidates using predefined templates when LLM is not available."""
        
        templates = [
            # Degree heuristic
            '''import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    """
    Degree heuristic: choose cell that affects most constrained cells.
    """
    max_degree = -1
    best_cell = None
    
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                # Count empty cells in same row, column, and box
                degree = 0
                
                # Count empty in row
                degree += sum(1 for c in range(9) if board[row, c] == 0 and c != col)
                
                # Count empty in column  
                degree += sum(1 for r in range(9) if board[r, col] == 0 and r != row)
                
                # Count empty in box
                box_row, box_col = 3 * (row // 3), 3 * (col // 3)
                for br in range(box_row, box_row + 3):
                    for bc in range(box_col, box_col + 3):
                        if board[br, bc] == 0 and (br != row or bc != col):
                            degree += 1
                
                if degree > max_degree:
                    max_degree = degree
                    best_cell = (row, col)
    
    return best_cell

def get_heuristic_name() -> str:
    return "degree_heuristic"

def get_heuristic_description() -> str:
    return "Degree heuristic - chooses cell affecting most constrained cells"
''',
            
            # Hybrid MRV + Degree
            '''import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    """
    Hybrid MRV + Degree heuristic.
    """
    best_cell = None
    best_score = -1
    
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                candidates = get_candidates(board, row, col)
                mrv_score = len(candidates)
                
                # Calculate degree
                degree = 0
                for r in range(9):
                    if board[r, col] == 0 and r != row:
                        degree += 1
                for c in range(9):
                    if board[row, c] == 0 and c != col:
                        degree += 1
                
                # Combined score (lower is better for MRV, higher for degree)
                combined_score = (10 - mrv_score) + degree * 0.1
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_cell = (row, col)
    
    return best_cell

def get_heuristic_name() -> str:
    return "mrv_degree_hybrid"

def get_heuristic_description() -> str:
    return "Hybrid MRV + Degree - combines minimum remaining values with degree heuristic"
''',
            
            # Sequential with optimization
            '''import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    """
    Sequential search with single-candidate optimization.
    """
    # First, look for cells with only one candidate (forced moves)
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                candidates = get_candidates(board, row, col)
                if len(candidates) == 1:
                    return (row, col)
    
    # If no forced moves, use MRV
    min_candidates = 10
    best_cell = None
    
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                candidates = get_candidates(board, row, col)
                if len(candidates) < min_candidates:
                    min_candidates = len(candidates)
                    best_cell = (row, col)
                    if min_candidates == 1:
                        return best_cell
    
    return best_cell

def get_heuristic_name() -> str:
    return "forced_first_mrv"

def get_heuristic_description() -> str:
    return "Forced moves first, then MRV - prioritizes single-candidate cells"
'''
        ]
        
        # Return up to n templates
        return templates[:min(n, len(templates))]
