"""
Collection of generated Sudoku heuristics
"""

import numpy as np
from typing import Tuple, Optional
from solver.utils import get_candidates

# Heuristic: heuristic_cycle1_candidate1_degree_heuristic (Cycle 1, Candidate 1)
def get_next_cell_heuristic_cycle1_candidate1_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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

def get_heuristic_name_heuristic_cycle1_candidate1_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle1_candidate1_degree_heuristic() -> str:
    return "Degree heuristic - chooses cell affecting most other empty cells"

# Heuristic: heuristic_cycle1_candidate2_degree_heuristic (Cycle 1, Candidate 2)
def get_next_cell_heuristic_cycle1_candidate2_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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

def get_heuristic_name_heuristic_cycle1_candidate2_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle1_candidate2_degree_heuristic() -> str:
    return "Degree heuristic - chooses cell affecting most other empty cells"

# Heuristic: heuristic_cycle1_candidate3_mrv_simple (Cycle 1, Candidate 3)
def get_next_cell_heuristic_cycle1_candidate3_mrv_simple(board: np.ndarray) -> Optional[Tuple[int, int]]:
    # MRV heuristic - choose cell with fewest candidates
    min_candidates = 10
    best_cell = None

    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                candidates = get_candidates(board, row, col)
                num_candidates = len(candidates)
                
                if num_candidates < min_candidates:
                    min_candidates = num_candidates
                    best_cell = (row, col)
                    
                    if num_candidates == 1:
                        return best_cell

    return best_cell

def get_heuristic_name_heuristic_cycle1_candidate3_mrv_simple() -> str:
    return "mrv_simple"

def get_heuristic_description_heuristic_cycle1_candidate3_mrv_simple() -> str:
    return "Minimum Remaining Values - chooses cell with fewest possible candidates"

# Heuristic: heuristic_cycle2_candidate1_degree_heuristic (Cycle 2, Candidate 1)
def get_next_cell_heuristic_cycle2_candidate1_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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

def get_heuristic_name_heuristic_cycle2_candidate1_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle2_candidate1_degree_heuristic() -> str:
    return "Degree heuristic - chooses cell affecting most other empty cells"

# Heuristic: heuristic_cycle2_candidate2_degree_heuristic (Cycle 2, Candidate 2)
def get_next_cell_heuristic_cycle2_candidate2_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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

def get_heuristic_name_heuristic_cycle2_candidate2_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle2_candidate2_degree_heuristic() -> str:
    return "Degree heuristic - chooses cell affecting most other empty cells"

# Heuristic: heuristic_cycle2_candidate3_mrv_simple (Cycle 2, Candidate 3)
def get_next_cell_heuristic_cycle2_candidate3_mrv_simple(board: np.ndarray) -> Optional[Tuple[int, int]]:
    # MRV heuristic - choose cell with fewest candidates
    min_candidates = 10
    best_cell = None

    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                candidates = get_candidates(board, row, col)
                num_candidates = len(candidates)
                
                if num_candidates < min_candidates:
                    min_candidates = num_candidates
                    best_cell = (row, col)
                    
                    if num_candidates == 1:
                        return best_cell

    return best_cell

def get_heuristic_name_heuristic_cycle2_candidate3_mrv_simple() -> str:
    return "mrv_simple"

def get_heuristic_description_heuristic_cycle2_candidate3_mrv_simple() -> str:
    return "Minimum Remaining Values - chooses cell with fewest possible candidates"

# Heuristic: heuristic_cycle1_candidate1_degree_heuristic (Cycle 1, Candidate 1)
def get_next_cell_heuristic_cycle1_candidate1_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle1_candidate1_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle1_candidate1_degree_heuristic() -> str:
    return "Generated heuristic - degree_heuristic"


# Heuristic: heuristic_cycle1_candidate2_degree_heuristic (Cycle 1, Candidate 2)
def get_next_cell_heuristic_cycle1_candidate2_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle1_candidate2_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle1_candidate2_degree_heuristic() -> str:
    return "Generated heuristic - degree_heuristic"


# Heuristic: heuristic_cycle1_candidate3_mrv_simple (Cycle 1, Candidate 3)
def get_next_cell_heuristic_cycle1_candidate3_mrv_simple(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle1_candidate3_mrv_simple() -> str:
    return "mrv_simple"

def get_heuristic_description_heuristic_cycle1_candidate3_mrv_simple() -> str:
    return "Generated heuristic - mrv_simple"


# Heuristic: heuristic_cycle2_candidate1_degree_heuristic (Cycle 2, Candidate 1)
def get_next_cell_heuristic_cycle2_candidate1_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle2_candidate1_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle2_candidate1_degree_heuristic() -> str:
    return "Generated heuristic - degree_heuristic"


# Heuristic: heuristic_cycle2_candidate2_degree_heuristic (Cycle 2, Candidate 2)
def get_next_cell_heuristic_cycle2_candidate2_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle2_candidate2_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle2_candidate2_degree_heuristic() -> str:
    return "Generated heuristic - degree_heuristic"


# Heuristic: heuristic_cycle2_candidate3_mrv_simple (Cycle 2, Candidate 3)
def get_next_cell_heuristic_cycle2_candidate3_mrv_simple(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle2_candidate3_mrv_simple() -> str:
    return "mrv_simple"

def get_heuristic_description_heuristic_cycle2_candidate3_mrv_simple() -> str:
    return "Generated heuristic - mrv_simple"


# Heuristic: heuristic_cycle3_candidate1_degree_heuristic (Cycle 3, Candidate 1)
def get_next_cell_heuristic_cycle3_candidate1_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle3_candidate1_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle3_candidate1_degree_heuristic() -> str:
    return "Generated heuristic - degree_heuristic"


# Heuristic: heuristic_cycle3_candidate2_degree_heuristic (Cycle 3, Candidate 2)
def get_next_cell_heuristic_cycle3_candidate2_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle3_candidate2_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle3_candidate2_degree_heuristic() -> str:
    return "Generated heuristic - degree_heuristic"


# Heuristic: heuristic_cycle3_candidate3_mrv_simple (Cycle 3, Candidate 3)
def get_next_cell_heuristic_cycle3_candidate3_mrv_simple(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle3_candidate3_mrv_simple() -> str:
    return "mrv_simple"

def get_heuristic_description_heuristic_cycle3_candidate3_mrv_simple() -> str:
    return "Generated heuristic - mrv_simple"


# Heuristic: heuristic_cycle4_candidate1_degree_heuristic (Cycle 4, Candidate 1)
def get_next_cell_heuristic_cycle4_candidate1_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle4_candidate1_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle4_candidate1_degree_heuristic() -> str:
    return "Generated heuristic - degree_heuristic"


# Heuristic: heuristic_cycle4_candidate2_degree_heuristic (Cycle 4, Candidate 2)
def get_next_cell_heuristic_cycle4_candidate2_degree_heuristic(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle4_candidate2_degree_heuristic() -> str:
    return "degree_heuristic"

def get_heuristic_description_heuristic_cycle4_candidate2_degree_heuristic() -> str:
    return "Generated heuristic - degree_heuristic"


# Heuristic: heuristic_cycle4_candidate3_mrv_simple (Cycle 4, Candidate 3)
def get_next_cell_heuristic_cycle4_candidate3_mrv_simple(board: np.ndarray) -> Optional[Tuple[int, int]]:
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


def get_heuristic_name_heuristic_cycle4_candidate3_mrv_simple() -> str:
    return "mrv_simple"

def get_heuristic_description_heuristic_cycle4_candidate3_mrv_simple() -> str:
    return "Generated heuristic - mrv_simple"

