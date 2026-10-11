#! /usr/bin/env python3

from mlx import Mlx
from mazegen.structure import Cell, Walls

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
BLACK = 0
WHITE = 255

KEY_1 = ord("1")


def build_visual_maze(config_ready: dict) -> None:
    show_grid(config_ready)


def build_grid(config_ready: dict) -> list[list[Cell]]:
    grid = []
    for y in range(config_ready["HEIGHT"]):
        row = []
        for x in range(config_ready["WIDTH"]):
            new_cell = Cell((x, y))
            row.append(new_cell)
        grid.append(row)
    return grid


def set_pixel(pixels: memoryview, position: int, value: int) -> None:
    # one pixel = 4 bytes in a row (blue, green, red, alpha, or similar order)
    # using the same value for all 4 keeps it simple: 0 = black, 255 = white
    pixels[position] = value
    pixels[position + 1] = value
    pixels[position + 2] = value
    pixels[position + 3] = value


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


def draw_cell(pixels: memoryview, size_line: int, cell: Cell) -> None:
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


def show_grid(config_ready: dict) -> None:
    mlx_library = Mlx()
    mlx_connection = mlx_library.mlx_init()

    window_width = config_ready["WIDTH"] * CELL_SIZE
    window_height = config_ready["HEIGHT"] * CELL_SIZE
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

    clear_image(pixels, size_line, window_width, window_height)

    grid = build_grid(config_ready)
    for row in grid:
        for cell in row:
            draw_cell(pixels, size_line, cell)

    mlx_library.mlx_put_image_to_window(mlx_connection, window, image, 0, 0)

    def on_key_press(key_code: int, extra_data: object) -> int:
        if key_code == KEY_1:
            mlx_library.mlx_loop_exit(mlx_connection)
        return 0

    mlx_library.mlx_key_hook(window, on_key_press, None)
    mlx_library.mlx_loop(mlx_connection)
    mlx_library.mlx_destroy_image(mlx_connection, image)
    mlx_library.mlx_release(mlx_connection)


def main() -> None:
    # standalone test values, used only when running this file directly
    test_config = {"WIDTH": 10, "HEIGHT": 8}
    show_grid(test_config)


if __name__ == "__main__":
    main()
