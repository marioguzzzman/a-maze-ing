#! /usr/bin/env python3

#Error handling
"""
Your program must handle all errors gracefully: invalid configuration, file not found, bad
syntax, impossible maze parameters, etc. It must never crash unexpectedly, and must always
provide a clear error message to the user.

The "42" pattern may be omitted in case the maze size does not allow it (i.e. too small).
> Print an error message on the console in that case.

 Graceful errors: missing file, bad syntax, missing key, out-of-bounds entry/exit,
      entry == exit, impossible dimensions
"""

class MazeAppError(Exception):
    def __init__(self, message: str = "Unknown Maze error") -> None:
        super().__init__(message)

class ConfigError(MazeAppError):
    def __init__(self, message: str = "Unknown Config error") -> None:
        super().__init__(message)