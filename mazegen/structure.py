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
        cell: Cell 
    ):
        self.width = width
        self.height = height
        self.cell = cell
