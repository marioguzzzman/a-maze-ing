# Shows the flood fill solving the maze, in your web browser.
#
# This script creates a file called maze_visual.html and opens it.
# It works on any computer that has a web browser (nothing to install).
#
# Run it with:  python3 visualize_html.py
#
# What you will see:
#   1. The maze: black = wall, white = open, green = start, red = end.
#   2. The flood spreading from the start, one step at a time (light blue).
#      Each cell shows its distance from the start.
#   3. The shortest path, drawn in yellow.

import os
import webbrowser

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

# Find the biggest distance, so the page knows when the flood is finished.
max_distance = 0
for y in range(height):
    for x in range(width):
        if distance[y][x] > max_distance:
            max_distance = distance[y][x]


# Build the HTML table: one <td> (square) for each cell of the maze.
# Each square remembers its distance (data-d) and if it is on the path.
table_rows = ""
for y in range(height):
    table_rows = table_rows + "<tr>"
    for x in range(width):
        letter = maze[y][x]

        style = "open"
        text = ""
        if letter == "1":
            style = "wall"
        elif letter == "S":
            style = "start"
            text = "S"
        elif letter == "E":
            style = "end"
            text = "E"

        on_path = "0"
        if drawing[y][x] == ".":
            on_path = "1"

        table_rows = (table_rows + '<td class="' + style + '" data-d="'
                      + str(distance[y][x]) + '" data-path="' + on_path + '">'
                      + text + "</td>")
    table_rows = table_rows + "</tr>\n"


# The page. TABLE_ROWS and MAX_DISTANCE are replaced just below.
page = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Flood fill maze solver</title>
<style>
  body  { font-family: Arial, sans-serif; text-align: center; }
  table { border-collapse: collapse; margin: 20px auto; }
  td    { width: 50px; height: 50px; border: 1px solid gray;
          text-align: center; font-weight: bold; font-size: 18px; }
  .wall  { background: black; }
  .open  { background: white; }
  .start { background: green; color: white; }
  .end   { background: red; color: white; }
  .flood { background: lightblue; }
  .path  { background: yellow; }
</style>
</head>
<body>
<h2>Flood fill maze solver</h2>
<table>
TABLE_ROWS</table>
<button onclick="location.reload()">Replay</button>

<script>
var level = 0;
var maxLevel = MAX_DISTANCE;
var cells = document.querySelectorAll("td");

// Color all the cells that are one step further than the last time.
function nextStep() {
  level = level + 1;
  for (var i = 0; i < cells.length; i++) {
    var cell = cells[i];
    if (cell.className == "open" && cell.dataset.d == level) {
      cell.className = "flood";
      cell.textContent = level;
    }
  }
  if (level < maxLevel) {
    setTimeout(nextStep, 250);
  } else {
    setTimeout(showPath, 500);
  }
}

// Color the shortest path.
function showPath() {
  for (var i = 0; i < cells.length; i++) {
    var cell = cells[i];
    if (cell.dataset.path == "1") {
      cell.className = "path";
      cell.textContent = cell.dataset.d;
    }
  }
}

setTimeout(nextStep, 500);
</script>
</body>
</html>
"""

page = page.replace("TABLE_ROWS", table_rows)
page = page.replace("MAX_DISTANCE", str(max_distance))

# Save the page next to this script and open it in the browser.
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maze_visual.html")
with open(file_path, "w", encoding="utf-8") as file:
    file.write(page)

print("Opening", file_path)
webbrowser.open(file_path)
