*This project has been created as part of the 42 curriculum by seyehash, ngomez-v.*

# A-Maze-ing

## Description

A-Maze-ing is a Python program that builds a maze from a configuration file, solves it, writes the result to a text file, and draws it with MiniLibX.

The maze is a grid of `Cell` objects. Each cell stores its four walls as bits:

- `NORTH = 1`
- `EAST = 2`
- `SOUTH = 4`
- `WEST = 8`

A set bit means that wall is closed. The outer border stays closed. Neighbouring walls stay coherent: if one cell opens its east wall, the cell to the east opens its west wall. A centered "42" glyph is stamped from fully closed cells when the board is at least 9 cells wide and 7 cells tall. A smaller board omits the glyph and prints `Maze TOO small for printing the 42 pattern`.

The program then finds a shortest path with breadth-first search and writes the grid, the entry, the exit, and that path to the output file.

## Instructions

### Requirements

- Python 3.10 or later
- `flake8` and `mypy`, installed by `make install`
- The MiniLibX Python wheel (`mlx*.whl`) in this directory when `make install` runs

### Installation

```bash
make install
```

This installs `flake8`, `mypy`, and `build`, installs this project in editable mode, and installs the local `mlx*.whl`.

### Run

```bash
python3 a_maze_ing.py config.txt
```

or:

```bash
make run
```

The program takes exactly one argument, the path to the configuration file.

### Debug

```bash
make debug
```

This runs `python3 -m pdb a_maze_ing.py config.txt`.

### Lint

```bash
make lint
```

`lint` runs `flake8 .` and `mypy` with the flags required by the subject. `make lint-strict` runs `flake8 .` and `mypy . --strict`.

### Clean

```bash
make clean
```

This removes `__pycache__`, `.mypy_cache`, `.pytest_cache`, and `*.pyc` files.

## Configuration file

One `KEY=VALUE` pair per line. A line may also use `:`. Blank lines and lines that start with `#` are ignored. Duplicate keys and unknown keys are rejected.

Required keys:

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=12,11
OUTPUT_FILE=maze.txt
PERFECT=False
```

| Key | Meaning | Example |
| --- | --- | --- |
| `WIDTH` | Number of columns. Must be greater than 0. | `WIDTH=20` |
| `HEIGHT` | Number of rows. Must be greater than 0. | `HEIGHT=15` |
| `ENTRY` | Entry cell, `x,y`, inside the board and different from the exit. | `ENTRY=0,0` |
| `EXIT` | Exit cell, `x,y`. | `EXIT=12,11` |
| `OUTPUT_FILE` | Path of the text file to write. The directory must be writable. | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | `True` for one path and no loops. `False` for a looped board. | `PERFECT=False` |

Optional keys:

| Key | Meaning | Example |
| --- | --- | --- |
| `SEED` | Integer seed for the random generator. The same seed rebuilds the same maze. `0` is rejected. If the key is absent, the generator is seeded from the system time and each run differs. | `SEED=22` |
| `DISPLAY_MODE` | Colour of the "42" glyph in the MiniLibX window. Allowed values are `green` and `purple`. If the key is absent, the glyph is blue (`0xFF2266AA`). | `DISPLAY_MODE=green` |

`green` uses `0xFF8FF9AA`. `purple` uses `0xFF8B1FFF`.

Entry and exit must lie on the board, must differ, and must not fall on a "42" cell when the board is large enough to contain the glyph.

## Maze generation algorithm

### Selected algorithm

The perfect maze is built with **iterative randomized depth-first search**, also called the **recursive backtracker**. The walk is stored on an explicit stack in `mazegen/perfect.py` (`open_maze`).

### How it works

1. Every cell starts with all four walls closed.
2. On a board of at least 9 by 7, the "42" cells are marked visited before carving, so the search never opens them.
3. The search starts at a random unvisited cell, marks it visited, and pushes it.
4. While the stack is not empty, it looks at the unvisited neighbours of the current cell, picks one at random, removes the wall on both sides, and pushes that neighbour.
5. A cell with no unvisited neighbour is a dead end. The search pops back until it finds a cell that still has one.
6. When every non-pattern cell has been visited, the result is a spanning tree: exactly one path between any two open cells, and no loops.

`PERFECT=False` starts from that tree and then braids it in `mazegen/imperfect.py`:

1. `delete_deadends` opens one extra wall on each dead end, skipping the border, the "42" cells, and any opening that would clear a 2x2 room.
2. Up to 10% of the remaining south and west internal walls are removed, with the same 2x2 check, which creates several independent loops.
3. `open_42_gap` opens the corridor in the column between the 4 and the 2.

### Why this algorithm

Randomized depth-first search is a spanning tree, so `PERFECT=True` has one path and no loops without a separate check. An explicit stack keeps the same algorithm and avoids Python’s recursion limit on large boards. The long corridors it produces are a good base for the imperfect board: dead ends can be opened one by one, and a small extra set of walls can be removed while the 3x3 rule is still enforced. Wilson’s algorithm would be less biased, and Prim or Kruskal would make shorter dead ends, but both are more code for the same perfect-maze guarantee. Breadth-first search is used only to solve the finished maze, because every step has the same cost.

## Shortest-path solver

The path is found with breadth-first search in `mazegen/solver.py`. The search keeps a queue of cells still to visit, a visited set, and a parent map. `reconstruct_path` walks from the exit back to the entry and returns a string of `N`, `E`, `S`, and `W`. Cells on that path are marked `solution` so the window can draw them.

## Visual representation

MiniLibX draws the board. Each cell is a square of `SQUARE = 24` pixels. Closed walls are white lines. The "42" cells are filled with the `DISPLAY_MODE` colour. The shortest path is a band of 14 pixels through each solution cell, joined across open walls. The entry marker is `0xFFF54927` and the exit marker is `0xFFF5AD27`.

Keys, handled in `a_maze_ing.py`:

| Key | Key code | Action |
| --- | --- | --- |
| `p` | 112 | Show the shortest path |
| `h` | 104 | Hide the shortest path |
| `r` | 114 | Generate a new maze, rewrite the output file, and redraw |
| `c` | 99 | Recolour the walls with a random light colour |
| Escape | 65307 | Close the window |

## Output file

Each row is `WIDTH` hexadecimal digits, one per cell, and there are `HEIGHT` rows. The low four bits are North, East, South, and West, with a closed wall as 1. A blank line follows the grid, then the entry, the exit, and the path. Every line ends with a newline.

```text
b9395511391793939553
86c4112a86c56c6c4796
ab956a84693b915553c3
aac53aad5042ac153a96
c295446952d6c383e843
96c513f83afffaa83c3a
c3956afec057fc2ac542
bc6956fffafffbc4393a
81529553fafd50396aae
ac56c17afafffeac56c3
c53d381454539545157a
d10386c155546951693a
9686c3bc51153c3a96aa
83c53c479283c56c6bc6
ec554555444455555457

0,0
12,11
SSSSESWSESENEENESSWWSWWWSSEESSSEESEEEENENWWNEEEEE
```

## Reusable package

Generation and solving live in the `mazegen` package and do not import the display or `a_maze_ing.py`.

```text
mazegen/
├── __init__.py
├── cell.py
├── generator.py
├── perfect.py
├── imperfect.py
└── solver.py
```

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    20,
    15,
    (0, 0),
    (12, 11),
    perfect=False,
    seed=22,
)
generator.generate()
board = generator.board
path = generator.solve()
```

`board` is a list of rows of `Cell` objects (`board[y][x]`). `path` is the shortest path as `N`/`E`/`S`/`W`, or `None` when generation failed. Parameters are `width`, `height`, entry, exit, `perfect` (default `False`), and `seed` (`None` uses the system time).

Build the package from this directory:

```bash
python3 -m build
```

The artifacts are `dist/mazegen-1.0.0-py3-none-any.whl` and `dist/mazegen-1.0.0.tar.gz`. Another project installs it with `pip install mazegen-1.0.0-py3-none-any.whl`.

## Team and project management

| Team member | 42 login | Responsibility |
| --- | --- | --- |
| Núria Gómez Vernet | ngomez-v | Configuration parser, cell and wall model, perfect and imperfect generation, MiniLibX display, integration|
| Morvarid Hasheminasab | seyehash | Shortest-path solver (breadth-first search, neighbours, and path reconstruction), package and documentation|

The original plan was to split the work into a generator and a solver, then connect both to one window. That split stayed. The generator landed first (cells, randomized depth-first search, then the imperfect braiding and the green/purple display colours). The solver was integrated after the board format was stable, and the path was drawn in the same window. Documentation and docstrings were finished after the behaviour was in place.

What worked was keeping generation in `mazegen/` with no display imports, so the same class writes the file and feeds the window. The seed made maze bugs reproducible. The Makefile gave both of us the same install, run, debug, lint, and clean commands.

What to improve is writing the README as each feature landed, instead of leaving the algorithm, keys, and logins for the end, and agreeing at the start that `a_maze_ing.py`, `LICENSE.md`, and `README.md` sit at the root that will be evaluated.

Tools: Python 3, Git on the 42 Vogsphere, the Makefile, `flake8`, `mypy`, MiniLibX, and `python -m build`.

## Resources

- Python documentation: https://docs.python.org/3/
- `enum.IntFlag`: https://docs.python.org/3/library/enum.html
- `collections.deque`: https://docs.python.org/3/library/collections.html#collections.deque
- Maze generation algorithms: https://en.wikipedia.org/wiki/Maze_generation_algorithm
- Breadth-first search: https://en.wikipedia.org/wiki/Breadth-first_search
- Python Packaging User Guide: https://packaging.python.org/
- MiniLibX Python binding shipped with the project (`pixels_library/mlx_CLXV`)

### Use of AI

AI was used for these tasks:

- Explaining the wall bit layout and `IntFlag`
- Explaining Python modules, packages, and dataclasses
- Walking through breadth-first search, the parent map, and path reconstruction
- Discussing how to split the generator, the solver, the display, and the package
- Reading the MiniLibX drawing code and naming the key codes
- Drafting the first README outline and later filling its missing sections from the finished code

Every suggestion was reviewed, tested, and adapted by the team. Both members can explain the submitted code.

## License

This project is released under the MIT License. See `LICENSE.md`. The license allows later projects to reuse and distribute this software, including the right to use, copy, modify, merge, publish, distribute, sublicense, and sell it, provided the copyright notice is kept.
```