from enum import Enum
from fourteen_minesweeper_variant_solver.rule import Rule

class CellKind(Enum):
    """Enum representing the possible states of a cell in the board."""

    # The cell is unknown.
    UNKNOWN = -1
    # The cell is not a mine, but the number of mines around it is hidden.
    HIDDEN = -2
    # The cell is a mine.
    MINE = -3
    # The cell is not a mine, and reveals the number of mines around it.
    BASIC = 9
    # For Cross (2X) rule.
    # The cell is not a mine, and reveals the number of mines in the colored cells and non-colored cells.
    DUAL_VALUE = 10

class Cell:
    kind: CellKind

    UNKNOWN: 'Cell'
    HIDDEN: 'Cell'
    MINE: 'Cell'

    def __init__(self, kind: CellKind) -> None:
        self.kind = kind
    
    @staticmethod
    def basic(value: int) -> 'Cell':
        return CellBasic(value)

    # @staticmethod
    # def from_dual(value: tuple[int, int]) -> 'Cell':
    #     return Cell(CellKind.DUAL_VALUE, value)
    
    def number_of_mines_around(self) -> int | None:
        """Return the number of mines around the cell."""
        return None
    
    def __repr__(self) -> str:
        return f"{self.kind.name}"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cell):
            return False
        if self.kind != other.kind:
            return False
        else:
            return True

class CellBasic(Cell):
    value: int

    def __init__(self, value: int) -> None:
        super().__init__(CellKind.BASIC)
        self.value = value
    
    def number_of_mines_around(self) -> int | None:
        return self.value
    
    def __repr__(self) -> str:
        return f"{self.value}"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CellBasic):
            return False
        if self.value != other.value:
            return False
        else:
            return True


Cell.UNKNOWN = Cell(CellKind.UNKNOWN)
Cell.HIDDEN = Cell(CellKind.HIDDEN)
Cell.MINE = Cell(CellKind.MINE)

class Game:
    width: int
    height: int
    total_mines: int | None
    # The board of the game. Rows are indexed first, then columns.
    board: list[list[Cell]]
    rules: list[Rule]

    def __init__(self, board: list[list[Cell]], total_mines: int | None, rules: list[Rule]) -> None:
        self.board = board
        self.height = len(board)
        self.width = len(board[0])
        self.total_mines = total_mines
        self.rules = rules
        assert all(len(row) == self.width for row in board)


class Fact:
    row: int
    column: int
    is_mine: bool

    def __init__(self, row: int, column: int, is_mine: bool) -> None:
        self.row = row
        self.column = column
        self.is_mine = is_mine
    
    def __repr__(self) -> str:
        return f"r{self.row}c{self.column}={self.is_mine}"


class Result:
    solved: bool
    known_facts: list[Fact]

    def __init__(self, solved: bool, facts: list[Fact]) -> None:
        self.solved = solved
        self.known_facts = facts

    def __repr__(self) -> str:
        return f"{', '.join(str(x) for x in self.known_facts)}"