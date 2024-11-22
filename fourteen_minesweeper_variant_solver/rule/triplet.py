from ortools.sat.python.cp_model import CpModel, IntVar, BoolVarT
from fourteen_minesweeper_variant_solver.rule import Rule
import typing

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver

class TripletRule(Rule):
    """
    2T: (1) Mines cannot form a triple in a row or column, (2) non-mines cannot form a triple in a row or column
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars

        for r in range(game.height):
            for c in range(game.width - 1):
                if c > 0:
                    model.Add(mine_vars[r][c-1] == False).OnlyEnforceIf(mine_vars[r][c], mine_vars[r][c + 1])
                    model.Add(mine_vars[r][c-1] == True).OnlyEnforceIf(mine_vars[r][c].Not(), mine_vars[r][c + 1].Not())
                if c < game.width - 3:
                    model.Add(mine_vars[r][c+2] == False).OnlyEnforceIf(mine_vars[r][c], mine_vars[r][c + 1])
                    model.Add(mine_vars[r][c+2] == True).OnlyEnforceIf(mine_vars[r][c].Not(), mine_vars[r][c + 1].Not())
        
        for c in range(game.width):
            for r in range(game.height - 1):
                if r > 0:
                    model.Add(mine_vars[r-1][c] == False).OnlyEnforceIf(mine_vars[r][c], mine_vars[r + 1][c])
                    model.Add(mine_vars[r-1][c] == True).OnlyEnforceIf(mine_vars[r][c].Not(), mine_vars[r + 1][c].Not())
                if r < game.height - 3:
                    model.Add(mine_vars[r+2][c] == False).OnlyEnforceIf(mine_vars[r][c], mine_vars[r + 1][c])
                    model.Add(mine_vars[r+2][c] == True).OnlyEnforceIf(mine_vars[r][c].Not(), mine_vars[r + 1][c].Not())
