import sys
from types import TracebackType

from mlx_wrapper import MLXError
from typing_extensions import Self


class ErrorHandler:
    """Context manager to catch OSError or ValueError."""

    def __init__(self) -> None:
        self.exception = (
            RuntimeError,
            TypeError,
            OSError,
            ValueError,
            MLXError
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            return True

        if issubclass(exc_type, self.exception):
            print(exc_val)
            sys.exit(1)

        return False
