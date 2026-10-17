def write_hex_to_file(
    maze: list[str],
    entry: tuple[int, int],
    exit: tuple[int, int],
    solution: str,
    filename: str = "output_maze.txt"
) -> None:
    """Write the maze to the output file, in the subject's format.

    One hex-encoded row per line, then a blank line, then the entry
    coordinates, the exit coordinates, and the solution path - each
    on its own line.

    Args:
        maze: one hex-digit string per row, as returned by
            MazeGenerator.maze_to_hex().
        entry: the (x, y) entry coordinates.
        exit: the (x, y) exit coordinates.
        solution: the shortest path as a string of N/E/S/W letters.
        filename: the file to write to.
    """
    with open(filename, "w") as file:
        for row in maze:
            file.write(row + "\n")

        file.write("\n")
        file.write((f"{entry[0]}, {entry[1]}\n"))
        file.write(f"{exit[0]}, {exit[1]}\n")

        file.write(solution + "\n")
