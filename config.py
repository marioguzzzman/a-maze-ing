#! /usr/bin/env python3

# Open and Parsing
"""
Open File, parse the config file and assign to variables
"""

from errors import ConfigError

ConfigValue = int | tuple[int, int] | str | bool
Config = dict[str, ConfigValue]

REQUIRED_KEYS = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]


def prepare_lines(lines: list[str]) -> list[str]:
    """Strip blank lines and '#' comments from the raw file lines.

    Args:
        lines: the raw lines read from the config file.

    Returns:
        Only the lines holding an actual KEY=VALUE pair, stripped of
        leading/trailing whitespace.
    """
    # Clean the lines, remove empty lines and comments
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            continue
        clean_lines.append(stripped)
    return clean_lines


def build_config(clean_lines: list[str]) -> dict[str, str]:
    """Split each 'KEY=VALUE' line into a plain string dict.

    Args:
        clean_lines: lines already stripped of comments/blanks, each
            expected to contain exactly one '='.

    Returns:
        A dict mapping each key to its raw, still-unconverted value.
    """
    raw_config: dict[str, str] = {}
    for line in clean_lines:
        key, value = line.split("=")
        raw_config[key] = value
    return raw_config


def clean_config(raw_config: dict[str, str]) -> Config:
    """Convert each raw string value to its real type.

    WIDTH/HEIGHT/SEED become int, ENTRY/EXIT become an (int, int)
    tuple, OUTPUT_FILE stays a str, PERFECT becomes a bool.

    Args:
        raw_config: the dict build_config() produced.

    Returns:
        The same keys, with values converted to their real types.
    """
    cleaned_config: Config = {}
    for key, value in raw_config.items():
        if key in ["WIDTH", "HEIGHT", "SEED"]:
            cleaned_config[key] = int(value)
        elif key in ["ENTRY", "EXIT"]:
            x_str, y_str = value.split(",")
            cleaned_config[key] = (int(x_str), int(y_str))
        elif key in ["OUTPUT_FILE"]:
            cleaned_config[key] = str(value)
        elif key in ["PERFECT"]:
            cleaned_config[key] = value == "True"
    return cleaned_config


def validate_config(config: Config) -> None:
    """Check cleaned config is complete and makes sense together.

    Args:
        config: the dict clean_config() produced.

    Raises:
        ConfigError: on a missing key, an impossible WIDTH/HEIGHT, an
            ENTRY/EXIT outside the maze, or ENTRY == EXIT.
    """
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ConfigError(f"Missing required key: {key}")

    width = config["WIDTH"]
    height = config["HEIGHT"]
    entry = config["ENTRY"]
    exit_point = config["EXIT"]

    if not isinstance(width, int) or width <= 0:
        raise ConfigError(f"WIDTH must be a positive integer, got {width!r}")
    if not isinstance(height, int) or height <= 0:
        raise ConfigError(
            f"HEIGHT must be a positive integer, got {height!r}"
        )
    if not isinstance(entry, tuple) or not isinstance(exit_point, tuple):
        raise ConfigError("ENTRY and EXIT must be x,y coordinates")

    entry_x, entry_y = entry
    exit_x, exit_y = exit_point

    if not (0 <= entry_x < width and 0 <= entry_y < height):
        raise ConfigError(
            f"ENTRY {entry} is outside the {width}x{height} maze"
        )
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        raise ConfigError(
            f"EXIT {exit_point} is outside the {width}x{height} maze"
        )
    if entry == exit_point:
        raise ConfigError("ENTRY and EXIT must be different cells")


def parse_config(lines: list[str]) -> Config:
    """Run the full config pipeline: parse, convert, and validate.

    Args:
        lines: the raw lines read from the config file.

    Returns:
        The parsed, type-converted, validated config dict.

    Raises:
        ConfigError: on bad syntax, a missing required key, or a
            value that doesn't make sense (see validate_config).
    """
    clean_lines = prepare_lines(lines)
    try:
        raw_config = build_config(clean_lines)
        cleaned_config = clean_config(raw_config)
    except ValueError as e:
        raise ConfigError(f"Bad syntax in config file: {e}") from e
    validate_config(cleaned_config)
    return cleaned_config
