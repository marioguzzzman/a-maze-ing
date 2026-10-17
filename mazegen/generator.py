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
    def __init__(
        self,
        width: int,
        height: int,
        entry_point: tuple[int, int],
        exit_point: tuple[int, int],
        seed: int | None = None,
        perfect: bool = False
    ):
        self.width = width
        self.height = height
        self.entry_point = entry_point
        self.exit_point = exit_point
        self.seed = seed
        self.perfect = perfect

        self.rng = random.Random(seed)
        self.grid = create_grid(width, height)

    def generate_maze(self) -> Grid:
        self.grid = create_grid(self.width, self.height)
        apply_42_pattern(self.grid)
        self.grid = self.grid
        self.build_maze()
        return self.grid

    def random_open_walls(self) -> None:
        """Roughly test the wall-opening mechanism with random picks.

        Placeholder to checkthat opening walls actually shows up correctly, 
        and that "42" cells work correctly stay sealed off. 
        For every cell, there's a 1 in 4 chance of trying to open one random 
        direction.
        """
        directions = [Walls.NORTH, Walls.EAST, Walls.SOUTH, Walls.WEST]
        for row in self.grid.cells:
            for cell in row:
                if cell.cell_42:
                    continue
                if random.random() < 1 / 3:
                    direction = random.choice(directions)
                    neighbor = self.grid.get_neighbor(
                        cell.position, direction
                    )
                    if neighbor is not None and not neighbor.cell_42:
                        self.grid.open_passage(cell.position, direction)


    def check_cell(self, name: str, cell: tuple[int, int]):
        """Check that a cell is inside the grid and not a 42 cell (Entry, Exit)"""
        x, y = cell
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise ValueError(f"{name} {cell} is outside the maze!")
        if self.grid.cells[y][x].cell_42:
            raise ValueError (f"{name} {cell} is in the 42 patters!")


    def get_unvisited_neighbors(self, cell: Cell):
        """Get the cell neighbors that are not visited yet"""
        result = []
        for direction in DIRECTIONS:
            neighbor = self.grid.get_neighbor(cell.position, direction)
            if neighbor is not None and not neighbor.visited:
                result.append((direction, neighbor))
        return result


    def build_maze(self):
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
        stack = [start_cell] # path we walk until we reach a dead end
        
        while len(stack) > 0:
            current = stack[-1]
            options = self.get_unvisited_neighbors(current) # where you can go
            if len(options) == 0:
                stack.pop() # dead end. remove the last cell, step back.
            else:
                direction, neighbor = self.rng.choice(options) # choose random option
                self.grid.open_passage(current.position, direction) # open passage between
                neighbor.visited = True
                stack.append(neighbor)


    def solve(self):
        """BFS (breadth-first search) algorithm to find the shortest path between entry and exit.
        The search spreads out from the entry one step at a time, so the
        first time it reaches the exit, it got there by a shortest path."""


        queue = deque([self.entry_point]) # cells we have to visit. start at entry
        seen = {self.entry_point} # cells we visited
        came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {} # cells we already reached,  where we came from and which move we used.

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
    def maze_to_hex(self):
        result = [] # hexa representation in rows

        for row in self.grid.cells:
            hex_row = "" # row of cells in hexa

            for cell in row:
                # format(value, format_specifier)
                hex_row += format(cell.walls, "x") # convert numbers to hexa
            result.append(hex_row)

        return result
