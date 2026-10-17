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
        """Create a Cell.

        Args:
            position: the cell's (x, y) position in the grid.
            walls: which sides are closed; defaults to all 4 closed.
            visited: whether a generation algorithm has visited this
                cell yet; defaults to False.
            cell_42: whether this cell is part of the "42" pattern;
                defaults to False.
        """
        self.position = position
        self.walls = walls
        self.visited = visited
        self.cell_42 = cell_42

    def open_wall(self, direction: Walls) -> None:
        """Open one of this cell's own walls.

        Args:
            direction: which wall to open (Walls.NORTH / EAST /
                SOUTH / WEST). Safe to call even if it's already open.
        """
        # ~direction = every wall except this one. & keeps only the
        # bits set in both self.walls and that complement, so this one
        # bit gets forced to 0 and every other bit is left untouched -
        # safe to call even if direction was already open.
        self.walls = self.walls & (~direction)


    def close_wall(self, direction: Walls) -> None:
        """Close one of the cell's walls."""
        self.walls = self.walls | direction



class Grid:
    """Owns space: creates the cells, knows who's next to whom."""

    def __init__(
        self,
        width: int,
        height: int,
        cells: list[list[Cell]] | None = None
    ):
        """Create a Grid.

        Args:
            width: number of cells across.
            height: number of cells down.
            cells: the 2D collection of Cells, indexed [y][x]; defaults
                to a fresh empty list when not given.
        """
        self.width = width
        self.height = height
        self.cells = cells if cells is not None else []

    def get_neighbor(
        self, position: tuple[int, int], direction: Walls
    ) -> Cell | None:
        """Return the neighboring Cell in a given direction.

        Args:
            position: the (x, y) position to look from.
            direction: which side to look at (Walls.NORTH / EAST /
                SOUTH / WEST).

        Returns:
            The Cell at that neighboring position, or None if that
            direction falls outside the grid's bounds.
        """
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

    def open_passage(
        self, position: tuple[int, int], direction: Walls
    ) -> None:
        """Open a passage between a cell and its neighbor in `direction`.

        Opens the wall on both sides of the shared boundary: `direction`
        on the cell at `position`, and the opposite direction on its
        neighbor, so the two stay coherent with each other.

        Args:
            position: the (x, y) position of the cell to open from.
            direction: which side to open (Walls.NORTH / EAST / SOUTH
                / WEST).

        Raises:
            ValueError: if `direction` points outside the grid's
                bounds (no neighbor exists there). A correctly
                written generator should never trigger this - it's a
                guard against a bug upstream, not a user-facing error.
        """
        neighbor = self.get_neighbor(position, direction)
        if neighbor is None:
            raise ValueError("Can't open a wall in that position")
        else:
            current_cell = self.cells[position[1]][position[0]]
            current_cell.open_wall(direction)
            if direction == Walls.NORTH:
                opposite_direction = Walls.SOUTH
            elif direction == Walls.WEST:
                opposite_direction = Walls.EAST
            elif direction == Walls.SOUTH:
                opposite_direction = Walls.NORTH
            else:
                opposite_direction = Walls.WEST
            neighbor.open_wall(opposite_direction)


    def close_passage(
        self, position: tuple[int, int], direction: Walls
    ) -> None:
        """Close a passage between a cell and its neighbor in `direction`.
        Closes the wall on both sides of
        the shared boundary, so the two cells stay coherent.
        """
        neighbor = self.get_neighbor(position, direction)
        if neighbor is None:
            raise ValueError("Can't close a wall in that position")
        current_cell = self.cells[position[1]][position[0]]
        current_cell.close_wall(direction)
        neighbor.close_wall(OPPOSITE[direction])


def create_grid(width: int, height: int) -> Grid:
    """Build a width x height Grid where every Cell starts fully walled.

    Args:
        width: number of cells across.
        height: number of cells down.

    Returns:
        A new Grid populated with one Cell per position.
    """
    cells = []
    for y in range(height):
        row = []
        for x in range(width):
            new_cell = Cell((x, y))
            row.append(new_cell)
        cells.append(row)
    return Grid(width, height, cells)


def create_42_pattern(grid: Grid) -> set[tuple[int, int]]:
    """Return the (row, col) positions that spell "42", centered on grid.

    Args:
        grid: the grid to center the pattern on. Only its width/height
            are read; its cells are not touched.

    Returns:
        A set of (row, col) positions - i.e. (y, x) - that should be
        marked as part of the "42" pattern.
    """
    pattern = [
        [1, 0, 0, 0, 1, 1, 1],  # 1 - closed, 0 - open
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1]
    ]

    pattern_height = len(pattern)
    pattern_width = len(pattern[0])

    # Leave a 1-cell margin on every side so the pattern never touches
    # the grid's border.
    min_width = pattern_width + 2
    min_height = pattern_height + 2
    if grid.width < min_width or grid.height < min_height:
        print(
            f"Warning: grid is {grid.width}x{grid.height}, too small for "
            f"the \"42\" pattern (needs at least {min_width}x{min_height})"
            " - skipping it."
        )
        return set()

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


def apply_42_pattern(grid: Grid) -> None:
    """Mark every "42"-pattern position's Cell with cell_42 = True.

    Args:
        grid: the grid to mark in place.
    """
    blocked_cells = create_42_pattern(grid)
    for row, col in blocked_cells:
        grid.cells[row][col].cell_42 = True
