"""
grid 
witdh and heigth
cells

exception: boundaries
"""

from enum import IntFlag

class Walls(IntFlag):
    # 0001 = 1st bit
    NORTH = 1
    # 0010 = 2nd bit
    EAST = 2
    # 0100 = 3rd bit
    SOUTH = 4
    # 1000 = 4th bit
    WEST = 8


class Cell:
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
    def __init__(
        self,
        width: int,
        height: int,
        cells: list[list[Cell]] = []
    ):
        self.width = width
        self.height = height
        self.cells = cells


def create_42_pattern(grid: Grid):
    pattern = [
        [1, 0, 0, 0, 1, 1, 1], # 1 - closed, 0 - open
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

    return blocked_cells


# blocked_cells_in_grid = create_42_pattern(grid)
# for row, col in blocked_cells_in_grid:
#     grid.cells[row][col].cell_42 = True






