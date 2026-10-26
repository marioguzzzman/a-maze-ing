*This project has been created as part of the 42 curriculum by maguzman, dbali*

# A-Maze-ing

## Description

A-Maze-ing generates a maze from a config file, saves it to a file, and shows it in a window. The maze has a "42" drawn in it with closed cells.

There are two modes:

- `PERFECT=True`: only one path between any two cells.
- `PERFECT=False`: the maze has loops, so there is more than one path.

In the window you can generate a new maze, show or hide the shortest path, and change the wall colors.
a
The code that makes the maze is in a separate package called `mazegen`, so it can be reused in other projects.

## Instructions

**Requirements:** Python 3.10 or higher. For the window you need Linux with Vulkan. These packages worked for us:

```
build-essential git pkg-config libvulkan-dev vulkan-tools mesa-vulkan-drivers
libxcb1-dev libxcb-keysyms1-dev libbsd-dev zlib1g-dev
```

**Makefile commands:**

```sh
make install      # creates .amazeing_env, installs dependencies, builds MLX
make run          # runs python3 a_maze_ing.py config.txt
make debug        # runs the program with pdb
make lint         # runs flake8 and mypy
make lint-strict  # runs flake8 and mypy --strict
make clean        # removes caches and build files
make build        # builds the mazegen-*.whl package
```

To use a different config file: `python3 a_maze_ing.py your_config.txt`

**Keys in the window:**

```
1  Generate a new maze
2  Show / hide the shortest path
3  Change the wall colors
4  Quit
```

## Config file

One `KEY=VALUE` per line. Lines starting with `#` are comments.

| Key           | Required | Description                                  | Example                |
| ------------- | -------- | -------------------------------------------- | ---------------------- |
| `WIDTH`       | yes      | Maze width in cells                          | `WIDTH=20`             |
| `HEIGHT`      | yes      | Maze height in cells                         | `HEIGHT=15`            |
| `ENTRY`       | yes      | Entry cell as `x,y`                          | `ENTRY=0,0`            |
| `EXIT`        | yes      | Exit cell as `x,y`                           | `EXIT=19,14`           |
| `OUTPUT_FILE` | yes      | File where the maze is saved                 | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | yes      | `True` for one path only, `False` for loops  | `PERFECT=True`         |
| `SEED`        | no       | Same seed gives the same maze                | `SEED=42`              |

See `config.txt` for an example.

## Reusable module

The `mazegen` package (`mazegen/generator.py` and `mazegen/structure.py`) does not depend on the config parsing, the output file, or the window.

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20, height=15,
    entry_point=(0, 0), exit_point=(19, 14),
    seed=42, perfect=True,
)
grid = generator.generate_maze()
solution = generator.solve()
```

- **Parameters:** `width` and `height` are the size. `entry_point` and `exit_point` are `(x, y)` tuples. `seed` is optional. `perfect` is `True` or `False`.
- **The maze:** `generate_maze()` returns a `Grid`. `grid.cells` is a 2D list of `Cell` objects, used as `[y][x]`. Each `Cell` has `.walls` (a bitmask) and `.position` (an `(x, y)` tuple). The grid is also saved in `generator.grid`.
- **The solution:** `solve()` returns the shortest path as a string of letters (`N`, `E`, `S`, `W`), for example `"EESEESS..."`.
- **Output format:** `maze_to_hex()` returns one hex digit per cell, one string per row. Bit 0 is North, bit 1 is East, bit 2 is South, bit 3 is West. A bit set to 1 means that wall is closed.

This is also documented in `mazegen/__init__.py`.

## Maze generation algorithm

### Algorithm used

We use the **recursive backtracker**, which is a randomized depth-first search. We use our own stack instead of recursion, because a big maze would pass Python's recursion limit.

Steps:

1. Start at one cell, mark it as visited, and put it on the stack.
2. Look at the neighbors of the current cell that are not visited yet.
3. If there is one, pick a random one, remove the wall between the two cells, mark the new cell as visited, and put it on the stack.
4. If there is none, take the top cell off the stack and go back to the previous one.
5. Stop when the stack is empty. At that point every cell has been visited.

The result has no loops, so it is already a perfect maze.

For `PERFECT=False`, we do a second step after this: we remove some extra walls to create loops. We check that this never makes a 3x3 open area.

### Why we chose it

- It is simple. It only needs a stack and a list of visited cells.
- It makes few dead ends, which is what the non-perfect mode needs.
- It takes time proportional to the number of cells, so it stays fast with a big `WIDTH` and `HEIGHT`.

### Seed

`SEED` works because Python's `random` gives the same numbers when you start it with the same seed. Each `MazeGenerator` has its own `random.Random(seed)`, so it does not change the global `random` module. Same seed, same maze.

### Solver

`solve()` uses **breadth-first search** (BFS). It is the same idea as the backtracker, but with a queue instead of a stack. A queue takes the oldest cell first, a stack takes the newest first. This is why BFS finds the shortest path.

Steps:

1. Put the entry cell in the queue and mark it as seen.
2. Take the first cell from the queue and look at its open walls.
3. For each neighbor not seen yet, mark it as seen, save which cell and direction it came from, and add it to the end of the queue.
4. Stop when the exit is taken from the queue.

Cells 1 step from the entry are checked before cells 2 steps away, and so on. So the first path that reaches the exit is a shortest one. To get the path, we go back from the exit to the entry using the saved directions, then reverse it.

## Resources

- MLX library: https://github.com/42school/mlx_CLXV
- MLX tutorial: https://aurelienbrabant.fr/blog/getting-started-with-the-minilibx
- Python bitwise operators: https://realpython.com/python-bitwise-operators/
- Lospec (color palettes): https://lospec.com/
- Python dictionary iteration: https://www.w3schools.com/PYTHON/python_dictionaries_loop.asp
- Maze algorithms, interactive: https://professor-l.github.io/mazes/
- CMU 15-112 maze generation notes (PDF): https://www.cs.cmu.edu/~112-s23/notes/student-tp-guides/Mazes.pdf

**How we used AI:** We used Claude as a tutor and to work through problems together. It asked us questions, questioned our ideas, and suggested options. It also explained Python topics we did not know (bitmasking, closures, `nonlocal`, type hints). We used it to learn the MLX library and to make the documentation for it easier to read.


## Team and project management

We both worked together debating the issues and trying to understand the elements needed for the maze. Diana focused more on developing the algorithm to build the maze and the solver as well as the logic for implementing multilple solutions. Mario focused more on getting the building block to make the elements of the maze functional to the algorithm. We were both looking into the color palettes ;)