#! /usr/bin/env python3

from mlx import Mlx  # type: ignore[import-untyped]
import random
from mazegen.generator import LETTERS, MazeGenerator
from mazegen.structure import Cell, Grid, Walls
from mazegen.output_maze import write_hex_to_file


CELL_SIZE = 60
BYTES_PER_PIXEL = 4
PATH_LINE_WIDTH = 10
# mlx_string_put's (x, y) is a glyph's top-left corner, not its center -
# these are the font's fixed glyph box size, straight from mlx_font.c /
# mlx_string_put.c (1140 / 95 chars - 2 = 10 wide, 20 tall).
LABEL_GLYPH_WIDTH = 10
LABEL_GLYPH_HEIGHT = 20

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


def packed_color(color: tuple[int, int, int, int]) -> int:
    """Pack a (B, G, R, A) tuple into the single int mlx_string_put wants.

    mlx_string_put's text goes through the same B8G8R8A8 image path as
    every other colour in this file - just as one 32-bit int instead of
    4 separate memoryview bytes.
    """
    blue, green, red, alpha = color
    return (alpha << 24) | (red << 16) | (green << 8) | blue


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


def cell_center(position: tuple[int, int]) -> tuple[int, int]:
    x, y = position
    center_x = x * CELL_SIZE + CELL_SIZE // 2
    center_y = y * CELL_SIZE + CELL_SIZE // 2
    return center_x, center_y


def draw_path_line(
    pixels: memoryview, size_line: int,
    start: tuple[int, int], end: tuple[int, int],
    color: tuple[int, int, int, int],
) -> None:
    start_x, start_y = start
    end_x, end_y = end
    half_width = PATH_LINE_WIDTH // 2
    if start_y == end_y:
        x_start, x_end = sorted((start_x, end_x))
        for y in range(start_y - half_width, start_y + half_width + 1):
            draw_horizontal_wall(pixels, size_line, y, x_start, x_end, color)
    else:
        y_start, y_end = sorted((start_y, end_y))
        for x in range(start_x - half_width, start_x + half_width + 1):
            draw_vertical_wall(pixels, size_line, x, y_start, y_end, color)


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
    hex_maze = generator.maze_to_hex()
    write_hex_to_file(
            hex_maze,
            generator.entry_point,
            generator.exit_point,
            path_letters,
    )
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
        if show_path:
            for i in range(len(path_to_show) - 1):
                start = cell_center(path_to_show[i])
                end = cell_center(path_to_show[i + 1])
                draw_path_line(
                    pixels, size_line, start, end, current_palette["path"]
                )
        entry_x, entry_y = generator.entry_point
        exit_x, exit_y = generator.exit_point
        entry_cell = current_grid.cells[entry_y][entry_x]
        exit_cell = current_grid.cells[exit_y][exit_x]
        fill_cell(pixels, size_line, entry_cell, current_palette["pattern"])
        fill_cell(pixels, size_line, exit_cell, current_palette["pattern"])
        for row in current_grid.cells:
            for cell in row:
                draw_cell(pixels, size_line, cell, current_palette)

        mlx_library.mlx_put_image_to_window(
            mlx_connection, window, image, 0, 0
        )
        label_color = packed_color(current_palette["background"])
        mlx_library.mlx_string_put(
            mlx_connection, window,
            entry_x * CELL_SIZE + CELL_SIZE // 2 - LABEL_GLYPH_WIDTH // 2,
            entry_y * CELL_SIZE + CELL_SIZE // 2 - LABEL_GLYPH_HEIGHT // 2,
            label_color, "A",
        )
        mlx_library.mlx_string_put(
            mlx_connection, window,
            exit_x * CELL_SIZE + CELL_SIZE // 2 - LABEL_GLYPH_WIDTH // 2,
            exit_y * CELL_SIZE + CELL_SIZE // 2 - LABEL_GLYPH_HEIGHT // 2,
            label_color, "B",
        )

    redraw(grid, palette_selected, path, show_path)
    menu_actions()

    def on_key_press(key_code: int, extra_data: object) -> int:
        nonlocal grid
        nonlocal palette_index
        nonlocal palette_selected
        nonlocal show_path
        nonlocal path_letters
        nonlocal path
        nonlocal hex_maze

        if key_code == KEY_1:
            grid = generator.generate_maze()
            path_letters = generator.solve()
            path = path_positions(path_letters, generator.entry_point, grid)
            hex_maze = generator.maze_to_hex()
            write_hex_to_file(
                hex_maze,
                generator.entry_point,
                generator.exit_point,
                path_letters,
            )
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
