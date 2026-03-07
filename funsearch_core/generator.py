"""
FunSearch Generator for Sudoku heuristics

Generates new Sudoku solving heuristics using LLM with fallback to offline methods.
"""

from __future__ import annotations
import os
import json
import urllib.request
import pathlib
import random
import time
import hashlib
import textwrap
import urllib.error
from typing import List, Optional


class FunSearchGenerator:
    def __init__(
        self,
        prompt_path: pathlib.Path,
        *,
        use_ollama: bool | None = None,
        ollama_base_url: str | None = None,
        ollama_model: str | None = None,
        ollama_timeout_s: float = 90.0,
    ):
        self.prompt_path = prompt_path
        self.prompt = prompt_path.read_text(encoding="utf-8")
        # Check priority order: final > opposition > ultra > mistral > minimal > forced > optimized > standard
        final_prompt = prompt_path.with_name("llm_prompt_final.txt")
        opposition_prompt = prompt_path.with_name("llm_prompt_opposition.txt")
        ultra_prompt = prompt_path.with_name("llm_prompt_ultra.txt")
        mistral_prompt = prompt_path.with_name("llm_prompt_mistral.txt")
        minimal_prompt = prompt_path.with_name("llm_prompt_minimal.txt")
        forced_prompt = prompt_path.with_name("llm_prompt_forced.txt")
        optimized_prompt = prompt_path.with_name("llm_prompt_optimized.txt")
        
        if final_prompt.exists():
            self.prompt = final_prompt.read_text(encoding="utf-8")
        elif opposition_prompt.exists():
            self.prompt = opposition_prompt.read_text(encoding="utf-8")
        elif ultra_prompt.exists():
            self.prompt = ultra_prompt.read_text(encoding="utf-8")
        elif mistral_prompt.exists():
            self.prompt = mistral_prompt.read_text(encoding="utf-8")
        elif minimal_prompt.exists():
            self.prompt = minimal_prompt.read_text(encoding="utf-8")
        elif forced_prompt.exists():
            self.prompt = forced_prompt.read_text(encoding="utf-8")
        elif optimized_prompt.exists():
            self.prompt = optimized_prompt.read_text(encoding="utf-8")
        else:
            self.prompt = prompt_path.read_text(encoding="utf-8")
        self.use_ollama = use_ollama if use_ollama is not None else (os.getenv("FUNSEARCH_USE_OLLAMA", "1") == "1")
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "mistral:7b")
        self.ollama_timeout_s = float(os.getenv("OLLAMA_TIMEOUT_S", str(ollama_timeout_s)))

    def generate_candidates(
        self, previous_solutions: Optional[List[str]] = None, n: int = 3
    ) -> List[str]:
        """Return Python code strings. Uses Ollama if available; falls back to offline stubs."""
        if self.use_ollama:
            try:
                return self._generate_with_ollama(previous_solutions=previous_solutions, n=n)
            except Exception:
                # Keep demo resilient: if Ollama is down/unreachable, still run.
                pass
        return self._generate_offline(previous_solutions=previous_solutions, n=n)

    def _generate_with_ollama(
        self, previous_solutions: Optional[List[str]] = None, n: int = 3
    ) -> List[str]:
        """
        Call Ollama local API to generate code.

        Requires an Ollama service running at OLLAMA_BASE_URL (default localhost:11434).
        """
        system = (
            "You are an expert Sudoku solver and algorithm designer. "
            "You generate ONLY valid Python code (no markdown fences). "
            "Return exactly one function definition get_next_cell(board) that returns (row, col) tuple. "
            "CRITICAL: Never return None when empty cells exist - this causes infinite loops in the solver."
        )
        reinject = ""
        # Désactiver reinject pour forcer la créativité avec Mistral
        # if previous_solutions:
        #     reinject = "\n\nPrevious best solution(s) (for improvement, do NOT copy blindly):\n" + "\n\n".join(
        #         previous_solutions[:2]
        #     )

        user_prompt = (
            self.prompt
            + "\n\nBoard format: board is 9x9 numpy array with 0 for empty cells."
            + "\nReturn (row, col) of next cell to fill, or None if no empty cells."
            + "\nCRITICAL SAFETY: Always return a valid (row, col) when empty cells exist. Never return None unless board is complete."
            + reinject
            + "\n\nNow output Python code only, defining get_next_cell(board) and helper functions."
        )

        outputs: List[str] = []
        for i in range(n):
            payload = {
                "model": self.ollama_model,
                "prompt": user_prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": 1.2 if i == 0 else 1.5,
                    "top_p": 0.9,
                    "num_predict": 512,
                },
            }
            url = self.ollama_base_url.rstrip("/") + "/api/generate"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.ollama_timeout_s) as resp:
                    raw = resp.read().decode("utf-8")
            except urllib.error.URLError as exc:
                raise RuntimeError(f"Ollama request failed: {exc}") from exc

            data = json.loads(raw)
            text = (data.get("response") or "").strip()
            outputs.append(self._sanitize_candidate_code(text))

        # Basic contract check: ensure we have a def get_next_cell and proper imports.
        validated = [code for code in outputs if self._looks_valid(code)]
        if len(validated) < n:
            # Fill rest with offline fallbacks for robustness.
            validated.extend(
                self._generate_offline(previous_solutions=previous_solutions, n=n - len(validated))
            )
        return validated[:n]

    @staticmethod
    def _sanitize_candidate_code(text: str) -> str:
        """
        Normalize common LLM responses into pure Python code.

        Handles:
        - ```python ... ``` fences
        - a leading 'python' line (seen in some UIs)
        """
        cleaned = text.strip()
        if cleaned.startswith("```"):
            # ```python\n...\n```
            parts = cleaned.split("```")
            if len(parts) >= 3:
                cleaned = parts[1]
                # drop optional language tag on first line
                cleaned_lines = cleaned.splitlines()
                if cleaned_lines and cleaned_lines[0].strip().lower() in {"python", "py"}:
                    cleaned = "\n".join(cleaned_lines[1:])
            else:
                cleaned = cleaned.replace("```", "")

        # Some models respond with a first line "python"
        lines = cleaned.splitlines()
        if lines and lines[0].strip().lower() in {"python", "py"}:
            cleaned = "\n".join(lines[1:])

        return cleaned.strip() + "\n"

    @staticmethod
    def _looks_valid(code: str) -> bool:
        """Heuristic: must define get_next_cell and have proper imports."""
        lowered = code.lower()
        return "def get_next_cell" in lowered and ("import numpy" in lowered or "from solver.utils" in lowered)

    def _generate_offline(
        self, previous_solutions: Optional[List[str]] = None, n: int = 3
    ) -> List[str]:
        """Offline deterministic candidates so the pipeline works without any LLM."""
        seeds = [
            """
import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    # Simple MRV heuristic - choose cell with fewest candidates
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
    return "mrv_simple"

def get_heuristic_description() -> str:
    return "Minimum Remaining Values - chooses cell with fewest possible candidates"
""",
            """
import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    # Degree heuristic - choose cell affecting most constrained cells
    max_degree = -1
    best_cell = None
    
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                # Count empty cells in same row, column, and box
                degree = 0
                # Row and column
                for i in range(9):
                    if board[row, i] == 0 and i != col:
                        degree += 1
                    if board[i, col] == 0 and i != row:
                        degree += 1
                # Box
                box_row, box_col = 3 * (row // 3), 3 * (col // 3)
                for i in range(box_row, box_row + 3):
                    for j in range(box_col, box_col + 3):
                        if board[i, j] == 0 and (i != row or j != col):
                            degree += 1
                
                if degree > max_degree:
                    max_degree = degree
                    best_cell = (row, col)
    
    return best_cell

def get_heuristic_name() -> str:
    return "degree_heuristic"

def get_heuristic_description() -> str:
    return "Degree heuristic - chooses cell affecting most other empty cells"
""",
            """
import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    # Hybrid MRV + Degree heuristic
    best_score = -1
    best_cell = None
    
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                candidates = get_candidates(board, row, col)
                mrv_score = 10 - len(candidates)  # Fewer candidates = higher score
                
                # Calculate degree
                degree = 0
                for i in range(9):
                    if board[row, i] == 0 and i != col:
                        degree += 1
                    if board[i, col] == 0 and i != row:
                        degree += 1
                
                box_row, box_col = 3 * (row // 3), 3 * (col // 3)
                for i in range(box_row, box_row + 3):
                    for j in range(box_col, box_col + 3):
                        if board[i, j] == 0 and (i != row or j != col):
                            degree += 1
                
                # Combined score (prioritize MRV, use degree as tiebreaker)
                combined_score = mrv_score * 10 + degree
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_cell = (row, col)
    
    return best_cell

def get_heuristic_name() -> str:
    return "hybrid_mrv_degree"

def get_heuristic_description() -> str:
    return "Hybrid MRV + Degree heuristic combining both strategies"
""",
        ]

        generated = []
        rnd = random.Random(0)
        for _ in range(n):
            template = rnd.choice(seeds)
            generated.append(textwrap.dedent(template).strip() + "\n")

        # Simple tweak: if we have previous solutions, create an improved variant.
        if previous_solutions:
            generated.append(
                textwrap.dedent(
                    """
import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

def get_next_cell(board: np.ndarray) -> Optional[Tuple[int, int]]:
    # Improved MRV with early termination and optimization
    min_candidates = 10
    best_cell = None
    
    # Pre-calculate all candidates for efficiency
    all_candidates = {}
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                candidates = get_candidates(board, row, col)
                all_candidates[(row, col)] = candidates
                if len(candidates) < min_candidates:
                    min_candidates = len(candidates)
                    best_cell = (row, col)
                    if min_candidates == 1:
                        return best_cell
    
    return best_cell

def get_heuristic_name() -> str:
    return "optimized_mrv"

def get_heuristic_description() -> str:
    return "Optimized MRV with early termination for single candidates"
                    """
                ).strip()
                + "\n"
            )

        return generated[:n]

    def save_heuristic_to_collection(self, code: str, cycle: int, candidate_id: int) -> str:
        """
        Save a new heuristic to the collection file instead of separate files.
        
        Args:
            code: The generated heuristic code
            cycle: Current cycle number
            candidate_id: Candidate identifier
            
        Returns:
            Function name of the saved heuristic
        """
        # Extract function name from code
        func_name = "unknown"
        for line in code.split('\n'):
            if 'def get_heuristic_name()' in line:
                # Find the return statement in the next few lines
                lines_after = code.split('\n')[code.split('\n').index(line):]
                for next_line in lines_after:
                    if 'return' in next_line and '"' in next_line:
                        func_name = next_line.split('"')[1]
                        break
                break
        
        # Generate unique function name
        unique_name = f"heuristic_cycle{cycle}_candidate{candidate_id}_{func_name}"
        
        # Create collection file if it doesn't exist
        collection_file = self.prompt_path.parent.parent / "heuristics" / "heuristic_collection.py"
        
        # Read existing collection
        if collection_file.exists():
            with open(collection_file, 'r', encoding='utf-8') as f:
                collection_content = f.read()
        else:
            collection_content = '''"""
Collection of generated Sudoku heuristics
"""

import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

'''
        
        # Add the new heuristic to collection
        new_heuristic_code = f'''
# Heuristic: {unique_name} (Cycle {cycle}, Candidate {candidate_id})
{code}

def get_next_cell_{unique_name}(board: np.ndarray) -> Optional[Tuple[int, int]]:
    """Wrapper for {unique_name}"""
    return get_next_cell(board)

'''
        
        collection_content += new_heuristic_code
        
        # Save collection
        with open(collection_file, 'w', encoding='utf-8') as f:
            f.write(collection_content)
        
        print(f"✅ Heuristic '{unique_name}' added to collection")
        return unique_name

