from collections.abc import Mapping
from typing import Self


class BaseError(Exception):
    """Base class for Gyomu application errors.

    Provides common contextual information for errors in addition to the
    information already provided by Python's :class:`Exception`.

    Args:
        message: A human-readable description of the error.
        context: An error context identifier.
        details: Additional structured diagnostic information.

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
        self.context = context
        self.details = details

    def chain(self, cause: BaseException) -> Self:
        """Associate an exception as the explicit cause of this error.

        Args:
            cause: The underlying exception that caused this error.

        Returns:
            This error instance.
        """
        self.__cause__ = cause
        return self
