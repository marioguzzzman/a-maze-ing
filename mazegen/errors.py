#! /usr/bin/env python3

# Error handling
"""
Your program must handle all errors gracefully: invalid configuration,
file not found, bad syntax, impossible maze parameters, etc. It must
never crash unexpectedly, and must always provide a clear error message
to the user.

The "42" pattern may be omitted in case the maze size does not allow it
(i.e. too small).
> Print an error message on the console in that case.

 Graceful errors: missing file, bad syntax, missing key, out-of-bounds
      entry/exit, entry == exit, impossible dimensions
"""


class MazeAppError(Exception):
    """Base class for this project's graceful, user-facing errors.

    Distinct from a plain ValueError, which this project reserves for
    internal programmer-bug tripwires (e.g. Grid.open_passage) rather
    than expected, user-facing problems.
    """

    def __init__(self, message: str = "Unknown Maze error") -> None:
        """Create a MazeAppError.

        Args:
            message: the error message shown to the user.
        """
        super().__init__(message)


class ConfigError(MazeAppError):
    """Raised for a problem with the config file.

    Covers bad syntax, a missing required key, or a value that
    doesn't make sense (e.g. ENTRY outside the maze bounds).
    """

    def __init__(self, message: str = "Unknown Config error") -> None:
        """Create a ConfigError.

        Args:
            message: the error message shown to the user.
        """
        super().__init__(message)
