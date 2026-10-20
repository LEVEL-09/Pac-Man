"""Context manager for handling uncaught game errors."""

import sys
from types import TracebackType

from mlx_wrapper import MLXError
from typing_extensions import Self


class ErrorHandler:
    """Context manager to catch OSError or ValueError."""

    def __init__(self) -> None:
        """Initialize the set of exception types to handle."""
        self.exception = (
            RuntimeError,
            TypeError,
            OSError,
            ValueError,
            MLXError
        )

    def __enter__(self) -> Self:
        """Enter the runtime context and return self."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Handle any exception raised within the context.

        Prints the exception message and exits the program if the
        raised exception matches one of the handled types.

        Args:
            exc_type: The exception type, if any.
            exc_val: The exception instance, if any.
            exc_tb: The exception traceback, if any.

        Returns:
            True if no exception occurred or it was handled;
            otherwise False to propagate the exception.
        """
        if exc_type is None:
            return True

        if issubclass(exc_type, self.exception):
            print(exc_val)
            sys.exit(1)

        return False
