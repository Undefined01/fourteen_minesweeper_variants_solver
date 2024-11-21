from fourteen_minesweeper_variant_solver.data import Cell
import typing

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver

def add_vanilla_rule(
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

    # Ensure the number of mines around each cell matches the number on the cell
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
                model.Add(sum(neighbors) == number_of_mines_around)
