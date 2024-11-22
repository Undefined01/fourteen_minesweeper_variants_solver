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


class ModuloRule:
    """
    2M: Clues indicates the remainder of the number of mines in the surrounding 3x3 area when divided by 3
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
                    helper = [model.NewBoolVar(f"helper_{r}_{c}_{i}") for i in range(3)]
                    model.Add(sum(neighbors) == number_of_mines_around).OnlyEnforceIf(helper[0])
                    model.Add(sum(neighbors) == number_of_mines_around + 3).OnlyEnforceIf(helper[1])
                    model.Add(sum(neighbors) == number_of_mines_around + 6).OnlyEnforceIf(helper[2])
                    model.AddBoolOr(helper)
