"""The MazeGenerator class.

This module knows nothing about config files, output files or terminals:
it takes plain Python values (size, entry, exit, seed, perfect) and
produces a maze structure plus a solution path. The separation should
make it reusable.
"""
from mazegen.structure import Cell, Grid, Walls, create_grid, apply_42_pattern
import random
from collections import deque

DIRECTIONS = [
    Walls.NORTH,
    Walls.EAST,
    Walls.SOUTH,
    Walls.WEST
]

LETTERS = {
    Walls.NORTH: "N",
    Walls.EAST: "E",
    Walls.SOUTH: "S",
    Walls.WEST: "W",
}

# maze generation

"""
What goes in?
width/height/entry/exit
perfect and seed can be changed or are not default.
what goes out?
list[list[int]], each int the 4-bit wall encoding.

MazeGenerator(width, height, entry, exit, seed=None, perfect=False)
"""


class MazeGenerator:
    """Generates a maze (perfect or not) and finds its shortest path."""

    def __init__(
        self,
        width: int,
        height: int,
        entry_point: tuple[int, int],
        exit_point: tuple[int, int],
        seed: int | None = None,
        perfect: bool = False
    ):
        """Store the settings. The maze itself is built by generate_maze.

        Args:
            width: number of cells across.
            height: number of cells down.
            entry_point: (x, y) of the entry cell.
            exit_point: (x, y) of the exit cell.
            seed: makes the maze reproducible; None = different each time.
            perfect: True = exactly one path between any two cells.
                False = game board with loops and fewer dead ends.
        """
        self.width = width
        self.height = height
        self.entry_point = entry_point
        self.exit_point = exit_point
        self.seed = seed
        self.perfect = perfect

        self.rng = random.Random(seed)
        self.grid = create_grid(width, height)

    def generate_maze(self) -> Grid:
        """Build a new maze and return its Grid.

        Always starts with a perfect maze. If perfect is False, loops
        are added and dead ends are opened up afterwards.

        Raises:
            ValueError: if ENTRY / EXIT are invalid for this grid.
        """
        self.grid = create_grid(self.width, self.height)
        apply_42_pattern(self.grid)
        self.check_cell("ENTRY", self.entry_point)
        self.check_cell("EXIT", self.exit_point)
        if self.entry_point == self.exit_point:
            raise ValueError("ENTRY and EXIT must be different cells!")

        self.build_maze()
        if not self.perfect:
            self.add_loops()
            self.remove_dead_ends()
        return self.grid

    def check_cell(self, name: str, cell: tuple[int, int]) -> None:
        """Check a cell is inside the grid and not a 42 cell (Entry, Exit)."""
        x, y = cell
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise ValueError(f"{name} {cell} is outside the maze!")
        if self.grid.cells[y][x].cell_42:
            raise ValueError(f"{name} {cell} is in the 42 pattern!")

    def get_unvisited_neighbors(
        self, cell: Cell
    ) -> list[tuple[Walls, Cell]]:
        """Get the cell neighbors that are not visited yet."""
        result = []
        for direction in DIRECTIONS:
            neighbor = self.grid.get_neighbor(cell.position, direction)
            if neighbor is not None and not neighbor.visited:
                result.append((direction, neighbor))
        return result

    def build_maze(self) -> None:
        """Build a maze with a depth-first search.
        Start at the entry. Move to a random unvisited neighbor and
        open the wall between the two cells. When there is nowhere
        left to go, step back and try from the previous cell.
        The 42 cells are marked as visited first, so the digging
        never goes into them and they stay fully closed.
        """

        # Mark 42 cells as visited
        for row in self.grid.cells:
            for cell in row:
                if cell.cell_42:
                    cell.visited = True

        # Mark entry
        start_x, start_y = self.entry_point
        start_cell = self.grid.cells[start_y][start_x]
        start_cell.visited = True
        stack = [start_cell]  # path we walk until we reach a dead end

        while len(stack) > 0:
            current = stack[-1]
            # where you can go
            options = self.get_unvisited_neighbors(current)
            if len(options) == 0:
                # dead end. remove the last cell, step back.
                stack.pop()
            else:
                # choose random option
                direction, neighbor = self.rng.choice(options)
                # open passage between current cell and its neighbor
                self.grid.open_passage(current.position, direction)
                neighbor.visited = True
                stack.append(neighbor)

    # PERFECT = False
    def block_is_open(self, left: int, top: int) -> bool:
        """Check if a 3x3 block has no walls inside it.
        left: x of the top-left cell of the block.
        top: y of the top-left cell of the block."""

        if left < 0 or top < 0:  # no negative coordinates
            return False
        if left + 2 >= self.width or top + 2 >= self.height:
            return False

        for y in range(top, top + 3):  # 3 cells
            for x in range(left, left + 3):
                cell = self.grid.cells[y][x]
                # Only look at the east and south wall of each cell, so
                # every wall inside the block is checked exactly once
                # wall on the east?
                if x < left + 2 and cell.walls & Walls.EAST:
                    return False
                # wall on the south?
                if y < top + 2 and cell.walls & Walls.SOUTH:
                    return False
        return True

    def makes_3x3(self, cell: Cell) -> bool:
        """Check if a cell is part of a 3x3 with no wall inside"""
        x, y = cell.position
        for top in range(y - 2, y + 1):
            for left in range(x - 2, x + 1):
                if self.block_is_open(left, top):
                    return True
        return False

    def try_open_wall(self, cell: Cell, direction: Walls) -> bool:
        """Try to open a wall unless it is outside, 42 cell, or would
        create a 3x3. Returns True if the wall is now open."""
        neighbor = self.grid.get_neighbor(cell.position, direction)
        if neighbor is None:
            return False
        if cell.cell_42 or neighbor.cell_42:
            return False
        if not cell.walls & direction:  # already open
            return False

        self.grid.open_passage(cell.position, direction)
        if self.makes_3x3(cell) or self.makes_3x3(neighbor):
            self.grid.close_passage(cell.position, direction)  # undo
            return False
        return True

    def add_loops(self) -> None:
        """Open extra walls so there is more than one way to go.
        A perfect maze has only one path between two cells. For a game
        board we want loops, so a player being chased always has
        another way to run. We open random closed walls (about one for
        every 20 cells, and at least 2), keeping the 3x3 rule.
        """
        loops_wanted = max(2, self.width * self.height // 20)
        loops_added = 0
        attempts = 0
        max_attempts = self.width * self.height * 20  # never loop forever

        while loops_added < loops_wanted and attempts < max_attempts:
            attempts += 1
            x = self.rng.randrange(self.width)
            y = self.rng.randrange(self.height)
            direction = self.rng.choice(DIRECTIONS)
            if self.try_open_wall(self.grid.cells[y][x], direction):
                loops_added += 1

    def count_open_walls(self, cell: Cell) -> int:
        """Count how many walls of a cell are open (0 to 4)."""
        count = 0
        for direction in DIRECTIONS:
            if not cell.walls & direction:
                count += 1
        return count

    def remove_dead_ends(self) -> None:
        """Open a wall in every dead end that can be opened.
        A dead end is a cell with only one open wall. For each of them
        we try to open one more wall, so the player can't get trapped.
        Some dead ends can't be fixed (for example a cell inside the
        "42" pattern with only one free neighbor), they stay.
        Opening a wall never creates a new dead end, so one pass over
        the grid is enough.
        """
        for row in self.grid.cells:
            for cell in row:
                if cell.cell_42 or self.count_open_walls(cell) != 1:
                    continue
                # try the directions in a random order
                directions = DIRECTIONS.copy()
                self.rng.shuffle(directions)
                for direction in directions:
                    if self.try_open_wall(cell, direction):
                        break

    # PERFECT = True
    def solve(self) -> str:
        """BFS to find the shortest path between entry and exit.

        The search spreads out from the entry one step at a time, so
        the first time it reaches the exit, it got there by a
        shortest path.
        """
        # cells we have to visit. start at entry
        queue = deque([self.entry_point])
        seen = {self.entry_point}  # cells we visited
        # cells we already reached, where we came from and which
        # move we used.
        came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        while len(queue) > 0:
            # Take the cell that has been waiting the longest (the front
            # of the line). New cells are added at the back, so cells
            # close to the entry always go first: all the cells 1 step
            # away, then all the cells 2 steps away, and so on.
            position = queue.popleft()

            # Reached the exit
            if position == self.exit_point:
                break

            # Get the Cell at this position. position is (x, y) but
            # cells is indexed [y][x], so y (position[1]) comes first.
            cell = self.grid.cells[position[1]][position[0]]

            # Try to move in each of the 4 directions.
            for direction in DIRECTIONS:
                if cell.walls & direction:
                    continue  # this wall is closed

                # The cell on the other side of the open wall
                neighbor = self.grid.get_neighbor(position, direction)

                # Skip it if it doesn't exist, or if we already reached it
                if neighbor is None or neighbor.position in seen:
                    continue

                # A new cell - mark it as reached, remember how we got
                # here, and put it at the back
                seen.add(neighbor.position)
                came_from[neighbor.position] = (
                    position, LETTERS[direction]
                )
                queue.append(neighbor.position)

        # If the exit was not reached
        if self.exit_point not in seen:
            raise ValueError("There is no path between ENTRY and EXIT")

        # walk back from the exit to the entry.
        # Each step, jump to the cell we came from, and write down the
        # move we used to get from there to here.
        letters = []
        position = self.exit_point
        while position != self.entry_point:
            position, letter = came_from[position]
            letters.append(letter)

        # We collected the moves from the exit backwards, so flip the
        # list to get them in the order entry -> exit.
        letters.reverse()
        return "".join(letters)

    # hexadecimal encoding - representing decimals in hexa
    def maze_to_hex(self) -> list[str]:
        """Return the maze as one string of hex digits per row."""
        result = []  # hexa representation in rows

        for row in self.grid.cells:
            hex_row = ""  # row of cells in hexa

            for cell in row:
                # format(value, format_specifier)
                hex_row += format(cell.walls, "x")  # numbers to hexa
            result.append(hex_row)

        return result
