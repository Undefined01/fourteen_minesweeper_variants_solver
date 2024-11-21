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


class SegmentRule:
    """
    2S: Each row contains one consecutive segment of mines
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars
        
        # https://qiita.com/semiexp/items/f38d015c55195186d267
        total_cell_count = game.width * game.height
        rank_vars = [
            [model.NewIntVar(0, total_cell_count - 1, f"segment_{r}_{c}") for c in range(game.width)] for r in range(game.height)
        ]
        rank_is_zero_vars = [
            [model.NewBoolVar(f"segment_zero_{r}_{c}") for c in range(game.width)] for r in range(game.height)
        ]
        for r in range(game.height):
            for c in range(game.width):
                model.Add(rank_vars[r][c] == 0).OnlyEnforceIf(rank_is_zero_vars[r][c])
                model.Add(rank_vars[r][c] != 0).OnlyEnforceIf(rank_is_zero_vars[r][c].Not())
        
        # There are exactly one connected region in each row
        for r in range(game.height):
            model.AddExactlyOne(rank_is_zero for rank_is_zero in rank_is_zero_vars[r])
            model.AddBoolOr(*mine_vars[r])

        neighbor_offsets = (
            (0, -1), (0, 1)
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