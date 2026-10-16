"""Maze data structures: Walls, Cell, and Grid.

A Grid owns space: it holds every Cell and knows how they're arranged
(bounds, who's next to whom). A Cell owns only its own local state:
its position, and which of its own walls are open or closed.
"""

from enum import IntFlag


class Walls(IntFlag):
    """Which sides of a cell have a wall, as a 4-bit flag."""

    # 0001 = 1st bit
    NORTH = 1
    # 0010 = 2nd bit
    EAST = 2
    # 0100 = 3rd bit
    SOUTH = 4
    # 1000 = 4th bit
    WEST = 8


class Cell:
    """Owns its own local state: which walls it has, position, flags."""

    def __init__(
        self,
        position: tuple[int, int],
        walls: Walls = Walls.NORTH | Walls.EAST | Walls.SOUTH | Walls.WEST,
        visited: bool = False,
        cell_42: bool = False
    ):
        self.position = position
        self.walls = walls
        self.visited = visited
        self.cell_42 = cell_42


class Grid:
    """Owns space: creates the cells, knows who's next to whom."""

    def __init__(
        self,
        width: int,
        height: int,
        cells: list[list[Cell]] | None = None
    ):
        self.width = width
        self.height = height
        self.cells = cells if cells is not None else []

    def get_neighbor(
        self, position: tuple[int, int], direction: Walls
    ) -> Cell | None:
        """Return the neighboring Cell in `direction`, or None at the edge."""
        x, y = position
        if direction == Walls.NORTH:
            neighbor_x, neighbor_y = x, y - 1
        elif direction == Walls.SOUTH:
            neighbor_x, neighbor_y = x, y + 1
        elif direction == Walls.EAST:
            neighbor_x, neighbor_y = x + 1, y
        else:
            neighbor_x, neighbor_y = x - 1, y

        if neighbor_x < 0 or neighbor_x >= self.width:
            return None
        if neighbor_y < 0 or neighbor_y >= self.height:
            return None

        return self.cells[neighbor_y][neighbor_x]


def create_grid(width: int, height: int) -> Grid:
    """Build a width x height Grid where every Cell starts fully walled."""
    cells = []
    for y in range(height):
        row = []
        for x in range(width):
            new_cell = Cell((x, y))
            row.append(new_cell)
        cells.append(row)
    return Grid(width, height, cells)


def create_42_pattern(grid: Grid) -> set[tuple[int, int]]:
    """Return the (row, col) positions that spell "42", centered on grid."""
    pattern = [
        [1, 0, 0, 0, 1, 1, 1],  # 1 - closed, 0 - open
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1]
    ]

    pattern_height = len(pattern)
    pattern_width = len(pattern[0])

    # Center the 42 pattern
    starting_row = (grid.height - pattern_height) // 2
    starting_col = (grid.width - pattern_width) // 2

    blocked_cells = set()

    for row in range(pattern_height):
        for col in range(pattern_width):
            if pattern[row][col] == 1:
                grid_row = starting_row + row
                grid_col = starting_col + col
                blocked_cells.add((grid_row, grid_col))

    # TODO: if the grid is too small for this pattern (width < 9 or
    # height < 7), skip it and print an error instead of returning
    # positions that may fall outside the grid.
    return blocked_cells


def apply_42_pattern(grid: Grid) -> None:
    """Mark every "42"-pattern position's Cell with cell_42 = True."""
    blocked_cells = create_42_pattern(grid)
    for row, col in blocked_cells:
        grid.cells[row][col].cell_42 = True
