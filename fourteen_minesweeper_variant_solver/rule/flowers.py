from ortools.sat.python.cp_model import CpModel, IntVar, BoolVarT
from fourteen_minesweeper_variant_solver.rule import Rule
import typing

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver

class FlowersRule(Rule):
    """
    2F: There is exactly one mine in within four cells around a colored-cell mine
    In other words, each mine in a colored cell has exactly one mine in its 4-neighbors
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars

        neighbor_offsets = (
            (1, 0), (0, 1), (-1, 0), (0, -1)
        )

        for r in range(game.height):
            for c in range(game.width):
                if (r + c) % 2 == 1:
                    neighbors = [mine_vars[r + dr][c + dc] for dr, dc in neighbor_offsets if 0 <= r + dr < game.height and 0 <= c + dc < game.width]
                    model.Add(sum(neighbors) == 1).OnlyEnforceIf(mine_vars[r][c])
