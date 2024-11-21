from ortools.sat.python.cp_model import CpModel, IntVar, BoolVarT
from fourteen_minesweeper_variant_solver.rule import Rule
import typing

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver

class HorizontalRule(Rule):
    """
    2H: Any mine must have a horizontally adjacent mine
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars

        for r in range(game.height):
            for c in range(game.width):
                conditions: list[BoolVarT] = [mine_vars[r][c].Not()]
                if c > 0:
                    conditions.append(mine_vars[r][c - 1])
                if c < game.width - 1:
                    conditions.append(mine_vars[r][c + 1])
                model.AddBoolOr(conditions)
                
