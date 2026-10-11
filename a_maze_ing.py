#! /usr/bin/env python3

import sys
from config import parse_config

"""A-Maze-ing: entry point.

Usage: python3 a_maze_ing.py config.txt

Reads the configuration file, asks ``mazegen.MazeGenerator`` for a maze,
writes the hex output file, and runs the interactive terminal display.
"""

# Notes on building:
#   1. config parsing   -> validated settings and errors
#   2. maze generation  -> mazegen/generator.py
#   3. output file      -> hex grid + entry + exit + path
#   4. display + menu   

#Error handling
"""
Your program must handle all errors gracefully: invalid configuration, file not found, bad
syntax, impossible maze parameters, etc. It must never crash unexpectedly, and must always
provide a clear error message to the user.

The "42" pattern may be omitted in case the maze size does not allow it (i.e. too small).
> Print an error message on the console in that case.

 Graceful errors: missing file, bad syntax, missing key, out-of-bounds entry/exit,
      entry == exit, impossible dimensions
"""

class MazeAppError(Exception):
    def __init__(self, message: str = "Unknown Maze error") -> None:
        super().__init__(message)

class ConfigError(MazeAppError):
    def __init__(self, message: str = "Unknown Config error") -> None:
        super().__init__(message)


#Menu
"""
- **A graphical display using the MiniLibX (MLX) library.**

=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit
Choice? (1-4): _
"""

if __name__ == "__main__":
    # Check arguments
    if len(sys.argv) == 1:
        print("No arguments provided!")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("Too many arguments provided!")
        sys.exit(1)
    # Read the file and process lines
    else:
        config_path = sys.argv[1]
        try:
            with open(config_path) as f:
                print(f"Preparing config {config_path}...")
                lines = f.readlines()
                config_ready = parse_config(lines)
        except FileNotFoundError as e:
            print(f"File {sys.argv[1]} not found!: {e}")
            sys.exit(1)
    print(config_ready)
    print("Config ready!")
    

