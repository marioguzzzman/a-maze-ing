#! /usr/bin/env python3

from mlx import Mlx
import random
from mazegen.generator import LETTERS, MazeGenerator
from mazegen.structure import Cell, Grid, Walls


CELL_SIZE = 60
BYTES_PER_PIXEL = 4

PUMPKIN = {
    "background": (14, 6, 6, 255),
    "wall": (125, 28, 54, 255),
    "pattern": (13, 79, 211, 255),
    "path": (144, 158, 249, 255),
}
SODA = {
    "background": (204, 118, 33, 255),
    "wall": (110, 125, 255, 255),
    "pattern": (172, 166, 252, 255),
    "path": (203, 231, 232, 255),
}
CHERRY_MELON = {
    "background": (234, 222, 252, 255),
    "wall": (109, 77, 255, 255),
    "pattern": (53, 89, 38, 255),
    "path": (36, 40, 1, 255),
}
SOVIET = {
    "background": (192, 214, 232, 255),
    "wall": (141, 147, 146, 255),
    "pattern": (28, 40, 161, 255),
    "path": (0, 0, 0, 255),
}
PALETTES = [PUMPKIN, SODA, CHERRY_MELON, SOVIET]

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
    pixels: memoryview, size_line: int, width: int, height: int,
    background_color: tuple[int, int, int, int],
) -> None:
    for y in range(height):
        for x in range(width):
            position = y * size_line + x * BYTES_PER_PIXEL
            set_pixel(pixels, position, background_color)


def draw_horizontal_wall(
    pixels: memoryview, size_line: int, y: int, x_start: int, x_end: int,
    wall_color: tuple[int, int, int, int],
) -> None:
    for x in range(x_start, x_end + 1):
        position = y * size_line + x * BYTES_PER_PIXEL
        set_pixel(pixels, position, wall_color)


def draw_vertical_wall(
    pixels: memoryview, size_line: int, x: int, y_start: int, y_end: int,
    wall_color: tuple[int, int, int, int],
) -> None:
    for y in range(y_start, y_end + 1):
        position = y * size_line + x * BYTES_PER_PIXEL
        set_pixel(pixels, position, wall_color)


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


def draw_cell(
    pixels: memoryview, size_line: int, cell: Cell,
    palette: dict[str, tuple[int, int, int, int]],
) -> None:
    if cell.cell_42:
        fill_cell(pixels, size_line, cell, palette["pattern"])
        return

    cell_x, cell_y = cell.position
    left = cell_x * CELL_SIZE
    top = cell_y * CELL_SIZE
    right = left + CELL_SIZE - 1
    bottom = top + CELL_SIZE - 1
    wall_color = palette["wall"]

    if (cell.walls & Walls.NORTH) == Walls.NORTH:
        draw_horizontal_wall(pixels, size_line, top, left, right, wall_color)
    if (cell.walls & Walls.SOUTH) == Walls.SOUTH:
        draw_horizontal_wall(
            pixels, size_line, bottom, left, right, wall_color
        )
    if (cell.walls & Walls.WEST) == Walls.WEST:
        draw_vertical_wall(pixels, size_line, left, top, bottom, wall_color)
    if (cell.walls & Walls.EAST) == Walls.EAST:
        draw_vertical_wall(pixels, size_line, right, top, bottom, wall_color)


def show_grid(generator: MazeGenerator) -> None:
    grid = generator.generate_maze()
    path_letters = generator.solve()
    mlx_library = Mlx()
    mlx_connection = mlx_library.mlx_init()

    window_width = grid.width * CELL_SIZE
    window_height = grid.height * CELL_SIZE
    window = mlx_library.mlx_new_window(
        mlx_connection, window_width, window_height, "maze"
    )
    mlx_library.mlx_clear_window(mlx_connection, window)

    palette_index = random.randint(0, len(PALETTES) - 1)
    palette_selected = color_chooser(palette_index)

    def path_positions(
        path_letters: str,
        entry_point: tuple[int, int],
        grid: Grid,
    ) -> list[tuple[int, int]]:
        positions = [entry_point]
        current_position = entry_point
        direction_from_letter = {}
        for direction, letter in LETTERS.items():
            direction_from_letter[letter] = direction
        for letter in path_letters:
            direction = direction_from_letter[letter]
            neighbor_cell = grid.get_neighbor(current_position, direction)
            if neighbor_cell is None:
                raise ValueError(
                    f"Path step {letter!r} from {current_position} points "
                    "outside the maze - solve() and the grid disagree"
                )
            current_position = neighbor_cell.position
            positions.append(current_position)
        return positions

    show_path = True
    path = path_positions(path_letters, generator.entry_point, grid)

    image = mlx_library.mlx_new_image(
        mlx_connection, window_width, window_height
    )
    # mlx_get_data_addr gives back 4 values at once: the writable pixel
    # buffer, plus 3 numbers describing it. We only need the first and
    # third here, but we still have to catch all 4 on the left-hand side.
    pixels, bits_per_pixel, size_line, image_format = (
        mlx_library.mlx_get_data_addr(image)
    )

    def redraw(
        current_grid: Grid,
        current_palette: dict[str, tuple[int, int, int, int]],
        path_to_show: list[tuple[int, int]],
        show_path: bool
    ) -> None:
        clear_image(
            pixels, size_line, window_width, window_height,
            current_palette["background"],
        )
        for row in current_grid.cells:
            for cell in row:
                draw_cell(pixels, size_line, cell, current_palette)
        if show_path:
            for x, y in path_to_show:
                path_cell = current_grid.cells[y][x]
                fill_cell(
                    pixels, size_line, path_cell, current_palette["path"]
                )

        mlx_library.mlx_put_image_to_window(
            mlx_connection, window, image, 0, 0
        )

    redraw(grid, palette_selected, path, show_path)
    menu_actions()

    def on_key_press(key_code: int, extra_data: object) -> int:
        nonlocal grid
        nonlocal palette_index
        nonlocal palette_selected
        nonlocal show_path

        if key_code == KEY_1:
            grid = generator.generate_maze()
            redraw(grid, palette_selected, path, show_path)
        if key_code == KEY_2:
            show_path = not show_path
            redraw(grid, palette_selected, path, show_path)
        if key_code == KEY_3:
            palette_index += 1
            palette_selected = color_chooser(palette_index)
            redraw(grid, palette_selected, path, show_path)
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


def color_chooser(
    color_selection: int,
) -> dict[str, tuple[int, int, int, int]]:
    """Return one palette from PALETTES.

    Args:
        color_selection: any integer. Wrapped with ``%`` so it's always a
            valid index - callers can just keep incrementing to rotate.

    Returns:
        The selected palette: a dict mapping role name ("background",
        "wall", "pattern", "path") to a colour tuple.
    """
    return PALETTES[color_selection % len(PALETTES)]


def main() -> None:
    # standalone test, used only when running this file directly -
    # the real pipeline builds this via a_maze_ing.py instead
    test_generator = MazeGenerator(10, 8, (0, 0), (9, 7), 42)
    show_grid(test_generator)


if __name__ == "__main__":
    main()
