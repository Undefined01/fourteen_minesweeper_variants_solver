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


class GroupRule:
    """
    2G: Each continuous mine region is of size 4
    """
    def apply(self, solver: 'Solver') -> None:
        game = solver.game
        model = solver.model
        mine_vars = solver.mine_vars
        
        # https://qiita.com/semiexp/items/f38d015c55195186d267
        # For each cell, if it is a mine, either:
        # - Its rank is 0
        # - It has at least one neighbor that is mine and with a lower rank
        rank_range = max(game.width, game.height)
        rank_vars = [
            [model.NewIntVar(0, rank_range - 1, f"group_rank_{r}_{c}") for c in range(game.width)] for r in range(game.height)
        ]
        rank_is_zero_vars = [
            [model.NewBoolVar(f"group_rank_is_zero_{r}_{c}") for c in range(game.width)] for r in range(game.height)
        ]
        for r in range(game.height):
            for c in range(game.width):
                model.Add(rank_vars[r][c] == 0).OnlyEnforceIf(rank_is_zero_vars[r][c])
                model.Add(rank_vars[r][c] != 0).OnlyEnforceIf(rank_is_zero_vars[r][c].Not())

        neighbor_offsets = (
            (1, 0), (0, 1), (-1, 0), (0, -1)
        )
        
        for r in range(game.height):
            for c in range(game.width):
                # Its rank is 0
                is_core = {
                    'and': [rank_is_zero_vars[r][c] == True],
                    'precondition': [mine_vars[r][c]]
                }
                # It has a neighbor that is mine and with a lower rank
                neighbor_has_lower_rank = []
                for dr, dc in neighbor_offsets:
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < game.height and 0 <= nc < game.width:
                        neighbor_has_lower_rank.append(
                            {
                                'and': [
                                    rank_is_zero_vars[r][c] == False,
                                    mine_vars[nr][nc] == True,
                                    rank_vars[nr][nc] < rank_vars[r][c],
                                ],
                                'precondition': [mine_vars[r][c]]
                            }
                        )
                exprs = [is_core] + neighbor_has_lower_rank

                # Add the constraints: or(expr.precondition -> and(e for e in expr.and) for expr in exprs)
                labels = [model.NewBoolVar(str(uuid.uuid4())) for _ in exprs]
                for label, expr_only_if in zip(labels, exprs):
                    for expr in expr_only_if['and']:
                        assert isinstance(expr, BoundedLinearExpression)
                        model.Add(expr).OnlyEnforceIf(label, *expr_only_if['precondition'])
                model.AddBoolOr(*labels)

        # For each cell that is a mine:
        # - If its rank is 0, its group_id is its position
        # - If its rank is not 0, its group_id is the same as the group_id of the neighbor that is a mine.
        #   This also implies that all its neighbors that are mines have the same group_id.
        # For each cell that is not a mine, its group_id is group_id_of_safe_cells.
        group_id_of_safe_cells = game.width * game.height
        group_id_vars = [
            [model.NewIntVar(0, game.width * game.height, f"group_id_{r}_{c}") for c in range(game.width)] for r in range(game.height)
        ]

        self.group_id_vars = group_id_vars
        self.rank_vars = rank_vars
        self.rank_is_zero_vars = rank_is_zero_vars

        for r in range(game.height):
            for c in range(game.width):
                model.Add(group_id_vars[r][c] == r * game.width + c).OnlyEnforceIf(mine_vars[r][c], rank_is_zero_vars[r][c])
                model.Add(group_id_vars[r][c] == group_id_of_safe_cells).OnlyEnforceIf(mine_vars[r][c].Not())
                
                for dr, dc in neighbor_offsets:
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < game.height and 0 <= nc < game.width:
                        model.Add(group_id_vars[nr][nc] == group_id_vars[r][c]).OnlyEnforceIf(mine_vars[r][c], mine_vars[nr][nc])

        # For each group_id, there are exactly 4 mines
        for group_id in range(game.width * game.height):
            cell_is_group_id = [
                model.NewBoolVar(f"cell_{r}_{c}_is_group_id_{group_id}") for r in range(game.height) for c in range(game.width)
            ]
            for r in range(game.height):
                for c in range(game.width):
                    helper = model.NewBoolVar(uuid.uuid4().hex)
                    model.Add(group_id_vars[r][c] == group_id).OnlyEnforceIf(helper)
                    model.Add(cell_is_group_id[r * game.width + c] == True).OnlyEnforceIf(helper)
                    model.Add(group_id_vars[r][c] != group_id).OnlyEnforceIf(helper.Not())
                    model.Add(cell_is_group_id[r * game.width + c] == False).OnlyEnforceIf(helper.Not())
            model.AddLinearExpressionInDomain(LinearExpr.Sum(cell_is_group_id), Domain.FromValues([0, 4]))