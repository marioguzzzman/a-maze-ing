def write_hex_to_file(
    maze: list[str],
    entry: tuple[int, int],
    exit: tuple[int, int],
    solution: str,
    filename: str = "output_maze.txt"
) -> None:

    with open(filename, "w") as file:
        for row in maze:
            file.write(row + "\n")

        file.write("\n")
        file.write((f"{entry[0]}, {entry[1]}\n"))
        file.write(f"{exit[0]}, {exit[1]}\n")

        file.write(solution + "\n")
