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

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver


class ConnectedRule:
    """
    2C: (1) Each orthogonally connected mine region is a rectangle
        (2) All mine regions are diagonally connected
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars
        
        for r in range(game.height - 1):
            for c in range(game.width - 1):
                # The top right, bottom left, and bottom right cells are all mines -> the top left cell is a mine
                # Hence, each orthogonally connected mine region is a rectangle
                tl = model.NewBoolVar(uuid.uuid4().hex)
                model.Add(mine_vars[r + 1][c] + mine_vars[r][c + 1] + mine_vars[r + 1][c + 1] != 3).OnlyEnforceIf(tl)
                model.Add(mine_vars[r][c] == True).OnlyEnforceIf(tl.Not())

                tr = model.NewBoolVar(uuid.uuid4().hex)
                model.Add(mine_vars[r][c] + mine_vars[r + 1][c] + mine_vars[r + 1][c + 1] != 3).OnlyEnforceIf(tr)
                model.Add(mine_vars[r][c + 1] == True).OnlyEnforceIf(tr.Not())

                bl = model.NewBoolVar(uuid.uuid4().hex)
                model.Add(mine_vars[r][c] + mine_vars[r][c + 1] + mine_vars[r + 1][c + 1] != 3).OnlyEnforceIf(bl)
                model.Add(mine_vars[r + 1][c] == True).OnlyEnforceIf(bl.Not())

                br = model.NewBoolVar(uuid.uuid4().hex)
                model.Add(mine_vars[r][c] + mine_vars[r][c + 1] + mine_vars[r + 1][c] != 3).OnlyEnforceIf(br)
                model.Add(mine_vars[r + 1][c + 1] == True).OnlyEnforceIf(br.Not())

        # https://qiita.com/semiexp/items/f38d015c55195186d267
        total_cell_count = game.width * game.height
        rank_vars = [
            [model.NewIntVar(0, total_cell_count - 1, f"connect_{r}_{c}") for c in range(game.width)] for r in range(game.height)
        ]
        rank_is_zero_vars = [
            [model.NewBoolVar(f"connect_zero_{r}_{c}") for c in range(game.width)] for r in range(game.height)
        ]
        for r in range(game.height):
            for c in range(game.width):
                model.Add(rank_vars[r][c] == 0).OnlyEnforceIf(rank_is_zero_vars[r][c])
                model.Add(rank_vars[r][c] != 0).OnlyEnforceIf(rank_is_zero_vars[r][c].Not())
        
        # There are only one connected region
        model.AddExactlyOne(rank_is_zero for row in rank_is_zero_vars for rank_is_zero in row)

        neighbor_offsets = (
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            (1, 0), (0, 1), (-1, 0), (0, -1)
        )
        
        for r in range(game.height):
            for c in range(game.width):
                is_core = {
                    'and': [rank_is_zero_vars[r][c] == True],
                    'precondition': [mine_vars[r][c]]
                }
                neighbor_has_lower_rank = []
                for dr, dc in neighbor_offsets:
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < game.height and 0 <= nc < game.width:
                        neighbor_has_lower_rank.append(
                            {
                                'and': [
                                    rank_vars[nr][nc] < rank_vars[r][c],
                                    mine_vars[nr][nc] == True
                                ],
                                'precondition': [mine_vars[r][c]]
                            }
                        )
                exprs = [is_core] + neighbor_has_lower_rank

                labels = [model.NewBoolVar(str(uuid.uuid4())) for _ in exprs]
                for label, expr_only_if in zip(labels, exprs):
                    for expr in expr_only_if['and']:
                        assert isinstance(expr, BoundedLinearExpression)
                        model.Add(expr).OnlyEnforceIf(label, *expr_only_if['precondition'])
                model.AddBoolOr(*labels)

