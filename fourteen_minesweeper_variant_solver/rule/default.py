from fourteen_minesweeper_variant_solver.data import Cell
import typing

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver

def add_default_rule(
    solver: 'Solver',
) -> None:
    game = solver.game
    model = solver.model
    mine_vars = solver.mine_vars

    # Set mine variables of the known cells
    for r in range(game.height):
        for c in range(game.width):
            cell = game.board[r][c]
            if cell == Cell.MINE:
                model.Add(mine_vars[r][c] == True)
            elif cell != Cell.UNKNOWN:
                model.Add(mine_vars[r][c] == False)

    # Ensure the total number of mines
    if game.total_mines is not None:
        model.Add(sum(sum(row) for row in mine_vars) == game.total_mines)
