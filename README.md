*This project has been created as part of the 42 curriculum by maguzman, dbali*

## Description

A-Maze-ing is a maze generator and visualizer, built for the 42 curriculum. It reads a
configuration file, generates a maze with a recursive-backtracker algorithm — either a
`PERFECT` maze with exactly one path between any two cells, or a Pac-Man-style playable board
with open corners and multiple routes — hides a "42" pattern in the walls, writes it out in a
hexadecimal format, and displays it live in an MLX window. The window is interactive: regenerate
a new maze, show or hide the shortest solution path, and rotate between several wall-colour
palettes, all without restarting the program. The generation logic itself lives in a standalone,
reusable `mazegen` package, independent of the config/display code around it.

## Instructions

**Requirements:** Python 3.10+, and (for the MLX display) a Linux environment with Vulkan
available — `build-essential git pkg-config libvulkan-dev vulkan-tools mesa-vulkan-drivers
libxcb1-dev libxcb-keysyms1-dev libbsd-dev zlib1g-dev`.

```sh
make install   # creates .amazeing_env, installs dependencies, builds MLX
make run       # runs python3 a_maze_ing.py config.txt
make debug     # same, under pdb
make lint      # flake8 . && mypy . --warn-return-any --warn-unused-ignores \
               #   --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
make lint-strict  # flake8 . && mypy . --strict
make clean     # removes caches/build artifacts
make build     # builds the mazegen-*.whl package
```

To run with a different config file: `python3 a_maze_ing.py your_config.txt`.

Once the window is open:

```
1  Re-generate a new maze
2  Show / Hide the shortest path
3  Rotate the wall colours
4  Quit
```

## Configuration file format

One `KEY=VALUE` pair per line; lines starting with `#` are comments and are ignored.

| Key           | Required? | Description                      | Example                |
| ------------- | --------- | --------------------------------- | ----------------------- |
| `WIDTH`       | yes       | Maze width, in cells              | `WIDTH=20`               |
| `HEIGHT`      | yes       | Maze height, in cells             | `HEIGHT=15`              |
| `ENTRY`       | yes       | Entry coordinates, `x,y`          | `ENTRY=0,0`               |
| `EXIT`        | yes       | Exit coordinates, `x,y`           | `EXIT=19,14`              |
| `OUTPUT_FILE` | yes       | Output filename                   | `OUTPUT_FILE=maze.txt`    |
| `PERFECT`     | yes       | `True` for a perfect (loopless) maze, `False` for a playable board with loops | `PERFECT=True` |
| `SEED`        | no        | Reproducibility seed; same seed → same maze | `SEED=42`       |

See `config.txt` at the repository root for a working example.

## Reusable module

The maze generation logic lives in the `mazegen` package (`mazegen/generator.py`,
`mazegen/structure.py`), and it is independent of config parsing, the output file, and the MLX display, making it reusable in another project.

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

- **Custom parameters:** `width`, `height` (maze size); `entry_point`, `exit_point` (`(x, y)`
  tuples); `seed` (optional - same seed twice gives the same maze back); `perfect` (`True` for
  exactly one path between any two cells, `False` for a looped, playable board).
- **Accessing the structure:** `generate_maze()` returns a `Grid`. `grid.cells` is a 2D list of
  `Cell` objects indexed `[y][x]`; each `Cell` has a `.walls` bitmask (`mazegen.structure.Walls`)
  and a `.position` `(x, y)` tuple. The same `Grid` stays available as `generator.grid`.
- **Accessing a solution:** `solve()` returns the shortest path from `entry_point` to
  `exit_point` as a string of direction letters (`N`/`E`/`S`/`W`), e.g. `"EESEESS..."`.
- `maze_to_hex()` returns the maze as a list of strings, one hex digit per cell per row (the
  output-file encoding: bit 0 = North, 1 = East, 2 = South, 3 = West; a set bit means that wall
  is closed).

The full version of this documentation can also be found in `mazegen/__init__.py`.

## Resources

- MLX library: https://github.com/42school/mlx_CLXV
- MLX tutorial: https://aurelienbrabant.fr/blog/getting-started-with-the-minilibx
- Python bitwise operators: https://realpython.com/python-bitwise-operators/
- Lospec (colour palette reference): https://lospec.com/
- Python dictionary iteration: https://www.w3schools.com/PYTHON/python_dictionaries_loop.asp
- Maze generation algorithms, interactive: https://professor-l.github.io/mazes/
- CMU 15-112 maze generation notes (PDF): https://www.cs.cmu.edu/~112-s23/notes/student-tp-guides/Mazes.pdf

**How AI was used:** Claude was used throughout this project primarily as a
Socratic tutor and pair-programming partner to guide us in some of the design decisions, questioning our hypothesis, and brainstorming on possible solutions. We also use it to explain some Python mechanics (bitmasking, closures,
`nonlocal`, type hints).  We also use it as a reference for discovering the MLX library and building a more easy to read documentation for it. 

## Maze generation algorithm

### Cells, graphs, and a tree hiding in the subject

Strip away the walls-and-corridors picture for a second and the maze is a **graph**: every
cell is a node, and every wall that gets knocked down becomes an edge connecting two nodes. A
**cycle** — or a "loop" — shows up when two nodes that already have a path
between them get a second one: walk from A to B one way, then a different way, and a cycle is
sitting in the middle of that. A **tree** is a connected graph with zero cycles; for N nodes a
tree always has exactly N-1 edges, no more, no less — pull one out and it falls apart into
disconnected pieces, add one back and a cycle appears out of nowhere. A **spanning tree** is a
tree that reaches every node of some bigger graph. Put those together and "perfect maze" stops
being a vague phrase: it's a spanning tree over the grid. "Exactly one path between any two
cells" isn't a rule we enforce separately — it's just what a spanning tree already is.

### The algorithm itself

We generate mazes with a **recursive backtracker** — randomized depth-first search over the
grid, run with an explicit stack rather than actual Python recursion (a 100x100 grid would blow
past the recursion limit otherwise).

A stack is a last-in-first-out pile — like a stack of plates, you only ever add or remove from
the top. The walk: start at any cell, mark it visited, push it onto the stack. At each step,
check the current cell's unvisited neighbours. If there's at least one, pick one at random,
knock down the wall between the two cells, mark the new one visited, and push it on top of the
stack — one step forward along the trail. If there are none left (a dead end), pop the stack
instead: discard whatever's on top and step back to the cell underneath it. The stack is
exactly the trail walked so far, so popping it is retracing the last move, cell by cell, until
landing somewhere with unexplored territory left to push into. Keep alternating push and pop
until the stack runs empty, which only happens once every cell has been visited. What's left
standing at that point is, by construction, a spanning tree — zero cycles, one route between
any two cells, a valid `PERFECT=True` maze with no extra work.

### Why this one

Our subject needs two different boards out of the same generator: a perfect maze
(`PERFECT=True`) and a Pac-Man-style board with loops, open corners, and a mostly dead-end-free
layout (the default mode). A spanning-tree algorithm only gives you the first one on its own —
getting from "perfect maze" to "playable board" always means a second pass afterward that
knocks down a few extra walls to open loops back up, while checking that doing so never opens a
3x3 block. That second pass is the same regardless of which spanning-tree algorithm produced
the starting maze, so the choice of *which* one matters less for the loopy mode than it does
for the perfect mode, and for the perfect mode, backtracker is simply the cheapest to get right.

Three things tipped it over Prim's or Kruskal's specifically:

- **One data structure.** A stack and a visited set. No union-find bookkeeping (Kruskal's
  needs one to avoid accidentally closing a loop), no frontier priority list (Prim's). Less
  code means less surface area for the kind of logic bug that's easy to introduce and hard to
  spot in a maze — a coherence error that only shows up three cells later.
- **Fewer dead-ends by construction.** Backtracker tends toward long, winding corridors instead
  of lots of short branches, which happens to line up with two requirements at once: "dead-ends
  should stay rare" in the default mode, and the zero-dead-end bonus, which needs fewer wall
  removals to reach zero if there weren't many dead-ends to begin with.
- **Bounded runtime.** Strictly O(width × height), with no risk of the pathological slow case
  that random-walk approaches (Aldous-Broder, Wilson's) can hit on larger grids — relevant here
  since `WIDTH`/`HEIGHT` come from the config file, not a fixed size we control.

Reproducibility (the `SEED` key) isn't a deciding factor — every algorithm below is equally
reproducible once Python's `random` module is seeded once at the start. It's a baseline
requirement, not a differentiator.

### Reproducibility, and why the tree shape helps with solving too

`SEED` works because Python's `random` module isn't actually random — it's a deterministic
generator sitting on an internal state. `MazeGenerator.__init__` creates its own dedicated
generator instance from it, `self.rng = random.Random(seed)`, rather than touching the global
`random` module's state — so building a maze never interferes with any other code in the same
program that also happens to use `random`. Seed it with the same number twice and every
`self.rng.choice()` call that follows — which neighbour to carve toward, which wall to reopen
later during braiding — comes back identical both times. The maze looks random to whoever's
staring at it; underneath, `SEED` already decided all of it.

The tree shape pays off again once it's time to solve the maze, not just build it. In
`PERFECT=True` mode the result is a tree, and a tree has exactly one path between any two
nodes — so finding the route from entry to exit needs no real searching: any walk that doesn't
double back on itself arrives by the only path there is, because there's nothing else to
compare it against. That stops being true the moment the default mode's braiding pass opens
loops back up — with more than one route on the board, picking the *shortest* one needs an
actual breadth-first search over the result. So the backtracker hands us a free solver for the
mandatory perfect mode, and the same traversal logic generalizes into a real BFS once loops
exist.

### The solver: breadth-first search

`MazeGenerator.solve()` finds the shortest entry-to-exit path with a **breadth-first search**
(BFS) — the same cell-by-cell traversal idea as the backtracker, but with one key structural
swap: a **queue** (first-in-first-out) instead of a **stack** (last-in-first-out). That
difference is the whole reason it finds the *shortest* path instead of just *a* path.

The walk: start at the entry, push it into the queue, mark it seen. At each step, pop the
*front* of the queue (the cell that's been waiting longest) and look at its open walls. For
every neighbour reached through one that hasn't been seen yet, mark it seen, remember which
cell and which direction (`N`/`E`/`S`/`W`) led to it, and push it onto the *back* of the queue.
Keep going until the exit comes out of the front of the queue.

Because new cells always go on the back and get processed in the order they went in, the queue
stays sorted by distance from the entry without anything having to sort it: every cell exactly
1 step away gets processed before any cell 2 steps away, which gets processed before any cell 3
steps away, and so on. So the very first time the exit is pulled off the queue, it's guaranteed
to have arrived via a shortest path — there's no way a longer route could have reached it first,
since everything closer was already fully explored. (A stack can't give that guarantee: it can
dive deep down one branch before ever looking at a closer cell on another branch.)

Once the exit is reached, the path itself gets reconstructed backwards: each cell remembers
only "which cell did I come from, and which direction did that take," so walking from the exit
back through those breadcrumbs to the entry retraces the whole route, one letter at a time. That
list comes out in exit-to-entry order, so it gets reversed once at the end to read entry-to-exit
— the same `N`/`E`/`S`/`W` format the output file expects.

Runtime is O(cells), same bound as the backtracker: every cell is pushed onto the queue and
popped off it at most once.

### Alternatives considered

| Algorithm | What it does | Dead-end texture | Extra data structure | Runtime on a grid |
| --- | --- | --- | --- | --- |
| **Recursive backtracker** (chosen) | Randomized DFS, carve as you go, backtrack on dead end | Long corridors, dead-ends relatively rare | Stack + visited set | O(cells), consistently fast |
| Prim's (randomized) | Grow outward from a start cell, adding a random frontier cell each step | Bushy, many short dead-ends | Frontier list | O(cells), fast |
| Kruskal's (randomized) | Randomly merge disjoint regions, skipping any wall that would close a loop | Evenly distributed branching | Union-find (disjoint-set) | O(cells log cells), fast |
| Wilson's (loop-erased random walk) | Random walk from each unvisited cell, erasing loops as it goes, until it hits the growing tree | Statistically unbiased — no structural texture at all | Path tracking per walk | Slower, walk length is unpredictable |
| Aldous-Broder (random walk) | Pure random walk until every cell's been visited once | Also unbiased | None beyond a visited set | Often much slower — walks re-visit the same cells a lot before finishing |
| Binary tree / sidewinder | For each cell, carve north or east (or similar fixed pair) | Strong diagonal bias toward two edges | None | O(cells), fastest of all |

Wilson's and Aldous-Broder are the "fairest" generators in a statistical sense — every possible
maze is equally likely — but that fairness costs runtime, and our subject never asks for
statistical uniformity, just a valid, reproducible, playable maze. Binary tree is the opposite
tradeoff: trivial and fast, but its visible diagonal drift would fight against hiding a
recognizable "42" pattern in the walls.

## Team and project management

We both worked together debating the issues and trying to understand the elements needed for the maze. Diana focused more on developing the algorithm to build the maze and the solver as well as the logic for implementing multilple solutions. Mario focused more on getting the building block to make the elements of the maze functional to the algorithm. We were both looking into the color palettes ;) 
