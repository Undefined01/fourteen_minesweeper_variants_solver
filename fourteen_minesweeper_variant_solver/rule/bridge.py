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
from fourteen_minesweeper_variant_solver.rule import Rule

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver


class BridgeRule(Rule):
    """
    2B: Mines form 2 chains from left to right (3 chains on a board 7x7 or larger). A chain is a group of mines that connect the board's left and right side by horizontally or diagonally connected mines.
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars
        bridge_count = 2 if game.width < 7 else 3
        
        for c in range(game.width):
            model.Add(sum(mine_vars[r][c] for r in range(game.height)) == bridge_count)
        
        # each mine must be connected to the left or right side
        for r in range(game.height):
            for c in range(game.width):
                if c > 0:
                    model.AddBoolOr([mine_vars[nr][c - 1] for nr in range(r - 1, r + 2) if 0 <= nr < game.height]).OnlyEnforceIf(mine_vars[r][c])
                if c < game.width - 1:
                    model.AddBoolOr([mine_vars[nr][c + 1] for nr in range(r - 1, r + 2) if 0 <= nr < game.height]).OnlyEnforceIf(mine_vars[r][c])

        # two vertically adjacent mines must have at least 2 adjacent mines on each side
        for r in range(game.height - 1):
            for c in range(game.width):
                if c > 0:
                    model.Add(sum(mine_vars[nr][c - 1] for nr in range(r - 1, r + 3) if 0 <= nr < game.height) >= 2).OnlyEnforceIf(mine_vars[r][c], mine_vars[r + 1][c])
                if c < game.width - 1:
                    model.Add(sum(mine_vars[nr][c + 1] for nr in range(r - 1, r + 3) if 0 <= nr < game.height) >= 2).OnlyEnforceIf(mine_vars[r][c], mine_vars[r + 1][c])

        # two vertically adjacent mines must have at least 2 adjacent mines on each side
        #   a
        # X b
        # ? c
        # X d
        #   e
        for r in range(game.height - 2):
            for c in range(game.width):
                if c > 0:
                    model.Add(sum(mine_vars[nr][c - 1] for nr in range(r - 1, r + 4) if 0 <= nr < game.height) >= 2).OnlyEnforceIf(mine_vars[r][c], mine_vars[r + 2][c])
                if c < game.width - 1:
                    model.Add(sum(mine_vars[nr][c + 1] for nr in range(r - 1, r + 4) if 0 <= nr < game.height) >= 2).OnlyEnforceIf(mine_vars[r][c], mine_vars[r + 2][c])

        # three vertically adjacent mines must have at least 3 adjacent mines on each side
        for r in range(game.height - 2):
            for c in range(game.width):
                if c > 0:
                    model.Add(sum(mine_vars[nr][c - 1] for nr in range(r - 1, r + 4) if 0 <= nr < game.height) >= 3).OnlyEnforceIf(mine_vars[r][c], mine_vars[r + 1][c], mine_vars[r + 2][c])
                if c < game.width - 1:
                    model.Add(sum(mine_vars[nr][c + 1] for nr in range(r - 1, r + 4) if 0 <= nr < game.height) >= 3).OnlyEnforceIf(mine_vars[r][c], mine_vars[r + 1][c], mine_vars[r + 2][c])