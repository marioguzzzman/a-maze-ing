*This project has been created as part of the 42 curriculum by maguzman, dbali*

**Description** section that clearly presents the project, including its goal and a brief
  overview.

**Instructions** section containing any relevant information about compilation,
  installation, and/or execution.

**Resources** section listing classic references related to the topic (documentation,
  articles, tutorials, etc.), as well as a description of **how AI was used** — specifying for
  which tasks and which parts of the project.

**Additional sections may be required depending on the project** (e.g., usage examples,
  feature list, technical choices, etc.).

*Any required additions will be explicitly listed below.*

- The complete structure and format of your config file.

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
generator sitting on an internal state, and `random.seed(SEED)` sets that state explicitly.
Seed it with the same number twice and every `random.choice()` call that follows — which
neighbour to carve toward, which wall to reopen later during braiding — comes back identical
both times. The maze looks random to whoever's staring at it; underneath, `SEED` already
decided all of it.

The tree shape pays off again once it's time to solve the maze, not just build it. In
`PERFECT=True` mode the result is a tree, and a tree has exactly one path between any two
nodes — so finding the route from entry to exit needs no real searching: any walk that doesn't
double back on itself arrives by the only path there is, because there's nothing else to
compare it against. That stops being true the moment the default mode's braiding pass opens
loops back up — with more than one route on the board, picking the *shortest* one needs an
actual breadth-first search over the result. So the backtracker hands us a free solver for the
mandatory perfect mode, and the same traversal logic generalizes into a real BFS once loops
exist.

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


# MLX visualizaton 

https://github.com/42school/mlx_CLXV

- What part of your code is reusable, and how.
- Your team and project management with:
  - The roles of each team member.
  - Your anticipated planning and how it evolved until the end.
  - What worked well and what could be improved.
  - Have you used any specific tools? Which ones?
