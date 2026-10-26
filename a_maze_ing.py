#! /usr/bin/env python3
"""A-Maze-ing: entry point.

Usage: python3 a_maze_ing.py config.txt

Reads the configuration file, asks ``mazegen.MazeGenerator`` for a maze,
writes the hex output file, and runs the interactive terminal display.
"""

import sys
from typing import cast
from app.config import Config, parse_config
from app.errors import ConfigError
from mazegen.generator import MazeGenerator
from mazegen.display import build_visual_maze

# Notes on building:
#   1. config parsing   -> validated settings and errors
#   2. maze generation  -> mazegen/generator.py
#   3. output file      -> hex grid + entry + exit + path
#   4. display + menu


# config check
def config_check() -> Config:
    """Validate CLI args, then parse and validate the config file.

    Reads the config path from sys.argv. A missing/extra argument, a
    missing file, or an invalid config each print a clear message and
    exit(1) rather than raising out of this function.

    Returns:
        The parsed, validated config dict.
    """
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
        except ConfigError as e:
            print(f"Invalid config: {e}")
            sys.exit(1)
    return config_ready


def main() -> None:
    """Parse the config, generate a maze, and display it."""
    config_ready = config_check()
    generator = MazeGenerator(
        cast(int, config_ready["WIDTH"]),
        cast(int, config_ready["HEIGHT"]),
        cast("tuple[int, int]", config_ready["ENTRY"]),
        cast("tuple[int, int]", config_ready["EXIT"]),
        cast("int | None", config_ready.get("SEED")),
        cast(bool, config_ready["PERFECT"]),
    )
    try:
        build_visual_maze(generator, cast(str, config_ready["OUTPUT_FILE"]))
    except ValueError as e:
        print(f"Can't generate this maze: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Can't write the output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
