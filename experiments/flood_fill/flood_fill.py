# Solves the maze from maze.py with a flood fill (breadth-first search).
#
# Step 1: flood fill from the start. Each cell we reach gets a number:
#         how many steps it takes to get there from the start.
# Step 2: starting at the end, go back to the start by always moving
#         to a neighbour with a number one smaller. That is the shortest path.
#
# Run it with:  python3 flood_fill.py

from maze import maze

height = len(maze)
width = len(maze[0])

# The 4 neighbours of a cell: right, left, down, up
dx_list = [1, -1, 0, 0]
dy_list = [0, 0, 1, -1]


# Find where S and E are
start_x = 0
start_y = 0
end_x = 0
end_y = 0
for y in range(height):
    for x in range(width):
        if maze[y][x] == "S":
            start_x = x
            start_y = y
        if maze[y][x] == "E":
            end_x = x
            end_y = y


# Step 1: flood fill.
# distance[y][x] = steps from the start. -1 means "not reached yet".
distance = []
for y in range(height):
    row = []
    for x in range(width):
        row.append(-1)
    distance.append(row)

distance[start_y][start_x] = 0

# The list of cells we still need to look at (a waiting line).
to_visit = [[start_x, start_y]]

while len(to_visit) > 0:
    # Take the first cell of the waiting line
    cell = to_visit.pop(0)
    x = cell[0]
    y = cell[1]

    # Look at its 4 neighbours
    for i in range(4):
        new_x = x + dx_list[i]
        new_y = y + dy_list[i]

        # Skip if outside the maze
        if new_x < 0 or new_x >= width or new_y < 0 or new_y >= height:
            continue
        # Skip if it is a wall
        if maze[new_y][new_x] == "1":
            continue
        # Skip if we already reached it
        if distance[new_y][new_x] != -1:
            continue

        # New cell: it is one step further than the current cell
        distance[new_y][new_x] = distance[y][x] + 1
        to_visit.append([new_x, new_y])


# Step 2: go back from the end to the start.
if distance[end_y][end_x] == -1:
    print("No path found.")
else:
    # Turn the maze into a list of lists so we can change characters
    drawing = []
    for row in maze:
        drawing.append(list(row))

    x = end_x
    y = end_y
    steps = 0

    while distance[y][x] != 0:
        # Find the neighbour that is one step closer to the start
        for i in range(4):
            new_x = x + dx_list[i]
            new_y = y + dy_list[i]

            if new_x < 0 or new_x >= width or new_y < 0 or new_y >= height:
                continue

            if distance[new_y][new_x] == distance[y][x] - 1:
                x = new_x
                y = new_y
                steps = steps + 1
                # Draw a dot on this cell (but keep the S as it is)
                if drawing[y][x] != "S":
                    drawing[y][x] = "."
                break

    # Print the maze with the path drawn
    for row in drawing:
        print("".join(row))
    print()
    print("Shortest path:", steps, "steps")
