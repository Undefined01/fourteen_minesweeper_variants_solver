from ortools.sat.python.cp_model import (
    CpModel,
    IntVar,
    BoundedLinearExpression,
    LinearExpr,
    _NotBooleanVariable,
)
import uuid
from .util import get_neighbors_of_cells
import typing
from fourteen_minesweeper_variant_solver.data import CellDual

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver


class CrossRule:
    """
    2X: Clues represent the number of mines in the colored cells and non-colored cells in neighboring 8 cells (unordered).
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars

        neighbor_cells = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        diagonal_cells = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for r in range(game.height):
            for c in range(game.width):
                cell = game.board[r][c]
                if isinstance(cell, CellDual):
                    a, b = cell.value
                    neighbor_mines = [mine_vars[r + dr][c + dc] for dr, dc in neighbor_cells if 0 <= r + dr < game.height and 0 <= c + dc < game.width]
                    diagonal_mines = [mine_vars[r + dr][c + dc] for dr, dc in diagonal_cells if 0 <= r + dr < game.height and 0 <= c + dc < game.width]

                    tmp_var = model.NewBoolVar(f"cross_{r}_{c}")
                    model.Add(sum(neighbor_mines) == a).OnlyEnforceIf(tmp_var)
                    model.Add(sum(diagonal_mines) == b).OnlyEnforceIf(tmp_var)

                    model.Add(sum(neighbor_mines) == b).OnlyEnforceIf(tmp_var.Not())
                    model.Add(sum(diagonal_mines) == a).OnlyEnforceIf(tmp_var.Not())

