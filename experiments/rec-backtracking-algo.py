
maze = [
    [0, 0, 1, 0, 0],
    [1, 0, 1, 0, 1],
    [0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0]
]

rows = len(maze)
cols = len(maze[0])

def solve_maze(r, c, path):
    # Check boundaries and walls
    if (r < 0 or r >= rows or
        c < 0 or c >= cols or
        maze[r][c] == 1):
        return False

    # Exit reached
    if (r, c) == (rows - 1, cols - 1):
        path.append((r, c))
        return True

    # Mark this cell as visited
    maze[r][c] = 1
    path.append((r, c))

    # Try moving down, right, up, and left
    directions = [
        (1, 0),
        (0, 1),
        (-1, 0),
        (0, -1)
    ]

    for dr, dc in directions:
        if solve_maze(r + dr, c + dc, path):
            return True

    # Backtrack: remove this cell from the path
    path.pop()

    return False


path = []

if solve_maze(0, 0, path):
    print("Path found:")
    print(path)
else:
    print("No path exists")
