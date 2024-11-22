import typing

if typing.TYPE_CHECKING:
    from fourteen_minesweeper_variant_solver.solver import Solver

class Rule:
    def apply(self, solver: 'Solver'):
        raise NotImplementedError()