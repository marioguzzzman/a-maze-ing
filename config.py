#! /usr/bin/env python3

# Open and Parsing
"""
Open File, parse the config file and assign to variables
"""

# from amaze.a_maze_ing import ConfigError

ConfigValue = int | tuple[int, int] | str | bool
Config = dict[str, ConfigValue]


def prepare_lines(lines: list[str]) -> list[str]:
    # Clean the lines, remove empty lines and comments
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            continue
        clean_lines.append(stripped)
    return clean_lines


def build_config(clean_lines: list[str]) -> dict[str, str]:
    raw_config: dict[str, str] = {}
    for line in clean_lines:
        key, value = line.split("=")
        raw_config[key] = value
    return raw_config


def clean_config(raw_config: dict[str, str]) -> Config:
    cleaned_config: Config = {}
    # try:
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
    # except:
        # raise ConfigError("Invalid value")

    return cleaned_config


def parse_config(lines: list[str]) -> Config:
    clean_lines = prepare_lines(lines)
    raw_config = build_config(clean_lines)
    cleaned_config = clean_config(raw_config)
    return cleaned_config
