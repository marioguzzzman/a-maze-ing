"""The MazeGenerator class.

This module knows nothing about config files, output files or terminals:
it takes plain Python values (size, entry, exit, seed, perfect) and
produces a maze structure plus a solution path. The separation should
make it reusable.
"""
from mazegen.structure import Grid, Walls, create_grid, apply_42_pattern
import random

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
        seed: int,
        perfect: bool = False
    ):
        self.width = width
        self.height = height
        self.entry_point = entry_point
        self.exit_point = exit_point
        self.seed = seed
        self.perfect = perfect

    def generate_maze(self) -> Grid:
        main_grid = create_grid(self.width, self.height)
        apply_42_pattern(main_grid)
        self.grid = main_grid
        self.random_open_walls()
        return main_grid

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
