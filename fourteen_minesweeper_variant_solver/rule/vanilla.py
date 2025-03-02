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

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver


class VanillaRule:
    """
    2V: The number on the cell equals to the number of mines around it
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
                    for i in range(max(0, r - 1), min(game.height, r + 2)):
                        for j in range(max(0, c - 1), min(game.width, c + 2)):
                            if (i, j) != (r, c):
                                neighbors.append(mine_vars[i][j])
                    model.Add(sum(neighbors) == number_of_mines_around)
