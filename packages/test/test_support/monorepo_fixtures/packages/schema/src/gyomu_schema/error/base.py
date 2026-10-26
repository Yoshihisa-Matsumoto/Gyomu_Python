import inspect
from collections.abc import Mapping
from typing import Self


def caller_context() -> str:
    """Return the module and function name of the caller."""
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        return "<unknown>"

    try:
        caller = frame.f_back
        if caller is None:
            return "<unknown>"

        parent_caller = caller.f_back

        while parent_caller is not None:
            module = parent_caller.f_globals.get("__name__", "<unknown>")
            function = parent_caller.f_code.co_name

            if function == "<lambda>" or module.startswith("returns."):
                parent_caller = parent_caller.f_back
                continue

            return f"{module}.{function}"

        return "<unknown>"
    finally:
        del frame


class BaseError(Exception):
    """Base class for Gyomu application errors.

    Provides common contextual information for errors in addition to the
    information already provided by Python's :class:`Exception`.

    Args:
        message (str): A human-readable description of the error.
        context (str | None): An error context identifier.
        details (Mapping[str, object] | None): Additional structured diagnostic
            information.

    Attributes:
        context: The error context identifier.
        details: Additional structured diagnostic information.

    Gyomu Context:
        context identifies the operation or location where the error occurred.
        It describes what the application was doing when the error occurred
        and does not replace the Python traceback.

        details contains additional structured information useful for
        diagnosing the error, such as relevant input values, configuration
        metadata, or other operational information.

        The original cause of an error is represented by Python's exception
        chaining mechanism (__cause__). The :meth:`chain` method can be used
        to explicitly associate an underlying exception as the cause.
    """

    def __init__(
        self,
        message: str,
        *,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        """Initialize a BaseError."""
        super().__init__(message)
        self.message = message
        self.context = context
        self.details = details

    def chain(self, cause: BaseException) -> Self:
        """Associate an exception as the explicit cause of this error.

        Args:
            cause (BaseException): The underlying exception that caused this error.

        Returns:
            Self: This error instance.
        """
        self.__cause__ = cause
        return self
