"""mazegen: a reusable maze generator.

Quickstart::

    from mazegen import MazeGenerator

    generator = MazeGenerator(
        width=20, height=15,
        entry_point=(0, 0), exit_point=(19, 14),
        seed=42, perfect=True,
    )
    grid = generator.generate_maze()
    solution = generator.solve()

Constructor parameters:
    width, height: size of the maze, in cells.
    entry_point, exit_point: (x, y) coordinates the maze is carved
        between.
    seed: optional int. Pass the same seed twice to get the same maze
        back - useful for reproducibility and testing. Omit it (or
        pass None) for a different maze each run.
    perfect: if True, the maze has exactly one path between any two
        cells (no loops). If False (the default), extra loops get
        carved in too, so there's more than one route between the
        entry and the exit.

Accessing the result:
    generate_maze() returns a Grid - the maze's actual structure. A
    Grid holds a 2D list of Cell objects at grid.cells, indexed
    [y][x]; each Cell has a .walls bitmask (see mazegen.structure.
    Walls) and a .position (x, y) tuple. The same Grid also stays
    available as generator.grid after generate_maze() runs.

    solve() returns the shortest path from entry_point to exit_point
    as a string of direction letters (N/E/S/W), e.g. "EESEESS...".
    Call it any time after generate_maze().

    maze_to_hex() returns the maze as a list of strings, one hex
    digit per cell per row (bit 0 = North, 1 = East, 2 = South,
    3 = West; a set bit means that wall is closed).

This module knows nothing about config files, output files or
terminals - generation and solving only. That separation is what
makes it reusable in another project.
"""
from mazegen.generator import MazeGenerator

__all__ = ["MazeGenerator"]
