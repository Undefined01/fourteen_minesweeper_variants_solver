from ortools.sat.python.cp_model import (
    CpModel,
    IntVar,
    BoundedLinearExpression,
    LinearExpr,
    Domain,
    _NotBooleanVariable,
)
import uuid
from .util import get_neighbors_of_cells
import typing
from fourteen_minesweeper_variant_solver.rule import Rule

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver


class DeviationRule(Rule):
    """
    2D: Clues indicate the number of mines in the 3x3 area centered on the cell above.
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars

        for r in range(game.height):
            for c in range(game.width):
                cell = game.board[r][c]
                number_of_mines_around = cell.number_of_mines_around()
                if number_of_mines_around is not None:
                    neighbors = []
                    for i in range(max(0, r - 2), min(game.height, r + 1)):
                        for j in range(max(0, c - 1), min(game.width, c + 2)):
                            if (i, j) != (r, c):
                                neighbors.append(mine_vars[i][j])
                    model.Add(sum(neighbors) == number_of_mines_around)
