from fourteen_minesweeper_variant_solver import Game, Result, Fact, Cell, CellKind
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, CpSolver
from fourteen_minesweeper_variant_solver.rule import add_default_rule
from tqdm.auto import tqdm

class Solver:
    game: Game

    model: CpModel
    mine_vars: list[list[cp_model.IntVar]]

    def __init__(self, game: Game) -> None:
        self.game = game
        self.model = CpModel()
        self.mine_vars = [
            [self.model.NewBoolVar(f"mine_{r}_{c}") for c in range(game.width)] for r in range(game.height)
        ]
    
        add_default_rule(self)
        for rule in self.game.rules:
            rule.apply(self)

    def is_satisfiable(self, pr = False) -> bool:
        solver = CpSolver()
        status = solver.Solve(self.model)
        if pr:
            if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
                print('Satisfiable')
                print('\n'.join([str([solver.value(self.mine_vars[r][c]) for c in range(self.game.width)]) for r in range(self.game.height)]))
            else:
                print('Unsatisfiable')
        return str(status) == str(cp_model.FEASIBLE) or str(status) == str(cp_model.OPTIMAL)

def solve(
    game: Game
) -> Result:
    solved = False
    known_facts: list[Fact] = []
    # if not Solver(game).is_satisfiable():
    #     return Result(solved=solved, facts=known_facts)

    done = False
    progress = tqdm(total=sum(2 for r in range(game.height) for c in range(game.width) if game.board[r][c].kind == CellKind.UNKNOWN))
    solver = Solver(game)
    for r in range(game.height):
        for c in range(game.width):
            if game.board[r][c].kind != CellKind.UNKNOWN:
                continue
        
            for possibility in [Cell.HIDDEN, Cell.MINE]:
                progress.update()
                solver.model.ClearAssumptions()
                if possibility == Cell.MINE:
                    solver.model.AddAssumption(solver.mine_vars[r][c])
                else:
                    solver.model.AddAssumption(solver.mine_vars[r][c].Not())
                if not solver.is_satisfiable(r == 0 and c == 1):
                    game.board[r][c] = Cell.MINE if possibility == Cell.HIDDEN else Cell.HIDDEN
                    known_facts.append(Fact(row=r, column=c, is_mine=game.board[r][c] == Cell.MINE))
                    break
            else:
                game.board[r][c] = Cell.UNKNOWN
            
            if possibility == Cell.HIDDEN:
                progress.update()

    if game.total_mines is not None:
        if sum(cell == Cell.MINE for row in game.board for cell in row) == game.total_mines:
            solved = True

    return Result(solved=solved, facts=known_facts)
