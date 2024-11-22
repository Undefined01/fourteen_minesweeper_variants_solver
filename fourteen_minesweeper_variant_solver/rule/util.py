
def get_neighbors_of_cells(height: int, width: int) -> dict[tuple[int, int], list[tuple[int, int]]]:
    neighbors: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for r in range(height):
        for c in range(width):
            neighbors[(r, c)] = [
                (i, j)
                for i in range(max(0, r - 1), min(height, r + 2))
                for j in range(max(0, c - 1), min(width, c + 2))
                if (i, j) != (r, c)
            ]
    return neighbors


def get_diagonal_neighbors_of_cells(height: int, width: int) -> dict[tuple[int, int], list[tuple[int, int]]]:
    neighbors: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for r in range(height):
        for c in range(width):
            neighbors[(r, c)] = [
                (i, j)
                for i in range(max(0, r - 1), min(height, r + 2))
                for j in range(max(0, c - 1), min(width, c + 2))
                if (i, j) != (r, c) and abs(i - r) == abs(j - c)
            ]
    return neighbors