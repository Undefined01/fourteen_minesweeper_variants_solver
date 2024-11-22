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
from fourteen_minesweeper_variant_solver.data import CellEncrypted

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.data import CellEncrypted
    from fourteen_minesweeper_variant_solver.solver import Solver


class EncryptedRule(Rule):
    """
    2E: Clues are encoded by letters. Each letter corresponds to a number, and each number corresponds to a letter.
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars

        encoding_variable_count = game.height
        # Each letter corresponds to a number
        encoding_vars = [
            model.NewIntVar(0, encoding_variable_count - 1, f"encoded_{i}") for i in range(encoding_variable_count)
        ]
        # Each number corresponds to a letter
        model.AddAllDifferent(encoding_vars)
        # model.Add(encoding_vars[2] < 4)

        # Clues indicate the number of mines
        for r in range(game.height):
            for c in range(game.width):
                cell = game.board[r][c]
                if isinstance(cell, CellEncrypted):
                    encoded_number = encoding_vars[cell.value]
                    neighbors = []
                    for i in range(max(0, r - 1), min(game.height, r + 2)):
                        for j in range(max(0, c - 1), min(game.width, c + 2)):
                            if (i, j) != (r, c):
                                neighbors.append(mine_vars[i][j])
                    model.Add(sum(neighbors) == encoded_number)

        # # The possibility of encoded number
        # for r in range(game.height):
        #     for c in range(game.width):
        #         cell = game.board[r][c]
        #         if isinstance(cell, CellEncrypted):
        #             encoded_number = encoding_vars[cell.value]
        #             model.Add(encoded_number >= 0)
        #             model.Add(encoded_number < encoding_variable_count)
        #             model.Add(mine_vars[r][c] == 1).OnlyEnforceIf(encoded_number == cell.value)
        #             model.Add(mine_vars[r][c] == 0).OnlyEnforceIf(encoded_number != cell.value)