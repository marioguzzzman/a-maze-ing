"""The MazeGenerator class.

This module knows nothing about config files, output files or terminals:
it takes plain Python values (size, entry, exit, seed, perfect) and
produces a maze structure plus a solution path. The separation should make it 
reusable.
"""

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
  def __init__(self, name, age):
    self.width = width
    self.height = height
    self.entry = entry
    self.exit = exit
    self.seed = seed
    self.perfect = perfect
    pass