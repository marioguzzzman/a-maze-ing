#! /usr/bin/env python3

from mlx import Mlx
from mazegen.generator import MazeGenerator
from mazegen.structure import Cell, Grid, Walls

# Menu
"""
- **A graphical display using the MiniLibX (MLX) library.**

=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit
Choice? (1-4): _
"""

CELL_SIZE = 70
BYTES_PER_PIXEL = 4
# each colour is 4 bytes: blue, green, red, alpha (or similar order)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
PATTERN_COLOR = (0, 165, 255, 255)

KEY_1 = ord("1")
KEY_2 = ord("2")
KEY_3 = ord("3")
KEY_4 = ord("4")


def build_visual_maze(generator: MazeGenerator) -> None:
    show_grid(generator)


def set_pixel(
    pixels: memoryview, position: int, color: tuple[int, int, int, int]
) -> None:
    pixels[position] = color[0]
    pixels[position + 1] = color[1]
    pixels[position + 2] = color[2]
    pixels[position + 3] = color[3]


def clear_image(
    pixels: memoryview, size_line: int, width: int, height: int
) -> None:
    for y in range(height):
        for x in range(width):
            position = y * size_line + x * BYTES_PER_PIXEL
            set_pixel(pixels, position, BLACK)


def draw_horizontal_wall(
    pixels: memoryview, size_line: int, y: int, x_start: int, x_end: int
) -> None:
    for x in range(x_start, x_end + 1):
        position = y * size_line + x * BYTES_PER_PIXEL
        set_pixel(pixels, position, WHITE)


def draw_vertical_wall(
    pixels: memoryview, size_line: int, x: int, y_start: int, y_end: int
) -> None:
    for y in range(y_start, y_end + 1):
        position = y * size_line + x * BYTES_PER_PIXEL
        set_pixel(pixels, position, WHITE)


def fill_cell(
    pixels: memoryview, size_line: int, cell: Cell,
    color: tuple[int, int, int, int],
) -> None:
    cell_x, cell_y = cell.position
    left = cell_x * CELL_SIZE
    top = cell_y * CELL_SIZE
    for y in range(top, top + CELL_SIZE):
        for x in range(left, left + CELL_SIZE):
            position = y * size_line + x * BYTES_PER_PIXEL
            set_pixel(pixels, position, color)


def draw_cell(pixels: memoryview, size_line: int, cell: Cell) -> None:
    if cell.cell_42:
        fill_cell(pixels, size_line, cell, PATTERN_COLOR)
        return

    cell_x, cell_y = cell.position
    left = cell_x * CELL_SIZE
    top = cell_y * CELL_SIZE
    right = left + CELL_SIZE - 1
    bottom = top + CELL_SIZE - 1

    if (cell.walls & Walls.NORTH) == Walls.NORTH:
        draw_horizontal_wall(pixels, size_line, top, left, right)
    if (cell.walls & Walls.SOUTH) == Walls.SOUTH:
        draw_horizontal_wall(pixels, size_line, bottom, left, right)
    if (cell.walls & Walls.WEST) == Walls.WEST:
        draw_vertical_wall(pixels, size_line, left, top, bottom)
    if (cell.walls & Walls.EAST) == Walls.EAST:
        draw_vertical_wall(pixels, size_line, right, top, bottom)


def show_grid(generator: MazeGenerator) -> None:
    grid = generator.generate_maze()
    mlx_library = Mlx()
    mlx_connection = mlx_library.mlx_init()

    window_width = grid.width * CELL_SIZE
    window_height = grid.height * CELL_SIZE
    window = mlx_library.mlx_new_window(
        mlx_connection, window_width, window_height, "maze"
    )
    mlx_library.mlx_clear_window(mlx_connection, window)

    image = mlx_library.mlx_new_image(
        mlx_connection, window_width, window_height
    )
    # mlx_get_data_addr gives back 4 values at once: the writable pixel
    # buffer, plus 3 numbers describing it. We only need the first and
    # third here, but we still have to catch all 4 on the left-hand side.
    pixels, bits_per_pixel, size_line, image_format = (
        mlx_library.mlx_get_data_addr(image)
    )

    def redraw(current_grid: Grid) -> None:
        clear_image(pixels, size_line, window_width, window_height)
        for row in current_grid.cells:
            for cell in row:
                draw_cell(pixels, size_line, cell)
        mlx_library.mlx_put_image_to_window(
            mlx_connection, window, image, 0, 0
        )

    redraw(grid)
    menu_actions()

    def on_key_press(key_code: int, extra_data: object) -> int:
        nonlocal grid
        if key_code == KEY_1:
            grid = generator.generate_maze()
            redraw(grid)
        if key_code == KEY_2:
            pass
        if key_code == KEY_3:
            pass
        if key_code == KEY_4:
            mlx_library.mlx_loop_exit(mlx_connection)
        return 0

    mlx_library.mlx_key_hook(window, on_key_press, None)
    mlx_library.mlx_loop(mlx_connection)
    mlx_library.mlx_destroy_image(mlx_connection, image)
    mlx_library.mlx_release(mlx_connection)


def menu_actions() -> None:
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show / Hide the shortest path")
    print("3. Rotate the wall colours")
    print("4. Quit")
    print("Choice? (1-4):")


def main() -> None:
    # standalone test, used only when running this file directly -
    # the real pipeline builds this via a_maze_ing.py instead
    test_generator = MazeGenerator(10, 8, (0, 0), (9, 7), 42)
    show_grid(test_generator)


if __name__ == "__main__":
    main()
