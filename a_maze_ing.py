#! /usr/bin/env python3

import sys
from config import parse_config
from mazegen.generator import MazeGenerator
from mazegen.display import build_visual_maze

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


# config check
def config_check() -> dict:
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
    return config_ready


def main() -> None:
    config_ready = config_check()
    generator = MazeGenerator(
        config_ready["WIDTH"],
        config_ready["HEIGHT"],
        config_ready["ENTRY"],
        config_ready["EXIT"],
        config_ready["SEED"],
        config_ready["PERFECT"],)
    build_visual_maze(generator)


if __name__ == "__main__":
    main()
