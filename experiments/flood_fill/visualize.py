# Shows the flood fill solving the maze, in a window.
#
# It uses tkinter, which comes with Python (nothing to install).
#
# Run it with:  python3 visualize.py
#
# What you will see:
#   1. The maze: black = wall, white = open, green = start, red = end.
#   2. The flood spreading from the start, one step at a time (light blue).
#      Each cell shows its distance from the start.
#   3. The shortest path, drawn in yellow.

try:
    import tkinter
except ImportError:
    print("tkinter is not installed on this computer.")
    print("Use visualize_html.py instead: it opens in your web browser.")
    exit()

# Importing flood_fill runs the whole algorithm (and prints the result).
# After that we can use its variables:
#   flood_fill.maze     -> the maze rows
#   flood_fill.distance -> the distance of every cell (-1 = not reached)
#   flood_fill.drawing  -> the maze with the shortest path drawn as '.'
import flood_fill

# If the maze has no solution, flood_fill has no path to draw.
if not hasattr(flood_fill, "drawing"):
    print("The maze has no solution, nothing to show.")
    exit()

maze = flood_fill.maze
distance = flood_fill.distance
drawing = flood_fill.drawing

height = len(maze)
width = len(maze[0])
cell_size = 50          # size of one cell, in pixels
delay = 250             # time between two steps, in milliseconds

# Find the biggest distance, so we know when the flood is finished.
max_distance = 0
for y in range(height):
    for x in range(width):
        if distance[y][x] > max_distance:
            max_distance = distance[y][x]


# Create the window and the drawing area.
try:
    window = tkinter.Tk()
except tkinter.TclError:
    print("Could not open a window (no screen available).")
    print("Use visualize_html.py instead: it opens in your web browser.")
    exit()
window.title("Flood fill maze solver")


def stop_staying_on_top():
    window.attributes("-topmost", False)


# Bring the window to the front for half a second, so it is not hidden.
window.lift()
window.attributes("-topmost", True)
window.after(500, stop_staying_on_top)
canvas = tkinter.Canvas(window, width=width * cell_size, height=height * cell_size)
canvas.pack()


def draw_cell(x, y, color, text):
    """Draw one square at position (x, y), with a text in the middle."""
    left = x * cell_size
    top = y * cell_size
    canvas.create_rectangle(left, top, left + cell_size, top + cell_size,
                            fill=color, outline="gray")
    if text != "":
        canvas.create_text(left + cell_size // 2, top + cell_size // 2,
                           text=text, font=("Arial", 14, "bold"))


# Step 1: draw the empty maze.
for y in range(height):
    for x in range(width):
        if maze[y][x] == "1":
            draw_cell(x, y, "black", "")
        elif maze[y][x] == "S":
            draw_cell(x, y, "green", "S")
        elif maze[y][x] == "E":
            draw_cell(x, y, "red", "E")
        else:
            draw_cell(x, y, "white", "")


# The distance we are showing right now.
current_distance = 0


def show_next_step():
    """Step 2: color all the cells that are one step further than the last time."""
    global current_distance
    current_distance = current_distance + 1

    for y in range(height):
        for x in range(width):
            is_open = maze[y][x] == "0"
            if is_open and distance[y][x] == current_distance:
                draw_cell(x, y, "light blue", str(current_distance))

    if current_distance < max_distance:
        window.after(delay, show_next_step)     # do it again in a moment
    else:
        window.after(delay * 2, show_path)      # the flood is finished


def show_path():
    """Step 3: color the shortest path."""
    for y in range(height):
        for x in range(width):
            if drawing[y][x] == ".":
                draw_cell(x, y, "yellow", str(distance[y][x]))


# Start the animation after a short pause, then keep the window open.
window.after(delay * 2, show_next_step)
window.mainloop()
