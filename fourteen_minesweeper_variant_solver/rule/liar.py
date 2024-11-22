from ortools.sat.python.cp_model import CpModel, IntVar, BoolVarT
from fourteen_minesweeper_variant_solver.rule import Rule
from fourteen_minesweeper_variant_solver.data import Cell
import typing

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver

class LiarRule(Rule):
    """
    2L: A liar is either one greater or one less than the actual value. Each row and each column has exactly one liar.
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars

        liar_vars = [[model.NewBoolVar(f'liar_{r}_{c}') for c in range(game.width)] for r in range(game.height)]

        for r in range(game.height):
            model.AddExactlyOne(liar_vars[r])
        for c in range(game.width):
            model.AddExactlyOne([liar_vars[r][c] for r in range(game.height)])

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
                    model.Add(sum(neighbors) == number_of_mines_around).OnlyEnforceIf(liar_vars[r][c].Not())
                    helper = model.NewBoolVar(f"helper_{r}_{c}")
                    model.Add(sum(neighbors) == number_of_mines_around + 1).OnlyEnforceIf(liar_vars[r][c], helper)
                    model.Add(sum(neighbors) == number_of_mines_around - 1).OnlyEnforceIf(liar_vars[r][c], helper.Not())
                
                model.Add(liar_vars[r][c] == False).OnlyEnforceIf(mine_vars[r][c])
                if cell == Cell.HIDDEN:
                    model.Add(liar_vars[r][c] == False)
                
